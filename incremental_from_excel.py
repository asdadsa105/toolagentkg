"""Incrementally add SciToolKG triples from an Excel workbook.

Run from the SciToolAgent project root:
  python incremental_from_excel.py --excel data/new_tools.xlsx --dry-run
  python incremental_from_excel.py --excel data/new_tools.xlsx --device cuda:0

Workbook schema:
  Sheet Tools: Category, Name, Function, Input, Output, Safety, Source
  Sheet Triples (optional): Subject, Predicate, Object

This updates the existing BGE-M3 LlamaIndex KG only. It does NOT modify Neo4j,
register executable tools, remove old triples, or re-embed existing descriptions.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

import pandas as pd

TOOL_COLUMNS = ["Category", "Name", "Function", "Input", "Output", "Safety", "Source"]
TRIPLE_COLUMNS = ["Subject", "Predicate", "Object"]


def read_sheet(file_path: Path, sheet: str, required: list[str]) -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name=sheet, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Excel工作表 {sheet!r} 缺少列: {missing}")
    df = df[required].copy()
    for c in required:
        df[c] = df[c].map(lambda v: str(v).strip())
    return df


def load_excel(file_path: Path, existing_tool_names: set[str]):
    from scripts.utils import create_triplets

    with pd.ExcelFile(file_path) as book:
        sheets = set(book.sheet_names)
    if not ({"Tools", "Triples"} & sheets):
        raise ValueError("Excel至少需要一个工作表: Tools 或 Triples")

    proposed: list[tuple[str, str, str]] = []
    new_tool_names: list[str] = []
    skipped_tools: list[str] = []

    if "Tools" in sheets:
        df = read_sheet(file_path, "Tools", TOOL_COLUMNS)
        new_rows = []
        seen_names: set[str] = set()
        for i, row in df.iterrows():
            obj = row.to_dict()
            if not any(obj.values()):
                continue
            # The original project example contains this empty placeholder row.
            if obj["Name"].lower() == "your tool here" and all(
                not obj[c] for c in TOOL_COLUMNS if c != "Name"
            ):
                continue
            missing = [c for c in TOOL_COLUMNS if not obj[c]]
            if missing:
                raise ValueError(f"Tools工作表Excel第{i+2}行缺少值: {missing}")
            if obj["Safety"].lower() not in {"yes", "no"}:
                raise ValueError(f"Tools工作表第{i+2}行Safety必须是Yes或No")
            obj["Safety"] = obj["Safety"].capitalize()
            name = obj["Name"]
            if name in seen_names:
                raise ValueError(f"Tools工作表存在重复工具名: {name}")
            seen_names.add(name)
            if name in existing_tool_names:
                skipped_tools.append(name)
                continue
            new_rows.append(obj)
            new_tool_names.append(name)
        if new_rows:
            proposed.extend(tuple(t) for t in create_triplets(pd.DataFrame(new_rows, columns=TOOL_COLUMNS)))

    if "Triples" in sheets:
        df = read_sheet(file_path, "Triples", TRIPLE_COLUMNS)
        for i, row in df.iterrows():
            obj = row.to_dict()
            if not any(obj.values()):
                continue
            missing = [c for c in TRIPLE_COLUMNS if not obj[c]]
            if missing:
                raise ValueError(f"Triples工作表Excel第{i+2}行缺少值: {missing}")
            proposed.append((obj["Subject"], obj["Predicate"], obj["Object"]))

    return proposed, new_tool_names, skipped_tools


def main():
    parser = argparse.ArgumentParser(description="从Excel增量更新现有SciToolKG和BGE-M3索引")
    parser.add_argument("--excel", default="data/new_tools.xlsx", help="增量Excel文件")
    parser.add_argument("--kg-dir", default="KG/storage_graph_bge_m3", help="当前知识图谱目录")
    parser.add_argument("--device", default="cuda:0", help="BGE-M3设备，如cuda:0或cpu")
    parser.add_argument("--dry-run", action="store_true", help="只检查和统计，不修改图谱")
    parser.add_argument("--no-backup", action="store_true", help="跳过自动备份（不建议）")
    args = parser.parse_args()

    excel = Path(args.excel).resolve()
    kg_dir = Path(args.kg_dir).resolve()
    graph_file = kg_dir / "graph_store.json"
    if not excel.is_file():
        parser.error(f"找不到Excel: {excel}")
    if not graph_file.is_file() or not (kg_dir / "index_store.json").is_file():
        parser.error(f"知识图谱路径无效: {kg_dir}，请在项目根目录执行")

    graph = json.loads(graph_file.read_text(encoding="utf-8"))["graph_dict"]
    existing_triples = {
        (source, rel, target)
        for source, pairs in graph.items()
        for rel, target in pairs
    }
    existing_tool_names = {
        source for source, pairs in graph.items()
        if any(rel == "is a" for rel, _ in pairs)
    }
    proposed, new_tool_names, skipped_tools = load_excel(excel, existing_tool_names)

    additions = []
    seen = set(existing_triples)
    for triple in proposed:
        if triple not in seen:
            additions.append(triple)
            seen.add(triple)

    new_embeddings = sum(rel == "has the functionality that" for _, rel, _ in additions)
    print(f"原有三元组(去重): {len(existing_triples)}")
    print(f"Excel内新工具: {len(new_tool_names)}；已有工具跳过: {len(skipped_tools)}")
    if skipped_tools:
        print("跳过的已有工具:", ", ".join(skipped_tools[:10]))
    print(f"本次新增三元组: {len(additions)}；需要生成BGE-M3向量: {new_embeddings}")
    for triple in additions[:8]:
        print("  +", triple)
    if args.dry_run:
        print("\n预检完成（--dry-run），未修改任何文件。")
        return
    if not additions:
        print("没有新增三元组，知识图谱未修改。")
        return

    # Import heavy dependencies only after the fast dry-run validation.
    from llama_index.core import Settings, StorageContext, load_index_from_storage
    from llama_index.core.llms import MockLLM
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-m3", device=args.device, embed_batch_size=16
    )
    Settings.llm = MockLLM(max_tokens=256)

    ctx = StorageContext.from_defaults(persist_dir=str(kg_dir))
    index = load_index_from_storage(ctx)
    before = len(index.index_struct.embedding_dict)

    if not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup = kg_dir.with_name(f"{kg_dir.name}_backup_{stamp}")
        shutil.copytree(kg_dir, backup)
        print("备份路径:", backup)

    for idx, triple in enumerate(additions, start=1):
        index.upsert_triplet(triple, include_embeddings=(triple[1] == "has the functionality that"))
        if idx % 20 == 0 or idx == len(additions):
            print(f"已新增: {idx}/{len(additions)}")

    # Make sure updated vector/knowledge-graph index is persisted alongside the graph store.
    ctx.index_store.add_index_struct(index.index_struct)
    ctx.persist(persist_dir=str(kg_dir))
    after = len(index.index_struct.embedding_dict)
    print("\n增量更新完成！")
    print(f"Embedding条目: {before} -> {after}")
    print("知识图谱目录:", kg_dir)
    print("注意：Neo4j可视化副本不会自动同步；新工具尚需注册Python函数才能实际执行。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}", file=sys.stderr)
        raise

"""Generate reviewable SciToolKG-compatible Excel from text via DeepSeek.

DOES NOT update graph index or Neo4j. Run from SciToolAgent project root:
  python text_to_excel_kg.py --input data/raw_documents --output data/new_tools.xlsx --preview
  python text_to_excel_kg.py --input data/raw_documents --output data/new_tools.xlsx
  python incremental_from_excel.py --excel data/new_tools.xlsx --dry-run
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

from text_ingestion.document_loader import load_documents
from text_ingestion.text_chunker import split_document, token_count, write_chunk_manifest
from text_ingestion.normalize import normalize_results
from text_ingestion.excel_exporter import export_excel


def main(argv=None):
    p=argparse.ArgumentParser(description='DeepSeek从TXT/MD自动提取工具信息并生成SciToolKG增量Excel（先审核后入库）')
    p.add_argument('--input',default='data/raw_documents',help='TXT/MD文件或文件夹')
    p.add_argument('--output',default='data/new_tools.xlsx',help='待审核Excel输出路径')
    p.add_argument('--chunk-size',type=int,default=1200,help='每块Token上限')
    p.add_argument('--chunk-overlap',type=int,default=100,help='连续块Token重叠')
    p.add_argument('--preview',action='store_true',help='仅分块和打印预览，不调用API、不生成Excel')
    p.add_argument('--max-chunks',type=int,default=0,help='仅处理前N块，0表示全部（测试用）')
    p.add_argument('--force-extract',action='store_true',help='忽略已有的API响应缓存')
    p.add_argument('--overwrite',action='store_true',help='允许覆盖已有输出Excel；谨慎使用')
    p.add_argument('--config',default='example.env',help='读取API密钥和模型配置')
    p.add_argument('--model',default=None,help='覆盖DEEPSEEK_MODEL设置')
    p.add_argument('--work-dir',default='data/text_kg_work',help='保存chunk清单和响应缓存')
    args=p.parse_args(argv)
    if args.max_chunks<0:
        p.error('--max-chunks不能为负')
    docs=load_documents(args.input)
    chunks=[]
    for doc in docs:
        chunks.extend(split_document(doc,args.chunk_size,args.chunk_overlap))
    if args.max_chunks:
        chunks=chunks[:args.max_chunks]
    work=Path(args.work_dir)
    write_chunk_manifest(chunks,work/'chunks.json')
    print(f'文档数={len(docs)}; 待处理Chunk数={len(chunks)}; 目录={work}')
    if not chunks:
        raise RuntimeError('切分后没有非空Chunk')
    for c in chunks[:4]:
        print(f' - {c.chunk_id}: {Path(c.file_path).name}:{c.start_line}-{c.end_line} [{token_count(c.text)} tokens], {c.section!r}')
    if args.preview:
        print('预览结束。未调用DeepSeek、未生成Excel、未更新知识图谱。')
        return 0

    from text_ingestion.deepseek_extractor import DeepSeekExtractor,load_api_config
    api_key,base_url,model=load_api_config(Path(args.config),args.model)
    extractor=DeepSeekExtractor(api_key,base_url,model,work/'cache')
    try:
        results=[]
        for i,c in enumerate(chunks,1):
            obj=extractor.extract(c,force=args.force_extract)
            results.append((c,obj))
            print(f'[{i}/{len(chunks)}] {c.chunk_id} 工具候选={len(obj["tools"])} 三元组候选={len(obj["triples"])}')
    finally:
        extractor.close()
    tables=normalize_results(results)
    print('生成统计:', ', '.join(f'{k}={len(v)}' for k,v in tables.items()))
    path=export_excel(tables,args.output,overwrite=args.overwrite)
    print('Excel已生成:',path.resolve())
    print('请先检查Tools、Triples和Review；确认无误再运行：')
    print(f'  python incremental_from_excel.py --excel "{path}" --dry-run')
    print('本程序不自动更新索引，不自动同步Neo4j，不注册可执行工具。')
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f'处理失败：{type(e).__name__}: {e}',file=sys.stderr)
        raise SystemExit(1)

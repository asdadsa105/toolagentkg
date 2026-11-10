"""Optional Jev decision stage for SciToolAgent candidate tools.

Place in scripts/jev_tool_selector.py. Calls the official TypeSafe System One API
using httpx, already required by SciToolAgent. No changes to the KG or BGE-M3.

JEV_MODE=off     : original pipeline
JEV_MODE=shadow  : compute and print scores, keep original candidates
JEV_MODE=rerank  : reorder candidate triples, keep all candidates
JEV_MODE=filter  : retain likely necessary tools + best input producers
"""
from __future__ import annotations

import os
from collections import defaultdict

import httpx


def _candidate_tools(triples):
    """Return ordered tools from functionality triples, enriched with I/O types."""
    candidates = {}
    for s, rel, obj in triples:
        if str(rel) == "has the functionality that":
            candidates.setdefault(str(s), {
                "name": str(s), "function": str(obj),
                "inputs": [], "outputs": [],
            })
    for s, rel, obj in triples:
        name = str(s)
        if name in candidates and str(rel) in ("inputs", "outputs"):
            values = candidates[name][str(rel)]
            if str(obj) not in values:
                values.append(str(obj))
    return candidates


def _graph_dependencies(candidates):
    """Record exact output-to-input matches between candidate tools."""
    dependencies = []
    for left, source in candidates.items():
        outputs = set(source["outputs"])
        if not outputs:
            continue
        for right, target in candidates.items():
            if left == right:
                continue
            for datatype in sorted(outputs & set(target["inputs"])):
                dependencies.append({
                    "from_tool": left,
                    "data_type": datatype,
                    "to_tool": right,
                })
    return dependencies


def _add_best_prerequisites(selected, scores, candidates):
    """Best-effort preservation of upstream tools for a selected tool's input."""
    selected = set(selected)
    changed = True
    while changed:
        changed = False
        for tool in list(selected):
            for need in candidates[tool]["inputs"]:
                # When a selected tool already produces the data type, keep it.
                if any(need in candidates[t]["outputs"] for t in selected):
                    continue
                producers = [
                    t for t in candidates
                    if t != tool and need in candidates[t]["outputs"]
                ]
                if producers:
                    best = max(producers, key=lambda t: scores.get(t, 0.0))
                    selected.add(best)
                    changed = True
    return selected


async def select_tools_with_jev(question: str, triples: list):
    """Return triples passed to DeepSeek Planner; fail open to original triples."""
    mode = os.getenv("JEV_MODE", "off").strip().lower()
    if mode == "off":
        return triples
    if mode not in {"shadow", "rerank", "filter"}:
        print(f"[Jev] 未知模式 {mode!r}，回退原工具列表", flush=True)
        return triples

    key = os.getenv("TYPESAFE_API_KEY", "").strip()
    if not key:
        print("[Jev] TYPESAFE_API_KEY未设置，回退原工具列表", flush=True)
        return triples

    candidates = _candidate_tools(triples)
    if not candidates:
        print("[Jev] 没有提取到候选工具，回退原工具列表", flush=True)
        return triples

    # The state contains actual tool properties and tool-to-tool data edges.
    state = {
        "task": question,
        "candidate_tools": list(candidates.values()),
        "connections": _graph_dependencies(candidates),
    }
    questions = {
        f"tool_{i}": {
            "type": "noul",
            "instructions": (
                f"For the scientific task in state.task, is tool '{name}' "
                "necessary or useful anywhere in a correct executable multi-step "
                "tool chain, including as an upstream input producer? "
                "Consider the tool's function, inputs, outputs, and connections. "
                "A prerequisite tool can be needed even if it does not directly "
                "answer the final question."
            ),
        }
        for i, name in enumerate(candidates)
    }
    payload = {
        "model": os.getenv("JEV_MODEL", "jev-latest"),
        "state": state,
        "questions": questions,
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.typesafe.ai/v1/systemone",
                headers={"Authorization": f"Bearer {key}"},
                json=payload,
            )
            response.raise_for_status()
            answer = response.json()["answers"]
        scores = {
            name: float(answer[f"tool_{i}"]["noul"])
            for i, name in enumerate(candidates)
        }
        if any(not (0 <= p <= 1) for p in scores.values()):
            raise ValueError("Jev返回的概率不在0～1内")
    except Exception as exc:
        print(f"[Jev] 调用失败，保留原Top-10：{type(exc).__name__}: {exc}", flush=True)
        return triples

    ranked = sorted(candidates, key=lambda name: scores[name], reverse=True)
    print(f"[Jev] 模式={mode}，评分（不是工具链准确率）：", flush=True)
    for name in ranked:
        print(f"    {name}: {scores[name]:.3f}", flush=True)

    if mode == "shadow":
        print("[Jev] shadow模式：仍将原始Top-10交给DeepSeek", flush=True)
        return triples

    if mode == "filter":
        threshold = float(os.getenv("JEV_THRESHOLD", "0.55"))
        selected = {name for name in ranked if scores[name] >= threshold}
        if not selected:
            print("[Jev] 无工具超过阈值，回退原始Top-10", flush=True)
            return triples
        selected = _add_best_prerequisites(selected, scores, candidates)
        ranked = [name for name in ranked if name in selected]
        print(f"[Jev] filter保留工具：{ranked}", flush=True)

    grouped = defaultdict(list)
    others = []
    for triple in triples:
        if str(triple[0]) in candidates:
            grouped[str(triple[0])].append(triple)
        else:
            others.append(triple)
    return [triple for name in ranked for triple in grouped[name]] + others

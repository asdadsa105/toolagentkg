"""Read the actual ToolsAgent registries without importing heavy scientific dependencies.

Newly extracted documentation is not executable until its function has been
registered in ToolsAgent/ToolsFuns/*/tool_name_dict.py.
"""
from __future__ import annotations
import ast
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def registered_tool_names() -> frozenset[str]:
    names = set()
    registry_files = list((ROOT / 'ToolsAgent' / 'ToolsFuns').glob('*/tool_name_dict.py'))
    if not registry_files:
        raise FileNotFoundError('ToolsAgent 的工具注册表缺失，无法确认工具可执行性')
    for file in registry_files:
        syntax = ast.parse(file.read_text(encoding='utf-8'), filename=str(file))
        for node in syntax.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.endswith('_TOOLS_DICT'):
                        if isinstance(node.value, ast.Dict):
                            for key in node.value.keys:
                                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                                    names.add(key.value)
    if not names:
        raise RuntimeError('未能解析实际工具注册表')
    return frozenset(names)


def keep_registered_candidates(triples: list) -> list:
    """Only let registered tool triples reach Jev/Planner.

    Keep the returned candidate triple bundles intact, including shared IO
    datatype nodes. Tool root names are identified by functionality triples.
    """
    registered = registered_tool_names()
    roots = {str(s) for s, rel, _ in triples if str(rel) == 'has the functionality that'}
    keep = roots & registered
    discarded = sorted(roots - keep)
    if discarded:
        print('[Registry] 忽略未注册的工具候选: ' + ', '.join(discarded[:15]), flush=True)
    return [t for t in triples if str(t[0]) not in roots or str(t[0]) in keep]

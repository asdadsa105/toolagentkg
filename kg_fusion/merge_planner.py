"""Prepare an auditable, conservative update from DeepSeek's reviewed Excel.

Guarantees:
- Existing tools never have executable metadata silently replaced.
- All imported free-form triples must match approved Evidence records.
- An existing tool's source can be appended ONLY with explicit review approval.
- The existing incremental_from_excel.py remains the sole KG index writer.

No alias merging, LLM-based conflict arbitration, or deletion is performed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from incremental_from_excel import TOOL_COLUMNS, TRIPLE_COLUMNS, read_sheet
from text_ingestion.normalize import CATEGORIES, SUPPORTED_REL

PREDICATES = {
    'Category': 'is a',
    'Function': 'has the functionality that',
    'Input': 'inputs',
    'Output': 'outputs',
    'Source': 'is sourced from',
}
EXECUTABLE_REL = {
    'is a', 'has the functionality that',
    'inputs', 'outputs', 'is the input of', 'is the output of',
    'needs', 'does not need'
}


def _clean(value: Any) -> str:
    return ' '.join(str(value or '').strip().split())


def _values(value: str) -> set[str]:
    return {v.strip() for v in value.split(',') if v.strip()}


def _t(s: str, p: str, o: str) -> tuple[str, str, str]:
    return _clean(s), _clean(p), _clean(o)


def _graph(folder: str | Path) -> dict:
    src = Path(folder) / 'graph_store.json'
    data = json.loads(src.read_text(encoding='utf-8'))
    if not isinstance(data.get('graph_dict'), dict):
        raise ValueError('graph_store.json 缺少 graph_dict')
    return data['graph_dict']


def _evidence_sets(excel: Path) -> tuple[set, set]:
    import pandas as pd
    with pd.ExcelFile(excel) as book:
        if 'Evidence' not in book.sheet_names:
            raise ValueError('融合入库必须包含Evidence工作表，请使用统一前端抽取的审核Excel')
    df = pd.read_excel(excel, sheet_name='Evidence', dtype=str, keep_default_na=False)
    required = {'RecordType', 'Subject', 'Predicate', 'Object', 'Disposition', 'ChunkID', 'Quote'}
    if not required.issubset(df.columns):
        raise ValueError('Evidence工作表字段不完整，不能确认来源')
    tool_evidence = set()
    triple_evidence = set()
    for row in df.to_dict('records'):
        if _clean(row.get('Disposition')).casefold() != 'approved' or not _clean(row.get('ChunkID')) or not _clean(row.get('Quote')):
            continue
        if row.get('RecordType') == 'Tool':
            tool_evidence.add((_clean(row.get('Subject')), _clean(row.get('Object'))))
        if row.get('RecordType') == 'Triple':
            triple_evidence.add(_t(row.get('Subject'), row.get('Predicate'), row.get('Object')))
    return tool_evidence, triple_evidence


def make_fusion_plan(excel: str | Path, kg_dir: str | Path, approved_source_ids=()) -> dict[str, Any]:
    """Compute what *may* enter the existing index, without modifying it."""
    excel, kg_dir = Path(excel), Path(kg_dir)
    import pandas as pd
    with pd.ExcelFile(excel) as book:
        sheets = set(book.sheet_names)
    tools_df = read_sheet(excel, 'Tools', TOOL_COLUMNS) if 'Tools' in sheets else pd.DataFrame(columns=TOOL_COLUMNS)
    extra_df = read_sheet(excel, 'Triples', TRIPLE_COLUMNS) if 'Triples' in sheets else pd.DataFrame(columns=TRIPLE_COLUMNS)
    tool_evidence, triple_evidence = _evidence_sets(excel)

    graph = _graph(kg_dir)
    original = {_t(s, p, o) for s, pairs in graph.items() for p, o in pairs}
    existing_tools = {s for s, pairs in graph.items() if any(p == 'is a' for p, _ in pairs)}
    selected_sources = set(approved_source_ids)
    new_tools, existing_tool_rows, source_options, reviews, duplicates = [], [], [], [], []
    seen_names = set()

    def conflict(kind: str, subject: str, message: str, old='', new=''):
        reviews.append({'Kind':kind, 'Subject':subject, 'Reason':message,
                        'Old':str(old), 'New':str(new)})

    def source_option(name: str, source: str):
        source = _clean(source)
        key = _t(name, 'is sourced from', source)
        if not source or key in original:
            return
        identifier = f'{name}::{source}'
        if not any(o['id'] == identifier for o in source_options):
            source_options.append({'id': identifier,'Name': name, 'Source':source,
                                   'Existing': ', '.join(o for p, o in graph.get(name, []) if p == 'is sourced from')})

    for i, row in tools_df.iterrows():
        r = {c: _clean(row[c]) for c in TOOL_COLUMNS}
        if not any(r.values()):
            continue
        name = r['Name']
        if not name or name in seen_names:
            conflict('Tool', name, f'Tools表第{i+2}行工具名称为空或重复')
            continue
        seen_names.add(name)
        if not all(r.values()) or r['Safety'] not in ('Yes', 'No') or r['Category'] not in CATEGORIES:
            conflict('Tool', name, '必填字段/类别/Safety不符合Schema；拒绝入库',new=r)
            continue
        if (name, r['Function']) not in tool_evidence:
            conflict('Tool', name, '没有匹配的Approved Tool证据；可能经过未经复核的人工编辑',new=r)
            continue
        if name not in existing_tools:
            new_tools.append(r)
            continue
        existing_tool_rows.append(r)
        outgoing = graph.get(name, [])
        for field, pred in PREDICATES.items():
            new_val = r[field]
            old_values = {_clean(o) for p, o in outgoing if p == pred}
            if field in ('Input', 'Output'):
                # Existing tools may legitimately have several input/output edges.
                compare_old = old_values
                compare_new = _values(new_val)
                same = compare_new == compare_old
            else:
                same = new_val in old_values
            if same:
                duplicates.append((name, pred, new_val))
            elif field == 'Source':
                source_option(name, new_val)
            else:
                conflict('Tool', name, f'已有工具{field}与图谱不同，禁止自动更新',
                         ', '.join(sorted(old_values)), new_val)
        safety_old = {'Yes' if p == 'does not need' else 'No' for p, o in outgoing
                      if p in {'does not need', 'needs'} and o == 'Security Check'}
        if r['Safety'] in safety_old:
            duplicates.append((name, 'Safety', r['Safety']))
        else:
            conflict('Tool', name, '已有工具Safety不一致或图谱缺失该字段，禁止自动更新',
                     ', '.join(sorted(safety_old)), r['Safety'])

    # Let the original writer expand *new* Tools rows to canonical triples.
    from scripts.utils import create_triplets
    implied = set()
    if new_tools:
        implied = {_t(*tri) for tri in create_triplets(pd.DataFrame(new_tools, columns=TOOL_COLUMNS))}
    accepted = []
    seen = set(original) | implied
    new_names = {r['Name'] for r in new_tools}
    for i, row in extra_df.iterrows():
        tri = _t(row['Subject'], row['Predicate'], row['Object'])
        s, p, o = tri
        if not any(tri) or all(not x for x in tri):
            continue
        if not s or not p or not o or p not in SUPPORTED_REL:
            conflict('Triple', s, f'Triples表第{i+2}行无效或关系类型不支持',new=tri)
            continue
        if tri not in triple_evidence:
            conflict('Triple', s, '找不到与当前内容精确匹配的Approved Triple证据，拒绝人工未复核编辑',new=tri)
            continue
        if tri in seen:
            duplicates.append(tri)
            continue
        if p == 'is sourced from' and s in existing_tools:
            source_option(s, o)
            continue
        if p in EXECUTABLE_REL:
            # Includes existing tool contract, inverse contract, and security.
            conflict('Triple', s, '可执行工具契约/安全关系不能通过额外Triples绕过审核',new=tri)
            continue
        if p == 'is sourced from' and s in new_names:
            conflict('Triple', s, '新增工具Source字段已生成关系；额外来源留待审核',new=tri)
            continue
        # Other approved, explicitly supported relationships can connect old/new entities.
        accepted.append(tri)
        seen.add(tri)

    # Safe optional source enrichment for an existing tool, AFTER explicit UI approval.
    for o in source_options:
        if o['id'] in selected_sources:
            tri = _t(o['Name'], 'is sourced from', o['Source'])
            if tri not in seen:
                accepted.append(tri)
                seen.add(tri)
    unknown_approvals = selected_sources - {o['id'] for o in source_options}
    if unknown_approvals:
        raise ValueError('来源批准选项已过期，请重新预检')
    # Never silently alter a tool's functionality embedding or executable contract.
    output_tables = {
        'Tools': new_tools,
        'Triples': [dict(zip(TRIPLE_COLUMNS, t)) for t in accepted],
        'Evidence': [], 'Review': [],
    }
    return {
        'tables': output_tables,
        'new_tools': [r['Name'] for r in new_tools],
        'existing_tools': [r['Name'] for r in existing_tool_rows],
        'source_options': source_options,
        'reviews': reviews,
        'duplicates': duplicates,
        'accepted_triples': accepted,
        'stats': {
            'new_tools': len(new_tools), 'existing_tools': len(existing_tool_rows),
            'new_extra_triples': len(accepted), 'duplicates': len(duplicates),
            'needs_review': len(reviews), 'source_candidates': len(source_options),
            'source_selected': sum(o['id'] in selected_sources for o in source_options),
        },
    }

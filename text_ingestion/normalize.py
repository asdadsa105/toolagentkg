"""Merge extracted records conservatively into existing SciToolKG Excel schema.

No LLM-created tool without complete, grounded metadata enters Tools. Source
provenance goes into Evidence, conflicts into Review.
"""
from __future__ import annotations
import re
from pathlib import Path
from collections import defaultdict
from .text_chunker import Chunk

TOOL_COLUMNS = ['Category', 'Name', 'Function', 'Input', 'Output', 'Safety', 'Source']
TRIPLE_COLUMNS = ['Subject','Predicate','Object']
EVIDENCE_COLUMNS = ['RecordType','Subject','Predicate','Object','SourceFile','ChunkID','Section','StartLine','EndLine','Quote','Disposition']
REVIEW_COLUMNS = ['Kind','NameOrSubject','Reason','SourceFile','ChunkID','Quote','Data']
SUPPORTED_REL = {'inputs','outputs','is the input of','is the output of','has the functionality that','is sourced from','needs','does not need','is a',
                 'uses','produces','contains','causes','inhibits','increases','decreases','depends on',
                 'located in','associated with','has property','is part of','is defined as','measured by','requires','based on'}
GENERAL_REL = SUPPORTED_REL - {'inputs','outputs','is the input of','is the output of','has the functionality that','is sourced from','needs','does not need','is a'}
CATEGORIES = {'Chemical Tool','Biological Tool','Material Tool','General Tool'}


def _s(value):
    return str(value).strip() if value is not None else ''


def _flat(value):
    return ' '.join(_s(value).split())


def _evidence_match_text(value: str) -> str:
    """For evidence matching only: ignore Markdown emphasis/code markers.

    This does NOT accept paraphrases. After removing formatting markers, the
    evidence must still appear as a continuous substring in the source chunk.
    """
    value = _flat(value)
    value = value.replace('**', '').replace('__', '').replace('`', '')
    value = value.replace('*', '')
    return value.casefold()


def _is_quote_valid(quote: str, chunk: Chunk, min_chars: int = 12) -> bool:
    evidence = _evidence_match_text(quote)
    source = _evidence_match_text(chunk.text)
    return len(evidence) >= min_chars and evidence in source


def _review(rows: list, chunk: Chunk, kind: str, name: str, reason: str, quote: str, obj: dict):
    import json
    rows.append({
        'Kind':kind,'NameOrSubject':name,'Reason':reason,
        'SourceFile':chunk.file_path,'ChunkID':chunk.chunk_id,
        'Quote':_s(quote)[:1000], 'Data':json.dumps(obj,ensure_ascii=False)
    })


def normalize_results(results: list[tuple[Chunk,dict]]) -> dict[str,list[dict]]:
    tools_raw = defaultdict(list)
    triples_raw = []
    reviews, evidences = [], []
    for chunk, output in results:
        for value in output.get('tools', []):
            if not isinstance(value,dict):
                _review(reviews,chunk,'Tool','','工具条目不是JSON对象','',{'raw':str(value)})
                continue
            name = _s(value.get('name',value.get('Name')))
            quote = _s(value.get('evidence'))
            if not name or name.casefold() not in chunk.text.casefold():
                _review(reviews,chunk,'Tool',name,'工具名称在原文中不存在',quote,value)
                continue
            if not _is_quote_valid(quote,chunk,min_chars=25):
                _review(reviews,chunk,'Tool',name,'证据引文与原文不匹配（已忽略Markdown强调标记）',quote,value)
                continue
            row = {k:_flat(value.get(k.lower(),value.get(k,''))) for k in TOOL_COLUMNS}
            row['Name'] = name
            # Excel Safety=Yes means tool DOES NOT require an extra safety check.
            if row['Safety'].lower() in {'yes','no'}:
                row['Safety']=row['Safety'].capitalize()
            elif row['Safety']:
                _review(reviews,chunk,'Tool',name,'Safety必须为Yes/No或空',quote,value)
                continue
            if row['Category'] and row['Category'] not in CATEGORIES:
                _review(reviews,chunk,'Tool',name,'未知的Category类别',quote,value)
                continue
            tools_raw[name].append((row,chunk,quote))
        for value in output.get('triples', []):
            if not isinstance(value,dict):
                _review(reviews,chunk,'Triple','','三元组不是JSON对象','',{'raw':str(value)})
                continue
            subject = _flat(value.get('subject',value.get('Subject')))
            predicate = _flat(value.get('predicate',value.get('Predicate')))
            object_ = _flat(value.get('object',value.get('Object')))
            quote = _s(value.get('evidence'))
            valid = (
                subject and predicate in SUPPORTED_REL and object_
                and _is_quote_valid(quote,chunk)
                and subject.casefold() in chunk.text.casefold()
            )
            if not valid:
                _review(reviews,chunk,'Triple',subject,'三元组不完整、关系类型不支持或证据不匹配',quote,value)
                continue
            if predicate in GENERAL_REL and _flat(object_).casefold() not in _evidence_match_text(chunk.text):
                _review(reviews,chunk,'Triple',subject,'一般知识关系的宾语未在原文中明确出现',quote,value)
                continue
            triples_raw.append((subject,predicate,object_,chunk,quote,value))

    tools = []
    approved_names = set()
    for name, records in sorted(tools_raw.items()):
        combined = {'Name':name}
        conflicting=[]
        for field in TOOL_COLUMNS:
            if field == 'Name':continue
            distinct = list(dict.fromkeys(row[field] for row,_,_ in records if row[field]))
            if len(distinct)>1:
                conflicting.append(field)
            elif distinct:
                combined[field] = distinct[0]
            else:
                combined[field] = ''
        if conflicting:
            row,chunk,quote=records[0]
            _review(reviews,chunk,'Tool',name,'跨Chunk字段冲突: '+', '.join(conflicting),quote,combined)
            continue
        missing = [key for key in TOOL_COLUMNS if not combined.get(key)]
        if missing:
            row,chunk,quote=records[0]
            _review(reviews,chunk,'Tool',name,'缺少字段: '+', '.join(missing),quote,combined)
            continue
        approved_names.add(name)
        tools.append({col:combined[col] for col in TOOL_COLUMNS})
        for _,chunk,quote in records:
            evidences.append({
                'RecordType':'Tool', 'Subject':name,'Predicate':'tool_metadata','Object':combined['Function'],
                'SourceFile':chunk.file_path,'ChunkID':chunk.chunk_id,
                'Section':chunk.section,'StartLine':chunk.start_line,'EndLine':chunk.end_line,
                'Quote':quote,'Disposition':'Approved'
            })

    # Avoid writing triples already materialized by the Tools-to-triplets converter.
    implied=set()
    for row in tools:
        name=row['Name']
        implied.add((name,'is a',row['Category']))
        implied.add((name,'has the functionality that',row['Function']))
        for col,pred,inv in [('Input','inputs','is the input of'),('Output','outputs','is the output of')]:
            for value in row[col].split(','):
                v=value.strip()
                if v:
                    implied.add((name,pred,v));implied.add((v,inv,name))
        implied.add((name,'is sourced from',row['Source']))
        implied.add((name,'does not need' if row['Safety']=='Yes' else 'needs','Security Check'))

    triples=[]
    seen=set()
    for s,p,o,chunk,quote,obj in triples_raw:
        # No generic 'is a' facts: the current downstream KG treats every
        # subject of 'is a' as an executable tool candidate.
        if p == 'is a' and s not in approved_names:
            _review(reviews,chunk,'Triple',s,'is a仅允许已审核的工具实体，避免误识别为可执行工具',quote,obj)
            continue
        if p == 'has the functionality that' and s not in approved_names:
            _review(reviews,chunk,'Triple',s,'功能关系需先有完整工具信息，防止无注册工具进入向量检索',quote,obj)
            continue
        if p in {'needs','does not need'} and o != 'Security Check':
            _review(reviews,chunk,'Triple',s,'安全关系Object必须是Security Check',quote,obj)
            continue
        key=(s,p,o)
        if key in seen or key in implied:
            continue
        seen.add(key)
        triples.append({'Subject':s,'Predicate':p,'Object':o})
        evidences.append({
            'RecordType':'Triple','Subject':s,'Predicate':p,'Object':o,
            'SourceFile':chunk.file_path,'ChunkID':chunk.chunk_id,'Section':chunk.section,
            'StartLine':chunk.start_line,'EndLine':chunk.end_line,
            'Quote':quote,'Disposition':'Approved'
        })
    return {'Tools':tools,'Triples':triples,'Evidence':evidences,'Review':reviews}

"""Audited deletion for SciToolAgent's existing LlamaIndex SimpleGraphStore KG.

This is deliberately format-specific. It refuses unfamiliar index layouts rather than
risk leaving a stale BGE-M3 embedding or document reference behind.

IMPORTANT: Do not use with a Neo4j or PropertyGraphStore graph; this manages local
KG/storage_graph_bge_m3* only. It does not unregister executable Python tools.
"""
from __future__ import annotations

import ast
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

LOCK_NAME = '.scitoolagent_kg.lock'
INVERSES = {
    'inputs': 'is the input of',
    'is the input of': 'inputs',
    'outputs': 'is the output of',
    'is the output of': 'outputs',
}


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _index_data(index_store: dict) -> tuple[dict, dict]:
    data = index_store.get('index_store/data')
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError('只支持当前单KG索引结构；检测到未知或多个索引，请停止删除')
    outer = next(iter(data.values()))
    if outer.get('__type__') != 'kg':
        raise ValueError('不是旧版LlamaIndex KnowledgeGraphIndex索引；不能安全修改')
    struct = json.loads(outer['__data__'])
    if not isinstance(struct.get('embedding_dict'), dict):
        raise ValueError('索引中找不到embedding_dict')
    if struct.get('table') or struct.get('rel_map'):
        raise ValueError('索引存在额外文档/关系缓存映射，不适用本轻量删除器')
    return outer, struct


def _snapshot(folder: Path, *, allow_locked: bool=False) -> dict[str, Any]:
    if not allow_locked and (folder / LOCK_NAME).exists():
        raise RuntimeError('图谱正在写入，暂不能操作')
    graph_file, index_file = folder/'graph_store.json', folder/'index_store.json'
    if not graph_file.is_file() or not index_file.is_file():
        raise FileNotFoundError('指定目录缺少graph_store.json或index_store.json')
    graph_raw, index_raw = graph_file.read_bytes(), index_file.read_bytes()
    graph_json, index_json = json.loads(graph_raw), json.loads(index_raw)
    graph = graph_json.get('graph_dict')
    if not isinstance(graph, dict):
        raise ValueError('graph_store.json缺少graph_dict')
    for source, pairs in graph.items():
        if not isinstance(source, str) or not isinstance(pairs, list):
            raise ValueError('图谱内容格式不正确')
        for pair in pairs:
            if not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(x,str) for x in pair):
                raise ValueError('图谱关系不是[谓词,宾语]字符串对')
    outer, struct = _index_data(index_json)
    triples = {(str(s),str(p),str(o)) for s,pairs in graph.items() for p,o in pairs}
    bad = []
    for key in struct['embedding_dict']:
        try:
            t = ast.literal_eval(key)
        except (SyntaxError, ValueError):
            bad.append(key)
            continue
        if not isinstance(t, tuple) or len(t) != 3 or t not in triples:
            bad.append(key)
    if bad:
        raise ValueError(f'索引中存在{len(bad)}条无法对应图谱的向量，拒绝操作，请先修复索引')
    for store_name in ('default__vector_store.json','image__vector_store.json'):
        fp = folder/store_name
        if fp.exists():
            vs = json.loads(fp.read_text(encoding='utf-8'))
            if vs.get('embedding_dict'):
                raise ValueError(f'{store_name}有外部向量，不适用本轻量删除器')
    return {'graph_raw':graph_raw,'index_raw':index_raw,
            'graph_json':graph_json,'index_json':index_json,'outer':outer,'struct':struct,
            'triples':triples,'graph':graph,
            'version':{'graph_sha256':_sha(graph_raw),'index_sha256':_sha(index_raw)}}


def incident_edges(graph: dict, entity: str) -> list[tuple[str,str,str]]:
    """Both directions; include nodes that only appear as object."""
    return sorted({(s,rel,obj) for s, pairs in graph.items() for rel,obj in pairs if s==entity or obj==entity})


def plan_deletion(folder: str|Path, *, entity: str|None=None,
                  triple: tuple[str,str,str]|None=None, include_inverse: bool=True) -> dict:
    folder = Path(folder).resolve()
    if (entity is None) == (triple is None):
        raise ValueError('必须且只能指定实体或一条三元组')
    snap = _snapshot(folder)
    triples = snap['triples']
    if entity is not None:
        entity = entity.strip()
        if not entity: raise ValueError('实体名称不能为空')
        found = {t for t in triples if entity in (t[0],t[2])}
        if not found: raise ValueError('没有找到与该实体关联的关系；简单图谱不保存孤立节点')
        mode,target = 'entity', entity
    else:
        if not isinstance(triple,(list,tuple)) or len(triple)!=3:
            raise ValueError('三元组必须是三项')
        triple = tuple(str(x) for x in triple)
        if triple not in triples: raise ValueError('当前图谱中已不存在这条关系')
        found = {triple}
        inverted = INVERSES.get(triple[1])
        if include_inverse and inverted:
            inv = (triple[2],inverted,triple[0])
            if inv in triples: found.add(inv)
        mode,target = 'triple',list(triple)
    keys = snap['struct']['embedding_dict']
    removed_keys = sorted(k for k in keys if ast.literal_eval(k) in found)
    return {'mode':mode, 'target':target, 'include_inverse':bool(include_inverse),
            'triples_to_remove':[list(t) for t in sorted(found)],
            'triple_count_before':len(triples), 'triple_count_after':len(triples-found),
            'embedding_count_before':len(keys),'embedding_count_after':len(keys)-len(removed_keys),
            'embeddings_to_remove':removed_keys,'version':snap['version']}


def _atomic_json_write(path: Path, obj: dict):
    """Single-file atomic replacement; paired files protected by lock and rollback."""
    raw = json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    fd, tmp_path = tempfile.mkstemp(prefix='._kg_edit_',suffix='.json',dir=str(path.parent))
    try:
        with os.fdopen(fd,'wb') as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp_path,path)
    finally:
        if os.path.exists(tmp_path): os.unlink(tmp_path)


def commit_deletion(folder: str|Path, plan: dict) -> dict:
    folder = Path(folder).resolve()
    lock = folder/LOCK_NAME
    fd = None
    try:
        fd = os.open(str(lock),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        os.write(fd,b'Graph management commit in progress\n')
    except FileExistsError as exc:
        raise RuntimeError('已有其他程序正在更新图谱，请稍后操作') from exc
    backup = None
    try:
        # Load and verify the preview inside the write lock.
        snap = _snapshot(folder,allow_locked=True)
        if plan.get('version')!=snap['version']:
            raise RuntimeError('图谱在预览后已改变，请重新预览再删除')
        targets = {tuple(t) for t in plan.get('triples_to_remove',[])}
        if not targets or not targets.issubset(snap['triples']):
            raise RuntimeError('拟删除关系已经改变，请重新预览')
        # Prevent forged or stale preview from deleting a different set.
        fresh = plan_deletion_unlocked(snap, plan)
        if targets != {tuple(t) for t in fresh['triples_to_remove']}:
            raise RuntimeError('预览内容与当前操作不一致，请重新预览')
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        backup = folder.with_name(folder.name + '_backup_delete_' + stamp)
        shutil.copytree(folder,backup,ignore=shutil.ignore_patterns(LOCK_NAME,LOCK_NAME+'.internal'))
        graph_copy = snap['graph_json']
        graph_copy['graph_dict'] = {
            s:[[p,o] for p,o in pairs if (s,p,o) not in targets]
            for s,pairs in snap['graph'].items()
            if any((s,p,o) not in targets for p,o in pairs)
        }
        outer, struct = _index_data(snap['index_json'])
        embedding_count_before = len(struct['embedding_dict'])
        for key in list(struct['embedding_dict']):
            if ast.literal_eval(key) in targets:
                del struct['embedding_dict'][key]
        outer['__data__']=json.dumps(struct,ensure_ascii=False)
        # Validate consistency before replacing live files.
        current = {(s,p,o) for s,pairs in graph_copy['graph_dict'].items() for p,o in pairs}
        if current!=snap['triples']-targets:
            raise RuntimeError('删除后图谱校验未通过')
        if any(ast.literal_eval(k) not in current for k in struct['embedding_dict']):
            raise RuntimeError('删除后索引含悬空向量')
        try:
            _atomic_json_write(folder/'graph_store.json',graph_copy)
            _atomic_json_write(folder/'index_store.json',snap['index_json'])
            _snapshot(folder,allow_locked=True)  # Verify persisted graph / embeddings.
        except Exception:
            # Restore original bytes from the trusted, complete backup.
            for name in ('graph_store.json','index_store.json'):
                shutil.copy2(backup/name,folder/name)
            raise
        return {'removed_triples':len(targets),'removed_embeddings':embedding_count_before-len(struct['embedding_dict']),
                'backup':str(backup),'remaining_triples':len(current),'remaining_embeddings':len(struct['embedding_dict'])}
    finally:
        if fd is not None: os.close(fd)
        lock.unlink(missing_ok=True)


def plan_deletion_unlocked(snap: dict, plan: dict) -> dict:
    """Recompute target edges under the write lock without reading files again."""
    entity = plan.get('target') if plan.get('mode')=='entity' else None
    triple = tuple(plan['target']) if plan.get('mode')=='triple' else None
    triples = snap['triples']
    if entity is not None:
        chosen = {t for t in triples if entity in (t[0],t[2])}
    elif triple is not None and triple in triples:
        chosen = {triple}
        inverted = INVERSES.get(triple[1])
        if plan.get('include_inverse') and inverted:
            rev = (triple[2],inverted,triple[0])
            if rev in triples:chosen.add(rev)
    else:
        chosen=set()
    return {'triples_to_remove':[list(t) for t in sorted(chosen)]}

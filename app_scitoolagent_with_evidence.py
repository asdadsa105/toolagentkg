"""Unified SciToolAgent Streamlit console.

Document upload + DeepSeek extraction + review + incremental index update
and the existing BGE-M3/Jev/DeepSeek/ToolsAgent workflow on one page.
No manual Excel authoring or Neo4j required.
"""
from __future__ import annotations
import asyncio
import csv
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import re

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from text_ingestion.excel_exporter import export_excel
from text_ingestion.normalize import TOOL_COLUMNS, TRIPLE_COLUMNS
from unified_services import (
    MAIN_KG, TEST_KG, create_text_run, extract_to_excel, find_graph_evidence,
    ask_graph_deepseek, kg_dir, invoke_incremental, read_graph, entity_edges,
)
from scripts.tool_registry import registered_tool_names

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'example.env', override=False)
st.set_page_config(page_title='SciToolAgent · 智能知识图谱工作台',page_icon='🧪',layout='wide')
st.title('🧪 SciToolAgent · 智能知识图谱工作台')
st.caption('上传文本 → DeepSeek抽取 → 审核并增量构图 → BGE-M3 / Jev / DeepSeek问答与证据展示')


def triples_csv(triples):
    buf=io.StringIO()
    w=csv.writer(buf)
    w.writerow(['Subject','Predicate','Object'])
    w.writerows(triples)
    return '\ufeff'+buf.getvalue()


def dot_graph(triples, special=()):
    nodes=sorted({s for s,_,_ in triples}|{o for _,_,o in triples})
    ids={n:f'n{i}' for i,n in enumerate(nodes)}
    lines=['digraph SciToolKG {','rankdir=LR;',
           'graph [pad="0.15", nodesep="0.28", ranksep="0.45"];',
           'node [fontname="Arial", fontsize=10];',
           'edge [fontname="Arial", fontsize=9, color="#63788e"];']
    mark=set(special)
    for name in nodes:
        label=name if len(name)<=65 else name[:62]+'…'
        attrs={'label':label,'shape':'box' if name in mark else 'ellipse',
               'style':'rounded,filled' if name in mark else 'filled',
               'fillcolor':'#D9EAFB' if name in mark else '#F3F6F9',
               'color':'#4283b5' if name in mark else '#A7B6C5'}
        lines.append(ids[name]+' ['+', '.join(f'{k}={json.dumps(v,ensure_ascii=False)}' for k,v in attrs.items())+'];')
    for s,r,o in triples:
        lines.append(f'{ids[s]} -> {ids[o]} [label={json.dumps(r,ensure_ascii=False)}];')
    lines.append('}')
    return '\n'.join(lines)


def graph_state(selected: str):
    # Only create the test copy when actually needed.
    return kg_dir(selected)


with st.sidebar:
    st.header('运行配置')
    selected_kg=st.selectbox('当前知识图谱',['测试图谱','正式图谱'],key='kg_selection',
                             help='建议先在测试图谱验证；正式图谱是项目原有的BGE-M3索引。')
    try:
        chosen=TEST_KG if selected_kg=='测试图谱' else MAIN_KG
        if chosen.is_dir():
            graph=read_graph(chosen)
            triple_num=sum(len(v) for v in graph.values())
            st.caption(f'当前已存储：{len(graph)}个主语节点 / {triple_num}条边（含可能重复的边）')
        else:
            st.info('测试图谱尚未创建；首次预检或问答时会从正式图谱复制。')
    except Exception as exc:
        st.warning(f'无法读取图谱统计：{exc}')
    st.divider()
    jev_mode=st.selectbox('Jev工具候选处理',['off','shadow','rerank','filter'],
                          index=['off','shadow','rerank','filter'].index(os.getenv('JEV_MODE','off') if os.getenv('JEV_MODE','off') in ['off','shadow','rerank','filter'] else 'off'),
                          help='仅对工具Agent问答生效；图谱事实问答不执行工具。')
    st.caption('工具Agent需要另外启动 ToolsAgent/main.py（端口60002）。')
    st.caption('新文档中的工具只有在ToolsAgent注册后才允许执行。')

upload_tab,qa_tab,browse_tab=st.tabs(['📤 上传文本与构建图谱','💬 智能问答','🕸️ 图谱浏览'])

with upload_tab:
    st.subheader('1. 上传本地文档')
    st.write('支持 `.txt`、`.md`、`.markdown`。上传后由程序自动生成Excel中间文件；你不需要自己填写。')
    upload=st.file_uploader('选择文本文件',type=['txt','md','markdown'],accept_multiple_files=True)
    c1,c2,c3=st.columns(3)
    with c1: chunk_size=st.number_input('Chunk最大Token数',min_value=100,max_value=6000,value=1200,step=100)
    with c2: overlap=st.number_input('重叠Token数',min_value=0,max_value=1000,value=100,step=50)
    with c3: device=st.selectbox('新增向量使用设备',['cuda:0','cpu'])
    if overlap>=chunk_size:
        st.error('重叠Token必须小于Chunk大小。')
    raw_upload=[]
    if upload:
        raw_upload=[(p.name,p.getvalue()) for p in upload]
        signature=sha256(b''.join(name.encode()+sha256(data).digest() for name,data in raw_upload)+f'{chunk_size}:{overlap}'.encode()).hexdigest()
        if signature!=st.session_state.get('current_upload_signature'):
            st.session_state['current_upload_signature']=signature
            for key in ['pending_run','pending_tables','pending_chunks','last_ingest_log','last_preflight',
                        'review_confirmation','prod_confirmation']:
                st.session_state.pop(key,None)
    col_preview,col_extract=st.columns(2)
    with col_preview:
        preview_clicked=st.button('① 预览Chunk（不调用API）',disabled=not bool(upload) or overlap>=chunk_size)
    with col_extract:
        extract_clicked=st.button('② DeepSeek抽取并生成审核表',type='primary',disabled=not bool(upload) or overlap>=chunk_size)

    if preview_clicked or extract_clicked:
        try:
            run,chunks=create_text_run(raw_upload,int(chunk_size),int(overlap))
            st.session_state['pending_run']=str(run)
            st.session_state['pending_chunks']=chunks
            if extract_clicked:
                prog=st.progress(0,text='正在解析Chunk...')
                def progress(i,total):
                    prog.progress(i/total,text=f'DeepSeek抽取进度：{i}/{total} Chunk')
                with st.spinner('DeepSeek正在抽取实体与关系；相同Chunk会优先使用已保存的API响应缓存。'):
                    tables=extract_to_excel(run,chunks,on_progress=progress)
                st.session_state['pending_tables']=tables
                st.session_state['last_preflight']=False
                st.success('已生成可审核内容。请检查下方Tools/Triples/Review，再预检并入库。')
            else:
                st.info('已完成切块预览：未调用DeepSeek，未修改知识图谱。')
        except Exception as exc:
            st.error(f'文本处理失败：{type(exc).__name__}: {exc}')

    chunks=st.session_state.get('pending_chunks')
    if chunks:
        with st.expander(f'查看Chunk预览（共{len(chunks)}块）',expanded=not bool(st.session_state.get('pending_tables'))):
            st.dataframe([{'ChunkID':c.chunk_id,'文件':Path(c.file_path).name,'章节':c.section,
                           '起始行':c.start_line,'结束行':c.end_line,'文本预览':c.text[:230]} for c in chunks],
                         hide_index=True,use_container_width=True)
            st.caption('完整Chunk文本保存在本次运行目录的chunks.json中。')

    tables=st.session_state.get('pending_tables')
    if tables:
        st.divider()
        st.subheader('2. 审核结构化结果')
        a,b,c,d=st.columns(4)
        a.metric('工具候选',len(tables['Tools']))
        b.metric('额外三元组',len(tables['Triples']))
        c.metric('证据记录',len(tables['Evidence']))
        d.metric('待审核项',len(tables['Review']))
        run=Path(st.session_state['pending_run'])
        with st.expander('Tools · 可直接在网页修改工具字段',expanded=True):
            edited_tools=st.data_editor(pd.DataFrame(tables['Tools'],columns=TOOL_COLUMNS),
                                        num_rows='dynamic',hide_index=True,use_container_width=True,
                                        key='editor_tools_'+run.name)
        with st.expander('Triples · 可直接在网页修改额外三元组'):
            edited_triples=st.data_editor(pd.DataFrame(tables['Triples'],columns=TRIPLE_COLUMNS),
                                          num_rows='dynamic',hide_index=True,use_container_width=True,
                                          key='editor_triples_'+run.name)
        for name,desc in [('Evidence','原文证据'),('Review','抽取中被拒绝或存在冲突的记录')]:
            with st.expander(f'{name} · {desc}',expanded=name=='Review'):
                st.dataframe(pd.DataFrame(tables[name]),hide_index=True,use_container_width=True)
        if st.button('保存网页审核调整（可选）'):
            updated=dict(tables)
            updated['Tools']=edited_tools.fillna('').to_dict('records')
            updated['Triples']=edited_triples.fillna('').to_dict('records')
            export_excel(updated,run/'review.xlsx',overwrite=True)
            st.session_state['pending_tables']=updated
            st.session_state['last_preflight']=False
            st.success('人工修改已经保存到内部审核文件。请重新进行增量预检。')
        st.download_button('下载审核Excel（可选）',data=(run/'review.xlsx').read_bytes(),
                           file_name='extracted_review.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.caption('系统内部会使用该Excel调用已有incremental_from_excel.py；不需要手动编辑Excel。')
        if not tables['Tools'] and not tables['Triples']:
            st.warning('本次没有可入库记录。普通叙述性文档目前无法自动形成通用事实图谱；抽取器仍以科学工具及其关系为主。')
        else:
            if st.button('③ 对当前图谱进行增量预检',type='secondary'):
                try:
                    target=graph_state(selected_kg)
                    with st.spinner('预检中：不会写入任何图谱文件...'):
                        result=invoke_incremental(run/'review.xlsx',target,commit=False)
                    st.session_state['last_preflight']=True
                    st.session_state['last_preflight_run']=str(run)
                    st.session_state['last_preflight_kg']=str(target)
                    st.code(result,language='text')
                except Exception as exc:
                    st.session_state['last_preflight']=False
                    st.error(str(exc))
            st.divider()
            st.subheader('3. 确认入库')
            if selected_kg=='正式图谱':
                st.warning('目前选择的是正式图谱。写入前会自动备份，但推荐先在测试图谱验证。')
            else:
                st.info('目前选择的是测试图谱；首次写入时会自动复制正式图谱，正式索引不会改变。')
            review_ok=st.checkbox('我已检查Tools和Review；同意只导入通过校验的记录',key='review_confirmation')
            prod_ok=True
            if selected_kg=='正式图谱':
                prod_ok=st.checkbox('我确认要修改正式知识图谱，并已检查工具的安全属性',key='prod_confirmation')
            if st.button('④ 写入选定知识图谱并更新BGE-M3索引',type='primary',
                         disabled=not (review_ok and prod_ok and st.session_state.get('last_preflight')
                                       and st.session_state.get('last_preflight_run')==str(run)
                                       and st.session_state.get('last_preflight_kg')==str(TEST_KG if selected_kg=='测试图谱' else MAIN_KG))):
                try:
                    target=graph_state(selected_kg)
                    with st.spinner('正在执行增量写入与BGE-M3更新，请勿关闭页面...'):
                        report=invoke_incremental(run/'review.xlsx',target,commit=True,device=device)
                    st.session_state['last_ingest_log']=report
                    st.session_state['last_preflight']=False
                    st.success('增量流程已结束。下方问答将重新读取当前图谱。')
                    st.code(report,language='text')
                except Exception as exc:
                    st.error(f'入库失败：{exc}')
            if st.session_state.get('last_ingest_log'):
                with st.expander('最近一次入库日志'):
                    st.code(st.session_state['last_ingest_log'],language='text')

with qa_tab:
    st.subheader('科学工具Agent与图谱证据问答')
    route=st.radio('选择问答方式',options=['科学工具Agent（Jev + DeepSeek + 执行）','图谱证据问答（DeepSeek只回答图谱事实）'],
                   help='新增但未注册的工具和实体，请先用图谱证据问答；实际计算选工具Agent。')
    with st.form('unified_question_form'):
        question=st.text_area('输入问题',value='What is the exact molecular weight of ethanol?' if route.startswith('科学工具') else 'NameToSMILES 输出什么？',height=105)
        submitted=st.form_submit_button('开始问答',type='primary')
    if submitted:
        question=question.strip()
        if not question:
            st.warning('请输入问题')
        else:
            try:
                selected_folder=graph_state(selected_kg)
                if (selected_folder/'.scitoolagent_kg.lock').exists():
                    raise RuntimeError('所选图谱正在写入，请完成构图后再问答')
                if route.startswith('科学工具'):
                    os.environ['JEV_MODE']=jev_mode
                    from scripts.retrieve_tool_info import run_SciToolAgent
                    with st.spinner('BGE-M3检索 → Jev工具筛选 → DeepSeek规划 → ToolsAgent执行...'):
                        output=asyncio.run(run_SciToolAgent(question,[],False,kg_dir=str(selected_folder)))
                    st.session_state['qa_last']={'mode':'agent','question':question,'output':output,'kg':str(selected_folder)}
                else:
                    g=read_graph(selected_folder)
                    evidence,anchors=find_graph_evidence(question,g)
                    if evidence:
                        with st.spinner('DeepSeek正在根据图谱证据生成答案...'):
                            answer=ask_graph_deepseek(question,evidence)
                    else:
                        answer='当前图谱没有检索到足够证据，无法回答。'
                    st.session_state['qa_last']={'mode':'kg','question':question,'output':answer,
                                                  'evidence':evidence,'anchors':anchors,'kg':str(selected_folder)}
            except Exception as exc:
                st.error(f'问答失败：{type(exc).__name__}: {exc}')
                st.caption('工具执行需先单独启动ToolsAgent；若是测试图谱新工具，需先注册Python函数。')
    last=st.session_state.get('qa_last')
    if last:
        st.caption(f"最近一次问答：{last['question']}  |  来源图谱：{last['kg']}")
        st.subheader('回答')
        output=last['output']
        if last['mode']=='agent' and '**Final Answer:**' in output:
            st.markdown(output.rsplit('**Final Answer:**',1)[-1].strip())
        else:
            st.markdown(output)
        if last['mode']=='agent':
            with st.expander('完整Agent执行日志'):
                st.markdown(output)
            tool_calls=re.findall(r'Now we have run the\s+\*\*([^*\r\n]+)\*\*\s+and obtained result',output,re.I)
            if tool_calls:
                st.markdown('**实际执行工具：** '+' → '.join(f'`{n}`' for n in tool_calls))
                try:
                    g=read_graph(Path(last['kg']))
                    ev=list(dict.fromkeys((name,str(p),str(o)) for name in tool_calls for p,o in g.get(name,[])))
                    st.graphviz_chart(dot_graph(ev,tool_calls),use_container_width=True)
                    with st.expander(f'查看本次工具的{len(ev)}条一阶图谱三元组'):
                        st.dataframe(pd.DataFrame(ev,columns=['Subject','Predicate','Object']),use_container_width=True)
                    st.download_button('导出工具证据CSV',data=triples_csv(ev),file_name='agent_evidence.csv',mime='text/csv')
                except Exception as exc:
                    st.warning('当前无法加载执行工具证据：'+str(exc))
            else:
                st.caption('本次回答没有可确认的真实执行工具记录。')
        else:
            ev=last.get('evidence',[])
            if ev:
                st.caption('字面实体/关键词锚定：'+', '.join(last.get('anchors',[])))
                with st.expander(f'图谱检索证据（{len(ev)}条）',expanded=True):
                    st.dataframe(pd.DataFrame([{'编号':f'E{i}','主语':s,'关系':p,'宾语':o}
                                               for i,(s,p,o) in enumerate(ev,1)]),hide_index=True,use_container_width=True)
                st.graphviz_chart(dot_graph(ev,last.get('anchors',[])),use_container_width=True)
                st.download_button('导出图谱证据CSV',data=triples_csv(ev),file_name='kg_qa_evidence.csv',mime='text/csv')
                st.caption('本模式使用本地图谱的字面实体/关键词匹配和至多三跳扩展；不是完整语义RAG，也不执行工具。')

with browse_tab:
    st.subheader('浏览本地图谱')
    st.caption('浏览直接从所选索引的graph_store.json读取，不依赖Neo4j，不修改存储。')
    with st.form('entity_browser'):
        entity_name=st.text_input('实体名称（例如 NameToSMILES、SMILES）',value='NameToSMILES')
        browse_submit=st.form_submit_button('查看实体及其相邻关系')
    if browse_submit:
        try:
            g=read_graph(graph_state(selected_kg))
            name=entity_name.strip()
            ev=entity_edges(g,name,max_edges=60)
            if not ev:
                st.warning(f'图谱中未找到实体「{name}」的直接输出边。')
            else:
                st.success(f'找到{len(ev)}条直接输出关系')
                st.graphviz_chart(dot_graph(ev,[name]),use_container_width=True)
                st.dataframe(pd.DataFrame(ev,columns=['Subject','Predicate','Object']),use_container_width=True,hide_index=True)
        except Exception as exc:
            st.error(f'图谱浏览失败：{exc}')

st.divider()
st.caption('已保留原始Agent执行链；新增文本入库和图谱证据问答均使用选择的本地图谱。Neo4j不会自动同步。')

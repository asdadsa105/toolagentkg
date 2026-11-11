"""CLI entry for conservative entity/relationship fusion.

Default action: preview only (no KG mutation).
Example:
  python fusion_from_excel.py --excel data/ingestion_runs/xxx/review.xlsx \
      --kg-dir KG/storage_graph_bge_m3_workspace
  python fusion_from_excel.py --excel ... --kg-dir ... --commit --device cpu
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from kg_fusion.merge_planner import make_fusion_plan
from text_ingestion.excel_exporter import export_excel
from unified_services import invoke_incremental


def main():
    parser=argparse.ArgumentParser(description='证据驱动的旧实体补充、新实体融合入库')
    parser.add_argument('--excel',required=True)
    parser.add_argument('--kg-dir',default='KG/storage_graph_bge_m3_workspace')
    parser.add_argument('--output',default='data/fusion_ready.xlsx')
    parser.add_argument('--approve-source',action='append',default=[],
                        help='来源补充ID，需从预览中的source_options字段复制')
    parser.add_argument('--commit',action='store_true',help='确认后实际写入（默认仅预检）')
    parser.add_argument('--device',default='cpu',choices=['cpu','cuda:0'])
    args=parser.parse_args()
    plan=make_fusion_plan(args.excel,args.kg_dir,args.approve_source)
    print(json.dumps({k:v for k,v in plan.items() if k!='tables'},ensure_ascii=False,indent=2))
    dest=Path(args.output).resolve()
    export_excel(plan['tables'],dest,overwrite=True)
    report=dest.with_suffix('.fusion_report.json')
    report.write_text(json.dumps({k:v for k,v in plan.items() if k!='tables'},ensure_ascii=False,indent=2),encoding='utf-8')
    print('融合入库文件:',dest)
    print('融合审核记录:',report)
    if not plan['new_tools'] and not plan['accepted_triples']:
        print('没有待新增的安全记录；无须启动增量入库。')
        return
    print(invoke_incremental(dest,Path(args.kg_dir).resolve(),commit=args.commit,device=args.device))

if __name__=='__main__':
    main()

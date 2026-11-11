"""Manage deletions in the local SciToolAgent KG (run from project root).

Examples:
  python graph_manage.py --kg-dir KG/storage_graph_bge_m3_workspace --entity KGFusionTestTool
  python graph_manage.py --kg-dir KG/storage_graph_bge_m3_workspace --entity KGFusionTestTool --apply --confirm DELETE
  python graph_manage.py --kg-dir KG/storage_graph_bge_m3_workspace --triple NameToSMILES uses FusionMarker_Z91
"""
import argparse
import json
from pathlib import Path
from kg_management.manager import plan_deletion, commit_deletion


def main():
    p=argparse.ArgumentParser(description='本地SciToolAgent知识图谱安全删减工具')
    p.add_argument('--kg-dir',default='KG/storage_graph_bge_m3_workspace')
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--entity',help='删除此实体以及所有入边、出边')
    g.add_argument('--triple',nargs=3,metavar=('SUBJECT','PREDICATE','OBJECT'),help='删除单条关系')
    p.add_argument('--no-inverse',action='store_true',help='不联动删除inputs/outputs的反向关系')
    p.add_argument('--apply',action='store_true',help='确认写入（默认只预览）')
    p.add_argument('--confirm',default='',help='实际写入需要明确传入DELETE')
    args=p.parse_args()
    folder=Path(args.kg_dir).resolve()
    plan=plan_deletion(folder,entity=args.entity,triple=tuple(args.triple) if args.triple else None,
                       include_inverse=not args.no_inverse)
    print(json.dumps(plan,ensure_ascii=False,indent=2))
    if args.apply:
        if args.confirm!='DELETE':
            p.error('实际删除必须添加 --confirm DELETE')
        result=commit_deletion(folder,plan)
        print('\n删除完成:\n'+json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print('\n只执行删除预览，未修改任何图谱文件。')

if __name__=='__main__':
    main()

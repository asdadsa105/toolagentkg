"""Excel compatibility layer: same schemas as incremental_from_excel.py.

Uses pandas+openpyxl, which are already needed by the existing incremental
script in the target SciToolAgent environment.
"""
from pathlib import Path
import pandas as pd
from .normalize import TOOL_COLUMNS, TRIPLE_COLUMNS, EVIDENCE_COLUMNS, REVIEW_COLUMNS

SCHEMAS = {
    'Tools':TOOL_COLUMNS,
    'Triples':TRIPLE_COLUMNS,
    'Evidence':EVIDENCE_COLUMNS,
    'Review':REVIEW_COLUMNS,
}


def export_excel(tables: dict[str,list[dict]], destination: str | Path, overwrite: bool = False):
    dest=Path(destination)
    if dest.exists() and not overwrite:
        raise FileExistsError(f'{dest} 已存在。审核过的Excel不会被自动覆盖；若确需覆盖请加 --overwrite')
    dest.parent.mkdir(parents=True,exist_ok=True)
    temp=dest.with_name(dest.stem+'.tmp'+dest.suffix)
    try:
        with pd.ExcelWriter(temp,engine='openpyxl') as writer:
            for tab,cols in SCHEMAS.items():
                frame=pd.DataFrame(tables.get(tab,[]),columns=cols).fillna('')
                frame.to_excel(writer,sheet_name=tab,index=False)
                ws=writer.sheets[tab]
                ws.freeze_panes='A2'
                ws.auto_filter.ref=ws.dimensions
                from openpyxl.styles import PatternFill, Font, Alignment
                for cell in ws[1]:
                    cell.fill=PatternFill('solid',fgColor='163A5F')
                    cell.font=Font(bold=True,color='FFFFFF')
                    cell.alignment=Alignment(vertical='center')
                widths={'Function':55,'Quote':70,'Reason':55,'Data':55,'Object':40,'SourceFile':45,'Name':24,'Subject':28,'Predicate':27,'Input':25,'Output':25}
                from openpyxl.utils import get_column_letter
                for i,c in enumerate(cols,1):
                    ws.column_dimensions[get_column_letter(i)].width=widths.get(c,21)
                ws.row_dimensions[1].height=25
        temp.replace(dest)
    finally:
        if temp.exists():
            temp.unlink()
    return dest

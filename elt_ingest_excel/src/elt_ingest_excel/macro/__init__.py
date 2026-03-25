"""VBA Macro analysis and execution utilities for Excel workbooks."""

from elt_ingest_excel.macro.vba_analyzer import (
    VbaMacroAnalyzer,
    VbaAnalysisResult,
    VbaMacro,
    list_vba_entry_points,
    analyze_workbook_macros,
)

__all__ = [
    "VbaMacroAnalyzer",
    "VbaAnalysisResult",
    "VbaMacro",
    "list_vba_entry_points",
    "analyze_workbook_macros",
]

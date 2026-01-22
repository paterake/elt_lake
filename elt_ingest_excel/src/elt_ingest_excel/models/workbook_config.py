"""Configuration models for workbook and sheet definitions."""

from dataclasses import dataclass, field


@dataclass
class SheetConfig:
    """Configuration for a single worksheet to be loaded.

    Attributes:
        sheet_name: Name of the worksheet in the Excel workbook.
        target_table_name: Name of the DuckDB table to load data into.
        header_row: Row number containing headers (1-indexed, default 1).
        skip_rows: Number of rows to skip before header row (default 0).
    """
    sheet_name: str
    target_table_name: str
    header_row: int = 1
    skip_rows: int = 0


@dataclass
class WorkbookConfig:
    """Configuration for a single Excel workbook.

    Attributes:
        workbook_file_name: Path to the Excel workbook file.
        sheets: List of sheet configurations to process.
    """
    workbook_file_name: str
    sheets: list[SheetConfig] = field(default_factory=list)

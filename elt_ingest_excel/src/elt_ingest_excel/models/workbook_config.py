"""Configuration models for workbook and sheet definitions."""

from dataclasses import dataclass, field


@dataclass
class SheetConfig:
    """Configuration for a single worksheet to be loaded.

    Attributes:
        sheet_name: Name of the worksheet in the Excel workbook.
        target_table_name: Name of the DuckDB table to load data into.
        header_row: Row number containing headers (1-indexed, default 1).
        data_row: Row number where data starts (1-indexed, default is header_row + 1).
    """
    sheet_name: str
    target_table_name: str
    header_row: int = 1
    data_row: int | None = None

    def __post_init__(self):
        """Set data_row default if not provided."""
        if self.data_row is None:
            self.data_row = self.header_row + 1


@dataclass
class WorkbookConfig:
    """Configuration for a single Excel workbook.

    Attributes:
        workbook_file_name: Path to the Excel workbook file.
        sheets: List of sheet configurations to process.
    """
    workbook_file_name: str
    sheets: list[SheetConfig] = field(default_factory=list)

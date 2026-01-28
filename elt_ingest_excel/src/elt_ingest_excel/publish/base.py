"""Base classes and types for Excel publishers."""

from dataclasses import dataclass


@dataclass
class PublishResult:
    """Result of publishing data to a sheet.

    Attributes:
        sheet_name: Name of the sheet written to.
        table_name: Source DuckDB table.
        rows_written: Number of rows written.
        success: Whether the publish succeeded.
        error: Error message if failed, None otherwise.
    """
    sheet_name: str
    table_name: str
    rows_written: int
    success: bool
    error: str | None = None

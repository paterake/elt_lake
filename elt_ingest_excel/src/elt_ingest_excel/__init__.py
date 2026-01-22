"""ELT module for ingesting Excel workbooks into DuckDB.

This module provides functionality to:
- Read Excel workbooks using openpyxl
- Load worksheet data into DuckDB tables
- Configure ingestion via JSON configuration files
- Validate loaded data by outputting table counts

Example usage:

    from elt_ingest_excel import (
        ExcelIngester,
        JsonConfigParser,
    )

    # Load configuration from JSON
    config = JsonConfigParser.from_json(
        "config.json",
        database_path="my_database.duckdb",
    )

    # Run ingestion
    with ExcelIngester(config) as ingester:
        results = ingester.ingest()
        ingester.print_summary(results)
"""

from .models import (
    ExcelIngestConfig,
    WorkbookConfig,
    SheetConfig,
)
from .parsers import JsonConfigParser
from .loaders import ExcelLoader
from .ingester import ExcelIngester, LoadResult
from .excel_reader import ExcelReader

__all__ = [
    # Models
    "ExcelIngestConfig",
    "WorkbookConfig",
    "SheetConfig",
    # Parsers
    "JsonConfigParser",
    # Loaders
    "ExcelLoader",
    # Ingester
    "ExcelIngester",
    "LoadResult",
    # Reader
    "ExcelReader",
]

__version__ = "0.1.0"

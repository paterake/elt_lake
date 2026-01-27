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
    FileType,
    WorkbookConfig,
    SheetConfig,
)
from .parsers import JsonConfigParser
from .loaders import ExcelLoader, ExcelReader
from .writers import SaveMode, DuckDBWriter, WriteResult
from .ingester import ExcelIngester, LoadResult
from .file_ingestor import FileIngestor, TransformResult

__all__ = [
    # Models
    "ExcelIngestConfig",
    "FileType",
    "WorkbookConfig",
    "SheetConfig",
    # Parsers
    "JsonConfigParser",
    # Loaders
    "ExcelLoader",
    "ExcelReader",
    # Writers
    "SaveMode",
    "DuckDBWriter",
    "WriteResult",
    # Ingester
    "ExcelIngester",
    "LoadResult",
    # File Ingestor (main ELT workflow)
    "FileIngestor",
    "TransformResult",
]

__version__ = "0.1.0"

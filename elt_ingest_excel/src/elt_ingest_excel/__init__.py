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
    PublishConfig,
    PublishWorkbookConfig,
    PublishSheetConfig,
)
from .parsers import JsonConfigParser, PublishConfigParser
from .loaders import ExcelLoader, ExcelReader
from .writers import SaveMode, DuckDBWriter, WriteResult
from .publish import ExcelPublisher, PublishResult
from .ingester import ExcelIngester, LoadResult
from .elt_pipeline import FileIngestor, TransformResult

__all__ = [
    # Models - Ingest
    "ExcelIngestConfig",
    "FileType",
    "WorkbookConfig",
    "SheetConfig",
    # Models - Publish
    "PublishConfig",
    "PublishWorkbookConfig",
    "PublishSheetConfig",
    # Parsers
    "JsonConfigParser",
    "PublishConfigParser",
    # Loaders
    "ExcelLoader",
    "ExcelReader",
    # Writers
    "SaveMode",
    "DuckDBWriter",
    "WriteResult",
    # Publisher
    "ExcelPublisher",
    "PublishResult",
    # Ingester
    "ExcelIngester",
    "LoadResult",
    # File Ingestor (main ELTP workflow)
    "FileIngestor",
    "TransformResult",
]

__version__ = "0.1.0"

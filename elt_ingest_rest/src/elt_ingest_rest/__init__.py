"""ELT Ingest REST - A flexible REST API ingestion library."""

from .ingest_rest import (
    IngestConfig,
    IngestConfigJson,
    PaginationConfig,
    PaginationType,
    RestApiIngester,
)

__all__ = [
    "IngestConfig",
    "IngestConfigJson",
    "PaginationConfig",
    "PaginationType",
    "RestApiIngester",
]

__version__ = "0.1.0"

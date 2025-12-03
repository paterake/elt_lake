"""ELT Ingest REST - A flexible REST API ingestion library."""

from .ingest_rest import (
    IngestConfig,
    PaginationConfig,
    PaginationType,
    RestApiIngester,
)

__all__ = [
    "IngestConfig",
    "PaginationConfig",
    "PaginationType",
    "RestApiIngester",
]

__version__ = "0.1.0"

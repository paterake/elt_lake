"""ELT Ingest REST - A flexible REST API ingestion library.

Modular Architecture:
- models/: Data classes (IngestConfig, PaginationConfig, PaginationType)
- parsers/: JSON configuration parser
- strategies/: Pagination strategy implementations
- ingester.py: Main orchestration class

For backwards compatibility, all classes are exported at the top level.
"""

# Import from new modular structure
from .models import IngestConfig, PaginationConfig, PaginationType
from .parsers import JsonConfigParser as IngestConfigJson
from .ingester import RestApiIngester

__all__ = [
    "IngestConfig",
    "IngestConfigJson",
    "PaginationConfig",
    "PaginationType",
    "RestApiIngester",
]

__version__ = "0.2.0"  # Bumped for refactoring

"""Transform module for SQL-based data transformations."""

from .sql_executor import SqlExecutor, TransformResult

__all__ = [
    "SqlExecutor",
    "TransformResult",
]

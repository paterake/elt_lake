"""Main ingester for loading Excel workbooks into DuckDB."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb

from .models import ExcelIngestConfig, WorkbookConfig, SheetConfig
from .loaders import ExcelLoader


@dataclass
class LoadResult:
    """Result of loading a single sheet.

    Attributes:
        workbook_file: Path to the source workbook.
        sheet_name: Name of the source sheet.
        table_name: Name of the target DuckDB table.
        rows_loaded: Number of rows loaded.
        row_count: Verified count from the table after loading.
    """
    workbook_file: str
    sheet_name: str
    table_name: str
    rows_loaded: int
    row_count: int


class ExcelIngester:
    """Ingests Excel workbooks into a DuckDB database.

    This class orchestrates the process of:
    1. Connecting to DuckDB
    2. Reading Excel workbooks
    3. Loading sheets into tables
    4. Validating the loaded data
    """

    def __init__(self, config: ExcelIngestConfig):
        """Initialize the ingester with configuration.

        Args:
            config: Configuration for the ingestion process.
        """
        self.config = config
        self._connection: duckdb.DuckDBPyConnection | None = None

    def __enter__(self):
        """Context manager entry - connect to DuckDB."""
        self._connection = duckdb.connect(str(self.config.database_path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close DuckDB connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def ingest(self) -> list[LoadResult]:
        """Execute the ingestion process.

        Iterates through all configured workbooks and sheets,
        loading each into the target DuckDB tables.

        Returns:
            List of LoadResult objects, one per sheet loaded.

        Raises:
            RuntimeError: If the ingester is not in a context manager.
        """
        if self._connection is None:
            raise RuntimeError("ExcelIngester must be used as a context manager")

        results = []

        for workbook_config in self.config.workbooks:
            workbook_results = self._process_workbook(workbook_config)
            results.extend(workbook_results)

        return results

    def _process_workbook(self, workbook_config: WorkbookConfig) -> list[LoadResult]:
        """Process a single workbook.

        Args:
            workbook_config: Configuration for the workbook.

        Returns:
            List of LoadResult objects for each sheet processed.
        """
        results = []

        with ExcelLoader(workbook_config.workbook_file_name) as loader:
            for sheet_config in workbook_config.sheets:
                result = self._process_sheet(
                    loader,
                    workbook_config.workbook_file_name,
                    sheet_config,
                )
                results.append(result)

        return results

    def _process_sheet(
        self,
        loader: ExcelLoader,
        workbook_file: str,
        sheet_config: SheetConfig,
    ) -> LoadResult:
        """Process a single sheet and load it into DuckDB.

        Args:
            loader: The ExcelLoader instance.
            workbook_file: Path to the workbook file.
            sheet_config: Configuration for the sheet.

        Returns:
            LoadResult with details of the load operation.
        """
        # Load data from the sheet
        data = loader.load_sheet(sheet_config)

        # Load into DuckDB
        rows_loaded = self._load_to_duckdb(data, sheet_config.target_table_name)

        # Validate by getting the count
        row_count = self._get_table_count(sheet_config.target_table_name)

        return LoadResult(
            workbook_file=workbook_file,
            sheet_name=sheet_config.sheet_name,
            table_name=sheet_config.target_table_name,
            rows_loaded=rows_loaded,
            row_count=row_count,
        )

    def _load_to_duckdb(self, data: list[dict[str, Any]], table_name: str) -> int:
        """Load data into a DuckDB table.

        Args:
            data: List of dictionaries to load.
            table_name: Name of the target table.

        Returns:
            Number of rows loaded.
        """
        if not data:
            return 0

        # If replacing data, drop the table first
        if self.config.replace_data:
            self._connection.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Get column names from the first row
        columns = list(data[0].keys())

        # Create table if needed
        if self.config.create_tables:
            # Infer column types from data
            col_types = self._infer_column_types(data, columns)
            col_defs = ", ".join(f'"{col}" {col_types[col]}' for col in columns)
            self._connection.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"
            )

        # Insert data using parameterized queries
        placeholders = ", ".join("?" for _ in columns)
        col_names = ", ".join(f'"{col}"' for col in columns)
        insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

        for row in data:
            values = [row.get(col) for col in columns]
            self._connection.execute(insert_sql, values)

        return len(data)

    def _infer_column_types(
        self, data: list[dict[str, Any]], columns: list[str]
    ) -> dict[str, str]:
        """Infer DuckDB column types from Python data.

        Args:
            data: List of dictionaries containing the data.
            columns: List of column names.

        Returns:
            Dictionary mapping column names to DuckDB types.
        """
        type_map = {}

        for col in columns:
            # Sample values from the data (skip None values)
            sample_values = [row.get(col) for row in data if row.get(col) is not None]

            if not sample_values:
                type_map[col] = "VARCHAR"
                continue

            sample = sample_values[0]

            if isinstance(sample, bool):
                type_map[col] = "BOOLEAN"
            elif isinstance(sample, int):
                type_map[col] = "BIGINT"
            elif isinstance(sample, float):
                type_map[col] = "DOUBLE"
            else:
                type_map[col] = "VARCHAR"

        return type_map

    def _get_table_count(self, table_name: str) -> int:
        """Get the row count from a table.

        Args:
            table_name: Name of the table.

        Returns:
            Number of rows in the table.
        """
        result = self._connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()
        return result[0] if result else 0

    def print_summary(self, results: list[LoadResult]) -> None:
        """Print a summary of the ingestion results.

        Args:
            results: List of LoadResult objects to summarize.
        """
        print("\n" + "=" * 60)
        print("INGESTION SUMMARY")
        print("=" * 60)

        total_rows = 0
        for result in results:
            print(f"\nWorkbook: {result.workbook_file}")
            print(f"  Sheet: {result.sheet_name}")
            print(f"  Table: {result.table_name}")
            print(f"  Rows loaded: {result.rows_loaded}")
            print(f"  Table count: {result.row_count}")

            if result.rows_loaded != result.row_count:
                print(f"  WARNING: Row count mismatch!")

            total_rows += result.row_count

        print("\n" + "-" * 60)
        print(f"Total tables loaded: {len(results)}")
        print(f"Total rows: {total_rows}")
        print("=" * 60 + "\n")

"""Main workflow module for file ingestion and transformation."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Union


class PipelinePhase(Enum):
    """Pipeline phases for controlling execution scope.

    Phases are cumulative - each phase includes all previous phases:
    - INGEST: Extract and load data only
    - TRANSFORM: Ingest + run SQL transformations
    - PUBLISH: Ingest + transform + publish to Excel
    """
    INGEST = "ingest"
    TRANSFORM = "transform"
    PUBLISH = "publish"

import duckdb
import pandas as pd

from .loaders import ExcelReader
from .models import FileType, SheetConfig
from .parsers import JsonConfigParser, PublishConfigParser
from .publish import ExcelPublisherOpenpyxl, ExcelPublisherXlwings, PublishResult
from .writers import SaveMode, DuckDBWriter, WriteResult


@dataclass
class TransformResult:
    """Result of executing a transform SQL file.

    Attributes:
        sql_file: Name of the SQL file executed.
        success: Whether execution succeeded.
        error: Error message if failed, None otherwise.
    """
    sql_file: str
    success: bool
    error: str | None = None


class FileIngestor:
    """Main ELT workflow orchestrator.

    This class orchestrates the full ELT process:
    1. Extract - Read data from source files (Excel, CSV, etc.)
    2. Load - Write raw data to DuckDB tables
    3. Transform - Execute SQL transformations

    Supports multiple file types (EXCEL, DELIMITED), though
    currently only EXCEL is implemented.
    """

    def __init__(
        self,
        config_base_path: Union[str, Path],
        cfg_ingest_path: str,
        cfg_transform_path: str,
        config_name: str,
        data_path: Union[str, Path],
        data_file_name: str,
        database_path: Union[str, Path],
        sheet_filter: str = "*",
        save_mode: SaveMode = SaveMode.RECREATE,
        cfg_publish_path: str | None = None,
        cfg_publish_name: str = "publish.json",
        publisher_type: str = "xlwings",
    ):
        """Initialize the file ingestor.

        Args:
            config_base_path: Base path to the config directory.
            cfg_ingest_path: Relative path to ingest config (e.g., "ingest/finance").
            cfg_transform_path: Relative path to transform config (e.g., "transform/finance").
            config_name: Name of the JSON config file (e.g., "supplier.json").
            data_path: Path to the data files directory.
            data_file_name: Name of the data file to process.
            database_path: Path to DuckDB database file.
            sheet_filter: Sheet name to filter on, or "*" for all sheets.
            save_mode: How to handle existing tables (DROP, RECREATE, OVERWRITE, APPEND).
            cfg_publish_path: Relative path to publish config (e.g., "publish/finance").
            cfg_publish_name: Name of the publish JSON config file.
            publisher_type: Excel publisher to use - "xlwings" (default) or "openpyxl".
                           "xlwings" preserves drawing shapes (requires Excel installed).
                           "openpyxl" works without Excel but may lose shapes in .xlsm files.
        """
        self.config_base_path = Path(config_base_path).expanduser()
        self.cfg_ingest_path = cfg_ingest_path
        self.cfg_transform_path = cfg_transform_path
        self.cfg_publish_path = cfg_publish_path
        self.cfg_publish_name = cfg_publish_name
        self.publisher_type = publisher_type
        self.config_name = config_name
        self.data_path = Path(data_path).expanduser()
        self.data_file_name = data_file_name
        self.database_path = Path(database_path).expanduser()
        self.sheet_filter = sheet_filter
        self.save_mode = save_mode

        # Build full config paths
        self.ingest_config_path = self.config_base_path / cfg_ingest_path / config_name
        self.transform_config_path = self.config_base_path / cfg_transform_path
        self.publish_config_path = (
            self.config_base_path / cfg_publish_path / cfg_publish_name
            if cfg_publish_path else None
        )

        # Configure pandas display
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)

        # Load ingest configuration
        self.config = JsonConfigParser.from_json(
            self.ingest_config_path,
            database_path=str(self.database_path),
        )

        # Find workbook config by filename
        self.workbook = JsonConfigParser.find_workbook(
            self.config,
            self.data_file_name,
        )

        if self.workbook is None:
            raise ValueError(f"No workbook config found for: {data_file_name}")

        # Get sheets (filtered)
        self.sheets = JsonConfigParser.get_sheets(self.workbook, self.sheet_filter)

        # Store results
        self.load_results: list[WriteResult] = []
        self.transform_results: list[TransformResult] = []
        self.publish_results: list[PublishResult] = []

    def extract_and_load(self) -> list[WriteResult]:
        """Execute Extract and Load phases.

        Reads data from source file and writes to DuckDB tables.

        Returns:
            List of WriteResult objects for each sheet processed.
        """
        print("\n" + "=" * 60)
        print("EXTRACT & LOAD PHASE")
        print("=" * 60)
        print(f"Config: {self.ingest_config_path}")
        print(f"Data file: {self.data_path / self.data_file_name}")
        print(f"File type: {self.workbook.file_type.value}")
        print(f"Database: {self.database_path}")
        print(f"Save mode: {self.save_mode.value}")
        print(f"Processing {len(self.sheets)} sheet(s)")

        self.load_results = []

        with DuckDBWriter(self.database_path) as writer:
            for sheet_config in self.sheets:
                result = self._process_sheet(sheet_config, writer)
                if result:
                    self.load_results.append(result)

        self._print_load_summary()
        return self.load_results

    def transform(self) -> list[TransformResult]:
        """Execute Transform phase.

        Reads order.txt from transform config path and executes
        SQL files in the specified order.

        Returns:
            List of TransformResult objects for each SQL file executed.
        """
        print("\n" + "=" * 60)
        print("TRANSFORM PHASE")
        print("=" * 60)
        print(f"Transform path: {self.transform_config_path}")

        order_file = self.transform_config_path / "order.txt"
        if not order_file.exists():
            print(f"No order.txt found at {order_file}")
            return []

        # Read order.txt to get list of SQL files
        sql_files = self._read_order_file(order_file)
        print(f"SQL files to execute: {len(sql_files)}")

        self.transform_results = []

        with duckdb.connect(str(self.database_path)) as conn:
            for sql_file in sql_files:
                result = self._execute_sql_file(conn, sql_file)
                self.transform_results.append(result)

        self._print_transform_summary()
        return self.transform_results

    def publish(self) -> list[PublishResult]:
        """Execute Publish phase.

        Reads publish config and exports transformed data to Excel workbooks.

        Returns:
            List of PublishResult objects for each sheet published.
        """
        print("\n" + "=" * 60)
        print("PUBLISH PHASE")
        print("=" * 60)

        if not self.publish_config_path:
            print("No publish config path configured")
            return []

        if not self.publish_config_path.exists():
            print(f"Publish config not found: {self.publish_config_path}")
            return []

        print(f"Publish config: {self.publish_config_path}")
        print(f"Publisher: {self.publisher_type}")

        # Load publish configuration
        publish_config = PublishConfigParser.from_json(self.publish_config_path)
        print(f"Workbooks to publish: {len(publish_config.workbooks)}")

        self.publish_results = []

        # Select publisher based on type
        if self.publisher_type == "xlwings":
            publisher_class = ExcelPublisherXlwings
        else:
            publisher_class = ExcelPublisherOpenpyxl

        with publisher_class(self.database_path) as publisher:
            self.publish_results = publisher.publish(publish_config)

        self._print_publish_summary()
        return self.publish_results

    def process(
        self,
        run_to_phase: PipelinePhase | str = PipelinePhase.PUBLISH,
    ) -> tuple[list[WriteResult], list[TransformResult], list[PublishResult]]:
        """Execute ELT pipeline up to the specified phase.

        Args:
            run_to_phase: Phase to run up to (inclusive). Can be:
                - PipelinePhase.INGEST or "ingest": Extract and load only
                - PipelinePhase.TRANSFORM or "transform": Ingest + transform
                - PipelinePhase.PUBLISH or "publish": Full pipeline (default)

        Returns:
            Tuple of (load_results, transform_results, publish_results).
            Later phases return empty lists if not executed.
        """
        # Normalize to enum
        if isinstance(run_to_phase, str):
            run_to_phase = PipelinePhase(run_to_phase.lower())

        # Always run ingest
        load_results = self.extract_and_load()

        if run_to_phase == PipelinePhase.INGEST:
            return load_results, [], []

        # Run transform
        transform_results = self.transform()

        if run_to_phase == PipelinePhase.TRANSFORM:
            return load_results, transform_results, []

        # Run publish
        publish_results = self.publish()
        return load_results, transform_results, publish_results

    def _read_order_file(self, order_file: Path) -> list[str]:
        """Read order.txt and return list of SQL file names.

        Args:
            order_file: Path to order.txt file.

        Returns:
            List of SQL file names to execute.
        """
        content = order_file.read_text()
        files = []
        for line in content.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                files.append(line)
        return files

    def _execute_sql_file(
        self,
        conn: duckdb.DuckDBPyConnection,
        sql_file: str,
    ) -> TransformResult:
        """Execute a single SQL file.

        Args:
            conn: DuckDB connection.
            sql_file: Name of the SQL file to execute.

        Returns:
            TransformResult with execution status.
        """
        sql_path = self.transform_config_path / sql_file
        print(f"\n  Executing: {sql_file}")

        if not sql_path.exists():
            error = f"SQL file not found: {sql_path}"
            print(f"    ERROR: {error}")
            return TransformResult(sql_file=sql_file, success=False, error=error)

        try:
            sql_content = sql_path.read_text()

            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]

            for i, statement in enumerate(statements, 1):
                if statement:
                    conn.execute(statement)
                    print(f"    Statement {i} executed")

            print(f"    SUCCESS")
            return TransformResult(sql_file=sql_file, success=True)

        except Exception as e:
            error = str(e)
            print(f"    ERROR: {error}")
            return TransformResult(sql_file=sql_file, success=False, error=error)

    def _process_sheet(
        self,
        sheet_config: SheetConfig,
        writer: DuckDBWriter,
    ) -> WriteResult | None:
        """Process a single sheet.

        Args:
            sheet_config: Configuration for the sheet to process.
            writer: DuckDBWriter instance for database operations.

        Returns:
            WriteResult if data was written, None otherwise.
        """
        print(f"\n  Sheet: {sheet_config.sheet_name}")
        print(f"    Target table: {sheet_config.target_table_name}")
        print(f"    Header row: {sheet_config.header_row}, Data row: {sheet_config.data_row}")

        if self.workbook.file_type == FileType.EXCEL:
            return self._process_excel_sheet(sheet_config, writer)
        elif self.workbook.file_type == FileType.DELIMITED:
            return self._process_delimited_file(sheet_config, writer)
        else:
            raise ValueError(f"Unsupported file type: {self.workbook.file_type}")

    def _process_excel_sheet(
        self,
        sheet_config: SheetConfig,
        writer: DuckDBWriter,
    ) -> WriteResult:
        """Process an Excel sheet.

        Args:
            sheet_config: Configuration for the sheet to process.
            writer: DuckDBWriter instance for database operations.

        Returns:
            WriteResult with details of the write operation.
        """
        reader = ExcelReader(
            file_path=self.data_path / self.data_file_name,
            sheet_name=sheet_config.sheet_name,
            header_row=sheet_config.header_row - 1,  # pandas uses 0-indexed
            dtype=str,
        )
        df = reader.load()

        print(f"    Rows read: {len(df)}")

        # Write to DuckDB
        result = writer.write(df, sheet_config.target_table_name, self.save_mode)

        print(f"    Rows written: {result.rows_written}")

        return result

    def _process_delimited_file(
        self,
        sheet_config: SheetConfig,
        writer: DuckDBWriter,
    ) -> WriteResult:
        """Process a delimited file (CSV, TSV, etc.).

        Args:
            sheet_config: Configuration for the file to process.
            writer: DuckDBWriter instance for database operations.

        Returns:
            WriteResult with details of the write operation.

        Note:
            Not yet implemented. Will be added in future version.
        """
        raise NotImplementedError("DELIMITED file type not yet supported")

    def _print_load_summary(self) -> None:
        """Print a summary of the load results."""
        print("\n" + "-" * 40)
        print("Load Summary:")
        total_rows = 0
        for result in self.load_results:
            print(f"  {result.table_name}: {result.row_count} rows")
            total_rows += result.row_count
        print(f"Total: {len(self.load_results)} tables, {total_rows} rows")

    def _print_transform_summary(self) -> None:
        """Print a summary of the transform results."""
        print("\n" + "-" * 40)
        print("Transform Summary:")
        success_count = sum(1 for r in self.transform_results if r.success)
        fail_count = len(self.transform_results) - success_count

        for result in self.transform_results:
            status = "OK" if result.success else f"FAILED: {result.error}"
            print(f"  {result.sql_file}: {status}")

        print(f"Total: {success_count} succeeded, {fail_count} failed")

    def _print_publish_summary(self) -> None:
        """Print a summary of the publish results."""
        print("\n" + "-" * 40)
        print("Publish Summary:")
        success_count = sum(1 for r in self.publish_results if r.success)
        fail_count = len(self.publish_results) - success_count
        total_rows = sum(r.rows_written for r in self.publish_results if r.success)

        for result in self.publish_results:
            if result.success:
                print(f"  {result.sheet_name}: {result.rows_written} rows")
            else:
                print(f"  {result.sheet_name}: FAILED - {result.error}")

        print(f"Total: {success_count} succeeded, {fail_count} failed, {total_rows} rows written")

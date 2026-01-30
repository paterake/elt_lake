"""Main workflow module for file ingestion and transformation."""

from enum import Enum
from pathlib import Path
from typing import Union

import pandas as pd

from .loaders import SheetProcessor
from .parsers import JsonConfigParser, PublishConfigParser
from .publish import ExcelPublisherOpenpyxl, ExcelPublisherXlwings, PublishResult
from .reporting import PipelineReporter
from .transform import SqlExecutor, TransformResult
from .writers import SaveMode, DuckDBWriter, WriteResult


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


class FileIngestor:
    """Main ELT workflow orchestrator.

    This class orchestrates the full ELT process by delegating to
    specialized modules:
    1. Extract/Load - SheetProcessor reads source files and writes to DuckDB
    2. Transform - SqlExecutor runs SQL transformations
    3. Publish - ExcelPublisher exports data to Excel workbooks
    4. Reporting - PipelineReporter handles all console output

    Supports multiple file types (EXCEL, DELIMITED), though
    currently only EXCEL is implemented.
    """

    def __init__(
        self,
        config_base_path: Union[str, Path],
        cfg_ingest_path: str,
        cfg_ingest_name: str,
        cfg_transform_path: str,
        cfg_publish_path: str | None = None,
        cfg_publish_name: str | None = None,
        data_path: Union[str, Path] = "",
        data_file_name: str = "",
        database_path: Union[str, Path] = "",
        sheet_filter: str = "*",
        save_mode: SaveMode = SaveMode.RECREATE,
        publisher_type: str = "xlwings",
    ):
        """Initialize the file ingestor.

        Args:
            config_base_path: Base path to the config directory.
            cfg_ingest_path: Relative path to ingest config (e.g., "ingest/finance").
            cfg_ingest_name: Name of the ingest JSON config file (e.g., "supplier.json").
            cfg_transform_path: Relative path to transform config (e.g., "transform/finance").
            cfg_publish_path: Relative path to publish config (e.g., "publish/finance").
            cfg_publish_name: Name of the publish JSON config file.
            data_path: Path to the data files directory.
            data_file_name: Name of the data file to process.
            database_path: Path to DuckDB database file.
            sheet_filter: Sheet name to filter on, or "*" for all sheets.
            save_mode: How to handle existing tables (DROP, RECREATE, OVERWRITE, APPEND).
            publisher_type: Excel publisher to use - "xlwings" (default) or "openpyxl".
                           "xlwings" preserves drawing shapes (requires Excel installed).
                           "openpyxl" works without Excel but may lose shapes in .xlsm files.
        """
        self.config_base_path = Path(config_base_path).expanduser()
        self.cfg_ingest_path = cfg_ingest_path
        self.cfg_ingest_name = cfg_ingest_name
        self.cfg_transform_path = cfg_transform_path
        self.cfg_publish_path = cfg_publish_path
        self.cfg_publish_name = cfg_publish_name
        self.publisher_type = publisher_type
        self.data_path = Path(data_path).expanduser()
        self.data_file_name = data_file_name
        self.database_path = Path(database_path).expanduser()
        self.sheet_filter = sheet_filter
        self.save_mode = save_mode

        # Build full config paths
        self.ingest_config_path = self.config_base_path / cfg_ingest_path / cfg_ingest_name
        self.transform_config_path = self.config_base_path / cfg_transform_path
        self.publish_config_path = (
            self.config_base_path / cfg_publish_path / cfg_publish_name
            if cfg_publish_path
            else None
        )

        # Configure pandas display
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", 50)

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

        # Initialize reporter
        self.reporter = PipelineReporter()

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
        self.reporter.print_extract_load_header(
            config_path=self.ingest_config_path,
            data_file=self.data_path / self.data_file_name,
            file_type=self.workbook.file_type.value,
            database_path=self.database_path,
            save_mode=self.save_mode,
            sheet_count=len(self.sheets),
        )

        # Create sheet processor and delegate extraction/loading
        processor = SheetProcessor(
            data_path=self.data_path,
            data_file_name=self.data_file_name,
            workbook_config=self.workbook,
            save_mode=self.save_mode,
        )

        with DuckDBWriter(self.database_path) as writer:
            self.load_results = processor.process_sheets(self.sheets, writer)

        self.reporter.print_load_summary(self.load_results)
        return self.load_results

    def transform(self) -> list[TransformResult]:
        """Execute Transform phase.

        Reads order.txt from transform config path and executes
        SQL files in the specified order.

        Returns:
            List of TransformResult objects for each SQL file executed.
        """
        self.reporter.print_transform_header(self.transform_config_path)

        # Create SQL executor and delegate transformation
        executor = SqlExecutor(
            transform_path=self.transform_config_path,
            database_path=self.database_path,
        )

        sql_count = executor.get_sql_file_count()
        if sql_count == 0:
            self.reporter.print_transform_no_order_file(
                self.transform_config_path / "order.txt"
            )
            return []

        self.reporter.print_transform_sql_count(sql_count)

        self.transform_results = executor.execute()

        self.reporter.print_transform_summary(self.transform_results)
        return self.transform_results

    def publish(self) -> list[PublishResult]:
        """Execute Publish phase.

        Reads publish config and exports transformed data to Excel workbooks.

        Returns:
            List of PublishResult objects for each sheet published.
        """
        self.reporter.print_publish_header()

        if not self.publish_config_path:
            self.reporter.print_publish_no_config()
            return []

        if not self.publish_config_path.exists():
            self.reporter.print_publish_config_not_found(self.publish_config_path)
            return []

        # Load publish configuration
        publish_config = PublishConfigParser.from_json(self.publish_config_path)

        self.reporter.print_publish_config_info(
            config_path=self.publish_config_path,
            publisher_type=self.publisher_type,
            workbook_count=len(publish_config.workbooks),
        )

        self.publish_results = []

        # Select publisher based on type and delegate publishing
        if self.publisher_type == "xlwings":
            publisher_class = ExcelPublisherXlwings
        else:
            publisher_class = ExcelPublisherOpenpyxl

        with publisher_class(self.database_path) as publisher:
            self.publish_results = publisher.publish(publish_config)

        self.reporter.print_publish_summary(self.publish_results)
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

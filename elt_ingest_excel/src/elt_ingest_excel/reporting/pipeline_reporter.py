"""Pipeline output reporting for ELT process."""

from pathlib import Path

from ..publish import PublishResult
from ..transform import TransformResult
from ..writers import SaveMode, WriteResult


class PipelineReporter:
    """Handles all output reporting for the ELT pipeline.

    Provides formatted console output for each pipeline phase
    including headers, progress details, and summaries.
    """

    SEPARATOR_WIDTH = 60
    SUMMARY_WIDTH = 40

    def print_extract_load_header(
        self,
        config_path: Path,
        data_file: Path,
        file_type: str,
        database_path: Path,
        save_mode: SaveMode,
        sheet_count: int,
    ) -> None:
        """Print header for Extract & Load phase.

        Args:
            config_path: Path to the ingest configuration file.
            data_file: Path to the source data file.
            file_type: Type of file being processed (e.g., "EXCEL").
            database_path: Path to the DuckDB database.
            save_mode: How existing tables are handled.
            sheet_count: Number of sheets to process.
        """
        print("\n" + "=" * self.SEPARATOR_WIDTH)
        print("EXTRACT & LOAD PHASE")
        print("=" * self.SEPARATOR_WIDTH)
        print(f"Config: {config_path}")
        print(f"Data file: {data_file}")
        print(f"File type: {file_type}")
        print(f"Database: {database_path}")
        print(f"Save mode: {save_mode.value}")
        print(f"Processing {sheet_count} sheet(s)")

    def print_transform_header(self, transform_path: Path) -> None:
        """Print header for Transform phase.

        Args:
            transform_path: Path to the transform configuration directory.
        """
        print("\n" + "=" * self.SEPARATOR_WIDTH)
        print("TRANSFORM PHASE")
        print("=" * self.SEPARATOR_WIDTH)
        print(f"Transform path: {transform_path}")

    def print_transform_no_order_file(self, order_file: Path) -> None:
        """Print message when order.txt is not found.

        Args:
            order_file: Path where order.txt was expected.
        """
        print(f"No order.txt found at {order_file}")

    def print_transform_sql_count(self, count: int) -> None:
        """Print number of SQL files to execute.

        Args:
            count: Number of SQL files.
        """
        print(f"SQL files to execute: {count}")

    def print_publish_header(self) -> None:
        """Print header for Publish phase."""
        print("\n" + "=" * self.SEPARATOR_WIDTH)
        print("PUBLISH PHASE")
        print("=" * self.SEPARATOR_WIDTH)

    def print_publish_no_config(self) -> None:
        """Print message when no publish config is configured."""
        print("No publish config path configured")

    def print_publish_config_not_found(self, config_path: Path) -> None:
        """Print message when publish config file is not found.

        Args:
            config_path: Path where config was expected.
        """
        print(f"Publish config not found: {config_path}")

    def print_publish_config_info(
        self,
        config_path: Path,
        publisher_type: str,
        workbook_count: int,
    ) -> None:
        """Print publish configuration details.

        Args:
            config_path: Path to the publish configuration file.
            publisher_type: Type of publisher being used.
            workbook_count: Number of workbooks to publish.
        """
        print(f"Publish config: {config_path}")
        print(f"Publisher: {publisher_type}")
        print(f"Workbooks to publish: {workbook_count}")

    def print_load_summary(self, results: list[WriteResult]) -> None:
        """Print summary of load results.

        Args:
            results: List of WriteResult objects from the load phase.
        """
        print("\n" + "-" * self.SUMMARY_WIDTH)
        print("Load Summary:")
        total_rows = 0
        for result in results:
            print(f"  {result.table_name}: {result.row_count} rows")
            total_rows += result.row_count
        print(f"Total: {len(results)} tables, {total_rows} rows")

    def print_transform_summary(self, results: list[TransformResult]) -> None:
        """Print summary of transform results.

        Args:
            results: List of TransformResult objects from the transform phase.
        """
        print("\n" + "-" * self.SUMMARY_WIDTH)
        print("Transform Summary:")
        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        for result in results:
            status = "OK" if result.success else f"FAILED: {result.error}"
            print(f"  {result.sql_file}: {status}")

        print(f"Total: {success_count} succeeded, {fail_count} failed")

    def print_publish_summary(self, results: list[PublishResult]) -> None:
        """Print summary of publish results.

        Args:
            results: List of PublishResult objects from the publish phase.
        """
        print("\n" + "-" * self.SUMMARY_WIDTH)
        print("Publish Summary:")
        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count
        total_rows = sum(r.rows_written for r in results if r.success)

        for result in results:
            if result.success:
                print(f"  {result.sheet_name}: {result.rows_written} rows")
            else:
                print(f"  {result.sheet_name}: FAILED - {result.error}")

        print(f"Total: {success_count} succeeded, {fail_count} failed, {total_rows} rows written")

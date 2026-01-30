"""Sheet processor for extracting and loading data from various file types."""

from pathlib import Path

from ..models import FileType, SheetConfig, WorkbookConfig
from ..writers import DuckDBWriter, SaveMode, WriteResult
from .excel_reader import ExcelReader


class SheetProcessor:
    """Processes sheets from workbooks and loads them into DuckDB.

    Handles different file types (Excel, delimited) and delegates
    to appropriate readers for data extraction.
    """

    def __init__(
        self,
        data_path: Path,
        data_file_name: str,
        workbook_config: WorkbookConfig,
        save_mode: SaveMode = SaveMode.RECREATE,
    ):
        """Initialize the sheet processor.

        Args:
            data_path: Path to the data files directory.
            data_file_name: Name of the data file to process.
            workbook_config: Configuration for the workbook.
            save_mode: How to handle existing tables.
        """
        self.data_path = Path(data_path)
        self.data_file_name = data_file_name
        self.workbook_config = workbook_config
        self.save_mode = save_mode
        self.file_path = self.data_path / self.data_file_name

    def process_sheets(
        self,
        sheets: list[SheetConfig],
        writer: DuckDBWriter,
    ) -> list[WriteResult]:
        """Process multiple sheets and write to DuckDB.

        Args:
            sheets: List of sheet configurations to process.
            writer: DuckDBWriter instance for database operations.

        Returns:
            List of WriteResult objects for each sheet processed.
        """
        results = []
        for sheet_config in sheets:
            result = self.process_sheet(sheet_config, writer)
            if result:
                results.append(result)
        return results

    def process_sheet(
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

        if self.workbook_config.file_type == FileType.EXCEL:
            return self._process_excel_sheet(sheet_config, writer)
        elif self.workbook_config.file_type == FileType.DELIMITED:
            return self._process_delimited_file(sheet_config, writer)
        else:
            raise ValueError(f"Unsupported file type: {self.workbook_config.file_type}")

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
            file_path=self.file_path,
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

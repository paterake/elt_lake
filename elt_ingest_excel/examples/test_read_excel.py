# examples/test_read_excel.py
"""Example script to read Excel workbooks using JSON configuration."""

from pathlib import Path

import pandas as pd

from elt_ingest_excel import JsonConfigParser, ExcelReader


# Configure pandas display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

# Path to examples directory (where config files are located)
EXAMPLES_DIR = Path(__file__).parent


def load_workbook_config(config_name: str, file_name: str):
    """Load workbook configuration from JSON file.

    Args:
        config_name: Name of the JSON config file (in examples directory).
        file_name: Workbook file name to match in the config.

    Returns:
        WorkbookConfig matching the file_name, or None if not found.
    """
    config_path = EXAMPLES_DIR / config_name
    config = JsonConfigParser.from_json(
        config_path,
        database_path="/tmp/unused.duckdb",  # Not used for reading
    )

    # Expand the file_name for comparison
    file_name_expanded = str(Path(file_name).expanduser())

    # Find the workbook config matching the file_name
    for workbook in config.workbooks:
        workbook_path_expanded = str(Path(workbook.workbook_file_name).expanduser())
        if workbook_path_expanded == file_name_expanded:
            return workbook

    return None


def process_sheets(workbook_config, sheet_name_filter: str = "*"):
    """Process sheets from workbook configuration.

    Args:
        workbook_config: WorkbookConfig with sheet definitions.
        sheet_name_filter: Sheet name to filter on, or "*" for all sheets.

    Yields:
        Tuple of (sheet_config, dataframe, reader) for each matching sheet.
    """
    for sheet_config in workbook_config.sheets:
        # Apply filter
        if sheet_name_filter != "*" and sheet_config.sheet_name != sheet_name_filter:
            continue

        print(f"\n{'='*60}")
        print(f"Processing sheet: {sheet_config.sheet_name}")
        print(f"  Target table: {sheet_config.target_table_name}")
        print(f"  Header row: {sheet_config.header_row}")
        print(f"  Data row: {sheet_config.data_row}")
        print(f"{'='*60}")

        # Create reader with config values
        # Note: pandas uses 0-indexed rows, config uses 1-indexed
        reader = ExcelReader(
            file_path=workbook_config.workbook_file_name,
            sheet_name=sheet_config.sheet_name,
            header_row=sheet_config.header_row - 1,  # Convert to 0-indexed
            dtype=str,
        )

        df = reader.load()
        yield sheet_config, df, reader


if __name__ == "__main__":
    # Configuration
    config_name = "finance_supplier.json"
    file_name = "~/Documents/__data/excel/FA Creditors with Activity Last 3 Years.xlsx"
    sheet_name_filter = "*"  # "*" for all sheets, or specific sheet name

    # Load workbook configuration
    workbook_config = load_workbook_config(config_name, file_name)

    if workbook_config is None:
        print(f"ERROR: No workbook config found for: {file_name}")
        print(f"Check that the file path matches 'workbookFileName' in {config_name}")
        exit(1)

    print(f"Loaded config for: {workbook_config.workbook_file_name}")
    print(f"Sheets defined: {len(workbook_config.sheets)}")

    # Process each matching sheet
    for sheet_config, df, reader in process_sheets(workbook_config, sheet_name_filter):
        reader.preview()
        print(f"\nFirst row as dict:")
        print(df.iloc[0].to_dict())
        print(f"\nTotal rows: {len(df)}")

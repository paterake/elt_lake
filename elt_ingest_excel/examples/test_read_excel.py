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


if __name__ == "__main__":
    # Configuration
    config_name = "finance_supplier.json"
    file_name = "~/Documents/__data/excel/FA Creditors with Activity Last 3 Years.xlsx"
    sheet_name_filter = "*"  # "*" for all sheets, or specific sheet name

    # Load config from JSON
    config = JsonConfigParser.from_json(
        EXAMPLES_DIR / config_name,
        database_path="/tmp/unused.duckdb",
    )

    # Find workbook by file name
    workbook = JsonConfigParser.find_workbook(config, file_name)
    if workbook is None:
        print(f"ERROR: No workbook config found for: {file_name}")
        exit(1)

    # Get sheets (filtered if not "*")
    sheets = JsonConfigParser.get_sheets(workbook, sheet_name_filter)
    print(f"Loaded config for: {workbook.workbook_file_name}")
    print(f"Processing {len(sheets)} sheet(s)")

    # Process each sheet
    for sheet_config in sheets:
        print(f"\n{'='*60}")
        print(f"Sheet: {sheet_config.sheet_name}")
        print(f"  Target table: {sheet_config.target_table_name}")
        print(f"  Header row: {sheet_config.header_row}")
        print(f"  Data row: {sheet_config.data_row}")
        print(f"{'='*60}")

        # Read the sheet (pandas uses 0-indexed rows)
        reader = ExcelReader(
            file_path=workbook.workbook_file_name,
            sheet_name=sheet_config.sheet_name,
            header_row=sheet_config.header_row - 1,
            dtype=str,
        )
        df = reader.load()

        # Output results
        reader.preview()
        print(f"\nFirst row as dict:")
        print(df.iloc[0].to_dict())
        print(f"\nTotal rows: {len(df)}")

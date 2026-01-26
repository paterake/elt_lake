# examples/test_read_excel.py
"""Example script to read Excel workbooks and write to DuckDB."""

from pathlib import Path

from elt_ingest_excel import FileIngestor, SaveMode


# Path to examples directory (where config files are located)
EXAMPLES_DIR = Path(__file__).parent


if __name__ == "__main__":
    # Configuration
    config_name = "finance_supplier.json"
    file_name = "~/Documents/__data/excel/FA Creditors with Activity Last 3 Years.xlsx"
    sheet_name_filter = "Lasst Purchase Date"  # "*" for all sheets, or specific sheet name
    database_path = "~/Documents/__data/duckdb/rpatel.duckdb"
    save_mode = SaveMode.RECREATE  # DROP, RECREATE, OVERWRITE, APPEND

    # Run ingestion workflow
    ingestor = FileIngestor(
        config_path=EXAMPLES_DIR / config_name,
        workbook_file_name=file_name,
        database_path=database_path,
        sheet_filter=sheet_name_filter,
        save_mode=save_mode,
    )
    results = ingestor.process()

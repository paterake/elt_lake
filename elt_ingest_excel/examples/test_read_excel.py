# examples/test_read_excel.py
"""Example script to read Excel workbooks using JSON configuration."""

from pathlib import Path

from elt_ingest_excel import FileIngestor


# Path to examples directory (where config files are located)
EXAMPLES_DIR = Path(__file__).parent


if __name__ == "__main__":
    # Configuration
    config_name = "finance_supplier.json"
    file_name = "~/Documents/__data/excel/FA Creditors with Activity Last 3 Years.xlsx"
    sheet_name_filter = "Lasst Purchase Date"  # "*" for all sheets, or specific sheet name

    # Run ingestion workflow
    ingestor = FileIngestor(
        config_path=EXAMPLES_DIR / config_name,
        workbook_file_name=file_name,
        sheet_filter=sheet_name_filter,
    )
    ingestor.process()

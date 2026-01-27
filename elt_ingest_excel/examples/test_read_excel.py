# examples/test_read_excel.py
"""Example script demonstrating the full ELT pipeline."""

from elt_ingest_excel import FileIngestor, SaveMode


if __name__ == "__main__":
    # Configuration paths (relative to config/ directory)
    cfg_ingest_path = "ingest/finance"
    cfg_transform_path = "transform/finance"
    config_name = "supplier.json"

    # Data file location
    data_path = "~/Documents/__data/excel/finance_ref"
    data_file_name = "FA Creditors with Activity Last 3 Years.xlsx"

    # Database and processing options
    database_path = "~/Documents/__data/duckdb/rpatel.duckdb"
    sheet_name_filter = "*"  # "*" for all sheets, or specific sheet name
    save_mode = SaveMode.RECREATE  # DROP, RECREATE, OVERWRITE, APPEND

    # Create ingestor
    ingestor = FileIngestor(
        cfg_ingest_path=cfg_ingest_path,
        cfg_transform_path=cfg_transform_path,
        config_name=config_name,
        data_path=data_path,
        data_file_name=data_file_name,
        database_path=database_path,
        sheet_filter=sheet_name_filter,
        save_mode=save_mode,
    )

    # Run full ELT pipeline (Extract, Load, Transform)
    load_results, transform_results = ingestor.process()

    # Or run phases separately:
    # load_results = ingestor.extract_and_load()
    # transform_results = ingestor.transform()

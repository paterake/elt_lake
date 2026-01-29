# examples/fin_supplier_creditor.py
"""Example script demonstrating the ELTP pipeline (Extract, Load, Transform, Publish)."""

from pathlib import Path

from elt_ingest_excel import FileIngestor, SaveMode, PipelinePhase


if __name__ == "__main__":
    # Config base path (project root config/ directory)
    # This script is in examples/, config is at ../config/
    config_base_path = Path(__file__).parent.parent / "config"

    # Data file location
    data_path = "~/Documents/__data/excel/finance_ref"
    data_file_name = "FA Debtors Activity Last 3 Years.xlsx"

    # Configuration paths (relative to config_base_path)
    cfg_ingest_path = "ingest/finance"
    cfg_ingest_name = "customer.json"
    cfg_transform_path = "transform/sql/finance/customer"
    cfg_publish_path = "publish/finance"
    cfg_publish_name = "publish_customer.json"

    # Database and processing options
    database_path = "~/Documents/__data/duckdb/rpatel.duckdb"
    sheet_name_filter = "*"  # "*" for all sheets, or specific sheet name
    save_mode = SaveMode.RECREATE  # DROP, RECREATE, OVERWRITE, APPEND

    # Publisher type for Publish phase
    # - "openpyxl": No Excel required, but may lose drawing shapes in .xlsm files
    # - "xlwings": Requires Excel installed, preserves all shapes/macros/formatting
    publisher_type = "xlwings"

    # Pipeline phase to run up to (inclusive)
    # - "ingest" or PipelinePhase.INGEST: Extract and load only
    # - "transform" or PipelinePhase.TRANSFORM: Ingest + SQL transformations
    # - "publish" or PipelinePhase.PUBLISH: Full pipeline (default)
    run_to_phase = PipelinePhase.PUBLISH

    # Create ingestor
    ingestor = FileIngestor(
        config_base_path=config_base_path,
        cfg_ingest_path=cfg_ingest_path,
        cfg_ingest_name=cfg_ingest_name,
        cfg_transform_path=cfg_transform_path,
        cfg_publish_path=cfg_publish_path,
        cfg_publish_name=cfg_publish_name,
        data_path=data_path,
        data_file_name=data_file_name,
        database_path=database_path,
        sheet_filter=sheet_name_filter,
        save_mode=save_mode,
        publisher_type=publisher_type,
    )

    # Run pipeline up to specified phase
    load_results, transform_results, publish_results = ingestor.process(run_to_phase)

    # Or run phases separately:
    # load_results = ingestor.extract_and_load()
    # transform_results = ingestor.transform()
    # publish_results = ingestor.publish()

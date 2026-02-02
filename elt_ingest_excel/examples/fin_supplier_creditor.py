# examples/fin_supplier_creditor.py
"""Pipeline runner for Finance Supplier/Creditor data."""

from base_runner import run_pipeline

if __name__ == "__main__":
    run_pipeline(
        # Data source
        data_path="~/Documents/__data/excel/finance_ref",
        data_file_name="FA Creditors with Activity Last 3 Years.xlsx",
        # Config paths
        cfg_ingest_path="ingest/finance",
        cfg_ingest_name="supplier.json",
        cfg_transform_path="transform/sql/finance/supplier",
        cfg_publish_path="publish/finance",
        cfg_publish_name="publish_supplier.json",
    )

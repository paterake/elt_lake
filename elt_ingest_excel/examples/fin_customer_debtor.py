# examples/fin_customer_debtor.py
"""Pipeline runner for Finance Customer/Debtor data."""

from base_runner import run_pipeline

if __name__ == "__main__":
    run_pipeline(
        # Data source (processes all workbooks defined in config)
        data_path="~/Documents/__data/excel/finance_ref",
        # Config paths
        cfg_ingest_path="ingest/finance",
        cfg_ingest_name="customer.json",
        cfg_transform_path="transform/sql/finance/customer",
        cfg_publish_path="publish/finance",
        cfg_publish_name="publish_customer.json",
    )

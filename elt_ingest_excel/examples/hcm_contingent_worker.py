# examples/hcm_contingent_worker.py
"""Pipeline runner for HCM Contingent Worker data."""

from base_runner import run_pipeline

if __name__ == "__main__":
    run_pipeline(
        # Data source (processes all workbooks defined in config)
        data_path="~/Documents/__data/excel/hcm",
        # Config paths
        cfg_ingest_path="ingest/hcm",
        cfg_ingest_name="contingent_worker.json",
        cfg_transform_path="transform/sql/hcm/contingent_worker",
        cfg_publish_path="publish/hcm",
        cfg_publish_name="publish_contingent_worker.json",
    )

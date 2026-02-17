# examples/hcm_contingent_worker.py
"""Pipeline runner for HCM Contingent Worker data."""

from base_runner import run_pipeline, create_parser
from elt_ingest_excel import PipelinePhase

if __name__ == "__main__":
    parser = create_parser("Run HCM Contingent Worker pipeline")
    args = parser.parse_args()

    run_pipeline(
        data_path="~/Documents/__data/excel/hcm",
        cfg_ingest_path="ingest/hcm",
        cfg_ingest_name="contingent_worker.json",
        cfg_transform_path="transform/sql/hcm/contingent_worker",
        cfg_publish_path="publish/hcm",
        cfg_publish_name="publish_contingent_worker.json",
        run_to_phase=PipelinePhase[args.run_to_phase],
    )

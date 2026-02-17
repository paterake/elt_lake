# examples/fin_customer_debtor.py
"""Pipeline runner for Finance Customer/Debtor data."""

from base_runner import run_pipeline, create_parser
from elt_ingest_excel import PipelinePhase

if __name__ == "__main__":
    parser = create_parser("Run Finance Customer/Debtor pipeline")
    args = parser.parse_args()

    run_pipeline(
        data_path="~/Documents/__data/excel/finance_ref",
        cfg_ingest_path="ingest/finance",
        cfg_ingest_name="customer.json",
        cfg_transform_path="transform/sql/finance/customer",
        cfg_publish_path="publish/finance",
        cfg_publish_name="publish_customer.json",
        run_to_phase=PipelinePhase[args.run_to_phase],
    )

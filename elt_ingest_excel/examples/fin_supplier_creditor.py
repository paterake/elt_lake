# examples/fin_supplier_creditor.py
"""Pipeline runner for Finance Supplier/Creditor data."""

from base_runner import run_pipeline, create_parser
from elt_ingest_excel import PipelinePhase

if __name__ == "__main__":
    parser = create_parser("Run Finance Supplier/Creditor pipeline")
    args = parser.parse_args()

    run_pipeline(
        data_path="~/Documents/__data/excel/finance_ref",
        cfg_ingest_path="ingest/finance",
        cfg_ingest_name="supplier.json",
        cfg_transform_path="transform/sql/finance/supplier",
        cfg_publish_path="publish/finance",
        cfg_publish_name="publish_supplier.json",
        run_to_phase=PipelinePhase[args.run_to_phase],
    )

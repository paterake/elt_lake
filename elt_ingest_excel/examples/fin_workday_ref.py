
# examples/fin_workday_ref.py
"""Pipeline runner for Finance Workday Reference data."""

from pathlib import Path
from base_runner import create_parser
# Import direct publisher components
from elt_ingest_excel.parsers import PublishConfigParser
from elt_ingest_excel.publish import ExcelPublisherOpenpyxl
from elt_ingest_excel.reporting import PipelineReporter

if __name__ == "__main__":
    parser = create_parser("Run Finance Workday Reference pipeline")
    args = parser.parse_args()

    # Define paths
    config_base_path = Path(__file__).parent.parent / "config"
    publish_config_path = config_base_path / "publish/finance/publish_workday_ref.json"
    database_path = Path("~/Documents/__data/duckdb/rpatel.duckdb").expanduser()

    print("--- Starting PUBLISH phase (Direct Publisher Mode) ---")
    
    # 1. Load Configuration
    if not publish_config_path.exists():
        raise FileNotFoundError(f"Config not found: {publish_config_path}")
        
    publish_config = PublishConfigParser.from_json(publish_config_path)
    
    # 2. Run Publisher directly (Skipping Ingest/Transform)
    # Using Openpyxl as we are creating a new file without macro/template requirements
    reporter = PipelineReporter()
    
    with ExcelPublisherOpenpyxl(database_path, reporter=reporter) as publisher:
        results = publisher.publish(publish_config)
        
    reporter.print_publish_summary(results)

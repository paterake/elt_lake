#!/usr/bin/env python3
"""Example script for running Excel ingestion from JSON config.

Usage:
    python run_from_json.py <config_file> <database_path> [--verbose]

Example:
    python run_from_json.py sample_config.json ./output/data.duckdb --verbose
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from elt_ingest_excel import ExcelIngester, JsonConfigParser


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Excel workbooks into DuckDB from JSON config"
    )
    parser.add_argument(
        "config_file",
        type=Path,
        help="Path to JSON configuration file",
    )
    parser.add_argument(
        "database_path",
        type=Path,
        help="Path to DuckDB database file",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed output",
    )
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="Append data instead of replacing",
    )

    args = parser.parse_args()

    # Validate config file exists
    if not args.config_file.exists():
        print(f"Error: Config file not found: {args.config_file}")
        sys.exit(1)

    # Create output directory if needed
    args.database_path.parent.mkdir(parents=True, exist_ok=True)

    # Load configuration
    if args.verbose:
        print(f"Loading config from: {args.config_file}")

    config = JsonConfigParser.from_json(
        args.config_file,
        database_path=args.database_path,
        replace_data=not args.no_replace,
    )

    if args.verbose:
        print(f"Database path: {config.database_path}")
        print(f"Workbooks to process: {len(config.workbooks)}")
        for wb in config.workbooks:
            print(f"  - {wb.workbook_file_name}")
            for sheet in wb.sheets:
                print(f"      {sheet.sheet_name} -> {sheet.target_table_name}")

    # Run ingestion
    print("\nStarting ingestion...")
    with ExcelIngester(config) as ingester:
        results = ingester.ingest()
        ingester.print_summary(results)

    print("Ingestion complete!")


if __name__ == "__main__":
    main()

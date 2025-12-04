#!/usr/bin/env python3
"""Run REST API ingestion from a JSON configuration file."""

import argparse
import sys
from pathlib import Path

from elt_ingest_rest import IngestConfigJson, RestApiIngester


def main():
    """Main entry point for JSON-based ingestion."""
    parser = argparse.ArgumentParser(
        description="Run REST API ingestion from JSON configuration file"
    )
    parser.add_argument(
        "config_file",
        type=Path,
        help="Path to JSON configuration file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Validate config file exists
    if not args.config_file.exists():
        print(f"Error: Config file not found: {args.config_file}", file=sys.stderr)
        sys.exit(1)

    # Set up logging
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    try:
        # Load configuration from JSON
        print(f"Loading configuration from: {args.config_file}")
        config = IngestConfigJson.from_json(args.config_file)

        # Run ingestion
        print(f"Starting ingestion from: {config.base_url}{config.endpoint}")
        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        # Report results
        print(f"\n✓ Success!")
        print(f"  - Fetched {len(data)} records")
        print(f"  - Saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

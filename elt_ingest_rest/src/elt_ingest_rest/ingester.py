"""Main REST API ingester orchestrator.

This module contains the RestApiIngester class which:
1. Initializes HTTP session with retry logic
2. Selects appropriate pagination strategy
3. Delegates fetching to the strategy
4. Saves results to disk
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import IngestConfig, PaginationType
from .strategies import (
    NoPaginationStrategy,
    OffsetLimitStrategy,
    PageNumberStrategy,
    CursorStrategy,
    NextUrlStrategy,
    LinkHeaderStrategy,
)

logger = logging.getLogger(__name__)


class RestApiIngester:
    """Main orchestrator for REST API data ingestion.

    Responsibilities:
    1. Setup HTTP session with authentication and retry logic
    2. Select pagination strategy based on configuration
    3. Coordinate data fetching via strategy.fetch()
    4. Save results to disk (single file or batches)

    Process Flow:
    ┌─────────────────────────────────────┐
    │ 1. Initialize session               │
    │    - Configure retries              │
    │    - Set authentication             │
    │    - Add headers                    │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │ 2. Select strategy                  │
    │    - Based on pagination.type       │
    │    - Create strategy instance       │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │ 3. Fetch data                       │
    │    - Delegate to strategy.fetch()   │
    │    - Strategy handles pagination    │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │ 4. Save results                     │
    │    - Single file or batch mode      │
    │    - Pretty-print JSON              │
    └─────────────────────────────────────┘
    """

    def __init__(self, config: IngestConfig):
        """Initialize ingester with configuration.

        Args:
            config: IngestConfig with all ingestion settings
        """
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic.

        Configures:
        - Exponential backoff retry strategy
        - Retry on specific status codes (429, 500, 502, 503, 504)
        - Authentication (if provided)
        - Custom headers
        - SSL verification

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=self.config.retry_status_codes,
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set authentication
        if self.config.auth:
            session.auth = self.config.auth

        # Set headers
        session.headers.update(self.config.headers)

        # SSL verification
        session.verify = self.config.verify_ssl

        return session

    def _select_strategy(self):
        """Select pagination strategy based on configuration.

        Returns:
            Instance of appropriate strategy class

        Raises:
            ValueError: If pagination type is not supported
        """
        strategy_map = {
            PaginationType.NONE: NoPaginationStrategy,
            PaginationType.OFFSET_LIMIT: OffsetLimitStrategy,
            PaginationType.PAGE_NUMBER: PageNumberStrategy,
            PaginationType.CURSOR: CursorStrategy,
            PaginationType.NEXT_URL: NextUrlStrategy,
            PaginationType.LINK_HEADER: LinkHeaderStrategy,
        }

        strategy_class = strategy_map.get(self.config.pagination.type)
        if not strategy_class:
            raise ValueError(
                f"Unsupported pagination type: {self.config.pagination.type}"
            )

        return strategy_class(self.config, self.session)

    def fetch(self) -> list[dict]:
        """Fetch all data from API using configured pagination strategy.

        Returns:
            List of all records fetched

        Raises:
            requests.HTTPError: If API requests fail
            ValueError: If pagination type is unsupported
        """
        logger.info(
            f"Starting ingestion from {self.config.base_url}{self.config.endpoint}"
        )
        logger.info(f"Pagination type: {self.config.pagination.type.value}")

        # Select and execute strategy
        strategy = self._select_strategy()
        data = strategy.fetch()

        logger.info(f"Fetched {len(data)} total records")
        return data

    def save(self, data: list[dict]) -> Path:
        """Save fetched data to disk.

        Args:
            data: List of records to save

        Returns:
            Path to saved file (or directory for batch mode)

        Raises:
            ValueError: If save_mode is invalid
        """
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        if self.config.save_mode == "single":
            return self._save_single(data)
        elif self.config.save_mode == "batch":
            return self._save_batch(data)
        else:
            raise ValueError(f"Unsupported save mode: {self.config.save_mode}")

    def _save_single(self, data: list[dict]) -> Path:
        """Save all data to a single JSON file.

        Args:
            data: Records to save

        Returns:
            Path to saved file
        """
        filename = self._get_output_filename()
        filepath = self.config.output_dir / filename

        logger.info(f"Saving {len(data)} records to {filepath}")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully saved data to {filepath}")
        return filepath

    def _save_batch(self, data: list[dict]) -> Path:
        """Save data across multiple batch files.

        Each batch file contains up to batch_size records.

        Args:
            data: Records to save

        Returns:
            Path to output directory
        """
        base_filename = self._get_output_filename().replace(".json", "")
        batch_size = self.config.batch_size

        num_batches = (len(data) + batch_size - 1) // batch_size

        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            batch_num = i // batch_size + 1
            filename = f"{base_filename}_batch_{batch_num:04d}.json"
            filepath = self.config.output_dir / filename

            logger.info(
                f"Saving batch {batch_num}/{num_batches} ({len(batch)} records) to {filepath}"
            )

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(batch, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Successfully saved {len(data)} records in {num_batches} batches to {self.config.output_dir}"
        )
        return self.config.output_dir

    def _get_output_filename(self) -> str:
        """Generate output filename.

        Uses config.output_filename if provided, otherwise generates
        from endpoint name and timestamp.

        Returns:
            Filename string
        """
        if self.config.output_filename:
            return self.config.output_filename

        # Generate filename from endpoint and timestamp
        endpoint_name = (
            self.config.endpoint.strip("/").replace("/", "_") or "api_data"
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{endpoint_name}_{timestamp}.json"

    def ingest(self) -> tuple[list[dict], Path]:
        """Fetch and save data from API (main entry point).

        This is the primary method users call to:
        1. Fetch all data from API (via configured pagination)
        2. Save to disk (single file or batches)

        Returns:
            Tuple of (fetched data, output path)

        Example:
            config = IngestConfig(base_url="https://api.example.com", ...)
            ingester = RestApiIngester(config)
            data, output_path = ingester.ingest()
            print(f"Saved {len(data)} records to {output_path}")
        """
        data = self.fetch()
        output_path = self.save(data)
        return data, output_path

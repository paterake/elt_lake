"""JSON configuration parser.

This module handles:
1. Reading JSON from file/string/dict
2. Parsing and validating JSON structure
3. Converting JSON to IngestConfig dataclass
4. Exporting IngestConfig back to JSON
"""

import json
import logging
from pathlib import Path
from typing import Optional

from ..models import IngestConfig, PaginationConfig, PaginationType

logger = logging.getLogger(__name__)


class JsonConfigParser:
    """Parser for JSON-based ingestion configuration.

    Responsible for:
    - Loading JSON from various sources (file, string, dict)
    - Type conversions (string → enum, string → Path, list → tuple)
    - Validation of required fields
    - Serialization back to JSON
    """

    @staticmethod
    def from_json(json_data: str | dict | Path) -> IngestConfig:
        """Create IngestConfig from JSON data.

        Args:
            json_data: JSON string, dict, or Path to JSON file

        Returns:
            IngestConfig instance

        Raises:
            TypeError: If json_data is not str, dict, or Path
            FileNotFoundError: If Path doesn't exist
            json.JSONDecodeError: If JSON is malformed
            ValueError: If pagination type is invalid

        Examples:
            # From JSON file
            config = JsonConfigParser.from_json(Path("config.json"))

            # From JSON string
            config = JsonConfigParser.from_json('{"base_url": "https://api.example.com"}')

            # From dict
            config = JsonConfigParser.from_json({"base_url": "https://api.example.com"})
        """
        # Step 1: Load JSON data
        data = JsonConfigParser._load_json(json_data)

        # Step 2: Parse pagination configuration
        pagination = JsonConfigParser._parse_pagination(data)

        # Step 3: Parse other type conversions
        JsonConfigParser._convert_types(data)

        # Step 4: Create and return IngestConfig
        return IngestConfig(pagination=pagination, **data)

    @staticmethod
    def to_json(
        config: IngestConfig, filepath: Optional[Path] = None, indent: int = 2
    ) -> str:
        """Export IngestConfig to JSON.

        Args:
            config: IngestConfig instance to export
            filepath: Optional path to save JSON file
            indent: JSON indentation (default: 2)

        Returns:
            JSON string

        Examples:
            config = IngestConfig(base_url="https://api.example.com")

            # Get JSON string
            json_str = JsonConfigParser.to_json(config)

            # Save to file
            JsonConfigParser.to_json(config, Path("config.json"))
        """
        data = {
            "base_url": config.base_url,
            "endpoint": config.endpoint,
            "method": config.method,
            "headers": config.headers,
            "params": config.params,
            "body": config.body,
            "auth": list(config.auth) if config.auth else None,
            "timeout": config.timeout,
            "verify_ssl": config.verify_ssl,
            "pagination": {
                "type": config.pagination.type.value,
                "page_size": config.pagination.page_size,
                "offset_param": config.pagination.offset_param,
                "limit_param": config.pagination.limit_param,
                "page_param": config.pagination.page_param,
                "page_size_param": config.pagination.page_size_param,
                "cursor_param": config.pagination.cursor_param,
                "cursor_path": config.pagination.cursor_path,
                "next_url_path": config.pagination.next_url_path,
                "link_header_name": config.pagination.link_header_name,
                "data_path": config.pagination.data_path,
                "max_pages": config.pagination.max_pages,
                "max_records": config.pagination.max_records,
            },
            "output_dir": str(config.output_dir),
            "output_filename": config.output_filename,
            "save_mode": config.save_mode,
            "batch_size": config.batch_size,
            "max_retries": config.max_retries,
            "backoff_factor": config.backoff_factor,
            "retry_status_codes": config.retry_status_codes,
        }

        json_str = json.dumps(data, indent=indent, ensure_ascii=False)

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info(f"Configuration saved to {filepath}")

        return json_str

    # --- Private Helper Methods ---

    @staticmethod
    def _load_json(json_data: str | dict | Path) -> dict:
        """Load JSON from file, string, or dict.

        Args:
            json_data: JSON source

        Returns:
            Dictionary of JSON data

        Raises:
            TypeError: If json_data is invalid type
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        if isinstance(json_data, Path):
            with open(json_data, "r", encoding="utf-8") as f:
                return json.load(f)
        elif isinstance(json_data, str):
            return json.loads(json_data)
        elif isinstance(json_data, dict):
            return json_data.copy()  # Copy to avoid mutating input
        else:
            raise TypeError(
                f"json_data must be str, dict, or Path, got {type(json_data)}"
            )

    @staticmethod
    def _parse_pagination(data: dict) -> PaginationConfig:
        """Parse pagination configuration from JSON data.

        Args:
            data: JSON data dict (will be mutated - pagination removed)

        Returns:
            PaginationConfig instance

        Raises:
            ValueError: If pagination type is invalid
        """
        pagination_data = data.pop("pagination", {})

        if not pagination_data:
            return PaginationConfig()

        # Convert pagination type string to enum
        if "type" in pagination_data:
            pagination_data["type"] = PaginationType(pagination_data["type"])

        return PaginationConfig(**pagination_data)

    @staticmethod
    def _convert_types(data: dict) -> None:
        """Convert JSON types to Python types in-place.

        Converts:
        - output_dir: str → Path
        - auth: list → tuple

        Args:
            data: JSON data dict (will be mutated)
        """
        # Convert output_dir to Path
        if "output_dir" in data:
            data["output_dir"] = Path(data["output_dir"])

        # Convert auth list to tuple
        if "auth" in data and isinstance(data["auth"], list):
            data["auth"] = tuple(data["auth"])

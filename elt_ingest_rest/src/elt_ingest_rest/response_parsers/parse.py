from typing import Any

import requests

from ..models import IngestConfig
from .csv_response import parse_csv
from .json_response import parse_json
from .xml_response import parse_xml


def parse_response(response: requests.Response, config: IngestConfig) -> Any:
    response_format = config.response_format.lower().strip()

    if response_format == "json":
        return parse_json(response)

    if response_format == "csv":
        return parse_csv(response, config)

    if response_format == "xml":
        return parse_xml(response.text, config)

    raise ValueError(f"Unsupported response_format: {config.response_format}")

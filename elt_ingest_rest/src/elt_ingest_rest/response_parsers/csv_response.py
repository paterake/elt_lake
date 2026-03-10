import csv
from io import StringIO

import requests

from ..models import IngestConfig


def parse_csv(response: requests.Response, config: IngestConfig) -> list[dict]:
    lines = response.text.splitlines()
    if config.csv_skip_rows:
        lines = lines[config.csv_skip_rows :]

    lines = [line for line in lines if line.strip()]
    if not lines:
        return []

    reader = csv.DictReader(StringIO("\n".join(lines)), delimiter=config.csv_delimiter)
    return [dict(row) for row in reader]

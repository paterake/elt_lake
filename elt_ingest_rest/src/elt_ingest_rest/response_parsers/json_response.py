from typing import Any

import requests


def parse_json(response: requests.Response) -> Any:
    return response.json()

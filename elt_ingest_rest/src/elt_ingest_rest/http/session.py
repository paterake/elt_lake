import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..models import IngestConfig


def create_session(config: IngestConfig) -> requests.Session:
    session = requests.Session()

    retry_strategy = Retry(
        total=config.max_retries,
        backoff_factor=config.backoff_factor,
        status_forcelist=config.retry_status_codes,
        allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    if config.auth:
        session.auth = config.auth

    session.headers.update(config.headers)
    session.verify = config.verify_ssl

    return session

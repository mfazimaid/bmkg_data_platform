"""
HTTP Client for BMKG JSON API.
Uses requests with retry for rate limit resilience.
"""

from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import config


class BMKGClient:
    """
    BMKG API Client (JSON Format).

    rate limit: 60 requests/minute per IP.
    we add delay between requests to respect this.
    """

    DEFAULT_HEADERS = {
        "user-agent": config.bmkg.user_agent,
        "Accept": "application/json"
    }

    def __init__(self) -> None:
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        """ Lazy-init session with retry adapter. """
        if self._session is None:
            self._session = requests.Session()
            retry_strategy = Retry(
                total=3, 
                backoff_factor=2.0, # Longer backoff for rate limit
                allowed_methods=["GET"],
                status_forcelist=[500, 502, 504, 429], # 429 rate limited 
                raise_on_status=False
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=1, 
                pool_maxsize=5
            )
            self._session.mount("https://", adapter)
        return self._session

    def fetch(
        self,
        url: str,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """ Fetch JSON from BMKG API. """
        if timeout is None:
            timeout = config.bmkg.timeout_sec

        response = self.session.get(
            url,
            headers=self.DEFAULT_HEADERS,
            timeout=timeout
        )
        response.raise_for_status()
        return response

    def fetch_json(self, url: str) -> dict:
        """ Fetch and parse JSON response. """
        response = self.fetch(url)
        return response.json()

    def close(self) -> None:
        """ Close session and release connections. """
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self) -> "BMKGClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
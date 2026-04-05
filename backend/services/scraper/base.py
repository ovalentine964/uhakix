"""
UHAKIX Scraper Base — Base class for all data source scrapers
Handles HTTP sessions, retries, rate limiting, and data validation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import asyncio
import time
import httpx
from urllib.parse import urljoin
import structlog

logger = structlog.get_logger()


class ScraperError(Exception):
    """Custom scraper exception."""
    pass


class BaseScraper(ABC):
    """Base class for all UHAKIX data source scrapers."""

    base_url: str = ""
    source_name: str = "base"
    default_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url or self.base_url
        self.timeout = timeout or self.default_timeout
        self.headers = headers or self._default_headers()
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time = 0.0
        self._min_request_interval = 1.0  # Rate limit: 1 req/sec default

    def _default_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "UHAKIX/1.0 (Government Transparency Platform; +https://uhakix.ke)",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9,sw;q=0.8",
        }

    def _set_rate_limit(self, requests_per_second: float = 1.0):
        """Configure rate limiting."""
        self._min_request_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
                http2=True,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _respect_rate_limit(self):
        """Ensure minimum interval between requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - elapsed)

    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
    ) -> httpx.Response:
        """Make an HTTP request with retries and rate limiting."""
        await self._respect_rate_limit()
        client = await self._get_client()

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                )
                self._last_request_time = time.monotonic()

                # Handle rate limiting from the server
                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", self.retry_delay * (attempt + 1)))
                    logger.warning(
                        "scraper_rate_limited",
                        source=self.source_name,
                        url=url,
                        retry_after=retry_after,
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        "scraper_http_error",
                        source=self.source_name,
                        url=url,
                        status=e.response.status_code,
                        attempt=attempt + 1,
                        retry_wait=wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    raise ScraperError(f"HTTP {e.response.status_code} for {url}: {e}") from e

            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        "scraper_timeout",
                        source=self.source_name,
                        url=url,
                        attempt=attempt + 1,
                        retry_wait=wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    raise ScraperError(f"Timeout fetching {url}") from e

            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait)
                else:
                    raise ScraperError(f"Request error fetching {url}: {e}") from e

        raise ScraperError(f"Failed after {self.max_retries} retries: {url}")

    async def fetch_json(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Fetch JSON data from a URL."""
        response = await self._request("GET", url, params=params)
        return response.json()

    async def fetch_html(self, url: str, params: Optional[Dict] = None) -> str:
        """Fetch HTML data from a URL."""
        response = await self._request("GET", url, params=params)
        return response.text

    @abstractmethod
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """Main fetch method — must be implemented by subclasses."""

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a single record. Override in subclass."""
        return True

    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw data into structured records. Override in subclass."""

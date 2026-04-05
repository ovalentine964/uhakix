"""
IEBC Scraper — Independent Electoral and Boundaries Commission
Source: iebc.or.ke
Scrapes election results, registered voters, and polling station data.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class IEBChScraper(BaseScraper):
    """Scrape IEBC election results and public data."""

    base_url = "https://www.iebc.or.ke"
    source_name = "iebc"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(0.5)

    async def fetch(
        self,
        election_type: str = "presidential",
        county: Optional[str] = None,
        constituency: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch election results.

        Args:
            election_type: presidential, parliamentary, gubernatorial, senatorial, mca
            county: County name filter
            constituency: Constituency name filter

        Returns:
            List of result records
        """
        try:
            # Try API
            params: Dict[str, Any] = {"type": election_type}
            if county:
                params["county"] = county
            if constituency:
                params["constituency"] = constituency

            try:
                raw = await self.fetch_json(f"{self.base_url}/api/results", params=params)
                records = self.parse(raw)
                logger.info("iebc_fetch_success", count=len(records), source="api")
                return records
            except (ScraperError, Exception):
                pass

            # HTML scrape
            html = await self.fetch_html(f"{self.base_url}/results", params=params)
            records = self.parse({"html": html, "type": election_type})
            logger.info("iebc_fetch_success", count=len(records), source="html")
            return records

        except (ScraperError, Exception) as e:
            logger.error("iebc_fetch_failed", error=str(e))
            return []

    async def fetch_polling_stations(self, county: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch polling station registry."""
        try:
            params = {"county": county} if county else {}
            html = await self.fetch_html(f"{self.base_url}/polling-stations", params=params)
            soup = BeautifulSoup(html, "lxml")
            stations = []
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True).lower() for th in table.find_all(["th"])]
                for row in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if cells:
                        record = dict(zip(headers, cells))
                        stations.append(record)
            return stations
        except Exception as e:
            logger.error("iebc_stations_failed", error=str(e))
            return []

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse IEBC election results."""
        records: List[Dict[str, Any]] = []

        if isinstance(raw_data, dict) and "data" in raw_data:
            items = raw_data["data"] if isinstance(raw_data["data"], list) else [raw_data["data"]]
            for item in items:
                record = self._normalize_result(item)
                if record and self.validate_record(record):
                    records.append(record)

        if isinstance(raw_data, dict) and "html" in raw_data:
            soup = BeautifulSoup(raw_data["html"], "lxml")
            election_type = raw_data.get("type", "")

            # Parse results tables
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True).lower() for th in table.find_all(["th"])]
                for row in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cells) < 3:
                        continue
                    record = dict(zip(headers, cells))
                    record["election_type"] = election_type
                    normalized = self._normalize_result(record)
                    if normalized and self.validate_record(normalized):
                        records.append(normalized)

        logger.info("iebc_parse_complete", count=len(records))
        return records

    def _normalize_result(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize IEBC result record."""
        if not raw or not isinstance(raw, dict):
            return None

        def parse_int(val: str) -> int:
            try:
                return int(str(val).replace(",", "").strip())
            except (ValueError, TypeError):
                return 0

        return {
            "station_code": raw.get("station_code", raw.get("polling_station_code", raw.get("code", ""))),
            "station_name": raw.get("station_name", raw.get("polling_station", "")),
            "constituency": raw.get("constituency", raw.get("ward", "")),
            "county": raw.get("county", raw.get("region", "")),
            "election_type": raw.get("election_type", "general"),
            "registered_voters": parse_int(raw.get("registered_voters", raw.get("voters", "0"))),
            "votes_cast": parse_int(raw.get("votes_cast", raw.get("total_votes", "0"))),
            "rejected_votes": parse_int(raw.get("rejected_votes", raw.get("spoilt", "0"))),
            "results": {k: parse_int(v) for k, v in raw.items()
                        if k not in ("station_code", "station_name", "constituency", "county",
                                     "registered_voters", "votes_cast", "rejected_votes",
                                     "election_type") and v},
            "source": "iebc.or.ke",
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate an election result record."""
        return bool(record.get("station_code") or record.get("station_name"))


iebc_scraper = IEBChScraper()

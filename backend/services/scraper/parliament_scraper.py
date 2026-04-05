"""
Parliament Hansard Scraper — Kenya's National Assembly
Source: parliament.go.ke
Scrapes parliamentary proceedings, questions, and committee reports.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class ParliamentHansardScraper(BaseScraper):
    """Scrape parliamentary Hansard records."""

    base_url = "https://www.parliament.go.ke"
    source_name = "parliament_hansard"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(0.5)

    async def fetch(
        self,
        document_type: str = "hansard",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Fetch parliamentary records.

        Args:
            document_type: hansard, order_paper, vote_of_account, committee_report
            date_from: YYYY-MM-DD start date
            date_to: YYYY-MM-DD end date
            page: Page number

        Returns:
            List of parliamentary records
        """
        try:
            params = {"type": document_type, "page": page}
            if date_from:
                params["from"] = date_from
            if date_to:
                params["to"] = date_to

            # Try API
            try:
                raw = await self.fetch_json(f"{self.base_url}/api/hansard", params=params)
                records = self.parse(raw)
                logger.info("hansard_fetch_success", count=len(records), source="api")
                return records
            except (ScraperError, Exception):
                pass

            # HTML scrape
            html = await self.fetch_html(f"{self.base_url}/the-house/hansard", params=params)
            records = self.parse({"html": html, "type": document_type})
            return records

        except (ScraperError, Exception) as e:
            logger.error("hansard_fetch_failed", error=str(e))
            return []

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse Hansard data."""
        records: List[Dict[str, Any]] = []

        if isinstance(raw_data, dict) and "data" in raw_data:
            items = raw_data["data"] if isinstance(raw_data["data"], list) else [raw_data["data"]]
            for item in items:
                record = self._normalize_hansard(item)
                if record and self.validate_record(record):
                    records.append(record)

        if isinstance(raw_data, dict) and "html" in raw_data:
            soup = BeautifulSoup(raw_data["html"], "lxml")

            for link in soup.find_all("a", href=re.compile(r"hansard|document|download", re.I)):
                title = link.get_text(strip=True)
                href = link.get("href", "")
                parent = link.find_parent("div") or link.find_parent("li")
                date_el = parent.find("time") if parent else None

                record = {
                    "title": title,
                    "url": href if href.startswith("http") else f"{self.base_url}{href}",
                    "date": date_el.get_text(strip=True) if date_el else "",
                    "type": raw_data.get("type", "hansard"),
                }
                normalized = self._normalize_hansard(record)
                if normalized and self.validate_record(normalized):
                    records.append(normalized)

            # Also extract content from hansard detail pages
            for div in soup.find_all(class_=re.compile(r"hansard-content|proceedings", re.I)):
                record = {
                    "title": div.find("h1", "h2").get_text(strip=True) if div.find(["h1", "h2"]) else "Hansard Record",
                    "content": div.get_text(strip=True)[:5000],
                    "date": raw_data.get("date", ""),
                    "type": "hansard_content",
                }
                normalized = self._normalize_hansard(record)
                if normalized and self.validate_record(normalized):
                    records.append(normalized)

        logger.info("hansard_parse_complete", count=len(records))
        return records

    def _normalize_hansard(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize Hansard record."""
        if not raw or not isinstance(raw, dict):
            return None

        # Extract date from various formats
        date_str = raw.get("date", "")
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%d/%m/%Y"):
            try:
                datetime.strptime(date_str, fmt)
                date_str = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

        return {
            "title": raw.get("title", raw.get("heading", raw.get("subject", ""))).strip()[:200],
            "url": raw.get("url", raw.get("link", "")),
            "date": date_str,
            "document_type": raw.get("type", raw.get("document_type", raw.get("category", "hansard"))),
            "content_preview": raw.get("content", raw.get("summary", ""))[:500],
            "source": "parliament.go.ke",
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a Hansard record."""
        return bool(record.get("title"))


hansard_scraper = ParliamentHansardScraper()

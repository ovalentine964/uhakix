"""
National Treasury Scraper — Kenya's National Treasury & Economic Planning
Source: treasury.go.ke
Scrapes budget estimates, economic reviews, public debt, and revenue data.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class TreasuryScraper(BaseScraper):
    """Scrape National Treasury publications and budget documents."""

    base_url = "https://www.treasury.go.ke"
    source_name = "national_treasury"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(0.5)

    async def fetch(
        self,
        document_type: str = "budget_estimates",
        fiscal_year: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch Treasury documents and extract financial data.

        Args:
            document_type: budget_estimates, economic_review, public_debt, revenue
            fiscal_year: Fiscal year filter

        Returns:
            List of financial records
        """
        try:
            # Try API
            try:
                params = {"type": document_type}
                if fiscal_year:
                    params["year"] = fiscal_year
                raw = await self.fetch_json(f"{self.base_url}/api/publications", params=params)
                records = self.parse(raw)
                logger.info("treasury_fetch_success", count=len(records), doc_type=document_type)
                return records
            except (ScraperError, Exception):
                pass

            # HTML scrape: publications index
            html = await self.fetch_html(f"{self.base_url}/publications")
            records = self.parse({"html": html, "doc_type": document_type, "year": fiscal_year})
            logger.info("treasury_fetch_success", count=len(records))
            return records

        except (ScraperError, Exception) as e:
            logger.error("treasury_fetch_failed", error=str(e))
            return []

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse Treasury data into structured records."""
        records: List[Dict[str, Any]] = []

        if isinstance(raw_data, dict) and "data" in raw_data:
            items = raw_data["data"] if isinstance(raw_data["data"], list) else [raw_data["data"]]
            for item in items:
                record = self._normalize_publication(item)
                if record and self.validate_record(record):
                    records.append(record)

        if isinstance(raw_data, dict) and "html" in raw_data:
            soup = BeautifulSoup(raw_data["html"], "lxml")

            # Extract publication links
            for link in soup.find_all("a", href=re.compile(r"publication|document|budget|report", re.I)):
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if href.startswith("/"):
                    href = f"{self.base_url}{href}"

                # Try to extract metadata from surrounding elements
                parent = link.find_parent("div") or link.find_parent("li")
                date_el = parent.find("time") if parent else None
                desc_el = parent.find(["p", "div"], class_=re.compile(r"desc|summary", re.I)) if parent else None

                record = {
                    "title": title,
                    "url": href,
                    "date": date_el.get_text(strip=True) if date_el else "",
                    "description": desc_el.get_text(strip=True) if desc_el else "",
                    "doc_type": raw_data.get("doc_type", "unknown"),
                }
                normalized = self._normalize_publication(record)
                if normalized and self.validate_record(normalized):
                    records.append(normalized)

            # Also extract any embedded financial tables
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True).lower() for th in table.find_all(["th"])]
                for row in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cells) < 2:
                        continue
                    record = dict(zip(headers, cells))
                    record["doc_type"] = raw_data.get("doc_type", "unknown")
                    normalized = self._normalize_publication(record)
                    if normalized and self.validate_record(normalized):
                        records.append(normalized)

        logger.info("treasury_parse_complete", count=len(records))
        return records

    def _normalize_publication(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize Treasury publication/financial data."""
        if not raw or not isinstance(raw, dict):
            return None

        return {
            "title": raw.get("title", raw.get("document_title", raw.get("name", ""))).strip(),
            "url": raw.get("url", raw.get("link", raw.get("file_url", ""))),
            "document_type": raw.get("doc_type", raw.get("type", raw.get("category", "other"))),
            "fiscal_year": raw.get("fiscal_year", raw.get("year", "")),
            "description": raw.get("description", raw.get("summary", "")),
            "date_published": raw.get("date", raw.get("published_date", "")),
            "source": "national_treasury",
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a Treasury record."""
        return bool(record.get("title"))


treasury_scraper = TreasuryScraper()

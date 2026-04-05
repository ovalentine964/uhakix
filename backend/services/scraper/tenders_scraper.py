"""
Tenders Scraper — Kenya Government Tenders Portal
Source: tenders.go.ke
Scrapes tender notices, bid awards, and procurement data.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class TendersScraper(BaseScraper):
    """Scrape tender data from tenders.go.ke."""

    base_url = "https://tenders.go.ke"
    source_name = "tenders"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(1.0)

    async def fetch(
        self,
        status: Optional[str] = None,
        ministry: Optional[str] = None,
        county: Optional[str] = None,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Fetch tender records.

        Args:
            status: Filter by status (open, closed, awarded, cancelled)
            ministry: Filter by procuring entity/ministry
            county: Filter by county
            page: Page number

        Returns:
            List of tender records
        """
        params: Dict[str, Any] = {"page": page}
        if status:
            params["status"] = status.lower()
        if ministry:
            params["ministry"] = ministry
        if county:
            params["county"] = county

        try:
            # Try API first
            try:
                raw = await self.fetch_json(f"{self.base_url}/api/tenders", params=params)
                records = self.parse(raw)
                logger.info("tenders_fetch_success", count=len(records), source="api")
                return records
            except (ScraperError, Exception):
                logger.debug("tenders_api_unavailable", attempting="html_scrape")

            # HTML scrape
            query_parts = []
            for k, v in params.items():
                if k != "page":
                    query_parts.append(f"{k}={v}")
            query_str = "&".join(query_parts)
            url = f"{self.base_url}/tenders" + (f"?{query_str}" if query_str else "") + f"&page={page}"

            html = await self.fetch_html(url)
            records = self.parse({"html": html, "params": params})

            logger.info("tenders_fetch_success", count=len(records), source="html")
            return records

        except (ScraperError, Exception) as e:
            logger.error("tenders_fetch_failed", error=str(e))
            return []

    async def fetch_tender_details(self, tender_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full details for a specific tender."""
        try:
            html = await self.fetch_html(f"{self.base_url}/tenders/{tender_id}")
            soup = BeautifulSoup(html, "lxml")
            return self._parse_tender_detail(soup, tender_id)
        except (ScraperError, Exception) as e:
            logger.error("tenders_detail_failed", tender_id=tender_id, error=str(e))
            return None

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse tender data into structured records."""
        records: List[Dict[str, Any]] = []

        if isinstance(raw_data, dict) and "data" in raw_data:
            items = raw_data["data"] if isinstance(raw_data["data"], list) else [raw_data["data"]]
            for item in items:
                record = self._normalize_tender(item)
                if record and self.validate_record(record):
                    records.append(record)

        if isinstance(raw_data, dict) and "html" in raw_data:
            soup = BeautifulSoup(raw_data["html"], "lxml")

            # Parse tender listing — look for link blocks or table rows
            for link in soup.find_all("a", href=re.compile(r"/tenders/\d+")):
                card = link.find_parent("div") or link.find_parent("li") or link
                title = card.get_text(strip=True) if card else link.get_text(strip=True)
                href = link.get("href", "")
                tender_id_match = re.search(r"/tenders/(\d+)", href)
                tender_id = tender_id_match.group(1) if tender_id_match else href

                # Try to extract date and entity from adjacent elements
                date_el = card.find("time") or card.find(class_=re.compile(r"date")) if card else None
                entity_el = card.find(class_=re.compile(r"entity|ministry|agency")) if card else None

                record = {
                    "id": tender_id,
                    "title": title,
                    "url": href if href.startswith("http") else f"{self.base_url}{href}",
                    "date": date_el.get_text(strip=True) if date_el else "",
                    "entity": entity_el.get_text(strip=True) if entity_el else "",
                    "status": "unknown",
                }
                normalized = self._normalize_tender(record)
                if normalized and self.validate_record(normalized):
                    records.append(normalized)

            # Also try table-based layouts
            for table in soup.find_all("table"):
                rows = table.find_all("tr")
                if len(rows) < 2:
                    continue
                headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
                for row in rows[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cells) < 2:
                        continue
                    record = dict(zip(headers, cells))
                    normalized = self._normalize_tender(record)
                    if normalized and self.validate_record(normalized):
                        records.append(normalized)

        logger.info("tenders_parse_complete", count=len(records))
        return records

    def _normalize_tender(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize tender record to schema."""
        if not raw or not isinstance(raw, dict):
            return None

        amount_raw = str(raw.get("estimated_cost", raw.get("budget", raw.get("amount", "0"))))
        amount_clean = re.sub(r"[^\d.]", "", amount_raw.replace(",", ""))
        try:
            estimated_cost = float(amount_clean) if amount_clean else 0.0
        except ValueError:
            estimated_cost = 0.0

        awarded_raw = str(raw.get("awarded_amount", raw.get("winning_bid", "0")))
        awarded_clean = re.sub(r"[^\d.]", "", awarded_raw.replace(",", ""))
        try:
            awarded_amount = float(awarded_clean) if awarded_clean else None
        except ValueError:
            awarded_amount = None

        status = str(raw.get("status", raw.get("stage", ""))).lower()
        if not status or status == "unknown":
            status = "open"

        return {
            "id": str(raw.get("id", raw.get("reference_number", raw.get("tender_no", "")))),
            "title": raw.get("title", raw.get("description", raw.get("subject_matter", ""))).strip(),
            "entity": raw.get("entity", raw.get("ministry", raw.get("procuring_entity", ""))).strip(),
            "county": raw.get("county", raw.get("region", "")).strip(),
            "status": status,
            "estimated_cost_kes": estimated_cost,
            "awarded_amount_kes": awarded_amount,
            "contractor": raw.get("contractor", raw.get("successful_bidder", raw.get("awarded_to", ""))).strip(),
            "closing_date": raw.get("closing_date", raw.get("deadline", "")),
            "published_date": raw.get("published_date", raw.get("date", raw.get("advertised_date", ""))),
            "source": "tenders.go.ke",
            "url": raw.get("url", ""),
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def _parse_tender_detail(self, soup: BeautifulSoup, tender_id: str) -> Optional[Dict[str, Any]]:
        """Parse a single tender detail page."""
        data = {"id": tender_id}

        # Extract all text content into key-value pairs
        for label in soup.find_all(["dt", "strong", "label"]):
            key = label.get_text(strip=True).lower().rstrip(":")
            dd = label.find_next_sibling(["dd", "span", "p", "td"])
            if dd:
                data[key] = dd.get_text(strip=True)

        return self._normalize_tender(data)

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a tender record."""
        if not record.get("id"):
            return False
        if not record.get("title"):
            return False
        return True


TendersScraper_instance = TendersScraper()

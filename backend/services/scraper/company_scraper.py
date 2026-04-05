"""
Company Registry Scraper — Kenya's eCitizen / Business Registration Service
Source: brs.go.ke (Business Registration Service)
Scrapes company registration, directors, and shareholder data.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class CompanyRegistryScraper(BaseScraper):
    """Scrape company registration data from Business Registration Service."""

    base_url = "https://www.brs.go.ke"
    source_name = "company_registry"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(0.3)  # Very conservative: ~2-3 sec between requests

    async def fetch(
        self,
        query: str = "",
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Search company registry.

        Args:
            query: Company name or registration number
            page: Page number

        Returns:
            List of company records
        """
        try:
            # Try API first
            if query:
                try:
                    params = {"q": query, "page": page}
                    raw = await self.fetch_json(f"{self.base_url}/api/search", params=params)
                    records = self.parse(raw)
                    logger.info("company_fetch_success", count=len(records), query=query, source="api")
                    return records
                except (ScraperError, Exception):
                    pass

            # HTML scrape
            html = await self.fetch_html(f"{self.base_url}/search", params={"q": query, "page": page})
            records = self.parse({"html": html, "query": query})
            logger.info("company_fetch_success", count=len(records))
            return records

        except (ScraperError, Exception) as e:
            logger.error("company_fetch_failed", error=str(e), query=query)
            return []

    async def fetch_company_details(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed company info including directors and shareholders."""
        try:
            html = await self.fetch_html(f"{self.base_url}/company/{company_id}")
            soup = BeautifulSoup(html, "lxml")
            return self._parse_company_detail(soup, company_id)
        except Exception as e:
            logger.error("company_detail_failed", company_id=company_id, error=str(e))
            return None

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse company registry data."""
        records: List[Dict[str, Any]] = []

        if isinstance(raw_data, dict) and "data" in raw_data:
            items = raw_data["data"] if isinstance(raw_data["data"], list) else [raw_data["data"]]
            for item in items:
                record = self._normalize_company(item)
                if record and self.validate_record(record):
                    records.append(record)

        if isinstance(raw_data, dict) and "html" in raw_data:
            soup = BeautifulSoup(raw_data["html"], "lxml")

            # Parse search results table
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True).lower() for th in table.find_all(["th"])]
                for row in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cells) < 2:
                        continue
                    record = dict(zip(headers, cells))
                    # Extract link
                    link_el = row.find("a")
                    if link_el:
                        record["detail_url"] = link_el.get("href", "")
                    normalized = self._normalize_company(record)
                    if normalized and self.validate_record(normalized):
                        records.append(normalized)

            # Card-based layouts
            for card in soup.find_all(class_=re.compile(r"result|card|item", re.I)):
                title_el = card.find(["h2", "h3", "a", "strong"])
                company_name = title_el.get_text(strip=True) if title_el else ""
                reg_el = card.find(text=re.compile(r"P\d+/\d+", re.I))
                status_el = card.find(class_=re.compile(r"status|badge", re.I))
                record = {
                    "name": company_name,
                    "reg_number": reg_el.strip() if reg_el else "",
                    "status": status_el.get_text(strip=True) if status_el else "",
                }
                normalized = self._normalize_company(record)
                if normalized and self.validate_record(normalized):
                    records.append(normalized)

        logger.info("company_parse_complete", count=len(records))
        return records

    def _normalize_company(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize company registry data."""
        if not raw or not isinstance(raw, dict):
            return None

        return {
            "id": raw.get("id", raw.get("reg_no", raw.get("company_id", raw.get("reg_number", "")))),
            "name": raw.get("name", raw.get("company_name", raw.get("entity_name", ""))).strip(),
            "registration_number": raw.get("registration_number", raw.get("reg_number", raw.get("reg_no", ""))),
            "registration_date": raw.get("registration_date", raw.get("incorporated", raw.get("date_registered", ""))),
            "status": self._normalize_status(raw.get("status", raw.get("company_status", raw.get("state", "unknown")))),
            "business_type": raw.get("business_type", raw.get("entity_type", raw.get("type", ""))),
            "address": raw.get("address", raw.get("registered_address", "")),
            "county": raw.get("county", raw.get("location", "")),
            "directors": raw.get("directors", []),
            "shareholders": raw.get("shareholders", []),
            "source": "company_registry",
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def _normalize_status(self, status: str) -> str:
        """Normalize company status."""
        status = str(status).lower().strip()
        if status in ("active", "registered", "in good standing"):
            return "active"
        elif status in ("dissolved", "wound up", "struck off", "removed"):
            return "dissolved"
        elif status in ("in receivership", "under administration"):
            return "under_receivership"
        else:
            return status or "unknown"

    def _parse_company_detail(self, soup: BeautifulSoup, company_id: str) -> Optional[Dict[str, Any]]:
        """Parse a company detail page for directors and shareholders."""
        data: Dict[str, Any] = {"id": company_id, "directors": [], "shareholders": []}

        # Extract all label-value pairs
        for label in soup.find_all(["dt", "strong", "label"]):
            key = label.get_text(strip=True).lower().rstrip(":")
            dd = label.find_next_sibling(["dd", "span", "p"])
            if dd:
                data[key] = dd.get_text(strip=True)

        # Parse directors table
        for header in soup.find_all(text=re.compile(r"director|officer", re.I)):
            table = header.find_next("table")
            if table:
                for row in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if cells:
                        data["directors"].append({
                            "name": cells[0] if len(cells) > 0 else "",
                            "id_number": cells[1] if len(cells) > 1 else "",
                            "address": cells[2] if len(cells) > 2 else "",
                            "appointment_date": cells[3] if len(cells) > 3 else "",
                        })

        # Parse shareholders table
        for header in soup.find_all(text=re.compile(r"shareholder", re.I)):
            table = header.find_next("table")
            if table:
                for row in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if cells:
                        data["shareholders"].append({
                            "name": cells[0] if len(cells) > 0 else "",
                            "shares": cells[1] if len(cells) > 1 else "",
                            "percentage": cells[2] if len(cells) > 2 else "",
                        })

        return self._normalize_company(data)

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a company record."""
        return bool(record.get("name")) or bool(record.get("registration_number"))


company_scraper = CompanyRegistryScraper()

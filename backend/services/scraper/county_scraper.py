"""
County Portals Scraper — Kenya's 47 County Government Portals
Sources: Each county's public portal (nairobi.go.ke, mombasa.go.ke, etc.)
Scrapes county budget, procurement, and development project data.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()

# Known county portal URLs
COUNTY_PORTALS = {
    "nairobi": "https://www.nairobi.go.ke",
    "mombasa": "https://mombasa.go.ke",
    "kisumu": "https://www.kisumu.go.ke",
    "nakuru": "https://www.nakurucounty.go.ke",
    "uasingishu": "https://uasingishucounty.go.ke",
    "kiambu": "https://www.kiambu.go.ke",
    "machakos": "https://www.machakos.go.ke",
    "kakamega": "https://www.kakamega.go.ke",
    "transnzoia": "https://www.transnzoia.go.ke",
    "uasin gishu": "https://uasingishucounty.go.ke",
}


class CountyPortalsScraper(BaseScraper):
    """Scrape county government portal data."""

    base_url = ""
    source_name = "county_portals"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(0.2)  # Very conservative: 5 sec per county

    async def fetch(
        self,
        county: str = "",
        data_type: str = "budget",
    ) -> List[Dict[str, Any]]:
        """
        Fetch county government data.

        Args:
            county: County name (empty = all available)
            data_type: budget, procurement, projects, reports

        Returns:
            List of county data records
        """
        all_records: List[Dict[str, Any]] = []
        counties_to_scan = [county] if county else list(COUNTY_PORTALS.keys())

        for county_name in counties_to_scan:
            base = COUNTY_PORTALS.get(county_name.lower().replace(" ", "").replace("-", ""))
            if not base:
                logger.debug("county_portal_not_found", county=county_name)
                continue

            self.base_url = base
            self.source_name = f"county_{county_name.lower()}"

            try:
                if data_type == "budget":
                    records = await self._fetch_county_budget(county_name)
                elif data_type == "procurement":
                    records = await self._fetch_county_procurement(county_name)
                elif data_type == "projects":
                    records = await self._fetch_county_projects(county_name)
                else:
                    records = await self._fetch_county_reports(county_name)

                all_records.extend(records)
                logger.info("county_portal_success", county=county_name, count=len(records))

            except Exception as e:
                logger.warning("county_portal_error", county=county_name, error=str(e))

        return all_records

    async def _fetch_county_budget(self, county_name: str) -> List[Dict[str, Any]]:
        """Fetch county budget documents and data."""
        try:
            html = await self.fetch_html(f"{self.base_url}/budget")
            return self._parse_budget_html(html, county_name)
        except (ScraperError, Exception):
            try:
                html = await self.fetch_html(f"{self.base_url}/finance")
                return self._parse_budget_html(html, county_name)
            except Exception:
                return []

    async def _fetch_county_procurement(self, county_name: str) -> List[Dict[str, Any]]:
        """Fetch county procurement data."""
        try:
            html = await self.fetch_html(f"{self.base_url}/procurement")
            return self._parse_procurement_html(html, county_name)
        except (ScraperError, Exception):
            return []

    async def _fetch_county_projects(self, county_name: str) -> List[Dict[str, Any]]:
        """Fetch county development projects."""
        try:
            html = await self.fetch_html(f"{self.base_url}/projects")
            return self._parse_projects_html(html, county_name)
        except (ScraperError, Exception):
            try:
                html = await self.fetch_html(f"{self.base_url}/development")
                return self._parse_projects_html(html, county_name)
            except Exception:
                return []

    async def _fetch_county_reports(self, county_name: str) -> List[Dict[str, Any]]:
        """Fetch county reports."""
        try:
            html = await self.fetch_html(f"{self.base_url}/reports")
            return self._parse_reports_html(html, county_name)
        except Exception:
            return []

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Placeholder — parsing is done per-type in helper methods."""
        if isinstance(raw_data, list):
            return raw_data
        return [raw_data] if raw_data else []

    def _parse_budget_html(self, html: str, county_name: str) -> List[Dict[str, Any]]:
        """Parse county budget HTML page."""
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, Any]] = []

        for link in soup.find_all("a", href=re.compile(r"budget|finance|cfo|cfsp", re.I)):
            title = link.get_text(strip=True)
            href = link.get("href", "")
            if href.startswith("/"):
                href = f"{self.base_url}{href}"
            records.append({
                "title": title,
                "url": href,
                "county": county_name,
                "data_type": "budget",
                "source": f"county_{county_name.lower()}",
                "fetched_at": datetime.utcnow().isoformat(),
            })

        # Budget tables
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all(["th"])]
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) < 2:
                    continue
                record = dict(zip(headers, cells))
                record["county"] = county_name
                record["data_type"] = "budget"
                record["source"] = f"county_{county_name.lower()}"
                record["fetched_at"] = datetime.utcnow().isoformat()
                records.append(record)

        return records

    def _parse_procurement_html(self, html: str, county_name: str) -> List[Dict[str, Any]]:
        """Parse county procurement HTML."""
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, Any]] = []

        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all(["th"])]
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) < 3:
                    continue
                record = dict(zip(headers, cells))
                record["county"] = county_name
                record["data_type"] = "procurement"
                record["source"] = f"county_{county_name.lower()}"
                record["fetched_at"] = datetime.utcnow().isoformat()
                records.append(record)

        return records

    def _parse_projects_html(self, html: str, county_name: str) -> List[Dict[str, Any]]:
        """Parse county development projects."""
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, Any]] = []

        for card in soup.find_all(class_=re.compile(r"project|card|item", re.I)):
            title_el = card.find(["h2", "h3", "h4", "a"])
            title = title_el.get_text(strip=True) if title_el else ""
            desc_el = card.find("p")
            desc = desc_el.get_text(strip=True) if desc_el else ""
            status_el = card.find(class_=re.compile(r"status|badge", re.I))
            status = status_el.get_text(strip=True) if status_el else ""

            records.append({
                "title": title,
                "description": desc,
                "status": status,
                "county": county_name,
                "data_type": "project",
                "source": f"county_{county_name.lower()}",
                "fetched_at": datetime.utcnow().isoformat(),
            })

        return records

    def _parse_reports_html(self, html: str, county_name: str) -> List[Dict[str, Any]]:
        """Parse county reports."""
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, Any]] = []

        for link in soup.find_all("a", href=re.compile(r"report|audit|annual", re.I)):
            title = link.get_text(strip=True)
            href = link.get("href", "")
            if href.startswith("/"):
                href = f"{self.base_url}{href}"
            records.append({
                "title": title,
                "url": href,
                "county": county_name,
                "data_type": "report",
                "source": f"county_{county_name.lower()}",
                "fetched_at": datetime.utcnow().isoformat(),
            })

        return records

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a county record."""
        return bool(record.get("title") or record.get("county"))


county_scraper = CountyPortalsScraper()

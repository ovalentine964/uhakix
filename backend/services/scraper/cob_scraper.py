"""
Controller of Budget Scraper — Kenya's Office of the Controller of Budget
Source: cob.go.ke
Scrapes budget execution reports, county expenditure, and national government reports.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class COBScraper(BaseScraper):
    """Scrape Controller of Budget reports."""

    base_url = "https://www.cob.go.ke"
    source_name = "controller_of_budget"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(0.5)

    async def fetch(
        self,
        report_type: str = "county_government",
        fiscal_year: Optional[str] = None,
        quarter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch budget execution reports.

        Args:
            report_type: county_government, national_government, public_debt
            fiscal_year: FY like "2023/24"
            quarter: Q1, Q2, Q3, Q4, Annual

        Returns:
            List of budget line items
        """
        try:
            # Build URL with filters
            path = f"/reports/{report_type}"
            params: Dict[str, Any] = {}
            if fiscal_year:
                params["year"] = fiscal_year
            if quarter:
                params["quarter"] = quarter

            # Try API endpoint
            try:
                raw = await self.fetch_json(f"{self.base_url}/api/reports", params={**params, "type": report_type})
                records = self.parse(raw)
                logger.info("cob_fetch_success", count=len(records), type=report_type, source="api")
                return records
            except (ScraperError, Exception):
                pass

            # HTML scrape
            html = await self.fetch_html(f"{self.base_url}{path}", params=params)
            records = self.parse({"html": html, "report_type": report_type, "year": fiscal_year, "quarter": quarter})
            logger.info("cob_fetch_success", count=len(records), type=report_type, source="html")
            return records

        except (ScraperError, Exception) as e:
            logger.error("cob_fetch_failed", error=str(e), report_type=report_type)
            return []

    async def fetch_county_report(self, county_name: str, fiscal_year: str) -> Optional[Dict[str, Any]]:
        """Fetch budget execution for a specific county."""
        try:
            html = await self.fetch_html(
                f"{self.base_url}/reports/county_government",
                params={"county": county_name, "year": fiscal_year},
            )
            soup = BeautifulSoup(html, "lxml")
            return self._parse_county_detail(soup, county_name, fiscal_year)
        except Exception as e:
            logger.error("cob_county_failed", county=county_name, error=str(e))
            return None

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse COB report data."""
        records: List[Dict[str, Any]] = []

        if isinstance(raw_data, dict) and "data" in raw_data:
            items = raw_data["data"] if isinstance(raw_data["data"], list) else [raw_data["data"]]
            for item in items:
                record = self._normalize_budget_line(item)
                if record and self.validate_record(record):
                    records.append(record)

        if isinstance(raw_data, dict) and "html" in raw_data:
            soup = BeautifulSoup(raw_data["html"], "lxml")

            # COB reports are typically structured tables
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True).lower() for th in table.find_all(["th"])]
                for row in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cells) < 2:
                        continue
                    record_data = {}
                    for i, h in enumerate(headers):
                        if i < len(cells):
                            record_data[h] = cells[i]
                    record_data["report_type"] = raw_data.get("report_type", "")
                    record_data["fiscal_year"] = raw_data.get("year", "")
                    record_data["quarter"] = raw_data.get("quarter", "")
                    normalized = self._normalize_budget_line(record_data)
                    if normalized and self.validate_record(normalized):
                        records.append(normalized)

        logger.info("cob_parse_complete", count=len(records))
        return records

    def _normalize_budget_line(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a budget line item."""
        if not raw or not isinstance(raw, dict):
            return None

        def parse_amount(val: str) -> float:
            if not val:
                return 0.0
            clean = re.sub(r"[^\d.]", "", str(val).replace(",", ""))
            try:
                return float(clean) if clean else 0.0
            except ValueError:
                return 0.0

        allocation = parse_amount(raw.get("allocation", raw.get("budget", raw.get("approved_budget", ""))))
        absorption = parse_amount(raw.get("absorption", raw.get("spent", raw.get("expenditure", raw.get("actual", "")))))
        variance = 0.0
        if allocation > 0:
            variance = ((absorption - allocation) / allocation) * 100

        return {
            "entity": raw.get("entity", raw.get("county", raw.get("ministry", raw.get("name", "")))),
            "sector": raw.get("sector", raw.get("vote_head", raw.get("program", ""))),
            "fiscal_year": raw.get("fiscal_year", raw.get("year", "")),
            "quarter": raw.get("quarter", raw.get("period", "")),
            "allocated_kes": allocation,
            "absorbed_kes": absorption,
            "variance_pct": round(variance, 2),
            "absorption_rate": round((absorption / allocation * 100) if allocation > 0 else 0, 2),
            "report_type": raw.get("report_type", "controller_of_budget"),
            "source": "cob.go.ke",
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def _parse_county_detail(self, soup: BeautifulSoup, county: str, year: str) -> Optional[Dict[str, Any]]:
        """Parse a county-specific budget detail page."""
        data: Dict[str, Any] = {"county": county, "fiscal_year": year}
        for label in soup.find_all(["dt", "strong", "label"]):
            key = label.get_text(strip=True).lower().rstrip(":")
            dd = label.find_next_sibling(["dd", "span", "p"])
            if dd:
                data[key] = dd.get_text(strip=True)
        return self._normalize_budget_line(data)

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate budget line record."""
        if not record.get("entity"):
            return False
        if record.get("allocated_kes", 0) < 0:
            return False
        return True


cob_scraper = COBScraper()

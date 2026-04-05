"""
IFMIS Scraper — Kenya's Integrated Financial Management Information System
Source: ifmis.go.ke (and Treasury API mirror)
Scrapes government transactions, payment vouchers, and commitment data.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from services.scraper.base import BaseScraper, ScraperError
from datetime import datetime
import structlog
import re

logger = structlog.get_logger()


class IFMISScraper(BaseScraper):
    """Scrape IFMIS transaction data from Treasury/IFMIS portals."""

    base_url = "https://www.treasury.go.ke"
    source_name = "ifmis"

    def __init__(self):
        super().__init__()
        self._set_rate_limit(0.5)  # Conservative: 1 req per 2 seconds

    async def fetch(
        self,
        ministry: Optional[str] = None,
        fiscal_year: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Fetch IFMIS transaction records.

        Args:
            ministry: Filter by ministry name
            fiscal_year: Filter by fiscal year (e.g., "2023/24")
            page: Page number for pagination
            limit: Records per page

        Returns:
            List of transaction records
        """
        records: List[Dict[str, Any]] = []

        try:
            # Attempt API endpoint first (modern government portals often expose APIs)
            params: Dict[str, Any] = {
                "page": page,
                "limit": limit,
                "format": "json",
            }
            if ministry:
                params["ministry"] = ministry
            if fiscal_year:
                params["fiscal_year"] = fiscal_year

            # Primary: Treasury open data API
            try:
                raw = await self.fetch_json(
                    f"{self.base_url}/api/v1/ifmis/transactions",
                    params=params,
                )
                records = self.parse(raw)
                logger.info(
                    "ifmis_fetch_success",
                    record_count=len(records),
                    page=page,
                    source="api",
                )
                return records
            except (ScraperError, Exception):
                logger.debug(
                    "ifmis_api_unavailable",
                    attempting="html_scrape",
                )

            # Fallback: Scrape HTML from budget/estimates pages
            html = await self.fetch_html(f"{self.base_url}/budget-estimates")
            records = self.parse({"html": html, "metadata": params})

            logger.info(
                "ifmis_fetch_success",
                record_count=len(records),
                page=page,
                source="html",
            )

        except (ScraperError, Exception) as e:
            logger.error("ifmis_fetch_failed", error=str(e), ministry=ministry)
            records = []

        return records

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse IFMIS data from JSON API or HTML."""
        records: List[Dict[str, Any]] = []

        # JSON API response
        if isinstance(raw_data, dict) and "data" in raw_data:
            items = raw_data["data"] if isinstance(raw_data["data"], list) else [raw_data["data"]]
            for item in items:
                record = self._normalize_transaction(item)
                if record and self.validate_record(record):
                    records.append(record)

        # HTML scrape
        if isinstance(raw_data, dict) and "html" in raw_data:
            html = raw_data["html"]
            soup = BeautifulSoup(html, "lxml")

            # Look for tables with transaction data
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                if len(rows) < 2:
                    continue

                headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]

                for row in rows[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cells) < 3:
                        continue

                    record = {}
                    for i, header in enumerate(headers):
                        if i < len(cells):
                            record[header] = cells[i]

                    normalized = self._normalize_transaction(record)
                    if normalized and self.validate_record(normalized):
                        records.append(normalized)

        logger.info("ifmis_parse_complete", record_count=len(records))
        return records

    def _normalize_transaction(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a raw transaction record to our schema."""
        if not raw or not isinstance(raw, dict):
            return None

        # Extract amount — handle KES formatting
        amount_raw = str(raw.get("amount", raw.get("amount_kes", raw.get("paid", "0"))))
        amount_clean = re.sub(r"[^\d.]", "", amount_raw.replace(",", ""))
        try:
            amount = float(amount_clean) if amount_clean else 0.0
        except ValueError:
            amount = 0.0

        # Extract date
        date_str = str(raw.get("date", raw.get("transaction_date", raw.get("payment_date", ""))))
        parsed_date = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                parsed_date = datetime.strptime(date_str, fmt).isoformat()
                break
            except ValueError:
                continue

        return {
            "id": raw.get("id", raw.get("transaction_id", raw.get("reference", ""))),
            "date": parsed_date or date_str,
            "ministry": raw.get("ministry", raw.get("vote", raw.get("mda", ""))).strip(),
            "department": raw.get("department", raw.get("program", "")).strip(),
            "amount_kes": amount,
            "purpose": raw.get("purpose", raw.get("description", raw.get("object", ""))).strip(),
            "vendor": raw.get("vendor", raw.get("payee", raw.get("contractor", ""))).strip(),
            "ifmis_code": raw.get("ifmis_code", raw.get("commitment_no", raw.get("voucher_no", ""))).strip(),
            "source": "ifmis",
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a transaction record has required fields."""
        required = ["ministry", "amount_kes", "date"]
        if not all(record.get(f) for f in required):
            return False
        if record["amount_kes"] < 0:
            return False
        return True


ifmis_scraper = IFMISScraper()

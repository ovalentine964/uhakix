"""
RIFT — Procurement Analysis Agent
NVIDIA Model: Nemotron-4-340B
Triggers: New tender, contract awarded, vendor appears in multiple contracts
Role: Monitors government procurement. Identifies bid-rigging patterns,
overpriced contracts, and vendor conflicts.
"""

from typing import Dict, Any, List
from agents.base import Agent


class RiftAgent(Agent):
    name = "RIFT"
    role = "Procurement Analysis — Monitors tenders, contracts, and procurement patterns"
    model_key = "complex"  # Nemotron-4-340B
    triggers = ["new_tender", "contract_awarded", "vendor_multi_contract"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "analyze_tender")

        if action == "analyze_tender":
            return await self._analyze_tender(input_data)
        elif action == "vendor_analysis":
            return await self._analyze_vendor(input_data)
        elif action == "bid_rigging_check":
            return await self._check_bid_rigging(input_data)
        else:
            return {"error": "Unknown action", "available": [
                "analyze_tender", "vendor_analysis", "bid_rigging_check",
            ]}

    async def _analyze_tender(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Analyze this Kenyan government tender for potential issues:
        Title: {data.get("title", "")}
        Ministry: {data.get("ministry", "")}
        Estimated Cost: KES {data.get("estimated_cost", 0):,.2f}
        Awarded Amount: KES {data.get("awarded_amount", 0):,.2f}
        Contractor: {data.get("contractor", "")}

        Analyze:
        1. Price markup percentage (awarded vs estimated)
        2. Is the contractor a repeat winner with this ministry?
        3. Timeline red flags (awarded too fast, no competition)
        4. Contract type appropriateness

        JSON: {{"markup_pct": 0, "risk_indicators": [], "analysis": "", "risk_level": "low|medium|high"}}
        """

        result = await self.call_nvidia(
            [{"role": "user", "content": prompt}],
            json_response=True,
        )

        return {
            "tender_id": data.get("id"),
            "analysis": result,
            "sources": ["tenders.go.ke", "company_registry"],
        }

    async def _analyze_vendor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Analyze this vendor's government contract history:
        Vendor: {data.get("vendor_name", "")}
        Contracts: {data.get("contracts", [])}
        Total Value: KES {data.get("total_value", 0):,.2f}

        Look for:
        1. Dominant position in specific ministries
        2. Geographic concentration
        3. Relationship patterns with other vendors
        4. Growth rate vs market size

        JSON: {{"profile": "", "concentration_risk": "low|medium|high", "patterns": []}}
        """

        return {
            "vendor": data.get("vendor_name"),
            "analysis": await self.call_nvidia(
                [{"role": "user", "content": prompt}],
                json_response=True,
            ),
        }

    async def _check_bid_rigging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tender = data.get("tender", {})
        bids = data.get("bids", [])

        prompt = f"""
        Check for bid rigging indicators in this tender:
        Tender: {tender.get("reference_number", "")}
        Number of Bids: {len(bids)}
        Bid Amounts: {bids}

        Analyze:
        1. Bid price clustering (unusually close amounts)
        2. Cover bidding (one very high bid, others close)
        3. Bid rotation patterns with other tenders
        4. Same directors across bidding companies

        JSON: {{"bid_rigging_score": 0.0, "indicators": [], "explanation": "", "recommendation": ""}}
        """

        return {
            "tender": tender.get("reference_number"),
            "analysis": await self.call_nvidia(
                [{"role": "user", "content": prompt}],
                json_response=True,
            ),
        }

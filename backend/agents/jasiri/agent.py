"""
JASIRI — Budget Intelligence Agent
NVIDIA Model: Nemotron-4-340B
Triggers: New budget data, variance >10%, quarterly review
Role: Analyzes government budgets vs actual spending. Deep analysis of allocation patterns.
"""

from typing import Dict, List, Any
from agents.base import Agent


class JasiriAgent(Agent):
    name = "JASIRI"
    role = "Budget Intelligence — Analyzes government budget allocation vs spending"
    model_key = "complex"  # Nemotron-4-340B
    triggers = ["new_budget_data", "variance_gt_10pct", "quarterly_review"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze budget data and identify anomalies."""
        action = input_data.get("action", "analyze_variance")

        if action == "analyze_variance":
            return await self._analyze_budget_variance(input_data)
        elif action == "county_comparison":
            return await self._county_budget_comparison(input_data)
        elif action == "trend_analysis":
            return await self._budget_trend_analysis(input_data)
        else:
            return {"error": "Unknown action", "available_actions": [
                "analyze_variance", "county_comparison", "trend_analysis"
            ]}

    async def _analyze_budget_variance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ministry = data.get("ministry", "")
        allocated = data.get("allocated_kes", 0)
        spent = data.get("spent_kes", 0)
        fiscal_year = data.get("fiscal_year", "")

        if allocated == 0:
            return {
                "ministry": ministry,
                "fiscal_year": fiscal_year,
                "variance_pct": 0,
                "anomaly_detected": False,
                "explanation": "No budget allocated.",
            }

        variance_pct = ((spent - allocated) / allocated) * 100
        anomaly = abs(variance_pct) > 10

        # Use Nemotron-4 for deep analysis
        prompt = f"""
        Analyze this Kenyan government budget variance:
        Ministry: {ministry}
        Fiscal Year: {fiscal_year}
        Budget Allocated: KES {allocated:,.2f}
        Amount Spent: KES {spent:,.2f}
        Variance: {variance_pct:.1f}%

        Provide analysis in 3-5 sentences. Focus on:
        1. Is this variance unusual for this type of ministry?
        2. Possible explanations (without making accusations)
        3. What citizens should look for

        Respond in JSON with keys: assessment, possible_explanations, citizen_action, risk_level
        """

        analysis = await self.call_nvidia(
            [{"role": "user", "content": prompt}],
            json_response=True,
        )

        connection_report = {
            "entity_name": ministry,
            "entity_type": "ministry",
            "connections": [],
            "total_transactions": spent,
            "flagged_patterns": ["variance_gt_10pct"] if anomaly else [],
            "sources": ["Controller of Budget", "National Treasury", "IFMIS"],
        }

        return {
            "ministry": ministry,
            "fiscal_year": fiscal_year,
            "allocated_kes": allocated,
            "spent_kes": spent,
            "variance_pct": round(variance_pct, 2),
            "anomaly_detected": anomaly,
            "analysis": analysis,
            "connection_report": connection_report,
            "sources_used": ["cob.go.ke", "treasury.go.ke", "ifmis.go.ke"],
        }

    async def _county_budget_comparison(self, data: Dict[str, Any]) -> Dict[str, Any]:
        counties = data.get("counties", [])

        prompt = f"""
        Compare budget execution across these Kenyan counties:
        {counties}

        Look for patterns in:
        - Development spending vs recurrent spending
        - Budget absorption rates
        - Geographic distribution patterns

        JSON response: {{"summary": "...", "top_performers": [], "underperformers": [], "observations": []}}
        """

        return {
            "action": "county_comparison",
            "analysis": await self.call_nvidia(
                [{"role": "user", "content": prompt}],
                json_response=True,
            ),
        }

    async def _budget_trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Analyze budget trends for {data.get("entity", "Kenya Government")}.
        Time period: {data.get("period", "2020-2024")}
        Historical data: {data.get("historical_data", [])}

        Identify:
        1. Growth patterns
        2. Spending shifts between categories
        3. Recurring anomalies

        JSON: {{"trends": [], "shifts": [], "anomalies": [], "summary": "..."}}
        """

        return {
            "action": "trend_analysis",
            "trends": await self.call_nvidia(
                [{"role": "user", "content": prompt}],
                json_response=True,
            ),
        }

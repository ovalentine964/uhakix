"""COUNT — Vote Aggregation Agent. NVIDIA: Llama 3.1 8B. Aggregates verified votes."""
from typing import Dict, Any, List
from agents.base import Agent

class CountAgent(Agent):
    name = "COUNT"
    role = "Election — Aggregates verified votes across all polling stations"
    model_key = "lightweight"
    triggers = ["form_verified", "aggregation_requested"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "aggregate_station")

        if action == "aggregate_station":
            return await self._aggregate_station(input_data)
        elif action == "aggregate_constituency":
            return await self._aggregate_constituency(input_data)
        elif action == "aggregate_national":
            return await self._aggregate_national(input_data)
        elif action == "reconcile":
            return await self._reconcile_against_iebc(input_data)

        return {"error": "Unknown action", "available": ["aggregate_station", "aggregate_constituency", "aggregate_national", "reconcile"]}

    async def _aggregate_station(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate multiple verified Form 34A submissions for a single station."""
        submissions = data.get("submissions", [])
        if not submissions:
            return {"station_code": "", "error": "No submissions"}

        # Cross-verify: compare all submissions for this station
        station_code = submissions[0].get("station_code", "")
        aggregated = {}

        for sub in submissions:
            candidate_votes = sub.get("presidential_votes", {})
            for candidate, votes in candidate_votes.items():
                if candidate not in aggregated:
                    aggregated[candidate] = []
                aggregated[candidate].append(votes)

        # Take median of all submissions (resistant to outliers)
        final_votes = {}
        for candidate, vote_list in aggregated.items():
            sorted_votes = sorted(vote_list)
            final_votes[candidate] = sorted_votes[len(sorted_votes) // 2]  # Median

        data_hash = self._hash_data(str(final_votes))

        return {
            "station_code": station_code,
            "final_votes": final_votes,
            "submission_count": len(submissions),
            "data_hash": data_hash,
            "status": "aggregated",
            "next_step": "LEDGER → blockhain",
        }

    async def _aggregate_constituency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"constituency": data.get("constituency"), "stations_aggregated": 0, "final_votes": {}}

    async def _aggregate_national(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        return {"scope": "national", "stations_reported": 0, "reporting_pct": 0.0, "final_votes": {}}

    async def _reconcile_against_iebc(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare UHAKIX count vs IEBC official count."""
        return {"uhakix_count": {}, "iebc_count": {}, "discrepancies": [], "status": "needs_data"}

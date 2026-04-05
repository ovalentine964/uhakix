"""
SPHINX — Anomaly Detection Agent
NVIDIA Model: Nemotron-4-340B
Triggers: Statistical outlier, pattern shift, periodic scan
Role: Statistical anomaly detection across all government data streams.
"""

from typing import Dict, Any, List
from agents.base import Agent
import numpy as np


class SphinxAgent(Agent):
    name = "SPHINX"
    role = "Anomaly Detection — Statistical outlier detection across all data"
    model_key = "complex"  # Nemotron-4-340B
    triggers = ["statistical_outlier", "pattern_shift", "periodic_scan"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "scan")

        if action == "scan":
            return await self._full_scan(input_data)
        elif action == "detect_outlier":
            return await self._detect_outlier(input_data)
        elif action == "pattern_analysis":
            return await self._pattern_analysis(input_data)
        else:
            return {"error": "Unknown action", "available": [
                "scan", "detect_outlier", "pattern_analysis"
            ]}

    async def _full_scan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run anomaly scan across all data streams."""
        results = []

        # Check transaction amounts
        transactions = data.get("transactions", [])
        if transactions:
            amounts = [t.get("amount_kes", 0) for t in transactions]
            results.extend(self._zscore_anomaly(amounts, "transaction_amount"))

        # Check spending velocity
        monthly_spending = data.get("monthly_spending", [])
        if monthly_spending:
            results.extend(self._trend_anomaly(monthly_spending, "spending_velocity"))

        # Use AI for qualitative analysis
        if results:
            prompt = f"""
            Review these detected statistical anomalies in Kenyan government data:
            {results}

            For each anomaly, provide:
            1. Contextual significance
            2. Whether it warrants a connection report
            3. Related entities to investigate

            JSON: {{"anomalies_assessed": [], "prioritized": []}}
            """

            ai_assessment = await self.call_nvidia(
                [{"role": "user", "content": prompt}],
                json_response=True,
            )

            return {
                "scan_complete": True,
                "anomalies_found": len(results),
                "statistical_anomalies": results,
                "ai_assessment": ai_assessment,
            }

        return {"scan_complete": True, "anomalies_found": 0}

    async def _detect_outlier(self, data: Dict[str, Any]) -> Dict[str, Any]:
        dataset = data.get("values", [])
        metric = data.get("metric", "unknown")

        if not dataset:
            return {"anomaly": False, "reason": "No data"}

        anomalies = self._zscore_anomaly(dataset, metric)

        return {
            "metric": metric,
            "anomalies": anomalies,
            "threshold": 3.0,  # 3 standard deviations
        }

    async def _pattern_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Analyze this pattern for anomalies:
        Entity: {data.get("entity", "")}
        Data Points: {data.get("data_points", [])}
        Time Period: {data.get("period", "")}

        Look for:
        1. Seasonal deviations
        2. Step changes
        3. Cyclical irregularities
        4. Endpoint effects (end of financial year spending spikes)

        JSON: {{"patterns": [], "irregularities": [], "significance": ""}}
        """

        return {
            "analysis": await self.call_nvidia(
                [{"role": "user", "content": prompt}],
                json_response=True,
            ),
        }

    def _zscore_anomaly(self, values: List[float], metric_name: str) -> List[Dict]:
        """Detect anomalies using Z-score (3+ stddev from mean)."""
        if len(values) < 3:
            return []

        arr = np.array(values, dtype=float)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return []

        anomalies = []
        for i, v in enumerate(values):
            z = abs((v - mean) / std)
            if z >= 3.0:
                anomalies.append({
                    "index": i,
                    "value": v,
                    "z_score": round(float(z), 2),
                    "mean": round(float(mean), 2),
                    "std": round(float(std), 2),
                    "metric": metric_name,
                })

        return anomalies

    def _trend_anomaly(self, data: List[Dict], metric: str) -> List[Dict]:
        """Detect trend breaks in time series."""
        values = [d.get("value", 0) for d in data]
        if len(values) < 6:
            return []

        # Simple: detect month-over-month change > 50%
        anomalies = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                change = abs(values[i] - values[i-1]) / values[i-1]
                if change > 0.5:
                    anomalies.append({
                        "index": i,
                        "value": values[i],
                        "previous_value": values[i-1],
                        "change_pct": round(change * 100, 1),
                        "metric": metric,
                    })

        return anomalies

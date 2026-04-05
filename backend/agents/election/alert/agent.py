"""ALERT — Election Anomaly Detection. Reuses SPHINX + real-time checks."""
from typing import Dict, Any, List
from agents.base import Agent
import numpy as np

class AlertAgent(Agent):
    name = "ALERT"
    role = "Election — Real-time anomaly detection for election data"
    model_key = "complex"
    triggers = ["new_form_verified", "station_complete", "periodic_scan"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "monitor")
        if action == "monitor":
            return await self._monitor_stations(input_data)
        elif action == "check_turnout":
            return await self._check_turnout_anomaly(input_data)
        elif action == "check_duplication":
            return await self._check_duplicate_submission(input_data)
        elif action == "check_timing":
            return await self._check_timing_anomaly(input_data)
        return {"action": action, "status": "available"}

    async def _monitor_stations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        stations = data.get("stations", [])
        alerts = []

        for station in stations:
            anomalies = await self._analyze_station(station)
            if anomalies:
                alerts.extend(anomalies)

        # AI assessment of alert patterns
        if alerts:
            prompt = f"Review these election anomalies and prioritize: {str(alerts)}"
            assessment = await self.call_nvidia([{"role": "user", "content": prompt}], json_response=True)
            return {"alert_count": len(alerts), "alerts": alerts, "ai_assessment": assessment}

        return {"alert_count": 0, "alerts": []}

    async def _check_turnout_anomaly(self, data: Dict[str, Any]) -> Dict[str, Any]:
        votes_cast = data.get("votes_cast", 0)
        registered = data.get("registered_voters", 1)
        turnout = votes_cast / registered if registered > 0 else 0
        
        anomaly = turnout > 0.95 or turnout < 0.15
        severity = "high" if turnout > 1.0 else "medium" if turnout > 0.95 or turnout < 0.15 else "low"
        
        return {
            "station": data.get("station_code"),
            "turnout_pct": round(turnout * 100, 1),
            "anomaly": anomaly,
            "severity": severity,
            "note": "Turnout > 95% or < 15% flagged for review" if anomaly else "Normal turnout range"
        }

    async def _check_duplicate_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        submissions = data.get("submissions", [])
        hashes = [s.get("image_hash", "") for s in submissions]
        unique_hashes = set(hashes)
        duplicates = len(hashes) - len(unique_hashes)
        
        return {
            "station": data.get("station_code"),
            "total_submissions": len(submissions),
            "unique_images": len(unique_hashes),
            "exact_duplicates": duplicates,
            "suspicious": duplicates > 0
        }

    async def _check_timing_anomaly(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"station": data.get("station_code"), "timing_analysis": "available"}

    async def _analyze_station(self, station: Dict[str, Any]) -> List[Dict]:
        alerts = []
        votes_cast = station.get("total_votes_cast", 0)
        registered = station.get("registered_voters", 1)
        
        if registered > 0:
            turnout = votes_cast / registered
            if turnout > 0.95:
                alerts.append({
                    "alert_type": "turnout_anomaly",
                    "severity": "high" if turnout > 1.0 else "medium",
                    "station": station.get("station_code"),
                    "description": f"Turnout {turnout*100:.1f}% exceeds normal range",
                    "value": turnout,
                })
            elif turnout < 0.15:
                alerts.append({
                    "alert_type": "low_turnout",
                    "severity": "medium",
                    "station": station.get("station_code"),
                    "description": f"Turnout {turnout*100:.1f}% below normal range",
                    "value": turnout,
                })
        
        return alerts

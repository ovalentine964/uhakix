"""ATLAS — Geographic Analysis. NVIDIA: Llama 3.1 70B. Maps data to geography."""
from typing import Dict, Any
from agents.base import Agent

class AtlasAgent(Agent):
    name = "ATLAS"
    role = "Geographic Analysis — County comparisons, regional heatmaps"
    model_key = "general"
    triggers = ["location_data_ingested", "mapping_request", "regional_comparison"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "county_heatmap")
        if action == "county_heatmap":
            return await self._county_heatmap(input_data)
        elif action == "regional_comparison":
            return await self._regional_comparison(input_data)
        return {"action": action, "status": "available"}

    async def _county_heatmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Analyze geographic patterns in Kenyan government data by county: {str(data)}"
        analysis = await self.call_nvidia([{"role": "user", "content": prompt}], json_response=True)
        return {"action": "county_heatmap", "analysis": analysis}

    async def _regional_comparison(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Compare regions: {str(data)}. Identify spending patterns per capita."
        analysis = await self.call_nvidia([{"role": "user", "content": prompt}], json_response=True)
        return {"action": "regional_comparison", "analysis": analysis}

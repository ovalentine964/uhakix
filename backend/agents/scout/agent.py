"""
SCOUT — Network Mapping Agent
NVIDIA Model: Llama 3.1 70B
Triggers: New entity discovered, cross-reference request, graph update
Role: Builds and maintains entity relationship graph. Discovers connections.
"""

from typing import Dict, Any, List
from agents.base import Agent

class ScoutAgent(Agent):
    name = "SCOUT"
    role = "Network Mapping — Entity relationship discovery and graph traversal"
    model_key = "general"  # Llama 3.1 70B
    triggers = ["new_entity_discovered", "cross_reference_request", "graph_update"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "map_connections")
        if action == "map_connections":
            return await self._map_connections(input_data)
        elif action == "find_path":
            return await self._find_path(input_data)
        elif action == "cross_reference":
            return await self._cross_reference(input_data)
        return {"error": "Unknown action", "available": ["map_connections", "find_path", "cross_reference"]}

    async def _map_connections(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Map all connections for entity: {data.get("entity_name", "")}
        Entity Type: {data.get("entity_type", "")}
        Known data: {data.get("known_data", {})}

        Find connections using:
        1. Company registry: directors, shareholders
        2. Procurement: contracts, tenders
        3. Gazette: appointments, resignations
        4. Transaction data: payments, beneficiaries

        JSON: {{"entity": "...", "connections": [], "connection_paths": [], "risk_flags": []}}
        """
        return {"action": "map_connections", "result": await self.call_nvidia([{"role": "user", "content": prompt}], json_response=True)}

    async def _find_path(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Find the connection path between:
        Entity A: {data.get("entity_a", "")}
        Entity B: {data.get("entity_b", "")}
        Known intermediate entities: {data.get("intermediates", [])}

        What is the shortest connection path? Include intermediate steps.

        JSON: {{"path": [], "path_length": 0, "explanation": "", "confidence": 0.0}}
        """
        return {"action": "find_path", "result": await self.call_nvidia([{"role": "user", "content": prompt}], json_response=True)}

    async def _cross_reference(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Cross-reference these entities for patterns:
        Entities: {data.get("entities", [])}
        Context: {data.get("context", "")}

        Look for: shared directors, shared addresses, shared tenders, temporal patterns.

        JSON: {{"shared_elements": [], "patterns": [], "significance": ""}}
        """
        return {"action": "cross_reference", "result": await self.call_nvidia([{"role": "user", "content": prompt}], json_response=True)}

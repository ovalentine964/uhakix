"""LEDGER — Blockchain Sync Agent. NVIDIA: Phi-3 mini. Pushes hashes to Polygon."""
from typing import Dict, Any, List
from agents.base import Agent

class LedgerAgent(Agent):
    name = "LEDGER"
    role = "Blockchain Sync — Pushes verified data hashes to Polygon blockchain"
    model_key = "edge"
    triggers = ["new_verified_data", "batch_threshold_reached", "periodic_sync"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "hash_to_chain")
        data_items = input_data.get("data_items", [])

        if action == "hash_to_chain":
            return await self._hash_single(data_items)
        elif action == "hash_batch":
            return await self._hash_batch(data_items, input_data.get("batch_id", ""))
        return {"action": action, "status": "ready"}

    async def _hash_single(self, data_items: List) -> Dict[str, Any]:
        hashes = []
        for item in data_items:
            h = self._hash_data(str(item))
            hashes.append(h)
        return {
            "action": "hash_to_chain",
            "hashes": hashes,
            "network": "polygon-amoy",
            "status": "pending_broadcast",
        }

    async def _hash_batch(self, data_items: List, batch_id: str) -> Dict[str, Any]:
        hashes = [self._hash_data(str(item)) for item in data_items]
        combined_hash = self._hash_data("".join(sorted(hashes)))
        return {
            "batch_id": batch_id,
            "hash_count": len(hashes),
            "combined_hash": combined_hash,
            "individual_hashes": hashes,
            "network": "polygon-amoy",
            "status": "pending_broadcast",
        }

"""KAZI — Task Orchestrator. NVIDIA: Llama 3.1 8B. Routes queries to correct agents."""
from typing import Dict, Any, List
from agents.base import Agent

class KaziAgent(Agent):
    name = "KAZI"
    role = "Task Orchestrator — Routes queries to correct agents and coordinates workflows"
    model_key = "lightweight"  # Llama 3.1 8B
    triggers = ["agent_request", "pipeline_trigger", "user_query"]

    ROUTING_PLAN = {
        "budget": ["JASIRI"],
        "spending": ["JASIRI"],
        "tender": ["RIFT"],
        "procurement": ["RIFT"],
        "company": ["SCOUT", "RIFT"],
        "person": ["SCOUT"],
        "connection": ["SCOUT"],
        "anomaly": ["SPHINX"],
        "outlier": ["SPHINX"],
        "election": ["POLL_WITNESS", "VERIFY", "COUNT"],
        "vote": ["COUNT"],
        "form 34a": ["POLL_WITNESS", "VERIFY"],
        "report": ["HERALD"],
        "ask": ["HERALD"],
        "map": ["ATLAS"],
        "county": ["ATLAS", "JASIRI"],
        "blockchain": ["LEDGER"],
        "verify on-chain": ["LEDGER"],
    }

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        # Route to appropriate agents
        routed_agents = self._route_query(query)
        return {"query": query, "routed_to": routed_agents, "orchestration_plan": f"Dispatch to: {', '.join(routed_agents)}"}

    def _route_query(self, query: str) -> List[str]:
        query_lower = query.lower()
        scored: Dict[str, int] = {}
        for keyword, agents in self.ROUTING_PLAN.items():
            if keyword in query_lower:
                for agent in agents:
                    scored[agent] = scored.get(agent, 0) + 1
        if not scored:
            return ["HERALD"]  # Default: citizen-facing
        return sorted(scored.keys(), key=lambda x: scored[x], reverse=True)

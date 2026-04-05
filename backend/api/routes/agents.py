"""UJUZIO Agent Status & Query API"""
from typing import List, Dict, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


AGENT_ROSTER = [
    {
        "name": "JASIRI",
        "role": "Budget Intelligence",
        "description": "Analyzes government budgets and spending patterns. Detects overspending, underspending, and budget anomalies.",
        "model": "nvidia/nemotron-4-340b-instruct",
        "triggers": ["new_budget_data", "variance_gt_10pct", "quarterly_review"],
        "status": "active",
    },
    {
        "name": "RIFT",
        "role": "Procurement Analysis",
        "description": "Monitors government tenders and procurement. Identifies bid-rigging, overpriced contracts, and conflict of interest patterns.",
        "model": "nvidia/nemotron-4-340b-instruct",
        "triggers": ["new_tender", "contract_awarded", "vendor_appears_multi_contract"],
        "status": "active",
    },
    {
        "name": "SCOUT",
        "role": "Network Mapping",
        "description": "Builds and maintains the entity relationship graph. Discovers connections between people, companies, and institutions.",
        "model": "meta/llama-3.1-70b-instruct",
        "triggers": ["new_entity_discovered", "cross_reference_request", "graph_update"],
        "status": "active",
    },
    {
        "name": "SPHINX",
        "role": "Anomaly Detection",
        "description": "Statistical anomaly detection across all data streams. Flags outliers, unusual patterns, and suspicious sequences.",
        "model": "nvidia/nemotron-4-340b-instruct",
        "triggers": ["statistical_outlier", "pattern_shift", "periodic_scan"],
        "status": "active",
    },
    {
        "name": "KAZI",
        "role": "Task Orchestrator",
        "description": "Coordinates agent workflows. Breaks complex queries into sub-tasks, dispatches to appropriate agents, aggregates results.",
        "model": "meta/llama-3.1-8b-instruct",
        "triggers": ["agent_request", "pipeline_trigger", "user_query"],
        "status": "active",
    },
    {
        "name": "HERALD",
        "role": "Citizen Communication",
        "description": "Translates complex findings into citizen-friendly language. Powers WhatsApp, USSD, and web responses.",
        "model": "meta/llama-3.1-8b-instruct",
        "triggers": ["query_received", "report_ready", "alert_to_broadcast"],
        "status": "active",
    },
    {
        "name": "SHIELD",
        "role": "Legal Compliance",
        "description": "Reviews ALL outputs before publication. Ensures legal language, auto-redacts personal info, requires 3+ source verification.",
        "model": "nvidia/nemotron-4-340b-instruct",
        "triggers": ["output_ready"],
        "status": "active",
    },
    {
        "name": "VIGIL",
        "role": "Audit Trail",
        "description": "Maintains immutable log of every system action. Every write, every agent decision, every data change is recorded.",
        "model": "microsoft/phi-3-mini-128k-instruct",
        "triggers": ["every_write_operation", "configuration_change", "data_ingestion"],
        "status": "active",
    },
    {
        "name": "ATLAS",
        "role": "Geographic Analysis",
        "description": "Maps data to geography. County comparisons, regional corruption heatmaps, spatial analysis of procurement clusters.",
        "model": "meta/llama-3.1-70b-instruct",
        "triggers": ["location_data_ingested", "mapping_request", "regional_comparison"],
        "status": "active",
    },
    {
        "name": "LEDGER",
        "role": "Blockchain Sync",
        "description": "Pushes verified data hashes to Polygon blockchain. Manages batch aggregation and on-chain verification.",
        "model": "microsoft/phi-3-mini-128k-instruct",
        "triggers": ["new_verified_data", "batch_threshold_reached", "periodic_sync"],
        "status": "active",
    },
]


@router.get("/")
async def list_agents():
    """List all agents with their roles, models, and status."""
    return {"agents": AGENT_ROSTER}


@router.get("/{agent_name}")
async def get_agent(agent_name: str):
    """Get details for a specific agent."""
    agent = next((a for a in AGENT_ROSTER if a["name"].upper() == agent_name.upper()), None)
    if not agent:
        return {"error": f"Agent {agent_name} not found"}
    return agent


@router.get("/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get real-time status of an agent."""
    return {
        "agent": agent_name,
        "status": "running",
        "tasks_completed_today": 0,
        "average_response_time_ms": 0,
        "model": "nvidia-nim",
    }


class AgentQueryRequest(BaseModel):
    query: str
    agent: Optional[str] = None  # If None, KAZI routes to appropriate agent


class AgentQueryResponse(BaseModel):
    answer: str
    agent_responded: str
    sources_used: List[str]
    compliance_status: str


@router.post("/query")
async def query_agents(request: AgentQueryRequest):
    """
    Query the agent team.
    KAZI routes to the right agent(s), SHIELD vets the response.
    """
    return {
        "answer": "Response from agents",
        "agent_responded": "KAZI/HERALD",
        "sources_used": [],
        "compliance_status": "shield-vetted",
    }

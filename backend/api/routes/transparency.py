"""UUHAKIX Transparency API — Government Financial Data"""
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field

router = APIRouter()


class TransactionResponse(BaseModel):
    id: str = Field(..., description="Transaction ID")
    date: date
    ministry: str
    department: str
    amount_kes: float
    purpose: str
    vendor: str
    ifmis_code: str
    sources_verified: int = Field(..., ge=3, description="Verification source count")


class EntityConnectionReport(BaseModel):
    """
    Connection report — NOT an accusation.
    Shows networks and relationships only.
    """
    entity_name: str
    entity_type: str  # person, company, ministry, county
    connections: List[dict]
    total_transactions: float
    flagged_patterns: List[str]
    source_count: int = Field(..., ge=3)
    compliance_status: str = "shield-vetted"


class BudgetVarianceReport(BaseModel):
    ministry: str
    fiscal_year: str
    allocated_kes: float
    spent_kes: float
    variance_pct: float
    anomaly_detected: bool
    explanation: str


# ── Transactions ────────────────────────────────────────────


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    ministry: Optional[str] = Query(None, description="Filter by ministry"),
    county: Optional[str] = Query(None, description="Filter by county"),
    amount_min: Optional[float] = Query(None, ge=0),
    amount_max: Optional[float] = Query(None, ge=0),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    vendor: Optional[str] = Query(None, description="Vendor name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Search government financial transactions from IFMIS.
    No ID required. Anyone can search.
    """
    # TODO: Query Neo4j for transaction data
    return []


@router.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get a single transaction with full context."""
    return {"id": transaction_id, "status": "available"}


# ── Entity Directory ────────────────────────────────────────


@router.get("/entities/{entity_id}/connections", response_model=EntityConnectionReport)
async def get_entity_connections(entity_id: str):
    """
    Get connection report for an entity (person, company, ministry).
    SCOUT agent builds the graph; SHIELD vets the output.
    """
    return EntityConnectionReport(
        entity_name="Sample Entity",
        entity_type="company",
        connections=[],
        total_transactions=0.0,
        flagged_patterns=[],
        source_count=3,
        compliance_status="shield-vetted",
    )


@router.get("/entities/{entity_id}/profile")
async def get_entity_profile(entity_id: str):
    """Full entity profile with aggregated data."""
    return {"id": entity_id, "profile": "available"}


# ── Budget Analysis ─────────────────────────────────────────


@router.get("/budget/{ministry}/variance", response_model=List[BudgetVarianceReport])
async def get_budget_variance(
    ministry: str,
    fiscal_year: Optional[str] = Query(None),
):
    """
    Budget vs actual spending analysis.
    JASIRI agent runs deep analysis on variance reports.
    """
    return []


@router.get("/county/{county_code}/budget")
async def get_county_budget(county_code: str, fiscal_year: Optional[str] = None):
    """County government budget data (47 counties)."""
    return {"county": county_code, "budget": "available"}


# ── Procurement / Tenders ──────────────────────────────────


@router.get("/tenders")
async def search_tenders(
    ministry: Optional[str] = None,
    status: Optional[str] = Query(None, description="open, awarded, cancelled"),
    amount_min: Optional[float] = None,
    vendor: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    """
    Search government tenders and procurement data.
    Source: tenders.go.ke
    """
    return {"tenders": [], "total": 0, "page": page}


@router.get("/tenders/{tender_id}")
async def get_tender(tender_id: str):
    """Full tender details with vendor connections."""
    return {"tender_id": tender_id}


# ── Anomaly Reports ────────────────────────────────────────


@router.get("/anomalies")
async def get_anomaly_reports(
    severity: str = Query("all", description="low, medium, high, critical, all"),
    category: str = Query("all", description="procurement, budget, election, all"),
    page: int = 1,
    page_size: int = 20,
):
    """
    SPHINX-detected anomalies in government data.
    Connection reports only — never accusations.
    """
    return {"anomalies": [], "total": 0}


@router.get("/anomalies/{anomaly_id}")
async def get_anomaly(anomaly_id: str):
    """Full anomaly detail with sources and connections."""
    return {"id": anomaly_id, "detail": "available"}

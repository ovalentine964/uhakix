"""UJUZIO Election Verification API"""
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, Query
from pydantic import BaseModel, Field

router = APIRouter()


class Form34AExtraction(BaseModel):
    """Extracted data from a citizen-uploaded Form 34A photo."""
    station_code: str
    station_name: str
    constituency: str
    county: str
    presidential_votes: dict  # candidate: votes
    registered_voters: int
    votes_cast: int
    rejected_votes: int
    presiding_officer: str
    form_photo_hash: str
    submission_id: str
    verification_status: str = "pending"  # pending → verified → rejected


class PollingStationResult(BaseModel):
    station_code: str
    station_name: str
    constituency: str
    county: str
    presidential_votes: dict
    total_votes_cast: int
    blockchain_hash: Optional[str] = None
    verification_count: int = 0
    status: str = "verified"


class ConstituencyAggregation(BaseModel):
    constituency: str
    county: str
    total_stations: int
    stations_reported: int
    reporting_pct: float
    results: dict  # candidate: total_votes
    last_updated: str


class ElectionAlert(BaseModel):
    alert_type: str  # turnout_anomaly, timing_anomaly, form_mismatch, duplicate
    severity: str  # low, medium, high, critical
    location: str
    description: str
    evidence_sources: int = Field(..., ge=1)
    created_at: str


# ── Submit Form 34A ────────────────────────────────────────


@router.post("/form34a/submit", response_model=Form34AExtraction)
async def submit_form_34a(
    photo: UploadFile = File(
        ...,
        description="Photo of Form 34A (polling station result)",
    ),
    submitter_name: Optional[str] = Form(None, description="Name (optional, for tracking)"),
    station_code: Optional[str] = Form(None, description="Polling station code if known"),
):
    """
    Submit a Form 34A photo for verification.
    No ID required. Name is optional. Station code is optional.

    Pipeline:
    1. POLL WITNESS Agent → OCR + extract data
    2. VERIFY Agent → check authenticity (watermarks, signatures)
    3. COUNT Agent → aggregate with other submissions
    4. LEDGER Agent → hash to blockchain
    5. ALERT Agent → check for anomalies
    """
    return {
        "station_code": station_code or "auto-detected",
        "station_name": "Station Name",
        "constituency": "Constituency",
        "county": "County",
        "presidential_votes": {},
        "registered_voters": 0,
        "votes_cast": 0,
        "rejected_votes": 0,
        "presiding_officer": "TBD by OCR",
        "form_photo_hash": "sha256:hash_of_photo",
        "submission_id": "unique-id",
        "verification_status": "pending",
    }


@router.get("/form34a/{submission_id}")
async def get_submission_status(submission_id: str):
    """Check verification status of a submitted Form 34A."""
    return {"submission_id": submission_id, "status": "in_progress"}


# ── Results ─────────────────────────────────────────────────


@router.get("/results/constituency/{constituency_name}", response_model=ConstituencyAggregation)
async def get_constituency_results(constituency_name: str):
    """Get aggregated results for a constituency."""
    return ConstituencyAggregation(
        constituency=constituency_name,
        county="County",
        total_stations=100,
        stations_reported=50,
        reporting_pct=50.0,
        results={},
        last_updated="2025-01-01T00:00:00Z",
    )


@router.get("/results/county/{county_name}")
async def get_county_results(county_name: str):
    """Get aggregated results for a county."""
    return {"county": county_name, "results": "available"}


@router.get("/results/national")
async def get_national_results():
    """Aggregated national presidential results from all verified Form 34A submissions."""
    return {"national": True, "results": {}, "reporting_stations": 0, "total_stations": 46229}


# ── Alerts ──────────────────────────────────────────────────


@router.get("/alerts", response_model=List[ElectionAlert])
async def get_election_alerts(
    severity: str = Query("all", description="low, medium, high, critical, all"),
    county: Optional[str] = None,
):
    """Real-time election anomaly alerts from ALERT Agent."""
    return []


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    """Full alert details."""
    return {"id": alert_id}


# ── Stations ────────────────────────────────────────────────


@router.get("/stations")
async def search_stations(
    query: str = Query(..., description="Search station name or code"),
    constituency: Optional[str] = None,
    county: Optional[str] = None,
):
    """Search for a polling station."""
    return {"stations": [], "total": 0}


@router.get("/stations/{station_code}/forms")
async def get_station_forms(station_code: str):
    """
    List all Form 34A submissions for this station.
    Multiple citizens can submit — we cross-verify.
    """
    return {"station_code": station_code, "submissions": []}

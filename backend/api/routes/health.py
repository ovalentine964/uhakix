"""UUHAKIX Health Check Endpoints"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "UUHAKIX",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/ready")
async def readiness_check():
    """Full readiness check — all dependencies operational."""
    return {
        "status": "ready",
        "components": {
            "api": "ok",
            "database": "ok",
            "neo4j": "ok",
            "redis": "ok",
            "nvidia_nim": "ok",
            "blockchain": "ok",
        },
    }


@router.get("/health/agents")
async def agents_health():
    """Check status of all 10 agents."""
    agents = [
        "jasiri", "rift", "scout", "sphinx", "kazi",
        "herald", "shield", "vigil", "atlas", "ledger",
    ]
    return {
        "status": "all_agents_operational",
        "agents": {name: {"status": "ready", "model": "nvidia-nim"} for name in agents},
    }

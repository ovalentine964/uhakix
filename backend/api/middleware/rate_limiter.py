"""
UHAKIX Rate Limiting Middleware
Protects against abuse while keeping access free for citizens.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import structlog

logger = structlog.get_logger()

# In production: use Redis for distributed rate limiting
_rate_limit_store: dict = {}


def _get_client_ip(request: Request) -> str:
    return request.client.host


async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting. Production: move to Redis-backed sliding window."""
    client_ip = _get_client_ip(request)
    now = time.time()

    # Skip rate limiting for health checks
    if request.url.path.startswith("/api/v1/health"):
        return await call_next(request)

    key = f"rate:{client_ip}"
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []

    # Clean old entries (last 60 seconds)
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < 60]

    if len(_rate_limit_store[key]) >= 60:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limited",
                "message": "Too many requests. Please wait a moment and try again.",
                "retry_after_seconds": 60,
            },
        )

    _rate_limit_store[key].append(now)
    response = await call_next(request)
    return response

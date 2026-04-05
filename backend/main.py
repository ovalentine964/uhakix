"""
UHAKIX Backend API — Production Entry Point
FastAPI application with middleware, routing, and lifecycle management.
"""

import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from api.middleware.rate_limiter import rate_limit_middleware
from api.middleware.compliance import compliance_middleware
from core.logging import setup_logging
from core.config import settings
from graph.neo4j_driver import Neo4jDriver, CREATE_SCHEMA_QUERIES
from graph.queries import GraphQueries
from services.storage.s3_client import S3Storage
from services.blockchain.service import blockchain_service

import structlog

logger = structlog.get_logger()

# Add backend root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("uhakix_startup", version="1.0.0", env=settings.app_env)
    setup_logging()

    # Initialize Neo4j
    app.state.neo4j = Neo4jDriver(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    try:
        await app.state.neo4j.connect()
        # Initialize schema
        graph_queries = GraphQueries(app.state.neo4j)
        await graph_queries.initialize_schema()
        app.state.graph = graph_queries
        logger.info("neo4j_schema_initialized")
    except Exception as e:
        logger.warning("neo4j_startup_failed", error=str(e), fallback="queries_will_degrade")
        app.state.neo4j = None
        app.state.graph = None

    # Initialize S3 storage
    app.state.storage = S3Storage(
        endpoint_url=settings.s3_endpoint_url,
        bucket=settings.s3_bucket_name,
        access_key=settings.s3_access_key_id,
        secret_key=settings.s3_secret_access_key,
    )

    # Initialize blockchain
    try:
        await blockchain_service.initialize()
        app.state.blockchain = blockchain_service
        logger.info("blockchain_initialized")
    except Exception as e:
        logger.warning("blockchain_startup_failed", error=str(e))
        app.state.blockchain = None

    # Start Celery worker info
    from core.celery_app import celery_app
    logger.info("celery_configured", broker=settings.redis_url)

    logger.info("services_initialized")

    yield

    # Shutdown
    if app.state.neo4j:
        await app.state.neo4j.close()
    logger.info("uhakix_shutdown")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="UHAKIX API",
        description="Kenya's AI-Powered Government Transparency Platform",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware Stack ──────────────────────────────────────
    # GZip compression for large responses
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    # Security headers on ALL responses
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, must-revalidate"
        return response

    # Custom middleware (order: last added runs first on request, first added runs first on response)
    app.middleware("http")(compliance_middleware)
    app.middleware("http")(rate_limit_middleware)

    # ── Routes ────────────────────────────────────────────────
    from api.routes import health, transparency, election, agents, directory, citizen, voice

    app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["Health"])
    app.include_router(transparency.router, prefix=f"{settings.api_v1_prefix}/transparency", tags=["Transparency"])
    app.include_router(election.router, prefix=f"{settings.api_v1_prefix}/election", tags=["Election"])
    app.include_router(agents.router, prefix=f"{settings.api_v1_prefix}/agents", tags=["Agents"])
    app.include_router(directory.router, prefix=f"{settings.api_v1_prefix}/directory", tags=["Entity Directory"])
    app.include_router(citizen.router, prefix=f"{settings.api_v1_prefix}/citizen", tags=["Citizen Access"])
    app.include_router(voice.router, prefix=f"{settings.api_v1_prefix}", tags=["Voice"])

    # ── Error Handlers ────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An internal error occurred. Report reference logged.",
            },
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        logger.warning("permission_denied", path=request.url.path)
        return JSONResponse(
            status_code=403,
            content={"error": "permission_denied", "message": "Access denied."},
        )

    return app


app = create_application()

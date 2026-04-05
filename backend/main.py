"""
UHAKIX Backend API — Production Entry Point
FastAPI application with middleware, routing, and lifecycle management.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from api.middleware.rate_limiter import rate_limit_middleware
from api.middleware.compliance import compliance_middleware
from core.logging import setup_logging
from core.config import settings
from graph.ne4j_driver import Neo4jDriver
from services.storage.s3_client import S3Storage

import structlog

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("uhakix_startup", version="1.0.0", env=settings.app_env)

    # Initialize database connections
    app.state.neo4j = Neo4jDriver(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    await app.state.neo4j.connect()

    app.state.storage = S3Storage(
        endpoint_url=settings.s3_endpoint_url,
        bucket=settings.s3_bucket_name,
        access_key=settings.s3_access_key_id,
        secret_key=settings.s3_secret_access_key,
    )

    # Start background workers (Celery)
    from core.celery_app import celery_app

    logger.info("services_initialized")

    yield

    # Shutdown
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    # Custom middleware (order matters — last added runs first)
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(compliance_middleware)

    # ── Routes ────────────────────────────────────────────────
    from api.routes import health, transparency, election, agents, directory, citizen

    app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["Health"])
    app.include_router(transparency.router, prefix=settings.api_v1_prefix, tags=["Transparency"])
    app.include_router(election.router, prefix=f"{settings.api_v1_prefix}/election", tags=["Election"])
    app.include_router(agents.router, prefix=f"{settings.api_v1_prefix}/agents", tags=["Agents"])
    app.include_router(directory.router, prefix=f"{settings.api_v1_prefix}/directory", tags=["Entity Directory"])
    app.include_router(citizen.router, prefix=f"{settings.api_v1_prefix}/citizen", tags=["Citizen Access"])

    # ── Error Handlers ────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An internal error occurred. Report reference logged.",
            },
        )

    return app


app = create_application()

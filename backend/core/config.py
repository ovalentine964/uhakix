"""
UUHAKIX Configuration — Pydantic Settings with .env support
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────
    app_name: str = "UUHAKIX"
    app_env: str = "production"
    app_debug: bool = False
    secret_key: str = "change-me"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ── Database ──────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://uuhakix:uuhakix@postgres:5432/uuhakix"

    # ── Redis ─────────────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"
    redis_cache_url: str = "redis://redis:6379/2"

    # ── Neo4j ─────────────────────────────────────────────
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_password_secure"

    # ── NVIDIA NIM ────────────────────────────────────────
    nvidia_api_key: str = ""
    nvidia_nemotron_4_340b: str = "nvidia/nemotron-4-340b-instruct"
    nvidia_llama_3_1_70b: str = "meta/llama-3.1-70b-instruct"
    nvidia_llama_3_1_8b: str = "meta/llama-3.1-8b-instruct"
    nvidia_phi_3_mini: str = "microsoft/phi-3-mini-128k-instruct"
    nvidia_llama_3_2_vision: str = "nvidia/llama-3.2-90b-vision-instruct"

    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"

    # ── Blockchain ────────────────────────────────────────
    blockchain_private_key: str = ""
    polygon_rpc_url: str = "https://rpc-amoy.polygon.technology"
    contract_address: str = ""
    blockchain_network: str = "polygon-amoy"
    hash_batch_threshold: int = 50

    # ── Storage ───────────────────────────────────────────
    s3_endpoint_url: str = ""
    s3_bucket_name: str = "uuhakix-media"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

    # ── Rate Limiting ────────────────────────────────────
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # ── Election Config ──────────────────────────────────
    election_verification_min_sources: int = 3
    alert_anomaly_threshold_stddev: float = 3.0
    form_34a_max_file_size_mb: int = 10

    # ── Logging ──────────────────────────────────────────
    log_level: str = "INFO"
    sentry_dsn: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

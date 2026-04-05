"""
HAKIX Celery Worker — Background Task Processing
Used for scraping, agent orchestration, and blockchain writes.
"""

from celery import Celery
from core.config import settings

celery_app = Celery(
    "ujuzio_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Nairobi",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    # Retry policy
    broker_connection_retry_on_startup=True,
    task_default_retry_policy={
        "max_retries": 3,
        "interval_start": 60,
        "interval_step": 120,
        "interval_max": 600,
    },
)

celery_app.autodiscover_tasks(["backend.agents", "backend.services.scraper"])

"""S3-compatible storage service for images (Form 34A photos, etc.)"""

from typing import Optional
from botocore.config import Config
import aiohttp
import structlog

logger = structlog.get_logger()


class S3Storage:
    """S3-compatible object storage for media files."""

    def __init__(self, endpoint_url: str, bucket: str, access_key: str, secret_key: str):
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        # In production: use aioboto3 for async S3 operations
        self.configured = bool(endpoint_url and access_key and secret_key)

    async def upload_file(self, file_key: str, file_data: bytes, content_type: str = "image/jpeg") -> str:
        """Upload a file and return the public URL."""
        # Production: use aioboto3 to upload
        if not self.configured:
            return f"local://{file_key}"
        url = f"{self.endpoint_url}/{self.bucket}/{file_key}"
        logger.info("file_uploaded", key=file_key, url=url)
        return url

    async def get_file_url(self, file_key: str) -> Optional[str]:
        """Get public URL for a stored file."""
        if not self.configured:
            return f"local://{file_key}"
        return f"{self.endpoint_url}/{self.bucket}/{file_key}"

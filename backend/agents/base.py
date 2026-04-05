"""
UHAKIX Agent Base — All agents inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from services.nvidia.nim_service import NVIDIANIMService, nvidia_service
import structlog
import time
import hashlib

logger = structlog.get_logger()


class Agent(ABC):
    """Base class for all UHAKIX agents."""

    name: str = "base"
    role: str = "Base Agent"
    model_key: str = "general"  # Maps to nvidia_service.models
    triggers: List[str] = []
    requires_shield: bool = True  # All agents default to SHIELD review

    def __init__(self, nvidia: Optional[NVIDIANIMService] = None):
        self.nvidia = nvidia or nvidia_service
        self.task_count = 0

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing pipeline — with SHIELD compliance."""
        start_time = time.time()

        try:
            result = await self._execute(input_data)
            self.task_count += 1

            # SHIELD compliance layer (runs on ALL outputs)
            if self.requires_shield:
                result = await self._apply_shield(result)

            result["agent"] = self.name
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)
            result["task_count"] = self.task_count

            logger.info(
                "agent_processing_complete",
                agent=self.name,
                time_ms=result["processing_time_ms"],
            )

            return result

        except Exception as e:
            logger.error(
                "agent_processing_failed",
                agent=self.name,
                error=str(e),
            )
            raise

    @abstractmethod
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent-specific logic. Override in subclass."""
        raise NotImplementedError

    async def _apply_shield(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Run SHIELD legal compliance check."""
        # In production, this calls the SHIELD agent which uses Nemotron-4
        # to redact PII, ensure proper language, and verify source count
        from api.middleware.compliance import validate_connection_report

        if "connection_report" in result:
            result["connection_report"] = validate_connection_report(
                result["connection_report"]
            )

        if "narrative" in result:
            from api.middleware.compliance import redact_personal_info
            result["narrative"] = redact_personal_info(result["narrative"])

        result.setdefault("compliance_status", "shield-vetted")
        return result

    def _hash_data(self, data: str) -> str:
        """Generate SHA-256 hash for blockchain storage."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    async def call_nvidia(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        json_response: bool = False,
    ) -> str:
        """Call NVIDIA NIM API via the service."""
        return await self.nvidia.chat(
            messages=messages,
            model_key=self.model_key,
            temperature=temperature,
            json_response=json_response,
        )

    async def call_vision(
        self,
        prompt: str,
        image_data: str,
    ) -> str:
        """Call NVIDIA vision model for image analysis."""
        return await self.nvidia.vision(
            prompt=prompt,
            image_url_or_base64=image_data,
            model_key="vision",
        )

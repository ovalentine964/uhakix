"""
NVIDIA NIM Service — AI Model Interface
All AI inference goes through NVIDIA's API, never OpenAI or Anthropic.
"""

from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from core.config import settings
import base64
import structlog

logger = structlog.get_logger()


class NVIDIANIMService:
    """Interface to NVIDIA NIM API endpoints."""

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.nvidia_api_key,
        )

        # Model mappings for each agent
        self.models = {
            "complex": settings.nvidia_nemotron_4_340b,        # Nemotron-4 — analysis
            "general": settings.nvidia_llama_3_1_70b,           # Llama 3.1 70B
            "lightweight": settings.nvidia_llama_3_1_8b,        # Llama 3.1 8B
            "edge": settings.nvidia_phi_3_mini,                  # Phi-3 mini
            "vision": settings.nvidia_llama_3_2_vision,          # Llama 3.2 Vision
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_key: str = "general",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        json_response: bool = False,
    ) -> str:
        """Text-based chat completion."""
        model = self.models.get(model_key, self.models["general"])

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.7,
        }

        if json_response:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)

        logger.info(
            "nvidia_chat_complete",
            model=model,
            tokens_used=response.usage.total_tokens if response.usage else 0,
        )

        return response.choices[0].message.content

    async def vision(
        self,
        prompt: str,
        image_url_or_base64: str,
        model_key: str = "vision",
        max_tokens: int = 4096,
    ) -> str:
        """Vision model — used for Form 34A OCR and analysis."""
        model = self.models.get(model_key, self.models["vision"])

        # If it's a file path or raw bytes, convert to base64 data URI
        if image_url_or_base64.startswith(("http://", "https://")):
            image_content = {"type": "image_url", "image_url": {"url": image_url_or_base64}}
        else:
            # Assume base64 encoded
            image_content = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_url_or_base64}"},
            }

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    image_content,
                ],
            }
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,  # Low temp for OCR — deterministic
            max_tokens=max_tokens,
        )

        logger.info("nvidia_vision_complete", model=model)
        return response.choices[0].message.content

    @property
    def model_info(self) -> Dict[str, str]:
        return {agent: model for agent, model in self.models.items()}


# Singleton
nvidia_service = NVIDIANIMService()

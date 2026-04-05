"""
UHAKIX Text-to-Speech — MMS-TTS for Audio Response Generation
Supports Swahili (swh), English (eng), and 1100+ languages.
Fully open-source — no external API.
"""

from typing import Optional
import structlog
import io
import os

logger = structlog.get_logger()

TRANSFORMERS_AVAILABLE = False
TORCH_AVAILABLE = False
try:
    import torch
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("tts_transformers_missing", message="TTS requires: pip install transformers torch soundfile")


# MMS-TTS language codes for supported Kenyan languages
MMS_LANGUAGE_MAP = {
    "sw": "swh",       # Swahili
    "swa": "swh",
    "swh": "swh",
    "en": "eng",       # English
    "eng": "eng",
    "luo": "luo",      # Dholuo (Luo)
    "kik": "kik",      # Kikuyu
    "kam": "kam",      # Kamba
    "luy": "luy",      # Luhya
    "mas": "mas",      # Maasai
    "mer": "mer",      # Kimîîru
}


class UHAKIXTextToSpeech:
    """
    Text-to-Speech engine using Facebook MMS-TTS.
    
    Features:
    - 1107 languages including Swahili, Dholuo, Kikuyu
    - Natural-sounding voice
    - WAV output format
    - Suitable for WhatsApp audio, Telegram, USSD, web playback
    """

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or os.getenv("VOICE_TTS_MODEL", "facebook/mms-tts")
        self._synthesizer = None
        self._device = self._detect_device()

        logger.info("tts_initialized", device=self._device, model=self.model_id)

    def _detect_device(self) -> int:
        """Return device index: 0 for CUDA, -1 for CPU."""
        if TORCH_AVAILABLE and torch.cuda.is_available():
            return 0
        return -1

    def _load_model(self):
        """Lazy-load the TTS model."""
        if self._synthesizer is not None:
            return

        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError(
                "Transformers not installed. Run: pip install transformers torch soundfile"
            )

        self._synthesizer = pipeline(
            "text-to-speech",
            model=self.model_id,
            device=self._device,
        )

        logger.info("tts_model_loaded", device=self._device)

    async def synthesize(
        self,
        text: str,
        language: str = "sw",
        max_length: int = 500,
    ) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to synthesize
            language: Language code (sw, en, luo, kik, etc.)
            max_length: Maximum text length to process

        Returns:
            WAV audio bytes
        """
        self._load_model()

        import soundfile as sf

        # Truncate if too long for synthesis
        text = text[:max_length]

        # Map language code to MMS format
        mms_lang = MMS_LANGUAGE_MAP.get(language.lower(), "swh")

        # Synthesize
        output = self._synthesizer(text, forward_params={"language": mms_lang})

        audio_data = output["audio"]
        sample_rate = output["sampling_rate"]

        # Convert to WAV bytes
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_data, samplerate=sample_rate, format="WAV")
        wav_buffer.seek(0)

        wav_bytes = wav_buffer.read()

        logger.info(
            "tts_synthesized",
            text_length=len(text),
            language=language,
            audio_size_bytes=len(wav_bytes),
        )

        return wav_bytes

    async def synthesize_to_file(
        self,
        text: str,
        file_path: str,
        language: str = "sw",
    ) -> str:
        """Synthesize text and save to WAV file."""
        wav_bytes = await self.synthesize(text, language)

        with open(file_path, "wb") as f:
            f.write(wav_bytes)

        return file_path

    async def synthesize_ogg(
        self,
        text: str,
        language: str = "sw",
    ) -> bytes:
        """
        Synthesize to OGG Opus format (for Telegram/WhatsApp).
        Requires additional encoding.
        """
        wav_bytes = await self.synthesize(text, language)
        # For full OGG conversion, use pydub or ffmpeg
        # Return WAV as fallback (WhatsApp/Telegram both accept WAV)
        return wav_bytes


# Singleton
_tts_instance = None


def get_tts_service() -> UHAKIXTextToSpeech:
    """Get or create the TTS singleton."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = UHAKIXTextToSpeech()
    return _tts_instance

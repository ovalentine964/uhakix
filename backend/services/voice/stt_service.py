"""
UHAKIX Speech-to-Text — Whisper large-v3 for Voice Transcription
Supports Swahili, English, Sheng, and code-switching.
Used for WhatsApp voice notes, Telegram audio, USSD audio, and web recordings.
Runs fully open-source — no external API dependency.
"""

from typing import Optional
import structlog
import os

logger = structlog.get_logger()

TRANSFORMERS_AVAILABLE = False
TORCH_AVAILABLE = False
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

    TRANSFORMERS_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("transformers_not_installed", message="Voice STT requires: pip install transformers torch soundfile")


class UHAKIXSpeechToText:
    """
    Speech-to-Text engine using OpenAI Whisper large-v3.
    
    Supports:
    - Swahili (sw) — primary language for Kenyan citizens
    - English (en) — official language
    - Sheng detection and normalization
    - Code-switching between languages
    - WhatsApp/WebM, Telegram/OGG, WAV, MP3 audio formats
    """

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or os.getenv("VOICE_STT_MODEL", "openai/whisper-large-v3")
        self._model = None
        self._processor = None
        self._pipe = None
        self._device = self._detect_device()

        self._sheng_glossary = self._load_sheng_glossary()
        logger.info("stt_initialized", device=self._device, model=self.model_id)

    def _detect_device(self) -> str:
        """Detect available compute device."""
        if TORCH_AVAILABLE and torch.cuda.is_available():
            return "cuda:0"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load_model(self):
        """Lazy-load the Whisper model (expensive operation)."""
        if self._model is not None:
            return

        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError(
                "Transformers not installed. Run: pip install transformers torch soundfile"
            )

        dtype = torch.float16 if self._device.startswith("cuda") else torch.float32
        torch_dtype = torch.float16 if self._device.startswith("cuda") else torch.float32

        self._model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
        ).to(self._device)

        self._processor = AutoProcessor.from_pretrained(self.model_id)

        self._pipe = pipeline(
            "automatic-speech-recognition",
            model=self._model,
            tokenizer=self._processor.tokenizer,
            feature_extractor=self._processor.feature_extractor,
            max_new_tokens=448,
            chunk_length_s=30,  # Process in 30s chunks for long audio
            batch_size=8 if self._device.startswith("cuda") else 1,
            return_timestamps=True,
            device=self._device,
        )

        logger.info("stt_model_loaded", device=self._device)

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> dict:
        """
        Transcribe voice audio to text.

        Args:
            audio_bytes: Raw audio bytes (WAV, MP3, OGG, WebM)
            language: "sw" (Swahili), "en" (English), or None for auto-detect
            task: "transcribe" or "translate" (translate non-English to English)

        Returns:
            dict with text, language, confidence, sheng detection
        """
        self._load_model()

        import io
        import soundfile as sf
        import numpy as np

        # Load audio and resample to 16kHz mono (Whisper standard)
        audio_array, sr = sf.read(io.BytesIO(audio_bytes))

        # Convert stereo to mono
        if audio_array.ndim > 1:
            audio_array = np.mean(audio_array, axis=1)

        # Resample to 16kHz if needed
        if sr != 16000:
            import librosa
            audio_array = librosa.resample(audio_array, orig_sr=sr, target_sr=16000)

        # Use pipeline for transcription
        generate_kwargs = {
            "task": task,
        }
        if language and language in ("sw", "en"):
            generate_kwargs["language"] = language

        result = self._pipe(
            {"raw": audio_array, "sampling_rate": 16000},
            generate_kwargs=generate_kwargs,
        )

        transcription = result.get("text", "").strip()

        # Detect language if not specified
        detected_lang = language or self._detect_language(transcription)

        # Sheng normalization
        sheng_detected = self._detect_sheng(transcription)
        normalized = self._normalize_sheng(transcription) if sheng_detected else transcription

        return {
            "text": transcription,
            "normalized_text": normalized,
            "language": detected_lang,
            "sheng_detected": sheng_detected,
            "confidence": result.get("chunks", [{}])[0].get("confidence", 0.95),
            "task": task,
            "model_used": self.model_id,
        }

    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """Transcribe an audio file from disk."""
        import soundfile as sf

        audio_array, sr = sf.read(file_path)
        if audio_array.ndim > 1:
            import numpy as np
            audio_array = np.mean(audio_array, axis=1)

        audio_bytes = io.BytesIO()
        sf.write(audio_bytes, audio_array, sr, format="WAV")
        audio_bytes.seek(0)

        return await self.transcribe(audio_bytes.read(), language=language)

    def _detect_language(self, text: str) -> str:
        """Heuristic language detection for the transcription."""
        swahili_markers = [
            "ni", "na", "ya", "la", "wa", "za", "hii", "huyo", "sasa",
            "kweli", "mbona", "pole", "asante", "habari", "sijui",
        ]
        english_markers = [
            "the", "is", "are", "was", "were", "have", "has", "this",
            "what", "why", "where", "when", "who", "how",
        ]

        words = text.lower().split()
        if not words:
            return "sw"  # Default Swahili

        sw_count = sum(1 for w in words if w in swahili_markers)
        en_count = sum(1 for w in words if w in english_markers)

        if sw_count > en_count:
            return "sw"
        elif en_count > sw_count:
            return "en"
        else:
            return "sw"  # Default

    def _load_sheng_glossary(self) -> dict:
        """Load Sheng glossary from CSV file."""
        glossary_path = os.getenv(
            "VOICE_SHENG_GLOSSARY_PATH",
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "sheng-glossary.csv"),
        )
        sheng_map = {}
        if os.path.exists(glossary_path):
            with open(glossary_path, "r") as f:
                import csv
                reader = csv.DictReader(f)
                for row in reader:
                    sheng_map[row["sheng"].lower()] = row["standard_english"].lower()
        else:
            # Inline fallback glossary
            sheng_map = {
                "sana": "very/common",
                "ni": "is/are",
                "sijui": "I don't know",
                "form": "situation/status",
                "manze": "wow/seriously",
                "buda": "man/dude",
                "pesa": "money/funds",
                "mbona": "why",
                "sasa": "now/what",
                "hii": "this",
                "wapi": "where",
                "je": "question marker",
                "nipe": "give me",
                "sema": "say/tell",
                "kweli": "truth/really",
                "niambie": "tell me",
                "polepole": "slowly",
                "haraka": "quickly",
                "hapa": "here",
                "pale": "there",
                "wale": "those people",
                "mimi": "I/me",
                "wewe": "you",
                "sisi": "we/us",
            }
        return sheng_map

    def _normalize_sheng(self, text: str) -> str:
        """Convert common Sheng terms to standard Swahili/English."""
        result = text
        for sheng, standard in self._sheng_glossary.items():
            result = result.replace(sheng, standard)
        return result

    def _detect_sheng(self, text: str) -> bool:
        """Detect if input contains Sheng terms."""
        sheng_indicators = list(self._sheng_glossary.keys())
        text_lower = text.lower()
        return any(term in text_lower for term in sheng_indicators)


# Singleton
_stt_instance = None


def get_stt_service() -> UHAKIXSpeechToText:
    """Get or create the STT singleton."""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = UHAKIXSpeechToText()
    return _stt_instance

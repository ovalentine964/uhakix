"""
UHAKIX Voice API — Speech-to-Text and Text-to-Speech Endpoints
Citizens can upload voice notes and receive audio responses.
Supports Swahili, English, Sheng, and code-switching.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
import structlog

from services.voice.stt_service import get_stt_service, UHAKIXSpeechToText
from services.voice.tts_service import get_tts_service, UHAKIXTextToSpeech

logger = structlog.get_logger()
router = APIRouter(prefix="/voice", tags=["voice"])

# Lazy-loaded singletons
_stt = None
_tts = None


def get_stt() -> UHAKIXSpeechToText:
    global _stt
    if _stt is None:
        _stt = get_stt_service()
    return _stt


def get_tts() -> UHAKIXTextToSpeech:
    global _tts
    if _tts is None:
        _tts = get_tts_service()
    return _tts


ALLOWED_AUDIO_TYPES = {
    "audio/wav",
    "audio/mpeg",
    "audio/ogg",
    "audio/webm",
    "audio/mp4",
    "audio/x-m4a",
    "audio/flac",
    "audio/amr",
    "audio/opus",
}

MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(..., description="Voice note (WAV, MP3, OGG, WebM)"),
    language: str = Form(None, description="Language hint: sw, en, or auto"),
):
    """
    Citizen uploads voice note → returns transcribed text.
    Supports WhatsApp voice notes, Telegram audio, web recordings.
    Automatically detects and normalizes Sheng terms.
    """
    # Validate file type
    content_type = audio.content_type or ""
    if content_type and content_type not in ALLOWED_AUDIO_TYPES:
        # Allow common audio types even if content-type is misreported
        if not content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio type: {content_type}. Accepted: WAV, MP3, OGG, WebM"
            )

    # Read audio (size check)
    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Audio too large: {len(audio_bytes)} bytes. Max: {MAX_AUDIO_SIZE} bytes."
        )
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file.")

    try:
        stt = get_stt()
        result = await stt.transcribe(audio_bytes, language=language)

        logger.info(
            "voice_transcribed",
            text_length=len(result["text"]),
            language=result["language"],
            sheng_detected=result["sheng_detected"],
        )

        return {
            "status": "success",
            "text": result["text"],
            "normalized_text": result["normalized_text"],
            "language": result["language"],
            "sheng_detected": result["sheng_detected"],
            "confidence": result["confidence"],
            "message": "Voice transcribed successfully. You can now ask UHAKIX questions.",
        }

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Voice service unavailable: {e}",
        )
    except Exception as e:
        logger.error("voice_transcription_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Voice transcription failed. Please try again or type your question."
        )


@router.post("/speak")
async def text_to_speech(
    text: str = Form(..., description="Text to convert to speech"),
    language: str = Form("sw", description="Language: sw (Swahili), en (English)"),
):
    """
    Convert text to audio response.
    Returns WAV audio bytes for playback in web/mobile clients.
    """
    if not text or len(text.strip()) < 2:
        raise HTTPException(status_code=400, detail="Text is too short.")
    if len(text) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Text too long. Maximum 5000 characters. Please shorten your request."
        )

    try:
        tts = get_tts()
        audio_bytes = await tts.synthesize(text, language=language)

        from fastapi.responses import Response
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "X-UHAKIX-Language": language,
                "Content-Disposition": 'inline; filename="uhakix_response.wav"',
            },
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Voice synthesis service unavailable: {e}",
        )
    except Exception as e:
        logger.error("voice_synthesis_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Speech synthesis failed. Here's the text response instead."
        )


@router.get("/languages")
async def list_supported_languages():
    """List all supported languages for voice operations."""
    return {
        "transcription_languages": ["sw (Swahili)", "en (English)", "auto-detect"],
        "synthesis_languages": [
            "sw/swh — Swahili",
            "en/eng — English",
            "luo — Dholuo",
            "kik — Kikuyu",
            "kam — Kamba",
            "luy — Luhya",
            "mas — Maasai",
            "mer — Kimîîru",
        ],
        "sheng_support": True,
        "supported_formats": list(ALLOWED_AUDIO_TYPES),
        "max_audio_size_mb": MAX_AUDIO_SIZE // (1024 * 1024),
    }

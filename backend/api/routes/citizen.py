"""
UHAKIX Citizen Access API — WhatsApp, USSD, Voice, Telegram, and Web Interactions
Integrated with Voice STT/TTS, Civic Education, and transparency engines.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException, Query
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()
router = APIRouter()

# Lazy-load services to avoid import errors if models aren't installed
_stt_instance = None
_tts_instance = None
_civic_edu_instance = None


def _get_stt():
    global _stt_instance
    if _stt_instance is None:
        from services.voice.stt_service import get_stt_service
        _stt_instance = get_stt_service()
    return _stt_instance


def _get_tts():
    global _tts_instance
    if _tts_instance is None:
        from services.voice.tts_service import get_tts_service
        _tts_instance = get_tts_service()
    return _tts_instance


def _get_civic_edu():
    global _civic_edu_instance
    if _civic_edu_instance is None:
        from services.civic_education.knowledge_base import get_civic_education
        _civic_edu_instance = get_civic_education()
    return _civic_edu_instance


class CitizenQuestion(BaseModel):
    """Citizen query for UHAKIX."""
    question: str = Field(..., min_length=2, max_length=5000, description="Question in any language (EN, SW, Sheng)")
    language: str = Field(default="sw", description="Language preference: sw, en, mixed")
    channel: str = Field(default="web", description="Source channel: web, whatsapp, ussd, telegram, api")


class CitizenResponse(BaseModel):
    """UHAKIX response to citizen."""
    status: str = Field(default="success")
    answer_narrative: str = Field(description="Human-readable answer")
    civic_education: Optional[dict] = Field(None, description="Civic education reference if applicable")
    transparency_data: Optional[dict] = Field(None, description="Supporting data if available")
    language: str = Field(description="Response language")
    audio_response_available: bool = Field(default=True)
    follow_up_suggestions: list = Field(default_factory=list)


@router.post("/ask", response_model=CitizenResponse)
async def citizen_ask(request: CitizenQuestion):
    """
    Ask UHAKIX anything about government spending, Constitutional rights,
    candidate accountability, or political manipulation detection.

    Supports: English, Kiswahili, Sheng (auto-detected).
    """
    # Step 1: Civic Education check (high priority — protects citizens)
    civic_response = await _get_civic_edu().answer_civic_question(
        request.question, language=request.language
    )

    # Step 2: Transparency engine check
    transparency_response = _route_transparency_query(request.question)

    # Step 3: Build combined response
    answer_narrative = civic_response.get(
        "answer",
        "Thank you for your question. UHAKIX helps you track government spending and understand your rights."
    )

    # Append transparency data if found
    if transparency_response.get("found"):
        answer_narrative += f"\n\nData found: {transparency_response.get('summary', '')}"

    # Build follow-up suggestions
    follow_ups = civic_response.get("actionable_steps", [])
    if "suggested_queries" in (transparency_response or {}):
        follow_ups.extend(transparency_response.get("suggested_queries", []))

    return CitizenResponse(
        status="success",
        answer_narrative=answer_narrative,
        civic_education=civic_response,
        transparency_data=transparency_response,
        language=request.language,
        audio_response_available=True,
        follow_up_suggestions=follow_ups[:5],
    )


@router.post("/ask-voice")
async def citizen_ask_voice(
    audio: UploadFile = File(None, description="Voice question (WAV, MP3, OGG, WebM)"),
    question: str = Form(None, description="Text question (fallback if no audio)"),
    language: str = Form("sw", description="Language preference"),
):
    """
    Ask UHAKIX via voice note or text.
    If audio is provided, it's transcribed first, then processed.
    Returns both text answer and audio response.
    """
    # Step 1: Transcribe voice if provided
    if audio:
        try:
            audio_bytes = await audio.read()
            stt = _get_stt()
            transcription = await stt.transcribe(audio_bytes, language=language)
            question = transcription.get("normalized_text", transcription.get("text", question))
            logger.info("citizen_voice_question", text=question[:100])
        except Exception as e:
            logger.error("voice_transcribe_failed_in_ask", error=str(e))
            if not question:
                raise HTTPException(
                    status_code=400,
                    detail="Voice transcription failed and no text question provided."
                )

    if not question or len(question.strip()) < 2:
        raise HTTPException(status_code=400, detail="No question provided.")

    # Step 2: Process as citizen question
    civic_response = await _get_civic_edu().answer_civic_question(question, language=language)
    transparency_response = _route_transparency_query(question)

    answer = civic_response.get("answer", "Thank you for your question.")

    # Step 3: Generate audio response
    audio_base64 = None
    try:
        tts = _get_tts()
        audio_bytes = await tts.synthesize(answer, language=language)
        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        logger.warning("tts_failed_in_ask_voice", error=str(e))

    return {
        "status": "success",
        "text": answer,
        "civic_education": civic_response,
        "transparency_data": transparency_response,
        "language": language,
        "audio_base64": audio_base64,
    }


def _route_transparency_query(question: str) -> Dict[str, Any]:
    """
    Quick routing of transparency queries.
    In production, this connects to Neo4j and the agent pipeline.
    """
    q = question.lower()

    if any(t in q for t in ["spend", "spent", "spending", "matumizi", "budget", "bajeti"]):
        return {
            "found": True,
            "category": "spending",
            "summary": "Use the transparency dashboard at /api/v1/transparency/transactions to search government spending by ministry, county, or vendor.",
            "endpoint": "/api/v1/transparency/transactions",
        }

    if any(t in q for t in ["tender", "contract", "procurement", "mkataba"]):
        return {
            "found": True,
            "category": "procurement",
            "summary": "Search government tenders at /api/v1/transparency/tenders to find procurement records, awarded contracts, and vendor information.",
            "endpoint": "/api/v1/transparency/tenders",
        }

    if any(t in q for t in ["company", "voting", "business", "registered"]):
        return {
            "found": True,
            "category": "entity",
            "summary": "Search companies, people, and connections at /api/v1/directory/search to find entities, their tenders, and relationship networks.",
            "endpoint": "/api/v1/directory/search",
        }

    if any(t in q for t in ["election", "vote", "form 34a", "results", "matokeo"]):
        return {
            "found": True,
            "category": "election",
            "summary": "View election results and submit Form 34A for verification at /api/v1/election/. We cross-verify citizen uploads with official data.",
            "endpoint": "/api/v1/election/results/national",
        }

    return {"found": False}


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    WhatsApp webhook — receives messages, voice notes, and photo uploads
    from citizens via WhatsApp Business API.

    Supported message types: text, voice, image (Form 34A), document
    """
    body = await request.json()

    # Extract message type from WhatsApp webhook payload
    entry = body.get("entry", [])
    if not entry:
        return {"status": "received"}

    value = entry[0].get("changes", [{}])[0].get("value", {})
    messages = value.get("messages", [])
    if not messages:
        return {"status": "received"}

    msg = messages[0]
    msg_type = msg.get("type", "text")
    phone = msg.get("from", "")

    logger.info("whatsapp_message_received", phone=phone, type=msg_type)

    # Route by message type
    if msg_type == "text":
        question = msg.get("text", {}).get("body", "")
        return await _process_citizen_query(question, phone, "whatsapp")

    elif msg_type == "voice":
        # Handle voice note
        voice_id = msg.get("voice", {}).get("id", "")
        return await _process_voice_note(voice_id, phone)

    elif msg_type == "image":
        # Handle Form 34A photo upload
        image_id = msg.get("image", {}).get("id", "")
        caption = msg.get("image", {}).get("caption", "")
        return await _process_form_34a(image_id, caption, phone)

    return {"status": "received", "type": msg_type}


@router.post("/ussd/callback")
async def ussd_callback(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
):
    """
    USSD callback from Africa's Talking.
    Menu-driven interface for feature phone citizens.
    No internet required.

    USSD Menu Flow:
    1 → Search Government Spending
    2 → Election Results  
    3 → Report Form 34A (get upload link via SMS)
    4 → My County Budget
    5 → Know Your Rights (Civic Education)
    0 → Back
    """
    menu_text = (
        "Karibu UHAKIX!\n\n"
        "1. Tafuta Matumizi ya Serikali\n"
        "2. Matokeo ya Uchaguzi\n"
        "3. Ripoti Form 34A\n"
        "4. Bajeti ya Kaunti Yangu\n"
        "5. Jua Haki Zako\n\n"
        "Jibu:"
    )

    if text == "":
        response = f"CON {menu_text}"

    elif text == "1" or text.startswith("1*"):
        sub = text.replace("1", "").strip("*")
        if sub == "":
            response = "CON Tafuta:\n1. Wizara\n2. Kaunti\n3. Mkandarasi\n9. Nyuma"
        elif sub.startswith("1"):
            response = "CON Ingiza jina la wizara:"
        elif sub.startswith("2"):
            response = "CON Ingiza jina la kaunti:"
        elif sub.startswith("3"):
            response = "CON Ingiza jina la mkandarasi:"
        else:
            response = f"END Tafadhali tumia UHAKIX web uhakix.ke kwa data kamili au piga simu *247#"
    elif text.startswith("2"):
        response = "CON Ingiza Jina la Eneo/Kaunti:"
    elif text.startswith("3"):
        response = "END Tafadhali tuma picha ya Form 34A kupitia WhatsApp: +254-XXX-XXXX"
    elif text.startswith("4"):
        response = "CON Ingiza jina la kaunti yako:"
    elif text.startswith("5"):
        sub = text.replace("5", "").strip("*")
        if sub == "":
            response = "CON Haki Zako:\n1. Haki ya Kujua\n2. Haki ya Afya\n3. Haki ya Elimu\n4. Ushiriki wa Bajeti\n9. Nyuma"
        elif sub.startswith("1"):
            response = "END Kif 35 - Kila raia ana haki ya kupata habari iliyo na Serikali. UHAKIX inakusaidia kupata habari hii bure."
        elif sub.startswith("2"):
            response = "END Kif 43(1)(a) - Kila mtu ana haki ya afya bora. Angalia bajeti ya afya ya kaunti yako kwenye uhakix.ke"
        elif sub.startswith("3"):
            response = "END Kif 43(1)(b) - Kila mtu ana haki ya kupata elimu. Bonyeza www.uhakix.ke kuangalia fedha za elimu."
        elif sub.startswith("4"):
            response = "END Kif 201 - Fedha za umma zinapaswa kuwa wazi na na uwajibikaji. Ushiriki wa umma ni lahimu."
        else:
            response = f"CON {menu_text}"
    else:
        response = f"END Asante kwa kutumia UHAKIX!\nTembelea www.uhakix.ke kwa data zaidi."

    return response


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram webhook — handles text, voice, photo, and document messages.
    Citizens can interact with UHAKIX through a Telegram bot.
    """
    body = await request.json()

    message = body.get("message", {})
    if not message:
        return {"status": "ok"}

    chat_id = message.get("chat", {}).get("id", "")
    msg_text = message.get("text", "")
    
    # Handle different message types
    if message.get("voice"):
        # Voice note — transcribe via Telegram file API
        file_id = message["voice"]["file_id"]
        return _handle_telegram_voice(chat_id, file_id)

    elif message.get("photo"):
        # Photo — could be Form 34A
        photo_id = message["photo"][-1]["file_id"]  # Best resolution
        caption = message.get("caption", "")
        return _handle_telegram_photo(chat_id, photo_id, caption)

    elif message.get("document"):
        # Document upload
        doc_id = message["document"]["file_id"]
        return {"status": "received", "type": "document"}

    elif msg_text:
        # Text message — process as citizen question
        return await _process_citizen_query(msg_text, chat_id, "telegram")

    return {"status": "ok"}


async def _process_citizen_query(question: str, sender_id: str, channel: str) -> dict:
    """Process a citizen's text question and prepare response."""
    civic_response = await _get_civic_edu().answer_civic_question(question)
    transparency = _route_transparency_query(question)

    answer = civic_response.get("answer", "Asante kwa swali lako.")
    if transparency.get("summary"):
        answer += f"\n\n{transparency['summary']}"

    return {
        "status": "success",
        "answer": answer,
        "answer_text": answer,
        "type": "text",
        "civic_education": civic_response,
    }


async def _process_voice_note(voice_id: str, phone: str) -> dict:
    """Process a WhatsApp voice note."""
    # In production: download from WhatsApp Media API, transcribe with Whisper
    return {
        "status": "processing",
        "message": "Voice note received. Processing transcription...",
        "type": "voice",
    }


async def _process_form_34a(image_id: str, caption: str, phone: str) -> dict:
    """Process a WhatsApp Form 34A photo."""
    # In production: download from WhatsApp Media API, run POLL_WITNESS + VERIFY
    return {
        "status": "processing",
        "message": "Form 34A photo received. Starting verification pipeline...",
        "type": "image",
    }


def _handle_telegram_voice(chat_id: str, file_id: str) -> dict:
    """Route Telegram voice note to STT service."""
    return {
        "status": "processing",
        "message": "Voice note received. Transcribing...",
        "type": "voice",
    }


def _handle_telegram_photo(chat_id: str, photo_id: str, caption: str) -> dict:
    """Route Telegram photo to Form 34A pipeline or general image analysis."""
    return {
        "status": "processing",
        "message": "Photo received. Analyzing...",
        "type": "photo",
    }


@router.get("/report/{report_id}")
async def get_report_status(report_id: str):
    """Check status of a citizen-submitted report or query."""
    return {"report_id": report_id, "status": "processing"}

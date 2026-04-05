"""UHAKIX Citizen Access API — WhatsApp, USSD, and citizen interactions"""
from fastapi import APIRouter, Request, Form
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class CitizenQuestion(BaseModel):
    question: str
    language: str = "sw"  # sw=Swahili, en=English, mix=Swahili-English mix
    channel: str = "web"  # web, whatsapp, ussd, api


class CitizenResponse(BaseModel):
    answer: str
    language: str
    sources_cited: int
    agent_used: str
    follow_up_suggestions: list


@router.post("/ask", response_model=CitizenResponse)
async def citizen_ask(request: CitizenQuestion):
    """
    Ask UHAKIX anything about government spending.
    HERALD agent generates citizen-friendly answers in Swahili or English.
    """
    return CitizenResponse(
        answer="Habari! UHAKIX ni hapa kukuambia...",
        language=request.language,
        sources_cited=0,
        agent_used="HERALD/KAZI",
        follow_up_suggestions=[],
    )


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """WhatsApp webhook — receives messages and photo uploads."""
    body = await request.json()
    # Process through WhatsApp service
    return {"status": "received"}


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

    USSD Menu Flow:
    1 → Search Gov't Spending
    2 → Election Results
    3 → Report Form 34A
    4 → My County Budget
    0 → Back
    """
    menu_text = "Karibu UHAKIX!\n\n1. Tafuta Matumizi ya Serikali\n2. Matokeo ya Uchaguzi\n3. Ripoti Form 34A\n4. Bajeti ya Kaunti Yangu\n\nJibu:"

    if text == "":
        response = f"CON {menu_text}"
    elif text.startswith("1"):
        response = f"CON Tafuta:\n1. Wizara\n2. Kaunti\n3. Mkandarasi\n9. Nyuma"
    elif text.startswith("2"):
        response = "CON Ingiza Jina la Eneo:"
    else:
        response = f"END Asante kwa kutumia UHAKIX!"

    return response


@router.get("/report/{report_id}")
async def get_report_status(report_id: str):
    """Check status of a citizen-submitted report or query."""
    return {"report_id": report_id, "status": "processing"}

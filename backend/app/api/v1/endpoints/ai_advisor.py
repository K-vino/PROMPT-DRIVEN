"""
AgriVision AI — AI Advisor Endpoints

Routes:
  POST /api/v1/advisor/crop     — Crop-specific management advisory.
  POST /api/v1/advisor/chat     — Multi-turn conversational AI advisor.
  POST /api/v1/advisor/ask      — Single-shot open question.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_gemini_service
from app.services.gemini_service import GeminiService
from app.models.response import SuccessResponse

router = APIRouter()


# ── Request bodies ────────────────────────────────────────────────────────────

class CropAdvisoryRequest(BaseModel):
    crop: str
    location: str
    soil_type: str = ""
    season: str = ""
    issue: str = ""


class ChatMessage(BaseModel):
    role: str   # "user" or "model"
    text: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class AskRequest(BaseModel):
    question: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "/crop",
    response_model=SuccessResponse[str],
    summary="Get AI crop management advisory",
)
async def crop_advisory(
    body: CropAdvisoryRequest,
    service: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[str]:
    """
    Generate a detailed crop management plan based on crop type, location,
    soil, season, and any specific challenges the farmer is facing.
    """
    advice = await service.get_crop_advisory(
        crop=body.crop,
        location=body.location,
        soil_type=body.soil_type,
        season=body.season,
        issue=body.issue,
    )
    return SuccessResponse(data=advice)


@router.post(
    "/chat",
    response_model=SuccessResponse[str],
    summary="Multi-turn AI advisor chat",
)
async def chat_with_advisor(
    body: ChatRequest,
    service: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[str]:
    """
    Continue a conversation with the AgriVision AI advisor.
    Pass the full conversation history (user + model turns) to maintain context.
    """
    conversation = [
        {"role": msg.role, "parts": [msg.text]}
        for msg in body.messages
    ]
    reply = await service.chat(conversation=conversation)
    return SuccessResponse(data=reply)


@router.post(
    "/ask",
    response_model=SuccessResponse[str],
    summary="Single-shot agricultural question",
)
async def ask_advisor(
    body: AskRequest,
    service: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[str]:
    """
    Ask any agriculture-related question and receive an AI-generated answer.
    """
    answer = await service.ask(body.question)
    return SuccessResponse(data=answer)

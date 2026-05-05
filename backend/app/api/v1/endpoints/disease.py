"""
AgriVision AI — Disease Detection Endpoints

Routes:
  POST /api/v1/disease/detect/upload  — Detect disease from uploaded image.
  POST /api/v1/disease/analyse        — Analyse symptoms with AI.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel

from app.dependencies import get_plantnet_service, get_gemini_service
from app.services.plantnet_service import PlantNetService
from app.services.gemini_service import GeminiService
from app.models.plant import DiseaseDetectionResult, DiseaseInfo
from app.models.response import SuccessResponse
from app.utils.image_utils import read_and_validate_image

router = APIRouter()


class SymptomAnalysisRequest(BaseModel):
    plant_name: str
    symptoms: str
    image_description: str = ""


@router.post(
    "/detect/upload",
    response_model=SuccessResponse[DiseaseDetectionResult],
    summary="Detect plant disease from uploaded image",
)
async def detect_disease_upload(
    file: UploadFile = File(..., description="Plant image showing suspected disease"),
    plant_name: str = Form(default="", description="Known plant name (optional)"),
    plantnet_svc: PlantNetService = Depends(get_plantnet_service),
    gemini_svc: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[DiseaseDetectionResult]:
    """
    Upload a plant image to:
    1. Identify the species with PlantNet.
    2. Use Gemini AI to assess likely diseases from the identification result
       and the visual description.
    """
    image_bytes = await read_and_validate_image(file)

    # Step 1: Identify the plant
    id_result = await plantnet_svc.identify_from_bytes(
        image_bytes=image_bytes,
        filename=file.filename or "image.jpg",
        organs=["leaf"],
    )
    identified_name = id_result.best_match.species_name or plant_name or "Unknown plant"

    # Step 2: Ask Gemini to assess potential diseases
    ai_response = await gemini_svc.analyse_disease(
        plant_name=identified_name,
        symptoms="Visual assessment from uploaded image",
        image_description=(
            f"Identified as '{identified_name}' "
            f"(confidence: {id_result.best_match.score:.0%})"
        ),
    )

    return SuccessResponse(
        data=DiseaseDetectionResult(
            is_healthy=False,   # conservative default; AI text provides nuance
            diseases=[],
            ai_recommendation=ai_response,
        )
    )


@router.post(
    "/analyse",
    response_model=SuccessResponse[DiseaseDetectionResult],
    summary="Analyse plant disease symptoms with AI",
)
async def analyse_symptoms(
    body: SymptomAnalysisRequest,
    gemini_svc: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[DiseaseDetectionResult]:
    """
    Describe plant symptoms in text and receive an AI-powered disease diagnosis
    with treatment and prevention recommendations.
    """
    ai_response = await gemini_svc.analyse_disease(
        plant_name=body.plant_name,
        symptoms=body.symptoms,
        image_description=body.image_description,
    )

    healthy_keywords = ["healthy", "no disease", "no signs", "appears normal"]
    is_healthy = any(kw in ai_response.lower() for kw in healthy_keywords)

    return SuccessResponse(
        data=DiseaseDetectionResult(
            is_healthy=is_healthy,
            diseases=[],
            ai_recommendation=ai_response,
        )
    )

"""
AgriVision AI — Crop Management Endpoints

Routes:
  GET  /api/v1/crops/                     — List all supported crops.
  GET  /api/v1/crops/{crop_name}          — Get info / season guide for a crop.
  POST /api/v1/crops/{crop_name}/plan     — Generate an AI planting plan.
  GET  /api/v1/crops/{crop_name}/pests    — Common pests & diseases for the crop.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.dependencies import get_gemini_service
from app.services.gemini_service import GeminiService
from app.models.response import SuccessResponse

router = APIRouter()

# ── Static reference data (extensible via a database in production) ───────────
SUPPORTED_CROPS: list[dict] = [
    {"name": "Wheat", "category": "Cereal", "seasons": ["rabi"]},
    {"name": "Rice", "category": "Cereal", "seasons": ["kharif"]},
    {"name": "Maize", "category": "Cereal", "seasons": ["kharif", "rabi", "summer"]},
    {"name": "Tomato", "category": "Vegetable", "seasons": ["rabi", "summer"]},
    {"name": "Potato", "category": "Vegetable", "seasons": ["rabi"]},
    {"name": "Onion", "category": "Vegetable", "seasons": ["rabi", "kharif"]},
    {"name": "Soybean", "category": "Legume", "seasons": ["kharif"]},
    {"name": "Chickpea", "category": "Legume", "seasons": ["rabi"]},
    {"name": "Cotton", "category": "Fibre", "seasons": ["kharif"]},
    {"name": "Sugarcane", "category": "Cash Crop", "seasons": ["annual"]},
    {"name": "Banana", "category": "Fruit", "seasons": ["annual"]},
    {"name": "Mango", "category": "Fruit", "seasons": ["annual"]},
]


# ── Request bodies ────────────────────────────────────────────────────────────

class PlantingPlanRequest(BaseModel):
    location: str
    soil_type: str = ""
    farm_size_hectares: float = 1.0
    available_water: str = ""   # e.g. "drip irrigation", "rain-fed"
    budget_level: str = ""      # "low", "medium", "high"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=SuccessResponse[list[dict]],
    summary="List supported crops",
)
async def list_crops(
    category: str | None = Query(default=None, description="Filter by category"),
    season: str | None = Query(default=None, description="Filter by growing season"),
) -> SuccessResponse[list[dict]]:
    """Return the list of crops supported by AgriVision AI."""
    crops = SUPPORTED_CROPS
    if category:
        crops = [c for c in crops if c["category"].lower() == category.lower()]
    if season:
        crops = [c for c in crops if season.lower() in [s.lower() for s in c["seasons"]]]
    return SuccessResponse(data=crops)


@router.get(
    "/{crop_name}",
    response_model=SuccessResponse[str],
    summary="Get AI overview for a crop",
)
async def get_crop_info(
    crop_name: str,
    service: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[str]:
    """
    Return an AI-generated overview of the crop including optimal growing
    conditions, typical yield, and key challenges.
    """
    prompt = (
        f"Provide a concise agricultural overview of {crop_name} covering: "
        "origin, optimal growing conditions (climate, soil, water), typical yield ranges, "
        "major production regions, nutritional / economic value, and key challenges."
    )
    info = await service.ask(prompt)
    return SuccessResponse(data=info)


@router.post(
    "/{crop_name}/plan",
    response_model=SuccessResponse[str],
    summary="Generate AI planting plan for a crop",
)
async def generate_planting_plan(
    crop_name: str,
    body: PlantingPlanRequest,
    service: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[str]:
    """
    Generate a detailed, location-specific planting plan that includes
    timeline, input requirements, and expected returns.
    """
    advice = await service.get_crop_advisory(
        crop=crop_name,
        location=body.location,
        soil_type=body.soil_type,
        issue=(
            f"Farm size: {body.farm_size_hectares} ha. "
            f"Water: {body.available_water}. "
            f"Budget: {body.budget_level}."
        ),
    )
    return SuccessResponse(data=advice)


@router.get(
    "/{crop_name}/pests",
    response_model=SuccessResponse[str],
    summary="Get common pests and diseases for a crop",
)
async def get_pests_diseases(
    crop_name: str,
    service: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[str]:
    """
    Return an AI-generated list of common pests and diseases that affect
    the specified crop, along with identification tips and integrated
    pest management (IPM) strategies.
    """
    prompt = (
        f"List the 5 most economically damaging pests and diseases of {crop_name}. "
        "For each one provide: name, identification signs, damage description, "
        "organic control methods, and chemical control options (if necessary)."
    )
    info = await service.ask(prompt)
    return SuccessResponse(data=info)

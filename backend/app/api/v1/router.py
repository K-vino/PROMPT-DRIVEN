"""
AgriVision AI — API v1 Router

Aggregates all feature-specific routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    plant_id,
    plant_care,
    weather,
    ai_advisor,
    disease,
    crops,
)

api_router = APIRouter()

api_router.include_router(plant_id.router, prefix="/plants/identify", tags=["Plant Identification"])
api_router.include_router(plant_care.router, prefix="/plants/care", tags=["Plant Care"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(ai_advisor.router, prefix="/advisor", tags=["AI Advisor"])
api_router.include_router(disease.router, prefix="/disease", tags=["Disease Detection"])
api_router.include_router(crops.router, prefix="/crops", tags=["Crop Management"])

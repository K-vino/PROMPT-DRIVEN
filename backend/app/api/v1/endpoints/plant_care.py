"""
AgriVision AI — Plant Care Endpoints

Routes:
  GET  /api/v1/plants/care/search        — Search plants by name.
  GET  /api/v1/plants/care/{plant_id}    — Get detailed care info for a plant.
  GET  /api/v1/plants/care/{plant_id}/guide — Get the full care guide.
"""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_perenual_service
from app.services.perenual_service import PerenualService
from app.models.plant import PlantCareInfo, PlantCareSearchResult
from app.models.response import SuccessResponse

router = APIRouter()


@router.get(
    "/search",
    response_model=SuccessResponse[PlantCareSearchResult],
    summary="Search plants by name",
)
async def search_plants(
    q: str = Query(..., min_length=1, description="Plant name search query"),
    page: int = Query(default=1, ge=1, description="Page number"),
    service: PerenualService = Depends(get_perenual_service),
) -> SuccessResponse[PlantCareSearchResult]:
    """
    Search the Perenual database for plants matching the query and return
    care summaries including watering frequency, sunlight, and care level.
    """
    result = await service.search_plants(query=q, page=page)
    return SuccessResponse(data=result)


@router.get(
    "/{plant_id}",
    response_model=SuccessResponse[PlantCareInfo],
    summary="Get plant care details by ID",
)
async def get_plant_care(
    plant_id: int,
    service: PerenualService = Depends(get_perenual_service),
) -> SuccessResponse[PlantCareInfo]:
    """
    Retrieve comprehensive care information for a specific plant using its
    Perenual species ID.
    """
    result = await service.get_plant_details(plant_id=plant_id)
    return SuccessResponse(data=result)


@router.get(
    "/{plant_id}/guide",
    response_model=SuccessResponse[dict],
    summary="Get full care guide for a plant",
)
async def get_care_guide(
    plant_id: int,
    service: PerenualService = Depends(get_perenual_service),
) -> SuccessResponse[dict]:
    """
    Retrieve the full structured care guide (watering schedule, sunlight
    requirements, pruning, fertilisation) for the given plant.
    """
    guide = await service.get_care_guide(plant_id=plant_id)
    return SuccessResponse(data=guide)

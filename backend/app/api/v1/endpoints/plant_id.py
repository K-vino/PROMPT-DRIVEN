"""
AgriVision AI — Plant Identification Endpoints

Routes:
  POST /api/v1/plants/identify/upload   — Identify plant from uploaded image.
  POST /api/v1/plants/identify/url      — Identify plant from image URL.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel

from app.dependencies import get_plantnet_service
from app.services.plantnet_service import PlantNetService
from app.models.plant import PlantIdentificationResult
from app.models.response import SuccessResponse
from app.utils.image_utils import read_and_validate_image

router = APIRouter()


class IdentifyByURLRequest(BaseModel):
    image_url: str
    organs: list[str] = ["auto"]


@router.post(
    "/upload",
    response_model=SuccessResponse[PlantIdentificationResult],
    summary="Identify plant from uploaded image",
)
async def identify_plant_upload(
    file: UploadFile = File(..., description="Plant image (JPEG, PNG, WebP)"),
    organs: str = Form(default="auto", description="Comma-separated organ names, e.g. 'leaf,flower'"),
    service: PlantNetService = Depends(get_plantnet_service),
) -> SuccessResponse[PlantIdentificationResult]:
    """
    Upload an image and receive species identification results ranked by
    confidence score.
    """
    image_bytes = await read_and_validate_image(file)
    organ_list = [o.strip() for o in organs.split(",") if o.strip()]
    result = await service.identify_from_bytes(
        image_bytes=image_bytes,
        filename=file.filename or "image.jpg",
        organs=organ_list or ["auto"],
    )
    return SuccessResponse(data=result)


@router.post(
    "/url",
    response_model=SuccessResponse[PlantIdentificationResult],
    summary="Identify plant from image URL",
)
async def identify_plant_url(
    body: IdentifyByURLRequest,
    service: PlantNetService = Depends(get_plantnet_service),
) -> SuccessResponse[PlantIdentificationResult]:
    """
    Provide a publicly accessible image URL and receive species identification
    results ranked by confidence score.
    """
    result = await service.identify_from_url(
        image_url=body.image_url,
        organs=body.organs,
    )
    return SuccessResponse(data=result)

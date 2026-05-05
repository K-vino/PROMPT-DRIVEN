"""
AgriVision AI — Plant-related Pydantic models.

Used by both the PlantNet (identification) and Perenual (care info) services.
"""

from pydantic import BaseModel, HttpUrl


# ── PlantNet identification ───────────────────────────────────────────────────

class PlantMatch(BaseModel):
    """A single candidate returned by the PlantNet identification API."""
    species_name: str
    common_names: list[str] = []
    family: str = ""
    score: float  # confidence 0–1
    image_url: str | None = None


class PlantIdentificationResult(BaseModel):
    best_match: PlantMatch
    candidates: list[PlantMatch]
    query_image_url: str | None = None


# ── Perenual care info ────────────────────────────────────────────────────────

class PlantCareInfo(BaseModel):
    """Care guide for a single plant species from the Perenual API."""
    id: int
    common_name: str
    scientific_name: list[str] = []
    watering: str = ""
    sunlight: list[str] = []
    care_level: str = ""
    description: str = ""
    image_url: str | None = None
    hardiness_zone: str = ""
    growth_rate: str = ""
    maintenance: str = ""
    poisonous_to_pets: bool = False
    poisonous_to_humans: bool = False


class PlantCareSearchResult(BaseModel):
    results: list[PlantCareInfo]
    total: int
    current_page: int
    last_page: int


# ── Disease detection ─────────────────────────────────────────────────────────

class DiseaseInfo(BaseModel):
    name: str
    confidence: float
    description: str = ""
    treatment: str = ""
    prevention: str = ""


class DiseaseDetectionResult(BaseModel):
    is_healthy: bool
    diseases: list[DiseaseInfo] = []
    ai_recommendation: str = ""

"""
AgriVision AI — Perenual Service

Responsibilities:
  - Search for plants and retrieve detailed care guides via the Perenual API.
  - Map raw API JSON to typed PlantCareInfo models.

Perenual API docs: https://perenual.com/docs/api
"""

import httpx
from app.models.plant import PlantCareInfo, PlantCareSearchResult
from app.core.exceptions import ExternalAPIError

PERENUAL_BASE_URL = "https://perenual.com/api"


class PerenualService:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    # ── Public methods ────────────────────────────────────────────────────────

    async def search_plants(
        self,
        query: str,
        page: int = 1,
    ) -> PlantCareSearchResult:
        """
        Search plants by common or scientific name.

        Args:
            query: Search term (plant name).
            page: Page number for pagination.
        """
        params = {"key": self._api_key, "q": query, "page": page}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{PERENUAL_BASE_URL}/species-list", params=params)
        if response.status_code != 200:
            raise ExternalAPIError(
                "Perenual",
                f"API returned {response.status_code}: {response.text[:200]}",
            )
        return self._parse_search(response.json())

    async def get_plant_details(self, plant_id: int) -> PlantCareInfo:
        """
        Fetch detailed care information for a specific plant by its Perenual ID.

        Args:
            plant_id: Perenual species ID.
        """
        params = {"key": self._api_key}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{PERENUAL_BASE_URL}/species/details/{plant_id}",
                params=params,
            )
        if response.status_code != 200:
            raise ExternalAPIError(
                "Perenual",
                f"API returned {response.status_code}: {response.text[:200]}",
            )
        return self._parse_detail(response.json())

    async def get_care_guide(self, plant_id: int) -> dict:
        """
        Retrieve the full care guide (watering schedule, sunlight, pruning, etc.)
        for a plant.

        Args:
            plant_id: Perenual species ID.
        """
        params = {"key": self._api_key, "species_id": plant_id}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{PERENUAL_BASE_URL}/species-care-guide-list", params=params)
        if response.status_code != 200:
            raise ExternalAPIError(
                "Perenual",
                f"API returned {response.status_code}: {response.text[:200]}",
            )
        data = response.json()
        guides = data.get("data", [])
        return guides[0] if guides else {}

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _parse_search(data: dict) -> PlantCareSearchResult:
        plants: list[PlantCareInfo] = []
        for item in data.get("data", []):
            plants.append(PerenualService._map_plant(item))
        return PlantCareSearchResult(
            results=plants,
            total=data.get("total", len(plants)),
            current_page=data.get("current_page", 1),
            last_page=data.get("last_page", 1),
        )

    @staticmethod
    def _map_plant(item: dict) -> PlantCareInfo:
        default_img = item.get("default_image") or {}
        img_url = default_img.get("medium_url") or default_img.get("original_url")
        hardiness = item.get("hardiness") or {}
        hardiness_str = f"{hardiness.get('min', '')} – {hardiness.get('max', '')}".strip(" –")
        return PlantCareInfo(
            id=item.get("id", 0),
            common_name=item.get("common_name", ""),
            scientific_name=item.get("scientific_name", []),
            watering=item.get("watering", ""),
            sunlight=item.get("sunlight", []),
            care_level=item.get("care_level", ""),
            description=item.get("description", ""),
            image_url=img_url,
            hardiness_zone=hardiness_str,
            growth_rate=item.get("growth_rate", ""),
            maintenance=item.get("maintenance", ""),
            poisonous_to_pets=bool(item.get("poisonous_to_pets")),
            poisonous_to_humans=bool(item.get("poisonous_to_humans")),
        )

    @staticmethod
    def _parse_detail(data: dict) -> PlantCareInfo:
        return PerenualService._map_plant(data)

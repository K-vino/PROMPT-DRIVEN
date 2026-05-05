"""
AgriVision AI — PlantNet Service

Responsibilities:
  - Send plant images to the PlantNet v2 identification API.
  - Parse the ranked candidate list into typed PlantMatch objects.
  - Support both file-upload and URL-based identification.

PlantNet API docs: https://my.plantnet.org/doc/openapi
"""

import httpx
from app.models.plant import PlantMatch, PlantIdentificationResult
from app.core.exceptions import ExternalAPIError

PLANTNET_BASE_URL = "https://my-api.plantnet.org/v2/identify"
DEFAULT_PROJECT = "all"  # use the global model


class PlantNetService:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    # ── Public methods ────────────────────────────────────────────────────────

    async def identify_from_url(
        self,
        image_url: str,
        organs: list[str] | None = None,
    ) -> PlantIdentificationResult:
        """
        Identify a plant from a publicly accessible image URL.

        Args:
            image_url: URL of the plant image.
            organs: List of plant organs visible in the image
                    (e.g. ["leaf", "flower"]). Defaults to ["auto"].
        """
        organs = organs or ["auto"]
        params = {
            "api-key": self._api_key,
            "images": image_url,
            "organs": organs,
            "lang": "en",
            "include-related-images": "true",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{PLANTNET_BASE_URL}/{DEFAULT_PROJECT}",
                params=params,
            )
        return self._parse_response(response, image_url)

    async def identify_from_bytes(
        self,
        image_bytes: bytes,
        filename: str = "image.jpg",
        organs: list[str] | None = None,
    ) -> PlantIdentificationResult:
        """
        Identify a plant from raw image bytes (multipart upload).

        Args:
            image_bytes: Raw image bytes.
            filename: Suggested filename sent to the API.
            organs: List of plant organs visible in the image.
        """
        organs = organs or ["auto"]
        params = {"api-key": self._api_key, "lang": "en", "organs": organs}
        files = [("images", (filename, image_bytes, "image/jpeg"))]
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{PLANTNET_BASE_URL}/{DEFAULT_PROJECT}",
                params=params,
                files=files,
            )
        return self._parse_response(response)

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _parse_response(
        response: httpx.Response,
        query_image_url: str | None = None,
    ) -> PlantIdentificationResult:
        if response.status_code != 200:
            raise ExternalAPIError(
                "PlantNet",
                f"API returned {response.status_code}: {response.text[:200]}",
            )
        data = response.json()
        results: list[PlantMatch] = []
        for result in data.get("results", []):
            species = result.get("species", {})
            images = result.get("images", [])
            thumb = images[0].get("url", {}).get("m") if images else None
            results.append(
                PlantMatch(
                    species_name=species.get("scientificNameWithoutAuthor", ""),
                    common_names=species.get("commonNames", []),
                    family=species.get("family", {}).get("scientificNameWithoutAuthor", ""),
                    score=result.get("score", 0.0),
                    image_url=thumb,
                )
            )
        if not results:
            raise ExternalAPIError("PlantNet", "No identification results returned.")
        return PlantIdentificationResult(
            best_match=results[0],
            candidates=results,
            query_image_url=query_image_url,
        )

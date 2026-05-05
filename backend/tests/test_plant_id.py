"""
Tests for PlantNet service parsing logic.

These tests mock the httpx responses so no real API calls are made.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.plantnet_service import PlantNetService
from app.core.exceptions import ExternalAPIError

MOCK_PLANTNET_RESPONSE = {
    "results": [
        {
            "score": 0.92,
            "species": {
                "scientificNameWithoutAuthor": "Solanum lycopersicum",
                "commonNames": ["Tomato", "Garden tomato"],
                "family": {"scientificNameWithoutAuthor": "Solanaceae"},
            },
            "images": [{"url": {"m": "https://example.com/tomato.jpg"}}],
        },
        {
            "score": 0.05,
            "species": {
                "scientificNameWithoutAuthor": "Solanum melongena",
                "commonNames": ["Eggplant"],
                "family": {"scientificNameWithoutAuthor": "Solanaceae"},
            },
            "images": [],
        },
    ]
}


@pytest.fixture
def service() -> PlantNetService:
    return PlantNetService(api_key="test-key")


@pytest.mark.asyncio
async def test_identify_from_url_success(service: PlantNetService) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_PLANTNET_RESPONSE

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        result = await service.identify_from_url("https://example.com/plant.jpg")

    assert result.best_match.species_name == "Solanum lycopersicum"
    assert result.best_match.score == pytest.approx(0.92)
    assert "Tomato" in result.best_match.common_names
    assert len(result.candidates) == 2


@pytest.mark.asyncio
async def test_identify_from_url_api_error(service: PlantNetService) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 403
    mock_response.text = "Unauthorized"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with pytest.raises(ExternalAPIError, match="PlantNet"):
            await service.identify_from_url("https://example.com/plant.jpg")


@pytest.mark.asyncio
async def test_identify_from_url_empty_results(service: PlantNetService) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with pytest.raises(ExternalAPIError, match="No identification results"):
            await service.identify_from_url("https://example.com/plant.jpg")

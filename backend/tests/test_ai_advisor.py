"""
Tests for GeminiService.

These tests mock the google.genai SDK so no real API calls are made.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.gemini_service import GeminiService
from app.core.exceptions import ExternalAPIError


@pytest.fixture
def service() -> GeminiService:
    with patch("google.genai.Client"):
        svc = GeminiService(api_key="test-key")
    return svc


@pytest.mark.asyncio
async def test_ask_success(service: GeminiService) -> None:
    mock_response = MagicMock()
    mock_response.text = "Tomatoes grow best in warm climates."
    service._client.models.generate_content = MagicMock(return_value=mock_response)

    result = await service.ask("How do I grow tomatoes?")
    assert "Tomatoes" in result
    service._client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_ask_raises_on_api_error(service: GeminiService) -> None:
    service._client.models.generate_content = MagicMock(side_effect=RuntimeError("quota exceeded"))

    with pytest.raises(ExternalAPIError, match="Gemini"):
        await service.ask("Tell me about wheat farming.")


@pytest.mark.asyncio
async def test_get_crop_advisory_calls_ask(service: GeminiService) -> None:
    mock_response = MagicMock()
    mock_response.text = "Wheat advisory: plant in October..."
    service._client.models.generate_content = MagicMock(return_value=mock_response)

    result = await service.get_crop_advisory(
        crop="Wheat",
        location="Punjab, India",
        soil_type="sandy loam",
        season="rabi",
    )
    assert "Wheat" in mock_response.text
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_analyse_disease_calls_ask(service: GeminiService) -> None:
    mock_response = MagicMock()
    mock_response.text = "Likely cause: late blight. Treatment: apply fungicide."
    service._client.models.generate_content = MagicMock(return_value=mock_response)

    result = await service.analyse_disease(
        plant_name="Tomato",
        symptoms="Brown spots on leaves, wilting",
    )
    assert isinstance(result, str)
    assert len(result) > 0

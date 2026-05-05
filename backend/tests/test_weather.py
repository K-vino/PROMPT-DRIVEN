"""
Tests for WeatherService parsing logic.

These tests mock the httpx responses so no real API calls are made.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.weather_service import WeatherService
from app.core.exceptions import ExternalAPIError

MOCK_CURRENT_WEATHER = {
    "name": "London",
    "sys": {"country": "GB", "sunrise": 1700000000, "sunset": 1700040000},
    "coord": {"lat": 51.5, "lon": -0.12},
    "main": {"temp": 15.5, "feels_like": 13.0, "humidity": 75, "pressure": 1013},
    "wind": {"speed": 5.2, "deg": 220},
    "visibility": 10000,
    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
    "dt": 1700020000,
}

MOCK_FORECAST = {
    "city": {"name": "London", "country": "GB"},
    "list": [
        {
            "dt": 1700020000,
            "main": {"temp": 14.0, "feels_like": 12.0, "humidity": 80},
            "wind": {"speed": 4.0},
            "weather": [{"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}],
        }
    ],
}


@pytest.fixture
def service() -> WeatherService:
    return WeatherService(api_key="test-key")


@pytest.mark.asyncio
async def test_get_current_weather_by_city(service: WeatherService) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_CURRENT_WEATHER

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        result = await service.get_current_weather(city="London")

    assert result.city == "London"
    assert result.country == "GB"
    assert result.temperature == pytest.approx(15.5)
    assert result.humidity == 75
    assert len(result.conditions) == 1
    assert result.conditions[0].main == "Clear"


@pytest.mark.asyncio
async def test_get_current_weather_api_error(service: WeatherService) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 401
    mock_response.text = "Invalid API key"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with pytest.raises(ExternalAPIError, match="OpenWeatherMap"):
            await service.get_current_weather(city="London")


def test_build_params_requires_city_or_coords(service: WeatherService) -> None:
    with pytest.raises(ValueError, match="Provide either"):
        service._build_params(city=None, lat=None, lon=None)


@pytest.mark.asyncio
async def test_get_forecast_success(service: WeatherService) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_FORECAST

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        result = await service.get_forecast(lat=51.5, lon=-0.12)

    assert result.city == "London"
    assert len(result.entries) == 1
    assert result.entries[0].temperature == pytest.approx(14.0)

"""
AgriVision AI — Weather Endpoints

Routes:
  GET /api/v1/weather/current   — Current weather by city or coordinates.
  GET /api/v1/weather/forecast  — 5-day forecast by city or coordinates.
  GET /api/v1/weather/insight   — AI-generated farm advisory for current weather.
"""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_weather_service, get_gemini_service
from app.services.weather_service import WeatherService
from app.services.gemini_service import GeminiService
from app.models.weather import CurrentWeather, WeatherForecast
from app.models.response import SuccessResponse
from app.utils.cache import default_cache

router = APIRouter()


@router.get(
    "/current",
    response_model=SuccessResponse[CurrentWeather],
    summary="Get current weather",
)
async def get_current_weather(
    city: str | None = Query(default=None, description="City name, e.g. 'London,UK'"),
    lat: float | None = Query(default=None, description="Latitude"),
    lon: float | None = Query(default=None, description="Longitude"),
    service: WeatherService = Depends(get_weather_service),
) -> SuccessResponse[CurrentWeather]:
    """
    Fetch real-time weather data. Provide either `city` or `lat`+`lon`.
    Results are cached for 5 minutes.
    """
    cache_key = f"weather:current:{city}:{lat}:{lon}"
    result: CurrentWeather = await default_cache.get_or_set(
        cache_key,
        lambda: service.get_current_weather(city=city, lat=lat, lon=lon),
    )
    return SuccessResponse(data=result)


@router.get(
    "/forecast",
    response_model=SuccessResponse[WeatherForecast],
    summary="Get weather forecast",
)
async def get_forecast(
    city: str | None = Query(default=None, description="City name"),
    lat: float | None = Query(default=None, description="Latitude"),
    lon: float | None = Query(default=None, description="Longitude"),
    days: int = Query(default=5, ge=1, le=5, description="Forecast days (1–5)"),
    service: WeatherService = Depends(get_weather_service),
) -> SuccessResponse[WeatherForecast]:
    """
    Fetch a multi-day 3-hour-interval weather forecast.
    Results are cached for 5 minutes.
    """
    cache_key = f"weather:forecast:{city}:{lat}:{lon}:{days}"
    result: WeatherForecast = await default_cache.get_or_set(
        cache_key,
        lambda: service.get_forecast(city=city, lat=lat, lon=lon, days=days),
    )
    return SuccessResponse(data=result)


@router.get(
    "/insight",
    response_model=SuccessResponse[str],
    summary="AI farming insight for current weather",
)
async def get_weather_insight(
    city: str | None = Query(default=None, description="City name"),
    lat: float | None = Query(default=None, description="Latitude"),
    lon: float | None = Query(default=None, description="Longitude"),
    crop: str = Query(default="", description="Primary crop being grown"),
    weather_svc: WeatherService = Depends(get_weather_service),
    gemini_svc: GeminiService = Depends(get_gemini_service),
) -> SuccessResponse[str]:
    """
    Combines current weather data with Gemini AI to produce actionable
    farming recommendations (irrigation, pest risk, planting windows).
    """
    weather = await weather_svc.get_current_weather(city=city, lat=lat, lon=lon)
    summary = (
        f"City: {weather.city}, {weather.country}\n"
        f"Temperature: {weather.temperature}°C (feels like {weather.feels_like}°C)\n"
        f"Humidity: {weather.humidity}%\n"
        f"Wind: {weather.wind_speed} m/s\n"
        f"Conditions: {', '.join(c.description for c in weather.conditions)}"
    )
    insight = await gemini_svc.weather_to_farm_insight(
        weather_summary=summary,
        crop=crop,
        region=f"{weather.city}, {weather.country}",
    )
    return SuccessResponse(data=insight)

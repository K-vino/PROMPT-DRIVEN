"""
AgriVision AI — Shared FastAPI dependencies.

Provides reusable Depends() callables for:
  - Accessing app settings.
  - Returning configured service instances.
"""

from fastapi import Depends
from app.config import Settings, get_settings
from app.services.plantnet_service import PlantNetService
from app.services.perenual_service import PerenualService
from app.services.weather_service import WeatherService
from app.services.gemini_service import GeminiService


def get_plantnet_service(settings: Settings = Depends(get_settings)) -> PlantNetService:
    return PlantNetService(api_key=settings.PLANTNET_API_KEY)


def get_perenual_service(settings: Settings = Depends(get_settings)) -> PerenualService:
    return PerenualService(api_key=settings.PERENUAL_API_KEY)


def get_weather_service(settings: Settings = Depends(get_settings)) -> WeatherService:
    return WeatherService(api_key=settings.OPENWEATHER_API_KEY)


def get_gemini_service(settings: Settings = Depends(get_settings)) -> GeminiService:
    return GeminiService(api_key=settings.GEMINI_API_KEY)

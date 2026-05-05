"""
AgriVision AI — Weather-related Pydantic models.

Wraps OpenWeatherMap Current Weather and Forecast responses into typed models.
"""

from pydantic import BaseModel


class WeatherCondition(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class CurrentWeather(BaseModel):
    city: str
    country: str
    lat: float
    lon: float
    temperature: float          # Celsius
    feels_like: float           # Celsius
    humidity: int               # %
    pressure: int               # hPa
    wind_speed: float           # m/s
    wind_direction: int         # degrees
    visibility: int             # metres
    conditions: list[WeatherCondition]
    sunrise: int                # Unix timestamp
    sunset: int                 # Unix timestamp
    timestamp: int              # Unix timestamp of observation


class ForecastEntry(BaseModel):
    timestamp: int
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    conditions: list[WeatherCondition]
    rain_3h: float = 0.0        # mm of rain in last 3 hours


class WeatherForecast(BaseModel):
    city: str
    country: str
    entries: list[ForecastEntry]


class AgriculturalWeatherInsight(BaseModel):
    """
    AI-generated commentary on how the current / forecast weather
    affects agricultural activities.
    """
    summary: str
    irrigation_advice: str
    planting_advice: str
    pest_risk: str
    frost_warning: bool = False

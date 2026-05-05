"""
AgriVision AI — Weather Service

Responsibilities:
  - Fetch current weather conditions from OpenWeatherMap.
  - Fetch a 5-day / 3-hour forecast.
  - Map raw API JSON to typed weather models.

OpenWeatherMap API docs: https://openweathermap.org/api
"""

import httpx
from app.models.weather import (
    CurrentWeather,
    WeatherCondition,
    WeatherForecast,
    ForecastEntry,
)
from app.core.exceptions import ExternalAPIError

OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherService:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    # ── Public methods ────────────────────────────────────────────────────────

    async def get_current_weather(
        self,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> CurrentWeather:
        """
        Fetch current weather by city name or coordinates.

        Provide either `city` or both `lat` and `lon`.
        """
        params = self._build_params(city=city, lat=lat, lon=lon)
        params["units"] = "metric"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{OWM_BASE_URL}/weather", params=params)
        if response.status_code != 200:
            raise ExternalAPIError(
                "OpenWeatherMap",
                f"API returned {response.status_code}: {response.text[:200]}",
            )
        return self._parse_current(response.json())

    async def get_forecast(
        self,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        days: int = 5,
    ) -> WeatherForecast:
        """
        Fetch a multi-day 3-hour-interval forecast.

        Args:
            days: Number of days to include (max 5, limited by free tier).
        """
        params = self._build_params(city=city, lat=lat, lon=lon)
        params["units"] = "metric"
        params["cnt"] = min(days * 8, 40)  # 8 slots per day, max 40
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{OWM_BASE_URL}/forecast", params=params)
        if response.status_code != 200:
            raise ExternalAPIError(
                "OpenWeatherMap",
                f"API returned {response.status_code}: {response.text[:200]}",
            )
        return self._parse_forecast(response.json())

    # ── Private helpers ───────────────────────────────────────────────────────

    def _build_params(
        self,
        city: str | None,
        lat: float | None,
        lon: float | None,
    ) -> dict:
        params: dict = {"appid": self._api_key}
        if city:
            params["q"] = city
        elif lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            raise ValueError("Provide either 'city' or both 'lat' and 'lon'.")
        return params

    @staticmethod
    def _parse_conditions(raw: list[dict]) -> list[WeatherCondition]:
        return [
            WeatherCondition(
                id=c.get("id", 0),
                main=c.get("main", ""),
                description=c.get("description", ""),
                icon=c.get("icon", ""),
            )
            for c in raw
        ]

    @staticmethod
    def _parse_current(data: dict) -> CurrentWeather:
        sys = data.get("sys", {})
        wind = data.get("wind", {})
        return CurrentWeather(
            city=data.get("name", ""),
            country=sys.get("country", ""),
            lat=data.get("coord", {}).get("lat", 0.0),
            lon=data.get("coord", {}).get("lon", 0.0),
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            pressure=data["main"]["pressure"],
            wind_speed=wind.get("speed", 0.0),
            wind_direction=wind.get("deg", 0),
            visibility=data.get("visibility", 0),
            conditions=WeatherService._parse_conditions(data.get("weather", [])),
            sunrise=sys.get("sunrise", 0),
            sunset=sys.get("sunset", 0),
            timestamp=data.get("dt", 0),
        )

    @staticmethod
    def _parse_forecast(data: dict) -> WeatherForecast:
        city_info = data.get("city", {})
        entries: list[ForecastEntry] = []
        for item in data.get("list", []):
            rain = item.get("rain", {})
            entries.append(
                ForecastEntry(
                    timestamp=item.get("dt", 0),
                    temperature=item["main"]["temp"],
                    feels_like=item["main"]["feels_like"],
                    humidity=item["main"]["humidity"],
                    wind_speed=item.get("wind", {}).get("speed", 0.0),
                    conditions=WeatherService._parse_conditions(item.get("weather", [])),
                    rain_3h=rain.get("3h", 0.0),
                )
            )
        return WeatherForecast(
            city=city_info.get("name", ""),
            country=city_info.get("country", ""),
            entries=entries,
        )

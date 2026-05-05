"""
AgriVision AI — Configuration
Reads all settings from environment variables (see .env.example).
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "AgriVision AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:5500"]

    # ── External API Keys ─────────────────────────────────────────────────────
    PLANTNET_API_KEY: str = ""
    PERENUAL_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # ── Cache (simple in-memory TTL, seconds) ─────────────────────────────────
    CACHE_TTL_SECONDS: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()

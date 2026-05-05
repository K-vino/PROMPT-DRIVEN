"""
AgriVision AI — Security utilities.

Responsibilities:
  - Validate that required API keys are configured.
  - Provide an optional bearer-token dependency for protecting internal routes.
"""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    """
    Dependency that enforces the presence of an X-API-Key header.
    Use on any route that should only be accessible by trusted clients.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    return api_key


def validate_external_key(key: str, service_name: str) -> None:
    """
    Raise a RuntimeError if a required external API key is empty.
    Called at service instantiation time so problems surface early.
    """
    if not key:
        raise RuntimeError(
            f"Missing API key for {service_name}. "
            f"Set the appropriate environment variable in your .env file."
        )

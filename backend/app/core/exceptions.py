"""
AgriVision AI — Custom exception handlers.

Centralises HTTP error responses so every endpoint returns a consistent JSON body:
  { "error": "<message>", "detail": "<optional detail>" }
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all custom exception handlers to the FastAPI instance."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)},
        )


class ExternalAPIError(Exception):
    """Raised when a third-party API returns an unexpected response."""

    def __init__(self, service: str, message: str) -> None:
        self.service = service
        super().__init__(f"[{service}] {message}")

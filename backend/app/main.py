"""
AgriVision AI — FastAPI application entry point.

Responsibilities:
  - Create the FastAPI app instance.
  - Register CORS middleware.
  - Mount the v1 API router.
  - Expose /health and /info endpoints.
  - Serve the static frontend (when running in production mode).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.config import get_settings
from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AgriVision AI — an intelligent agriculture platform that integrates "
        "plant identification, disease detection, weather forecasting, and "
        "AI-powered crop advisory."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Custom exception handlers ─────────────────────────────────────────────────
register_exception_handlers(app)

# ── API router (versioned) ────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")

# ── Built-in utility endpoints ────────────────────────────────────────────────
@app.get("/health", tags=["system"], summary="Health check")
async def health() -> JSONResponse:
    """Returns 200 when the service is up."""
    return JSONResponse({"status": "ok", "service": settings.APP_NAME})


@app.get("/info", tags=["system"], summary="Application info")
async def info() -> JSONResponse:
    """Returns application metadata."""
    return JSONResponse(
        {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
        }
    )


# ── Serve frontend static files (production) ─────────────────────────────────
# Must be mounted AFTER all API routes so it doesn't shadow them.
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

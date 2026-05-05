"""
AgriVision AI — Generic API response envelope models.

Every endpoint returns one of these shapes so the frontend can rely on a
consistent structure.
"""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    page: int
    per_page: int
    total: int

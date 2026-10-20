"""
Common Pydantic schemas used across all entities.
"""

from datetime import datetime
from typing import Generic, TypeVar, Optional
from uuid import UUID

from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: list[T]
    total: int = Field(ge=0, description="Total number of records")
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)


class GeoCoordinate(BaseModel):
    """Geographic coordinate pair."""
    latitude: float = Field(ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(ge=-180.0, le=180.0, description="Longitude in decimal degrees")


class TimestampMixin(BaseModel):
    """Mixin providing standard timestamp fields."""
    created_at: datetime = Field(description="Record creation timestamp (UTC)")
    updated_at: datetime = Field(description="Last modification timestamp (UTC)")


class IDMixin(BaseModel):
    """Mixin providing UUID identifier."""
    id: UUID = Field(description="UUID primary key")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: Optional[str] = None
    database: Optional[str] = None
    timestamp: datetime


class ErrorResponse(BaseModel):
    """RFC 7807 Problem Details error response."""
    type: str = Field(description="URI reference for error type")
    title: str = Field(description="Short human-readable summary")
    status: int = Field(description="HTTP status code")
    detail: str = Field(description="Human-readable explanation")
    instance: Optional[str] = Field(None, description="URI of the specific occurrence")

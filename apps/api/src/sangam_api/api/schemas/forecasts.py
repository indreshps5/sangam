"""Forecast API schemas."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    """Schema for requesting a forecast."""
    warehouse_id: UUID
    forecast_horizon_days: int = Field(ge=1, le=90, default=30)
    product_category: Optional[str] = None
    confidence_level: float = Field(ge=0.5, le=0.99, default=0.95)


class ForecastDataPoint(BaseModel):
    """Single forecast data point."""
    date: date
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    confidence: float


class ForecastResponse(BaseModel):
    """Schema for forecast response."""
    id: UUID
    warehouse_id: UUID
    product_category: Optional[str]
    forecast_horizon_days: int
    confidence_level: float
    data_points: list[ForecastDataPoint]
    model_version: str
    created_at: datetime
    accuracy_score: Optional[float] = None

    model_config = {"from_attributes": True}


class ForecastListResponse(BaseModel):
    """List of forecasts."""
    items: list[ForecastResponse]
    total: int

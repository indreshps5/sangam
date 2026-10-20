"""
Forecast API schemas — request/response for demand forecasting.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from sangam_api.core.enums import ForecastModelType
from sangam_api.api.schemas.common import IDMixin, TimestampMixin


class ForecastDataPointCreate(BaseModel):
    """Schema for a single forecast data point."""
    forecast_date: date = Field(description="Date being predicted")
    predicted_demand: float = Field(ge=0, description="Point estimate")
    lower_bound: float = Field(ge=0, description="Lower confidence bound")
    upper_bound: float = Field(ge=0, description="Upper confidence bound")


class ForecastCreate(BaseModel):
    """Schema for creating a forecast."""
    depot_id: UUID = Field(description="Target depot")
    product_category: Optional[str] = Field(None, max_length=100)
    model_type: ForecastModelType = Field(description="ML model type")
    model_version: str = Field(min_length=1, max_length=50)
    forecast_horizon_days: int = Field(ge=1, le=365, description="Days into the future")
    confidence_level: float = Field(0.95, ge=0.5, le=0.99, description="Statistical confidence")
    training_data_end_date: Optional[date] = None
    parameters: Optional[str] = Field(None, description="JSON model hyperparameters")


class ForecastDataPointResponse(IDMixin):
    """Schema for forecast data point response."""
    forecast_id: UUID
    forecast_date: date
    predicted_demand: float
    lower_bound: float
    upper_bound: float

    model_config = {"from_attributes": True}


class ForecastResponse(IDMixin, TimestampMixin):
    """Schema for forecast response."""
    depot_id: UUID
    product_category: Optional[str] = None
    model_type: str
    model_version: str
    forecast_horizon_days: int
    confidence_level: float
    accuracy_score: Optional[float] = None
    training_data_end_date: Optional[date] = None
    parameters: Optional[str] = None
    status: str
    data_points: list[ForecastDataPointResponse] = []

    model_config = {"from_attributes": True}


class ForecastListResponse(BaseModel):
    """Paginated list of forecasts."""
    items: list[ForecastResponse]
    total: int
    skip: int
    limit: int


class DemandObservationCreate(BaseModel):
    """Schema for creating a demand observation."""
    depot_id: UUID = Field(description="Depot where demand was observed")
    product_category: str = Field(min_length=1, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    observation_date: date = Field(description="Date of observation")
    demand_quantity: float = Field(ge=0, description="Observed demand quantity")
    unit_of_measure: str = Field("unit", max_length=20)
    source: str = Field("manual", max_length=50, description="Data source")
    is_outlier: bool = Field(False, description="Flag for anomalous observations")
    notes: Optional[str] = None


class DemandObservationResponse(IDMixin, TimestampMixin):
    """Schema for demand observation response."""
    depot_id: UUID
    product_category: str
    sku: Optional[str] = None
    observation_date: date
    demand_quantity: float
    unit_of_measure: str
    source: str
    is_outlier: bool
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class DemandObservationListResponse(BaseModel):
    """Paginated list of demand observations."""
    items: list[DemandObservationResponse]
    total: int
    skip: int
    limit: int

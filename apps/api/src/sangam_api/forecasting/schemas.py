"""
Pydantic schemas for forecasting API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    """Request schema for generating a forecast."""
    inventory_item_id: UUID = Field(..., description="ID of inventory item to forecast")
    horizon_days: int = Field(30, ge=1, le=365, description="Number of days to forecast")
    model_type: str = Field("baseline", description="Model type (baseline, naive)")
    confidence_level: float = Field(0.95, ge=0.5, le=0.99, description="Confidence level")


class ForecastDataPointResponse(BaseModel):
    """Single forecast data point."""
    date: date
    predicted_demand: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    """Complete forecast response."""
    status: str
    forecast_id: Optional[str] = None
    inventory_item_id: str
    model_info: Dict[str, Any]
    forecast_data: List[Dict[str, Any]]
    evaluation_metrics: Optional[Dict[str, float]] = None
    data_assessment: Dict[str, Any]
    generated_at: str


class ShortageRiskRequest(BaseModel):
    """Request schema for shortage risk analysis."""
    inventory_item_id: UUID = Field(..., description="ID of inventory item")
    forecast_id: Optional[UUID] = Field(None, description="Specific forecast to use (latest if None)")


class ContributingFactor(BaseModel):
    """Contributing factor to shortage risk."""
    factor: str
    severity: str
    description: str
    impact: str
    recommendation: str


class DaysOfStock(BaseModel):
    """Days of stock calculation."""
    days_of_stock: float
    status: str
    message: str
    current_stock: float
    average_daily_demand: float
    incoming_shipments_total: float


class ShortageEstimate(BaseModel):
    """Shortage quantity estimate."""
    total_demand_forecast: float
    current_stock: float
    incoming_shipments: float
    net_requirement: float
    shortage_quantity: float
    horizon_days: int
    has_shortage: bool


class ReorderRecommendation(BaseModel):
    """Reorder timing recommendation."""
    should_reorder: bool
    urgency: str
    days_until_reorder: float
    recommended_reorder_date: str
    lead_time_days: int
    safety_stock_days: int
    reorder_point_days: int
    message: str


class RiskAssessment(BaseModel):
    """Complete risk assessment."""
    risk_level: str
    risk_score: float
    days_of_stock: DaysOfStock
    shortage_estimate: ShortageEstimate
    reorder_recommendation: ReorderRecommendation
    contributing_factors: List[ContributingFactor]
    summary: str
    assessment_timestamp: str


class ShortageRiskResponse(BaseModel):
    """Shortage risk analysis response."""
    status: str
    inventory_item_id: str
    forecast_id: Optional[str] = None
    risk_assessment: Optional[RiskAssessment] = None
    current_stock: Optional[float] = None
    analyzed_at: Optional[str] = None
    message: Optional[str] = None
    forecast_error: Optional[Dict[str, Any]] = None


class ForecastSummary(BaseModel):
    """Summary of a forecast."""
    id: str
    inventory_item_id: str
    model_type: str
    model_version: str
    horizon_days: int
    confidence_level: float
    accuracy_score: Optional[float] = None
    status: str
    created_at: str
    data_points_count: int


class ForecastListResponse(BaseModel):
    """List of forecast summaries."""
    forecasts: List[ForecastSummary]
    total: int


class ModelInfo(BaseModel):
    """Model information."""
    model_name: str
    version: str
    type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    training_info: Optional[Dict[str, Any]] = None
    is_fitted: bool
    description: Optional[str] = None


class EvaluationMetrics(BaseModel):
    """Model evaluation metrics."""
    mae: float
    rmse: float
    mape: Optional[float] = None
    test_samples: int
    mean_actual: Optional[float] = None
    mean_predicted: Optional[float] = None

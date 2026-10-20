"""
Route API schemas — request/response for route operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from sangam_api.core.enums import RouteStatus, RouteOptimizationObjective
from sangam_api.api.schemas.common import IDMixin, TimestampMixin


class RouteCreate(BaseModel):
    """Schema for creating a route."""
    name: str = Field(min_length=1, max_length=200, description="Human-readable route name")
    code: str = Field(min_length=2, max_length=30, description="Short unique identifier")
    origin_depot_id: UUID = Field(description="Starting depot")
    destination_depot_id: UUID = Field(description="Ending depot")
    status: RouteStatus = Field(RouteStatus.PLANNED)
    distance_km: float = Field(gt=0, description="Total distance in kilometers")
    estimated_duration_hours: float = Field(gt=0, description="Estimated travel time")
    optimization_objective: RouteOptimizationObjective = Field(
        RouteOptimizationObjective.BALANCED, description="What the route optimizes for"
    )
    waypoint_data: Optional[str] = Field(None, description="JSON array of intermediate stops")
    vehicle_type: Optional[str] = Field(None, max_length=50)
    max_weight_kg: float = Field(10000.0, gt=0, description="Maximum weight capacity")
    max_volume_m3: float = Field(50.0, gt=0, description="Maximum volume capacity")
    cost_per_km: float = Field(0.0, ge=0, description="Cost per kilometer")
    carbon_emission_factor: float = Field(0.0, ge=0, description="kg CO2 per km")


class RouteUpdate(BaseModel):
    """Schema for updating a route."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[RouteStatus] = None
    distance_km: Optional[float] = Field(None, gt=0)
    estimated_duration_hours: Optional[float] = Field(None, gt=0)
    optimization_objective: Optional[RouteOptimizationObjective] = None
    waypoint_data: Optional[str] = None
    vehicle_type: Optional[str] = Field(None, max_length=50)
    max_weight_kg: Optional[float] = Field(None, gt=0)
    max_volume_m3: Optional[float] = Field(None, gt=0)
    cost_per_km: Optional[float] = Field(None, ge=0)
    carbon_emission_factor: Optional[float] = Field(None, ge=0)


class RouteResponse(IDMixin, TimestampMixin):
    """Schema for route response."""
    name: str
    code: str
    origin_depot_id: UUID
    destination_depot_id: UUID
    status: str
    distance_km: float
    estimated_duration_hours: float
    optimization_objective: str
    waypoint_data: Optional[str] = None
    vehicle_type: Optional[str] = None
    max_weight_kg: float
    max_volume_m3: float
    cost_per_km: float
    carbon_emission_factor: float

    model_config = {"from_attributes": True}


class RouteListResponse(BaseModel):
    """Paginated list of routes."""
    items: list[RouteResponse]
    total: int
    skip: int
    limit: int

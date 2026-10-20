"""
Route Schemas

Pydantic models for route API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class RouteStatus(str, Enum):
    """Route status enumeration."""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISRUPTED = "disrupted"


class RouteType(str, Enum):
    """Route type enumeration."""
    PRIMARY = "primary"
    ALTERNATIVE = "alternative"
    EMERGENCY = "emergency"


class CoordinateSchema(BaseModel):
    """Geographic coordinate schema."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    
    class Config:
        from_attributes = True


class RouteSegmentSchema(BaseModel):
    """Route segment schema."""
    start: CoordinateSchema
    end: CoordinateSchema
    distance_km: float = Field(..., ge=0, description="Distance in kilometers")
    duration_minutes: float = Field(..., ge=0, description="Duration in minutes")
    waypoints: List[CoordinateSchema] = Field(default_factory=list, description="Intermediate waypoints")
    
    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    """Schema for creating a new route."""
    name: str = Field(..., min_length=1, max_length=200, description="Route name")
    code: str = Field(..., min_length=1, max_length=50, description="Route code")
    origin_depot_id: UUID = Field(..., description="Origin depot ID")
    destination_depot_id: UUID = Field(..., description="Destination depot ID")
    route_type: RouteType = Field(RouteType.PRIMARY, description="Route type")
    status: RouteStatus = Field(RouteStatus.PLANNED, description="Route status")
    vehicle_type: str = Field("truck", max_length=50, description="Vehicle type")
    max_weight_kg: float = Field(..., gt=0, description="Maximum weight capacity")
    max_volume_m3: float = Field(..., gt=0, description="Maximum volume capacity")
    waypoints: Optional[List[CoordinateSchema]] = Field(None, description="Route waypoints")
    notes: Optional[str] = Field(None, max_length=2000, description="Route notes")
    
    @field_validator('destination_depot_id')
    @classmethod
    def validate_different_depots(cls, v, info):
        """Ensure origin and destination are different."""
        if 'origin_depot_id' in info.data and v == info.data['origin_depot_id']:
            raise ValueError('Origin and destination depots must be different')
        return v


class RouteUpdate(BaseModel):
    """Schema for updating a route."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[RouteStatus] = None
    route_type: Optional[RouteType] = None
    vehicle_type: Optional[str] = Field(None, max_length=50)
    max_weight_kg: Optional[float] = Field(None, gt=0)
    max_volume_m3: Optional[float] = Field(None, gt=0)
    waypoints: Optional[List[CoordinateSchema]] = None
    disruption_reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class RouteResponse(BaseModel):
    """Complete route response."""
    id: UUID
    name: str
    code: str
    origin_depot_id: UUID
    destination_depot_id: UUID
    route_type: str
    status: str
    vehicle_type: str
    distance_km: Optional[float] = Field(None, description="Calculated distance (if available)")
    duration_minutes: Optional[float] = Field(None, description="Calculated duration (if available)")
    max_weight_kg: float
    max_volume_m3: float
    waypoints: Optional[List[CoordinateSchema]] = None
    disruption_reason: Optional[str] = None
    route_data: Optional[Dict[str, Any]] = Field(None, description="Full route calculation data")
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    origin_depot_name: Optional[str] = None
    destination_depot_name: Optional[str] = None
    is_calculated: bool = Field(default=False, description="Whether route has been calculated")
    
    class Config:
        from_attributes = True


class RouteListItem(BaseModel):
    """Route list item (summary)."""
    id: UUID
    name: str
    code: str
    origin_depot_id: UUID
    destination_depot_id: UUID
    route_type: str
    status: str
    distance_km: Optional[float] = None
    duration_minutes: Optional[float] = None
    is_disrupted: bool = Field(default=False)
    created_at: datetime
    
    class Config:
        from_attributes = True


class RouteListResponse(BaseModel):
    """Paginated list of routes."""
    items: List[RouteListItem]
    total: int
    skip: int
    limit: int


class RouteDetailResponse(RouteResponse):
    """Detailed route response with additional context."""
    segments: Optional[List[RouteSegmentSchema]] = None
    provider_info: Optional[Dict[str, Any]] = None


class RouteCalculationRequest(BaseModel):
    """Request for route calculation."""
    waypoints: Optional[List[CoordinateSchema]] = Field(None, description="Additional waypoints")
    vehicle_type: str = Field("truck", max_length=50, description="Vehicle type")
    recalculate: bool = Field(False, description="Force recalcation even if already calculated")


class RouteCalculationResponse(BaseModel):
    """Response from route calculation."""
    route_id: UUID
    total_distance_km: float
    total_duration_minutes: float
    segments: List[RouteSegmentSchema]
    provider: str
    metadata: Dict[str, Any]
    calculated_at: datetime


class RouteDisruptionRequest(BaseModel):
    """Request to mark route as disrupted."""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for disruption")
    severity: str = Field("medium", description="Severity: low, medium, high, critical")
    estimated_resolution_hours: Optional[float] = Field(None, ge=0, description="Estimated hours to resolve")


class RouteMatrixRequest(BaseModel):
    """Request for distance/duration matrix calculation."""
    depot_ids: List[UUID] = Field(..., min_length=2, description="List of depot IDs")
    vehicle_type: str = Field("truck", max_length=50, description="Vehicle type")


class RouteMatrixResponse(BaseModel):
    """Response with distance/duration matrix."""
    depot_ids: List[UUID]
    matrix: List[List[Dict[str, float]]]
    provider: str
    calculated_at: datetime


class RouteProviderInfo(BaseModel):
    """Information about the routing provider."""
    name: str
    version: str
    type: str
    capabilities: List[str]
    limitations: List[str]
    is_available: bool
    synthetic: bool = Field(default=False)

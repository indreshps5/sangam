"""
Shipment Schemas

Pydantic models for shipment API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ShipmentStatus(str, Enum):
    """Shipment status enumeration."""
    PLANNED = "planned"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ShipmentPriority(int, Enum):
    """Shipment priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


# ============================================================================
# Location Schema
# ============================================================================

class LocationData(BaseModel):
    """GPS location data for simulation."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: datetime
    accuracy_meters: Optional[float] = Field(None, ge=0)
    
    class Config:
        from_attributes = True


# ============================================================================
# Status History Schema
# ============================================================================

class StatusChange(BaseModel):
    """Single status change event."""
    status: ShipmentStatus
    timestamp: datetime
    changed_by: Optional[UUID] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Shipment Create/Update Schemas
# ============================================================================

class ShipmentCreate(BaseModel):
    """Schema for creating a new shipment."""
    origin_depot_id: UUID = Field(..., description="Origin depot ID")
    destination_depot_id: UUID = Field(..., description="Destination depot ID")
    route_id: Optional[UUID] = Field(None, description="Route ID")
    inventory_item_id: Optional[UUID] = Field(None, description="Inventory item ID (commodity)")
    weight_kg: float = Field(..., gt=0, description="Total weight in kilograms")
    volume_m3: float = Field(..., gt=0, description="Total volume in cubic meters")
    quantity: float = Field(1.0, gt=0, description="Number of units")
    priority: int = Field(3, ge=1, le=5, description="Priority level (1=critical, 5=minimal)")
    shipment_type: str = Field("standard", max_length=50, description="Shipment type")
    carrier_name: Optional[str] = Field(None, max_length=200, description="Carrier name")
    tracking_number: Optional[str] = Field(None, max_length=100, description="External tracking number")
    estimated_departure: Optional[datetime] = Field(None, description="Planned departure time")
    estimated_arrival: Optional[datetime] = Field(None, description="Planned arrival time")
    idempotency_key: Optional[str] = Field(None, max_length=100, description="Idempotency key")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")
    
    @field_validator('destination_depot_id')
    @classmethod
    def validate_different_depots(cls, v, info):
        """Ensure origin and destination are different."""
        if 'origin_depot_id' in info.data and v == info.data['origin_depot_id']:
            raise ValueError('Origin and destination depots must be different')
        return v


class ShipmentUpdate(BaseModel):
    """Schema for updating a shipment."""
    status: Optional[ShipmentStatus] = Field(None, description="New status")
    weight_kg: Optional[float] = Field(None, gt=0, description="Updated weight")
    volume_m3: Optional[float] = Field(None, gt=0, description="Updated volume")
    quantity: Optional[float] = Field(None, gt=0, description="Updated quantity")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Updated priority")
    carrier_name: Optional[str] = Field(None, max_length=200)
    tracking_number: Optional[str] = Field(None, max_length=100)
    estimated_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    delay_reason: Optional[str] = Field(None, max_length=500, description="Reason for delay")
    notes: Optional[str] = Field(None, max_length=2000)


class StatusUpdateRequest(BaseModel):
    """Schema for updating shipment status."""
    status: ShipmentStatus = Field(..., description="New status")
    notes: Optional[str] = Field(None, max_length=500, description="Status change notes")
    delay_reason: Optional[str] = Field(None, max_length=500, description="Reason for delay (if delayed)")
    changed_by: Optional[UUID] = Field(None, description="User who made the change")


class LocationUpdateRequest(BaseModel):
    """Schema for updating shipment location (GPS simulation)."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    accuracy_meters: Optional[float] = Field(None, ge=0, description="GPS accuracy")
    timestamp: Optional[datetime] = Field(None, description="Location timestamp")


# ============================================================================
# Shipment Response Schemas
# ============================================================================

class ShipmentResponse(BaseModel):
    """Complete shipment response."""
    id: UUID
    origin_depot_id: UUID
    destination_depot_id: UUID
    route_id: Optional[UUID] = None
    inventory_item_id: Optional[UUID] = None
    status: str
    weight_kg: float
    volume_m3: float
    quantity: float
    priority: int
    shipment_type: str
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_departure: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    status_history: Optional[List[StatusChange]] = None
    current_location: Optional[LocationData] = None
    delay_reason: Optional[str] = None
    idempotency_key: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_delayed: bool = Field(default=False, description="Whether shipment is delayed")
    delay_hours: Optional[float] = Field(None, description="Hours of delay")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Journey progress")
    
    class Config:
        from_attributes = True


class ShipmentListItem(BaseModel):
    """Shipment list item (summary)."""
    id: UUID
    origin_depot_id: UUID
    destination_depot_id: UUID
    status: str
    priority: int
    shipment_type: str
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    is_delayed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class ShipmentListResponse(BaseModel):
    """Paginated list of shipments."""
    items: List[ShipmentListItem]
    total: int
    skip: int
    limit: int


class ShipmentDetailResponse(ShipmentResponse):
    """Detailed shipment response with additional context."""
    origin_depot_name: Optional[str] = None
    destination_depot_name: Optional[str] = None
    route_name: Optional[str] = None
    inventory_item_name: Optional[str] = None
    inventory_item_sku: Optional[str] = None


# ============================================================================
# Shipment Statistics Schemas
# ============================================================================

class ShipmentStats(BaseModel):
    """Shipment statistics for dashboard."""
    total_shipments: int = Field(description="Total number of shipments")
    planned_count: int = Field(description="Shipments in planned status")
    dispatched_count: int = Field(description="Shipments dispatched")
    in_transit_count: int = Field(description="Shipments in transit")
    delayed_count: int = Field(description="Delayed shipments")
    delivered_count: int = Field(description="Delivered shipments")
    cancelled_count: int = Field(description="Cancelled shipments")
    average_delay_hours: Optional[float] = Field(None, description="Average delay in hours")
    on_time_delivery_rate: Optional[float] = Field(None, ge=0, le=100, description="On-time delivery percentage")


# ============================================================================
# Shipment Alert Schemas
# ============================================================================

class ShipmentAlert(BaseModel):
    """Shipment alert for overdue or at-risk shipments."""
    shipment_id: UUID
    tracking_number: Optional[str] = None
    status: str
    severity: str = Field(description="Alert severity: warning, critical")
    alert_type: str = Field(description="Type: overdue, at_risk, delayed")
    message: str
    estimated_arrival: Optional[datetime] = None
    hours_overdue: Optional[float] = None
    hours_at_risk: Optional[float] = None
    origin_depot_name: Optional[str] = None
    destination_depot_name: Optional[str] = None


class ShipmentAlertListResponse(BaseModel):
    """List of shipment alerts."""
    alerts: List[ShipmentAlert]
    total: int

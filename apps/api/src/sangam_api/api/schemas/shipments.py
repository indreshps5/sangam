"""
Shipment API schemas — request/response for shipment operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from sangam_api.core.enums import ShipmentStatus
from sangam_api.api.schemas.common import IDMixin, TimestampMixin


class ShipmentCreate(BaseModel):
    """Schema for creating a shipment."""
    origin_depot_id: UUID = Field(description="Origin depot")
    destination_depot_id: UUID = Field(description="Destination depot")
    route_id: Optional[UUID] = Field(None, description="Assigned route")
    status: ShipmentStatus = Field(ShipmentStatus.PENDING)
    weight_kg: float = Field(gt=0, description="Total weight in kilograms")
    volume_m3: float = Field(gt=0, description="Total volume in cubic meters")
    priority: int = Field(3, ge=1, le=5, description="Priority 1=critical, 5=minimal")
    shipment_type: str = Field("standard", max_length=50)
    carrier_name: Optional[str] = Field(None, max_length=200)
    tracking_number: Optional[str] = Field(None, max_length=100)
    estimated_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    notes: Optional[str] = None


class ShipmentUpdate(BaseModel):
    """Schema for updating a shipment."""
    status: Optional[ShipmentStatus] = None
    route_id: Optional[UUID] = None
    weight_kg: Optional[float] = Field(None, gt=0)
    volume_m3: Optional[float] = Field(None, gt=0)
    priority: Optional[int] = Field(None, ge=1, le=5)
    carrier_name: Optional[str] = Field(None, max_length=200)
    tracking_number: Optional[str] = Field(None, max_length=100)
    estimated_departure: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    notes: Optional[str] = None


class ShipmentResponse(IDMixin, TimestampMixin):
    """Schema for shipment response."""
    origin_depot_id: UUID
    destination_depot_id: UUID
    route_id: Optional[UUID] = None
    status: str
    weight_kg: float
    volume_m3: float
    priority: int
    shipment_type: str
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_departure: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ShipmentListResponse(BaseModel):
    """Paginated list of shipments."""
    items: list[ShipmentResponse]
    total: int
    skip: int
    limit: int

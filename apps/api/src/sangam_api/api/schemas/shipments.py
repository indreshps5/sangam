"""Shipment API schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ShipmentStatus(str, Enum):
    """Shipment lifecycle states."""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class ShipmentCreate(BaseModel):
    """Schema for creating/updating a shipment."""
    origin_warehouse_id: UUID
    destination_warehouse_id: UUID
    status: ShipmentStatus = ShipmentStatus.PENDING
    weight_kg: float = Field(gt=0, description="Weight in kilograms")
    volume_m3: float = Field(gt=0, description="Volume in cubic meters")
    priority: int = Field(ge=1, le=5, default=3, description="Priority 1=highest")
    estimated_arrival: Optional[datetime] = None
    notes: Optional[str] = None


class ShipmentResponse(BaseModel):
    """Schema for shipment response."""
    id: UUID
    origin_warehouse_id: UUID
    destination_warehouse_id: UUID
    status: ShipmentStatus
    weight_kg: float
    volume_m3: float
    priority: int
    estimated_arrival: Optional[datetime]
    actual_arrival: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ShipmentListResponse(BaseModel):
    """Paginated list of shipments."""
    items: list[ShipmentResponse]
    total: int
    skip: int
    limit: int

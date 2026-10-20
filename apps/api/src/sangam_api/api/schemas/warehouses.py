"""Warehouse API schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WarehouseCreate(BaseModel):
    """Schema for creating a warehouse."""
    name: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=2, max_length=20, description="Short warehouse code")
    region: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    capacity_units: int = Field(gt=0)
    address: Optional[str] = None


class WarehouseResponse(BaseModel):
    """Schema for warehouse response."""
    id: UUID
    name: str
    code: str
    region: str
    latitude: float
    longitude: float
    capacity_units: int
    current_utilization: float
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WarehouseListResponse(BaseModel):
    """Paginated list of warehouses."""
    items: list[WarehouseResponse]
    total: int
    skip: int
    limit: int

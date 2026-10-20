"""
Depot API schemas — request/response validation for depot operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from sangam_api.core.enums import DepotType, DepotStatus
from sangam_api.api.schemas.common import IDMixin, TimestampMixin


class DepotCreate(BaseModel):
    """Schema for creating a new depot."""
    name: str = Field(min_length=1, max_length=200, description="Human-readable facility name")
    code: str = Field(min_length=2, max_length=20, description="Short unique identifier (e.g., WH-MUM-001)")
    depot_type: DepotType = Field(description="Classification of facility")
    status: DepotStatus = Field(DepotStatus.ACTIVE, description="Operational status")
    region: str = Field(min_length=1, max_length=100, description="Geographic region")
    latitude: float = Field(ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    capacity_units: int = Field(gt=0, description="Maximum storage capacity")
    address: Optional[str] = Field(None, max_length=500, description="Physical address")
    contact_email: Optional[str] = Field(None, max_length=255, description="Primary contact email")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Primary contact phone")

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """Ensure code is uppercase and alphanumeric with hyphens."""
        v = v.upper().strip()
        if not all(c.isalnum() or c == "-" for c in v):
            raise ValueError("Code must contain only alphanumeric characters and hyphens")
        return v


class DepotUpdate(BaseModel):
    """Schema for updating a depot (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    depot_type: Optional[DepotType] = None
    status: Optional[DepotStatus] = None
    region: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    capacity_units: Optional[int] = Field(None, gt=0)
    current_utilization: Optional[float] = Field(None, ge=0.0, le=1.0)
    address: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)


class DepotResponse(IDMixin, TimestampMixin):
    """Schema for depot response."""
    name: str
    code: str
    depot_type: str
    status: str
    region: str
    latitude: float
    longitude: float
    capacity_units: int
    current_utilization: float
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    model_config = {"from_attributes": True}


class DepotListResponse(BaseModel):
    """Paginated list of depots."""
    items: list[DepotResponse]
    total: int
    skip: int
    limit: int

"""
Sensor and Alert API schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from sangam_api.core.enums import SensorType, AlertSeverity, AlertStatus
from sangam_api.api.schemas.common import IDMixin, TimestampMixin


# ─── SensorReading ───

class SensorReadingCreate(BaseModel):
    """Schema for creating a sensor reading."""
    device_id: str = Field(min_length=1, max_length=100, description="Unique sensor/device ID")
    depot_id: Optional[UUID] = Field(None, description="Depot where sensor is located")
    shipment_id: Optional[UUID] = Field(None, description="Shipment if sensor is in transit")
    sensor_type: SensorType = Field(description="Type of sensor")
    reading_value: float = Field(description="Numeric sensor value")
    unit: str = Field(min_length=1, max_length=20, description="Unit of measurement")
    reading_timestamp: datetime = Field(description="When the reading was taken")
    quality_flag: str = Field("good", max_length=20, description="Data quality indicator")
    raw_payload: Optional[str] = Field(None, description="JSON original payload")


class SensorReadingResponse(IDMixin, TimestampMixin):
    """Schema for sensor reading response."""
    device_id: str
    depot_id: Optional[UUID] = None
    shipment_id: Optional[UUID] = None
    sensor_type: str
    reading_value: float
    unit: str
    reading_timestamp: datetime
    quality_flag: str
    raw_payload: Optional[str] = None

    model_config = {"from_attributes": True}


class SensorReadingListResponse(BaseModel):
    """Paginated list of sensor readings."""
    items: list[SensorReadingResponse]
    total: int
    skip: int
    limit: int


# ─── Alert ───

class AlertCreate(BaseModel):
    """Schema for creating an alert."""
    title: str = Field(min_length=1, max_length=200, description="Short alert title")
    description: Optional[str] = Field(None, max_length=5000)
    severity: AlertSeverity = Field(description="Alert severity")
    status: AlertStatus = Field(AlertStatus.TRIGGERED)
    source_type: str = Field(min_length=1, max_length=50, description="What triggered the alert")
    source_id: Optional[UUID] = Field(None, description="ID of triggering entity")
    depot_id: Optional[UUID] = Field(None, description="Related depot")
    shipment_id: Optional[UUID] = Field(None, description="Related shipment")
    triggered_by: Optional[UUID] = Field(None, description="User or system that triggered")


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[UUID] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = Field(None, max_length=2000)


class AlertResponse(IDMixin, TimestampMixin):
    """Schema for alert response."""
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    source_type: str
    source_id: Optional[UUID] = None
    depot_id: Optional[UUID] = None
    shipment_id: Optional[UUID] = None
    triggered_by: Optional[UUID] = None
    acknowledged_by: Optional[UUID] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Paginated list of alerts."""
    items: list[AlertResponse]
    total: int
    skip: int
    limit: int

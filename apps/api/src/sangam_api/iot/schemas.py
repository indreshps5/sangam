"""
IoT Sensor Schemas

Pydantic schemas for sensor data validation and API contracts.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class SensorType(str, Enum):
    """Supported sensor types."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    LIGHT = "light"
    MOTION = "motion"
    GAS = "gas"
    VIBRATION = "vibration"
    POWER = "power"


class SensorUnit(str, Enum):
    """Supported measurement units."""
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    PERCENT = "percent"
    PASCAL = "pascal"
    LUX = "lux"
    BOOLEAN = "boolean"
    PPM = "ppm"  # parts per million
    G_FORCE = "g_force"
    WATT = "watt"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types."""
    THRESHOLD_HIGH = "threshold_high"
    THRESHOLD_LOW = "threshold_low"
    OFFLINE = "offline"
    MALFUNCTION = "malfunction"


# ============================================================================
# Sensor Message Schema (Version 1.0)
# ============================================================================

class SensorMessageV1(BaseModel):
    """
    Version 1.0 sensor message schema.
    
    This is the canonical schema for all sensor readings.
    All ingestion paths (MQTT, HTTP, simulator) must validate against this schema.
    """
    
    version: str = Field("1.0", description="Schema version")
    sensor_id: str = Field(..., min_length=1, max_length=100, description="Unique sensor identifier")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    value: float = Field(..., description="Measurement value")
    unit: SensorUnit = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(..., description="Timestamp of measurement (UTC)")
    
    # Optional context
    depot_id: Optional[str] = Field(None, description="Associated depot ID")
    shipment_id: Optional[str] = Field(None, description="Associated shipment ID")
    
    # Quality and metadata
    quality: Optional[str] = Field(None, max_length=20, description="Data quality indicator")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Ensure timestamp is not in the future and not too old."""
        now = datetime.utcnow()
        
        # Reject future timestamps (allow 1 minute clock skew)
        if v > now.replace(microsecond=0):
            raise ValueError("Timestamp cannot be in the future")
        
        # Reject very old timestamps (older than 30 days)
        max_age_days = 30
        if (now - v).days > max_age_days:
            raise ValueError(f"Timestamp is too old (max {max_age_days} days)")
        
        return v
    
    @model_validator(mode='after')
    def validate_sensor_type_unit_combination(self):
        """Validate that sensor type and unit are compatible."""
        valid_combinations = {
            SensorType.TEMPERATURE: [SensorUnit.CELSIUS, SensorUnit.FAHRENHEIT],
            SensorType.HUMIDITY: [SensorUnit.PERCENT],
            SensorType.PRESSURE: [SensorUnit.PASCAL],
            SensorType.LIGHT: [SensorUnit.LUX],
            SensorType.MOTION: [SensorUnit.BOOLEAN],
            SensorType.GAS: [SensorUnit.PPM],
            SensorType.VIBRATION: [SensorUnit.G_FORCE],
            SensorType.POWER: [SensorUnit.WATT],
        }
        
        allowed_units = valid_combinations.get(self.sensor_type, [])
        if self.unit not in allowed_units:
            raise ValueError(
                f"Unit '{self.unit}' is not valid for sensor type '{self.sensor_type}'. "
                f"Allowed units: {[u.value for u in allowed_units]}"
            )
        
        return self


# ============================================================================
# Sensor Management Schemas
# ============================================================================

class SensorCreate(BaseModel):
    """Schema for creating a new sensor."""
    sensor_id: str = Field(..., min_length=1, max_length=100, description="Unique sensor identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Human-readable sensor name")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    unit: SensorUnit = Field(..., description="Unit of measurement")
    
    # Associations
    depot_id: Optional[UUID] = Field(None, description="Associated depot ID")
    shipment_id: Optional[UUID] = Field(None, description="Associated shipment ID")
    
    # Thresholds
    min_threshold: Optional[float] = Field(None, description="Minimum threshold for alerts")
    max_threshold: Optional[float] = Field(None, description="Maximum threshold for alerts")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @model_validator(mode='after')
    def validate_thresholds(self):
        """Validate that min < max if both are provided."""
        if self.min_threshold is not None and self.max_threshold is not None:
            if self.min_threshold >= self.max_threshold:
                raise ValueError("min_threshold must be less than max_threshold")
        return self


class SensorUpdate(BaseModel):
    """Schema for updating a sensor."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class SensorResponse(BaseModel):
    """Response schema for sensor."""
    id: UUID
    sensor_id: str
    name: str
    sensor_type: str
    unit: str
    depot_id: Optional[UUID]
    shipment_id: Optional[UUID]
    min_threshold: Optional[float]
    max_threshold: Optional[float]
    is_active: bool
    last_seen_at: Optional[datetime]
    last_reading_value: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SensorListResponse(BaseModel):
    """List of sensors."""
    items: List[SensorResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# Sensor Reading Schemas
# ============================================================================

class SensorReadingResponse(BaseModel):
    """Response schema for sensor reading."""
    id: UUID
    sensor_id: UUID
    value: float
    unit: str
    timestamp: datetime
    quality: Optional[str]
    message_version: str
    received_at: datetime
    
    model_config = {"from_attributes": True}


class SensorReadingListResponse(BaseModel):
    """List of sensor readings."""
    items: List[SensorReadingResponse]
    total: int
    skip: int
    limit: int


class SensorReadingTrend(BaseModel):
    """Trend data point for charts."""
    timestamp: datetime
    value: float
    sensor_id: UUID


class SensorTrendResponse(BaseModel):
    """Trend data for a sensor."""
    sensor_id: UUID
    sensor_name: str
    sensor_type: str
    unit: str
    data_points: List[SensorReadingTrend]
    min_value: float
    max_value: float
    avg_value: float


# ============================================================================
# Sensor Alert Schemas
# ============================================================================

class SensorAlertResponse(BaseModel):
    """Response schema for sensor alert."""
    id: UUID
    sensor_id: UUID
    reading_id: Optional[UUID]
    alert_type: str
    severity: str
    message: str
    triggered_value: Optional[float]
    threshold_value: Optional[float]
    is_acknowledged: bool
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[UUID]
    triggered_at: datetime
    resolved_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class SensorAlertListResponse(BaseModel):
    """List of sensor alerts."""
    items: List[SensorAlertResponse]
    total: int
    skip: int
    limit: int


class AlertAcknowledgment(BaseModel):
    """Schema for acknowledging an alert."""
    acknowledged_by: UUID = Field(..., description="User acknowledging the alert")


# ============================================================================
# Ingestion Schemas
# ============================================================================

class IngestionResult(BaseModel):
    """Result of sensor data ingestion."""
    success: bool
    reading_id: Optional[UUID] = None
    alert_ids: List[UUID] = Field(default_factory=list)
    message: str
    error: Optional[str] = None


class BatchIngestionRequest(BaseModel):
    """Request for batch ingestion of sensor readings."""
    messages: List[SensorMessageV1] = Field(..., min_length=1, max_length=100)


class BatchIngestionResponse(BaseModel):
    """Response for batch ingestion."""
    total: int
    successful: int
    failed: int
    results: List[IngestionResult]


# ============================================================================
# Simulator Schemas
# ============================================================================

class SimulatorConfig(BaseModel):
    """Configuration for sensor simulator."""
    sensor_id: str = Field(..., description="Sensor ID to simulate")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    unit: SensorUnit = Field(..., description="Unit of measurement")
    
    # Simulation parameters
    base_value: float = Field(..., description="Base value for simulation")
    variance: float = Field(5.0, ge=0, description="Random variance")
    interval_seconds: int = Field(60, ge=1, le=3600, description="Interval between readings")
    
    # Optional context
    depot_id: Optional[str] = None
    shipment_id: Optional[str] = None
    
    # Duration
    duration_minutes: int = Field(60, ge=1, le=1440, description="How long to simulate")


class SimulatorStatus(BaseModel):
    """Status of a running simulator."""
    sensor_id: str
    is_running: bool
    readings_generated: int
    started_at: Optional[datetime]
    last_reading_at: Optional[datetime]


# ============================================================================
# MQTT Configuration Schemas
# ============================================================================

class MQTTConfig(BaseModel):
    """MQTT broker configuration (never exposed to frontend)."""
    broker_host: str
    broker_port: int = 1883
    use_tls: bool = False
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = "sangam_iot_worker"
    
    # Topics
    topic_prefix: str = "sangam/sensors"
    qos: int = Field(1, ge=0, le=2)
    
    # Connection settings
    keepalive: int = 60
    reconnect_delay: int = 5


class MQTTTopicInfo(BaseModel):
    """Information about MQTT topics (safe to expose)."""
    topic: str
    description: str
    example_payload: Dict[str, Any]
    qos: int

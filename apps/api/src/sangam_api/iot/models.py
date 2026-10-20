"""
IoT Sensor Models

Database models for sensors, readings, and alerts.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sangam_api.core.database import Base


class Sensor(Base):
    """
    Represents a physical or virtual sensor device.
    
    Sensors can be associated with a depot or shipment.
    """
    
    __tablename__ = "sensors"
    
    # Basic info
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    sensor_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # temperature, humidity, etc.
    
    # Associations
    depot_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    shipment_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shipments.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Configuration
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # celsius, percent, etc.
    min_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reading_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")
    alerts = relationship("SensorAlert", back_populates="sensor", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_sensors_depot_type', 'depot_id', 'sensor_type'),
        Index('ix_sensors_shipment_type', 'shipment_id', 'sensor_type'),
    )
    
    def __repr__(self) -> str:
        return f"<Sensor(id={self.id}, sensor_id={self.sensor_id}, type={self.sensor_type})>"


class SensorReading(Base):
    """
    Individual sensor reading with timestamp and measurement.
    
    Optimized for high-volume ingestion with time-based partitioning.
    """
    
    __tablename__ = "sensor_readings"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    sensor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sensors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Reading data
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Quality and metadata
    quality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # good, warning, error
    message_version: Mapped[str] = mapped_column(String(10), nullable=False, default="1.0")
    
    # Raw payload for debugging
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="readings")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_sensor_readings_sensor_timestamp', 'sensor_id', 'timestamp'),
        Index('ix_sensor_readings_timestamp_desc', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<SensorReading(id={self.id}, sensor_id={self.sensor_id}, value={self.value})>"


class SensorAlert(Base):
    """
    Threshold-based alerts triggered by sensor readings.
    """
    
    __tablename__ = "sensor_alerts"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    sensor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sensors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    reading_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sensor_readings.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Alert details
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # threshold_high, threshold_low, offline
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="warning")  # info, warning, critical
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Triggered values
    triggered_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="alerts")
    reading = relationship("SensorReading")
    
    # Indexes
    __table_args__ = (
        Index('ix_sensor_alerts_sensor_triggered', 'sensor_id', 'triggered_at'),
        Index('ix_sensor_alerts_active', 'is_acknowledged', 'triggered_at'),
    )
    
    def __repr__(self) -> str:
        return f"<SensorAlert(id={self.id}, type={self.alert_type}, severity={self.severity})>"

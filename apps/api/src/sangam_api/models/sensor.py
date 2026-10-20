"""
SensorReading — IoT sensor data from supply chain assets.
Alert — system-generated notifications and warnings.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from sangam_api.core.database import Base
from sangam_api.core.types import UUIDPrimaryKeyMixin, TimestampMixin


class SensorReading(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A single sensor reading from an IoT device.

    Canonical fields:
    - device_id: Unique sensor/device identifier
    - depot_id: FK to the depot where sensor is located (nullable for in-transit)
    - shipment_id: FK to shipment if sensor is on a moving asset
    - sensor_type: Type of sensor (temperature, humidity, GPS, etc.)
    - reading_value: Numeric sensor value
    - unit: Unit of measurement
    - reading_timestamp: When the reading was taken
    - quality_flag: Data quality indicator
    - raw_payload: Original sensor payload (JSON)
    """

    __tablename__ = "sensor_readings"

    __table_args__ = (
        CheckConstraint("reading_value IS NOT NULL", name="ck_sensor_reading_not_null"),
    )

    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    depot_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipment_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shipments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reading_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    reading_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    quality_flag: Mapped[str] = mapped_column(String(20), nullable=False, default="good", index=True)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON original payload")


class Alert(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    System-generated alert or notification.

    Canonical fields:
    - severity: Alert severity (info, warning, critical, emergency)
    - status: Current alert status
    - title: Short alert title
    - description: Detailed description
    - source_type: What triggered the alert (sensor, threshold, system, etc.)
    - source_id: ID of the triggering entity
    - depot_id: FK to related depot (nullable)
    - shipment_id: FK to related shipment (nullable)
    - triggered_by: User or system that triggered
    - acknowledged_by: User who acknowledged
    - acknowledged_at: When acknowledged
    - resolved_at: When resolved
    - resolution_notes: How it was resolved
    """

    __tablename__ = "alerts"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="triggered", index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    depot_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipment_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shipments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    triggered_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    acknowledged_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

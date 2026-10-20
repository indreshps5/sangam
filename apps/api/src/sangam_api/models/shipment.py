"""Shipment database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from sangam_api.core.database import Base


class ShipmentModel(Base):
    """SQLAlchemy model for shipments table."""

    __tablename__ = "shipments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    origin_warehouse_id: Mapped[UUID] = mapped_column(index=True)
    destination_warehouse_id: Mapped[UUID] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    weight_kg: Mapped[float] = mapped_column(Float)
    volume_m3: Mapped[float] = mapped_column(Float)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    estimated_arrival: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

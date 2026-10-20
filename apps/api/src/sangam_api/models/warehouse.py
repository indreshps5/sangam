"""Warehouse database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from sangam_api.core.database import Base


class WarehouseModel(Base):
    """SQLAlchemy model for warehouses table."""

    __tablename__ = "warehouses"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    region: Mapped[str] = mapped_column(String(100), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    capacity_units: Mapped[int] = mapped_column(Integer)
    current_utilization: Mapped[float] = mapped_column(Float, default=0.0)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

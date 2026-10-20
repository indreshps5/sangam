"""
Depot (canonical entity) — physical facility in the supply chain network.
Replaces the previous 'Warehouse' concept with a more comprehensive model.
"""

from uuid import UUID

from sqlalchemy import String, Float, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sangam_api.core.database import Base
from sangam_api.core.types import UUIDPrimaryKeyMixin, TimestampMixin


class Depot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A physical depot/facility in the logistics network.

    Canonical fields:
    - name: Human-readable facility name
    - code: Short unique identifier (e.g., "WH-MUM-001")
    - depot_type: Classification of facility
    - status: Operational status
    - region: Geographic region
    - latitude/longitude: GPS coordinates
    - capacity_units: Maximum storage capacity
    - current_utilization: Current usage ratio (0.0-1.0)
    - address: Physical address
    - contact_email: Primary contact email
    - contact_phone: Primary contact phone
    """

    __tablename__ = "depots"

    __table_args__ = (
        CheckConstraint("capacity_units > 0", name="ck_depots_capacity_positive"),
        CheckConstraint(
            "current_utilization >= 0.0 AND current_utilization <= 1.0",
            name="ck_depots_utilization_range",
        ),
        CheckConstraint(
            "latitude >= -90.0 AND latitude <= 90.0",
            name="ck_depots_latitude_range",
        ),
        CheckConstraint(
            "longitude >= -180.0 AND longitude <= 180.0",
            name="ck_depots_longitude_range",
        ),
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    depot_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    capacity_units: Mapped[int] = mapped_column(Integer, nullable=False)
    current_utilization: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        back_populates="depot", lazy="selectin"
    )
    outbound_shipments: Mapped[list["Shipment"]] = relationship(
        back_populates="origin_depot",
        foreign_keys="Shipment.origin_depot_id",
        lazy="selectin",
    )
    inbound_shipments: Mapped[list["Shipment"]] = relationship(
        back_populates="destination_depot",
        foreign_keys="Shipment.destination_depot_id",
        lazy="selectin",
    )

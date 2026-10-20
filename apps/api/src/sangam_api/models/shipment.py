"""
Shipment — goods in transit between depots.
Route — planned or active transportation path.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sangam_api.core.database import Base
from sangam_api.core.types import UUIDPrimaryKeyMixin, TimestampMixin


class Shipment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A shipment of goods between depots.

    Canonical fields:
    - origin_depot_id: FK to origin depot
    - destination_depot_id: FK to destination depot
    - route_id: Optional FK to assigned route
    - status: Current shipment status
    - weight_kg: Total weight in kilograms
    - volume_m3: Total volume in cubic meters
    - priority: Priority level (1=critical, 5=minimal)
    - shipment_type: Type of shipment (standard, express, etc.)
    - carrier_name: Name of the carrier
    - tracking_number: External tracking identifier
    - estimated_departure: Planned departure time
    - actual_departure: Actual departure time
    - estimated_arrival: Planned arrival time
    - actual_arrival: Actual arrival time
    - notes: Additional information
    """

    __tablename__ = "shipments"

    __table_args__ = (
        CheckConstraint("weight_kg > 0", name="ck_shipments_weight_positive"),
        CheckConstraint("volume_m3 > 0", name="ck_shipments_volume_positive"),
        CheckConstraint("priority >= 1 AND priority <= 5", name="ck_shipments_priority_range"),
    )

    origin_depot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    destination_depot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    route_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("routes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    volume_m3: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    shipment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    carrier_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    estimated_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    origin_depot: Mapped["Depot"] = relationship(
        back_populates="outbound_shipments",
        foreign_keys=[origin_depot_id],
        lazy="joined",
    )
    destination_depot: Mapped["Depot"] = relationship(
        back_populates="inbound_shipments",
        foreign_keys=[destination_depot_id],
        lazy="joined",
    )
    route: Mapped["Route | None"] = relationship(
        back_populates="shipments", lazy="joined"
    )


class Route(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A planned or active transportation route.

    Canonical fields:
    - name: Human-readable route name
    - code: Short unique identifier
    - origin_depot_id: Starting depot
    - destination_depot_id: Ending depot
    - status: Route status
    - distance_km: Total distance in kilometers
    - estimated_duration_hours: Estimated travel time
    - optimization_objective: What the route optimizes for
    - waypoint_data: JSON array of intermediate stops
    - vehicle_type: Type of vehicle for this route
    - max_weight_kg: Maximum weight capacity
    - max_volume_m3: Maximum volume capacity
    - cost_per_km: Cost per kilometer
    - carbon_emission_factor: CO2 emissions per km
    """

    __tablename__ = "routes"

    __table_args__ = (
        CheckConstraint("distance_km > 0", name="ck_routes_distance_positive"),
        CheckConstraint("estimated_duration_hours > 0", name="ck_routes_duration_positive"),
        CheckConstraint("max_weight_kg > 0", name="ck_routes_max_weight_positive"),
        CheckConstraint("max_volume_m3 > 0", name="ck_routes_max_volume_positive"),
        CheckConstraint("cost_per_km >= 0", name="ck_routes_cost_non_negative"),
        CheckConstraint("carbon_emission_factor >= 0", name="ck_routes_emission_non_negative"),
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    origin_depot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    destination_depot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    optimization_objective: Mapped[str] = mapped_column(String(50), nullable=False, default="balanced")
    waypoint_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON array of waypoints")
    vehicle_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    max_weight_kg: Mapped[float] = mapped_column(Float, nullable=False, default=10000.0)
    max_volume_m3: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    cost_per_km: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbon_emission_factor: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="kg CO2 per km")

    # Relationships
    shipments: Mapped[list["Shipment"]] = relationship(
        back_populates="route", lazy="selectin"
    )

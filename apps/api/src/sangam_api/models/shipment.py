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
    - inventory_item_id: Optional FK to inventory item (commodity)
    - status: Current shipment status
    - weight_kg: Total weight in kilograms
    - volume_m3: Total volume in cubic meters
    - quantity: Number of units (if tracking by count)
    - priority: Priority level (1=critical, 5=minimal)
    - shipment_type: Type of shipment (standard, express, etc.)
    - carrier_name: Name of the carrier
    - tracking_number: External tracking identifier
    - estimated_departure: Planned departure time
    - actual_departure: Actual departure time
    - estimated_arrival: Planned arrival time
    - actual_arrival: Actual arrival time
    - status_history: JSON array of status changes with timestamps
    - current_location: JSON object with lat/lng for GPS simulation
    - delay_reason: Reason for delay (if delayed)
    - idempotency_key: Unique key for idempotent operations
    - notes: Additional information
    """

    __tablename__ = "shipments"

    __table_args__ = (
        CheckConstraint("weight_kg > 0", name="ck_shipments_weight_positive"),
        CheckConstraint("volume_m3 > 0", name="ck_shipments_volume_positive"),
        CheckConstraint("priority >= 1 AND priority <= 5", name="ck_shipments_priority_range"),
        CheckConstraint("quantity > 0", name="ck_shipments_quantity_positive"),
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
    inventory_item_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="planned", index=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    volume_m3: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    shipment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    carrier_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    estimated_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status_history: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON array of status changes")
    current_location: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON object with lat/lng")
    delay_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
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
    inventory_item: Mapped["InventoryItem | None"] = relationship(
        lazy="joined"
    )


class Route(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A planned or active transportation route.

    Canonical fields:
    - name: Human-readable route name
    - code: Short unique identifier
    - origin_depot_id: Starting depot
    - destination_depot_id: Ending depot
    - route_type: Type of route (primary, alternative, emergency)
    - status: Route status (planned, active, completed, cancelled, disrupted)
    - distance_km: Total distance in kilometers (calculated, nullable)
    - estimated_duration_hours: Estimated travel time (calculated, nullable)
    - optimization_objective: What the route optimizes for
    - waypoint_data: JSON array of intermediate stops
    - route_data: JSON object with full route calculation data
    - vehicle_type: Type of vehicle for this route
    - max_weight_kg: Maximum weight capacity
    - max_volume_m3: Maximum volume capacity
    - cost_per_km: Cost per kilometer
    - carbon_emission_factor: CO2 emissions per km
    - disruption_reason: Reason for disruption (if disrupted)
    - disruption_severity: Severity of disruption
    - disruption_estimated_resolution: Estimated hours to resolve
    """

    __tablename__ = "routes"

    __table_args__ = (
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
    route_type: Mapped[str] = mapped_column(String(30), nullable=False, default="primary", index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Calculated distance")
    estimated_duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Calculated duration")
    optimization_objective: Mapped[str] = mapped_column(String(50), nullable=False, default="balanced")
    waypoint_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON array of waypoints")
    route_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON object with full route calculation")
    vehicle_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    max_weight_kg: Mapped[float] = mapped_column(Float, nullable=False, default=10000.0)
    max_volume_m3: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    cost_per_km: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbon_emission_factor: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="kg CO2 per km")
    disruption_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    disruption_severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    disruption_estimated_resolution: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Hours to resolve")

    # Relationships
    shipments: Mapped[list["Shipment"]] = relationship(
        back_populates="route", lazy="selectin"
    )

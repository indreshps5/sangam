"""
InventoryItem — stock-keeping unit at a depot.
InventoryTransaction — record of inventory movement.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Float, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sangam_api.core.database import Base
from sangam_api.core.types import UUIDPrimaryKeyMixin, TimestampMixin


class InventoryItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A stock-keeping unit at a specific depot.

    Canonical fields:
    - depot_id: FK to the depot where this item is stored
    - sku: Stock Keeping Unit code (unique per depot)
    - name: Item name
    - description: Detailed description
    - category: Product category
    - unit_of_measure: Standard unit (kg, m3, unit, pallet, etc.)
    - quantity_on_hand: Current available quantity
    - quantity_reserved: Quantity reserved for pending shipments
    - quantity_available: Computed (on_hand - reserved)
    - min_stock_level: Reorder threshold
    - max_stock_level: Maximum capacity allocation
    - unit_cost: Cost per unit in base currency
    - location_code: Bin/shelf location within depot
    - batch_number: Production batch identifier
    - expiry_date: Expiration date (for perishable goods)
    """

    __tablename__ = "inventory_items"

    __table_args__ = (
        CheckConstraint("quantity_on_hand >= 0", name="ck_inventory_on_hand_non_negative"),
        CheckConstraint("quantity_reserved >= 0", name="ck_inventory_reserved_non_negative"),
        CheckConstraint("min_stock_level >= 0", name="ck_inventory_min_stock_non_negative"),
        CheckConstraint("max_stock_level >= 0", name="ck_inventory_max_stock_non_negative"),
        CheckConstraint("unit_cost >= 0", name="ck_inventory_unit_cost_non_negative"),
    )

    depot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default="unit")
    quantity_on_hand: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_reserved: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_stock_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_stock_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD", comment="ISO 4217 currency code")
    location_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    depot: Mapped["Depot"] = relationship(back_populates="inventory_items", lazy="joined")
    transactions: Mapped[list["InventoryTransaction"]] = relationship(
        back_populates="inventory_item", lazy="selectin"
    )


class InventoryTransaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Record of an inventory movement or adjustment.

    Canonical fields:
    - inventory_item_id: FK to the affected inventory item
    - depot_id: FK to the depot (denormalized for query performance)
    - transaction_type: Type of movement (receipt, shipment, transfer, etc.)
    - quantity: Amount moved (positive = in, negative = out)
    - unit_of_measure: Unit for the quantity
    - reference_id: Optional reference to related entity (shipment ID, etc.)
    - reference_type: Type of reference entity
    - notes: Human-readable description
    - performed_by: User who performed the transaction
    - performed_at: When the transaction occurred
    """

    __tablename__ = "inventory_transactions"

    __table_args__ = (
        CheckConstraint("quantity != 0", name="ck_inv_transaction_quantity_non_zero"),
    )

    inventory_item_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    depot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default="unit")
    reference_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Relationships
    inventory_item: Mapped["InventoryItem"] = relationship(
        back_populates="transactions", lazy="joined"
    )

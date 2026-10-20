"""
Inventory API schemas — request/response for inventory items and transactions.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from sangam_api.core.enums import InventoryTransactionType
from sangam_api.api.schemas.common import IDMixin, TimestampMixin


# ─── InventoryItem ───

class InventoryItemCreate(BaseModel):
    """Schema for creating an inventory item."""
    depot_id: UUID = Field(description="Depot where item is stored")
    sku: str = Field(min_length=1, max_length=100, description="Stock Keeping Unit code")
    name: str = Field(min_length=1, max_length=200, description="Item name")
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    unit_of_measure: str = Field("unit", max_length=20, description="Standard unit (kg, m3, unit, pallet)")
    quantity_on_hand: float = Field(0.0, ge=0, description="Current available quantity")
    quantity_reserved: float = Field(0.0, ge=0, description="Quantity reserved for pending shipments")
    min_stock_level: float = Field(0.0, ge=0, description="Reorder threshold")
    max_stock_level: float = Field(0.0, ge=0, description="Maximum capacity allocation")
    unit_cost: float = Field(0.0, ge=0, description="Cost per unit in base currency")
    currency: str = Field("USD", min_length=3, max_length=3, description="ISO 4217 currency code")
    location_code: Optional[str] = Field(None, max_length=50, description="Bin/shelf location")
    batch_number: Optional[str] = Field(None, max_length=100)
    expiry_date: Optional[datetime] = None


class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    quantity_on_hand: Optional[float] = Field(None, ge=0)
    quantity_reserved: Optional[float] = Field(None, ge=0)
    min_stock_level: Optional[float] = Field(None, ge=0)
    max_stock_level: Optional[float] = Field(None, ge=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    location_code: Optional[str] = Field(None, max_length=50)
    batch_number: Optional[str] = Field(None, max_length=100)
    expiry_date: Optional[datetime] = None


class InventoryItemResponse(IDMixin, TimestampMixin):
    """Schema for inventory item response."""
    depot_id: UUID
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: str
    quantity_on_hand: float
    quantity_reserved: float
    quantity_available: float = Field(description="Computed: on_hand - reserved")
    min_stock_level: float
    max_stock_level: float
    unit_cost: float
    currency: str
    location_code: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_computed(cls, obj) -> "InventoryItemResponse":
        """Create response with computed quantity_available."""
        data = {
            "id": obj.id,
            "depot_id": obj.depot_id,
            "sku": obj.sku,
            "name": obj.name,
            "description": obj.description,
            "category": obj.category,
            "unit_of_measure": obj.unit_of_measure,
            "quantity_on_hand": obj.quantity_on_hand,
            "quantity_reserved": obj.quantity_reserved,
            "quantity_available": obj.quantity_on_hand - obj.quantity_reserved,
            "min_stock_level": obj.min_stock_level,
            "max_stock_level": obj.max_stock_level,
            "unit_cost": obj.unit_cost,
            "currency": obj.currency,
            "location_code": obj.location_code,
            "batch_number": obj.batch_number,
            "expiry_date": obj.expiry_date,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)


class InventoryItemListResponse(BaseModel):
    """Paginated list of inventory items."""
    items: list[InventoryItemResponse]
    total: int
    skip: int
    limit: int


# ─── InventoryTransaction ───

class InventoryTransactionCreate(BaseModel):
    """Schema for creating an inventory transaction."""
    inventory_item_id: UUID = Field(description="Affected inventory item")
    depot_id: UUID = Field(description="Depot where transaction occurred")
    transaction_type: InventoryTransactionType = Field(description="Type of movement")
    quantity: float = Field(description="Amount moved (positive=in, negative=out)")
    unit_of_measure: str = Field("unit", max_length=20)
    reference_id: Optional[UUID] = Field(None, description="Related entity ID")
    reference_type: Optional[str] = Field(None, max_length=50, description="Related entity type")
    notes: Optional[str] = Field(None, max_length=2000)
    performed_by: Optional[UUID] = Field(None, description="User who performed")
    performed_at: datetime = Field(description="When the transaction occurred")


class InventoryTransactionResponse(IDMixin, TimestampMixin):
    """Schema for inventory transaction response."""
    inventory_item_id: UUID
    depot_id: UUID
    transaction_type: str
    quantity: float
    unit_of_measure: str
    reference_id: Optional[UUID] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None
    performed_by: Optional[UUID] = None
    performed_at: datetime

    model_config = {"from_attributes": True}


class InventoryTransactionListResponse(BaseModel):
    """Paginated list of inventory transactions."""
    items: list[InventoryTransactionResponse]
    total: int
    skip: int
    limit: int

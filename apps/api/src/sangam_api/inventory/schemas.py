"""
Inventory Schemas

Pydantic models for inventory API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Inventory Item Schemas
# ============================================================================

class InventoryItemBase(BaseModel):
    """Base schema for inventory item fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Item name")
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit code")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    description: Optional[str] = Field(None, max_length=1000, description="Item description")
    unit_of_measure: str = Field("units", max_length=20, description="Unit of measurement")
    min_stock_level: float = Field(0.0, ge=0, description="Reorder threshold")
    max_stock_level: float = Field(0.0, ge=0, description="Maximum capacity")
    unit_cost: float = Field(0.0, ge=0, description="Cost per unit")
    currency: str = Field("USD", max_length=3, description="ISO 4217 currency code")
    location_code: Optional[str] = Field(None, max_length=50, description="Storage location")
    batch_number: Optional[str] = Field(None, max_length=100, description="Batch identifier")
    expiry_date: Optional[datetime] = Field(None, description="Expiration date")


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating a new inventory item."""
    depot_id: UUID = Field(..., description="Depot ID where item is stored")
    quantity_on_hand: float = Field(0.0, ge=0, description="Initial quantity")
    quantity_reserved: float = Field(0.0, ge=0, description="Initial reserved quantity")


class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    min_stock_level: Optional[float] = Field(None, ge=0)
    max_stock_level: Optional[float] = Field(None, ge=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    location_code: Optional[str] = Field(None, max_length=50)
    batch_number: Optional[str] = Field(None, max_length=100)
    expiry_date: Optional[datetime] = None


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response."""
    id: UUID
    depot_id: UUID
    quantity_on_hand: float
    quantity_reserved: float
    quantity_available: float = Field(description="Available stock (on_hand - reserved)")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InventoryItemListResponse(BaseModel):
    """Paginated list of inventory items."""
    items: List[InventoryItemResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# Inventory Transaction Schemas
# ============================================================================

class InventoryTransactionBase(BaseModel):
    """Base schema for transaction fields."""
    transaction_type: str = Field(..., description="Type: receipt, shipment, transfer, adjustment")
    quantity: float = Field(..., description="Quantity (positive for in, negative for out)")
    unit_of_measure: str = Field("units", max_length=20, description="Unit of measurement")
    notes: Optional[str] = Field(None, max_length=500, description="Transaction notes")
    reference_id: Optional[UUID] = Field(None, description="Reference entity ID")
    reference_type: Optional[str] = Field(None, max_length=50, description="Reference entity type")


class InventoryTransactionCreate(InventoryTransactionBase):
    """Schema for creating a new inventory transaction."""
    inventory_item_id: UUID = Field(..., description="Inventory item ID")
    performed_by: Optional[UUID] = Field(None, description="User who performed transaction")


class InventoryTransactionResponse(InventoryTransactionBase):
    """Schema for transaction response."""
    id: UUID
    inventory_item_id: UUID
    depot_id: UUID
    performed_by: Optional[UUID]
    performed_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InventoryTransactionListResponse(BaseModel):
    """Paginated list of inventory transactions."""
    items: List[InventoryTransactionResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# Stock Adjustment Schemas
# ============================================================================

class StockAdjustmentRequest(BaseModel):
    """Schema for adjusting stock levels."""
    adjustment_type: str = Field(..., description="Type: receipt, consumption, adjustment")
    quantity: float = Field(..., description="Quantity to adjust")
    notes: Optional[str] = Field(None, max_length=500, description="Adjustment notes")
    performed_by: Optional[UUID] = Field(None, description="User performing adjustment")


class StockTransferRequest(BaseModel):
    """Schema for transferring stock between depots."""
    source_depot_id: UUID = Field(..., description="Source depot ID")
    destination_depot_id: UUID = Field(..., description="Destination depot ID")
    quantity: float = Field(..., gt=0, description="Quantity to transfer")
    notes: Optional[str] = Field(None, max_length=500, description="Transfer notes")
    performed_by: Optional[UUID] = Field(None, description="User performing transfer")


# ============================================================================
# Low Stock Alert Schemas
# ============================================================================

class LowStockAlertResponse(BaseModel):
    """Schema for low stock alert."""
    inventory_item_id: UUID
    item_name: str
    sku: str
    depot_id: UUID
    depot_name: str
    quantity_available: float
    min_stock_level: float
    shortage: float = Field(description="Amount below minimum stock level")
    unit_of_measure: str
    
    model_config = ConfigDict(from_attributes=True)


class LowStockAlertListResponse(BaseModel):
    """List of low stock alerts."""
    alerts: List[LowStockAlertResponse]
    total: int


# ============================================================================
# Inventory Statistics Schemas
# ============================================================================

class InventoryStatsResponse(BaseModel):
    """Inventory statistics for dashboard KPIs."""
    total_items: int = Field(description="Total number of inventory items")
    total_value: float = Field(description="Total inventory value")
    low_stock_count: int = Field(description="Number of items below minimum stock")
    out_of_stock_count: int = Field(description="Number of items with zero available stock")
    total_quantity: float = Field(description="Total quantity across all items")
    currency: str = Field(description="Currency for values")

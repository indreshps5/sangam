"""
Inventory Service

Business logic for inventory management operations.
Follows SOLID principles with single responsibility and dependency inversion.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.inventory.models import InventoryItem, InventoryTransaction
from sangam_api.inventory.repository import (
    InventoryItemRepositoryInterface,
    InventoryTransactionRepositoryInterface,
)
from sangam_api.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryTransactionCreate,
    StockAdjustmentRequest,
    StockTransferRequest,
    InventoryItemResponse,
    InventoryTransactionResponse,
    LowStockAlertResponse,
    InventoryStatsResponse,
)
from sangam_api.core.exceptions import (
    NotFoundException,
    ValidationException,
    ConflictException,
)


class InventoryService:
    """
    Service for inventory management operations.
    
    Responsibilities:
    - Inventory item CRUD operations
    - Stock adjustments and transfers
    - Transaction recording
    - Low stock alerts
    - Inventory statistics
    """
    
    def __init__(
        self,
        item_repo: InventoryItemRepositoryInterface,
        transaction_repo: InventoryTransactionRepositoryInterface,
    ):
        self.item_repo = item_repo
        self.transaction_repo = transaction_repo
    
    # ========================================================================
    # Inventory Item Operations
    # ========================================================================
    
    async def get_item(self, item_id: UUID) -> InventoryItemResponse:
        """Get inventory item by ID."""
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("Inventory item", str(item_id))
        
        return self._to_item_response(item)
    
    async def list_items(
        self,
        depot_id: Optional[UUID] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> tuple[List[InventoryItemResponse], int]:
        """List inventory items with filtering and pagination."""
        items = await self.item_repo.list_items(
            depot_id=depot_id,
            category=category,
            search=search,
            low_stock_only=low_stock_only,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        total = await self.item_repo.count_items(
            depot_id=depot_id,
            category=category,
            search=search,
            low_stock_only=low_stock_only
        )
        
        return [self._to_item_response(item) for item in items], total
    
    async def create_item(self, data: InventoryItemCreate) -> InventoryItemResponse:
        """Create a new inventory item."""
        # Check for duplicate SKU in depot
        existing = await self.item_repo.get_by_sku(data.depot_id, data.sku)
        if existing:
            raise ConflictException(
                f"Item with SKU '{data.sku}' already exists in this depot"
            )
        
        # Validate quantities
        if data.quantity_reserved > data.quantity_on_hand:
            raise ValidationException(
                "Reserved quantity cannot exceed quantity on hand"
            )
        
        # Create item
        item = InventoryItem(
            depot_id=data.depot_id,
            name=data.name,
            sku=data.sku,
            category=data.category,
            description=data.description,
            unit_of_measure=data.unit_of_measure,
            quantity_on_hand=data.quantity_on_hand,
            quantity_reserved=data.quantity_reserved,
            min_stock_level=data.min_stock_level,
            max_stock_level=data.max_stock_level,
            unit_cost=data.unit_cost,
            currency=data.currency,
            location_code=data.location_code,
            batch_number=data.batch_number,
            expiry_date=data.expiry_date,
        )
        
        created_item = await self.item_repo.create(item)
        return self._to_item_response(created_item)
    
    async def update_item(
        self,
        item_id: UUID,
        data: InventoryItemUpdate
    ) -> InventoryItemResponse:
        """Update an inventory item."""
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("Inventory item", str(item_id))
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.updated_at = datetime.now(timezone.utc)
        
        updated_item = await self.item_repo.update(item)
        return self._to_item_response(updated_item)
    
    async def delete_item(self, item_id: UUID) -> bool:
        """Delete an inventory item."""
        return await self.item_repo.delete(item_id)
    
    # ========================================================================
    # Stock Adjustment Operations
    # ========================================================================
    
    async def adjust_stock(
        self,
        item_id: UUID,
        adjustment: StockAdjustmentRequest
    ) -> InventoryTransactionResponse:
        """
        Adjust stock levels for an inventory item.
        
        adjustment_type:
        - receipt: Add stock (quantity must be positive)
        - consumption: Remove stock (quantity must be positive, will be negated)
        - adjustment: Direct adjustment (quantity can be positive or negative)
        """
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("Inventory item", str(item_id))
        
        # Validate adjustment type and quantity
        if adjustment.adjustment_type == "receipt":
            if adjustment.quantity <= 0:
                raise ValidationException("Receipt quantity must be positive")
            quantity_change = adjustment.quantity
            
        elif adjustment.adjustment_type == "consumption":
            if adjustment.quantity <= 0:
                raise ValidationException("Consumption quantity must be positive")
            quantity_change = -adjustment.quantity
            
        elif adjustment.adjustment_type == "adjustment":
            quantity_change = adjustment.quantity
            
        else:
            raise ValidationException(
                f"Invalid adjustment type: {adjustment.adjustment_type}"
            )
        
        # Calculate new quantity
        new_quantity = item.quantity_on_hand + quantity_change
        
        # Prevent negative stock
        if new_quantity < 0:
            raise ValidationException(
                f"Insufficient stock. Current: {item.quantity_on_hand}, "
                f"Requested: {abs(quantity_change)}"
            )
        
        # Update item quantity
        item.quantity_on_hand = new_quantity
        item.updated_at = datetime.now(timezone.utc)
        await self.item_repo.update(item)
        
        # Create transaction record
        transaction = InventoryTransaction(
            inventory_item_id=item_id,
            depot_id=item.depot_id,
            transaction_type=adjustment.adjustment_type,
            quantity=quantity_change,
            unit_of_measure=item.unit_of_measure,
            notes=adjustment.notes,
            performed_by=adjustment.performed_by,
            performed_at=datetime.now(timezone.utc),
        )
        
        created_transaction = await self.transaction_repo.create(transaction)
        return self._to_transaction_response(created_transaction)
    
    async def transfer_stock(
        self,
        source_item_id: UUID,
        transfer: StockTransferRequest
    ) -> tuple[InventoryTransactionResponse, InventoryTransactionResponse]:
        """
        Transfer stock from one depot to another.
        
        Creates two transactions:
        1. Consumption at source depot
        2. Receipt at destination depot
        """
        # Validate source item
        source_item = await self.item_repo.get_by_id(source_item_id)
        if not source_item:
            raise NotFoundException("Source inventory item", str(source_item_id))
        
        # Validate source depot
        if source_item.depot_id != transfer.source_depot_id:
            raise ValidationException(
                "Source item does not belong to specified source depot"
            )
        
        # Validate quantity
        if transfer.quantity <= 0:
            raise ValidationException("Transfer quantity must be positive")
        
        # Check available stock
        available = source_item.quantity_on_hand - source_item.quantity_reserved
        if available < transfer.quantity:
            raise ValidationException(
                f"Insufficient available stock. Available: {available}, "
                f"Requested: {transfer.quantity}"
            )
        
        # Check if destination item exists
        dest_item = await self.item_repo.get_by_sku(
            transfer.destination_depot_id,
            source_item.sku
        )
        
        if not dest_item:
            raise ValidationException(
                f"Item with SKU '{source_item.sku}' does not exist in destination depot. "
                "Please create the item first."
            )
        
        # Perform transfer in a single transaction
        now = datetime.now(timezone.utc)
        
        # Update source item
        source_item.quantity_on_hand -= transfer.quantity
        source_item.updated_at = now
        await self.item_repo.update(source_item)
        
        # Update destination item
        dest_item.quantity_on_hand += transfer.quantity
        dest_item.updated_at = now
        await self.item_repo.update(dest_item)
        
        # Create source transaction (consumption)
        source_transaction = InventoryTransaction(
            inventory_item_id=source_item_id,
            depot_id=transfer.source_depot_id,
            transaction_type="transfer",
            quantity=-transfer.quantity,
            unit_of_measure=source_item.unit_of_measure,
            notes=f"Transfer to depot {transfer.destination_depot_id}. {transfer.notes or ''}",
            performed_by=transfer.performed_by,
            performed_at=now,
            reference_id=dest_item.id,
            reference_type="inventory_item"
        )
        
        # Create destination transaction (receipt)
        dest_transaction = InventoryTransaction(
            inventory_item_id=dest_item.id,
            depot_id=transfer.destination_depot_id,
            transaction_type="transfer",
            quantity=transfer.quantity,
            unit_of_measure=dest_item.unit_of_measure,
            notes=f"Transfer from depot {transfer.source_depot_id}. {transfer.notes or ''}",
            performed_by=transfer.performed_by,
            performed_at=now,
            reference_id=source_item_id,
            reference_type="inventory_item"
        )
        
        created_source = await self.transaction_repo.create(source_transaction)
        created_dest = await self.transaction_repo.create(dest_transaction)
        
        return (
            self._to_transaction_response(created_source),
            self._to_transaction_response(created_dest)
        )
    
    # ========================================================================
    # Transaction Operations
    # ========================================================================
    
    async def get_transaction(self, transaction_id: UUID) -> InventoryTransactionResponse:
        """Get transaction by ID."""
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundException("Inventory transaction", str(transaction_id))
        
        return self._to_transaction_response(transaction)
    
    async def list_transactions(
        self,
        inventory_item_id: Optional[UUID] = None,
        depot_id: Optional[UUID] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "performed_at",
        sort_order: str = "desc"
    ) -> tuple[List[InventoryTransactionResponse], int]:
        """List transactions with filtering and pagination."""
        transactions = await self.transaction_repo.list_transactions(
            inventory_item_id=inventory_item_id,
            depot_id=depot_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        total = await self.transaction_repo.count_transactions(
            inventory_item_id=inventory_item_id,
            depot_id=depot_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return [self._to_transaction_response(t) for t in transactions], total
    
    # ========================================================================
    # Alert Operations
    # ========================================================================
    
    async def get_low_stock_alerts(
        self,
        depot_id: Optional[UUID] = None
    ) -> tuple[List[LowStockAlertResponse], int]:
        """Get items below minimum stock level."""
        items = await self.item_repo.get_low_stock_items(depot_id)
        
        alerts = []
        for item in items:
            available = item.quantity_on_hand - item.quantity_reserved
            shortage = item.min_stock_level - available
            
            alert = LowStockAlertResponse(
                inventory_item_id=item.id,
                item_name=item.name,
                sku=item.sku,
                depot_id=item.depot_id,
                depot_name=item.depot.name if item.depot else "Unknown",
                quantity_available=available,
                min_stock_level=item.min_stock_level,
                shortage=shortage,
                unit_of_measure=item.unit_of_measure
            )
            alerts.append(alert)
        
        return alerts, len(alerts)
    
    # ========================================================================
    # Statistics Operations
    # ========================================================================
    
    async def get_inventory_stats(
        self,
        depot_id: Optional[UUID] = None
    ) -> InventoryStatsResponse:
        """Get inventory statistics for dashboard KPIs."""
        # Get all items (or filtered by depot)
        items, total = await self.list_items(depot_id=depot_id, limit=10000)
        
        # Calculate statistics
        total_items = total
        total_quantity = sum(item.quantity_on_hand for item in items)
        total_value = sum(
            item.quantity_on_hand * item.unit_cost for item in items
        )
        
        # Count low stock items
        low_stock_count = sum(
            1 for item in items
            if item.min_stock_level > 0 and
            (item.quantity_on_hand - item.quantity_reserved) < item.min_stock_level
        )
        
        # Count out of stock items
        out_of_stock_count = sum(
            1 for item in items
            if (item.quantity_on_hand - item.quantity_reserved) <= 0
        )
        
        # Get currency from first item or default to USD
        currency = items[0].currency if items else "USD"
        
        return InventoryStatsResponse(
            total_items=total_items,
            total_value=total_value,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            total_quantity=total_quantity,
            currency=currency
        )
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _to_item_response(self, item: InventoryItem) -> InventoryItemResponse:
        """Convert InventoryItem model to response schema."""
        return InventoryItemResponse(
            id=item.id,
            depot_id=item.depot_id,
            name=item.name,
            sku=item.sku,
            category=item.category,
            description=item.description,
            unit_of_measure=item.unit_of_measure,
            quantity_on_hand=item.quantity_on_hand,
            quantity_reserved=item.quantity_reserved,
            quantity_available=item.quantity_on_hand - item.quantity_reserved,
            min_stock_level=item.min_stock_level,
            max_stock_level=item.max_stock_level,
            unit_cost=item.unit_cost,
            currency=item.currency,
            location_code=item.location_code,
            batch_number=item.batch_number,
            expiry_date=item.expiry_date,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
    
    def _to_transaction_response(
        self,
        transaction: InventoryTransaction
    ) -> InventoryTransactionResponse:
        """Convert InventoryTransaction model to response schema."""
        return InventoryTransactionResponse(
            id=transaction.id,
            inventory_item_id=transaction.inventory_item_id,
            depot_id=transaction.depot_id,
            transaction_type=transaction.transaction_type,
            quantity=transaction.quantity,
            unit_of_measure=transaction.unit_of_measure,
            notes=transaction.notes,
            reference_id=transaction.reference_id,
            reference_type=transaction.reference_type,
            performed_by=transaction.performed_by,
            performed_at=transaction.performed_at,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )

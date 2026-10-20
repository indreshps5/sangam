"""
Inventory Repository

Repository interfaces and implementations for inventory data access.
Follows SOLID principles with dependency inversion.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sangam_api.inventory.models import InventoryItem, InventoryTransaction
from sangam_api.models.depot import Depot


# ============================================================================
# Repository Interfaces
# ============================================================================

class InventoryItemRepositoryInterface:
    """Interface for inventory item data access."""
    
    async def get_by_id(self, item_id: UUID) -> Optional[InventoryItem]:
        """Get inventory item by ID."""
        raise NotImplementedError
    
    async def get_by_sku(self, depot_id: UUID, sku: str) -> Optional[InventoryItem]:
        """Get inventory item by SKU within a depot."""
        raise NotImplementedError
    
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
    ) -> List[InventoryItem]:
        """List inventory items with filtering and pagination."""
        raise NotImplementedError
    
    async def count_items(
        self,
        depot_id: Optional[UUID] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        low_stock_only: bool = False
    ) -> int:
        """Count inventory items with filtering."""
        raise NotImplementedError
    
    async def create(self, item: InventoryItem) -> InventoryItem:
        """Create a new inventory item."""
        raise NotImplementedError
    
    async def update(self, item: InventoryItem) -> InventoryItem:
        """Update an inventory item."""
        raise NotImplementedError
    
    async def delete(self, item_id: UUID) -> bool:
        """Delete an inventory item."""
        raise NotImplementedError
    
    async def get_low_stock_items(self, depot_id: Optional[UUID] = None) -> List[InventoryItem]:
        """Get items below minimum stock level."""
        raise NotImplementedError


class InventoryTransactionRepositoryInterface:
    """Interface for inventory transaction data access."""
    
    async def get_by_id(self, transaction_id: UUID) -> Optional[InventoryTransaction]:
        """Get transaction by ID."""
        raise NotImplementedError
    
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
    ) -> List[InventoryTransaction]:
        """List transactions with filtering and pagination."""
        raise NotImplementedError
    
    async def count_transactions(
        self,
        inventory_item_id: Optional[UUID] = None,
        depot_id: Optional[UUID] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count transactions with filtering."""
        raise NotImplementedError
    
    async def create(self, transaction: InventoryTransaction) -> InventoryTransaction:
        """Create a new transaction."""
        raise NotImplementedError


# ============================================================================
# Repository Implementations
# ============================================================================

class InventoryItemRepository(InventoryItemRepositoryInterface):
    """SQLAlchemy implementation of inventory item repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, item_id: UUID) -> Optional[InventoryItem]:
        """Get inventory item by ID."""
        result = await self.session.execute(
            select(InventoryItem)
            .options(selectinload(InventoryItem.depot))
            .where(InventoryItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, depot_id: UUID, sku: str) -> Optional[InventoryItem]:
        """Get inventory item by SKU within a depot."""
        result = await self.session.execute(
            select(InventoryItem)
            .options(selectinload(InventoryItem.depot))
            .where(
                and_(
                    InventoryItem.depot_id == depot_id,
                    InventoryItem.sku == sku
                )
            )
        )
        return result.scalar_one_or_none()
    
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
    ) -> List[InventoryItem]:
        """List inventory items with filtering and pagination."""
        query = select(InventoryItem).options(selectinload(InventoryItem.depot))
        
        # Apply filters
        if depot_id:
            query = query.where(InventoryItem.depot_id == depot_id)
        
        if category:
            query = query.where(InventoryItem.category == category)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    InventoryItem.name.ilike(search_pattern),
                    InventoryItem.sku.ilike(search_pattern),
                    InventoryItem.description.ilike(search_pattern)
                )
            )
        
        if low_stock_only:
            query = query.where(
                and_(
                    InventoryItem.min_stock_level > 0,
                    (InventoryItem.quantity_on_hand - InventoryItem.quantity_reserved) < InventoryItem.min_stock_level
                )
            )
        
        # Apply sorting
        sort_column = getattr(InventoryItem, sort_by, InventoryItem.name)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_items(
        self,
        depot_id: Optional[UUID] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        low_stock_only: bool = False
    ) -> int:
        """Count inventory items with filtering."""
        query = select(func.count(InventoryItem.id))
        
        # Apply filters
        if depot_id:
            query = query.where(InventoryItem.depot_id == depot_id)
        
        if category:
            query = query.where(InventoryItem.category == category)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    InventoryItem.name.ilike(search_pattern),
                    InventoryItem.sku.ilike(search_pattern),
                    InventoryItem.description.ilike(search_pattern)
                )
            )
        
        if low_stock_only:
            query = query.where(
                and_(
                    InventoryItem.min_stock_level > 0,
                    (InventoryItem.quantity_on_hand - InventoryItem.quantity_reserved) < InventoryItem.min_stock_level
                )
            )
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, item: InventoryItem) -> InventoryItem:
        """Create a new inventory item."""
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item
    
    async def update(self, item: InventoryItem) -> InventoryItem:
        """Update an inventory item."""
        await self.session.flush()
        await self.session.refresh(item)
        return item
    
    async def delete(self, item_id: UUID) -> bool:
        """Delete an inventory item."""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        await self.session.delete(item)
        await self.session.flush()
        return True
    
    async def get_low_stock_items(self, depot_id: Optional[UUID] = None) -> List[InventoryItem]:
        """Get items below minimum stock level."""
        query = (
            select(InventoryItem)
            .options(selectinload(InventoryItem.depot))
            .where(
                and_(
                    InventoryItem.min_stock_level > 0,
                    (InventoryItem.quantity_on_hand - InventoryItem.quantity_reserved) < InventoryItem.min_stock_level
                )
            )
        )
        
        if depot_id:
            query = query.where(InventoryItem.depot_id == depot_id)
        
        query = query.order_by(
            (InventoryItem.quantity_on_hand - InventoryItem.quantity_reserved - InventoryItem.min_stock_level).asc()
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())


class InventoryTransactionRepository(InventoryTransactionRepositoryInterface):
    """SQLAlchemy implementation of inventory transaction repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, transaction_id: UUID) -> Optional[InventoryTransaction]:
        """Get transaction by ID."""
        result = await self.session.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
    
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
    ) -> List[InventoryTransaction]:
        """List transactions with filtering and pagination."""
        query = select(InventoryTransaction)
        
        # Apply filters
        if inventory_item_id:
            query = query.where(InventoryTransaction.inventory_item_id == inventory_item_id)
        
        if depot_id:
            query = query.where(InventoryTransaction.depot_id == depot_id)
        
        if transaction_type:
            query = query.where(InventoryTransaction.transaction_type == transaction_type)
        
        if start_date:
            query = query.where(InventoryTransaction.performed_at >= start_date)
        
        if end_date:
            query = query.where(InventoryTransaction.performed_at <= end_date)
        
        # Apply sorting
        sort_column = getattr(InventoryTransaction, sort_by, InventoryTransaction.performed_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_transactions(
        self,
        inventory_item_id: Optional[UUID] = None,
        depot_id: Optional[UUID] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count transactions with filtering."""
        query = select(func.count(InventoryTransaction.id))
        
        # Apply filters
        if inventory_item_id:
            query = query.where(InventoryTransaction.inventory_item_id == inventory_item_id)
        
        if depot_id:
            query = query.where(InventoryTransaction.depot_id == depot_id)
        
        if transaction_type:
            query = query.where(InventoryTransaction.transaction_type == transaction_type)
        
        if start_date:
            query = query.where(InventoryTransaction.performed_at >= start_date)
        
        if end_date:
            query = query.where(InventoryTransaction.performed_at <= end_date)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, transaction: InventoryTransaction) -> InventoryTransaction:
        """Create a new transaction."""
        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction

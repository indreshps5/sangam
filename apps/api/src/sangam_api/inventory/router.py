"""
Inventory Router

API endpoints for inventory management operations.
Thin controller layer that delegates to service.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db_session
from sangam_api.core.auth import get_current_user
from sangam_api.models.user import User
from sangam_api.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryItemListResponse,
    InventoryTransactionCreate,
    InventoryTransactionResponse,
    InventoryTransactionListResponse,
    StockAdjustmentRequest,
    StockTransferRequest,
    LowStockAlertListResponse,
    InventoryStatsResponse,
)
from sangam_api.inventory.repository import (
    InventoryItemRepository,
    InventoryTransactionRepository,
)
from sangam_api.inventory.service import InventoryService


router = APIRouter(prefix="/inventory", tags=["inventory"])


# ============================================================================
# Dependency Injection
# ============================================================================

def get_inventory_service(
    session: AsyncSession = Depends(get_db_session)
) -> InventoryService:
    """Create inventory service with repository dependencies."""
    item_repo = InventoryItemRepository(session)
    transaction_repo = InventoryTransactionRepository(session)
    return InventoryService(item_repo, transaction_repo)


# ============================================================================
# Inventory Item Endpoints
# ============================================================================

@router.get("/items", response_model=InventoryItemListResponse)
async def list_inventory_items(
    depot_id: Optional[UUID] = Query(None, description="Filter by depot ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name, SKU, description"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """
    List inventory items with filtering, search, and pagination.
    
    Supports filtering by depot, category, and low stock status.
    Search works across name, SKU, and description fields.
    """
    items, total = await service.list_items(
        depot_id=depot_id,
        category=category,
        search=search,
        low_stock_only=low_stock_only,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return InventoryItemListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """Get a specific inventory item by ID."""
    return await service.get_item(item_id)


@router.post(
    "/items",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_inventory_item(
    data: InventoryItemCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new inventory item.
    
    Validates SKU uniqueness within depot and quantity constraints.
    """
    return await service.create_item(data)


@router.put("/items/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: UUID,
    data: InventoryItemUpdate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """Update an existing inventory item."""
    return await service.update_item(item_id, data)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """Delete an inventory item."""
    deleted = await service.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )


# ============================================================================
# Stock Adjustment Endpoints
# ============================================================================

@router.post(
    "/items/{item_id}/adjust",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def adjust_stock(
    item_id: UUID,
    adjustment: StockAdjustmentRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """
    Adjust stock levels for an inventory item.
    
    Adjustment types:
    - receipt: Add stock (quantity must be positive)
    - consumption: Remove stock (quantity must be positive)
    - adjustment: Direct adjustment (quantity can be positive or negative)
    
    Prevents negative stock levels.
    """
    # Set performed_by to current user if not specified
    if not adjustment.performed_by:
        adjustment.performed_by = current_user.id
    
    return await service.adjust_stock(item_id, adjustment)


@router.post(
    "/items/{item_id}/transfer",
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def transfer_stock(
    item_id: UUID,
    transfer: StockTransferRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """
    Transfer stock from one depot to another.
    
    Creates two transactions:
    1. Consumption at source depot
    2. Receipt at destination depot
    
    Validates available stock and destination item existence.
    """
    # Set performed_by to current user if not specified
    if not transfer.performed_by:
        transfer.performed_by = current_user.id
    
    source_transaction, dest_transaction = await service.transfer_stock(
        item_id, transfer
    )
    
    return {
        "source_transaction": source_transaction,
        "destination_transaction": dest_transaction
    }


# ============================================================================
# Transaction Endpoints
# ============================================================================

@router.get("/transactions", response_model=InventoryTransactionListResponse)
async def list_transactions(
    inventory_item_id: Optional[UUID] = Query(None, description="Filter by item ID"),
    depot_id: Optional[UUID] = Query(None, description="Filter by depot ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum transactions to return"),
    sort_by: str = Query("performed_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """
    List inventory transactions with filtering and pagination.
    
    Supports filtering by item, depot, transaction type, and date range.
    """
    transactions, total = await service.list_transactions(
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
    
    return InventoryTransactionListResponse(
        items=transactions,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/transactions/{transaction_id}",
    response_model=InventoryTransactionResponse
)
async def get_transaction(
    transaction_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """Get a specific transaction by ID."""
    return await service.get_transaction(transaction_id)


# ============================================================================
# Alert Endpoints
# ============================================================================

@router.get("/alerts/low-stock", response_model=LowStockAlertListResponse)
async def get_low_stock_alerts(
    depot_id: Optional[UUID] = Query(None, description="Filter by depot ID"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get items below minimum stock level.
    
    Returns alerts with shortage calculations for reordering.
    """
    alerts, total = await service.get_low_stock_alerts(depot_id)
    
    return LowStockAlertListResponse(
        alerts=alerts,
        total=total
    )


# ============================================================================
# Statistics Endpoints
# ============================================================================

@router.get("/stats", response_model=InventoryStatsResponse)
async def get_inventory_stats(
    depot_id: Optional[UUID] = Query(None, description="Filter by depot ID"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory statistics for dashboard KPIs.
    
    Returns:
    - Total items count
    - Total inventory value
    - Low stock count
    - Out of stock count
    - Total quantity
    """
    return await service.get_inventory_stats(depot_id)

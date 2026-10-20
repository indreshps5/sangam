"""
Warehouse routes - thin controllers delegating to application services.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db_session
from sangam_api.api.schemas.warehouses import (
    WarehouseCreate,
    WarehouseResponse,
    WarehouseListResponse,
)
from sangam_api.services.warehouse_service import WarehouseService
from sangam_api.repositories.warehouse_repository import WarehouseRepository

router = APIRouter()


def get_warehouse_service(
    db: AsyncSession = Depends(get_db_session),
) -> WarehouseService:
    """Dependency injection for WarehouseService."""
    repository = WarehouseRepository(db)
    return WarehouseService(repository)


@router.get("/", response_model=WarehouseListResponse)
async def list_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    region: Optional[str] = Query(None),
    service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseListResponse:
    """List warehouses with optional region filter."""
    return await service.list_warehouses(skip=skip, limit=limit, region=region)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: UUID,
    service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseResponse:
    """Get a single warehouse by ID."""
    return await service.get_warehouse(warehouse_id)


@router.post("/", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(
    payload: WarehouseCreate,
    service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseResponse:
    """Create a new warehouse."""
    return await service.create_warehouse(payload)

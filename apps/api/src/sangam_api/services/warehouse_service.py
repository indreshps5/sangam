"""
Warehouse Application Service.
Contains business logic for warehouse operations.
"""

from typing import Optional
from uuid import UUID

from sangam_api.api.schemas.warehouses import (
    WarehouseCreate,
    WarehouseResponse,
    WarehouseListResponse,
)
from sangam_api.repositories.interfaces import WarehouseRepositoryInterface
from sangam_api.core.exceptions import NotFoundException
from sangam_api.core.logging import get_logger

logger = get_logger(__name__)


class WarehouseService:
    """Application service for warehouse operations."""

    def __init__(self, repository: WarehouseRepositoryInterface):
        self._repository = repository

    async def list_warehouses(
        self,
        skip: int = 0,
        limit: int = 20,
        region: Optional[str] = None,
    ) -> WarehouseListResponse:
        """List warehouses with optional region filter."""
        items = await self._repository.list(skip=skip, limit=limit, region=region)
        total = await self._repository.count(region=region)
        return WarehouseListResponse(items=items, total=total, skip=skip, limit=limit)

    async def get_warehouse(self, warehouse_id: UUID) -> WarehouseResponse:
        """Get a single warehouse by ID."""
        warehouse = await self._repository.get_by_id(warehouse_id)
        if not warehouse:
            raise NotFoundException("Warehouse", str(warehouse_id))
        return warehouse

    async def create_warehouse(self, payload: WarehouseCreate) -> WarehouseResponse:
        """Create a new warehouse."""
        logger.info("creating_warehouse", name=payload.name, code=payload.code)
        return await self._repository.create(payload)

"""
Depot Application Service.
Contains business logic for depot operations.
"""

from typing import Optional
from uuid import UUID

from sangam_api.api.schemas.depots import (
    DepotCreate,
    DepotUpdate,
    DepotResponse,
    DepotListResponse,
)
from sangam_api.repositories.interfaces import DepotRepositoryInterface
from sangam_api.core.exceptions import NotFoundException, ConflictException
from sangam_api.core.logging import get_logger

logger = get_logger(__name__)


class DepotService:
    """
    Application service for depot operations.
    Orchestrates business rules and delegates persistence to repository.
    """

    def __init__(self, repository: DepotRepositoryInterface):
        self._repository = repository

    async def list_depots(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        region: Optional[str] = None,
        depot_type: Optional[str] = None,
    ) -> DepotListResponse:
        """List depots with pagination and filters."""
        items = await self._repository.list(
            skip=skip, limit=limit, status=status, region=region, depot_type=depot_type
        )
        total = await self._repository.count(status=status, region=region, depot_type=depot_type)
        return DepotListResponse(items=items, total=total, skip=skip, limit=limit)

    async def get_depot(self, depot_id: UUID) -> DepotResponse:
        """Get a single depot by ID."""
        depot = await self._repository.get_by_id(depot_id)
        if not depot:
            raise NotFoundException("Depot", str(depot_id))
        return depot

    async def create_depot(self, payload: DepotCreate) -> DepotResponse:
        """Create a new depot with business validation."""
        # Check for duplicate code
        existing = await self._repository.get_by_code(payload.code)
        if existing:
            raise ConflictException(f"Depot with code '{payload.code}' already exists")

        logger.info("creating_depot", name=payload.name, code=payload.code)
        return await self._repository.create(payload)

    async def update_depot(self, depot_id: UUID, payload: DepotUpdate) -> DepotResponse:
        """Update an existing depot."""
        existing = await self._repository.get_by_id(depot_id)
        if not existing:
            raise NotFoundException("Depot", str(depot_id))
        result = await self._repository.update(depot_id, payload)
        if not result:
            raise NotFoundException("Depot", str(depot_id))
        return result

    async def delete_depot(self, depot_id: UUID) -> None:
        """Delete a depot."""
        existing = await self._repository.get_by_id(depot_id)
        if not existing:
            raise NotFoundException("Depot", str(depot_id))
        deleted = await self._repository.delete(depot_id)
        if not deleted:
            raise NotFoundException("Depot", str(depot_id))
        logger.info("deleted_depot", depot_id=str(depot_id))

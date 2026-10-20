"""
Shipment Application Service.
Contains business logic for shipment operations.
Depends on repository interface (dependency inversion).
"""

from uuid import UUID

from sangam_api.api.schemas.shipments import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentListResponse,
)
from sangam_api.repositories.interfaces import ShipmentRepositoryInterface
from sangam_api.core.exceptions import NotFoundException
from sangam_api.core.logging import get_logger

logger = get_logger(__name__)


class ShipmentService:
    """
    Application service for shipment operations.
    Orchestrates business rules and delegates persistence to repository.
    """

    def __init__(self, repository: ShipmentRepositoryInterface):
        self._repository = repository

    async def list_shipments(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
    ) -> ShipmentListResponse:
        """List shipments with pagination."""
        items = await self._repository.list(skip=skip, limit=limit, status=status)
        total = await self._repository.count(status=status)
        return ShipmentListResponse(items=items, total=total, skip=skip, limit=limit)

    async def get_shipment(self, shipment_id: UUID) -> ShipmentResponse:
        """Get a single shipment by ID."""
        shipment = await self._repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment", str(shipment_id))
        return shipment

    async def create_shipment(self, payload: ShipmentCreate) -> ShipmentResponse:
        """Create a new shipment with business validation."""
        logger.info("creating_shipment", origin=str(payload.origin_warehouse_id))
        return await self._repository.create(payload)

    async def update_shipment(
        self, shipment_id: UUID, payload: ShipmentCreate
    ) -> ShipmentResponse:
        """Update an existing shipment."""
        existing = await self._repository.get_by_id(shipment_id)
        if not existing:
            raise NotFoundException("Shipment", str(shipment_id))
        return await self._repository.update(shipment_id, payload)

    async def delete_shipment(self, shipment_id: UUID) -> None:
        """Delete a shipment."""
        existing = await self._repository.get_by_id(shipment_id)
        if not existing:
            raise NotFoundException("Shipment", str(shipment_id))
        await self._repository.delete(shipment_id)
        logger.info("deleted_shipment", shipment_id=str(shipment_id))

"""
Repository interfaces (abstractions).
Following Dependency Inversion Principle - services depend on these interfaces,
not on concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sangam_api.api.schemas.shipments import ShipmentCreate, ShipmentResponse
from sangam_api.api.schemas.warehouses import WarehouseCreate, WarehouseResponse


class ShipmentRepositoryInterface(ABC):
    """Interface for shipment persistence operations."""

    @abstractmethod
    async def list(
        self, skip: int = 0, limit: int = 20, status: Optional[str] = None
    ) -> list[ShipmentResponse]:
        """List shipments with pagination and optional filter."""
        ...

    @abstractmethod
    async def count(self, status: Optional[str] = None) -> int:
        """Count shipments with optional filter."""
        ...

    @abstractmethod
    async def get_by_id(self, shipment_id: UUID) -> Optional[ShipmentResponse]:
        """Get a shipment by its ID."""
        ...

    @abstractmethod
    async def create(self, payload: ShipmentCreate) -> ShipmentResponse:
        """Create a new shipment."""
        ...

    @abstractmethod
    async def update(
        self, shipment_id: UUID, payload: ShipmentCreate
    ) -> ShipmentResponse:
        """Update an existing shipment."""
        ...

    @abstractmethod
    async def delete(self, shipment_id: UUID) -> None:
        """Delete a shipment by ID."""
        ...


class WarehouseRepositoryInterface(ABC):
    """Interface for warehouse persistence operations."""

    @abstractmethod
    async def list(
        self, skip: int = 0, limit: int = 20, region: Optional[str] = None
    ) -> list[WarehouseResponse]:
        """List warehouses with pagination and optional region filter."""
        ...

    @abstractmethod
    async def count(self, region: Optional[str] = None) -> int:
        """Count warehouses with optional region filter."""
        ...

    @abstractmethod
    async def get_by_id(self, warehouse_id: UUID) -> Optional[WarehouseResponse]:
        """Get a warehouse by its ID."""
        ...

    @abstractmethod
    async def create(self, payload: WarehouseCreate) -> WarehouseResponse:
        """Create a new warehouse."""
        ...

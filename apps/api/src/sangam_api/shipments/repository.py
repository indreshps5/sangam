"""
Shipment Repository Interfaces

Abstract interfaces for shipment data access following SOLID principles.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sangam_api.models.shipment import Shipment
from sangam_api.shipments.schemas import ShipmentCreate, ShipmentUpdate


class ShipmentRepositoryInterface:
    """Interface for shipment data access operations."""
    
    async def get_by_id(self, shipment_id: UUID) -> Optional[Shipment]:
        """Get shipment by ID."""
        raise NotImplementedError
    
    async def get_by_tracking_number(self, tracking_number: str) -> Optional[Shipment]:
        """Get shipment by tracking number."""
        raise NotImplementedError
    
    async def get_by_idempotency_key(self, key: str) -> Optional[Shipment]:
        """Get shipment by idempotency key."""
        raise NotImplementedError
    
    async def list_shipments(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        priority: Optional[int] = None,
        is_delayed: Optional[bool] = None
    ) -> List[Shipment]:
        """List shipments with filtering."""
        raise NotImplementedError
    
    async def count_shipments(
        self,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        priority: Optional[int] = None,
        is_delayed: Optional[bool] = None
    ) -> int:
        """Count shipments with filtering."""
        raise NotImplementedError
    
    async def create(self,  ShipmentCreate) -> Shipment:
        """Create a new shipment."""
        raise NotImplementedError
    
    async def update(self, shipment_id: UUID,  ShipmentUpdate) -> Optional[Shipment]:
        """Update an existing shipment."""
        raise NotImplementedError
    
    async def update_status(
        self,
        shipment_id: UUID,
        status: str,
        changed_by: Optional[UUID] = None,
        notes: Optional[str] = None,
        delay_reason: Optional[str] = None
    ) -> Optional[Shipment]:
        """Update shipment status with history tracking."""
        raise NotImplementedError
    
    async def update_location(
        self,
        shipment_id: UUID,
        latitude: float,
        longitude: float,
        accuracy_meters: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> Optional[Shipment]:
        """Update shipment GPS location."""
        raise NotImplementedError
    
    async def get_delayed_shipments(self) -> List[Shipment]:
        """Get all delayed shipments."""
        raise NotImplementedError
    
    async def get_overdue_shipments(self, threshold_hours: float = 24.0) -> List[Shipment]:
        """Get shipments that are overdue (past estimated arrival)."""
        raise NotImplementedError
    
    async def get_shipments_by_status(self, status: str) -> List[Shipment]:
        """Get all shipments with a specific status."""
        raise NotImplementedError
    
    async def get_statistics(self) -> dict:
        """Get shipment statistics."""
        raise NotImplementedError

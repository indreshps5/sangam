"""
Route Repository Interface

Abstract interface for route data access.
"""

from typing import Optional, List
from uuid import UUID

from sangam_api.models.shipment import Route
from sangam_api.routes.schemas import RouteCreate, RouteUpdate


class RouteRepositoryInterface:
    """Interface for route data access operations."""
    
    async def get_by_id(self, route_id: UUID) -> Optional[Route]:
        """Get route by ID."""
        raise NotImplementedError
    
    async def get_by_code(self, code: str) -> Optional[Route]:
        """Get route by code."""
        raise NotImplementedError
    
    async def list_routes(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        route_type: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        is_disrupted: Optional[bool] = None
    ) -> List[Route]:
        """List routes with filtering."""
        raise NotImplementedError
    
    async def count_routes(
        self,
        status: Optional[str] = None,
        route_type: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        is_disrupted: Optional[bool] = None
    ) -> int:
        """Count routes with filtering."""
        raise NotImplementedError
    
    async def create(self,  RouteCreate) -> Route:
        """Create a new route."""
        raise NotImplementedError
    
    async def update(self, route_id: UUID,  RouteUpdate) -> Optional[Route]:
        """Update an existing route."""
        raise NotImplementedError
    
    async def update_calculation(
        self,
        route_id: UUID,
        distance_km: float,
        duration_minutes: float,
        route_data: str
    ) -> Optional[Route]:
        """Update route with calculation results."""
        raise NotImplementedError
    
    async def mark_disrupted(
        self,
        route_id: UUID,
        reason: str,
        severity: str,
        estimated_resolution_hours: Optional[float] = None
    ) -> Optional[Route]:
        """Mark route as disrupted."""
        raise NotImplementedError
    
    async def clear_disruption(self, route_id: UUID) -> Optional[Route]:
        """Clear disruption status."""
        raise NotImplementedError
    
    async def get_routes_by_depot(self, depot_id: UUID) -> List[Route]:
        """Get all routes involving a depot (origin or destination)."""
        raise NotImplementedError
    
    async def get_disrupted_routes(self) -> List[Route]:
        """Get all disrupted routes."""
        raise NotImplementedError

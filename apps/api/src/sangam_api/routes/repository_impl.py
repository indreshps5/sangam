"""
Route Repository Implementation

SQLAlchemy implementation of route repository interface.
"""

import json
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sangam_api.models.shipment import Route
from sangam_api.routes.repository import RouteRepositoryInterface
from sangam_api.routes.schemas import RouteCreate, RouteUpdate


class RouteRepository(RouteRepositoryInterface):
    """SQLAlchemy implementation of route repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, route_id: UUID) -> Optional[Route]:
        """Get route by ID."""
        result = await self.session.execute(
            select(Route)
            .options(
                selectinload(Route.origin_depot),
                selectinload(Route.destination_depot)
            )
            .where(Route.id == route_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Route]:
        """Get route by code."""
        result = await self.session.execute(
            select(Route).where(Route.code == code)
        )
        return result.scalar_one_or_none()
    
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
        query = select(Route).options(
            selectinload(Route.origin_depot),
            selectinload(Route.destination_depot)
        )
        
        # Apply filters
        if status:
            query = query.where(Route.status == status)
        
        if route_type:
            query = query.where(Route.route_type == route_type)
        
        if origin_depot_id:
            query = query.where(Route.origin_depot_id == origin_depot_id)
        
        if destination_depot_id:
            query = query.where(Route.destination_depot_id == destination_depot_id)
        
        if is_disrupted is not None:
            if is_disrupted:
                query = query.where(Route.status == "disrupted")
            else:
                query = query.where(Route.status != "disrupted")
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Order by created_at desc
        query = query.order_by(Route.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_routes(
        self,
        status: Optional[str] = None,
        route_type: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        is_disrupted: Optional[bool] = None
    ) -> int:
        """Count routes with filtering."""
        query = select(func.count(Route.id))
        
        # Apply filters (same as list_routes)
        if status:
            query = query.where(Route.status == status)
        
        if route_type:
            query = query.where(Route.route_type == route_type)
        
        if origin_depot_id:
            query = query.where(Route.origin_depot_id == origin_depot_id)
        
        if destination_depot_id:
            query = query.where(Route.destination_depot_id == destination_depot_id)
        
        if is_disrupted is not None:
            if is_disrupted:
                query = query.where(Route.status == "disrupted")
            else:
                query = query.where(Route.status != "disrupted")
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self,  RouteCreate) -> Route:
        """Create a new route."""
        # Convert waypoints to JSON
        waypoint_json = None
        if data.waypoints:
            waypoint_json = json.dumps([
                {"lat": wp.latitude, "lng": wp.longitude}
                for wp in data.waypoints
            ])
        
        route = Route(
            name=data.name,
            code=data.code,
            origin_depot_id=data.origin_depot_id,
            destination_depot_id=data.destination_depot_id,
            route_type=data.route_type.value,
            status=data.status.value,
            vehicle_type=data.vehicle_type,
            max_weight_kg=data.max_weight_kg,
            max_volume_m3=data.max_volume_m3,
            waypoint_data=waypoint_json,
            notes=data.notes
        )
        
        self.session.add(route)
        await self.session.flush()
        await self.session.refresh(route)
        
        return route
    
    async def update(self, route_id: UUID,  RouteUpdate) -> Optional[Route]:
        """Update an existing route."""
        route = await self.get_by_id(route_id)
        if not route:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "waypoints" and value is not None:
                # Convert waypoints to JSON
                route.waypoint_data = json.dumps([
                    {"lat": wp["latitude"], "lng": wp["longitude"]}
                    for wp in value
                ])
            elif hasattr(route, field):
                # Handle enum values
                if hasattr(value, "value"):
                    value = value.value
                setattr(route, field, value)
        
        route.updated_at = datetime.now(timezone.utc)
        
        await self.session.flush()
        await self.session.refresh(route)
        
        return route
    
    async def update_calculation(
        self,
        route_id: UUID,
        distance_km: float,
        duration_minutes: float,
        route_data: str
    ) -> Optional[Route]:
        """Update route with calculation results."""
        route = await self.get_by_id(route_id)
        if not route:
            return None
        
        route.distance_km = distance_km
        route.estimated_duration_hours = duration_minutes / 60.0  # Convert to hours
        route.route_data = route_data
        route.updated_at = datetime.now(timezone.utc)
        
        await self.session.flush()
        await self.session.refresh(route)
        
        return route
    
    async def mark_disrupted(
        self,
        route_id: UUID,
        reason: str,
        severity: str,
        estimated_resolution_hours: Optional[float] = None
    ) -> Optional[Route]:
        """Mark route as disrupted."""
        route = await self.get_by_id(route_id)
        if not route:
            return None
        
        route.status = "disrupted"
        route.disruption_reason = reason
        route.disruption_severity = severity
        route.disruption_estimated_resolution = estimated_resolution_hours
        route.updated_at = datetime.now(timezone.utc)
        
        await self.session.flush()
        await self.session.refresh(route)
        
        return route
    
    async def clear_disruption(self, route_id: UUID) -> Optional[Route]:
        """Clear disruption status."""
        route = await self.get_by_id(route_id)
        if not route:
            return None
        
        route.status = "active"
        route.disruption_reason = None
        route.disruption_severity = None
        route.disruption_estimated_resolution = None
        route.updated_at = datetime.now(timezone.utc)
        
        await self.session.flush()
        await self.session.refresh(route)
        
        return route
    
    async def get_routes_by_depot(self, depot_id: UUID) -> List[Route]:
        """Get all routes involving a depot (origin or destination)."""
        result = await self.session.execute(
            select(Route)
            .options(
                selectinload(Route.origin_depot),
                selectinload(Route.destination_depot)
            )
            .where(
                or_(
                    Route.origin_depot_id == depot_id,
                    Route.destination_depot_id == depot_id
                )
            )
            .order_by(Route.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_disrupted_routes(self) -> List[Route]:
        """Get all disrupted routes."""
        result = await self.session.execute(
            select(Route)
            .options(
                selectinload(Route.origin_depot),
                selectinload(Route.destination_depot)
            )
            .where(Route.status == "disrupted")
            .order_by(Route.created_at.desc())
        )
        return list(result.scalars().all())

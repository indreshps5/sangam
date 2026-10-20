"""
Route Service

Business logic for route management with provider integration.
"""

import json
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.models.shipment import Route, Depot
from sangam_api.routes.repository import RouteRepositoryInterface
from sangam_api.routes.provider import RouteProvider, Coordinate, RouteResult
from sangam_api.routes.schemas import (
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    RouteListItem,
    RouteListResponse,
    RouteDetailResponse,
    RouteCalculationRequest,
    RouteCalculationResponse,
    RouteDisruptionRequest,
    RouteMatrixRequest,
    RouteMatrixResponse,
    RouteProviderInfo,
    RouteSegmentSchema,
    CoordinateSchema
)
from sangam_api.core.exceptions import (
    NotFoundException,
    ValidationException,
    ConflictException
)


class RouteService:
    """Service for route management operations."""
    
    def __init__(
        self,
        repository: RouteRepositoryInterface,
        route_provider: RouteProvider,
        db: AsyncSession
    ):
        self.repository = repository
        self.route_provider = route_provider
        self.db = db
    
    async def get_route(self, route_id: UUID) -> RouteDetailResponse:
        """Get route by ID with full details."""
        route = await self.repository.get_by_id(route_id)
        if not route:
            raise NotFoundException("Route", str(route_id))
        
        return await self._to_detail_response(route)
    
    async def get_route_by_code(self, code: str) -> RouteDetailResponse:
        """Get route by code."""
        route = await self.repository.get_by_code(code)
        if not route:
            raise NotFoundException("Route", code)
        
        return await self._to_detail_response(route)
    
    async def list_routes(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        route_type: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        is_disrupted: Optional[bool] = None
    ) -> RouteListResponse:
        """List routes with filtering and pagination."""
        routes = await self.repository.list_routes(
            skip=skip,
            limit=limit,
            status=status,
            route_type=route_type,
            origin_depot_id=origin_depot_id,
            destination_depot_id=destination_depot_id,
            is_disrupted=is_disrupted
        )
        
        total = await self.repository.count_routes(
            status=status,
            route_type=route_type,
            origin_depot_id=origin_depot_id,
            destination_depot_id=destination_depot_id,
            is_disrupted=is_disrupted
        )
        
        items = [self._to_list_item(r) for r in routes]
        
        return RouteListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def create_route(self,  RouteCreate) -> RouteResponse:
        """Create a new route."""
        # Check for duplicate code
        existing = await self.repository.get_by_code(data.code)
        if existing:
            raise ConflictException(f"Route with code '{data.code}' already exists")
        
        # Validate depots exist
        await self._validate_depots(data.origin_depot_id, data.destination_depot_id)
        
        # Create route
        route = await self.repository.create(data)
        
        return self._to_response(route)
    
    async def update_route(
        self,
        route_id: UUID,
         RouteUpdate
    ) -> RouteResponse:
        """Update route details."""
        route = await self.repository.get_by_id(route_id)
        if not route:
            raise NotFoundException("Route", str(route_id))
        
        # Prevent updates to completed/cancelled routes
        if route.status in ["completed", "cancelled"]:
            raise ValidationException(
                f"Cannot update route in {route.status} status"
            )
        
        # Update route
        updated = await self.repository.update(route_id, data)
        if not updated:
            raise NotFoundException("Route", str(route_id))
        
        return self._to_response(updated)
    
    async def calculate_route(
        self,
        route_id: UUID,
         RouteCalculationRequest
    ) -> RouteCalculationResponse:
        """
        Calculate route using the configured route provider.
        
        Only calculates if:
        1. Route provider is available
        2. Route hasn't been calculated yet (or recalculate=True)
        3. Depot coordinates are available
        """
        route = await self.repository.get_by_id(route_id)
        if not route:
            raise NotFoundException("Route", str(route_id))
        
        # Check if provider is available
        if not self.route_provider.is_available():
            raise ValidationException("Route provider is not available")
        
        # Check if already calculated
        if route.distance_km is not None and not request.recalculate:
            raise ValidationException(
                "Route already calculated. Use recalculate=true to force recalculation."
            )
        
        # Get depot coordinates
        origin_depot = await self._get_depot(route.origin_depot_id)
        destination_depot = await self._get_depot(route.destination_depot_id)
        
        # Build coordinate list
        origin = Coordinate(
            latitude=origin_depot.latitude,
            longitude=origin_depot.longitude
        )
        destination = Coordinate(
            latitude=destination_depot.latitude,
            longitude=destination_depot.longitude
        )
        
        # Parse existing waypoints
        waypoints = None
        if request.waypoints:
            waypoints = [
                Coordinate(latitude=wp.latitude, longitude=wp.longitude)
                for wp in request.waypoints
            ]
        elif route.waypoint_data:
            try:
                wp_data = json.loads(route.waypoint_data)
                waypoints = [
                    Coordinate(latitude=wp["lat"], longitude=wp["lng"])
                    for wp in wp_data
                ]
            except:
                waypoints = None
        
        # Calculate route
        try:
            result = await self.route_provider.calculate_route(
                origin=origin,
                destination=destination,
                waypoints=waypoints,
                vehicle_type=request.vehicle_type or route.vehicle_type or "truck"
            )
        except Exception as e:
            raise ValidationException(f"Route calculation failed: {str(e)}")
        
        # Save calculation results
        route_data_json = json.dumps(result.to_dict())
        updated_route = await self.repository.update_calculation(
            route_id=route_id,
            distance_km=result.total_distance_km,
            duration_minutes=result.total_duration_minutes,
            route_data=route_data_json
        )
        
        # Build response
        segments = [
            RouteSegmentSchema(
                start=CoordinateSchema(
                    latitude=seg.start.latitude,
                    longitude=seg.start.longitude
                ),
                end=CoordinateSchema(
                    latitude=seg.end.latitude,
                    longitude=seg.end.longitude
                ),
                distance_km=seg.distance_km,
                duration_minutes=seg.duration_minutes,
                waypoints=[
                    CoordinateSchema(latitude=wp.latitude, longitude=wp.longitude)
                    for wp in seg.waypoints
                ]
            )
            for seg in result.segments
        ]
        
        return RouteCalculationResponse(
            route_id=route_id,
            total_distance_km=result.total_distance_km,
            total_duration_minutes=result.total_duration_minutes,
            segments=segments,
            provider=result.provider,
            metadata=result.metadata,
            calculated_at=datetime.now(timezone.utc)
        )
    
    async def mark_disrupted(
        self,
        route_id: UUID,
         RouteDisruptionRequest
    ) -> RouteResponse:
        """Mark route as disrupted."""
        route = await self.repository.get_by_id(route_id)
        if not route:
            raise NotFoundException("Route", str(route_id))
        
        if route.status in ["completed", "cancelled"]:
            raise ValidationException(
                f"Cannot disrupt route in {route.status} status"
            )
        
        updated = await self.repository.mark_disrupted(
            route_id=route_id,
            reason=request.reason,
            severity=request.severity,
            estimated_resolution_hours=request.estimated_resolution_hours
        )
        
        return self._to_response(updated)
    
    async def clear_disruption(self, route_id: UUID) -> RouteResponse:
        """Clear disruption status."""
        route = await self.repository.get_by_id(route_id)
        if not route:
            raise NotFoundException("Route", str(route_id))
        
        if route.status != "disrupted":
            raise ValidationException("Route is not currently disrupted")
        
        updated = await self.repository.clear_disruption(route_id)
        return self._to_response(updated)
    
    async def calculate_matrix(
        self,
         RouteMatrixRequest
    ) -> RouteMatrixResponse:
        """Calculate distance/duration matrix between depots."""
        # Check if provider is available
        if not self.route_provider.is_available():
            raise ValidationException("Route provider is not available")
        
        # Get depot coordinates
        coordinates = []
        for depot_id in request.depot_ids:
            depot = await self._get_depot(depot_id)
            coordinates.append(Coordinate(
                latitude=depot.latitude,
                longitude=depot.longitude
            ))
        
        # Calculate matrix
        try:
            matrix = await self.route_provider.calculate_matrix(
                coordinates=coordinates,
                vehicle_type=request.vehicle_type
            )
        except Exception as e:
            raise ValidationException(f"Matrix calculation failed: {str(e)}")
        
        return RouteMatrixResponse(
            depot_ids=request.depot_ids,
            matrix=matrix,
            provider=self.route_provider.provider_name,
            calculated_at=datetime.now(timezone.utc)
        )
    
    async def get_provider_info(self) -> RouteProviderInfo:
        """Get information about the routing provider."""
        info = await self.route_provider.get_provider_info()
        
        return RouteProviderInfo(
            name=info["name"],
            version=info["version"],
            type=info["type"],
            capabilities=info.get("capabilities", []),
            limitations=info.get("limitations", []),
            is_available=self.route_provider.is_available(),
            synthetic=info.get("synthetic", False)
        )
    
    async def get_routes_for_depot(self, depot_id: UUID) -> List[RouteResponse]:
        """Get all routes involving a depot."""
        routes = await self.repository.get_routes_by_depot(depot_id)
        return [self._to_response(r) for r in routes]
    
    async def get_disrupted_routes(self) -> List[RouteResponse]:
        """Get all disrupted routes."""
        routes = await self.repository.get_disrupted_routes()
        return [self._to_response(r) for r in routes]
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _validate_depots(self, origin_id: UUID, destination_id: UUID):
        """Validate that both depots exist."""
        origin = await self._get_depot(origin_id)
        destination = await self._get_depot(destination_id)
        
        if origin.id == destination.id:
            raise ValidationException("Origin and destination depots must be different")
    
    async def _get_depot(self, depot_id: UUID) -> Depot:
        """Get depot by ID."""
        from sqlalchemy import select
        result = await self.db.execute(
            select(Depot).where(Depot.id == depot_id)
        )
        depot = result.scalar_one_or_none()
        if not depot:
            raise NotFoundException("Depot", str(depot_id))
        return depot
    
    def _to_response(self, route: Route) -> RouteResponse:
        """Convert Route model to response schema."""
        # Parse waypoints
        waypoints = None
        if route.waypoint_data:
            try:
                wp_data = json.loads(route.waypoint_data)
                waypoints = [
                    CoordinateSchema(latitude=wp["lat"], longitude=wp["lng"])
                    for wp in wp_data
                ]
            except:
                waypoints = None
        
        # Parse route_data
        route_data = None
        if route.route_data:
            try:
                route_data = json.loads(route.route_data)
            except:
                route_data = None
        
        is_calculated = route.distance_km is not None
        
        return RouteResponse(
            id=route.id,
            name=route.name,
            code=route.code,
            origin_depot_id=route.origin_depot_id,
            destination_depot_id=route.destination_depot_id,
            route_type=route.route_type,
            status=route.status,
            vehicle_type=route.vehicle_type,
            distance_km=route.distance_km,
            duration_minutes=route.estimated_duration_hours * 60 if route.estimated_duration_hours else None,
            max_weight_kg=route.max_weight_kg,
            max_volume_m3=route.max_volume_m3,
            waypoints=waypoints,
            disruption_reason=route.disruption_reason,
            route_data=route_data,
            notes=route.notes,
            created_at=route.created_at,
            updated_at=route.updated_at,
            origin_depot_name=route.origin_depot.name if route.origin_depot else None,
            destination_depot_name=route.destination_depot.name if route.destination_depot else None,
            is_calculated=is_calculated
        )
    
    def _to_list_item(self, route: Route) -> RouteListItem:
        """Convert Route model to list item schema."""
        return RouteListItem(
            id=route.id,
            name=route.name,
            code=route.code,
            origin_depot_id=route.origin_depot_id,
            destination_depot_id=route.destination_depot_id,
            route_type=route.route_type,
            status=route.status,
            distance_km=route.distance_km,
            duration_minutes=route.estimated_duration_hours * 60 if route.estimated_duration_hours else None,
            is_disrupted=route.status == "disrupted",
            created_at=route.created_at
        )
    
    async def _to_detail_response(self, route: Route) -> RouteDetailResponse:
        """Convert Route model to detail response schema."""
        base_response = self._to_response(route)
        
        # Parse segments from route_data
        segments = None
        if route.route_data:
            try:
                route_data = json.loads(route.route_data)
                if "segments" in route_data:
                    segments = [
                        RouteSegmentSchema(
                            start=CoordinateSchema(**seg["start"]),
                            end=CoordinateSchema(**seg["end"]),
                            distance_km=seg["distance_km"],
                            duration_minutes=seg["duration_minutes"],
                            waypoints=[CoordinateSchema(**wp) for wp in seg["waypoints"]]
                        )
                        for seg in route_data["segments"]
                    ]
            except:
                segments = None
        
        # Get provider info
        provider_info = None
        if route.route_data:
            try:
                route_data = json.loads(route.route_data)
                if "provider" in route_data:
                    provider_info = await self.route_provider.get_provider_info()
            except:
                pass
        
        return RouteDetailResponse(
            **base_response.model_dump(),
            segments=segments,
            provider_info=provider_info.model_dump() if provider_info else None
        )

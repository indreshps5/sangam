"""
Route Router

API endpoints for route management and GIS operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db
from sangam_api.core.auth import get_current_user
from sangam_api.models.user import User
from sangam_api.routes.repository_impl import RouteRepository
from sangam_api.routes.provider import SyntheticRouteProvider
from sangam_api.routes.service import RouteService
from sangam_api.routes.schemas import (
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    RouteDetailResponse,
    RouteListResponse,
    RouteCalculationRequest,
    RouteCalculationResponse,
    RouteDisruptionRequest,
    RouteMatrixRequest,
    RouteMatrixResponse,
    RouteProviderInfo
)

router = APIRouter(prefix="/routes", tags=["routes"])


def get_route_service(
    db: AsyncSession = Depends(get_db)
) -> RouteService:
    """Dependency injection for route service."""
    repository = RouteRepository(db)
    route_provider = SyntheticRouteProvider()  # Can be swapped for real provider
    return RouteService(repository, route_provider, db)


# ============================================================================
# Route CRUD Endpoints
# ============================================================================

@router.get("/", response_model=RouteListResponse)
async def list_routes(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    route_type: Optional[str] = Query(None, description="Filter by route type"),
    origin_depot_id: Optional[UUID] = Query(None, description="Filter by origin depot"),
    destination_depot_id: Optional[UUID] = Query(None, description="Filter by destination depot"),
    is_disrupted: Optional[bool] = Query(None, description="Filter by disruption status"),
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    List routes with filtering and pagination.
    
    Supports filtering by status, type, depots, and disruption status.
    """
    return await service.list_routes(
        skip=skip,
        limit=limit,
        status=status_filter,
        route_type=route_type,
        origin_depot_id=origin_depot_id,
        destination_depot_id=destination_depot_id,
        is_disrupted=is_disrupted
    )


@router.get("/{route_id}", response_model=RouteDetailResponse)
async def get_route(
    route_id: UUID,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get route by ID with full details.
    
    Includes waypoints, calculated route data, and segments.
    """
    return await service.get_route(route_id)


@router.get("/code/{code}", response_model=RouteDetailResponse)
async def get_route_by_code(
    code: str,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get route by code.
    
    Useful for external systems referencing routes by code.
    """
    return await service.get_route_by_code(code)


@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(
     RouteCreate,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new route.
    
    Validates depot references and code uniqueness.
    Route calculation must be triggered separately.
    """
    return await service.create_route(data)


@router.put("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: UUID,
     RouteUpdate,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update route details.
    
    Cannot update completed or cancelled routes.
    """
    return await service.update_route(route_id, data)


# ============================================================================
# Route Calculation Endpoints
# ============================================================================

@router.post("/{route_id}/calculate", response_model=RouteCalculationResponse)
async def calculate_route(
    route_id: UUID,
     RouteCalculationRequest,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate route using the configured routing provider.
    
    Note: Currently uses synthetic route provider for demonstration.
    Distance and duration are calculated using simplified algorithms.
    Not suitable for production routing without a real provider.
    
    Returns:
    - Total distance and duration
    - Route segments with waypoints
    - Provider information
    - Metadata indicating synthetic data
    """
    return await service.calculate_route(route_id, request)


@router.post("/matrix", response_model=RouteMatrixResponse)
async def calculate_matrix(
     RouteMatrixRequest,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate distance/duration matrix between multiple depots.
    
    Useful for:
    - Route optimization
    - Multi-stop planning
    - Depot network analysis
    
    Note: Uses synthetic calculations for demonstration.
    """
    return await service.calculate_matrix(request)


# ============================================================================
# Disruption Management Endpoints
# ============================================================================

@router.post("/{route_id}/disrupt", response_model=RouteResponse)
async def mark_route_disrupted(
    route_id: UUID,
     RouteDisruptionRequest,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Mark route as disrupted.
    
    Used for simulating or recording real disruptions like:
    - Road closures
    - Weather events
    - Traffic incidents
    - Construction
    
    Cannot disrupt completed or cancelled routes.
    """
    return await service.mark_disrupted(route_id, request)


@router.post("/{route_id}/resolve-disruption", response_model=RouteResponse)
async def clear_route_disruption(
    route_id: UUID,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Clear disruption status and mark route as active.
    
    Used when disruption is resolved.
    """
    return await service.clear_disruption(route_id)


@router.get("/disrupted/list", response_model=list[RouteResponse])
async def get_disrupted_routes(
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all currently disrupted routes.
    
    Useful for dashboard alerts and operational awareness.
    """
    return await service.get_disrupted_routes()


# ============================================================================
# Depot-Specific Routes
# ============================================================================

@router.get("/depot/{depot_id}", response_model=list[RouteResponse])
async def get_routes_for_depot(
    depot_id: UUID,
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all routes involving a specific depot.
    
    Returns routes where depot is either origin or destination.
    Useful for depot-specific views and planning.
    """
    return await service.get_routes_for_depot(depot_id)


# ============================================================================
# Provider Information
# ============================================================================

@router.get("/provider/info", response_model=RouteProviderInfo)
async def get_provider_info(
    service: RouteService = Depends(get_route_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the routing provider.
    
    Returns:
    - Provider name and version
    - Capabilities and limitations
    - Availability status
    - Whether data is synthetic
    """
    return await service.get_provider_info()

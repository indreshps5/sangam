"""
Shipment Router

API endpoints for shipment management.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db
from sangam_api.core.auth import get_current_user
from sangam_api.models.user import User
from sangam_api.services.audit_service import AuditService
from sangam_api.shipments.repository_impl import ShipmentRepository
from sangam_api.shipments.service import ShipmentService
from sangam_api.shipments.schemas import (
    ShipmentCreate,
    ShipmentUpdate,
    StatusUpdateRequest,
    LocationUpdateRequest,
    ShipmentResponse,
    ShipmentDetailResponse,
    ShipmentListResponse,
    ShipmentStats,
    ShipmentAlertListResponse
)

router = APIRouter(prefix="/shipments", tags=["shipments"])


def get_shipment_service(
    db: AsyncSession = Depends(get_db)
) -> ShipmentService:
    """Dependency injection for shipment service."""
    repository = ShipmentRepository(db)
    audit_service = AuditService(db)
    return ShipmentService(repository, audit_service)


# ============================================================================
# Shipment CRUD Endpoints
# ============================================================================

@router.get("/", response_model=ShipmentListResponse)
async def list_shipments(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    origin_depot_id: Optional[UUID] = Query(None, description="Filter by origin depot"),
    destination_depot_id: Optional[UUID] = Query(None, description="Filter by destination depot"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority"),
    is_delayed: Optional[bool] = Query(None, description="Filter by delayed status"),
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    List shipments with filtering and pagination.
    
    Supports filtering by status, depots, priority, and delay status.
    """
    return await service.list_shipments(
        skip=skip,
        limit=limit,
        status=status_filter,
        origin_depot_id=origin_depot_id,
        destination_depot_id=destination_depot_id,
        priority=priority,
        is_delayed=is_delayed
    )


@router.get("/stats", response_model=ShipmentStats)
async def get_shipment_stats(
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get shipment statistics for dashboard KPIs.
    
    Returns counts by status, average delay, and on-time delivery rate.
    """
    return await service.get_statistics()


@router.get("/alerts", response_model=ShipmentAlertListResponse)
async def get_shipment_alerts(
    overdue_threshold_hours: float = Query(24.0, ge=0, description="Hours threshold for overdue"),
    at_risk_threshold_hours: float = Query(6.0, ge=0, description="Hours threshold for at-risk"),
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get shipment alerts for overdue and at-risk shipments.
    
    Returns alerts with severity levels and actionable information.
    """
    return await service.get_shipment_alerts(
        overdue_threshold_hours=overdue_threshold_hours,
        at_risk_threshold_hours=at_risk_threshold_hours
    )


@router.get("/{shipment_id}", response_model=ShipmentDetailResponse)
async def get_shipment(
    shipment_id: UUID,
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get shipment by ID with full details.
    
    Includes status history, current location, and related entities.
    """
    return await service.get_shipment(shipment_id)


@router.get("/tracking/{tracking_number}", response_model=ShipmentDetailResponse)
async def get_shipment_by_tracking(
    tracking_number: str,
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get shipment by tracking number.
    
    Useful for external tracking systems.
    """
    return await service.get_shipment_by_tracking(tracking_number)


@router.post("/", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
     ShipmentCreate,
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new shipment.
    
    Supports idempotency via idempotency_key field.
    Validates depot and inventory item references.
    """
    return await service.create_shipment(data, user_id=current_user.id)


@router.put("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: UUID,
     ShipmentUpdate,
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update shipment details.
    
    Cannot update shipments in terminal states (delivered, cancelled).
    """
    return await service.update_shipment(shipment_id, data, user_id=current_user.id)


# ============================================================================
# Status Management Endpoints
# ============================================================================

@router.post("/{shipment_id}/status", response_model=ShipmentResponse)
async def update_shipment_status(
    shipment_id: UUID,
     StatusUpdateRequest,
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update shipment status with validation.
    
    Validates state transitions:
    - planned → dispatched, cancelled
    - dispatched → in_transit, cancelled
    - in_transit → delayed, delivered, cancelled
    - delayed → in_transit, delivered, cancelled
    - delivered, cancelled (terminal states)
    
    Requires delay_reason when marking as delayed.
    """
    return await service.update_status(shipment_id, request, user_id=current_user.id)


# ============================================================================
# Location Tracking Endpoints (Simulation)
# ============================================================================

@router.post("/{shipment_id}/location", response_model=ShipmentResponse)
async def update_shipment_location(
    shipment_id: UUID,
     LocationUpdateRequest,
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update shipment GPS location (simulation).
    
    Note: This is for demonstration purposes only.
    GPS locations are simulated and not from real tracking devices.
    
    Only allowed for active shipments (dispatched, in_transit, delayed).
    """
    return await service.update_location(shipment_id, request)


@router.post("/{shipment_id}/simulate-progress", response_model=ShipmentResponse)
async def simulate_shipment_progress(
    shipment_id: UUID,
    service: ShipmentService = Depends(get_shipment_service),
    current_user: User = Depends(get_current_user)
):
    """
    Simulate shipment progress for demonstration.
    
    This is a user-triggered simulation that advances the shipment
    through its lifecycle stages:
    - planned → dispatched
    - dispatched → in_transit (with midpoint location)
    - in_transit → delivered (with destination location)
    
    Note: This is clearly simulated data for demonstration purposes.
    Not a permanent tracking loop.
    """
    return await service.simulate_shipment_progress(shipment_id)

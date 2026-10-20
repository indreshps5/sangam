"""
Shipment routes - thin controllers that delegate to application services.
Business logic is NOT in routes.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db_session
from sangam_api.api.schemas.shipments import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentListResponse,
)
from sangam_api.services.shipment_service import ShipmentService
from sangam_api.repositories.shipment_repository import ShipmentRepository

router = APIRouter()


def get_shipment_service(
    db: AsyncSession = Depends(get_db_session),
) -> ShipmentService:
    """Dependency injection: creates ShipmentService with its repository."""
    repository = ShipmentRepository(db)
    return ShipmentService(repository)


@router.get("/", response_model=ShipmentListResponse)
async def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentListResponse:
    """List shipments with pagination and optional status filter."""
    return await service.list_shipments(skip=skip, limit=limit, status=status)


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: UUID,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentResponse:
    """Get a single shipment by ID."""
    return await service.get_shipment(shipment_id)


@router.post("/", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    payload: ShipmentCreate,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentResponse:
    """Create a new shipment."""
    return await service.create_shipment(payload)


@router.patch("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment_status(
    shipment_id: UUID,
    payload: ShipmentCreate,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentResponse:
    """Update shipment details."""
    return await service.update_shipment(shipment_id, payload)


@router.delete("/{shipment_id}", status_code=204)
async def delete_shipment(
    shipment_id: UUID,
    service: ShipmentService = Depends(get_shipment_service),
) -> None:
    """Delete a shipment."""
    await service.delete_shipment(shipment_id)

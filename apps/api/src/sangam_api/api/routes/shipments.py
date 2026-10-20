"""
Shipment routes — thin controllers delegating to application services.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db_session
from sangam_api.api.schemas.shipments import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentListResponse,
)
from sangam_api.repositories.implementations import ShipmentRepository

router = APIRouter()


def get_shipment_repository(
    db: AsyncSession = Depends(get_db_session),
) -> ShipmentRepository:
    """Dependency injection for ShipmentRepository."""
    return ShipmentRepository(db)


@router.get("/", response_model=ShipmentListResponse)
async def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    origin_depot_id: Optional[UUID] = Query(None),
    destination_depot_id: Optional[UUID] = Query(None),
    repo: ShipmentRepository = Depends(get_shipment_repository),
) -> ShipmentListResponse:
    """List shipments with pagination and optional filters."""
    items = await repo.list(
        skip=skip, limit=limit, status=status,
        origin_depot_id=origin_depot_id,
        destination_depot_id=destination_depot_id,
    )
    total = await repo.count(
        status=status,
        origin_depot_id=origin_depot_id,
        destination_depot_id=destination_depot_id,
    )
    return ShipmentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: UUID,
    repo: ShipmentRepository = Depends(get_shipment_repository),
) -> ShipmentResponse:
    """Get a single shipment by ID."""
    shipment = await repo.get_by_id(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.post("/", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    payload: ShipmentCreate,
    repo: ShipmentRepository = Depends(get_shipment_repository),
) -> ShipmentResponse:
    """Create a new shipment."""
    return await repo.create(payload)


@router.patch("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: UUID,
    payload: ShipmentUpdate,
    repo: ShipmentRepository = Depends(get_shipment_repository),
) -> ShipmentResponse:
    """Update a shipment."""
    shipment = await repo.update(shipment_id, payload)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.delete("/{shipment_id}", status_code=204)
async def delete_shipment(
    shipment_id: UUID,
    repo: ShipmentRepository = Depends(get_shipment_repository),
) -> None:
    """Delete a shipment."""
    deleted = await repo.delete(shipment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Shipment not found")

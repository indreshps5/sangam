"""
Depot routes — thin controllers delegating to application services.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db_session
from sangam_api.api.schemas.depots import (
    DepotCreate,
    DepotUpdate,
    DepotResponse,
    DepotListResponse,
)
from sangam_api.repositories.implementations import DepotRepository

router = APIRouter()


def get_depot_repository(
    db: AsyncSession = Depends(get_db_session),
) -> DepotRepository:
    """Dependency injection for DepotRepository."""
    return DepotRepository(db)


@router.get("/", response_model=DepotListResponse)
async def list_depots(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    depot_type: Optional[str] = Query(None),
    repo: DepotRepository = Depends(get_depot_repository),
) -> DepotListResponse:
    """List depots with pagination and optional filters."""
    items = await repo.list(skip=skip, limit=limit, status=status, region=region, depot_type=depot_type)
    total = await repo.count(status=status, region=region, depot_type=depot_type)
    return DepotListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{depot_id}", response_model=DepotResponse)
async def get_depot(
    depot_id: UUID,
    repo: DepotRepository = Depends(get_depot_repository),
) -> DepotResponse:
    """Get a single depot by ID."""
    depot = await repo.get_by_id(depot_id)
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")
    return depot


@router.post("/", response_model=DepotResponse, status_code=201)
async def create_depot(
    payload: DepotCreate,
    repo: DepotRepository = Depends(get_depot_repository),
) -> DepotResponse:
    """Create a new depot."""
    return await repo.create(payload)


@router.patch("/{depot_id}", response_model=DepotResponse)
async def update_depot(
    depot_id: UUID,
    payload: DepotUpdate,
    repo: DepotRepository = Depends(get_depot_repository),
) -> DepotResponse:
    """Update an existing depot."""
    depot = await repo.update(depot_id, payload)
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")
    return depot


@router.delete("/{depot_id}", status_code=204)
async def delete_depot(
    depot_id: UUID,
    repo: DepotRepository = Depends(get_depot_repository),
) -> None:
    """Delete a depot."""
    deleted = await repo.delete(depot_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Depot not found")

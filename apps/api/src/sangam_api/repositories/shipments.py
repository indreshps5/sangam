"""
SQLAlchemy repository implementations.
Concrete implementations of repository interfaces using async SQLAlchemy.
"""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.repositories.interfaces import (
    ShipmentRepositoryInterface,
    WarehouseRepositoryInterface,
)
from sangam_api.api.schemas.shipments import ShipmentCreate, ShipmentResponse
from sangam_api.api.schemas.warehouses import WarehouseCreate, WarehouseResponse
from sangam_api.models.shipment import ShipmentModel
from sangam_api.models.warehouse import WarehouseModel


class ShipmentRepository(ShipmentRepositoryInterface):
    """SQLAlchemy implementation of ShipmentRepositoryInterface."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self, skip: int = 0, limit: int = 20, status: Optional[str] = None
    ) -> list[ShipmentResponse]:
        query = select(ShipmentModel).offset(skip).limit(limit)
        if status:
            query = query.where(ShipmentModel.status == status)
        query = query.order_by(ShipmentModel.created_at.desc())
        result = await self._session.execute(query)
        return [ShipmentResponse.model_validate(row) for row in result.scalars().all()]

    async def count(self, status: Optional[str] = None) -> int:
        query = select(func.count(ShipmentModel.id))
        if status:
            query = query.where(ShipmentModel.status == status)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, shipment_id: UUID) -> Optional[ShipmentResponse]:
        result = await self._session.execute(
            select(ShipmentModel).where(ShipmentModel.id == shipment_id)
        )
        row = result.scalar_one_or_none()
        return ShipmentResponse.model_validate(row) if row else None

    async def create(self, payload: ShipmentCreate) -> ShipmentResponse:
        model = ShipmentModel(
            id=uuid4(),
            origin_warehouse_id=payload.origin_warehouse_id,
            destination_warehouse_id=payload.destination_warehouse_id,
            status=payload.status.value,
            weight_kg=payload.weight_kg,
            volume_m3=payload.volume_m3,
            priority=payload.priority,
            estimated_arrival=payload.estimated_arrival,
            notes=payload.notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._session.add(model)
        await self._session.flush()
        return ShipmentResponse.model_validate(model)

    async def update(
        self, shipment_id: UUID, payload: ShipmentCreate
    ) -> ShipmentResponse:
        result = await self._session.execute(
            select(ShipmentModel).where(ShipmentModel.id == shipment_id)
        )
        model = result.scalar_one()
        model.status = payload.status.value
        model.weight_kg = payload.weight_kg
        model.volume_m3 = payload.volume_m3
        model.priority = payload.priority
        model.estimated_arrival = payload.estimated_arrival
        model.notes = payload.notes
        model.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return ShipmentResponse.model_validate(model)

    async def delete(self, shipment_id: UUID) -> None:
        result = await self._session.execute(
            select(ShipmentModel).where(ShipmentModel.id == shipment_id)
        )
        model = result.scalar_one()
        await self._session.delete(model)
        await self._session.flush()


class WarehouseRepository(WarehouseRepositoryInterface):
    """SQLAlchemy implementation of WarehouseRepositoryInterface."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self, skip: int = 0, limit: int = 20, region: Optional[str] = None
    ) -> list[WarehouseResponse]:
        query = select(WarehouseModel).offset(skip).limit(limit)
        if region:
            query = query.where(WarehouseModel.region == region)
        result = await self._session.execute(query)
        return [WarehouseResponse.model_validate(row) for row in result.scalars().all()]

    async def count(self, region: Optional[str] = None) -> int:
        query = select(func.count(WarehouseModel.id))
        if region:
            query = query.where(WarehouseModel.region == region)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, warehouse_id: UUID) -> Optional[WarehouseResponse]:
        result = await self._session.execute(
            select(WarehouseModel).where(WarehouseModel.id == warehouse_id)
        )
        row = result.scalar_one_or_none()
        return WarehouseResponse.model_validate(row) if row else None

    async def create(self, payload: WarehouseCreate) -> WarehouseResponse:
        model = WarehouseModel(
            id=uuid4(),
            name=payload.name,
            code=payload.code,
            region=payload.region,
            latitude=payload.latitude,
            longitude=payload.longitude,
            capacity_units=payload.capacity_units,
            current_utilization=0.0,
            address=payload.address,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._session.add(model)
        await self._session.flush()
        return WarehouseResponse.model_validate(model)

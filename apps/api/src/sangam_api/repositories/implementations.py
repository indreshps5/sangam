"""
SQLAlchemy repository implementations for canonical entities.
Concrete implementations of repository interfaces using async SQLAlchemy.
"""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.repositories.interfaces import (
    DepotRepositoryInterface,
    ShipmentRepositoryInterface,
    RouteRepositoryInterface,
)
from sangam_api.api.schemas.depots import DepotCreate, DepotUpdate, DepotResponse
from sangam_api.api.schemas.shipments import ShipmentCreate, ShipmentUpdate, ShipmentResponse
from sangam_api.api.schemas.routes import RouteCreate, RouteUpdate, RouteResponse
from sangam_api.models.depot import Depot
from sangam_api.models.shipment import Shipment, Route
from sangam_api.core.exceptions import NotFoundException


class DepotRepository(DepotRepositoryInterface):
    """SQLAlchemy implementation of DepotRepositoryInterface."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        region: Optional[str] = None,
        depot_type: Optional[str] = None,
    ) -> list[DepotResponse]:
        query = select(Depot).offset(skip).limit(limit)
        if status:
            query = query.where(Depot.status == status)
        if region:
            query = query.where(Depot.region == region)
        if depot_type:
            query = query.where(Depot.depot_type == depot_type)
        query = query.order_by(Depot.created_at.desc())
        result = await self._session.execute(query)
        return [DepotResponse.model_validate(row) for row in result.scalars().all()]

    async def count(
        self,
        status: Optional[str] = None,
        region: Optional[str] = None,
        depot_type: Optional[str] = None,
    ) -> int:
        query = select(func.count(Depot.id))
        if status:
            query = query.where(Depot.status == status)
        if region:
            query = query.where(Depot.region == region)
        if depot_type:
            query = query.where(Depot.depot_type == depot_type)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, depot_id: UUID) -> Optional[DepotResponse]:
        result = await self._session.execute(
            select(Depot).where(Depot.id == depot_id)
        )
        row = result.scalar_one_or_none()
        return DepotResponse.model_validate(row) if row else None

    async def get_by_code(self, code: str) -> Optional[DepotResponse]:
        result = await self._session.execute(
            select(Depot).where(Depot.code == code.upper())
        )
        row = result.scalar_one_or_none()
        return DepotResponse.model_validate(row) if row else None

    async def create(self, payload: DepotCreate) -> DepotResponse:
        model = Depot(
            id=uuid4(),
            name=payload.name,
            code=payload.code,
            depot_type=payload.depot_type.value,
            status=payload.status.value,
            region=payload.region,
            latitude=payload.latitude,
            longitude=payload.longitude,
            capacity_units=payload.capacity_units,
            current_utilization=0.0,
            address=payload.address,
            contact_email=payload.contact_email,
            contact_phone=payload.contact_phone,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._session.add(model)
        await self._session.flush()
        return DepotResponse.model_validate(model)

    async def update(self, depot_id: UUID, payload: DepotUpdate) -> Optional[DepotResponse]:
        result = await self._session.execute(
            select(Depot).where(Depot.id == depot_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(model, field):
                # Handle enum values
                if hasattr(value, "value"):
                    value = value.value
                setattr(model, field, value)
        model.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return DepotResponse.model_validate(model)

    async def delete(self, depot_id: UUID) -> bool:
        result = await self._session.execute(
            select(Depot).where(Depot.id == depot_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True


class ShipmentRepository(ShipmentRepositoryInterface):
    """SQLAlchemy implementation of ShipmentRepositoryInterface."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
    ) -> list[ShipmentResponse]:
        query = select(Shipment).offset(skip).limit(limit)
        if status:
            query = query.where(Shipment.status == status)
        if origin_depot_id:
            query = query.where(Shipment.origin_depot_id == origin_depot_id)
        if destination_depot_id:
            query = query.where(Shipment.destination_depot_id == destination_depot_id)
        query = query.order_by(Shipment.created_at.desc())
        result = await self._session.execute(query)
        return [ShipmentResponse.model_validate(row) for row in result.scalars().all()]

    async def count(
        self,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
    ) -> int:
        query = select(func.count(Shipment.id))
        if status:
            query = query.where(Shipment.status == status)
        if origin_depot_id:
            query = query.where(Shipment.origin_depot_id == origin_depot_id)
        if destination_depot_id:
            query = query.where(Shipment.destination_depot_id == destination_depot_id)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, shipment_id: UUID) -> Optional[ShipmentResponse]:
        result = await self._session.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        row = result.scalar_one_or_none()
        return ShipmentResponse.model_validate(row) if row else None

    async def create(self, payload: ShipmentCreate) -> ShipmentResponse:
        model = Shipment(
            id=uuid4(),
            origin_depot_id=payload.origin_depot_id,
            destination_depot_id=payload.destination_depot_id,
            route_id=payload.route_id,
            status=payload.status.value,
            weight_kg=payload.weight_kg,
            volume_m3=payload.volume_m3,
            priority=payload.priority,
            shipment_type=payload.shipment_type,
            carrier_name=payload.carrier_name,
            tracking_number=payload.tracking_number,
            estimated_departure=payload.estimated_departure,
            estimated_arrival=payload.estimated_arrival,
            notes=payload.notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._session.add(model)
        await self._session.flush()
        return ShipmentResponse.model_validate(model)

    async def update(self, shipment_id: UUID, payload: ShipmentUpdate) -> Optional[ShipmentResponse]:
        result = await self._session.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(model, field):
                if hasattr(value, "value"):
                    value = value.value
                setattr(model, field, value)
        model.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return ShipmentResponse.model_validate(model)

    async def delete(self, shipment_id: UUID) -> bool:
        result = await self._session.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True


class RouteRepository(RouteRepositoryInterface):
    """SQLAlchemy implementation of RouteRepositoryInterface."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self, skip: int = 0, limit: int = 20, status: Optional[str] = None
    ) -> list[RouteResponse]:
        query = select(Route).offset(skip).limit(limit)
        if status:
            query = query.where(Route.status == status)
        query = query.order_by(Route.created_at.desc())
        result = await self._session.execute(query)
        return [RouteResponse.model_validate(row) for row in result.scalars().all()]

    async def count(self, status: Optional[str] = None) -> int:
        query = select(func.count(Route.id))
        if status:
            query = query.where(Route.status == status)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, route_id: UUID) -> Optional[RouteResponse]:
        result = await self._session.execute(
            select(Route).where(Route.id == route_id)
        )
        row = result.scalar_one_or_none()
        return RouteResponse.model_validate(row) if row else None

    async def create(self, payload: RouteCreate) -> RouteResponse:
        model = Route(
            id=uuid4(),
            name=payload.name,
            code=payload.code,
            origin_depot_id=payload.origin_depot_id,
            destination_depot_id=payload.destination_depot_id,
            status=payload.status.value,
            distance_km=payload.distance_km,
            estimated_duration_hours=payload.estimated_duration_hours,
            optimization_objective=payload.optimization_objective.value,
            waypoint_data=payload.waypoint_data,
            vehicle_type=payload.vehicle_type,
            max_weight_kg=payload.max_weight_kg,
            max_volume_m3=payload.max_volume_m3,
            cost_per_km=payload.cost_per_km,
            carbon_emission_factor=payload.carbon_emission_factor,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._session.add(model)
        await self._session.flush()
        return RouteResponse.model_validate(model)

    async def update(self, route_id: UUID, payload: RouteUpdate) -> Optional[RouteResponse]:
        result = await self._session.execute(
            select(Route).where(Route.id == route_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(model, field):
                if hasattr(value, "value"):
                    value = value.value
                setattr(model, field, value)
        model.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return RouteResponse.model_validate(model)

    async def delete(self, route_id: UUID) -> bool:
        result = await self._session.execute(
            select(Route).where(Route.id == route_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

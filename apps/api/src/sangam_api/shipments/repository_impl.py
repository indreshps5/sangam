"""
Shipment Repository Implementation

SQLAlchemy implementation of shipment repository interface.
"""

import json
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sangam_api.models.shipment import Shipment
from sangam_api.shipments.repository import ShipmentRepositoryInterface
from sangam_api.shipments.schemas import ShipmentCreate, ShipmentUpdate, StatusChange


class ShipmentRepository(ShipmentRepositoryInterface):
    """SQLAlchemy implementation of shipment repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, shipment_id: UUID) -> Optional[Shipment]:
        """Get shipment by ID."""
        result = await self.session.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.origin_depot),
                selectinload(Shipment.destination_depot),
                selectinload(Shipment.route),
                selectinload(Shipment.inventory_item)
            )
            .where(Shipment.id == shipment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_tracking_number(self, tracking_number: str) -> Optional[Shipment]:
        """Get shipment by tracking number."""
        result = await self.session.execute(
            select(Shipment).where(Shipment.tracking_number == tracking_number)
        )
        return result.scalar_one_or_none()
    
    async def get_by_idempotency_key(self, key: str) -> Optional[Shipment]:
        """Get shipment by idempotency key."""
        result = await self.session.execute(
            select(Shipment).where(Shipment.idempotency_key == key)
        )
        return result.scalar_one_or_none()
    
    async def list_shipments(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        priority: Optional[int] = None,
        is_delayed: Optional[bool] = None
    ) -> List[Shipment]:
        """List shipments with filtering."""
        query = select(Shipment).options(
            selectinload(Shipment.origin_depot),
            selectinload(Shipment.destination_depot)
        )
        
        # Apply filters
        if status:
            query = query.where(Shipment.status == status)
        
        if origin_depot_id:
            query = query.where(Shipment.origin_depot_id == origin_depot_id)
        
        if destination_depot_id:
            query = query.where(Shipment.destination_depot_id == destination_depot_id)
        
        if priority:
            query = query.where(Shipment.priority == priority)
        
        if is_delayed is not None:
            if is_delayed:
                # Delayed shipments: status is delayed OR past estimated arrival
                now = datetime.now(timezone.utc)
                query = query.where(
                    or_(
                        Shipment.status == "delayed",
                        and_(
                            Shipment.estimated_arrival < now,
                            Shipment.status.in_(["in_transit", "dispatched"]),
                            Shipment.actual_arrival.is_(None)
                        )
                    )
                )
            else:
                # Not delayed
                now = datetime.now(timezone.utc)
                query = query.where(
                    and_(
                        Shipment.status != "delayed",
                        or_(
                            Shipment.estimated_arrival >= now,
                            Shipment.estimated_arrival.is_(None),
                            Shipment.status.in_(["planned", "delivered", "cancelled"])
                        )
                    )
                )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Order by created_at desc
        query = query.order_by(Shipment.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_shipments(
        self,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        priority: Optional[int] = None,
        is_delayed: Optional[bool] = None
    ) -> int:
        """Count shipments with filtering."""
        query = select(func.count(Shipment.id))
        
        # Apply filters (same as list_shipments)
        if status:
            query = query.where(Shipment.status == status)
        
        if origin_depot_id:
            query = query.where(Shipment.origin_depot_id == origin_depot_id)
        
        if destination_depot_id:
            query = query.where(Shipment.destination_depot_id == destination_depot_id)
        
        if priority:
            query = query.where(Shipment.priority == priority)
        
        if is_delayed is not None:
            if is_delayed:
                now = datetime.now(timezone.utc)
                query = query.where(
                    or_(
                        Shipment.status == "delayed",
                        and_(
                            Shipment.estimated_arrival < now,
                            Shipment.status.in_(["in_transit", "dispatched"]),
                            Shipment.actual_arrival.is_(None)
                        )
                    )
                )
            else:
                now = datetime.now(timezone.utc)
                query = query.where(
                    and_(
                        Shipment.status != "delayed",
                        or_(
                            Shipment.estimated_arrival >= now,
                            Shipment.estimated_arrival.is_(None),
                            Shipment.status.in_(["planned", "delivered", "cancelled"])
                        )
                    )
                )
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self,  ShipmentCreate) -> Shipment:
        """Create a new shipment."""
        # Create initial status history
        initial_status = StatusChange(
            status="planned",
            timestamp=datetime.now(timezone.utc),
            notes="Shipment created"
        )
        status_history = [initial_status.model_dump(mode='json')]
        
        shipment = Shipment(
            origin_depot_id=data.origin_depot_id,
            destination_depot_id=data.destination_depot_id,
            route_id=data.route_id,
            inventory_item_id=data.inventory_item_id,
            status="planned",
            weight_kg=data.weight_kg,
            volume_m3=data.volume_m3,
            quantity=data.quantity,
            priority=data.priority,
            shipment_type=data.shipment_type,
            carrier_name=data.carrier_name,
            tracking_number=data.tracking_number,
            estimated_departure=data.estimated_departure,
            estimated_arrival=data.estimated_arrival,
            status_history=json.dumps(status_history),
            idempotency_key=data.idempotency_key,
            notes=data.notes
        )
        
        self.session.add(shipment)
        await self.session.flush()
        await self.session.refresh(shipment)
        
        return shipment
    
    async def update(self, shipment_id: UUID,  ShipmentUpdate) -> Optional[Shipment]:
        """Update an existing shipment."""
        shipment = await self.get_by_id(shipment_id)
        if not shipment:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(shipment, field, value)
        
        shipment.updated_at = datetime.now(timezone.utc)
        
        await self.session.flush()
        await self.session.refresh(shipment)
        
        return shipment
    
    async def update_status(
        self,
        shipment_id: UUID,
        status: str,
        changed_by: Optional[UUID] = None,
        notes: Optional[str] = None,
        delay_reason: Optional[str] = None
    ) -> Optional[Shipment]:
        """Update shipment status with history tracking."""
        shipment = await self.get_by_id(shipment_id)
        if not shipment:
            return None
        
        # Update status
        shipment.status = status
        
        # Update timestamps based on status
        now = datetime.now(timezone.utc)
        if status == "dispatched" and not shipment.actual_departure:
            shipment.actual_departure = now
        elif status == "delivered" and not shipment.actual_arrival:
            shipment.actual_arrival = now
        
        # Update delay reason if provided
        if delay_reason:
            shipment.delay_reason = delay_reason
        elif status != "delayed":
            shipment.delay_reason = None
        
        # Update status history
        status_change = StatusChange(
            status=status,
            timestamp=now,
            changed_by=changed_by,
            notes=notes
        )
        
        # Parse existing history
        history = []
        if shipment.status_history:
            try:
                history = json.loads(shipment.status_history)
            except:
                history = []
        
        # Add new status change
        history.append(status_change.model_dump(mode='json'))
        shipment.status_history = json.dumps(history)
        
        shipment.updated_at = now
        
        await self.session.flush()
        await self.session.refresh(shipment)
        
        return shipment
    
    async def update_location(
        self,
        shipment_id: UUID,
        latitude: float,
        longitude: float,
        accuracy_meters: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> Optional[Shipment]:
        """Update shipment GPS location."""
        shipment = await self.get_by_id(shipment_id)
        if not shipment:
            return None
        
        # Create location data
        location_data = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
            "accuracy_meters": accuracy_meters
        }
        
        shipment.current_location = json.dumps(location_data)
        shipment.updated_at = datetime.now(timezone.utc)
        
        await self.session.flush()
        await self.session.refresh(shipment)
        
        return shipment
    
    async def get_delayed_shipments(self) -> List[Shipment]:
        """Get all delayed shipments."""
        result = await self.session.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.origin_depot),
                selectinload(Shipment.destination_depot)
            )
            .where(Shipment.status == "delayed")
            .order_by(Shipment.priority.asc(), Shipment.estimated_arrival.asc())
        )
        return list(result.scalars().all())
    
    async def get_overdue_shipments(self, threshold_hours: float = 24.0) -> List[Shipment]:
        """Get shipments that are overdue (past estimated arrival)."""
        now = datetime.now(timezone.utc)
        
        result = await self.session.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.origin_depot),
                selectinload(Shipment.destination_depot)
            )
            .where(
                and_(
                    Shipment.estimated_arrival < now,
                    Shipment.status.in_(["in_transit", "dispatched"]),
                    Shipment.actual_arrival.is_(None)
                )
            )
            .order_by(Shipment.estimated_arrival.asc())
        )
        return list(result.scalars().all())
    
    async def get_shipments_by_status(self, status: str) -> List[Shipment]:
        """Get all shipments with a specific status."""
        result = await self.session.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.origin_depot),
                selectinload(Shipment.destination_depot)
            )
            .where(Shipment.status == status)
            .order_by(Shipment.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_statistics(self) -> dict:
        """Get shipment statistics."""
        # Count by status
        status_counts = await self.session.execute(
            select(Shipment.status, func.count(Shipment.id))
            .group_by(Shipment.status)
        )
        
        stats = {row[0]: row[1] for row in status_counts.all()}
        
        # Calculate average delay for delayed shipments
        delayed_result = await self.session.execute(
            select(Shipment).where(Shipment.status == "delayed")
        )
        delayed_shipments = delayed_result.scalars().all()
        
        total_delay_hours = 0
        delay_count = 0
        
        for shipment in delayed_shipments:
            if shipment.estimated_arrival and shipment.actual_arrival:
                delay = (shipment.actual_arrival - shipment.estimated_arrival).total_seconds() / 3600
                if delay > 0:
                    total_delay_hours += delay
                    delay_count += 1
        
        avg_delay = total_delay_hours / delay_count if delay_count > 0 else None
        
        # Calculate on-time delivery rate
        delivered_result = await self.session.execute(
            select(Shipment).where(Shipment.status == "delivered")
        )
        delivered_shipments = delivered_result.scalars().all()
        
        on_time_count = 0
        for shipment in delivered_shipments:
            if shipment.estimated_arrival and shipment.actual_arrival:
                if shipment.actual_arrival <= shipment.estimated_arrival:
                    on_time_count += 1
        
        on_time_rate = (on_time_count / len(delivered_shipments) * 100) if delivered_shipments else None
        
        return {
            "total_shipments": sum(stats.values()),
            "planned_count": stats.get("planned", 0),
            "dispatched_count": stats.get("dispatched", 0),
            "in_transit_count": stats.get("in_transit", 0),
            "delayed_count": stats.get("delayed", 0),
            "delivered_count": stats.get("delivered", 0),
            "cancelled_count": stats.get("cancelled", 0),
            "average_delay_hours": avg_delay,
            "on_time_delivery_rate": on_time_rate
        }

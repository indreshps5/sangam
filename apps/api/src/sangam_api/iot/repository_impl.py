"""
IoT Repository Implementations

SQLAlchemy implementations of sensor data access interfaces.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sangam_api.iot.models import Sensor, SensorReading, SensorAlert
from sangam_api.iot.repository import (
    SensorRepositoryInterface,
    SensorReadingRepositoryInterface,
    SensorAlertRepositoryInterface,
)


class SensorRepository(SensorRepositoryInterface):
    """SQLAlchemy implementation of sensor repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, sensor_id: UUID) -> Optional[Sensor]:
        """Get sensor by database ID."""
        result = await self.session.execute(
            select(Sensor).where(Sensor.id == sensor_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_sensor_id(self, sensor_id: str) -> Optional[Sensor]:
        """Get sensor by sensor_id string."""
        result = await self.session.execute(
            select(Sensor).where(Sensor.sensor_id == sensor_id)
        )
        return result.scalar_one_or_none()
    
    async def list_sensors(
        self,
        skip: int = 0,
        limit: int = 50,
        sensor_type: Optional[str] = None,
        depot_id: Optional[UUID] = None,
        shipment_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[Sensor]:
        """List sensors with filtering."""
        query = select(Sensor)
        
        if sensor_type:
            query = query.where(Sensor.sensor_type == sensor_type)
        if depot_id:
            query = query.where(Sensor.depot_id == depot_id)
        if shipment_id:
            query = query.where(Sensor.shipment_id == shipment_id)
        if is_active is not None:
            query = query.where(Sensor.is_active == is_active)
        
        query = query.order_by(Sensor.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_sensors(
        self,
        sensor_type: Optional[str] = None,
        depot_id: Optional[UUID] = None,
        shipment_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Count sensors with filtering."""
        query = select(func.count(Sensor.id))
        
        if sensor_type:
            query = query.where(Sensor.sensor_type == sensor_type)
        if depot_id:
            query = query.where(Sensor.depot_id == depot_id)
        if shipment_id:
            query = query.where(Sensor.shipment_id == shipment_id)
        if is_active is not None:
            query = query.where(Sensor.is_active == is_active)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, sensor: Sensor) -> Sensor:
        """Create a new sensor."""
        self.session.add(sensor)
        await self.session.flush()
        await self.session.refresh(sensor)
        return sensor
    
    async def update(self, sensor: Sensor) -> Sensor:
        """Update an existing sensor."""
        await self.session.flush()
        await self.session.refresh(sensor)
        return sensor
    
    async def delete(self, sensor_id: UUID) -> bool:
        """Delete a sensor."""
        sensor = await self.get_by_id(sensor_id)
        if not sensor:
            return False
        
        await self.session.delete(sensor)
        await self.session.flush()
        return True
    
    async def update_last_seen(
        self,
        sensor_id: UUID,
        last_seen_at: datetime,
        last_reading_value: Optional[float] = None
    ) -> Optional[Sensor]:
        """Update sensor's last seen timestamp and last reading value."""
        sensor = await self.get_by_id(sensor_id)
        if not sensor:
            return None
        
        sensor.last_seen_at = last_seen_at
        if last_reading_value is not None:
            sensor.last_reading_value = last_reading_value
        
        await self.session.flush()
        await self.session.refresh(sensor)
        return sensor


class SensorReadingRepository(SensorReadingRepositoryInterface):
    """SQLAlchemy implementation of sensor reading repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, reading_id: UUID) -> Optional[SensorReading]:
        """Get reading by ID."""
        result = await self.session.execute(
            select(SensorReading).where(SensorReading.id == reading_id)
        )
        return result.scalar_one_or_none()
    
    async def list_readings(
        self,
        sensor_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SensorReading]:
        """List readings with filtering."""
        query = select(SensorReading).options(selectinload(SensorReading.sensor))
        
        if sensor_id:
            query = query.where(SensorReading.sensor_id == sensor_id)
        if start_time:
            query = query.where(SensorReading.timestamp >= start_time)
        if end_time:
            query = query.where(SensorReading.timestamp <= end_time)
        
        query = query.order_by(SensorReading.timestamp.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_readings(
        self,
        sensor_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Count readings with filtering."""
        query = select(func.count(SensorReading.id))
        
        if sensor_id:
            query = query.where(SensorReading.sensor_id == sensor_id)
        if start_time:
            query = query.where(SensorReading.timestamp >= start_time)
        if end_time:
            query = query.where(SensorReading.timestamp <= end_time)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, reading: SensorReading) -> SensorReading:
        """Create a new reading."""
        self.session.add(reading)
        await self.session.flush()
        await self.session.refresh(reading)
        return reading
    
    async def get_latest_reading(self, sensor_id: UUID) -> Optional[SensorReading]:
        """Get the most recent reading for a sensor."""
        result = await self.session.execute(
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_trend_data(
        self,
        sensor_id: UUID,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int = 60
    ) -> List[SensorReading]:
        """Get trend data for a sensor over a time range."""
        # For simplicity, return all readings in the range
        # In production, you might want to aggregate by interval
        result = await self.session.execute(
            select(SensorReading)
            .where(
                and_(
                    SensorReading.sensor_id == sensor_id,
                    SensorReading.timestamp >= start_time,
                    SensorReading.timestamp <= end_time
                )
            )
            .order_by(SensorReading.timestamp.asc())
        )
        return list(result.scalars().all())
    
    async def delete_old_readings(self, older_than: datetime) -> int:
        """Delete readings older than specified timestamp (for retention)."""
        result = await self.session.execute(
            delete(SensorReading).where(SensorReading.timestamp < older_than)
        )
        await self.session.flush()
        return result.rowcount


class SensorAlertRepository(SensorAlertRepositoryInterface):
    """SQLAlchemy implementation of sensor alert repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, alert_id: UUID) -> Optional[SensorAlert]:
        """Get alert by ID."""
        result = await self.session.execute(
            select(SensorAlert).where(SensorAlert.id == alert_id)
        )
        return result.scalar_one_or_none()
    
    async def list_alerts(
        self,
        sensor_id: Optional[UUID] = None,
        severity: Optional[str] = None,
        is_acknowledged: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SensorAlert]:
        """List alerts with filtering."""
        query = select(SensorAlert).options(selectinload(SensorAlert.sensor))
        
        if sensor_id:
            query = query.where(SensorAlert.sensor_id == sensor_id)
        if severity:
            query = query.where(SensorAlert.severity == severity)
        if is_acknowledged is not None:
            query = query.where(SensorAlert.is_acknowledged == is_acknowledged)
        if start_time:
            query = query.where(SensorAlert.triggered_at >= start_time)
        if end_time:
            query = query.where(SensorAlert.triggered_at <= end_time)
        
        query = query.order_by(SensorAlert.triggered_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_alerts(
        self,
        sensor_id: Optional[UUID] = None,
        severity: Optional[str] = None,
        is_acknowledged: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Count alerts with filtering."""
        query = select(func.count(SensorAlert.id))
        
        if sensor_id:
            query = query.where(SensorAlert.sensor_id == sensor_id)
        if severity:
            query = query.where(SensorAlert.severity == severity)
        if is_acknowledged is not None:
            query = query.where(SensorAlert.is_acknowledged == is_acknowledged)
        if start_time:
            query = query.where(SensorAlert.triggered_at >= start_time)
        if end_time:
            query = query.where(SensorAlert.triggered_at <= end_time)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, alert: SensorAlert) -> SensorAlert:
        """Create a new alert."""
        self.session.add(alert)
        await self.session.flush()
        await self.session.refresh(alert)
        return alert
    
    async def acknowledge(
        self,
        alert_id: UUID,
        acknowledged_by: UUID,
        acknowledged_at: datetime
    ) -> Optional[SensorAlert]:
        """Acknowledge an alert."""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None
        
        alert.is_acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = acknowledged_at
        
        await self.session.flush()
        await self.session.refresh(alert)
        return alert
    
    async def resolve(self, alert_id: UUID, resolved_at: datetime) -> Optional[SensorAlert]:
        """Resolve an alert."""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None
        
        alert.resolved_at = resolved_at
        
        await self.session.flush()
        await self.session.refresh(alert)
        return alert
    
    async def get_active_alerts(self, sensor_id: Optional[UUID] = None) -> List[SensorAlert]:
        """Get all active (unacknowledged) alerts."""
        query = select(SensorAlert).options(selectinload(SensorAlert.sensor))
        query = query.where(SensorAlert.is_acknowledged == False)
        
        if sensor_id:
            query = query.where(SensorAlert.sensor_id == sensor_id)
        
        query = query.order_by(SensorAlert.triggered_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

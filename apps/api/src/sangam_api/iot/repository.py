"""
IoT Repository Interfaces

Abstract interfaces for sensor data access.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sangam_api.iot.models import Sensor, SensorReading, SensorAlert


class SensorRepositoryInterface:
    """Interface for sensor data access."""
    
    async def get_by_id(self, sensor_id: UUID) -> Optional[Sensor]:
        """Get sensor by database ID."""
        raise NotImplementedError
    
    async def get_by_sensor_id(self, sensor_id: str) -> Optional[Sensor]:
        """Get sensor by sensor_id string."""
        raise NotImplementedError
    
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
        raise NotImplementedError
    
    async def count_sensors(
        self,
        sensor_type: Optional[str] = None,
        depot_id: Optional[UUID] = None,
        shipment_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Count sensors with filtering."""
        raise NotImplementedError
    
    async def create(self, sensor: Sensor) -> Sensor:
        """Create a new sensor."""
        raise NotImplementedError
    
    async def update(self, sensor: Sensor) -> Sensor:
        """Update an existing sensor."""
        raise NotImplementedError
    
    async def delete(self, sensor_id: UUID) -> bool:
        """Delete a sensor."""
        raise NotImplementedError
    
    async def update_last_seen(
        self,
        sensor_id: UUID,
        last_seen_at: datetime,
        last_reading_value: Optional[float] = None
    ) -> Optional[Sensor]:
        """Update sensor's last seen timestamp and last reading value."""
        raise NotImplementedError


class SensorReadingRepositoryInterface:
    """Interface for sensor reading data access."""
    
    async def get_by_id(self, reading_id: UUID) -> Optional[SensorReading]:
        """Get reading by ID."""
        raise NotImplementedError
    
    async def list_readings(
        self,
        sensor_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SensorReading]:
        """List readings with filtering."""
        raise NotImplementedError
    
    async def count_readings(
        self,
        sensor_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Count readings with filtering."""
        raise NotImplementedError
    
    async def create(self, reading: SensorReading) -> SensorReading:
        """Create a new reading."""
        raise NotImplementedError
    
    async def get_latest_reading(self, sensor_id: UUID) -> Optional[SensorReading]:
        """Get the most recent reading for a sensor."""
        raise NotImplementedError
    
    async def get_trend_data(
        self,
        sensor_id: UUID,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int = 60
    ) -> List[SensorReading]:
        """Get trend data for a sensor over a time range."""
        raise NotImplementedError
    
    async def delete_old_readings(self, older_than: datetime) -> int:
        """Delete readings older than specified timestamp (for retention)."""
        raise NotImplementedError


class SensorAlertRepositoryInterface:
    """Interface for sensor alert data access."""
    
    async def get_by_id(self, alert_id: UUID) -> Optional[SensorAlert]:
        """Get alert by ID."""
        raise NotImplementedError
    
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
        raise NotImplementedError
    
    async def count_alerts(
        self,
        sensor_id: Optional[UUID] = None,
        severity: Optional[str] = None,
        is_acknowledged: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Count alerts with filtering."""
        raise NotImplementedError
    
    async def create(self, alert: SensorAlert) -> SensorAlert:
        """Create a new alert."""
        raise NotImplementedError
    
    async def acknowledge(
        self,
        alert_id: UUID,
        acknowledged_by: UUID,
        acknowledged_at: datetime
    ) -> Optional[SensorAlert]:
        """Acknowledge an alert."""
        raise NotImplementedError
    
    async def resolve(self, alert_id: UUID, resolved_at: datetime) -> Optional[SensorAlert]:
        """Resolve an alert."""
        raise NotImplementedError
    
    async def get_active_alerts(self, sensor_id: Optional[UUID] = None) -> List[SensorAlert]:
        """Get all active (unacknowledged) alerts."""
        raise NotImplementedError

"""
IoT Sensor Service

Core service for sensor data ingestion, processing, and alerting.
Implements the SensorProvider interface for multiple ingestion sources.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.iot.models import Sensor, SensorReading, SensorAlert
from sangam_api.iot.repository import (
    SensorRepositoryInterface,
    SensorReadingRepositoryInterface,
    SensorAlertRepositoryInterface,
)
from sangam_api.iot.schemas import (
    SensorMessageV1,
    IngestionResult,
    AlertType,
    AlertSeverity,
)
from sangam_api.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class SensorProvider(ABC):
    """
    Abstract interface for sensor data ingestion.
    
    This allows different ingestion sources (MQTT, HTTP, simulator)
    to use the same processing logic.
    """
    
    @abstractmethod
    async def ingest_message(self, message: SensorMessageV1) -> IngestionResult:
        """
        Ingest a single sensor message.
        
        Args:
            message: Validated sensor message
            
        Returns:
            IngestionResult with success status and any alerts generated
        """
        pass
    
    @abstractmethod
    async def ingest_batch(self, messages: List[SensorMessageV1]) -> List[IngestionResult]:
        """
        Ingest a batch of sensor messages.
        
        Args:
            messages: List of validated sensor messages
            
        Returns:
            List of IngestionResult for each message
        """
        pass


class SensorIngestionService(SensorProvider):
    """
    Core sensor ingestion service.
    
    Handles:
    - Message validation
    - Duplicate detection
    - Reading persistence
    - Threshold checking
    - Alert generation
    - Sensor status updates
    """
    
    def __init__(
        self,
        sensor_repo: SensorRepositoryInterface,
        reading_repo: SensorReadingRepositoryInterface,
        alert_repo: SensorAlertRepositoryInterface,
        db: AsyncSession
    ):
        self.sensor_repo = sensor_repo
        self.reading_repo = reading_repo
        self.alert_repo = alert_repo
        self.db = db
    
    async def ingest_message(self, message: SensorMessageV1) -> IngestionResult:
        """
        Ingest a single sensor message.
        
        Process:
        1. Find or validate sensor exists
        2. Check for duplicate readings
        3. Create reading record
        4. Check thresholds and generate alerts
        5. Update sensor status
        6. Commit transaction
        """
        try:
            # Step 1: Find sensor
            sensor = await self.sensor_repo.get_by_sensor_id(message.sensor_id)
            if not sensor:
                return IngestionResult(
                    success=False,
                    message=f"Sensor '{message.sensor_id}' not found",
                    error="SENSOR_NOT_FOUND"
                )
            
            if not sensor.is_active:
                return IngestionResult(
                    success=False,
                    message=f"Sensor '{message.sensor_id}' is inactive",
                    error="SENSOR_INACTIVE"
                )
            
            # Step 2: Check for duplicate (same sensor, same timestamp)
            existing = await self._check_duplicate(sensor.id, message.timestamp)
            if existing:
                logger.warning(
                    f"Duplicate reading detected for sensor {message.sensor_id} "
                    f"at {message.timestamp}"
                )
                return IngestionResult(
                    success=True,
                    reading_id=existing.id,
                    message="Duplicate reading (already exists)",
                )
            
            # Step 3: Create reading
            reading = SensorReading(
                id=uuid4(),
                sensor_id=sensor.id,
                value=message.value,
                unit=message.unit.value,
                timestamp=message.timestamp,
                quality=message.quality,
                message_version=message.version,
                raw_payload=message.model_dump(mode='json')
            )
            reading = await self.reading_repo.create(reading)
            
            # Step 4: Check thresholds and generate alerts
            alert_ids = await self._check_thresholds(sensor, reading)
            
            # Step 5: Update sensor status
            await self.sensor_repo.update_last_seen(
                sensor.id,
                message.timestamp,
                message.value
            )
            
            # Step 6: Commit
            await self.db.commit()
            
            logger.info(
                f"Successfully ingested reading for sensor {message.sensor_id}: "
                f"{message.value} {message.unit.value}"
            )
            
            return IngestionResult(
                success=True,
                reading_id=reading.id,
                alert_ids=alert_ids,
                message="Reading ingested successfully"
            )
            
        except Exception as e:
            logger.error(f"Error ingesting message: {str(e)}", exc_info=True)
            await self.db.rollback()
            return IngestionResult(
                success=False,
                message="Failed to ingest reading",
                error=str(e)
            )
    
    async def ingest_batch(self, messages: List[SensorMessageV1]) -> List[IngestionResult]:
        """
        Ingest a batch of sensor messages.
        
        Processes each message independently.
        """
        results = []
        for message in messages:
            result = await self.ingest_message(message)
            results.append(result)
        
        return results
    
    async def _check_duplicate(
        self,
        sensor_id: UUID,
        timestamp: datetime
    ) -> Optional[SensorReading]:
        """Check if a reading with the same timestamp already exists."""
        # Get latest reading for this sensor
        latest = await self.reading_repo.get_latest_reading(sensor_id)
        
        if latest and latest.timestamp == timestamp:
            return latest
        
        return None
    
    async def _check_thresholds(
        self,
        sensor: Sensor,
        reading: SensorReading
    ) -> List[UUID]:
        """
        Check if reading exceeds thresholds and generate alerts.
        
        Returns list of alert IDs created.
        """
        alert_ids = []
        
        # Check max threshold
        if sensor.max_threshold is not None and reading.value > sensor.max_threshold:
            alert = await self._create_threshold_alert(
                sensor=sensor,
                reading=reading,
                alert_type=AlertType.THRESHOLD_HIGH,
                triggered_value=reading.value,
                threshold_value=sensor.max_threshold,
                severity=self._calculate_severity(reading.value, sensor.max_threshold, is_high=True)
            )
            alert_ids.append(alert.id)
        
        # Check min threshold
        if sensor.min_threshold is not None and reading.value < sensor.min_threshold:
            alert = await self._create_threshold_alert(
                sensor=sensor,
                reading=reading,
                alert_type=AlertType.THRESHOLD_LOW,
                triggered_value=reading.value,
                threshold_value=sensor.min_threshold,
                severity=self._calculate_severity(reading.value, sensor.min_threshold, is_high=False)
            )
            alert_ids.append(alert.id)
        
        return alert_ids
    
    async def _create_threshold_alert(
        self,
        sensor: Sensor,
        reading: SensorReading,
        alert_type: AlertType,
        triggered_value: float,
        threshold_value: float,
        severity: AlertSeverity
    ) -> SensorAlert:
        """Create a threshold alert."""
        # Generate alert message
        if alert_type == AlertType.THRESHOLD_HIGH:
            message = (
                f"{sensor.name} reading ({triggered_value:.2f} {reading.unit}) "
                f"exceeds maximum threshold ({threshold_value:.2f} {reading.unit})"
            )
        else:
            message = (
                f"{sensor.name} reading ({triggered_value:.2f} {reading.unit}) "
                f"below minimum threshold ({threshold_value:.2f} {reading.unit})"
            )
        
        alert = SensorAlert(
            id=uuid4(),
            sensor_id=sensor.id,
            reading_id=reading.id,
            alert_type=alert_type.value,
            severity=severity.value,
            message=message,
            triggered_value=triggered_value,
            threshold_value=threshold_value,
            triggered_at=reading.timestamp
        )
        
        alert = await self.alert_repo.create(alert)
        
        logger.warning(
            f"Alert created for sensor {sensor.sensor_id}: "
            f"{alert_type.value} ({severity.value})"
        )
        
        return alert
    
    def _calculate_severity(
        self,
        value: float,
        threshold: float,
        is_high: bool
    ) -> AlertSeverity:
        """
        Calculate alert severity based on how far the value is from threshold.
        
        Rules:
        - >20% beyond threshold: CRITICAL
        - >10% beyond threshold: WARNING
        - Otherwise: INFO
        """
        if is_high:
            deviation_percent = ((value - threshold) / threshold) * 100
        else:
            deviation_percent = ((threshold - value) / threshold) * 100
        
        if deviation_percent > 20:
            return AlertSeverity.CRITICAL
        elif deviation_percent > 10:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO
    
    async def check_offline_sensors(self, timeout_minutes: int = 5) -> List[SensorAlert]:
        """
        Check for sensors that haven't reported recently.
        
        Args:
            timeout_minutes: Minutes since last reading to consider offline
            
        Returns:
            List of offline alerts created
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        # Get all active sensors
        sensors = await self.sensor_repo.list_sensors(is_active=True, limit=1000)
        
        offline_alerts = []
        
        for sensor in sensors:
            if sensor.last_seen_at and sensor.last_seen_at < cutoff_time:
                # Check if we already have an active offline alert
                active_alerts = await self.alert_repo.get_active_alerts(sensor.id)
                has_offline_alert = any(
                    a.alert_type == AlertType.OFFLINE.value 
                    for a in active_alerts
                )
                
                if not has_offline_alert:
                    # Create offline alert
                    minutes_offline = int(
                        (datetime.utcnow() - sensor.last_seen_at).total_seconds() / 60
                    )
                    
                    alert = SensorAlert(
                        id=uuid4(),
                        sensor_id=sensor.id,
                        alert_type=AlertType.OFFLINE.value,
                        severity=AlertSeverity.WARNING.value,
                        message=f"{sensor.name} has been offline for {minutes_offline} minutes",
                        triggered_at=sensor.last_seen_at
                    )
                    
                    alert = await self.alert_repo.create(alert)
                    offline_alerts.append(alert)
                    
                    logger.warning(
                        f"Offline alert created for sensor {sensor.sensor_id}: "
                        f"{minutes_offline} minutes"
                    )
        
        if offline_alerts:
            await self.db.commit()
        
        return offline_alerts
    
    async def cleanup_old_readings(self, retention_days: int = 30) -> int:
        """
        Delete readings older than retention period.
        
        Args:
            retention_days: Number of days to retain readings
            
        Returns:
            Number of readings deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        deleted_count = await self.reading_repo.delete_old_readings(cutoff_date)
        
        await self.db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old readings (older than {retention_days} days)")
        
        return deleted_count

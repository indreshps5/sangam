"""
IoT Router

API endpoints for IoT sensor monitoring.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db
from sangam_api.core.auth import get_current_user
from sangam_api.models.user import User
from sangam_api.iot.repository_impl import (
    SensorRepository,
    SensorReadingRepository,
    SensorAlertRepository,
)
from sangam_api.iot.service import SensorIngestionService
from sangam_api.iot.simulator import simulator
from sangam_api.iot.schemas import (
    SensorCreate,
    SensorUpdate,
    SensorResponse,
    SensorListResponse,
    SensorReadingResponse,
    SensorReadingListResponse,
    SensorTrendResponse,
    SensorReadingTrend,
    SensorAlertResponse,
    SensorAlertListResponse,
    AlertAcknowledgment,
    SensorMessageV1,
    IngestionResult,
    BatchIngestionRequest,
    BatchIngestionResponse,
    SimulatorConfig,
    SimulatorStatus,
    MQTTTopicInfo,
    SensorType,
    SensorUnit,
)

router = APIRouter(prefix="/iot", tags=["iot"])


def get_sensor_service(
    db: AsyncSession = Depends(get_db)
) -> SensorIngestionService:
    """Dependency injection for sensor service."""
    sensor_repo = SensorRepository(db)
    reading_repo = SensorReadingRepository(db)
    alert_repo = SensorAlertRepository(db)
    return SensorIngestionService(sensor_repo, reading_repo, alert_repo, db)


# ============================================================================
# Sensor Management Endpoints
# ============================================================================

@router.get("/sensors", response_model=SensorListResponse)
async def list_sensors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sensor_type: Optional[str] = None,
    depot_id: Optional[UUID] = None,
    shipment_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List sensors with filtering."""
    repo = SensorRepository(db)
    sensors = await repo.list_sensors(
        skip=skip,
        limit=limit,
        sensor_type=sensor_type,
        depot_id=depot_id,
        shipment_id=shipment_id,
        is_active=is_active
    )
    total = await repo.count_sensors(
        sensor_type=sensor_type,
        depot_id=depot_id,
        shipment_id=shipment_id,
        is_active=is_active
    )
    
    return SensorListResponse(
        items=[SensorResponse.model_validate(s) for s in sensors],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/sensors/{sensor_db_id}", response_model=SensorResponse)
async def get_sensor(
    sensor_db_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sensor by database ID."""
    repo = SensorRepository(db)
    sensor = await repo.get_by_id(sensor_db_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return SensorResponse.model_validate(sensor)


@router.post("/sensors", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(
     SensorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sensor."""
    from uuid import uuid4
    from sangam_api.iot.models import Sensor
    
    repo = SensorRepository(db)
    
    # Check if sensor_id already exists
    existing = await repo.get_by_sensor_id(data.sensor_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Sensor with ID '{data.sensor_id}' already exists"
        )
    
    sensor = Sensor(
        id=uuid4(),
        sensor_id=data.sensor_id,
        name=data.name,
        sensor_type=data.sensor_type.value,
        unit=data.unit.value,
        depot_id=data.depot_id,
        shipment_id=data.shipment_id,
        min_threshold=data.min_threshold,
        max_threshold=data.max_threshold,
        metadata=data.metadata,
        is_active=True
    )
    
    sensor = await repo.create(sensor)
    return SensorResponse.model_validate(sensor)


@router.put("/sensors/{sensor_db_id}", response_model=SensorResponse)
async def update_sensor(
    sensor_db_id: UUID,
     SensorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sensor."""
    repo = SensorRepository(db)
    sensor = await repo.get_by_id(sensor_db_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sensor, field, value)
    
    sensor = await repo.update(sensor)
    return SensorResponse.model_validate(sensor)


@router.delete("/sensors/{sensor_db_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sensor(
    sensor_db_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a sensor."""
    repo = SensorRepository(db)
    deleted = await repo.delete(sensor_db_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sensor not found")


# ============================================================================
# Sensor Readings Endpoints
# ============================================================================

@router.get("/sensors/{sensor_db_id}/readings", response_model=SensorReadingListResponse)
async def get_sensor_readings(
    sensor_db_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get readings for a sensor."""
    repo = SensorReadingRepository(db)
    readings = await repo.list_readings(
        sensor_id=sensor_db_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    total = await repo.count_readings(
        sensor_id=sensor_db_id,
        start_time=start_time,
        end_time=end_time
    )
    
    return SensorReadingListResponse(
        items=[SensorReadingResponse.model_validate(r) for r in readings],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/sensors/{sensor_db_id}/trend", response_model=SensorTrendResponse)
async def get_sensor_trend(
    sensor_db_id: UUID,
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 7 days
    interval_minutes: int = Query(60, ge=1, le=1440),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend data for a sensor."""
    sensor_repo = SensorRepository(db)
    sensor = await sensor_repo.get_by_id(sensor_db_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    reading_repo = SensorReadingRepository(db)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    readings = await reading_repo.get_trend_data(
        sensor_id=sensor_db_id,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=interval_minutes
    )
    
    # Calculate statistics
    values = [r.value for r in readings]
    
    return SensorTrendResponse(
        sensor_id=sensor.id,
        sensor_name=sensor.name,
        sensor_type=sensor.sensor_type,
        unit=sensor.unit,
        data_points=[
            SensorReadingTrend(
                timestamp=r.timestamp,
                value=r.value,
                sensor_id=r.sensor_id
            )
            for r in readings
        ],
        min_value=min(values) if values else 0,
        max_value=max(values) if values else 0,
        avg_value=sum(values) / len(values) if values else 0
    )


# ============================================================================
# Sensor Alerts Endpoints
# ============================================================================

@router.get("/alerts", response_model=SensorAlertListResponse)
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sensor_id: Optional[UUID] = None,
    severity: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List sensor alerts."""
    repo = SensorAlertRepository(db)
    alerts = await repo.list_alerts(
        sensor_id=sensor_id,
        severity=severity,
        is_acknowledged=is_acknowledged,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    total = await repo.count_alerts(
        sensor_id=sensor_id,
        severity=severity,
        is_acknowledged=is_acknowledged,
        start_time=start_time,
        end_time=end_time
    )
    
    return SensorAlertListResponse(
        items=[SensorAlertResponse.model_validate(a) for a in alerts],
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/alerts/{alert_id}/acknowledge", response_model=SensorAlertResponse)
async def acknowledge_alert(
    alert_id: UUID,
     AlertAcknowledgment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a sensor alert."""
    repo = SensorAlertRepository(db)
    alert = await repo.acknowledge(
        alert_id=alert_id,
        acknowledged_by=data.acknowledged_by,
        acknowledged_at=datetime.utcnow()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return SensorAlertResponse.model_validate(alert)


# ============================================================================
# Ingestion Endpoints
# ============================================================================

@router.post("/ingest", response_model=IngestionResult)
async def ingest_sensor_message(
    message: SensorMessageV1,
    service: SensorIngestionService = Depends(get_sensor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Manually ingest a sensor message.
    
    Useful for testing and debugging.
    In production, use MQTT ingestion.
    """
    return await service.ingest_message(message)


@router.post("/ingest/batch", response_model=BatchIngestionResponse)
async def ingest_batch_messages(
     BatchIngestionRequest,
    service: SensorIngestionService = Depends(get_sensor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Ingest a batch of sensor messages.
    
    Processes each message independently.
    """
    results = await service.ingest_batch(data.messages)
    
    return BatchIngestionResponse(
        total=len(results),
        successful=sum(1 for r in results if r.success),
        failed=sum(1 for r in results if not r.success),
        results=results
    )


# ============================================================================
# Simulator Endpoints
# ============================================================================

@router.post("/simulator/start", response_model=SimulatorStatus)
async def start_simulator(
    config: SimulatorConfig,
    service: SensorIngestionService = Depends(get_sensor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Start a sensor simulator.
    
    Generates synthetic readings at configured intervals.
    All simulated data is clearly labeled.
    """
    # Define ingestion callback
    async def ingestion_callback(message: SensorMessageV1):
        await service.ingest_message(message)
    
    status = await simulator.start_simulation(config, ingestion_callback)
    return status


@router.post("/simulator/stop/{sensor_id}")
async def stop_simulator(
    sensor_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stop a running simulator."""
    stopped = await simulator.stop_simulation(sensor_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="Simulator not running")
    return {"message": f"Simulator for {sensor_id} stopped"}


@router.get("/simulator/status", response_model=dict)
async def get_simulator_statuses(
    current_user: User = Depends(get_current_user)
):
    """Get status of all running simulators."""
    return simulator.get_all_statuses()


# ============================================================================
# MQTT Information Endpoints
# ============================================================================

@router.get("/mqtt/topics")
async def get_mqtt_topics(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about MQTT topics.
    
    Returns topic structure and example payloads.
    Does NOT expose credentials.
    """
    topics = [
        MQTTTopicInfo(
            topic="sangam/sensors/{sensor_id}/data",
            description="Sensor data readings",
            example_payload={
                "version": "1.0",
                "sensor_id": "temp-001",
                "sensor_type": "temperature",
                "value": 23.5,
                "unit": "celsius",
                "timestamp": "2024-01-15T10:30:00Z",
                "depot_id": "uuid-here",
                "quality": "good",
                "metadata": {"location": "zone-a"}
            },
            qos=1
        ),
        MQTTTopicInfo(
            topic="sangam/sensors/{sensor_id}/status",
            description="Sensor status updates",
            example_payload={
                "sensor_id": "temp-001",
                "status": "online",
                "battery_level": 85,
                "timestamp": "2024-01-15T10:30:00Z"
            },
            qos=1
        ),
        MQTTTopicInfo(
            topic="sangam/sensors/{sensor_id}/config",
            description="Sensor configuration (downlink)",
            example_payload={
                "sensor_id": "temp-001",
                "interval_seconds": 60,
                "thresholds": {
                    "min": 10.0,
                    "max": 40.0
                }
            },
            qos=1
        )
    ]
    
    return {
        "topics": [t.model_dump() for t in topics],
        "note": "Replace {sensor_id} with actual sensor identifier"
    }


# ============================================================================
# Maintenance Endpoints
# ============================================================================

@router.post("/maintenance/check-offline")
async def check_offline_sensors(
    timeout_minutes: int = Query(5, ge=1, le=60),
    service: SensorIngestionService = Depends(get_sensor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Check for offline sensors and create alerts.
    
    Can be run manually or scheduled.
    """
    alerts = await service.check_offline_sensors(timeout_minutes)
    return {
        "offline_alerts_created": len(alerts),
        "alert_ids": [str(a.id) for a in alerts]
    }


@router.post("/maintenance/cleanup-readings")
async def cleanup_old_readings(
    retention_days: int = Query(30, ge=1, le=365),
    service: SensorIngestionService = Depends(get_sensor_service),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up old sensor readings.
    
    Deletes readings older than retention period.
    """
    deleted_count = await service.cleanup_old_readings(retention_days)
    return {
        "deleted_count": deleted_count,
        "retention_days": retention_days
    }

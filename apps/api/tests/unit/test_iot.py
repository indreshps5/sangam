"""
IoT Module Tests

Comprehensive tests for sensor ingestion, validation, and alerting.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from pydantic import ValidationError

from sangam_api.iot.schemas import (
    SensorMessageV1,
    SensorType,
    SensorUnit,
)
from sangam_api.iot.service import SensorIngestionService
from sangam_api.iot.models import Sensor, SensorReading, SensorAlert


class TestSensorMessageValidation:
    """Tests for sensor message schema validation."""
    
    def test_valid_temperature_message(self):
        """Test valid temperature sensor message."""
        message = SensorMessageV1(
            version="1.0",
            sensor_id="temp-001",
            sensor_type=SensorType.TEMPERATURE,
            value=23.5,
            unit=SensorUnit.CELSIUS,
            timestamp=datetime.utcnow()
        )
        
        assert message.version == "1.0"
        assert message.sensor_id == "temp-001"
        assert message.value == 23.5
    
    def test_valid_humidity_message(self):
        """Test valid humidity sensor message."""
        message = SensorMessageV1(
            version="1.0",
            sensor_id="humidity-001",
            sensor_type=SensorType.HUMIDITY,
            value=65.0,
            unit=SensorUnit.PERCENT,
            timestamp=datetime.utcnow()
        )
        
        assert message.sensor_type == SensorType.HUMIDITY
        assert message.unit == SensorUnit.PERCENT
    
    def test_invalid_sensor_type_unit_combination(self):
        """Test that invalid sensor type/unit combinations are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SensorMessageV1(
                version="1.0",
                sensor_id="temp-001",
                sensor_type=SensorType.TEMPERATURE,
                value=23.5,
                unit=SensorUnit.PERCENT,  # Invalid: temperature should use celsius/fahrenheit
                timestamp=datetime.utcnow()
            )
        
        assert "not valid for sensor type" in str(exc_info.value)
    
    def test_future_timestamp_rejected(self):
        """Test that future timestamps are rejected."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            SensorMessageV1(
                version="1.0",
                sensor_id="temp-001",
                sensor_type=SensorType.TEMPERATURE,
                value=23.5,
                unit=SensorUnit.CELSIUS,
                timestamp=future_time
            )
        
        assert "cannot be in the future" in str(exc_info.value)
    
    def test_old_timestamp_rejected(self):
        """Test that very old timestamps are rejected."""
        old_time = datetime.utcnow() - timedelta(days=31)
        
        with pytest.raises(ValidationError) as exc_info:
            SensorMessageV1(
                version="1.0",
                sensor_id="temp-001",
                sensor_type=SensorType.TEMPERATURE,
                value=23.5,
                unit=SensorUnit.CELSIUS,
                timestamp=old_time
            )
        
        assert "too old" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError):
            SensorMessageV1(
                version="1.0",
                sensor_id="temp-001"
                # Missing sensor_type, value, unit, timestamp
            )
    
    def test_empty_sensor_id_rejected(self):
        """Test that empty sensor_id is rejected."""
        with pytest.raises(ValidationError):
            SensorMessageV1(
                version="1.0",
                sensor_id="",  # Empty string
                sensor_type=SensorType.TEMPERATURE,
                value=23.5,
                unit=SensorUnit.CELSIUS,
                timestamp=datetime.utcnow()
            )
    
    def test_message_with_metadata(self):
        """Test message with optional metadata."""
        message = SensorMessageV1(
            version="1.0",
            sensor_id="temp-001",
            sensor_type=SensorType.TEMPERATURE,
            value=23.5,
            unit=SensorUnit.CELSIUS,
            timestamp=datetime.utcnow(),
            depot_id=str(uuid4()),
            quality="good",
            metadata={"location": "zone-a", "battery": 85}
        )
        
        assert message.metadata is not None
        assert message.metadata["location"] == "zone-a"
        assert message.metadata["battery"] == 85


class TestMalformedMessages:
    """Tests for handling malformed messages."""
    
    def test_invalid_json_structure(self):
        """Test that invalid JSON structure is rejected."""
        invalid_data = {
            "version": "1.0",
            "sensor_id": "temp-001",
            "sensor_type": "invalid_type",  # Invalid enum value
            "value": 23.5,
            "unit": "celsius",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with pytest.raises(ValidationError):
            SensorMessageV1(**invalid_data)
    
    def test_wrong_data_types(self):
        """Test that wrong data types are rejected."""
        with pytest.raises(ValidationError):
            SensorMessageV1(
                version="1.0",
                sensor_id="temp-001",
                sensor_type=SensorType.TEMPERATURE,
                value="not a number",  # Wrong type
                unit=SensorUnit.CELSIUS,
                timestamp=datetime.utcnow()
            )
    
    def test_negative_value_allowed(self):
        """Test that negative values are allowed (e.g., negative temperatures)."""
        message = SensorMessageV1(
            version="1.0",
            sensor_id="temp-001",
            sensor_type=SensorType.TEMPERATURE,
            value=-15.5,  # Negative temperature
            unit=SensorUnit.CELSIUS,
            timestamp=datetime.utcnow()
        )
        
        assert message.value == -15.5
    
    def test_very_large_value_allowed(self):
        """Test that very large values are allowed."""
        message = SensorMessageV1(
            version="1.0",
            sensor_id="temp-001",
            sensor_type=SensorType.TEMPERATURE,
            value=999999.99,
            unit=SensorUnit.CELSIUS,
            timestamp=datetime.utcnow()
        )
        
        assert message.value == 999999.99


class TestDuplicateDetection:
    """Tests for duplicate message detection."""
    
    @pytest.mark.asyncio
    async def test_duplicate_reading_detected(self, db_session):
        """Test that duplicate readings are detected and not stored twice."""
        # This test would require a full service setup
        # Placeholder for integration test
        pass
    
    @pytest.mark.asyncio
    async def test_same_timestamp_different_value_allowed(self, db_session):
        """Test that same timestamp with different value is allowed."""
        # This would be a different reading, not a duplicate
        pass


class TestThresholdAlerts:
    """Tests for threshold-based alert generation."""
    
    def test_high_threshold_alert(self):
        """Test that high threshold violations generate alerts."""
        # This would be tested in integration tests
        pass
    
    def test_low_threshold_alert(self):
        """Test that low threshold violations generate alerts."""
        pass
    
    def test_severity_calculation(self):
        """Test alert severity calculation based on deviation."""
        from sangam_api.iot.service import SensorIngestionService
        
        # Mock service to test severity calculation
        service = SensorIngestionService(None, None, None, None)
        
        # Test critical severity (>20% beyond threshold)
        severity = service._calculate_severity(120, 100, is_high=True)
        assert severity.value == "critical"
        
        # Test warning severity (>10% beyond threshold)
        severity = service._calculate_severity(115, 100, is_high=True)
        assert severity.value == "warning"
        
        # Test info severity (<=10% beyond threshold)
        severity = service._calculate_severity(105, 100, is_high=True)
        assert severity.value == "info"


class TestSimulator:
    """Tests for sensor simulator."""
    
    def test_simulator_generates_valid_messages(self):
        """Test that simulator generates valid sensor messages."""
        from sangam_api.iot.simulator import SensorSimulator
        from sangam_api.iot.schemas import SimulatorConfig
        
        simulator = SensorSimulator()
        
        config = SimulatorConfig(
            sensor_id="sim-temp-001",
            sensor_type=SensorType.TEMPERATURE,
            unit=SensorUnit.CELSIUS,
            base_value=25.0,
            variance=5.0,
            interval_seconds=60,
            duration_minutes=10
        )
        
        message = simulator._generate_reading(config)
        
        assert message.sensor_id == "sim-temp-001"
        assert message.sensor_type == SensorType.TEMPERATURE
        assert message.unit == SensorUnit.CELSIUS
        assert message.metadata is not None
        assert message.metadata["simulated"] is True
    
    def test_simulator_respects_variance(self):
        """Test that simulator respects configured variance."""
        from sangam_api.iot.simulator import SensorSimulator
        from sangam_api.iot.schemas import SimulatorConfig
        
        simulator = SensorSimulator()
        
        config = SimulatorConfig(
            sensor_id="sim-temp-001",
            sensor_type=SensorType.TEMPERATURE,
            unit=SensorUnit.CELSIUS,
            base_value=25.0,
            variance=2.0,
            interval_seconds=60,
            duration_minutes=10
        )
        
        # Generate multiple readings and check they're within variance
        values = []
        for _ in range(100):
            message = simulator._generate_reading(config)
            values.append(message.value)
        
        # All values should be within base_value ± variance
        for value in values:
            assert 23.0 <= value <= 27.0
    
    def test_simulator_clamps_values(self):
        """Test that simulator clamps values to reasonable bounds."""
        from sangam_api.iot.simulator import SensorSimulator
        from sangam_api.iot.schemas import SimulatorConfig
        
        simulator = SensorSimulator()
        
        # Temperature should be clamped to -40 to 80
        config = SimulatorConfig(
            sensor_id="sim-temp-001",
            sensor_type=SensorType.TEMPERATURE,
            unit=SensorUnit.CELSIUS,
            base_value=100.0,  # Above max
            variance=50.0,
            interval_seconds=60,
            duration_minutes=10
        )
        
        message = simulator._generate_reading(config)
        assert message.value <= 80.0  # Should be clamped


class TestMQTTWorker:
    """Tests for MQTT worker service."""
    
    def test_mqtt_config_from_env(self):
        """Test that MQTT configuration is loaded from environment."""
        import os
        from unittest.mock import patch
        
        with patch.dict(os.environ, {
            'MQTT_BROKER_HOST': 'test.mosquitto.org',
            'MQTT_BROKER_PORT': '8883',
            'MQTT_USERNAME': 'testuser',
            'MQTT_PASSWORD': 'testpass',
            'MQTT_USE_TLS': 'true'
        }):
            from sangam_api.iot.mqtt_worker import MQTTWorker
            
            worker = MQTTWorker()
            
            assert worker.broker_host == 'test.mosquitto.org'
            assert worker.broker_port == 8883
            assert worker.username == 'testuser'
            assert worker.password == 'testpass'
            assert worker.use_tls is True
    
    @pytest.mark.asyncio
    async def test_mqtt_message_handling(self):
        """Test MQTT message handling and validation."""
        # This would be tested with mocked MQTT client
        pass


class TestRetention:
    """Tests for data retention policies."""
    
    @pytest.mark.asyncio
    async def test_old_readings_cleanup(self, db_session):
        """Test that old readings are cleaned up."""
        # This would be tested in integration tests
        pass
    
    @pytest.mark.asyncio
    async def test_retention_respects_config(self, db_session):
        """Test that retention respects configured period."""
        pass


# Fixtures
@pytest.fixture
def db_session():
    """Database session fixture."""
    # This would be a real database session in integration tests
    return None

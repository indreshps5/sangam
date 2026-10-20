# IoT Monitoring Module

## Overview

The IoT Monitoring module provides comprehensive sensor data ingestion, processing, and monitoring capabilities for SANGAM. It supports both real MQTT ingestion from ESP32 devices and a simulator mode for testing and demonstration.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  ESP32 Sensors  │─────▶│   MQTT Broker    │─────▶│  MQTT Worker    │
│  (Temperature,  │      │  (Mosquitto,     │      │  (Separate      │
│   Humidity, etc)│      │   EMQX, etc.)    │      │   Service)      │
└─────────────────┘      └──────────────────┘      └────────┬────────┘
                                                            │
                                                            ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React Frontend│◀─────│   FastAPI REST   │◀─────│ Sensor Service  │
│   (Monitoring   │      │   API            │      │ (Ingestion,     │
│    Dashboard)   │      │                  │      │  Validation,    │
└─────────────────┘      └──────────────────┘      │  Alerting)      │
                                                    └────────┬────────┘
                                                            │
                                                            ▼
                                                    ┌─────────────────┐
                                                    │   PostgreSQL    │
                                                    │   (Sensors,     │
                                                    │    Readings,    │
                                                    │    Alerts)      │
                                                    └─────────────────┘
```

### Key Components

1. **Sensor Models** (`iot/models.py`)
   - `Sensor`: Represents a physical or virtual sensor
   - `SensorReading`: Individual sensor readings with timestamps
   - `SensorAlert`: Threshold-based alerts

2. **Sensor Service** (`iot/service.py`)
   - Message validation
   - Duplicate detection
   - Threshold checking
   - Alert generation
   - Sensor status updates

3. **MQTT Worker** (`iot/mqtt_worker.py`)
   - Separate service for MQTT ingestion
   - Runs independently from API
   - Secure broker connection
   - Topic subscription and message handling

4. **Simulator** (`iot/simulator.py`)
   - Generates synthetic sensor data
   - Configurable patterns and intervals
   - Clearly labeled as simulated

5. **API Router** (`iot/router.py`)
   - Sensor management (CRUD)
   - Reading retrieval and trends
   - Alert management
   - Simulator control
   - MQTT topic information

## Sensor Message Schema (Version 1.0)

All sensor messages must conform to this schema:

```json
{
  "version": "1.0",
  "sensor_id": "temp-001",
  "sensor_type": "temperature",
  "value": 23.5,
  "unit": "celsius",
  "timestamp": "2024-01-15T10:30:00Z",
  "depot_id": "uuid-here",
  "shipment_id": "uuid-here",
  "quality": "good",
  "metadata": {
    "location": "zone-a",
    "battery": 85
  }
}
```

### Supported Sensor Types

| Type | Unit | Description |
|------|------|-------------|
| `temperature` | `celsius`, `fahrenheit` | Temperature measurements |
| `humidity` | `percent` | Relative humidity |
| `pressure` | `pascal` | Atmospheric pressure |
| `light` | `lux` | Light intensity |
| `motion` | `boolean` | Motion detection |
| `gas` | `ppm` | Gas concentration |
| `vibration` | `g_force` | Vibration intensity |
| `power` | `watt` | Power consumption |

### Validation Rules

1. **Timestamp**: Must be UTC, not in the future, not older than 30 days
2. **Sensor Type/Unit**: Must be a valid combination (e.g., temperature → celsius)
3. **Sensor ID**: Must be unique, 1-100 characters
4. **Value**: Any float value (negative values allowed for temperature)

## MQTT Integration

### Topic Structure

```
sangam/sensors/{sensor_id}/data      # Sensor readings
sangam/sensors/{sensor_id}/status    # Sensor status updates
sangam/sensors/{sensor_id}/config    # Configuration (downlink)
```

### Example Payloads

#### Sensor Data
```json
{
  "version": "1.0",
  "sensor_id": "temp-001",
  "sensor_type": "temperature",
  "value": 23.5,
  "unit": "celsius",
  "timestamp": "2024-01-15T10:30:00Z",
  "depot_id": "550e8400-e29b-41d4-a716-446655440000",
  "quality": "good",
  "metadata": {
    "location": "zone-a",
    "battery_level": 85
  }
}
```

#### Sensor Status
```json
{
  "sensor_id": "temp-001",
  "status": "online",
  "battery_level": 85,
  "firmware_version": "1.2.3",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### MQTT Worker Configuration

Environment variables:

```bash
MQTT_BROKER_HOST=broker.example.com
MQTT_BROKER_PORT=8883
MQTT_USERNAME=sangam_worker
MQTT_PASSWORD=secure_password_here
MQTT_USE_TLS=true
MQTT_TOPIC_PREFIX=sangam/sensors
MQTT_CLIENT_ID=sangam_iot_worker
MQTT_QOS=1
```

### Running the MQTT Worker

The MQTT worker runs as a separate service:

```bash
# From the apps/api directory
python -m sangam_api.iot.mqtt_worker
```

Or with Docker:

```bash
docker run -d \
  --name sangam-mqtt-worker \
  -e MQTT_BROKER_HOST=broker.example.com \
  -e MQTT_BROKER_PORT=8883 \
  -e MQTT_USERNAME=sangam_worker \
  -e MQTT_PASSWORD=secure_password_here \
  -e MQTT_USE_TLS=true \
  sangam/mqtt-worker:latest
```

**Important**: The MQTT worker must run as a persistent service, not in serverless functions.

## API Endpoints

### Sensor Management

#### List Sensors
```http
GET /api/v1/iot/sensors
```

**Query Parameters:**
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 50, max: 100)
- `sensor_type`: Filter by sensor type
- `depot_id`: Filter by depot
- `shipment_id`: Filter by shipment
- `is_active`: Filter by active status

#### Get Sensor
```http
GET /api/v1/iot/sensors/{sensor_db_id}
```

#### Create Sensor
```http
POST /api/v1/iot/sensors
```

**Request Body:**
```json
{
  "sensor_id": "temp-001",
  "name": "Mumbai Warehouse Temperature",
  "sensor_type": "temperature",
  "unit": "celsius",
  "depot_id": "uuid-here",
  "min_threshold": 10.0,
  "max_threshold": 40.0,
  "metadata": {
    "location": "zone-a",
    "manufacturer": "ESP32"
  }
}
```

#### Update Sensor
```http
PUT /api/v1/iot/sensors/{sensor_db_id}
```

#### Delete Sensor
```http
DELETE /api/v1/iot/sensors/{sensor_db_id}
```

### Sensor Readings

#### Get Readings
```http
GET /api/v1/iot/sensors/{sensor_db_id}/readings
```

**Query Parameters:**
- `skip`: Number of items to skip
- `limit`: Maximum items to return (max: 1000)
- `start_time`: Start of time range (ISO 8601)
- `end_time`: End of time range (ISO 8601)

#### Get Trend Data
```http
GET /api/v1/iot/sensors/{sensor_db_id}/trend
```

**Query Parameters:**
- `hours`: Time range in hours (1-168, default: 24)
- `interval_minutes`: Aggregation interval (1-1440, default: 60)

**Response:**
```json
{
  "sensor_id": "uuid",
  "sensor_name": "Mumbai Warehouse Temperature",
  "sensor_type": "temperature",
  "unit": "celsius",
  "data_points": [
    {
      "timestamp": "2024-01-15T10:00:00Z",
      "value": 23.5,
      "sensor_id": "uuid"
    }
  ],
  "min_value": 20.1,
  "max_value": 26.8,
  "avg_value": 23.2
}
```

### Alerts

#### List Alerts
```http
GET /api/v1/iot/alerts
```

**Query Parameters:**
- `skip`: Number of items to skip
- `limit`: Maximum items to return
- `sensor_id`: Filter by sensor
- `severity`: Filter by severity (info, warning, critical)
- `is_acknowledged`: Filter by acknowledgment status
- `start_time`: Start of time range
- `end_time`: End of time range

#### Acknowledge Alert
```http
POST /api/v1/iot/alerts/{alert_id}/acknowledge
```

**Request Body:**
```json
{
  "acknowledged_by": "user-uuid"
}
```

### Data Ingestion

#### Manual Ingestion (Testing)
```http
POST /api/v1/iot/ingest
```

**Request Body:**
```json
{
  "version": "1.0",
  "sensor_id": "temp-001",
  "sensor_type": "temperature",
  "value": 23.5,
  "unit": "celsius",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Batch Ingestion
```http
POST /api/v1/iot/ingest/batch
```

**Request Body:**
```json
{
  "messages": [
    {
      "version": "1.0",
      "sensor_id": "temp-001",
      "sensor_type": "temperature",
      "value": 23.5,
      "unit": "celsius",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "version": "1.0",
      "sensor_id": "humidity-001",
      "sensor_type": "humidity",
      "value": 65.0,
      "unit": "percent",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Simulator

#### Start Simulator
```http
POST /api/v1/iot/simulator/start
```

**Request Body:**
```json
{
  "sensor_id": "sim-temp-001",
  "sensor_type": "temperature",
  "unit": "celsius",
  "base_value": 25.0,
  "variance": 3.0,
  "interval_seconds": 10,
  "duration_minutes": 60,
  "depot_id": "uuid-here"
}
```

#### Stop Simulator
```http
POST /api/v1/iot/simulator/stop/{sensor_id}
```

#### Get Simulator Status
```http
GET /api/v1/iot/simulator/status
```

### Maintenance

#### Check Offline Sensors
```http
POST /api/v1/iot/maintenance/check-offline
```

**Query Parameters:**
- `timeout_minutes`: Minutes since last reading (default: 5)

#### Cleanup Old Readings
```http
POST /api/v1/iot/maintenance/cleanup-readings
```

**Query Parameters:**
- `retention_days`: Days to retain (default: 30)

## Simulator

The simulator generates synthetic sensor readings for testing and demonstration.

### Features

- Configurable base value and variance
- Sensor-specific patterns (e.g., daily temperature cycles)
- Realistic quality indicators
- Clearly labeled as simulated in metadata
- Configurable intervals and duration

### Example Usage

```python
from sangam_api.iot.simulator import simulator
from sangam_api.iot.schemas import SimulatorConfig, SensorType, SensorUnit

config = SimulatorConfig(
    sensor_id="sim-temp-001",
    sensor_type=SensorType.TEMPERATURE,
    unit=SensorUnit.CELSIUS,
    base_value=25.0,
    variance=3.0,
    interval_seconds=10,
    duration_minutes=60,
    depot_id="uuid-here"
)

# Start simulation
status = await simulator.start_simulation(config, ingestion_callback)

# Check status
status = simulator.get_status("sim-temp-001")

# Stop simulation
await simulator.stop_simulation("sim-temp-001")
```

### Simulated Patterns

- **Temperature**: Daily cycle with peak at 2 PM
- **Humidity**: Inversely related to temperature
- **Other sensors**: Random variance around base value

## Security

### MQTT Security

1. **Authentication**: Username/password authentication
2. **TLS**: Encrypted connections (recommended for production)
3. **Topic Permissions**: ACL-based access control
4. **Credentials**: Stored in environment variables, never in code

### API Security

1. **Authentication**: All endpoints require JWT authentication
2. **Authorization**: Role-based access control
3. **Validation**: Strict schema validation for all inputs
4. **Rate Limiting**: Consider implementing rate limits for ingestion endpoints

### Best Practices

1. **Never expose MQTT credentials** to the frontend
2. **Use TLS** for all MQTT connections in production
3. **Implement topic-level ACLs** to restrict sensor access
4. **Rotate credentials** regularly
5. **Monitor** for unusual patterns or unauthorized access attempts

## Data Retention

### Default Retention Policy

- **Sensor Readings**: 30 days
- **Sensor Alerts**: 90 days
- **Sensor Metadata**: Indefinite

### Cleanup

Run the cleanup endpoint periodically:

```bash
curl -X POST "http://localhost:8000/api/v1/iot/maintenance/cleanup-readings?retention_days=30"
```

Or schedule it with cron:

```bash
# Run daily at 2 AM
0 2 * * * curl -X POST "http://localhost:8000/api/v1/iot/maintenance/cleanup-readings?retention_days=30"
```

## ESP32 Integration

### Example ESP32 Code (Arduino)

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "your-ssid";
const char* password = "your-password";

// MQTT credentials
const char* mqtt_server = "broker.example.com";
const int mqtt_port = 8883;
const char* mqtt_user = "esp32-sensor-001";
const char* mqtt_pass = "secure-password";

// Sensor setup
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

WiFiClientSecure espClient;
PubSubClient client(espClient);

String sensor_id = "temp-001";
String depot_id = "550e8400-e29b-41d4-a716-446655440000";

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // WiFi connection
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  // MQTT TLS setup
  espClient.setInsecure(); // For testing only! Use proper certificates in production
  client.setServer(mqtt_server, mqtt_port);
  client.setCredentials(mqtt_user, mqtt_pass);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Read sensor
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["version"] = "1.0";
  doc["sensor_id"] = sensor_id;
  doc["sensor_type"] = "temperature";
  doc["value"] = temperature;
  doc["unit"] = "celsius";
  doc["timestamp"] = getTimestamp();
  doc["depot_id"] = depot_id;
  doc["quality"] = "good";
  
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  
  // Publish to MQTT
  String topic = "sangam/sensors/" + sensor_id + "/data";
  client.publish(topic.c_str(), jsonBuffer);
  
  // Wait before next reading
  delay(60000); // 60 seconds
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("esp32-client")) {
      Serial.println("Connected!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

String getTimestamp() {
  // Implement NTP time sync
  // Return ISO 8601 timestamp
  return "2024-01-15T10:30:00Z";
}
```

### Production Considerations

1. **Use proper TLS certificates** (not `setInsecure()`)
2. **Implement NTP time synchronization** for accurate timestamps
3. **Add retry logic** for failed connections
4. **Implement watchdog timers** for reliability
5. **Use deep sleep** for battery-powered devices
6. **Implement OTA updates** for firmware updates

## Testing

### Running Tests

```bash
# Unit tests
pytest apps/api/tests/unit/test_iot.py -v

# Integration tests (requires database)
pytest apps/api/tests/integration/test_iot.py -v
```

### Test Coverage

- ✅ Schema validation
- ✅ Malformed message handling
- ✅ Duplicate detection
- ✅ Threshold alerts
- ✅ Simulator functionality
- ✅ MQTT configuration
- ✅ Data retention

## Troubleshooting

### Common Issues

1. **Sensor not found**
   - Ensure sensor is created before ingesting data
   - Check sensor_id matches exactly

2. **Timestamp validation failed**
   - Ensure timestamps are in UTC
   - Check device clock synchronization
   - Verify timestamp is not in the future or too old

3. **MQTT connection failed**
   - Verify broker host and port
   - Check credentials
   - Verify TLS configuration
   - Check network connectivity

4. **Simulator not generating data**
   - Check simulator is running (`GET /iot/simulator/status`)
   - Verify sensor exists
   - Check logs for errors

### Logs

Check application logs for detailed error messages:

```bash
# API logs
tail -f logs/api.log

# MQTT worker logs
tail -f logs/mqtt_worker.log
```

## Performance Considerations

### High-Volume Ingestion

1. **Batch ingestion**: Use `/ingest/batch` for multiple readings
2. **Database indexing**: Ensure proper indexes on timestamp and sensor_id
3. **Connection pooling**: Use connection pooling for database access
4. **Async processing**: MQTT worker processes messages asynchronously

### Storage Optimization

1. **Data retention**: Regularly clean up old readings
2. **Aggregation**: Store aggregated data for long-term trends
3. **Partitioning**: Consider time-based partitioning for large datasets

## Future Enhancements

1. **Real-time WebSocket updates** for live monitoring
2. **Advanced analytics** and anomaly detection
3. **Predictive maintenance** based on sensor patterns
4. **Multi-tenancy** support for different organizations
5. **Edge computing** for local processing
6. **Machine learning** for pattern recognition
7. **Integration with forecasting** module for demand prediction
8. **Automated response** actions based on alerts

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Check application logs
- Contact the development team

---

**Note**: This module is designed for production use but should be thoroughly tested in your specific environment before deployment.

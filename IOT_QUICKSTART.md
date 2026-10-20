# IoT Monitoring Module - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- MQTT Broker (optional, for real devices)

## 1. Setup Backend

### Install Dependencies

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add:

```bash
# MQTT Configuration (optional for testing)
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_USE_TLS=false
MQTT_TOPIC_PREFIX=sangam/sensors
```

### Start Database

```bash
# Using Docker
docker-compose -f infra/docker/docker-compose.yml up -d postgres

# Or use existing PostgreSQL
```

### Seed Database

```bash
python -m sangam_api.scripts.seed
```

### Start API Server

```bash
uvicorn sangam_api.main:app --reload --port 8000
```

API will be available at: http://localhost:8000

## 2. Setup Frontend

```bash
# From project root
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## 3. Access IoT Monitoring

1. Login with demo credentials:
   - Email: `admin@sangam.dev`
   - Password: `admin123!`

2. Navigate to: http://localhost:3000/iot

## 4. Quick Test with Simulator

### Start a Temperature Simulator

```bash
curl -X POST http://localhost:8000/api/v1/iot/simulator/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sim-temp-001",
    "sensor_type": "temperature",
    "unit": "celsius",
    "base_value": 25.0,
    "variance": 3.0,
    "interval_seconds": 10,
    "duration_minutes": 60
  }'
```

### Check Simulator Status

```bash
curl http://localhost:8000/api/v1/iot/simulator/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View in UI

Refresh the IoT monitoring page to see the simulated sensor and its readings.

## 5. Create a Real Sensor

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/iot/sensors \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "temp-warehouse-001",
    "name": "Mumbai Warehouse Temperature",
    "sensor_type": "temperature",
    "unit": "celsius",
    "depot_id": "DEPOT_UUID_HERE",
    "min_threshold": 10.0,
    "max_threshold": 40.0,
    "metadata": {
      "location": "zone-a",
      "manufacturer": "ESP32"
    }
  }'
```

### Via UI

1. Go to IoT Monitoring page
2. Click "Add Sensor" (if available) or use API
3. Fill in sensor details
4. Set thresholds for alerts

## 6. Test MQTT Ingestion (Optional)

### Install Mosquitto Client

```bash
# Ubuntu/Debian
sudo apt-get install mosquitto-clients

# macOS
brew install mosquitto
```

### Start MQTT Worker

```bash
# In a separate terminal
python -m sangam_api.iot.mqtt_worker
```

### Publish Test Message

```bash
mosquitto_pub -h localhost -p 1883 \
  -t "sangam/sensors/temp-warehouse-001/data" \
  -m '{
    "version": "1.0",
    "sensor_id": "temp-warehouse-001",
    "sensor_type": "temperature",
    "value": 23.5,
    "unit": "celsius",
    "timestamp": "2024-01-15T10:30:00Z",
    "quality": "good"
  }'
```

### View in UI

Refresh the IoT monitoring page to see the new reading.

## 7. Test Alerts

### Create Sensor with Thresholds

```bash
curl -X POST http://localhost:8000/api/v1/iot/sensors \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "temp-alert-test",
    "name": "Alert Test Sensor",
    "sensor_type": "temperature",
    "unit": "celsius",
    "min_threshold": 20.0,
    "max_threshold": 30.0
  }'
```

### Send Reading That Triggers Alert

```bash
curl -X POST http://localhost:8000/api/v1/iot/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0",
    "sensor_id": "temp-alert-test",
    "sensor_type": "temperature",
    "value": 35.0,
    "unit": "celsius",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### View Alerts

Navigate to the "Alerts" tab in the IoT monitoring page to see the threshold alert.

## 8. View Trends

1. Select a sensor from the list
2. View the trend chart
3. Change time range (6h, 24h, 48h, 7d)
4. Analyze patterns

## 9. Common Operations

### List All Sensors

```bash
curl http://localhost:8000/api/v1/iot/sensors \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Sensor Readings

```bash
curl "http://localhost:8000/api/v1/iot/sensors/SENSOR_DB_ID/readings?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Trend Data

```bash
curl "http://localhost:8000/api/v1/iot/sensors/SENSOR_DB_ID/trend?hours=24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Alerts

```bash
curl "http://localhost:8000/api/v1/iot/alerts?is_acknowledged=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Acknowledge Alert

```bash
curl -X POST http://localhost:8000/api/v1/iot/alerts/ALERT_ID/acknowledge \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "acknowledged_by": "USER_UUID"
  }'
```

### Check Offline Sensors

```bash
curl -X POST "http://localhost:8000/api/v1/iot/maintenance/check-offline?timeout_minutes=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Cleanup Old Readings

```bash
curl -X POST "http://localhost:8000/api/v1/iot/maintenance/cleanup-readings?retention_days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 10. ESP32 Quick Setup

### Arduino Code Template

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

const char* ssid = "your-wifi-ssid";
const char* password = "your-wifi-password";
const char* mqtt_server = "your-broker.com";
const int mqtt_port = 1883;
const char* mqtt_user = "esp32-sensor";
const char* mqtt_pass = "your-password";

#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

String sensor_id = "esp32-temp-001";

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCredentials(mqtt_user, mqtt_pass);
}

void loop() {
  if (!client.connected()) {
    client.connect("esp32-client");
  }
  client.loop();
  
  float temp = dht.readTemperature();
  
  StaticJsonDocument<256> doc;
  doc["version"] = "1.0";
  doc["sensor_id"] = sensor_id;
  doc["sensor_type"] = "temperature";
  doc["value"] = temp;
  doc["unit"] = "celsius";
  doc["timestamp"] = getISOTime();
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  client.publish("sangam/sensors/esp32-temp-001/data", buffer);
  
  delay(60000); // 1 minute
}

String getISOTime() {
  // Implement NTP time sync
  return "2024-01-15T10:30:00Z";
}
```

## 11. Troubleshooting

### Sensor Not Appearing
- Check sensor is created via API
- Verify sensor_id matches exactly
- Check API logs for errors

### No Readings Showing
- Verify sensor is active
- Check MQTT worker is running (if using MQTT)
- Check simulator is running (if using simulator)
- Review API logs for ingestion errors

### Alerts Not Triggering
- Verify thresholds are set correctly
- Check reading value exceeds threshold
- Review alert creation logs

### MQTT Connection Issues
- Verify broker host and port
- Check credentials
- Verify network connectivity
- Check TLS configuration

### Simulator Not Working
- Check simulator status via API
- Verify sensor exists
- Check API logs for errors

## 12. Next Steps

1. **Explore the UI**: Navigate through all tabs and features
2. **Create more sensors**: Test different sensor types
3. **Configure thresholds**: Set up alerts for your use case
4. **Test with ESP32**: Connect real hardware
5. **Set up MQTT broker**: For production use
6. **Configure retention**: Set up data cleanup
7. **Monitor performance**: Check ingestion rates
8. **Review alerts**: Test alert workflows

## 13. API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 14. Additional Resources

- **Full Documentation**: `docs/IOT_MODULE.md`
- **Implementation Details**: `IOT_IMPLEMENTATION.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Tests**: `apps/api/tests/unit/test_iot.py`

---

**You're all set!** 🎉

The IoT Monitoring system is ready to use with simulators, real devices, and comprehensive monitoring capabilities.

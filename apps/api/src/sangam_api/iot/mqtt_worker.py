"""
MQTT Worker Service

Separate worker service for MQTT ingestion.
This runs as a standalone process, not in serverless functions.

Deployment:
- Run as a separate service/container
- Connects to MQTT broker with secure credentials
- Validates and ingests sensor messages
- Never exposes credentials to frontend

Configuration via environment variables:
- MQTT_BROKER_HOST
- MQTT_BROKER_PORT
- MQTT_USERNAME
- MQTT_PASSWORD
- MQTT_USE_TLS
- MQTT_TOPIC_PREFIX
"""

import asyncio
import json
import logging
import os
import signal
import sys
from typing import Optional

from pydantic import ValidationError

# Note: In production, you would install paho-mqtt
# pip install paho-mqtt
# import paho.mqtt.client as mqtt

from sangam_api.iot.schemas import SensorMessageV1
from sangam_api.iot.service import SensorIngestionService
from sangam_api.iot.repository_impl import (
    SensorRepository,
    SensorReadingRepository,
    SensorAlertRepository,
)
from sangam_api.core.database import async_session_factory

logger = logging.getLogger(__name__)


class MQTTWorker:
    """
    MQTT worker for sensor data ingestion.
    
    Connects to MQTT broker, subscribes to sensor topics,
    validates messages, and ingests them via the service layer.
    """
    
    def __init__(self):
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        self.username = os.getenv("MQTT_USERNAME")
        self.password = os.getenv("MQTT_PASSWORD")
        self.use_tls = os.getenv("MQTT_USE_TLS", "false").lower() == "true"
        self.topic_prefix = os.getenv("MQTT_TOPIC_PREFIX", "sangam/sensors")
        self.client_id = os.getenv("MQTT_CLIENT_ID", "sangam_iot_worker")
        
        self.running = False
        # self.client: Optional[mqtt.Client] = None  # Uncomment when paho-mqtt installed
    
    async def start(self):
        """Start the MQTT worker."""
        logger.info("Starting MQTT worker...")
        logger.info(f"Broker: {self.broker_host}:{self.broker_port}")
        logger.info(f"Topic prefix: {self.topic_prefix}")
        logger.info(f"TLS: {self.use_tls}")
        
        self.running = True
        
        # Initialize MQTT client
        # Uncomment when paho-mqtt is installed
        """
        self.client = mqtt.Client(client_id=self.client_id)
        
        # Set authentication if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Set TLS if enabled
        if self.use_tls:
            self.client.tls_set()
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Connect to broker
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            logger.info("MQTT client started")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            raise
        """
        
        # Keep running until stopped
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("MQTT worker cancelled")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the MQTT worker."""
        logger.info("Stopping MQTT worker...")
        self.running = False
        
        """
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client stopped")
        """
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            
            # Subscribe to sensor topics
            topic = f"{self.topic_prefix}/+/data"
            client.subscribe(topic, qos=1)
            logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker."""
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker (rc={rc})")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received."""
        # Run async handler in event loop
        asyncio.create_task(self._handle_message(msg.topic, msg.payload))
    
    async def _handle_message(self, topic: str, payload: bytes):
        """
        Handle incoming MQTT message.
        
        Validates message and ingests via service.
        """
        try:
            # Parse payload
            try:
                data = json.loads(payload.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Invalid JSON payload from topic {topic}: {str(e)}")
                return
            
            # Validate message schema
            try:
                message = SensorMessageV1(**data)
            except ValidationError as e:
                logger.error(f"Invalid sensor message from topic {topic}: {str(e)}")
                return
            
            # Ingest message
            async with async_session_factory() as session:
                sensor_repo = SensorRepository(session)
                reading_repo = SensorReadingRepository(session)
                alert_repo = SensorAlertRepository(session)
                
                service = SensorIngestionService(
                    sensor_repo=sensor_repo,
                    reading_repo=reading_repo,
                    alert_repo=alert_repo,
                    db=session
                )
                
                result = await service.ingest_message(message)
                
                if result.success:
                    logger.info(
                        f"Ingested reading from {topic}: "
                        f"sensor={message.sensor_id}, value={message.value}"
                    )
                else:
                    logger.warning(
                        f"Failed to ingest reading from {topic}: {result.message}"
                    )
        
        except Exception as e:
            logger.error(f"Error handling MQTT message: {str(e)}", exc_info=True)


async def main():
    """Main entry point for MQTT worker."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create worker
    worker = MQTTWorker()
    
    # Handle shutdown signals
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        worker.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start worker
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Worker error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

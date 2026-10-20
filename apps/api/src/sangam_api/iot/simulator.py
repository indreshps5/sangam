"""
IoT Sensor Simulator

Generates synthetic sensor readings for testing and demonstration.
All simulated data is clearly labeled as synthetic.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID

from sangam_api.iot.schemas import (
    SensorMessageV1,
    SensorType,
    SensorUnit,
    SimulatorConfig,
    SimulatorStatus,
)

logger = logging.getLogger(__name__)


class SensorSimulator:
    """
    Simulator for generating synthetic sensor readings.
    
    Generates realistic-looking sensor data with configurable patterns.
    All simulated data is clearly labeled with metadata.
    """
    
    def __init__(self):
        self._running_simulators: Dict[str, asyncio.Task] = {}
        self._simulator_stats: Dict[str, SimulatorStatus] = {}
    
    async def start_simulation(
        self,
        config: SimulatorConfig,
        ingestion_callback
    ) -> SimulatorStatus:
        """
        Start a simulation for a sensor.
        
        Args:
            config: Simulator configuration
            ingestion_callback: Async function to call with each generated message
            
        Returns:
            SimulatorStatus with current state
        """
        sensor_id = config.sensor_id
        
        # Stop existing simulator if running
        if sensor_id in self._running_simulators:
            await self.stop_simulation(sensor_id)
        
        # Create status tracker
        status = SimulatorStatus(
            sensor_id=sensor_id,
            is_running=True,
            readings_generated=0,
            started_at=datetime.utcnow(),
            last_reading_at=None
        )
        self._simulator_stats[sensor_id] = status
        
        # Start simulation task
        task = asyncio.create_task(
            self._run_simulation(config, ingestion_callback, status)
        )
        self._running_simulators[sensor_id] = task
        
        logger.info(f"Started simulation for sensor {sensor_id}")
        
        return status
    
    async def stop_simulation(self, sensor_id: str) -> bool:
        """
        Stop a running simulation.
        
        Args:
            sensor_id: Sensor ID to stop
            
        Returns:
            True if simulation was stopped, False if not running
        """
        if sensor_id not in self._running_simulators:
            return False
        
        task = self._running_simulators[sensor_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self._running_simulators[sensor_id]
        
        if sensor_id in self._simulator_stats:
            self._simulator_stats[sensor_id].is_running = False
        
        logger.info(f"Stopped simulation for sensor {sensor_id}")
        
        return True
    
    def get_status(self, sensor_id: str) -> Optional[SimulatorStatus]:
        """Get status of a simulator."""
        return self._simulator_stats.get(sensor_id)
    
    def get_all_statuses(self) -> Dict[str, SimulatorStatus]:
        """Get status of all simulators."""
        return self._simulator_stats.copy()
    
    async def _run_simulation(
        self,
        config: SimulatorConfig,
        ingestion_callback,
        status: SimulatorStatus
    ):
        """
        Run the simulation loop.
        
        Generates readings at configured intervals until duration expires.
        """
        start_time = datetime.utcnow()
        duration = timedelta(minutes=config.duration_minutes)
        
        try:
            while datetime.utcnow() - start_time < duration:
                # Generate reading
                message = self._generate_reading(config)
                
                # Call ingestion callback
                try:
                    await ingestion_callback(message)
                    status.readings_generated += 1
                    status.last_reading_at = datetime.utcnow()
                    
                    logger.debug(
                        f"Simulator generated reading for {config.sensor_id}: "
                        f"{message.value:.2f} {message.unit.value}"
                    )
                except Exception as e:
                    logger.error(f"Error in ingestion callback: {str(e)}")
                
                # Wait for next interval
                await asyncio.sleep(config.interval_seconds)
        
        except asyncio.CancelledError:
            logger.info(f"Simulation for {config.sensor_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Simulation error for {config.sensor_id}: {str(e)}")
        finally:
            status.is_running = False
    
    def _generate_reading(self, config: SimulatorConfig) -> SensorMessageV1:
        """
        Generate a synthetic sensor reading.
        
        Uses base value with random variance and optional patterns.
        """
        # Calculate value with variance
        value = config.base_value + random.uniform(-config.variance, config.variance)
        
        # Apply sensor-specific patterns
        if config.sensor_type == SensorType.TEMPERATURE:
            # Add daily temperature cycle
            hour = datetime.utcnow().hour
            daily_variation = 5 * (1 - abs(hour - 14) / 14)  # Peak at 2 PM
            value += daily_variation
        
        elif config.sensor_type == SensorType.HUMIDITY:
            # Humidity inversely related to temperature
            hour = datetime.utcnow().hour
            daily_variation = -3 * (1 - abs(hour - 14) / 14)
            value += daily_variation
        
        # Ensure value is within reasonable bounds
        value = self._clamp_value(value, config.sensor_type)
        
        # Determine quality
        quality = self._determine_quality(value, config)
        
        # Create message
        message = SensorMessageV1(
            version="1.0",
            sensor_id=config.sensor_id,
            sensor_type=config.sensor_type,
            value=round(value, 2),
            unit=config.unit,
            timestamp=datetime.utcnow(),
            depot_id=config.depot_id,
            shipment_id=config.shipment_id,
            quality=quality,
            metadata={
                "simulated": True,
                "simulator_version": "1.0",
                "base_value": config.base_value,
                "variance": config.variance
            }
        )
        
        return message
    
    def _clamp_value(self, value: float, sensor_type: SensorType) -> float:
        """Clamp value to reasonable bounds for sensor type."""
        bounds = {
            SensorType.TEMPERATURE: (-40, 80),  # Celsius
            SensorType.HUMIDITY: (0, 100),  # Percent
            SensorType.PRESSURE: (300, 1100),  # hPa
            SensorType.LIGHT: (0, 100000),  # Lux
            SensorType.MOTION: (0, 1),  # Boolean as 0/1
            SensorType.GAS: (0, 10000),  # PPM
            SensorType.VIBRATION: (0, 10),  # G-force
            SensorType.POWER: (0, 10000),  # Watts
        }
        
        min_val, max_val = bounds.get(sensor_type, (0, 100))
        return max(min_val, min(max_val, value))
    
    def _determine_quality(self, value: float, config: SimulatorConfig) -> str:
        """Determine data quality based on value."""
        # Simulate occasional bad readings
        if random.random() < 0.02:  # 2% chance
            return "warning"
        elif random.random() < 0.005:  # 0.5% chance
            return "error"
        else:
            return "good"
    
    def generate_single_reading(
        self,
        sensor_id: str,
        sensor_type: SensorType,
        unit: SensorUnit,
        base_value: float,
        variance: float = 5.0
    ) -> SensorMessageV1:
        """
        Generate a single synthetic reading (non-continuous).
        
        Useful for testing and one-off simulations.
        """
        config = SimulatorConfig(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            unit=unit,
            base_value=base_value,
            variance=variance,
            interval_seconds=60,
            duration_minutes=1
        )
        
        return self._generate_reading(config)


# Global simulator instance
simulator = SensorSimulator()

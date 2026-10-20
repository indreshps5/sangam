"""
Route Provider Interface

Abstract interface for routing and mapping providers.
Allows switching between different routing services (OSRM, MapBox, Google, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Coordinate:
    """Geographic coordinate."""
    latitude: float
    longitude: float
    
    def to_dict(self) -> Dict[str, float]:
        return {"lat": self.latitude, "lng": self.longitude}
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Coordinate':
        return cls(latitude=data["lat"], longitude=data["lng"])


@dataclass
class RouteSegment:
    """A segment of a route between two waypoints."""
    start: Coordinate
    end: Coordinate
    distance_km: float
    duration_minutes: float
    waypoints: List[Coordinate]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "distance_km": self.distance_km,
            "duration_minutes": self.duration_minutes,
            "waypoints": [wp.to_dict() for wp in self.waypoints]
        }


@dataclass
class RouteResult:
    """Result from route calculation."""
    total_distance_km: float
    total_duration_minutes: float
    segments: List[RouteSegment]
    provider: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_distance_km": self.total_distance_km,
            "total_duration_minutes": self.total_duration_minutes,
            "segments": [seg.to_dict() for seg in self.segments],
            "provider": self.provider,
            "metadata": self.metadata
        }


@dataclass
class RouteOptimizationRequest:
    """Request for route optimization."""
    origin: Coordinate
    destination: Coordinate
    waypoints: List[Coordinate]
    vehicle_type: str  # truck, car, bike, etc.
    avoid_tolls: bool = False
    avoid_highways: bool = False
    departure_time: Optional[str] = None  # ISO format


class RouteProvider(ABC):
    """
    Abstract interface for routing providers.
    
    Implementations can use:
    - OSRM (Open Source Routing Machine)
    - MapBox Directions API
    - Google Maps Directions API
    - OpenRouteService
    - Custom routing algorithms
    """
    
    @abstractmethod
    async def calculate_route(
        self,
        origin: Coordinate,
        destination: Coordinate,
        waypoints: Optional[List[Coordinate]] = None,
        vehicle_type: str = "truck"
    ) -> RouteResult:
        """
        Calculate route between points.
        
        Args:
            origin: Starting coordinate
            destination: Ending coordinate
            waypoints: Optional intermediate points
            vehicle_type: Type of vehicle (affects routing)
        
        Returns:
            RouteResult with distance, duration, and path
        """
        pass
    
    @abstractmethod
    async def calculate_matrix(
        self,
        coordinates: List[Coordinate],
        vehicle_type: str = "truck"
    ) -> List[List[Dict[str, float]]]:
        """
        Calculate distance/duration matrix between multiple points.
        
        Args:
            coordinates: List of coordinates
            vehicle_type: Type of vehicle
        
        Returns:
            Matrix where matrix[i][j] = {distance_km, duration_minutes}
            from coordinates[i] to coordinates[j]
        """
        pass
    
    @abstractmethod
    async def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the routing provider.
        
        Returns:
            Dict with provider name, version, capabilities, etc.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is currently available.
        
        Returns:
            True if provider can handle requests
        """
        pass


class SyntheticRouteProvider(RouteProvider):
    """
    Synthetic route provider for demonstration.
    
    Generates realistic-looking routes using simple calculations.
    Clearly labeled as synthetic data.
    """
    
    def __init__(self):
        self.provider_name = "SyntheticRouteProvider"
        self.version = "1.0.0"
    
    async def calculate_route(
        self,
        origin: Coordinate,
        destination: Coordinate,
        waypoints: Optional[List[Coordinate]] = None,
        vehicle_type: str = "truck"
    ) -> RouteResult:
        """
        Calculate synthetic route.
        
        Uses haversine formula for distance and estimates duration
        based on average speeds.
        """
        # Build list of points
        points = [origin]
        if waypoints:
            points.extend(waypoints)
        points.append(destination)
        
        # Calculate segments
        segments = []
        total_distance = 0.0
        total_duration = 0.0
        
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            
            # Calculate distance using haversine formula
            distance_km = self._haversine_distance(start, end)
            
            # Estimate duration based on vehicle type
            # Average speeds (km/h): truck=60, car=80, bike=30
            speed_map = {"truck": 60, "car": 80, "bike": 30}
            avg_speed = speed_map.get(vehicle_type, 60)
            
            # Add 20% overhead for stops, traffic, etc.
            duration_hours = (distance_km / avg_speed) * 1.2
            duration_minutes = duration_hours * 60
            
            # Generate intermediate waypoints for visualization
            segment_waypoints = self._generate_waypoints(start, end, num_points=5)
            
            segment = RouteSegment(
                start=start,
                end=end,
                distance_km=distance_km,
                duration_minutes=duration_minutes,
                waypoints=segment_waypoints
            )
            
            segments.append(segment)
            total_distance += distance_km
            total_duration += duration_minutes
        
        return RouteResult(
            total_distance_km=total_distance,
            total_duration_minutes=total_duration,
            segments=segments,
            provider=self.provider_name,
            metadata={
                "synthetic": True,
                "note": "Route calculated using synthetic data for demonstration",
                "vehicle_type": vehicle_type,
                "waypoint_count": len(waypoints) if waypoints else 0
            }
        )
    
    async def calculate_matrix(
        self,
        coordinates: List[Coordinate],
        vehicle_type: str = "truck"
    ) -> List[List[Dict[str, float]]]:
        """Calculate distance/duration matrix."""
        n = len(coordinates)
        matrix = [[None for _ in range(n)] for _ in range(n)]
        
        speed_map = {"truck": 60, "car": 80, "bike": 30}
        avg_speed = speed_map.get(vehicle_type, 60)
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = {"distance_km": 0.0, "duration_minutes": 0.0}
                else:
                    distance_km = self._haversine_distance(coordinates[i], coordinates[j])
                    duration_hours = (distance_km / avg_speed) * 1.2
                    duration_minutes = duration_hours * 60
                    
                    matrix[i][j] = {
                        "distance_km": distance_km,
                        "duration_minutes": duration_minutes
                    }
        
        return matrix
    
    async def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        return {
            "name": self.provider_name,
            "version": self.version,
            "type": "synthetic",
            "capabilities": [
                "route_calculation",
                "distance_matrix",
                "multi_waypoint"
            ],
            "limitations": [
                "Uses simplified calculations",
                "Does not account for real traffic",
                "Does not consider road restrictions",
                "For demonstration purposes only"
            ],
            "synthetic": True
        }
    
    def is_available(self) -> bool:
        """Synthetic provider is always available."""
        return True
    
    def _haversine_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        """
        Calculate distance between two coordinates using haversine formula.
        
        Returns distance in kilometers.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1 = radians(coord1.latitude)
        lat2 = radians(coord2.latitude)
        delta_lat = radians(coord2.latitude - coord1.latitude)
        delta_lon = radians(coord2.longitude - coord1.longitude)
        
        a = sin(delta_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    def _generate_waypoints(
        self,
        start: Coordinate,
        end: Coordinate,
        num_points: int = 5
    ) -> List[Coordinate]:
        """
        Generate intermediate waypoints between two coordinates.
        
        Creates a slightly curved path for more realistic visualization.
        """
        import random
        
        waypoints = []
        
        for i in range(1, num_points + 1):
            # Linear interpolation
            t = i / (num_points + 1)
            
            lat = start.latitude + t * (end.latitude - start.latitude)
            lng = start.longitude + t * (end.longitude - start.longitude)
            
            # Add small random offset for curve effect
            offset_scale = 0.01  # ~1km
            lat += random.uniform(-offset_scale, offset_scale)
            lng += random.uniform(-offset_scale, offset_scale)
            
            waypoints.append(Coordinate(latitude=lat, longitude=lng))
        
        return waypoints

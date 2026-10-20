"""
Canonical enumerations for the SANGAM platform.
All entities reference these enums for consistent state representation.
"""

from enum import Enum


class DepotType(str, Enum):
    """Physical classification of a depot."""
    WAREHOUSE = "warehouse"
    DISTRIBUTION_CENTER = "distribution_center"
    CROSS_DOCK = "cross_dock"
    COLD_STORAGE = "cold_storage"
    YARD = "yard"


class DepotStatus(str, Enum):
    """Operational status of a depot."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class InventoryTransactionType(str, Enum):
    """Type of inventory movement."""
    RECEIPT = "receipt"
    SHIPMENT = "shipment"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"
    COUNT_CORRECTION = "count_correction"


class ShipmentStatus(str, Enum):
    """Shipment lifecycle states."""
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    AT_HUB = "at_hub"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class RouteStatus(str, Enum):
    """Route operational status."""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RouteOptimizationObjective(str, Enum):
    """Objective for route optimization."""
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_DISTANCE = "minimize_distance"
    MINIMIZE_EMISSIONS = "minimize_emissions"
    BALANCED = "balanced"


class SensorType(str, Enum):
    """Types of IoT sensors in the supply chain."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    GPS = "gps"
    VIBRATION = "vibration"
    PRESSURE = "pressure"
    LIGHT = "light"
    DOOR_OPEN = "door_open"
    FUEL_LEVEL = "fuel_level"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(str, Enum):
    """Alert lifecycle status."""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class SimulationStatus(str, Enum):
    """Simulation scenario lifecycle."""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class RecommendationStatus(str, Enum):
    """Recommendation lifecycle."""
    GENERATED = "generated"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    EXPIRED = "expired"


class RecommendationCategory(str, Enum):
    """Category of recommendation."""
    INVENTORY_REBALANCE = "inventory_rebalance"
    ROUTE_OPTIMIZATION = "route_optimization"
    DEMAND_FORECAST = "demand_forecast"
    MAINTENANCE = "maintenance"
    PROCUREMENT = "procurement"
    CAPACITY_PLANNING = "capacity_planning"


class ApprovalStatus(str, Enum):
    """Approval record status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    WITHDRAWN = "withdrawn"


class AuditAction(str, Enum):
    """Types of auditable actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    CONFIG_CHANGE = "config_change"


class UserRole(str, Enum):
    """System roles for access control."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    ANALYST = "analyst"
    VIEWER = "viewer"
    DRIVER = "driver"
    AUDITOR = "auditor"


class ForecastModelType(str, Enum):
    """Supported forecasting model types."""
    ARIMA = "arima"
    SARIMA = "sarima"
    PROPHET = "prophet"
    XGBOOST = "xgboost"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"


class UnitOfMeasure(str, Enum):
    """Standard units of measure for validated quantities."""
    KILOGRAM = "kg"
    METRIC_TON = "mt"
    CUBIC_METER = "m3"
    LITER = "L"
    UNIT = "unit"
    PALLET = "pallet"
    CONTAINER_20FT = "container_20ft"
    CONTAINER_40FT = "container_40ft"


class TemperatureUnit(str, Enum):
    """Temperature measurement units."""
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    KELVIN = "kelvin"

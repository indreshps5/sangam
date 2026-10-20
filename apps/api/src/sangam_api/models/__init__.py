"""
Canonical entity models for the SANGAM platform.

All models use:
- UUID primary keys (uuid4)
- UTC timestamps (DateTime with timezone=True)
- Validated units and constraints
- Proper foreign keys with ON DELETE behavior
- Indexes on FK columns and common query fields

Entity relationship summary:
- Depot ←→ InventoryItem (1:N)
- Depot ←→ Shipment (1:N, both origin and destination)
- Depot ←→ Route (1:N, both origin and destination)
- Depot ←→ DemandObservation (1:N)
- Depot ←→ Forecast (1:N)
- Depot ←→ SensorReading (1:N)
- Depot ←→ Alert (1:N)
- Depot ←→ Recommendation (1:N)
- InventoryItem ←→ InventoryTransaction (1:N)
- Route ←→ Shipment (1:N)
- User ←→ Role (M:N via user_roles)
- User ←→ AuditLog (1:N)
- Forecast ←→ ForecastDataPoint (1:N)
"""

# Core entities
from sangam_api.models.depot import Depot
from sangam_api.models.user import User, Role, user_roles

# Inventory
from sangam_api.models.inventory import InventoryItem, InventoryTransaction

# Demand & Forecasting
from sangam_api.models.forecast import DemandObservation, Forecast, ForecastDataPoint

# Shipments & Routes
from sangam_api.models.shipment import Shipment, Route

# Sensors & Alerts
from sangam_api.models.sensor import SensorReading, Alert

# Simulation, Recommendations & Audit
from sangam_api.models.simulation import (
    SimulationScenario,
    Recommendation,
    ApprovalRecord,
    AuditLog,
)

__all__ = [
    # Core
    "Depot",
    "User",
    "Role",
    "user_roles",
    # Inventory
    "InventoryItem",
    "InventoryTransaction",
    # Demand & Forecasting
    "DemandObservation",
    "Forecast",
    "ForecastDataPoint",
    # Shipments & Routes
    "Shipment",
    "Route",
    # Sensors & Alerts
    "SensorReading",
    "Alert",
    # Simulation & Audit
    "SimulationScenario",
    "Recommendation",
    "ApprovalRecord",
    "AuditLog",
]

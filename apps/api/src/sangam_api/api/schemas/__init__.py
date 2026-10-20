"""
API schemas module — Pydantic models for request/response validation.
All schemas follow canonical entity definitions.
"""

# Common
from sangam_api.api.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    GeoCoordinate,
    TimestampMixin,
    IDMixin,
    HealthResponse,
    ErrorResponse,
)

# Depots
from sangam_api.api.schemas.depots import (
    DepotCreate,
    DepotUpdate,
    DepotResponse,
    DepotListResponse,
)

# Inventory
from sangam_api.api.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryItemListResponse,
    InventoryTransactionCreate,
    InventoryTransactionResponse,
    InventoryTransactionListResponse,
)

# Shipments
from sangam_api.api.schemas.shipments import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentListResponse,
)

# Routes
from sangam_api.api.schemas.routes import (
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    RouteListResponse,
)

# Forecasts & Demand
from sangam_api.api.schemas.forecasts import (
    ForecastCreate,
    ForecastDataPointCreate,
    ForecastDataPointResponse,
    ForecastResponse,
    ForecastListResponse,
    DemandObservationCreate,
    DemandObservationResponse,
    DemandObservationListResponse,
)

# Sensors & Alerts
from sangam_api.api.schemas.sensors import (
    SensorReadingCreate,
    SensorReadingResponse,
    SensorReadingListResponse,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
)

# Simulation, Recommendations, Approvals, Audit, Users
from sangam_api.api.schemas.entities import (
    SimulationScenarioCreate,
    SimulationScenarioUpdate,
    SimulationScenarioResponse,
    SimulationScenarioListResponse,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationListResponse,
    ApprovalRecordCreate,
    ApprovalRecordUpdate,
    ApprovalRecordResponse,
    ApprovalRecordListResponse,
    AuditLogCreate,
    AuditLogResponse,
    AuditLogListResponse,
    RoleCreate,
    RoleResponse,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    "GeoCoordinate",
    "TimestampMixin",
    "IDMixin",
    "HealthResponse",
    "ErrorResponse",
    # Depots
    "DepotCreate",
    "DepotUpdate",
    "DepotResponse",
    "DepotListResponse",
    # Inventory
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemResponse",
    "InventoryItemListResponse",
    "InventoryTransactionCreate",
    "InventoryTransactionResponse",
    "InventoryTransactionListResponse",
    # Shipments
    "ShipmentCreate",
    "ShipmentUpdate",
    "ShipmentResponse",
    "ShipmentListResponse",
    # Routes
    "RouteCreate",
    "RouteUpdate",
    "RouteResponse",
    "RouteListResponse",
    # Forecasts
    "ForecastCreate",
    "ForecastDataPointCreate",
    "ForecastDataPointResponse",
    "ForecastResponse",
    "ForecastListResponse",
    "DemandObservationCreate",
    "DemandObservationResponse",
    "DemandObservationListResponse",
    # Sensors & Alerts
    "SensorReadingCreate",
    "SensorReadingResponse",
    "SensorReadingListResponse",
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertListResponse",
    # Entities
    "SimulationScenarioCreate",
    "SimulationScenarioUpdate",
    "SimulationScenarioResponse",
    "SimulationScenarioListResponse",
    "RecommendationCreate",
    "RecommendationUpdate",
    "RecommendationResponse",
    "RecommendationListResponse",
    "ApprovalRecordCreate",
    "ApprovalRecordUpdate",
    "ApprovalRecordResponse",
    "ApprovalRecordListResponse",
    "AuditLogCreate",
    "AuditLogResponse",
    "AuditLogListResponse",
    "RoleCreate",
    "RoleResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
]

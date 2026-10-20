"""
Repository interfaces module.
All repository abstractions for dependency injection.
"""

from sangam_api.repositories.interfaces import (
    BaseRepositoryInterface,
    DepotRepositoryInterface,
    InventoryItemRepositoryInterface,
    InventoryTransactionRepositoryInterface,
    ShipmentRepositoryInterface,
    RouteRepositoryInterface,
    ForecastRepositoryInterface,
    DemandObservationRepositoryInterface,
    SensorReadingRepositoryInterface,
    AlertRepositoryInterface,
    SimulationScenarioRepositoryInterface,
    RecommendationRepositoryInterface,
    ApprovalRecordRepositoryInterface,
    AuditLogRepositoryInterface,
    UserRepositoryInterface,
    RoleRepositoryInterface,
)

__all__ = [
    "BaseRepositoryInterface",
    "DepotRepositoryInterface",
    "InventoryItemRepositoryInterface",
    "InventoryTransactionRepositoryInterface",
    "ShipmentRepositoryInterface",
    "RouteRepositoryInterface",
    "ForecastRepositoryInterface",
    "DemandObservationRepositoryInterface",
    "SensorReadingRepositoryInterface",
    "AlertRepositoryInterface",
    "SimulationScenarioRepositoryInterface",
    "RecommendationRepositoryInterface",
    "ApprovalRecordRepositoryInterface",
    "AuditLogRepositoryInterface",
    "UserRepositoryInterface",
    "RoleRepositoryInterface",
]

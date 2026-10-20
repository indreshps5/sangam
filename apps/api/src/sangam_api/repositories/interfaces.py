"""
Repository interfaces (abstractions) for all canonical entities.

Following the Dependency Inversion Principle (DIP):
- Services depend on these interfaces, not concrete implementations
- Enables easy testing with mock repositories
- Allows swapping data access strategies without changing business logic

All interfaces define async methods for CRUD + list operations.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sangam_api.api.schemas.depots import DepotCreate, DepotUpdate, DepotResponse
from sangam_api.api.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryTransactionCreate,
    InventoryTransactionResponse,
)
from sangam_api.api.schemas.shipments import ShipmentCreate, ShipmentUpdate, ShipmentResponse
from sangam_api.api.schemas.routes import RouteCreate, RouteUpdate, RouteResponse
from sangam_api.api.schemas.forecasts import (
    ForecastCreate,
    ForecastResponse,
    DemandObservationCreate,
    DemandObservationResponse,
)
from sangam_api.api.schemas.sensors import (
    SensorReadingCreate,
    SensorReadingResponse,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
)
from sangam_api.api.schemas.entities import (
    SimulationScenarioCreate,
    SimulationScenarioUpdate,
    SimulationScenarioResponse,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    ApprovalRecordCreate,
    ApprovalRecordUpdate,
    ApprovalRecordResponse,
    AuditLogCreate,
    AuditLogResponse,
    UserCreate,
    UserUpdate,
    UserResponse,
    RoleCreate,
    RoleResponse,
)


class BaseRepositoryInterface(ABC):
    """Base interface with common CRUD operations."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[object]:
        """Get entity by ID, returns None if not found."""
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID. Returns True if deleted, False if not found."""
        ...


class DepotRepositoryInterface(BaseRepositoryInterface):
    """Interface for depot persistence operations."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        region: Optional[str] = None,
        depot_type: Optional[str] = None,
    ) -> list[DepotResponse]:
        """List depots with pagination and optional filters."""
        ...

    @abstractmethod
    async def count(
        self,
        status: Optional[str] = None,
        region: Optional[str] = None,
        depot_type: Optional[str] = None,
    ) -> int:
        """Count depots with optional filters."""
        ...

    @abstractmethod
    async def get_by_id(self, depot_id: UUID) -> Optional[DepotResponse]:
        """Get a depot by ID."""
        ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[DepotResponse]:
        """Get a depot by its unique code."""
        ...

    @abstractmethod
    async def create(self, payload: DepotCreate) -> DepotResponse:
        """Create a new depot."""
        ...

    @abstractmethod
    async def update(self, depot_id: UUID, payload: DepotUpdate) -> Optional[DepotResponse]:
        """Update an existing depot."""
        ...

    @abstractmethod
    async def delete(self, depot_id: UUID) -> bool:
        """Delete a depot."""
        ...


class InventoryItemRepositoryInterface(BaseRepositoryInterface):
    """Interface for inventory item persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        depot_id: Optional[UUID] = None,
        category: Optional[str] = None,
    ) -> list[InventoryItemResponse]:
        """List inventory items with filters."""
        ...

    @abstractmethod
    async def count(self, depot_id: Optional[UUID] = None, category: Optional[str] = None) -> int:
        """Count inventory items."""
        ...

    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[InventoryItemResponse]:
        """Get inventory item by ID."""
        ...

    @abstractmethod
    async def get_by_sku(self, depot_id: UUID, sku: str) -> Optional[InventoryItemResponse]:
        """Get inventory item by SKU within a depot."""
        ...

    @abstractmethod
    async def create(self, payload: InventoryItemCreate) -> InventoryItemResponse:
        """Create a new inventory item."""
        ...

    @abstractmethod
    async def update(self, item_id: UUID, payload: InventoryItemUpdate) -> Optional[InventoryItemResponse]:
        """Update an inventory item."""
        ...


class InventoryTransactionRepositoryInterface(BaseRepositoryInterface):
    """Interface for inventory transaction persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        depot_id: Optional[UUID] = None,
        item_id: Optional[UUID] = None,
        transaction_type: Optional[str] = None,
    ) -> list[InventoryTransactionResponse]:
        """List transactions with filters."""
        ...

    @abstractmethod
    async def count(
        self,
        depot_id: Optional[UUID] = None,
        item_id: Optional[UUID] = None,
        transaction_type: Optional[str] = None,
    ) -> int:
        """Count transactions."""
        ...

    @abstractmethod
    async def create(self, payload: InventoryTransactionCreate) -> InventoryTransactionResponse:
        """Record a new inventory transaction."""
        ...


class ShipmentRepositoryInterface(BaseRepositoryInterface):
    """Interface for shipment persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
    ) -> list[ShipmentResponse]:
        """List shipments with filters."""
        ...

    @abstractmethod
    async def count(
        self,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
    ) -> int:
        """Count shipments."""
        ...

    @abstractmethod
    async def get_by_id(self, shipment_id: UUID) -> Optional[ShipmentResponse]:
        """Get shipment by ID."""
        ...

    @abstractmethod
    async def create(self, payload: ShipmentCreate) -> ShipmentResponse:
        """Create a new shipment."""
        ...

    @abstractmethod
    async def update(self, shipment_id: UUID, payload: ShipmentUpdate) -> Optional[ShipmentResponse]:
        """Update a shipment."""
        ...


class RouteRepositoryInterface(BaseRepositoryInterface):
    """Interface for route persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> list[RouteResponse]:
        """List routes."""
        ...

    @abstractmethod
    async def count(self, status: Optional[str] = None) -> int:
        """Count routes."""
        ...

    @abstractmethod
    async def get_by_id(self, route_id: UUID) -> Optional[RouteResponse]:
        """Get route by ID."""
        ...

    @abstractmethod
    async def create(self, payload: RouteCreate) -> RouteResponse:
        """Create a new route."""
        ...

    @abstractmethod
    async def update(self, route_id: UUID, payload: RouteUpdate) -> Optional[RouteResponse]:
        """Update a route."""
        ...


class ForecastRepositoryInterface(BaseRepositoryInterface):
    """Interface for forecast persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        depot_id: Optional[UUID] = None,
        model_type: Optional[str] = None,
    ) -> list[ForecastResponse]:
        """List forecasts."""
        ...

    @abstractmethod
    async def count(self, depot_id: Optional[UUID] = None) -> int:
        """Count forecasts."""
        ...

    @abstractmethod
    async def create(self, payload: ForecastCreate) -> ForecastResponse:
        """Create a new forecast."""
        ...


class DemandObservationRepositoryInterface(BaseRepositoryInterface):
    """Interface for demand observation persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        depot_id: Optional[UUID] = None,
        product_category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[DemandObservationResponse]:
        """List demand observations."""
        ...

    @abstractmethod
    async def count(
        self,
        depot_id: Optional[UUID] = None,
        product_category: Optional[str] = None,
    ) -> int:
        """Count demand observations."""
        ...

    @abstractmethod
    async def create(self, payload: DemandObservationCreate) -> DemandObservationResponse:
        """Record a demand observation."""
        ...


class SensorReadingRepositoryInterface(BaseRepositoryInterface):
    """Interface for sensor reading persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        device_id: Optional[str] = None,
        sensor_type: Optional[str] = None,
        depot_id: Optional[UUID] = None,
    ) -> list[SensorReadingResponse]:
        """List sensor readings."""
        ...

    @abstractmethod
    async def count(self, device_id: Optional[str] = None, sensor_type: Optional[str] = None) -> int:
        """Count sensor readings."""
        ...

    @abstractmethod
    async def create(self, payload: SensorReadingCreate) -> SensorReadingResponse:
        """Record a sensor reading."""
        ...


class AlertRepositoryInterface(BaseRepositoryInterface):
    """Interface for alert persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[AlertResponse]:
        """List alerts."""
        ...

    @abstractmethod
    async def count(self, severity: Optional[str] = None, status: Optional[str] = None) -> int:
        """Count alerts."""
        ...

    @abstractmethod
    async def create(self, payload: AlertCreate) -> AlertResponse:
        """Create an alert."""
        ...

    @abstractmethod
    async def update(self, alert_id: UUID, payload: AlertUpdate) -> Optional[AlertResponse]:
        """Update an alert."""
        ...


class SimulationScenarioRepositoryInterface(BaseRepositoryInterface):
    """Interface for simulation scenario persistence."""

    @abstractmethod
    async def list(
        self, skip: int = 0, limit: int = 20, status: Optional[str] = None
    ) -> list[SimulationScenarioResponse]:
        """List scenarios."""
        ...

    @abstractmethod
    async def count(self, status: Optional[str] = None) -> int:
        """Count scenarios."""
        ...

    @abstractmethod
    async def create(self, payload: SimulationScenarioCreate) -> SimulationScenarioResponse:
        """Create a scenario."""
        ...

    @abstractmethod
    async def update(
        self, scenario_id: UUID, payload: SimulationScenarioUpdate
    ) -> Optional[SimulationScenarioResponse]:
        """Update a scenario."""
        ...


class RecommendationRepositoryInterface(BaseRepositoryInterface):
    """Interface for recommendation persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[RecommendationResponse]:
        """List recommendations."""
        ...

    @abstractmethod
    async def count(self, category: Optional[str] = None, status: Optional[str] = None) -> int:
        """Count recommendations."""
        ...

    @abstractmethod
    async def create(self, payload: RecommendationCreate) -> RecommendationResponse:
        """Create a recommendation."""
        ...

    @abstractmethod
    async def update(
        self, rec_id: UUID, payload: RecommendationUpdate
    ) -> Optional[RecommendationResponse]:
        """Update a recommendation."""
        ...


class ApprovalRecordRepositoryInterface(BaseRepositoryInterface):
    """Interface for approval record persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> list[ApprovalRecordResponse]:
        """List approval records."""
        ...

    @abstractmethod
    async def count(self, status: Optional[str] = None) -> int:
        """Count approval records."""
        ...

    @abstractmethod
    async def create(self, payload: ApprovalRecordCreate) -> ApprovalRecordResponse:
        """Create an approval record."""
        ...

    @abstractmethod
    async def update(
        self, record_id: UUID, payload: ApprovalRecordUpdate
    ) -> Optional[ApprovalRecordResponse]:
        """Update an approval record."""
        ...


class AuditLogRepositoryInterface(BaseRepositoryInterface):
    """Interface for audit log persistence."""

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> list[AuditLogResponse]:
        """List audit logs."""
        ...

    @abstractmethod
    async def count(
        self,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
    ) -> int:
        """Count audit logs."""
        ...

    @abstractmethod
    async def create(self, payload: AuditLogCreate) -> AuditLogResponse:
        """Record an audit log entry."""
        ...


class UserRepositoryInterface(BaseRepositoryInterface):
    """Interface for user persistence."""

    @abstractmethod
    async def list(
        self, skip: int = 0, limit: int = 20, is_active: Optional[bool] = None
    ) -> list[UserResponse]:
        """List users."""
        ...

    @abstractmethod
    async def count(self, is_active: Optional[bool] = None) -> int:
        """Count users."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[UserResponse]:
        """Get user by ID."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username."""
        ...

    @abstractmethod
    async def create(self, payload: UserCreate) -> UserResponse:
        """Create a new user."""
        ...

    @abstractmethod
    async def update(self, user_id: UUID, payload: UserUpdate) -> Optional[UserResponse]:
        """Update a user."""
        ...


class RoleRepositoryInterface(BaseRepositoryInterface):
    """Interface for role persistence."""

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 20) -> list[RoleResponse]:
        """List roles."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Count roles."""
        ...

    @abstractmethod
    async def get_by_id(self, role_id: UUID) -> Optional[RoleResponse]:
        """Get role by ID."""
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[RoleResponse]:
        """Get role by name."""
        ...

    @abstractmethod
    async def create(self, payload: RoleCreate) -> RoleResponse:
        """Create a new role."""
        ...

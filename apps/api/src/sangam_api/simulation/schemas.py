"""
Simulation Schemas

Pydantic schemas for simulation API requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ScenarioType(str, Enum):
    """Types of simulation scenarios."""
    ROUTE_CLOSURE = "route_closure"
    SHIPMENT_DELAY = "shipment_delay"
    INCREASED_DEMAND = "increased_demand"
    REDUCED_STOCK = "reduced_stock"
    DELAYED_REPLENISHMENT = "delayed_replenishment"
    STORAGE_CONDITIONS = "storage_conditions"


class ScenarioStatus(str, Enum):
    """Simulation scenario status."""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Scenario Parameter Schemas
# ============================================================================

class RouteClosureParams(BaseModel):
    """Parameters for route closure simulation."""
    route_id: UUID = Field(..., description="ID of route to close")
    duration_hours: float = Field(..., gt=0, description="Duration of closure in hours")
    reason: Optional[str] = Field(None, description="Reason for closure")


class ShipmentDelayParams(BaseModel):
    """Parameters for shipment delay simulation."""
    shipment_id: UUID = Field(..., description="ID of shipment to delay")
    delay_hours: float = Field(..., gt=0, description="Delay duration in hours")
    reason: Optional[str] = Field(None, description="Reason for delay")


class IncreasedDemandParams(BaseModel):
    """Parameters for increased demand simulation."""
    inventory_item_id: UUID = Field(..., description="ID of inventory item")
    demand_increase_percent: float = Field(..., gt=0, le=500, description="Demand increase percentage")
    duration_days: int = Field(..., gt=0, le=365, description="Duration in days")


class ReducedStockParams(BaseModel):
    """Parameters for reduced stock simulation."""
    inventory_item_id: UUID = Field(..., description="ID of inventory item")
    stock_reduction_percent: float = Field(..., gt=0, le=100, description="Stock reduction percentage")
    reason: Optional[str] = Field(None, description="Reason for reduction")


class DelayedReplenishmentParams(BaseModel):
    """Parameters for delayed replenishment simulation."""
    inventory_item_id: UUID = Field(..., description="ID of inventory item")
    delay_days: int = Field(..., gt=0, le=365, description="Delay in days")
    reason: Optional[str] = Field(None, description="Reason for delay")


class StorageConditionsParams(BaseModel):
    """Parameters for storage conditions simulation."""
    depot_id: UUID = Field(..., description="ID of depot")
    temperature_change: Optional[float] = Field(None, description="Temperature change in Celsius")
    humidity_change: Optional[float] = Field(None, description="Humidity change percentage")
    duration_hours: float = Field(..., gt=0, description="Duration in hours")
    reason: Optional[str] = Field(None, description="Reason for condition change")


# ============================================================================
# Scenario Creation Schemas
# ============================================================================

class SimulationScenarioCreate(BaseModel):
    """Schema for creating a simulation scenario."""
    name: str = Field(..., min_length=1, max_length=200, description="Scenario name")
    description: Optional[str] = Field(None, max_length=2000, description="Scenario description")
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    parameters: Dict[str, Any] = Field(..., description="Scenario-specific parameters")
    is_deterministic: bool = Field(True, description="Use deterministic simulation")
    random_seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    
    @field_validator('parameters')
    @classmethod
    def validate_parameters(cls, v: Dict[str, Any], info) -> Dict[str, Any]:
        """Validate parameters based on scenario type."""
        scenario_type = info.data.get('scenario_type')
        if not scenario_type:
            return v
        
        # Validate parameters based on scenario type
        try:
            if scenario_type == ScenarioType.ROUTE_CLOSURE:
                RouteClosureParams(**v)
            elif scenario_type == ScenarioType.SHIPMENT_DELAY:
                ShipmentDelayParams(**v)
            elif scenario_type == ScenarioType.INCREASED_DEMAND:
                IncreasedDemandParams(**v)
            elif scenario_type == ScenarioType.REDUCED_STOCK:
                ReducedStockParams(**v)
            elif scenario_type == ScenarioType.DELAYED_REPLENISHMENT:
                DelayedReplenishmentParams(**v)
            elif scenario_type == ScenarioType.STORAGE_CONDITIONS:
                StorageConditionsParams(**v)
        except Exception as e:
            raise ValueError(f"Invalid parameters for {scenario_type}: {str(e)}")
        
        return v


class SimulationScenarioUpdate(BaseModel):
    """Schema for updating a simulation scenario."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    parameters: Optional[Dict[str, Any]] = None


# ============================================================================
# Result Schemas
# ============================================================================

class ShipmentImpact(BaseModel):
    """Impact on a shipment."""
    shipment_id: UUID
    tracking_number: Optional[str] = None
    baseline_arrival: Optional[datetime] = None
    simulated_arrival: Optional[datetime] = None
    delay_hours: Optional[float] = None
    status_change: Optional[str] = None
    alternative_route_id: Optional[UUID] = None
    alternative_route_name: Optional[str] = None
    impact_description: str


class InventoryImpact(BaseModel):
    """Impact on inventory."""
    inventory_item_id: UUID
    item_name: str
    sku: str
    depot_name: str
    baseline_stock: float
    simulated_stock: float
    stock_change: float
    stockout_risk: bool
    days_until_stockout: Optional[float] = None
    reorder_recommended: bool
    impact_description: str


class RouteImpact(BaseModel):
    """Impact on a route."""
    route_id: UUID
    route_name: str
    baseline_status: str
    simulated_status: str
    affected_shipments: int
    alternative_routes: List[Dict[str, Any]] = []
    impact_description: str


class SimulationResults(BaseModel):
    """Complete simulation results."""
    summary: Dict[str, Any] = Field(..., description="High-level summary")
    shipment_impacts: List[ShipmentImpact] = Field(default_factory=list)
    inventory_impacts: List[InventoryImpact] = Field(default_factory=list)
    route_impacts: List[RouteImpact] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


# ============================================================================
# Response Schemas
# ============================================================================

class SimulationScenarioResponse(BaseModel):
    """Response schema for simulation scenario."""
    id: UUID
    name: str
    description: Optional[str]
    scenario_type: str
    parameters: Dict[str, Any]
    baseline_snapshot: Optional[Dict[str, Any]]
    results: Optional[Dict[str, Any]]
    status: str
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    executed_at: Optional[datetime]
    execution_duration_ms: Optional[int]
    error_message: Optional[str]
    is_deterministic: bool
    random_seed: Optional[int]
    
    model_config = {"from_attributes": True}


class SimulationScenarioListResponse(BaseModel):
    """List of simulation scenarios."""
    items: List[SimulationScenarioResponse]
    total: int
    skip: int
    limit: int


class SimulationExecutionResponse(BaseModel):
    """Response after executing a simulation."""
    scenario_id: UUID
    status: str
    results: Optional[SimulationResults]
    execution_duration_ms: int
    message: str


class SimulationComparisonResponse(BaseModel):
    """Comparison between baseline and simulation."""
    scenario_id: UUID
    scenario_name: str
    scenario_type: str
    baseline: Dict[str, Any]
    simulated: Dict[str, Any]
    differences: Dict[str, Any]
    impact_summary: Dict[str, Any]

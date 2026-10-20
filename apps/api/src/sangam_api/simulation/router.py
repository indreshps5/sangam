"""
Simulation Router

API endpoints for what-if disruption simulation.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db
from sangam_api.core.auth import get_current_user
from sangam_api.models.user import User
from sangam_api.simulation.repository_impl import (
    SimulationScenarioRepository,
    SimulationResultRepository,
)
from sangam_api.simulation.service import SimulationService
from sangam_api.simulation.schemas import (
    SimulationScenarioCreate,
    SimulationScenarioUpdate,
    SimulationScenarioResponse,
    SimulationScenarioListResponse,
    SimulationExecutionResponse,
    SimulationComparisonResponse,
)

router = APIRouter(prefix="/simulation", tags=["simulation"])


def get_simulation_service(
    db: AsyncSession = Depends(get_db)
) -> SimulationService:
    """Dependency injection for simulation service."""
    scenario_repo = SimulationScenarioRepository(db)
    result_repo = SimulationResultRepository(db)
    return SimulationService(scenario_repo, result_repo, db)


# ============================================================================
# Scenario Management Endpoints
# ============================================================================

@router.get("/", response_model=SimulationScenarioListResponse)
async def list_scenarios(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    scenario_type: Optional[str] = Query(None, description="Filter by scenario type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    created_by: Optional[UUID] = Query(None, description="Filter by creator"),
    service: SimulationService = Depends(get_simulation_service),
    current_user: User = Depends(get_current_user)
):
    """
    List simulation scenarios with filtering and pagination.
    
    Returns all scenarios the user has access to.
    """
    scenarios, total = await service.list_scenarios(
        skip=skip,
        limit=limit,
        scenario_type=scenario_type,
        status=status,
        created_by=created_by
    )
    
    return SimulationScenarioListResponse(
        items=[SimulationScenarioResponse.model_validate(s) for s in scenarios],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{scenario_id}", response_model=SimulationScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    service: SimulationService = Depends(get_simulation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get simulation scenario by ID.
    
    Returns scenario details including parameters and results.
    """
    scenario = await service.get_scenario(scenario_id)
    return SimulationScenarioResponse.model_validate(scenario)


@router.post("/", response_model=SimulationScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
     SimulationScenarioCreate,
    service: SimulationService = Depends(get_simulation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new simulation scenario.
    
    Validates parameters based on scenario type.
    Scenario is created in 'draft' status.
    """
    scenario = await service.create_scenario(data, user_id=current_user.id)
    return SimulationScenarioResponse.model_validate(scenario)


@router.put("/{scenario_id}", response_model=SimulationScenarioResponse)
async def update_scenario(
    scenario_id: UUID,
     SimulationScenarioUpdate,
    service: SimulationService = Depends(get_simulation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update a simulation scenario.
    
    Only draft scenarios can be updated.
    """
    scenario = await service.update_scenario(scenario_id, data)
    return SimulationScenarioResponse.model_validate(scenario)


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: UUID,
    service: SimulationService = Depends(get_simulation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a simulation scenario and its results.
    
    This action cannot be undone.
    """
    deleted = await service.delete_scenario(scenario_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )


# ============================================================================
# Simulation Execution Endpoints
# ============================================================================

@router.post("/{scenario_id}/execute", response_model=SimulationExecutionResponse)
async def execute_simulation(
    scenario_id: UUID,
    service: SimulationService = Depends(get_simulation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a simulation scenario.
    
    IMPORTANT: This is a READ-ONLY operation. It does not modify:
    - Inventory stock levels
    - Shipment statuses
    - Route configurations
    - Any operational data
    
    The simulation:
    1. Captures baseline state
    2. Calculates simulated impacts
    3. Stores results for comparison
    4. Returns detailed impact analysis
    
    All calculations use synthetic/deterministic data where applicable.
    """
    try:
        results = await service.execute_simulation(scenario_id)
        
        scenario = await service.get_scenario(scenario_id)
        
        return SimulationExecutionResponse(
            scenario_id=scenario.id,
            status=scenario.status,
            results=results,
            execution_duration_ms=scenario.execution_duration_ms or 0,
            message="Simulation completed successfully. No operational data was modified."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{scenario_id}/comparison", response_model=SimulationComparisonResponse)
async def get_comparison(
    scenario_id: UUID,
    service: SimulationService = Depends(get_simulation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get comparison between baseline and simulation.
    
    Returns detailed comparison showing:
    - Baseline state
    - Simulated state
    - Key differences
    - Impact summary
    """
    comparison = await service.get_comparison(scenario_id)
    return SimulationComparisonResponse(**comparison)


# ============================================================================
# Scenario Type Information
# ============================================================================

@router.get("/types/info")
async def get_scenario_types_info():
    """
    Get information about available scenario types.
    
    Returns descriptions, parameters, and use cases for each type.
    """
    return {
        "scenario_types": [
            {
                "type": "route_closure",
                "name": "Route Closure",
                "description": "Simulates the impact of closing a transportation route",
                "parameters": {
                    "route_id": "UUID of the route to close",
                    "duration_hours": "Duration of closure in hours",
                    "reason": "Optional reason for closure"
                },
                "impacts_calculated": [
                    "Affected shipments",
                    "Estimated arrival delays",
                    "Alternative route availability",
                    "Rerouting recommendations"
                ],
                "use_cases": [
                    "Road construction",
                    "Weather-related closures",
                    "Infrastructure maintenance"
                ]
            },
            {
                "type": "shipment_delay",
                "name": "Shipment Delay",
                "description": "Simulates the impact of delaying a specific shipment",
                "parameters": {
                    "shipment_id": "UUID of the shipment to delay",
                    "delay_hours": "Delay duration in hours",
                    "reason": "Optional reason for delay"
                },
                "impacts_calculated": [
                    "New estimated arrival time",
                    "Downstream inventory impacts"
                ],
                "use_cases": [
                    "Carrier delays",
                    "Customs hold-ups",
                    "Vehicle breakdowns"
                ]
            },
            {
                "type": "increased_demand",
                "name": "Increased Demand",
                "description": "Simulates the impact of increased demand for an item",
                "parameters": {
                    "inventory_item_id": "UUID of the inventory item",
                    "demand_increase_percent": "Demand increase percentage (0-500)",
                    "duration_days": "Duration in days (1-365)"
                },
                "impacts_calculated": [
                    "Stock depletion rate",
                    "Stockout risk",
                    "Reorder recommendations",
                    "Days until stockout"
                ],
                "use_cases": [
                    "Seasonal demand spikes",
                    "Promotional campaigns",
                    "Market surge"
                ]
            },
            {
                "type": "reduced_stock",
                "name": "Reduced Stock",
                "description": "Simulates the impact of sudden stock reduction",
                "parameters": {
                    "inventory_item_id": "UUID of the inventory item",
                    "stock_reduction_percent": "Stock reduction percentage (0-100)",
                    "reason": "Optional reason for reduction"
                },
                "impacts_calculated": [
                    "Immediate stock levels",
                    "Stockout risk",
                    "Reorder urgency"
                ],
                "use_cases": [
                    "Damage or spoilage",
                    "Theft or loss",
                    "Quality issues"
                ]
            },
            {
                "type": "delayed_replenishment",
                "name": "Delayed Replenishment",
                "description": "Simulates the impact of delayed inventory replenishment",
                "parameters": {
                    "inventory_item_id": "UUID of the inventory item",
                    "delay_days": "Delay in days (1-365)",
                    "reason": "Optional reason for delay"
                },
                "impacts_calculated": [
                    "Stock depletion timeline",
                    "Stockout risk",
                    "Days until stockout"
                ],
                "use_cases": [
                    "Supplier delays",
                    "Shipping disruptions",
                    "Production issues"
                ]
            },
            {
                "type": "storage_conditions",
                "name": "Storage Conditions",
                "description": "Simulates the impact of changed storage conditions",
                "parameters": {
                    "depot_id": "UUID of the depot",
                    "temperature_change": "Temperature change in Celsius",
                    "humidity_change": "Humidity change percentage",
                    "duration_hours": "Duration in hours",
                    "reason": "Optional reason for condition change"
                },
                "impacts_calculated": [
                    "Affected inventory items",
                    "Quality degradation",
                    "Potential losses"
                ],
                "use_cases": [
                    "HVAC failure",
                    "Power outage",
                    "Environmental incidents"
                ]
            }
        ],
        "important_notes": [
            "All simulations are READ-ONLY and do not modify operational data",
            "Results are stored for review and comparison",
            "Synthetic data is used where real data is unavailable",
            "Calculations are deterministic when random_seed is provided",
            "Limitations and assumptions are documented in each result"
        ]
    }

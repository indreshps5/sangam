"""
Simulation Service

Orchestrates simulation execution and result storage.
Ensures all simulations are read-only and do not modify operational data.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.simulation.models import SimulationScenario, SimulationResult
from sangam_api.simulation.repository import (
    SimulationScenarioRepositoryInterface,
    SimulationResultRepositoryInterface,
)
from sangam_api.simulation.engines import get_simulation_engine
from sangam_api.simulation.schemas import (
    SimulationScenarioCreate,
    SimulationScenarioUpdate,
    SimulationResults,
    ScenarioStatus,
)
from sangam_api.core.exceptions import NotFoundException, ValidationException


class SimulationService:
    """
    Service for managing and executing what-if simulations.
    
    All simulations are read-only and do not modify operational data.
    """
    
    def __init__(
        self,
        scenario_repo: SimulationScenarioRepositoryInterface,
        result_repo: SimulationResultRepositoryInterface,
        db: AsyncSession
    ):
        self.scenario_repo = scenario_repo
        self.result_repo = result_repo
        self.db = db
    
    async def create_scenario(
        self,
        data: SimulationScenarioCreate,
        user_id: Optional[UUID] = None
    ) -> SimulationScenario:
        """Create a new simulation scenario."""
        scenario = SimulationScenario(
            id=uuid4(),
            name=data.name,
            description=data.description,
            scenario_type=data.scenario_type.value,
            parameters=data.parameters,
            status=ScenarioStatus.DRAFT.value,
            created_by=user_id,
            is_deterministic=data.is_deterministic,
            random_seed=data.random_seed
        )
        
        return await self.scenario_repo.create(scenario)
    
    async def get_scenario(self, scenario_id: UUID) -> SimulationScenario:
        """Get scenario by ID."""
        scenario = await self.scenario_repo.get_by_id(scenario_id)
        if not scenario:
            raise NotFoundException("Simulation scenario", str(scenario_id))
        return scenario
    
    async def list_scenarios(
        self,
        skip: int = 0,
        limit: int = 50,
        scenario_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> tuple[list[SimulationScenario], int]:
        """List scenarios with filtering."""
        scenarios = await self.scenario_repo.list_scenarios(
            skip=skip,
            limit=limit,
            scenario_type=scenario_type,
            status=status,
            created_by=created_by
        )
        total = await self.scenario_repo.count_scenarios(
            scenario_type=scenario_type,
            status=status,
            created_by=created_by
        )
        return scenarios, total
    
    async def update_scenario(
        self,
        scenario_id: UUID,
        data: SimulationScenarioUpdate
    ) -> SimulationScenario:
        """Update a scenario."""
        scenario = await self.get_scenario(scenario_id)
        
        # Only allow updates to draft scenarios
        if scenario.status != ScenarioStatus.DRAFT.value:
            raise ValidationException(
                "Can only update scenarios in draft status"
            )
        
        if data.name is not None:
            scenario.name = data.name
        if data.description is not None:
            scenario.description = data.description
        if data.parameters is not None:
            scenario.parameters = data.parameters
        
        return await self.scenario_repo.update(scenario)
    
    async def delete_scenario(self, scenario_id: UUID) -> bool:
        """Delete a scenario and its results."""
        scenario = await self.get_scenario(scenario_id)
        
        # Delete results first
        await self.result_repo.delete_by_scenario_id(scenario_id)
        
        # Delete scenario
        return await self.scenario_repo.delete(scenario_id)
    
    async def execute_simulation(self, scenario_id: UUID) -> SimulationResults:
        """
        Execute a simulation scenario.
        
        This method is READ-ONLY and does not modify operational data.
        It captures baseline, runs simulation, and stores results.
        """
        scenario = await self.get_scenario(scenario_id)
        
        # Update status to running
        scenario.status = ScenarioStatus.RUNNING.value
        await self.scenario_repo.update(scenario)
        
        start_time = time.time()
        
        try:
            # Get appropriate engine
            engine = get_simulation_engine(
                scenario.scenario_type,
                self.db,
                scenario.random_seed if scenario.is_deterministic else None
            )
            
            # Capture baseline
            baseline = await engine.capture_baseline(scenario.parameters)
            scenario.baseline_snapshot = baseline
            
            # Execute simulation (read-only)
            results = await engine.simulate(scenario.parameters)
            
            # Store results
            scenario.results = results.model_dump()
            scenario.status = ScenarioStatus.COMPLETED.value
            scenario.executed_at = datetime.utcnow()
            
            execution_duration = int((time.time() - start_time) * 1000)
            scenario.execution_duration_ms = execution_duration
            
            await self.scenario_repo.update(scenario)
            
            # Store detailed results
            await self._store_detailed_results(scenario.id, results)
            
            return results
            
        except Exception as e:
            # Mark as failed
            scenario.status = ScenarioStatus.FAILED.value
            scenario.error_message = str(e)
            scenario.execution_duration_ms = int((time.time() - start_time) * 1000)
            await self.scenario_repo.update(scenario)
            
            raise ValidationException(f"Simulation failed: {str(e)}")
    
    async def _store_detailed_results(
        self,
        scenario_id: UUID,
        results: SimulationResults
    ) -> None:
        """Store detailed simulation results."""
        # Delete existing results
        await self.result_repo.delete_by_scenario_id(scenario_id)
        
        # Store shipment impacts
        for impact in results.shipment_impacts:
            result = SimulationResult(
                id=uuid4(),
                scenario_id=scenario_id,
                result_type="shipment_impact",
                entity_type="shipment",
                entity_id=impact.shipment_id,
                baseline_value={
                    "estimated_arrival": impact.baseline_arrival.isoformat() if impact.baseline_arrival else None,
                },
                simulated_value={
                    "estimated_arrival": impact.simulated_arrival.isoformat() if impact.simulated_arrival else None,
                    "delay_hours": impact.delay_hours,
                    "status_change": impact.status_change,
                },
                impact_score=impact.delay_hours or 0,
                impact_description=impact.impact_description
            )
            await self.result_repo.create(result)
        
        # Store inventory impacts
        for impact in results.inventory_impacts:
            result = SimulationResult(
                id=uuid4(),
                scenario_id=scenario_id,
                result_type="inventory_impact",
                entity_type="inventory_item",
                entity_id=impact.inventory_item_id,
                baseline_value={
                    "stock": impact.baseline_stock,
                },
                simulated_value={
                    "stock": impact.simulated_stock,
                    "stock_change": impact.stock_change,
                    "stockout_risk": impact.stockout_risk,
                },
                impact_score=abs(impact.stock_change),
                impact_description=impact.impact_description
            )
            await self.result_repo.create(result)
        
        # Store route impacts
        for impact in results.route_impacts:
            result = SimulationResult(
                id=uuid4(),
                scenario_id=scenario_id,
                result_type="route_impact",
                entity_type="route",
                entity_id=impact.route_id,
                baseline_value={
                    "status": impact.baseline_status,
                },
                simulated_value={
                    "status": impact.simulated_status,
                    "affected_shipments": impact.affected_shipments,
                },
                impact_score=float(impact.affected_shipments),
                impact_description=impact.impact_description
            )
            await self.result_repo.create(result)
    
    async def get_comparison(self, scenario_id: UUID) -> Dict[str, Any]:
        """Get comparison between baseline and simulation."""
        scenario = await self.get_scenario(scenario_id)
        
        if not scenario.baseline_snapshot or not scenario.results:
            raise ValidationException(
                "Scenario has not been executed yet"
            )
        
        # Extract key differences
        differences = {}
        
        # Shipment impacts
        if "shipment_impacts" in scenario.results:
            shipment_impacts = scenario.results["shipment_impacts"]
            differences["shipments_affected"] = len(shipment_impacts)
            differences["total_delay_hours"] = sum(
                s.get("delay_hours", 0) for s in shipment_impacts
            )
        
        # Inventory impacts
        if "inventory_impacts" in scenario.results:
            inventory_impacts = scenario.results["inventory_impacts"]
            differences["inventory_items_affected"] = len(inventory_impacts)
            differences["stockout_risk_count"] = sum(
                1 for i in inventory_impacts if i.get("stockout_risk")
            )
            differences["total_stock_change"] = sum(
                i.get("stock_change", 0) for i in inventory_impacts
            )
        
        # Route impacts
        if "route_impacts" in scenario.results:
            route_impacts = scenario.results["route_impacts"]
            differences["routes_affected"] = len(route_impacts)
        
        return {
            "scenario_id": str(scenario.id),
            "scenario_name": scenario.name,
            "scenario_type": scenario.scenario_type,
            "baseline": scenario.baseline_snapshot,
            "simulated": scenario.results,
            "differences": differences,
            "impact_summary": scenario.results.get("summary", {})
        }

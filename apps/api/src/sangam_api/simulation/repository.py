"""
Simulation Repository Interfaces

Abstract interfaces for simulation data access.
"""

from typing import List, Optional
from uuid import UUID

from sangam_api.simulation.models import SimulationScenario, SimulationResult


class SimulationScenarioRepositoryInterface:
    """Interface for simulation scenario data access."""
    
    async def get_by_id(self, scenario_id: UUID) -> Optional[SimulationScenario]:
        """Get scenario by ID."""
        raise NotImplementedError
    
    async def list_scenarios(
        self,
        skip: int = 0,
        limit: int = 50,
        scenario_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> List[SimulationScenario]:
        """List scenarios with filtering."""
        raise NotImplementedError
    
    async def count_scenarios(
        self,
        scenario_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> int:
        """Count scenarios with filtering."""
        raise NotImplementedError
    
    async def create(self, scenario: SimulationScenario) -> SimulationScenario:
        """Create a new scenario."""
        raise NotImplementedError
    
    async def update(self, scenario: SimulationScenario) -> SimulationScenario:
        """Update an existing scenario."""
        raise NotImplementedError
    
    async def delete(self, scenario_id: UUID) -> bool:
        """Delete a scenario."""
        raise NotImplementedError


class SimulationResultRepositoryInterface:
    """Interface for simulation result data access."""
    
    async def get_by_scenario_id(self, scenario_id: UUID) -> List[SimulationResult]:
        """Get all results for a scenario."""
        raise NotImplementedError
    
    async def create(self, result: SimulationResult) -> SimulationResult:
        """Create a new result."""
        raise NotImplementedError
    
    async def delete_by_scenario_id(self, scenario_id: UUID) -> int:
        """Delete all results for a scenario."""
        raise NotImplementedError

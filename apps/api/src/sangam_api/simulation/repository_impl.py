"""
Simulation Repository Implementations

SQLAlchemy implementations of simulation repository interfaces.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.simulation.models import SimulationScenario, SimulationResult
from sangam_api.simulation.repository import (
    SimulationScenarioRepositoryInterface,
    SimulationResultRepositoryInterface,
)


class SimulationScenarioRepository(SimulationScenarioRepositoryInterface):
    """SQLAlchemy implementation of simulation scenario repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, scenario_id: UUID) -> Optional[SimulationScenario]:
        """Get scenario by ID."""
        result = await self.session.execute(
            select(SimulationScenario).where(SimulationScenario.id == scenario_id)
        )
        return result.scalar_one_or_none()
    
    async def list_scenarios(
        self,
        skip: int = 0,
        limit: int = 50,
        scenario_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> List[SimulationScenario]:
        """List scenarios with filtering."""
        query = select(SimulationScenario)
        
        if scenario_type:
            query = query.where(SimulationScenario.scenario_type == scenario_type)
        if status:
            query = query.where(SimulationScenario.status == status)
        if created_by:
            query = query.where(SimulationScenario.created_by == created_by)
        
        query = query.order_by(SimulationScenario.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_scenarios(
        self,
        scenario_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> int:
        """Count scenarios with filtering."""
        query = select(func.count(SimulationScenario.id))
        
        if scenario_type:
            query = query.where(SimulationScenario.scenario_type == scenario_type)
        if status:
            query = query.where(SimulationScenario.status == status)
        if created_by:
            query = query.where(SimulationScenario.created_by == created_by)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, scenario: SimulationScenario) -> SimulationScenario:
        """Create a new scenario."""
        self.session.add(scenario)
        await self.session.flush()
        await self.session.refresh(scenario)
        return scenario
    
    async def update(self, scenario: SimulationScenario) -> SimulationScenario:
        """Update an existing scenario."""
        await self.session.flush()
        await self.session.refresh(scenario)
        return scenario
    
    async def delete(self, scenario_id: UUID) -> bool:
        """Delete a scenario."""
        scenario = await self.get_by_id(scenario_id)
        if not scenario:
            return False
        
        await self.session.delete(scenario)
        await self.session.flush()
        return True


class SimulationResultRepository(SimulationResultRepositoryInterface):
    """SQLAlchemy implementation of simulation result repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_scenario_id(self, scenario_id: UUID) -> List[SimulationResult]:
        """Get all results for a scenario."""
        result = await self.session.execute(
            select(SimulationResult)
            .where(SimulationResult.scenario_id == scenario_id)
            .order_by(SimulationResult.created_at)
        )
        return list(result.scalars().all())
    
    async def create(self, result: SimulationResult) -> SimulationResult:
        """Create a new result."""
        self.session.add(result)
        await self.session.flush()
        await self.session.refresh(result)
        return result
    
    async def delete_by_scenario_id(self, scenario_id: UUID) -> int:
        """Delete all results for a scenario."""
        result = await self.session.execute(
            delete(SimulationResult).where(SimulationResult.scenario_id == scenario_id)
        )
        await self.session.flush()
        return result.rowcount

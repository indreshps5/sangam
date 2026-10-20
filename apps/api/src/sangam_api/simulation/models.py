"""
Simulation Models

Database models for what-if disruption simulation scenarios.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sangam_api.core.database import Base


class SimulationScenario(Base):
    """
    What-if simulation scenario.
    
    Stores scenario configuration, baseline snapshot, and simulation results.
    All simulations are read-only and do not modify operational data.
    """
    
    __tablename__ = "simulation_scenarios"
    
    # Basic info
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Scenario type and parameters
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Baseline snapshot (before simulation)
    baseline_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Simulation results
    results: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Status and metadata
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    execution_duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Deterministic flag for reproducible simulations
    is_deterministic: Mapped[bool] = mapped_column(Boolean, default=True)
    random_seed: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self) -> str:
        return f"<SimulationScenario(id={self.id}, name={self.name}, type={self.scenario_type})>"


class SimulationResult(Base):
    """
    Detailed simulation results for comparison.
    
    Stores granular results for each affected entity.
    """
    
    __tablename__ = "simulation_results"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    scenario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Result type (shipment_impact, inventory_impact, route_impact, etc.)
    result_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Entity reference (shipment_id, inventory_item_id, route_id, etc.)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
    
    # Baseline and simulated values
    baseline_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    simulated_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Impact metrics
    impact_score: Mapped[Optional[float]] = mapped_column(Float)
    impact_description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    scenario = relationship("SimulationScenario", back_populates="results_detail")
    
    def __repr__(self) -> str:
        return f"<SimulationResult(id={self.id}, type={self.result_type}, entity={self.entity_type})>"


# Add relationship to SimulationScenario
SimulationScenario.results_detail = relationship(
    "SimulationResult",
    back_populates="scenario",
    cascade="all, delete-orphan"
)

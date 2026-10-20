"""
SimulationScenario — what-if analysis configurations and results.
Recommendation — AI-generated supply chain recommendations.
ApprovalRecord — approval workflow tracking.
AuditLog — comprehensive audit trail.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sangam_api.core.database import Base
from sangam_api.core.types import UUIDPrimaryKeyMixin, TimestampMixin


class SimulationScenario(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A what-if simulation scenario for supply chain analysis.

    Canonical fields:
    - name: Human-readable scenario name
    - description: Detailed scenario description
    - status: Current simulation status
    - scenario_type: Type of simulation (demand, route, inventory, etc.)
    - parameters: JSON configuration for the simulation
    - input_data_snapshot: JSON snapshot of input data
    - results: JSON simulation results
    - created_by: User who created the scenario
    - started_at: When simulation started running
    - completed_at: When simulation finished
    - duration_seconds: How long it took to run
    """

    __tablename__ = "simulation_scenarios"

    __table_args__ = (
        CheckConstraint("duration_seconds >= 0", name="ck_simulation_duration_non_negative"),
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    parameters: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON simulation parameters")
    input_data_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON input data snapshot")
    results: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON simulation results")
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)


class Recommendation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    AI-generated recommendation for supply chain optimization.

    Canonical fields:
    - category: Type of recommendation
    - status: Current recommendation status
    - title: Short recommendation title
    - description: Detailed recommendation
    - rationale: Why this recommendation was made
    - confidence_score: Model confidence (0.0-1.0)
    - expected_impact: JSON expected impact metrics
    - implementation_cost: Estimated cost to implement
    - expected_savings: Estimated savings/benefit
    - priority: Recommendation priority (1-5)
    - expiry_date: When this recommendation expires
    - depot_id: FK to related depot (nullable)
    - generated_by_model: Which ML model generated this
    - approved_by: User who approved
    - approved_at: When approved
    """

    __tablename__ = "recommendations"

    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_recommendations_confidence_range",
        ),
        CheckConstraint("priority >= 1 AND priority <= 5", name="ck_recommendations_priority_range"),
        CheckConstraint("implementation_cost >= 0", name="ck_recommendations_cost_non_negative"),
        CheckConstraint("expected_savings >= 0", name="ck_recommendations_savings_non_negative"),
    )

    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="generated", index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expected_impact: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON expected impact")
    implementation_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expected_savings: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    depot_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    generated_by_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ApprovalRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Approval workflow record for recommendations and other actions.

    Canonical fields:
    - entity_type: Type of entity being approved (recommendation, shipment, etc.)
    - entity_id: ID of the entity being approved
    - requester_id: User who requested approval
    - approver_id: User who should approve
    - status: Current approval status
    - priority: Approval priority
    - reason: Why approval is needed
    - decision: Approver's decision notes
    - decided_at: When decision was made
    - due_date: When approval is due
    - escalation_count: Number of times escalated
    """

    __tablename__ = "approval_records"

    __table_args__ = (
        CheckConstraint("escalation_count >= 0", name="ck_approval_escalation_non_negative"),
    )

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    requester_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approver_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escalation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AuditLog(Base, UUIDPrimaryKeyMixin):
    """
    Comprehensive audit trail for all system actions.

    Canonical fields:
    - user_id: FK to the user who performed the action (nullable for system actions)
    - action: Type of action (create, update, delete, etc.)
    - entity_type: Type of entity affected
    - entity_id: ID of the affected entity
    - timestamp: When the action occurred
    - ip_address: Client IP address
    - user_agent: Client user agent
    - changes: JSON diff of what changed
    - metadata: Additional context (JSON)
    """

    __tablename__ = "audit_logs"

    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    changes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON diff of changes")
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON additional context")

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="audit_logs", lazy="joined")

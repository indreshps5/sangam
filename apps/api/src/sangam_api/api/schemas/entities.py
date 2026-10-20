"""
Simulation, Recommendation, Approval, Audit, and User schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from sangam_api.core.enums import (
    SimulationStatus,
    RecommendationStatus,
    RecommendationCategory,
    ApprovalStatus,
    AuditAction,
    UserRole,
)
from sangam_api.api.schemas.common import IDMixin, TimestampMixin


# ─── SimulationScenario ───

class SimulationScenarioCreate(BaseModel):
    """Schema for creating a simulation scenario."""
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    scenario_type: str = Field(min_length=1, max_length=50, description="Type of simulation")
    parameters: Optional[str] = Field(None, description="JSON simulation parameters")
    input_data_snapshot: Optional[str] = Field(None, description="JSON input data")
    created_by: Optional[UUID] = None


class SimulationScenarioUpdate(BaseModel):
    """Schema for updating a simulation scenario."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[SimulationStatus] = None
    results: Optional[str] = Field(None, description="JSON simulation results")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = Field(None, ge=0)


class SimulationScenarioResponse(IDMixin, TimestampMixin):
    """Schema for simulation scenario response."""
    name: str
    description: Optional[str] = None
    status: str
    scenario_type: str
    parameters: Optional[str] = None
    input_data_snapshot: Optional[str] = None
    results: Optional[str] = None
    created_by: Optional[UUID] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    model_config = {"from_attributes": True}


class SimulationScenarioListResponse(BaseModel):
    """Paginated list of simulation scenarios."""
    items: list[SimulationScenarioResponse]
    total: int
    skip: int
    limit: int


# ─── Recommendation ───

class RecommendationCreate(BaseModel):
    """Schema for creating a recommendation."""
    category: RecommendationCategory = Field(description="Type of recommendation")
    title: str = Field(min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=10000)
    rationale: Optional[str] = Field(None, max_length=5000)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    expected_impact: Optional[str] = Field(None, description="JSON expected impact")
    implementation_cost: float = Field(0.0, ge=0)
    expected_savings: float = Field(0.0, ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    priority: int = Field(3, ge=1, le=5)
    expiry_date: Optional[datetime] = None
    depot_id: Optional[UUID] = None
    generated_by_model: Optional[str] = Field(None, max_length=100)


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation."""
    status: Optional[RecommendationStatus] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None


class RecommendationResponse(IDMixin, TimestampMixin):
    """Schema for recommendation response."""
    category: str
    status: str
    title: str
    description: Optional[str] = None
    rationale: Optional[str] = None
    confidence_score: float
    expected_impact: Optional[str] = None
    implementation_cost: float
    expected_savings: float
    currency: str
    priority: int
    expiry_date: Optional[datetime] = None
    depot_id: Optional[UUID] = None
    generated_by_model: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RecommendationListResponse(BaseModel):
    """Paginated list of recommendations."""
    items: list[RecommendationResponse]
    total: int
    skip: int
    limit: int


# ─── ApprovalRecord ───

class ApprovalRecordCreate(BaseModel):
    """Schema for creating an approval record."""
    entity_type: str = Field(min_length=1, max_length=50)
    entity_id: UUID = Field(description="ID of entity being approved")
    requester_id: UUID = Field(description="User who requested approval")
    approver_id: Optional[UUID] = Field(None, description="User who should approve")
    priority: int = Field(3, ge=1, le=5)
    reason: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None


class ApprovalRecordUpdate(BaseModel):
    """Schema for updating an approval record."""
    approver_id: Optional[UUID] = None
    status: Optional[ApprovalStatus] = None
    decision: Optional[str] = Field(None, max_length=2000)
    decided_at: Optional[datetime] = None
    escalation_count: Optional[int] = Field(None, ge=0)


class ApprovalRecordResponse(IDMixin, TimestampMixin):
    """Schema for approval record response."""
    entity_type: str
    entity_id: UUID
    requester_id: UUID
    approver_id: Optional[UUID] = None
    status: str
    priority: int
    reason: Optional[str] = None
    decision: Optional[str] = None
    decided_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    escalation_count: int

    model_config = {"from_attributes": True}


class ApprovalRecordListResponse(BaseModel):
    """Paginated list of approval records."""
    items: list[ApprovalRecordResponse]
    total: int
    skip: int
    limit: int


# ─── AuditLog ───

class AuditLogCreate(BaseModel):
    """Schema for creating an audit log entry."""
    user_id: Optional[UUID] = Field(None, description="User who performed action")
    action: AuditAction = Field(description="Type of action")
    entity_type: str = Field(min_length=1, max_length=50)
    entity_id: Optional[UUID] = None
    timestamp: datetime = Field(description="When the action occurred")
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    changes: Optional[str] = Field(None, description="JSON diff of changes")
    metadata: Optional[str] = Field(None, description="JSON additional context")


class AuditLogResponse(IDMixin):
    """Schema for audit log response."""
    user_id: Optional[UUID] = None
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes: Optional[str] = None
    metadata: Optional[str] = None

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Paginated list of audit logs."""
    items: list[AuditLogResponse]
    total: int
    skip: int
    limit: int


# ─── User & Role ───

class RoleCreate(BaseModel):
    """Schema for creating a role."""
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    permissions: Optional[str] = Field(None, max_length=2000, description="JSON array of permissions")
    is_system: bool = Field(False, description="System roles cannot be deleted")


class RoleResponse(IDMixin, TimestampMixin):
    """Schema for role response."""
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None
    is_system: bool

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Schema for creating a user."""
    email: EmailStr = Field(description="Unique email address")
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128, description="Plain text password (will be hashed)")
    full_name: Optional[str] = Field(None, max_length=200)
    preferred_timezone: Optional[str] = Field(None, max_length=50)
    preferred_language: Optional[str] = Field(None, max_length=10)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    full_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    preferred_timezone: Optional[str] = Field(None, max_length=50)
    preferred_language: Optional[str] = Field(None, max_length=10)


class UserResponse(IDMixin, TimestampMixin):
    """Schema for user response (never includes password)."""
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    preferred_timezone: Optional[str] = None
    preferred_language: Optional[str] = None
    roles: list[RoleResponse] = []

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Paginated list of users."""
    items: list[UserResponse]
    total: int
    skip: int
    limit: int

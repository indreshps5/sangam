"""
Recommendation Schemas

Pydantic models for recommendation API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


class RecommendationType(str, Enum):
    """Types of recommendations."""
    STOCK_TRANSFER = "stock_transfer"
    REPLENISHMENT = "replenishment"
    ROUTE_CHANGE = "route_change"
    SHIPMENT_PRIORITY = "shipment_priority"
    SHORTAGE_REVIEW = "shortage_review"
    CAPACITY_OPTIMIZATION = "capacity_optimization"
    COST_REDUCTION = "cost_reduction"
    RISK_MITIGATION = "risk_mitigation"


class RecommendationCategory(str, Enum):
    """Categories of recommendations."""
    INVENTORY = "inventory"
    SHIPMENT = "shipment"
    ROUTE = "route"
    FORECAST = "forecast"
    OPERATIONS = "operations"


class RecommendationStatus(str, Enum):
    """Recommendation workflow states."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class RecommendationPriority(int, Enum):
    """Recommendation priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


class RecommendationBase(BaseModel):
    """Base schema for recommendations."""
    recommendation_type: RecommendationType
    category: RecommendationCategory
    priority: int = Field(default=3, ge=1, le=5)
    
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    rationale: str
    suggested_action: str
    
    # Affected entities
    affected_depot_id: Optional[UUID] = None
    affected_shipment_id: Optional[UUID] = None
    affected_inventory_item_id: Optional[UUID] = None
    affected_route_id: Optional[UUID] = None
    
    # Supporting data
    supporting_data: Optional[Dict[str, Any]] = None
    assumptions: Optional[Dict[str, Any]] = None
    
    # Impact estimation
    estimated_impact: Optional[Dict[str, Any]] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Source information
    source_service: str
    source_records: Optional[Dict[str, Any]] = None
    
    # Expiration
    expires_at: Optional[datetime] = None


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation."""
    created_by: Optional[UUID] = None


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation."""
    status: Optional[RecommendationStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    rationale: Optional[str] = None
    suggested_action: Optional[str] = None
    supporting_data: Optional[Dict[str, Any]] = None
    assumptions: Optional[Dict[str, Any]] = None
    estimated_impact: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    expires_at: Optional[datetime] = None


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""
    id: UUID
    recommendation_type: str
    category: str
    priority: int
    status: str
    
    # Affected entities
    affected_depot_id: Optional[UUID] = None
    affected_shipment_id: Optional[UUID] = None
    affected_inventory_item_id: Optional[UUID] = None
    affected_route_id: Optional[UUID] = None
    
    # Content
    title: str
    description: str
    rationale: str
    suggested_action: str
    
    # Supporting data
    supporting_data: Optional[Dict[str, Any]] = None
    assumptions: Optional[Dict[str, Any]] = None
    
    # Impact
    estimated_impact: Optional[Dict[str, Any]] = None
    confidence_score: float
    
    # Source
    source_service: str
    source_records: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    
    # Approval workflow
    created_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Execution
    executed_at: Optional[datetime] = None
    executed_by: Optional[UUID] = None
    execution_result: Optional[Dict[str, Any]] = None
    
    # Related entity names (for display)
    depot_name: Optional[str] = None
    shipment_tracking: Optional[str] = None
    inventory_item_name: Optional[str] = None
    route_name: Optional[str] = None
    creator_name: Optional[str] = None
    approver_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema for list of recommendations."""
    items: List[RecommendationResponse]
    total: int
    skip: int
    limit: int


class ApprovalRequest(BaseModel):
    """Schema for approving a recommendation."""
    notes: Optional[str] = None


class RejectionRequest(BaseModel):
    """Schema for rejecting a recommendation."""
    reason: str = Field(..., min_length=1, max_length=500)


class ExecutionRequest(BaseModel):
    """Schema for executing a recommendation."""
    notes: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None  # Additional execution parameters


class ExecutionResponse(BaseModel):
    """Schema for execution result."""
    success: bool
    message: str
    result_data: Optional[Dict[str, Any]] = None
    executed_at: datetime


class RecommendationStats(BaseModel):
    """Statistics about recommendations."""
    total: int
    pending: int
    approved: int
    rejected: int
    completed: int
    by_type: Dict[str, int]
    by_category: Dict[str, int]
    by_priority: Dict[int, int]
    average_confidence_score: float


class RecommendationAuditLogResponse(BaseModel):
    """Schema for audit log entry."""
    id: UUID
    recommendation_id: UUID
    action: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for list of audit logs."""
    items: List[RecommendationAuditLogResponse]
    total: int

"""
Recommendation API Router

REST API endpoints for recommendation management.
"""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db
from sangam_api.core.auth import get_current_user
from sangam_api.models.user import User
from sangam_api.recommendations.repository_impl import (
    RecommendationRepository,
    RecommendationAuditLogRepository,
)
from sangam_api.recommendations.service import RecommendationService
from sangam_api.recommendations.schemas import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationListResponse,
    ApprovalRequest,
    RejectionRequest,
    ExecutionRequest,
    ExecutionResponse,
    RecommendationStats,
    RecommendationAuditLogResponse,
    AuditLogListResponse,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_recommendation_service(
    db: AsyncSession = Depends(get_db)
) -> RecommendationService:
    """Dependency injection for recommendation service."""
    recommendation_repo = RecommendationRepository(db)
    audit_log_repo = RecommendationAuditLogRepository(db)
    
    # In production, inject actual services here
    # For now, we'll pass None and strategies won't be available
    return RecommendationService(
        recommendation_repo=recommendation_repo,
        audit_log_repo=audit_log_repo,
        db=db,
        inventory_service=None,
        forecast_service=None,
        shipment_service=None,
        route_service=None,
    )


# ============================================================================
# Recommendation Management Endpoints
# ============================================================================

@router.get("/", response_model=RecommendationListResponse)
async def list_recommendations(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    recommendation_type: Optional[str] = Query(None, description="Filter by type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority"),
    affected_depot_id: Optional[UUID] = Query(None, description="Filter by depot"),
    affected_shipment_id: Optional[UUID] = Query(None, description="Filter by shipment"),
    affected_inventory_item_id: Optional[UUID] = Query(None, description="Filter by inventory item"),
    affected_route_id: Optional[UUID] = Query(None, description="Filter by route"),
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    List recommendations with filtering and pagination.
    
    Returns recommendations ordered by priority (highest first) then creation date.
    """
    recommendations, total = await service.list_recommendations(
        skip=skip,
        limit=limit,
        status=status,
        recommendation_type=recommendation_type,
        category=category,
        priority=priority,
        affected_depot_id=affected_depot_id,
        affected_shipment_id=affected_shipment_id,
        affected_inventory_item_id=affected_inventory_item_id,
        affected_route_id=affected_route_id,
    )
    
    return RecommendationListResponse(
        items=[RecommendationResponse.model_validate(r) for r in recommendations],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/stats", response_model=RecommendationStats)
async def get_recommendation_stats(
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get recommendation statistics.
    
    Returns counts by status, type, category, and priority.
    """
    stats = await service.get_statistics()
    return RecommendationStats(**stats)


@router.get("/pending", response_model=List[RecommendationResponse])
async def get_pending_recommendations(
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    priority_threshold: Optional[int] = Query(None, ge=1, le=5, description="Max priority level"),
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get pending recommendations.
    
    Returns recommendations awaiting approval, ordered by priority.
    """
    recommendations = await service.get_pending_recommendations(
        limit=limit,
        priority_threshold=priority_threshold
    )
    
    return [RecommendationResponse.model_validate(r) for r in recommendations]


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: UUID,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get recommendation by ID.
    
    Returns full recommendation details including related entities.
    """
    recommendation = await service.get_recommendation(recommendation_id)
    return RecommendationResponse.model_validate(recommendation)


@router.post("/", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
     RecommendationCreate,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new recommendation.
    
    Manually create a recommendation (usually generated by strategies).
    """
    from sangam_api.recommendations.models import Recommendation
    from uuid import uuid4
    
    recommendation = Recommendation(
        id=uuid4(),
        recommendation_type=data.recommendation_type.value,
        category=data.category.value,
        priority=data.priority,
        title=data.title,
        description=data.description,
        rationale=data.rationale,
        suggested_action=data.suggested_action,
        affected_depot_id=data.affected_depot_id,
        affected_shipment_id=data.affected_shipment_id,
        affected_inventory_item_id=data.affected_inventory_item_id,
        affected_route_id=data.affected_route_id,
        supporting_data=data.supporting_data,
        assumptions=data.assumptions,
        estimated_impact=data.estimated_impact,
        confidence_score=data.confidence_score,
        source_service=data.source_service,
        source_records=data.source_records,
        expires_at=data.expires_at,
        created_by=data.created_by or current_user.id,
        status='pending'
    )
    
    recommendation = await service.recommendation_repo.create(recommendation)
    
    # Log creation
    await service._log_action(
        recommendation_id=recommendation.id,
        action='created',
        new_status='pending',
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email,
        notes="Manually created"
    )
    
    await service.db.commit()
    
    return RecommendationResponse.model_validate(recommendation)


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_id: UUID,
     RecommendationUpdate,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update a recommendation.
    
    Only pending recommendations can be updated.
    """
    recommendation = await service.update_recommendation(
        recommendation_id=recommendation_id,
         data,
        user_id=current_user.id
    )
    
    return RecommendationResponse.model_validate(recommendation)


# ============================================================================
# Approval Workflow Endpoints
# ============================================================================

@router.post("/{recommendation_id}/approve", response_model=RecommendationResponse)
async def approve_recommendation(
    recommendation_id: UUID,
    request: ApprovalRequest,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a recommendation.
    
    Approval does NOT automatically execute the recommendation.
    Execution requires a separate explicit action.
    
    Requires appropriate permissions.
    """
    # Check permissions (in production, check for 'recommendations:approve')
    # For now, any authenticated user can approve
    
    recommendation = await service.approve_recommendation(
        recommendation_id=recommendation_id,
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email,
        notes=request.notes
    )
    
    return RecommendationResponse.model_validate(recommendation)


@router.post("/{recommendation_id}/reject", response_model=RecommendationResponse)
async def reject_recommendation(
    recommendation_id: UUID,
    request: RejectionRequest,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Reject a recommendation.
    
    Requires a reason for rejection.
    Requires appropriate permissions.
    """
    recommendation = await service.reject_recommendation(
        recommendation_id=recommendation_id,
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email,
        reason=request.reason
    )
    
    return RecommendationResponse.model_validate(recommendation)


# ============================================================================
# Execution Endpoints
# ============================================================================

@router.post("/{recommendation_id}/execute", response_model=RecommendationResponse)
async def execute_recommendation(
    recommendation_id: UUID,
    request: ExecutionRequest,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Execute an approved recommendation.
    
    This is a simulated execution for the prototype.
    In production, this would integrate with actual operational systems.
    
    Requires the recommendation to be in 'approved' status.
    """
    recommendation = await service.execute_recommendation(
        recommendation_id=recommendation_id,
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email,
        notes=request.notes,
        parameters=request.parameters
    )
    
    return RecommendationResponse.model_validate(recommendation)


# ============================================================================
# Generation Endpoints
# ============================================================================

@router.post("/generate", response_model=List[RecommendationResponse])
async def generate_recommendations(
    strategy_names: Optional[List[str]] = Query(None, description="Specific strategies to run"),
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Generate recommendations using AI strategies.
    
    Runs specified strategies (or all if none specified) to generate
    new recommendations based on current system state.
    
    This is a long-running operation and may take several seconds.
    """
    recommendations = await service.generate_recommendations(
        strategy_names=strategy_names
    )
    
    return [RecommendationResponse.model_validate(r) for r in recommendations]


# ============================================================================
# Audit Log Endpoints
# ============================================================================

@router.get("/{recommendation_id}/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    recommendation_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a recommendation.
    
    Returns all actions taken on this recommendation.
    """
    logs, total = await service.get_audit_logs(
        recommendation_id=recommendation_id,
        skip=skip,
        limit=limit
    )
    
    return AuditLogListResponse(
        items=[RecommendationAuditLogResponse.model_validate(log) for log in logs],
        total=total
    )


# ============================================================================
# Maintenance Endpoints
# ============================================================================

@router.post("/maintenance/cleanup-expired")
async def cleanup_expired_recommendations(
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up expired recommendations.
    
    Automatically rejects recommendations that have passed their expiration date.
    """
    count = await service.cleanup_expired_recommendations()
    
    return {
        "message": f"Cleaned up {count} expired recommendations",
        "count": count
    }


@router.get("/strategies")
async def list_strategies(
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User = Depends(get_current_user)
):
    """
    List available recommendation strategies.
    
    Returns information about each strategy and what it does.
    """
    strategies_info = []
    
    for name, strategy in service.strategies.items():
        strategies_info.append({
            "name": name,
            "strategy_name": strategy.get_strategy_name(),
            "recommendation_type": strategy.get_recommendation_type(),
            "description": strategy.__doc__ or "No description available"
        })
    
    return {
        "strategies": strategies_info,
        "total": len(strategies_info)
    }

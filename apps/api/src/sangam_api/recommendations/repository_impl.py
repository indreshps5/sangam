"""
Recommendation Repository Implementations

SQLAlchemy implementations of recommendation repositories.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sangam_api.recommendations.models import Recommendation, RecommendationAuditLog
from sangam_api.recommendations.repository import (
    RecommendationRepositoryInterface,
    RecommendationAuditLogRepositoryInterface,
)


class RecommendationRepository(RecommendationRepositoryInterface):
    """SQLAlchemy implementation of recommendation repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, recommendation_id: UUID) -> Optional[Recommendation]:
        """Get recommendation by ID with all relationships loaded."""
        result = await self.session.execute(
            select(Recommendation)
            .options(
                selectinload(Recommendation.depot),
                selectinload(Recommendation.shipment),
                selectinload(Recommendation.inventory_item),
                selectinload(Recommendation.route),
                selectinload(Recommendation.creator),
                selectinload(Recommendation.approver),
            )
            .where(Recommendation.id == recommendation_id)
        )
        return result.scalar_one_or_none()
    
    async def list_recommendations(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        recommendation_type: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        affected_depot_id: Optional[UUID] = None,
        affected_shipment_id: Optional[UUID] = None,
        affected_inventory_item_id: Optional[UUID] = None,
        affected_route_id: Optional[UUID] = None,
    ) -> List[Recommendation]:
        """List recommendations with filtering."""
        query = select(Recommendation).options(
            selectinload(Recommendation.depot),
            selectinload(Recommendation.shipment),
            selectinload(Recommendation.inventory_item),
            selectinload(Recommendation.route),
        )
        
        # Apply filters
        if status:
            query = query.where(Recommendation.status == status)
        if recommendation_type:
            query = query.where(Recommendation.recommendation_type == recommendation_type)
        if category:
            query = query.where(Recommendation.category == category)
        if priority:
            query = query.where(Recommendation.priority == priority)
        if affected_depot_id:
            query = query.where(Recommendation.affected_depot_id == affected_depot_id)
        if affected_shipment_id:
            query = query.where(Recommendation.affected_shipment_id == affected_shipment_id)
        if affected_inventory_item_id:
            query = query.where(Recommendation.affected_inventory_item_id == affected_inventory_item_id)
        if affected_route_id:
            query = query.where(Recommendation.affected_route_id == affected_route_id)
        
        # Order by priority (ascending) then created_at (descending)
        query = query.order_by(Recommendation.priority.asc(), Recommendation.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_recommendations(
        self,
        status: Optional[str] = None,
        recommendation_type: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        affected_depot_id: Optional[UUID] = None,
        affected_shipment_id: Optional[UUID] = None,
        affected_inventory_item_id: Optional[UUID] = None,
        affected_route_id: Optional[UUID] = None,
    ) -> int:
        """Count recommendations with filtering."""
        query = select(func.count(Recommendation.id))
        
        # Apply filters
        if status:
            query = query.where(Recommendation.status == status)
        if recommendation_type:
            query = query.where(Recommendation.recommendation_type == recommendation_type)
        if category:
            query = query.where(Recommendation.category == category)
        if priority:
            query = query.where(Recommendation.priority == priority)
        if affected_depot_id:
            query = query.where(Recommendation.affected_depot_id == affected_depot_id)
        if affected_shipment_id:
            query = query.where(Recommendation.affected_shipment_id == affected_shipment_id)
        if affected_inventory_item_id:
            query = query.where(Recommendation.affected_inventory_item_id == affected_inventory_item_id)
        if affected_route_id:
            query = query.where(Recommendation.affected_route_id == affected_route_id)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, recommendation: Recommendation) -> Recommendation:
        """Create a new recommendation."""
        self.session.add(recommendation)
        await self.session.flush()
        await self.session.refresh(recommendation)
        return recommendation
    
    async def update(self, recommendation: Recommendation) -> Recommendation:
        """Update an existing recommendation."""
        await self.session.flush()
        await self.session.refresh(recommendation)
        return recommendation
    
    async def delete(self, recommendation_id: UUID) -> bool:
        """Delete a recommendation."""
        recommendation = await self.get_by_id(recommendation_id)
        if not recommendation:
            return False
        
        await self.session.delete(recommendation)
        await self.session.flush()
        return True
    
    async def get_pending_recommendations(
        self,
        limit: int = 50,
        priority_threshold: Optional[int] = None
    ) -> List[Recommendation]:
        """Get pending recommendations, optionally filtered by priority."""
        query = select(Recommendation).options(
            selectinload(Recommendation.depot),
            selectinload(Recommendation.shipment),
            selectinload(Recommendation.inventory_item),
            selectinload(Recommendation.route),
        ).where(Recommendation.status == 'pending')
        
        if priority_threshold:
            query = query.where(Recommendation.priority <= priority_threshold)
        
        query = query.order_by(Recommendation.priority.asc(), Recommendation.created_at.desc())
        query = query.limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_expired_recommendations(self) -> List[Recommendation]:
        """Get recommendations that have expired."""
        now = datetime.utcnow()
        
        result = await self.session.execute(
            select(Recommendation)
            .where(
                and_(
                    Recommendation.expires_at.isnot(None),
                    Recommendation.expires_at < now,
                    Recommendation.status == 'pending'
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_statistics(self) -> dict:
        """Get recommendation statistics."""
        # Total count
        total_result = await self.session.execute(
            select(func.count(Recommendation.id))
        )
        total = total_result.scalar_one()
        
        # Count by status
        status_counts = {}
        for status in ['pending', 'approved', 'rejected', 'completed']:
            result = await self.session.execute(
                select(func.count(Recommendation.id))
                .where(Recommendation.status == status)
            )
            status_counts[status] = result.scalar_one()
        
        # Count by type
        type_result = await self.session.execute(
            select(Recommendation.recommendation_type, func.count(Recommendation.id))
            .group_by(Recommendation.recommendation_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}
        
        # Count by category
        category_result = await self.session.execute(
            select(Recommendation.category, func.count(Recommendation.id))
            .group_by(Recommendation.category)
        )
        by_category = {row[0]: row[1] for row in category_result.all()}
        
        # Count by priority
        priority_result = await self.session.execute(
            select(Recommendation.priority, func.count(Recommendation.id))
            .group_by(Recommendation.priority)
        )
        by_priority = {row[0]: row[1] for row in priority_result.all()}
        
        # Average confidence score
        avg_confidence_result = await self.session.execute(
            select(func.avg(Recommendation.confidence_score))
        )
        avg_confidence = avg_confidence_result.scalar_one() or 0.0
        
        return {
            'total': total,
            'pending': status_counts.get('pending', 0),
            'approved': status_counts.get('approved', 0),
            'rejected': status_counts.get('rejected', 0),
            'completed': status_counts.get('completed', 0),
            'by_type': by_type,
            'by_category': by_category,
            'by_priority': by_priority,
            'average_confidence_score': float(avg_confidence)
        }


class RecommendationAuditLogRepository(RecommendationAuditLogRepositoryInterface):
    """SQLAlchemy implementation of recommendation audit log repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, audit_log: RecommendationAuditLog) -> RecommendationAuditLog:
        """Create a new audit log entry."""
        self.session.add(audit_log)
        await self.session.flush()
        await self.session.refresh(audit_log)
        return audit_log
    
    async def list_by_recommendation(
        self,
        recommendation_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[RecommendationAuditLog]:
        """List audit logs for a recommendation."""
        result = await self.session.execute(
            select(RecommendationAuditLog)
            .options(selectinload(RecommendationAuditLog.user))
            .where(RecommendationAuditLog.recommendation_id == recommendation_id)
            .order_by(RecommendationAuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_recommendation(self, recommendation_id: UUID) -> int:
        """Count audit logs for a recommendation."""
        result = await self.session.execute(
            select(func.count(RecommendationAuditLog.id))
            .where(RecommendationAuditLog.recommendation_id == recommendation_id)
        )
        return result.scalar_one()

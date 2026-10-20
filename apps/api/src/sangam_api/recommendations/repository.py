"""
Recommendation Repository Interfaces

Abstract interfaces for recommendation data access.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sangam_api.recommendations.models import Recommendation, RecommendationAuditLog


class RecommendationRepositoryInterface:
    """Interface for recommendation data access."""
    
    async def get_by_id(self, recommendation_id: UUID) -> Optional[Recommendation]:
        """Get recommendation by ID."""
        raise NotImplementedError
    
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
        raise NotImplementedError
    
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
        raise NotImplementedError
    
    async def create(self, recommendation: Recommendation) -> Recommendation:
        """Create a new recommendation."""
        raise NotImplementedError
    
    async def update(self, recommendation: Recommendation) -> Recommendation:
        """Update an existing recommendation."""
        raise NotImplementedError
    
    async def delete(self, recommendation_id: UUID) -> bool:
        """Delete a recommendation."""
        raise NotImplementedError
    
    async def get_pending_recommendations(
        self,
        limit: int = 50,
        priority_threshold: Optional[int] = None
    ) -> List[Recommendation]:
        """Get pending recommendations, optionally filtered by priority."""
        raise NotImplementedError
    
    async def get_expired_recommendations(self) -> List[Recommendation]:
        """Get recommendations that have expired."""
        raise NotImplementedError
    
    async def get_statistics(self) -> dict:
        """Get recommendation statistics."""
        raise NotImplementedError


class RecommendationAuditLogRepositoryInterface:
    """Interface for recommendation audit log data access."""
    
    async def create(self, audit_log: RecommendationAuditLog) -> RecommendationAuditLog:
        """Create a new audit log entry."""
        raise NotImplementedError
    
    async def list_by_recommendation(
        self,
        recommendation_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[RecommendationAuditLog]:
        """List audit logs for a recommendation."""
        raise NotImplementedError
    
    async def count_by_recommendation(self, recommendation_id: UUID) -> int:
        """Count audit logs for a recommendation."""
        raise NotImplementedError

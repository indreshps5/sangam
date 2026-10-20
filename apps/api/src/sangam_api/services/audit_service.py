"""
Audit logging service.
Records security and administrative actions.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sangam_api.models.simulation import AuditLog
from sangam_api.core.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    """Service for recording audit log entries."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_action(
        self,
        action: str,
        entity_type: str,
        user_id: Optional[UUID] = None,
        entity_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> AuditLog:
        """
        Record an audit log entry.
        
        Args:
            action: Type of action (login, logout, create, update, delete, etc.)
            entity_type: Type of entity affected (user, depot, shipment, etc.)
            user_id: ID of the user performing the action
            entity_id: ID of the affected entity
            ip_address: Client IP address
            user_agent: Client user agent
            changes: Dictionary of changes made
            metadata: Additional context
        
        Returns:
            Created AuditLog entry
        """
        import json
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=json.dumps(changes) if changes else None,
            metadata=json.dumps(metadata) if metadata else None,
        )
        
        self.db.add(audit_log)
        await self.db.flush()
        
        logger.info(
            "audit_log_created",
            action=action,
            entity_type=entity_type,
            user_id=str(user_id) if user_id else None,
            entity_id=str(entity_id) if entity_id else None,
        )
        
        return audit_log
    
    async def log_login(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
    ) -> AuditLog:
        """Log a login attempt."""
        return await self.log_action(
            action="login",
            entity_type="user",
            user_id=user_id,
            entity_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"success": success},
        )
    
    async def log_logout(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log a logout event."""
        return await self.log_action(
            action="logout",
            entity_type="user",
            user_id=user_id,
            entity_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    async def log_password_change(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log a password change event."""
        return await self.log_action(
            action="password_change",
            entity_type="user",
            user_id=user_id,
            entity_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    async def log_permission_denied(
        self,
        user_id: UUID,
        required_permission: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log a permission denied event."""
        return await self.log_action(
            action="permission_denied",
            entity_type="user",
            user_id=user_id,
            entity_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"required_permission": required_permission},
        )
    
    async def log_shipment_created(
        self,
        shipment_id: UUID,
        user_id: Optional[UUID] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log shipment creation."""
        return await self.log_action(
            action="shipment_created",
            entity_type="shipment",
            user_id=user_id,
            entity_id=shipment_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "origin_depot_id": str(origin_depot_id) if origin_depot_id else None,
                "destination_depot_id": str(destination_depot_id) if destination_depot_id else None
            }
        )
    
    async def log_shipment_updated(
        self,
        shipment_id: UUID,
        user_id: Optional[UUID] = None,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log shipment update."""
        return await self.log_action(
            action="shipment_updated",
            entity_type="shipment",
            user_id=user_id,
            entity_id=shipment_id,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes
        )
    
    async def log_shipment_status_changed(
        self,
        shipment_id: UUID,
        user_id: Optional[UUID] = None,
        old_status: Optional[str] = None,
        new_status: Optional[str] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log shipment status change."""
        return await self.log_action(
            action="shipment_status_changed",
            entity_type="shipment",
            user_id=user_id,
            entity_id=shipment_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "old_status": old_status,
                "new_status": new_status,
                "notes": notes
            }
        )
    
    async def get_recent_logs(
        self,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Retrieve recent audit logs.
        
        Args:
            user_id: Filter by user ID
            action: Filter by action type
            limit: Maximum number of logs to return
        
        Returns:
            List of audit logs
        """
        query = select(AuditLog).order_by(AuditLog.timestamp.desc())
        
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

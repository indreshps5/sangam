"""
Admin routes - protected endpoints requiring specific permissions.
Demonstrates role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sangam_api.core.database import get_db_session
from sangam_api.core.auth import get_current_user, PermissionChecker, require_role
from sangam_api.core.logging import get_logger
from sangam_api.models.user import User, Role
from sangam_api.services.audit_service import AuditService

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(PermissionChecker(["admin:read"])),
):
    """
    Admin dashboard - requires admin:read permission.
    
    This endpoint demonstrates permission-based access control.
    """
    return {
        "message": "Welcome to admin dashboard",
        "user": current_user.email,
        "roles": [role.name for role in current_user.roles],
    }


@router.get("/users")
async def list_users(
    current_user: User = Depends(PermissionChecker(["users:read"])),
    db: AsyncSession = Depends(get_db_session),
):
    """
    List all users - requires users:read permission.
    
    Only accessible to users with user management permissions.
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
            }
            for user in users
        ]
    }


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(PermissionChecker(["users:write"])),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Deactivate a user - requires users:write permission.
    
    Demonstrates write permission enforcement.
    """
    from uuid import UUID
    
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent self-deactivation
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    user.is_active = False
    
    # Log the action
    audit_service = AuditService(db)
    await audit_service.log_action(
        action="deactivate_user",
        entity_type="user",
        user_id=current_user.id,
        entity_id=user.id,
        changes={"is_active": False},
    )
    
    await db.commit()
    
    logger.info(
        "user_deactivated",
        deactivated_user_id=user_id,
        deactivated_by=str(current_user.id),
    )
    
    return {"message": f"User {user.email} has been deactivated"}


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    current_user: User = Depends(PermissionChecker(["audit:read"])),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get audit logs - requires audit:read permission.
    
    Only accessible to auditors and administrators.
    """
    audit_service = AuditService(db)
    logs = await audit_service.get_recent_logs(limit=limit)
    
    return {
        "logs": [
            {
                "id": str(log.id),
                "action": log.action,
                "entity_type": log.entity_type,
                "user_id": str(log.user_id) if log.user_id else None,
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
            }
            for log in logs
        ]
    }


@router.get("/super-admin-only")
async def super_admin_endpoint(
    current_user: User = Depends(require_role("super_admin")),
):
    """
    Super admin only endpoint - requires super_admin role.
    
    Demonstrates role-based (not permission-based) access control.
    """
    return {
        "message": "You are a super administrator",
        "user": current_user.email,
    }

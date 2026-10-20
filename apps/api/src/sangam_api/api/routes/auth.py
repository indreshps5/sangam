"""
Authentication routes.
Handles login, logout, token refresh, and current user retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sangam_api.core.database import get_db_session
from sangam_api.core.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_password_hash,
)
from sangam_api.core.logging import get_logger
from sangam_api.models.user import User, Role
from sangam_api.api.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    ChangePasswordRequest,
    MessageResponse,
)
from sangam_api.services.audit_service import AuditService
from sangam_api.config import get_settings

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Authenticate user and return JWT tokens.
    
    - Validates email and password
    - Returns short-lived access token and longer-lived refresh token
    - Logs login attempt in audit log
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        logger.warning(
            "login_failed",
            email=login_data.email,
            reason="invalid_credentials",
        )
        
        # Log failed login attempt if user exists
        if user:
            audit_service = AuditService(db)
            await audit_service.log_login(
                user_id=user.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                success=False,
            )
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(
            "login_failed",
            email=login_data.email,
            reason="user_inactive",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Load user roles
    await db.refresh(user, ["roles"])
    
    # Extract role names and permissions
    roles = [role.name for role in user.roles]
    permissions = []
    for role in user.roles:
        if role.permissions:
            import json
            try:
                perms = json.loads(role.permissions)
                permissions.extend(perms)
            except (json.JSONDecodeError, TypeError):
                pass
    
    # Remove duplicates from permissions
    permissions = list(set(permissions))
    
    # Generate tokens
    access_token = create_access_token(
        user_id=user.id,
        roles=roles,
        permissions=permissions,
    )
    refresh_token = create_refresh_token(user_id=user.id)
    
    # Log successful login
    audit_service = AuditService(db)
    await audit_service.log_login(
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )
    await db.commit()
    
    logger.info(
        "login_success",
        user_id=str(user.id),
        email=user.email,
        roles=roles,
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Refresh access token using refresh token.
    
    - Validates refresh token
    - Returns new access token and refresh token
    """
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    
    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Fetch user
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Load user roles
    await db.refresh(user, ["roles"])
    
    # Extract role names and permissions
    roles = [role.name for role in user.roles]
    permissions = []
    for role in user.roles:
        if role.permissions:
            import json
            try:
                perms = json.loads(role.permissions)
                permissions.extend(perms)
            except (json.JSONDecodeError, TypeError):
                pass
    
    permissions = list(set(permissions))
    
    # Generate new tokens
    access_token = create_access_token(
        user_id=user.id,
        roles=roles,
        permissions=permissions,
    )
    refresh_token = create_refresh_token(user_id=user.id)
    
    logger.info(
        "token_refreshed",
        user_id=str(user.id),
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Logout current user.
    
    Note: JWT tokens are stateless, so logout is client-side.
    This endpoint logs the logout event for audit purposes.
    """
    # Log logout event
    audit_service = AuditService(db)
    await audit_service.log_logout(
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()
    
    logger.info(
        "logout_success",
        user_id=str(current_user.id),
    )
    
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get current authenticated user information.
    
    - Returns user details without sensitive data
    - Includes roles and permissions
    """
    # Load user roles
    await db.refresh(current_user, ["roles"])
    
    # Extract role names and permissions
    roles = [role.name for role in current_user.roles]
    permissions = []
    for role in current_user.roles:
        if role.permissions:
            import json
            try:
                perms = json.loads(role.permissions)
                permissions.extend(perms)
            except (json.JSONDecodeError, TypeError):
                pass
    
    permissions = list(set(permissions))
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        roles=roles,
        permissions=permissions,
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Change current user's password.
    
    - Validates current password
    - Updates to new password
    - Logs password change in audit log
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    
    # Log password change
    audit_service = AuditService(db)
    await audit_service.log_password_change(
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    
    await db.commit()
    
    logger.info(
        "password_changed",
        user_id=str(current_user.id),
    )
    
    return MessageResponse(message="Password changed successfully")

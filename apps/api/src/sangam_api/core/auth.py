"""
Authentication and authorization module.
Handles JWT tokens, password hashing, and permission enforcement.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.config import get_settings
from sangam_api.core.database import get_db_session
from sangam_api.core.logging import get_logger
from sangam_api.models.user import User

logger = get_logger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(user_id: UUID, roles: list[str], permissions: list[str]) -> str:
    """
    Create a short-lived JWT access token.
    
    Args:
        user_id: User's UUID
        roles: List of role names
        permissions: List of permission strings
    
    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    
    to_encode = {
        "sub": str(user_id),
        "roles": roles,
        "permissions": permissions,
        "exp": expire,
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    return encoded_jwt


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a longer-lived refresh token.
    
    Note: Refresh tokens are not stored in the database for simplicity.
    In production, consider storing them in a secure database table
    with revocation capability.
    
    Args:
        user_id: User's UUID
    
    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError as e:
        logger.warning("token_decode_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials: Bearer token credentials
        db: Database session
    
    Returns:
        Current User object
    
    Raises:
        HTTPException: If user not found or token invalid
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    # Verify token type
    if payload.get("type") != "access":
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
    
    # Fetch user from database
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure user is active.
    Alias for get_current_user with explicit naming.
    """
    return current_user


class PermissionChecker:
    """
    Dependency class to check if user has required permissions.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(
            user: User = Depends(PermissionChecker(["admin:read", "admin:write"]))
        ):
            ...
    """
    
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:
        """
        Check if user has all required permissions.
        
        Args:
            current_user: Authenticated user
        
        Returns:
            User if authorized
        
        Raises:
            HTTPException: If user lacks required permissions
        """
        # Get user's permissions from token
        # In production, you might want to fetch fresh from DB
        # For now, we'll use a simplified check
        
        # Super admin has all permissions
        user_roles = [role.name for role in current_user.roles]
        if "super_admin" in user_roles:
            return current_user
        
        # Check if user has all required permissions
        # This is a simplified check - in production, you'd decode the token
        # and check permissions from there
        user_permissions = set()
        for role in current_user.roles:
            if role.permissions:
                import json
                try:
                    perms = json.loads(role.permissions)
                    user_permissions.update(perms)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Check for wildcard permissions
        if "*" in user_permissions:
            return current_user
        
        # Check each required permission
        for perm in self.required_permissions:
            # Check for exact match or wildcard in domain
            domain = perm.split(":")[0] if ":" in perm else perm
            if perm not in user_permissions and f"{domain}:*" not in user_permissions:
                logger.warning(
                    "permission_denied",
                    user_id=str(current_user.id),
                    required_permission=perm,
                    user_permissions=list(user_permissions),
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {perm}",
                )
        
        return current_user


def require_role(role_name: str):
    """
    Dependency to check if user has a specific role.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(
            user: User = Depends(require_role("admin"))
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_roles = [role.name for role in current_user.roles]
        if role_name not in user_roles:
            logger.warning(
                "role_denied",
                user_id=str(current_user.id),
                required_role=role_name,
                user_roles=user_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {role_name}",
            )
        return current_user
    
    return role_checker

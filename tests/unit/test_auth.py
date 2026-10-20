"""
Authentication tests.
Tests login, logout, token refresh, and current user endpoints.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sangam_api.main import app
from sangam_api.core.database import async_session_factory
from sangam_api.core.auth import (
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from sangam_api.models.user import User, Role
from sangam_api.config import get_settings


settings = get_settings()


@pytest.fixture
async def test_user():
    """Create a test user."""
    async with async_session_factory() as session:
        # Create role
        role = Role(
            id=uuid4(),
            name="test_role",
            description="Test role",
            permissions='["depots:read", "shipments:read"]',
            is_system=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(role)
        
        # Create user
        user = User(
            id=uuid4(),
            email="test@sangam.dev",
            full_name="Test User",
            hashed_password=get_password_hash("testpass123!"),
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        user.roles.append(role)
        session.add(user)
        
        await session.commit()
        await session.refresh(user)
        
        yield user
        
        # Cleanup
        await session.delete(user)
        await session.delete(role)
        await session.commit()


@pytest.mark.asyncio
async def test_login_success(test_user):
    """Test successful login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@sangam.dev",
                "password": "testpass123!",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == settings.access_token_expire_minutes * 60


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_user):
    """Test login with invalid credentials."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@sangam.dev",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
        
        # Wrong email
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@sangam.dev",
                "password": "testpass123!",
            },
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(test_user):
    """Test login with inactive user."""
    # Deactivate user
    async with async_session_factory() as session:
        test_user.is_active = False
        session.add(test_user)
        await session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@sangam.dev",
                "password": "testpass123!",
            },
        )
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(test_user):
    """Test getting current user info."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@sangam.dev",
                "password": "testpass123!",
            },
        )
        
        tokens = login_response.json()
        
        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "test@sangam.dev"
        assert data["full_name"] == "Test User"
        assert "test_role" in data["roles"]
        assert "depots:read" in data["permissions"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized():
    """Test getting current user without token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test getting current user with invalid token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(test_user):
    """Test token refresh."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@sangam.dev",
                "password": "testpass123!",
            },
        )
        
        tokens = login_response.json()
        
        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data


@pytest.mark.asyncio
async def test_logout(test_user):
    """Test logout."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@sangam.dev",
                "password": "testpass123!",
            },
        )
        
        tokens = login_response.json()
        
        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()


def test_password_hashing():
    """Test password hashing and verification."""
    password = "secure_password_123!"
    hashed = get_password_hash(password)
    
    # Verify correct password
    assert verify_password(password, hashed) is True
    
    # Verify wrong password
    assert verify_password("wrong_password", hashed) is False


def test_token_creation_and_decoding():
    """Test JWT token creation and decoding."""
    user_id = uuid4()
    roles = ["admin", "user"]
    permissions = ["depots:read", "shipments:write"]
    
    # Create access token
    access_token = create_access_token(user_id, roles, permissions)
    
    # Decode and verify
    payload = decode_token(access_token)
    
    assert payload["sub"] == str(user_id)
    assert payload["roles"] == roles
    assert payload["permissions"] == permissions
    assert payload["type"] == "access"
    assert "exp" in payload
    
    # Create refresh token
    refresh_token = create_refresh_token(user_id)
    
    # Decode and verify
    payload = decode_token(refresh_token)
    
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_expired_token():
    """Test expired token handling."""
    from jose import jwt
    
    user_id = uuid4()
    
    # Create expired token
    expire = datetime.now(timezone.utc) - timedelta(hours=1)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    
    expired_token = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    # Try to decode - should raise exception
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        decode_token(expired_token)
    
    assert exc_info.value.status_code == 401

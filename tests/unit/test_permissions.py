"""
Permission and authorization tests.
Tests role-based access control and permission enforcement.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timezone
from uuid import uuid4

from sangam_api.main import app
from sangam_api.core.database import async_session_factory
from sangam_api.core.auth import get_password_hash
from sangam_api.models.user import User, Role


@pytest.fixture
async def admin_user():
    """Create an admin user with full permissions."""
    async with async_session_factory() as session:
        role = Role(
            id=uuid4(),
            name="admin",
            description="Administrator",
            permissions='["*"]',
            is_system=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(role)
        
        user = User(
            id=uuid4(),
            email="admin_test@sangam.dev",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123!"),
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
        
        await session.delete(user)
        await session.delete(role)
        await session.commit()


@pytest.fixture
async def logistics_user():
    """Create a logistics officer user."""
    async with async_session_factory() as session:
        role = Role(
            id=uuid4(),
            name="logistics_officer",
            description="Logistics Officer",
            permissions='["shipments:read", "shipments:write", "routes:read"]',
            is_system=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(role)
        
        user = User(
            id=uuid4(),
            email="logistics_test@sangam.dev",
            full_name="Logistics Officer",
            hashed_password=get_password_hash("logistics123!"),
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
        
        await session.delete(user)
        await session.delete(role)
        await session.commit()


@pytest.fixture
async def viewer_user():
    """Create a viewer user with read-only permissions."""
    async with async_session_factory() as session:
        role = Role(
            id=uuid4(),
            name="viewer",
            description="Viewer",
            permissions='["depots:read", "shipments:read"]',
            is_system=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(role)
        
        user = User(
            id=uuid4(),
            email="viewer_test@sangam.dev",
            full_name="Viewer User",
            hashed_password=get_password_hash("viewer123!"),
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
        
        await session.delete(user)
        await session.delete(role)
        await session.commit()


@pytest.mark.asyncio
async def test_admin_access_admin_dashboard(admin_user):
    """Test admin can access admin dashboard."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin_test@sangam.dev",
                "password": "admin123!",
            },
        )
        tokens = login_response.json()
        
        # Access admin dashboard
        response = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        assert "admin dashboard" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_logistics_officer_cannot_access_admin(logistics_user):
    """Test logistics officer cannot access admin dashboard."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "logistics_test@sangam.dev",
                "password": "logistics123!",
            },
        )
        tokens = login_response.json()
        
        # Try to access admin dashboard
        response = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_viewer_cannot_write_shipments(viewer_user):
    """Test viewer cannot write shipments."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "viewer_test@sangam.dev",
                "password": "viewer123!",
            },
        )
        tokens = login_response.json()
        
        # Try to create a shipment (should fail)
        response = await client.post(
            "/api/v1/shipments/",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "origin_depot_id": str(uuid4()),
                "destination_depot_id": str(uuid4()),
                "weight_kg": 100.0,
                "volume_m3": 5.0,
            },
        )
        
        # Should be forbidden (403) or not found (404) depending on implementation
        assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_logistics_officer_can_read_shipments(logistics_user):
    """Test logistics officer can read shipments."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "logistics_test@sangam.dev",
                "password": "logistics123!",
            },
        )
        tokens = login_response.json()
        
        # Read shipments (should succeed)
        response = await client.get(
            "/api/v1/shipments/",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_list_users(admin_user):
    """Test admin can list users."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin_test@sangam.dev",
                "password": "admin123!",
            },
        )
        tokens = login_response.json()
        
        # List users
        response = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        assert "users" in response.json()


@pytest.mark.asyncio
async def test_viewer_cannot_list_users(viewer_user):
    """Test viewer cannot list users."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "viewer_test@sangam.dev",
                "password": "viewer123!",
            },
        )
        tokens = login_response.json()
        
        # Try to list users
        response = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_view_audit_logs(admin_user):
    """Test admin can view audit logs."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin_test@sangam.dev",
                "password": "admin123!",
            },
        )
        tokens = login_response.json()
        
        # View audit logs
        response = await client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        assert "logs" in response.json()


@pytest.mark.asyncio
async def test_logistics_officer_cannot_view_audit_logs(logistics_user):
    """Test logistics officer cannot view audit logs."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "logistics_test@sangam.dev",
                "password": "logistics123!",
            },
        )
        tokens = login_response.json()
        
        # Try to view audit logs
        response = await client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_access():
    """Test unauthenticated access to protected endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try to access admin dashboard without token
        response = await client.get("/api/v1/admin/dashboard")
        assert response.status_code == 401
        
        # Try to list users without token
        response = await client.get("/api/v1/admin/users")
        assert response.status_code == 401
        
        # Try to view audit logs without token
        response = await client.get("/api/v1/admin/audit-logs")
        assert response.status_code == 401

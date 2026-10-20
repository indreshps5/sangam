"""
Integration tests for inventory API endpoints.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timezone
from uuid import uuid4

from sangam_api.main import app
from sangam_api.core.database import async_session_factory
from sangam_api.core.auth import get_password_hash
from sangam_api.models.user import User, Role
from sangam_api.models.depot import Depot
from sangam_api.inventory.models import InventoryItem


@pytest.fixture
async def test_user_with_inventory_perms():
    """Create a test user with inventory permissions."""
    async with async_session_factory() as session:
        # Create role with inventory permissions
        role = Role(
            id=uuid4(),
            name="inventory_test_role",
            description="Test role with inventory permissions",
            permissions='["inventory:read", "inventory:write"]',
            is_system=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(role)
        
        # Create user
        user = User(
            id=uuid4(),
            email="inventory_test@sangam.dev",
            full_name="Inventory Test User",
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


@pytest.fixture
async def test_depot():
    """Create a test depot."""
    async with async_session_factory() as session:
        depot = Depot(
            id=uuid4(),
            name="Test Depot",
            code="TEST-DEPOT",
            depot_type="warehouse",
            status="active",
            region="Test Region",
            latitude=19.0760,
            longitude=72.8777,
            capacity_units=10000,
            current_utilization=0.5,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(depot)
        await session.commit()
        await session.refresh(depot)
        
        yield depot
        
        # Cleanup
        await session.delete(depot)
        await session.commit()


@pytest.fixture
async def test_inventory_item(test_depot):
    """Create a test inventory item."""
    async with async_session_factory() as session:
        item = InventoryItem(
            id=uuid4(),
            depot_id=test_depot.id,
            name="Test Item",
            sku="TEST-ITEM-001",
            category="Test",
            unit_of_measure="units",
            quantity_on_hand=100.0,
            quantity_reserved=10.0,
            min_stock_level=20.0,
            max_stock_level=200.0,
            unit_cost=10.0,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        
        yield item
        
        # Cleanup
        await session.delete(item)
        await session.commit()


@pytest.mark.asyncio
async def test_list_inventory_items(test_user_with_inventory_perms, test_inventory_item):
    """Test listing inventory items."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # List items
        response = await client.get(
            "/api/v1/inventory/items",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_inventory_items_with_filters(test_user_with_inventory_perms, test_inventory_item):
    """Test listing inventory items with filters."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # List items with search filter
        response = await client.get(
            "/api/v1/inventory/items",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"search": "Test"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_inventory_item(test_user_with_inventory_perms, test_inventory_item):
    """Test getting a specific inventory item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # Get item
        response = await client.get(
            f"/api/v1/inventory/items/{test_inventory_item.id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_inventory_item.id)
        assert data["name"] == "Test Item"
        assert data["quantity_available"] == 90.0


@pytest.mark.asyncio
async def test_create_inventory_item(test_user_with_inventory_perms, test_depot):
    """Test creating a new inventory item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # Create item
        response = await client.post(
            "/api/v1/inventory/items",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "depot_id": str(test_depot.id),
                "name": "New Test Item",
                "sku": "NEW-TEST-001",
                "category": "Test",
                "unit_of_measure": "units",
                "quantity_on_hand": 50.0,
                "quantity_reserved": 5.0,
                "min_stock_level": 10.0,
                "max_stock_level": 100.0,
                "unit_cost": 15.0,
                "currency": "USD",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Item"
        assert data["sku"] == "NEW-TEST-001"
        assert data["quantity_available"] == 45.0


@pytest.mark.asyncio
async def test_adjust_stock_receipt(test_user_with_inventory_perms, test_inventory_item):
    """Test adjusting stock with receipt."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # Adjust stock
        response = await client.post(
            f"/api/v1/inventory/items/{test_inventory_item.id}/adjust",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "adjustment_type": "receipt",
                "quantity": 50.0,
                "notes": "Test receipt",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_type"] == "receipt"
        assert data["quantity"] == 50.0


@pytest.mark.asyncio
async def test_adjust_stock_insufficient_quantity(test_user_with_inventory_perms, test_inventory_item):
    """Test adjusting stock with insufficient quantity."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # Try to consume more than available
        response = await client.post(
            f"/api/v1/inventory/items/{test_inventory_item.id}/adjust",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "adjustment_type": "consumption",
                "quantity": 200.0,  # More than on_hand (100)
                "notes": "Invalid consumption",
            },
        )
        
        assert response.status_code == 422
        assert "Insufficient stock" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_low_stock_alerts(test_user_with_inventory_perms, test_inventory_item):
    """Test getting low stock alerts."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # Get alerts
        response = await client.get(
            "/api/v1/inventory/alerts/low-stock",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_get_inventory_stats(test_user_with_inventory_perms, test_inventory_item):
    """Test getting inventory statistics."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # Get stats
        response = await client.get(
            "/api/v1/inventory/stats",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data
        assert "total_value" in data
        assert "low_stock_count" in data
        assert "out_of_stock_count" in data
        assert "total_quantity" in data
        assert "currency" in data


@pytest.mark.asyncio
async def test_list_transactions(test_user_with_inventory_perms, test_inventory_item):
    """Test listing inventory transactions."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inventory_test@sangam.dev",
                "password": "testpass123!",
            },
        )
        tokens = login_response.json()
        
        # List transactions
        response = await client.get(
            "/api/v1/inventory/transactions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test unauthorized access to inventory endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try to access without authentication
        response = await client.get("/api/v1/inventory/items")
        assert response.status_code == 401
        
        response = await client.get("/api/v1/inventory/stats")
        assert response.status_code == 401

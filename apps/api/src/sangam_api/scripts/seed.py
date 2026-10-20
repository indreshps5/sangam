"""
Database seed script for SANGAM.
Creates demonstration roles, users, depots, and sample data.

Usage:
    cd apps/api
    python -m sangam_api.scripts.seed

Roles created:
    - super_admin: Full system access
    - admin: Administrative access
    - logistics_officer: Shipment and route management
    - inventory_manager: Inventory operations
    - analyst: Data analysis and forecasting
    - viewer: Read-only access

Development users (created when DEV_SEED_USERS is set):
    - admin@sangam.dev / admin123! (Administrator)
    - logistics@sangam.dev / logistics123! (Logistics Officer)
    - inventory@sangam.dev / inventory123! (Inventory Manager)
    - analyst@sangam.dev / analyst123! (Analyst)
    - viewer@sangam.dev / viewer123! (Viewer)
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, text
from sangam_api.core.database import async_session_factory, engine, Base
from sangam_api.core.auth import get_password_hash
from sangam_api.core.permissions import ROLE_PERMISSIONS
from sangam_api.core.logging import get_logger
from sangam_api.models.user import User, Role
from sangam_api.models.depot import Depot
from sangam_api.models.shipment import Shipment, Route
from sangam_api.inventory.models import InventoryItem, InventoryTransaction
from sangam_api.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


async def create_roles():
    """Create demonstration roles with permissions."""
    async with async_session_factory() as session:
        for role_name, permissions in ROLE_PERMISSIONS.items():
            # Check if role exists
            result = await session.execute(
                select(Role).where(Role.name == role_name)
            )
            existing_role = result.scalar_one_or_none()
            
            if existing_role:
                logger.info(f"Role '{role_name}' already exists, skipping")
                continue
            
            role = Role(
                id=uuid4(),
                name=role_name,
                description=f"Demo role: {role_name.replace('_', ' ').title()}",
                permissions=json.dumps(permissions),
                is_system=(role_name == "super_admin"),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(role)
            logger.info(f"Created role: {role_name}")
        
        await session.commit()
        logger.info("Roles created successfully")


async def create_dev_users():
    """Create development users from environment variable or defaults."""
    async with async_session_factory() as session:
        # Check for dev seed users in environment
        dev_users_json = settings.dev_seed_users
        
        if dev_users_json:
            try:
                dev_users = json.loads(dev_users_json)
            except json.JSONDecodeError:
                logger.error("Invalid DEV_SEED_USERS JSON format")
                return
        else:
            # Default development users
            dev_users = [
                {
                    "email": "admin@sangam.dev",
                    "password": "admin123!",
                    "full_name": "System Administrator",
                    "roles": ["super_admin"],
                },
                {
                    "email": "logistics@sangam.dev",
                    "password": "logistics123!",
                    "full_name": "Priya Sharma - Logistics Officer",
                    "roles": ["logistics_officer"],
                },
                {
                    "email": "inventory@sangam.dev",
                    "password": "inventory123!",
                    "full_name": "Rajesh Kumar - Inventory Manager",
                    "roles": ["inventory_manager"],
                },
                {
                    "email": "analyst@sangam.dev",
                    "password": "analyst123!",
                    "full_name": "Ananya Patel - Supply Chain Analyst",
                    "roles": ["analyst"],
                },
                {
                    "email": "viewer@sangam.dev",
                    "password": "viewer123!",
                    "full_name": "Demo Viewer",
                    "roles": ["viewer"],
                },
            ]
        
        for user_data in dev_users:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info(f"User '{user_data['email']}' already exists, skipping")
                continue
            
            # Create user
            user = User(
                id=uuid4(),
                email=user_data["email"],
                full_name=user_data.get("full_name"),
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(user)
            await session.flush()
            
            # Assign roles
            for role_name in user_data.get("roles", []):
                result = await session.execute(
                    select(Role).where(Role.name == role_name)
                )
                role = result.scalar_one_or_none()
                if role:
                    user.roles.append(role)
                    logger.info(f"Assigned role '{role_name}' to user '{user_data['email']}'")
            
            logger.info(f"Created user: {user_data['email']}")
        
        await session.commit()
        logger.info("Development users created successfully")


async def create_sample_depots():
    """Create sample depot data."""
    async with async_session_factory() as session:
        # Check if depots already exist
        result = await session.execute(select(Depot).limit(1))
        if result.scalar_one_or_none():
            logger.info("Depots already exist, skipping")
            return
        
        depots = [
            {
                "name": "Mumbai Central Warehouse",
                "code": "WH-MUM-001",
                "depot_type": "warehouse",
                "status": "active",
                "region": "West India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "capacity_units": 50000,
                "current_utilization": 0.72,
                "address": "Plot 42, Andheri East, Mumbai 400093",
                "contact_email": "mumbai.wh@sangam.io",
            },
            {
                "name": "Delhi Distribution Center",
                "code": "DC-DEL-001",
                "depot_type": "distribution_center",
                "status": "active",
                "region": "North India",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "capacity_units": 75000,
                "current_utilization": 0.58,
                "address": "Sector 18, Noida, UP 201301",
                "contact_email": "delhi.dc@sangam.io",
            },
            {
                "name": "Bangalore Cold Storage",
                "code": "CS-BLR-001",
                "depot_type": "cold_storage",
                "status": "active",
                "region": "South India",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "capacity_units": 20000,
                "current_utilization": 0.85,
                "address": "Peenya Industrial Area, Bangalore 560058",
                "contact_email": "bangalore.cs@sangam.io",
            },
        ]
        
        for depot_data in depots:
            depot = Depot(
                id=uuid4(),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                **depot_data,
            )
            session.add(depot)
            logger.info(f"Created depot: {depot_data['name']}")
        
        await session.commit()
        logger.info("Sample depots created successfully")


async def create_sample_inventory():
    """Create sample inventory items and transactions."""
    async with async_session_factory() as session:
        # Check if inventory items already exist
        result = await session.execute(select(InventoryItem).limit(1))
        if result.scalar_one_or_none():
            logger.info("Inventory items already exist, skipping")
            return
        
        # Get depots
        depots_result = await session.execute(select(Depot))
        depots = depots_result.scalars().all()
        
        if not depots:
            logger.warning("No depots found, skipping inventory seeding")
            return
        
        # Sample inventory items for each depot
        inventory_items = [
            # Mumbai Warehouse
            {
                "depot_id": depots[0].id,
                "name": "Electronics - Smartphones",
                "sku": "ELEC-SMART-001",
                "category": "Electronics",
                "description": "Latest generation smartphones",
                "unit_of_measure": "units",
                "quantity_on_hand": 1250.0,
                "quantity_reserved": 150.0,
                "min_stock_level": 200.0,
                "max_stock_level": 2000.0,
                "unit_cost": 450.0,
                "currency": "USD",
                "location_code": "A-01-03",
            },
            {
                "depot_id": depots[0].id,
                "name": "Electronics - Laptops",
                "sku": "ELEC-LAPTOP-001",
                "category": "Electronics",
                "description": "Business laptops",
                "unit_of_measure": "units",
                "quantity_on_hand": 380.0,
                "quantity_reserved": 45.0,
                "min_stock_level": 100.0,
                "max_stock_level": 800.0,
                "unit_cost": 850.0,
                "currency": "USD",
                "location_code": "A-02-01",
            },
            {
                "depot_id": depots[0].id,
                "name": "Packaging Materials - Boxes",
                "sku": "PKG-BOX-001",
                "category": "Packaging",
                "description": "Standard shipping boxes",
                "unit_of_measure": "units",
                "quantity_on_hand": 5000.0,
                "quantity_reserved": 500.0,
                "min_stock_level": 1000.0,
                "max_stock_level": 10000.0,
                "unit_cost": 2.5,
                "currency": "USD",
                "location_code": "B-05-02",
            },
            # Delhi Distribution Center
            {
                "depot_id": depots[1].id,
                "name": "Consumer Goods - Beverages",
                "sku": "CONS-BEV-001",
                "category": "Consumer Goods",
                "description": "Bottled water (1L)",
                "unit_of_measure": "units",
                "quantity_on_hand": 8500.0,
                "quantity_reserved": 1200.0,
                "min_stock_level": 2000.0,
                "max_stock_level": 15000.0,
                "unit_cost": 0.5,
                "currency": "USD",
                "location_code": "C-01-01",
            },
            {
                "depot_id": depots[1].id,
                "name": "Consumer Goods - Snacks",
                "sku": "CONS-SNACK-001",
                "category": "Consumer Goods",
                "description": "Packaged snacks",
                "unit_of_measure": "units",
                "quantity_on_hand": 3200.0,
                "quantity_reserved": 400.0,
                "min_stock_level": 800.0,
                "max_stock_level": 6000.0,
                "unit_cost": 1.2,
                "currency": "USD",
                "location_code": "C-02-03",
            },
            {
                "depot_id": depots[1].id,
                "name": "Office Supplies - Paper",
                "sku": "OFF-PAPER-001",
                "category": "Office Supplies",
                "description": "A4 paper (500 sheets)",
                "unit_of_measure": "reams",
                "quantity_on_hand": 150.0,
                "quantity_reserved": 20.0,
                "min_stock_level": 50.0,
                "max_stock_level": 500.0,
                "unit_cost": 5.0,
                "currency": "USD",
                "location_code": "D-03-01",
            },
            # Bangalore Cold Storage
            {
                "depot_id": depots[2].id,
                "name": "Perishables - Dairy Products",
                "sku": "PERISH-DAIRY-001",
                "category": "Perishables",
                "description": "Milk and dairy products",
                "unit_of_measure": "liters",
                "quantity_on_hand": 2500.0,
                "quantity_reserved": 300.0,
                "min_stock_level": 500.0,
                "max_stock_level": 5000.0,
                "unit_cost": 1.5,
                "currency": "USD",
                "location_code": "CS-01-01",
            },
            {
                "depot_id": depots[2].id,
                "name": "Perishables - Frozen Foods",
                "sku": "PERISH-FROZEN-001",
                "category": "Perishables",
                "description": "Frozen vegetables and meals",
                "unit_of_measure": "kg",
                "quantity_on_hand": 1800.0,
                "quantity_reserved": 250.0,
                "min_stock_level": 400.0,
                "max_stock_level": 3000.0,
                "unit_cost": 3.5,
                "currency": "USD",
                "location_code": "CS-02-01",
            },
            {
                "depot_id": depots[2].id,
                "name": "Perishables - Fresh Produce",
                "sku": "PERISH-PRODUCE-001",
                "category": "Perishables",
                "description": "Fresh fruits and vegetables",
                "unit_of_measure": "kg",
                "quantity_on_hand": 85.0,  # Low stock example
                "quantity_reserved": 10.0,
                "min_stock_level": 200.0,
                "max_stock_level": 1000.0,
                "unit_cost": 2.0,
                "currency": "USD",
                "location_code": "CS-03-01",
            },
        ]
        
        created_items = []
        for item_data in inventory_items:
            item = InventoryItem(
                id=uuid4(),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                **item_data,
            )
            session.add(item)
            created_items.append(item)
            logger.info(f"Created inventory item: {item_data['name']}")
        
        await session.flush()
        
        # Create sample transactions
        transactions = [
            {
                "inventory_item_id": created_items[0].id,
                "depot_id": created_items[0].depot_id,
                "transaction_type": "receipt",
                "quantity": 500.0,
                "unit_of_measure": "units",
                "notes": "Initial stock receipt",
                "performed_at": datetime.now(timezone.utc),
            },
            {
                "inventory_item_id": created_items[0].id,
                "depot_id": created_items[0].depot_id,
                "transaction_type": "shipment",
                "quantity": -150.0,
                "unit_of_measure": "units",
                "notes": "Shipped to Delhi DC",
                "performed_at": datetime.now(timezone.utc),
            },
            {
                "inventory_item_id": created_items[3].id,
                "depot_id": created_items[3].depot_id,
                "transaction_type": "receipt",
                "quantity": 2000.0,
                "unit_of_measure": "units",
                "notes": "Bulk receipt from supplier",
                "performed_at": datetime.now(timezone.utc),
            },
            {
                "inventory_item_id": created_items[8].id,
                "depot_id": created_items[8].depot_id,
                "transaction_type": "consumption",
                "quantity": -115.0,
                "unit_of_measure": "kg",
                "notes": "Damage and spoilage adjustment",
                "performed_at": datetime.now(timezone.utc),
            },
        ]
        
        for txn_data in transactions:
            transaction = InventoryTransaction(
                id=uuid4(),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                **txn_data,
            )
            session.add(transaction)
            logger.info(f"Created transaction: {txn_data['transaction_type']} for {txn_data['quantity']}")
        
        await session.commit()
        logger.info(f"Sample inventory created: {len(inventory_items)} items, {len(transactions)} transactions")


async def seed_database():
    """Main seed function."""
    logger.info("Starting database seeding...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed data
    await create_roles()
    await create_dev_users()
    await create_sample_depots()
    await create_sample_inventory()
    
    logger.info("Database seeding completed successfully")
    logger.info("")
    logger.info("Development users created:")
    logger.info("  - admin@sangam.dev / admin123! (Super Admin)")
    logger.info("  - logistics@sangam.dev / logistics123! (Logistics Officer)")
    logger.info("  - inventory@sangam.dev / inventory123! (Inventory Manager)")
    logger.info("  - analyst@sangam.dev / analyst123! (Analyst)")
    logger.info("  - viewer@sangam.dev / viewer123! (Viewer)")
    logger.info("")
    logger.info("Sample data created:")
    logger.info("  - 3 depots (Mumbai, Delhi, Bangalore)")
    logger.info("  - 9 inventory items across all depots")
    logger.info("  - 4 sample transactions")


if __name__ == "__main__":
    asyncio.run(seed_database())

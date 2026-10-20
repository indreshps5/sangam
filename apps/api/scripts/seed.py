"""
Seed script for SANGAM database.
Populates the database with clearly labelled synthetic data for development and testing.

Usage:
    cd apps/api
    python -m scripts.seed

All data is synthetic and clearly marked as such.
"""

import asyncio
import sys
from datetime import datetime, date, timezone, timedelta
from uuid import uuid4

# Add parent to path for imports
sys.path.insert(0, "src")

from sqlalchemy import text
from sangam_api.core.database import engine, async_session_factory


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA — Clearly labelled for development/testing
# ═══════════════════════════════════════════════════════════════

SYNTHETIC_ROLES = [
    {
        "id": "a0000000-0000-0000-0000-000000000001",
        "name": "super_admin",
        "description": "[SYNTHETIC] Full system access",
        "permissions": '["*"]',
        "is_system": True,
    },
    {
        "id": "a0000000-0000-0000-0000-000000000002",
        "name": "admin",
        "description": "[SYNTHETIC] Administrative access",
        "permissions": '["depots:*", "shipments:*", "users:read", "forecasts:read"]',
        "is_system": True,
    },
    {
        "id": "a0000000-0000-0000-0000-000000000003",
        "name": "manager",
        "description": "[SYNTHETIC] Regional manager",
        "permissions": '["depots:read", "shipments:*", "inventory:*", "forecasts:read"]',
        "is_system": False,
    },
    {
        "id": "a0000000-0000-0000-0000-000000000004",
        "name": "operator",
        "description": "[SYNTHETIC] Warehouse operator",
        "permissions": '["inventory:*", "shipments:read"]',
        "is_system": False,
    },
    {
        "id": "a0000000-0000-0000-0000-000000000005",
        "name": "analyst",
        "description": "[SYNTHETIC] Data analyst",
        "permissions": '["depots:read", "forecasts:*", "recommendations:*", "audit:read"]',
        "is_system": False,
    },
]

SYNTHETIC_USERS = [
    {
        "id": "b0000000-0000-0000-0000-000000000001",
        "email": "admin@sangam.dev",
        "username": "admin",
        "hashed_password": "$2b$12$LJ3m4ys3Lg0VQZ5XzYzYzOQKJvVxZ5XzYzYzOQKJvVxZ5XzYzYzO",  # [SYNTHETIC] not a real password
        "full_name": "[SYNTHETIC] System Administrator",
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "b0000000-0000-0000-0000-000000000002",
        "email": "manager.mumbai@sangam.dev",
        "username": "mgr_mumbai",
        "hashed_password": "$2b$12$LJ3m4ys3Lg0VQZ5XzYzYzOQKJvVxZ5XzYzYzOQKJvVxZ5XzYzYzO",
        "full_name": "[SYNTHETIC] Priya Sharma — Mumbai Regional Manager",
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "b0000000-0000-0000-0000-000000000003",
        "email": "operator.delhi@sangam.dev",
        "username": "opr_delhi",
        "hashed_password": "$2b$12$LJ3m4ys3Lg0VQZ5XzYzYzOQKJvVxZ5XzYzYzOQKJvVxZ5XzYzYzO",
        "full_name": "[SYNTHETIC] Rajesh Kumar — Delhi Warehouse Operator",
        "is_active": True,
        "is_verified": True,
    },
    {
        "id": "b0000000-0000-0000-0000-000000000004",
        "email": "analyst@sangam.dev",
        "username": "analyst_01",
        "hashed_password": "$2b$12$LJ3m4ys3Lg0VQZ5XzYzYzOQKJvVxZ5XzYzYzOQKJvVxZ5XzYzYzO",
        "full_name": "[SYNTHETIC] Ananya Patel — Supply Chain Analyst",
        "is_active": True,
        "is_verified": True,
    },
]

SYNTHETIC_DEPOTS = [
    {
        "id": "c0000000-0000-0000-0000-000000000001",
        "name": "[SYNTHETIC] Mumbai Central Warehouse",
        "code": "WH-MUM-001",
        "depot_type": "warehouse",
        "status": "active",
        "region": "South Asia",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "capacity_units": 50000,
        "current_utilization": 0.72,
        "address": "[SYNTHETIC] Plot 42, Andheri East, Mumbai 400093",
        "contact_email": "mumbai.wh@sangam.dev",
    },
    {
        "id": "c0000000-0000-0000-0000-000000000002",
        "name": "[SYNTHETIC] Delhi Distribution Center",
        "code": "DC-DEL-001",
        "depot_type": "distribution_center",
        "status": "active",
        "region": "South Asia",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "capacity_units": 75000,
        "current_utilization": 0.58,
        "address": "[SYNTHETIC] Sector 18, Noida, UP 201301",
        "contact_email": "delhi.dc@sangam.dev",
    },
    {
        "id": "c0000000-0000-0000-0000-000000000003",
        "name": "[SYNTHETIC] Bangalore Cold Storage",
        "code": "CS-BLR-001",
        "depot_type": "cold_storage",
        "status": "active",
        "region": "South Asia",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "capacity_units": 20000,
        "current_utilization": 0.85,
        "address": "[SYNTHETIC] Peenya Industrial Area, Bangalore 560058",
        "contact_email": "bangalore.cs@sangam.dev",
    },
    {
        "id": "c0000000-0000-0000-0000-000000000004",
        "name": "[SYNTHETIC] Chennai Cross-Dock",
        "code": "XD-CHN-001",
        "depot_type": "cross_dock",
        "status": "active",
        "region": "South Asia",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "capacity_units": 30000,
        "current_utilization": 0.41,
        "address": "[SYNTHETIC] Guindy Industrial Estate, Chennai 600032",
        "contact_email": "chennai.xd@sangam.dev",
    },
    {
        "id": "c0000000-0000-0000-0000-000000000005",
        "name": "[SYNTHETIC] Singapore Regional Hub",
        "code": "RH-SIN-001",
        "depot_type": "distribution_center",
        "status": "active",
        "region": "Asia Pacific",
        "latitude": 1.3521,
        "longitude": 103.8198,
        "capacity_units": 100000,
        "current_utilization": 0.63,
        "address": "[SYNTHETIC] 21 Jurong Port Road, Singapore 619117",
        "contact_email": "singapore.hub@sangam.dev",
    },
]

SYNTHETIC_ROUTES = [
    {
        "id": "d0000000-0000-0000-0000-000000000001",
        "name": "[SYNTHETIC] Mumbai-Delhi Express Corridor",
        "code": "RT-MUM-DEL-001",
        "origin_depot_id": "c0000000-0000-0000-0000-000000000001",
        "destination_depot_id": "c0000000-0000-0000-0000-000000000002",
        "status": "active",
        "distance_km": 1395.0,
        "estimated_duration_hours": 24.0,
        "optimization_objective": "minimize_time",
        "vehicle_type": "truck_heavy",
        "max_weight_kg": 20000.0,
        "max_volume_m3": 80.0,
        "cost_per_km": 45.0,
        "carbon_emission_factor": 0.89,
    },
    {
        "id": "d0000000-0000-0000-0000-000000000002",
        "name": "[SYNTHETIC] Mumbai-Bangalore Tech Route",
        "code": "RT-MUM-BLR-001",
        "origin_depot_id": "c0000000-0000-0000-0000-000000000001",
        "destination_depot_id": "c0000000-0000-0000-0000-000000000003",
        "status": "active",
        "distance_km": 985.0,
        "estimated_duration_hours": 16.0,
        "optimization_objective": "balanced",
        "vehicle_type": "truck_medium",
        "max_weight_kg": 12000.0,
        "max_volume_m3": 60.0,
        "cost_per_km": 40.0,
        "carbon_emission_factor": 0.75,
    },
    {
        "id": "d0000000-0000-0000-0000-000000000003",
        "name": "[SYNTHETIC] Singapore-Mumbai International",
        "code": "RT-SIN-MUM-001",
        "origin_depot_id": "c0000000-0000-0000-0000-000000000005",
        "destination_depot_id": "c0000000-0000-0000-0000-000000000001",
        "status": "planned",
        "distance_km": 3900.0,
        "estimated_duration_hours": 120.0,
        "optimization_objective": "minimize_cost",
        "vehicle_type": "container_ship",
        "max_weight_kg": 200000.0,
        "max_volume_m3": 1000.0,
        "cost_per_km": 12.0,
        "carbon_emission_factor": 0.015,
    },
]

SYNTHETIC_SHIPMENTS = [
    {
        "id": "e0000000-0000-0000-0000-000000000001",
        "origin_depot_id": "c0000000-0000-0000-0000-000000000001",
        "destination_depot_id": "c0000000-0000-0000-0000-000000000002",
        "route_id": "d0000000-0000-0000-0000-000000000001",
        "status": "in_transit",
        "weight_kg": 5200.0,
        "volume_m3": 22.5,
        "priority": 2,
        "shipment_type": "express",
        "carrier_name": "[SYNTHETIC] BlueDart Express",
        "tracking_number": "SANGAM-SHP-001",
    },
    {
        "id": "e0000000-0000-0000-0000-000000000002",
        "origin_depot_id": "c0000000-0000-0000-0000-000000000005",
        "destination_depot_id": "c0000000-0000-0000-0000-000000000001",
        "route_id": "d0000000-0000-0000-0000-000000000003",
        "status": "pending",
        "weight_kg": 48000.0,
        "volume_m3": 220.0,
        "priority": 3,
        "shipment_type": "standard",
        "carrier_name": "[SYNTHETIC] Maersk Line",
        "tracking_number": "SANGAM-SHP-002",
    },
    {
        "id": "e0000000-0000-0000-0000-000000000003",
        "origin_depot_id": "c0000000-0000-0000-0000-000000000001",
        "destination_depot_id": "c0000000-0000-0000-0000-000000000003",
        "route_id": "d0000000-0000-0000-0000-000000000002",
        "status": "delivered",
        "weight_kg": 3100.0,
        "volume_m3": 15.0,
        "priority": 1,
        "shipment_type": "express",
        "carrier_name": "[SYNTHETIC] Delhivery",
        "tracking_number": "SANGAM-SHP-003",
    },
]


async def seed_database() -> None:
    """Seed the database with synthetic data."""
    print("[SEED] Starting database seeding with synthetic data...")

    async with async_session_factory() as session:
        try:
            # Roles
            for role in SYNTHETIC_ROLES:
                await session.execute(text("""
                    INSERT INTO roles (id, name, description, permissions, is_system, created_at, updated_at)
                    VALUES (:id, :name, :description, :permissions, :is_system, NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING
                """), role)
            print(f"[SEED] Inserted {len(SYNTHETIC_ROLES)} synthetic roles")

            # Users
            for user in SYNTHETIC_USERS:
                await session.execute(text("""
                    INSERT INTO users (id, email, username, hashed_password, full_name, is_active, is_verified, created_at, updated_at)
                    VALUES (:id, :email, :username, :hashed_password, :full_name, :is_active, :is_verified, NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING
                """), user)
            print(f"[SEED] Inserted {len(SYNTHETIC_USERS)} synthetic users")

            # User-Role assignments
            user_role_pairs = [
                ("b0000000-0000-0000-0000-000000000001", "a0000000-0000-0000-0000-000000000001"),  # admin -> super_admin
                ("b0000000-0000-0000-0000-000000000002", "a0000000-0000-0000-0000-000000000003"),  # mgr -> manager
                ("b0000000-0000-0000-0000-000000000003", "a0000000-0000-0000-0000-000000000004"),  # opr -> operator
                ("b0000000-0000-0000-0000-000000000004", "a0000000-0000-0000-0000-000000000005"),  # analyst -> analyst
            ]
            for user_id, role_id in user_role_pairs:
                await session.execute(text("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (:user_id::uuid, :role_id::uuid)
                    ON CONFLICT DO NOTHING
                """), {"user_id": user_id, "role_id": role_id})
            print(f"[SEED] Assigned {len(user_role_pairs)} synthetic user-role pairs")

            # Depots
            for depot in SYNTHETIC_DEPOTS:
                await session.execute(text("""
                    INSERT INTO depots (id, name, code, depot_type, status, region, latitude, longitude,
                                       capacity_units, current_utilization, address, contact_email, created_at, updated_at)
                    VALUES (:id, :name, :code, :depot_type, :status, :region, :latitude, :longitude,
                           :capacity_units, :current_utilization, :address, :contact_email, NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING
                """), depot)
            print(f"[SEED] Inserted {len(SYNTHETIC_DEPOTS)} synthetic depots")

            # Routes
            for route in SYNTHETIC_ROUTES:
                await session.execute(text("""
                    INSERT INTO routes (id, name, code, origin_depot_id, destination_depot_id, status,
                                       distance_km, estimated_duration_hours, optimization_objective,
                                       vehicle_type, max_weight_kg, max_volume_m3, cost_per_km,
                                       carbon_emission_factor, created_at, updated_at)
                    VALUES (:id, :name, :code, :origin_depot_id::uuid, :destination_depot_id::uuid, :status,
                           :distance_km, :estimated_duration_hours, :optimization_objective,
                           :vehicle_type, :max_weight_kg, :max_volume_m3, :cost_per_km,
                           :carbon_emission_factor, NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING
                """), route)
            print(f"[SEED] Inserted {len(SYNTHETIC_ROUTES)} synthetic routes")

            # Shipments
            for shipment in SYNTHETIC_SHIPMENTS:
                await session.execute(text("""
                    INSERT INTO shipments (id, origin_depot_id, destination_depot_id, route_id, status,
                                          weight_kg, volume_m3, priority, shipment_type, carrier_name,
                                          tracking_number, created_at, updated_at)
                    VALUES (:id, :origin_depot_id::uuid, :destination_depot_id::uuid, :route_id::uuid, :status,
                           :weight_kg, :volume_m3, :priority, :shipment_type, :carrier_name,
                           :tracking_number, NOW(), NOW())
                    ON CONFLICT (id) DO NOTHING
                """), shipment)
            print(f"[SEED] Inserted {len(SYNTHETIC_SHIPMENTS)} synthetic shipments")

            await session.commit()
            print("[SEED] ✓ Database seeded successfully with synthetic data")
            print("[SEED] NOTE: All data is synthetic and clearly labelled [SYNTHETIC]")

        except Exception as e:
            await session.rollback()
            print(f"[SEED] ✗ Seeding failed: {e}")
            raise


def main():
    """Entry point for seed script."""
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()

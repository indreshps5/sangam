"""
Centralized permission definitions for SANGAM.
All permissions are defined here and referenced throughout the application.

Permission format: "domain:action"
- domain: The resource domain (e.g., depots, shipments, users, admin)
- action: The action type (read, write, delete, admin)

Wildcard permissions:
- "domain:*" grants all actions in a domain
- "*" grants all permissions (super admin)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    """Immutable permission definition."""
    domain: str
    action: str
    description: str
    
    @property
    def key(self) -> str:
        """Full permission key (domain:action)."""
        return f"{self.domain}:{self.action}"
    
    @property
    def wildcard(self) -> str:
        """Wildcard permission for this domain."""
        return f"{self.domain}:*"


# ═══════════════════════════════════════════════════════════════
# DEPOT PERMISSIONS
# ═══════════════════════════════════════════════════════════════

DEPOT_READ = Permission("depots", "read", "View depot information")
DEPOT_WRITE = Permission("depots", "write", "Create and update depots")
DEPOT_DELETE = Permission("depots", "delete", "Delete depots")

# ═══════════════════════════════════════════════════════════════
# SHIPMENT PERMISSIONS
# ═══════════════════════════════════════════════════════════════

SHIPMENT_READ = Permission("shipments", "read", "View shipment information")
SHIPMENT_WRITE = Permission("shipments", "write", "Create and update shipments")
SHIPMENT_DELETE = Permission("shipments", "delete", "Delete shipments")
SHIPMENT_DISPATCH = Permission("shipments", "dispatch", "Dispatch shipments")

# ═══════════════════════════════════════════════════════════════
# INVENTORY PERMISSIONS
# ═══════════════════════════════════════════════════════════════

INVENTORY_READ = Permission("inventory", "read", "View inventory information")
INVENTORY_WRITE = Permission("inventory", "write", "Update inventory levels")
INVENTORY_ADJUST = Permission("inventory", "adjust", "Make inventory adjustments")
INVENTORY_TRANSFER = Permission("inventory", "transfer", "Transfer inventory between depots")

# ═══════════════════════════════════════════════════════════════
# FORECAST PERMISSIONS
# ═══════════════════════════════════════════════════════════════

FORECAST_READ = Permission("forecasts", "read", "View demand forecasts")
FORECAST_WRITE = Permission("forecasts", "write", "Create and update forecasts")
FORECAST_RUN = Permission("forecasts", "run", "Run forecast models")

# ═══════════════════════════════════════════════════════════════
# ROUTE PERMISSIONS
# ═══════════════════════════════════════════════════════════════

ROUTE_READ = Permission("routes", "read", "View route information")
ROUTE_WRITE = Permission("routes", "write", "Create and update routes")
ROUTE_OPTIMIZE = Permission("routes", "optimize", "Run route optimization")

# ═══════════════════════════════════════════════════════════════
# USER MANAGEMENT PERMISSIONS
# ═══════════════════════════════════════════════════════════════

USER_READ = Permission("users", "read", "View user information")
USER_WRITE = Permission("users", "write", "Create and update users")
USER_DELETE = Permission("users", "delete", "Delete users")
USER_ASSIGN_ROLE = Permission("users", "assign_role", "Assign roles to users")

# ═══════════════════════════════════════════════════════════════
# ROLE MANAGEMENT PERMISSIONS
# ═══════════════════════════════════════════════════════════════

ROLE_READ = Permission("roles", "read", "View role definitions")
ROLE_WRITE = Permission("roles", "write", "Create and update roles")
ROLE_DELETE = Permission("roles", "delete", "Delete roles")

# ═══════════════════════════════════════════════════════════════
# AUDIT PERMISSIONS
# ═══════════════════════════════════════════════════════════════

AUDIT_READ = Permission("audit", "read", "View audit logs")

# ═══════════════════════════════════════════════════════════════
# ADMIN PERMISSIONS
# ═══════════════════════════════════════════════════════════════

ADMIN_READ = Permission("admin", "read", "Access admin dashboard")
ADMIN_SYSTEM = Permission("admin", "system", "System administration")

# ═══════════════════════════════════════════════════════════════
# SENSOR & ALERT PERMISSIONS
# ═══════════════════════════════════════════════════════════════

SENSOR_READ = Permission("sensors", "read", "View sensor data")
SENSOR_WRITE = Permission("sensors", "write", "Configure sensors")
ALERT_READ = Permission("alerts", "read", "View alerts")
ALERT_ACKNOWLEDGE = Permission("alerts", "acknowledge", "Acknowledge alerts")

# ═══════════════════════════════════════════════════════════════
# SIMULATION & RECOMMENDATION PERMISSIONS
# ═══════════════════════════════════════════════════════════════

SIMULATION_READ = Permission("simulations", "read", "View simulation scenarios")
SIMULATION_WRITE = Permission("simulations", "write", "Create simulations")
SIMULATION_RUN = Permission("simulations", "run", "Run simulations")
RECOMMENDATION_READ = Permission("recommendations", "read", "View recommendations")
RECOMMENDATION_APPROVE = Permission("recommendations", "approve", "Approve recommendations")


# ═══════════════════════════════════════════════════════════════
# ROLE DEFINITIONS
# ═══════════════════════════════════════════════════════════════

# All permissions list for reference
ALL_PERMISSIONS = [
    DEPOT_READ, DEPOT_WRITE, DEPOT_DELETE,
    SHIPMENT_READ, SHIPMENT_WRITE, SHIPMENT_DELETE, SHIPMENT_DISPATCH,
    INVENTORY_READ, INVENTORY_WRITE, INVENTORY_ADJUST, INVENTORY_TRANSFER,
    FORECAST_READ, FORECAST_WRITE, FORECAST_RUN,
    ROUTE_READ, ROUTE_WRITE, ROUTE_OPTIMIZE,
    USER_READ, USER_WRITE, USER_DELETE, USER_ASSIGN_ROLE,
    ROLE_READ, ROLE_WRITE, ROLE_DELETE,
    AUDIT_READ,
    ADMIN_READ, ADMIN_SYSTEM,
    SENSOR_READ, SENSOR_WRITE,
    ALERT_READ, ALERT_ACKNOWLEDGE,
    SIMULATION_READ, SIMULATION_WRITE, SIMULATION_RUN,
    RECOMMENDATION_READ, RECOMMENDATION_APPROVE,
]


# Role permission mappings
ROLE_PERMISSIONS = {
    "super_admin": ["*"],  # All permissions
    
    "admin": [
        ADMIN_READ.key,
        DEPOT_READ.key, DEPOT_WRITE.key, DEPOT_DELETE.key,
        SHIPMENT_READ.key, SHIPMENT_WRITE.key, SHIPMENT_DELETE.key,
        INVENTORY_READ.key, INVENTORY_WRITE.key, INVENTORY_ADJUST.key, INVENTORY_TRANSFER.key,
        FORECAST_READ.key, FORECAST_WRITE.key, FORECAST_RUN.key,
        ROUTE_READ.key, ROUTE_WRITE.key, ROUTE_OPTIMIZE.key,
        USER_READ.key, USER_WRITE.key, USER_ASSIGN_ROLE.key,
        ROLE_READ.key,
        AUDIT_READ.key,
        SENSOR_READ.key, SENSOR_WRITE.key,
        ALERT_READ.key, ALERT_ACKNOWLEDGE.key,
        SIMULATION_READ.key, SIMULATION_WRITE.key, SIMULATION_RUN.key,
        RECOMMENDATION_READ.key, RECOMMENDATION_APPROVE.key,
    ],
    
    "logistics_officer": [
        SHIPMENT_READ.key, SHIPMENT_WRITE.key, SHIPMENT_DISPATCH.key,
        ROUTE_READ.key, ROUTE_WRITE.key,
        DEPOT_READ.key,
        INVENTORY_READ.key,
        FORECAST_READ.key,
        ALERT_READ.key, ALERT_ACKNOWLEDGE.key,
        SENSOR_READ.key,
    ],
    
    "inventory_manager": [
        INVENTORY_READ.key, INVENTORY_WRITE.key, INVENTORY_ADJUST.key, INVENTORY_TRANSFER.key,
        DEPOT_READ.key,
        SHIPMENT_READ.key,
        FORECAST_READ.key, FORECAST_WRITE.key,
        SENSOR_READ.key,
        ALERT_READ.key,
    ],
    
    "analyst": [
        FORECAST_READ.key, FORECAST_RUN.key,
        SIMULATION_READ.key, SIMULATION_WRITE.key, SIMULATION_RUN.key,
        RECOMMENDATION_READ.key,
        AUDIT_READ.key,
        DEPOT_READ.key,
        SHIPMENT_READ.key,
        INVENTORY_READ.key,
        ROUTE_READ.key,
        SENSOR_READ.key,
        ALERT_READ.key,
    ],
    
    "viewer": [
        DEPOT_READ.key,
        SHIPMENT_READ.key,
        INVENTORY_READ.key,
        FORECAST_READ.key,
        ROUTE_READ.key,
        SENSOR_READ.key,
        ALERT_READ.key,
    ],
}


def get_permissions_for_role(role_name: str) -> list[str]:
    """Get permission keys for a given role."""
    return ROLE_PERMISSIONS.get(role_name, [])


def get_all_permission_keys() -> list[str]:
    """Get all permission keys."""
    return [p.key for p in ALL_PERMISSIONS]

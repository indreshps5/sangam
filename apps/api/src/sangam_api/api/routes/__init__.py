"""
API Router aggregation.
All route modules are registered here for clean separation.
"""

from fastapi import APIRouter

from sangam_api.api.routes.health import router as health_router
from sangam_api.api.routes.auth import router as auth_router
from sangam_api.api.routes.admin import router as admin_router
from sangam_api.api.routes.depots import router as depots_router
from sangam_api.api.routes.shipments import router as shipments_router
from sangam_api.api.routes.forecasts import router as forecasts_router
from sangam_api.inventory.router import router as inventory_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(depots_router, prefix="/depots", tags=["depots"])
api_router.include_router(shipments_router, prefix="/shipments", tags=["shipments"])
api_router.include_router(forecasts_router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(inventory_router)

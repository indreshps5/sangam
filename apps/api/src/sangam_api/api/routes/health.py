"""
Health check endpoints.
Used for load balancer probes and monitoring.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db_session

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check - returns 200 if service is running."""
    return {
        "status": "healthy",
        "service": "sangam-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db_session)):
    """
    Readiness check - verifies database connectivity.
    Returns 503 if database is unreachable.
    """
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/health/live")
async def liveness_check():
    """Liveness probe - lightweight check for container orchestration."""
    return {"status": "alive"}

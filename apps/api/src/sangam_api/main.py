"""
SANGAM API - FastAPI Application Entry Point

Architecture: Router → Application Service → Repository Interface → Repository Implementation
Follows SOLID principles with dependency injection.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sangam_api.config import get_settings
from sangam_api.core.logging import setup_logging
from sangam_api.core.database import engine, Base
from sangam_api.api.routes import api_router
from sangam_api.api.middleware import ErrorHandlingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager - handles startup and shutdown."""
    setup_logging()
    # Startup: create tables (dev only - use migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory following dependency injection pattern."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="SANGAM Predictive Logistics & Forward Supply Chain API",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ErrorHandlingMiddleware)

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()

"""
Forecast routes - delegates to ML service for predictions.
"""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.core.database import get_db_session
from sangam_api.api.schemas.forecasts import (
    ForecastRequest,
    ForecastResponse,
    ForecastListResponse,
)
from sangam_api.services.forecast_service import ForecastService

router = APIRouter()


def get_forecast_service(
    db: AsyncSession = Depends(get_db_session),
) -> ForecastService:
    """Dependency injection for ForecastService."""
    return ForecastService()


@router.post("/predict", response_model=ForecastResponse)
async def create_forecast(
    payload: ForecastRequest,
    service: ForecastService = Depends(get_forecast_service),
) -> ForecastResponse:
    """Generate a demand forecast."""
    return await service.generate_forecast(payload)


@router.get("/", response_model=ForecastListResponse)
async def list_forecasts(
    warehouse_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: ForecastService = Depends(get_forecast_service),
) -> ForecastListResponse:
    """List historical forecasts."""
    return await service.list_forecasts(
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date,
    )

"""
Forecasting API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from sangam_api.core.database import get_db
from sangam_api.forecasting.service import ForecastingService
from sangam_api.forecasting.schemas import (
    ForecastRequest,
    ForecastResponse,
    ShortageRiskRequest,
    ShortageRiskResponse,
    ForecastSummary,
    ForecastListResponse
)

router = APIRouter(prefix="/forecasting", tags=["forecasting"])


@router.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate demand forecast for an inventory item.
    
    This endpoint:
    - Retrieves historical consumption data
    - Validates data sufficiency
    - Trains forecasting model
    - Generates predictions with confidence intervals
    - Evaluates model if sufficient test data exists
    - Saves forecast to database
    
    Returns forecast results with model metadata and evaluation metrics.
    """
    try:
        service = ForecastingService(db)
        result = await service.generate_forecast(
            inventory_item_id=request.inventory_item_id,
            horizon_days=request.horizon_days,
            model_type=request.model_type,
            confidence_level=request.confidence_level
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate forecast: {str(e)}"
        )


@router.post("/shortage-risk", response_model=ShortageRiskResponse)
async def analyze_shortage_risk(
    request: ShortageRiskRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze shortage risk for an inventory item.
    
    This endpoint:
    - Retrieves or generates forecast
    - Calculates days of stock remaining
    - Classifies risk level
    - Estimates shortage quantities
    - Recommends reorder timing
    - Identifies contributing factors
    
    Returns comprehensive risk assessment with actionable recommendations.
    """
    try:
        service = ForecastingService(db)
        result = await service.analyze_shortage_risk(
            inventory_item_id=request.inventory_item_id,
            forecast_id=request.forecast_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze shortage risk: {str(e)}"
        )


@router.get("/forecasts", response_model=ForecastListResponse)
async def list_forecasts(
    inventory_item_id: Optional[UUID] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    List recent forecasts.
    
    Returns summary of forecasts with metadata.
    Can filter by inventory item ID.
    """
    try:
        service = ForecastingService(db)
        summaries = await service.get_forecast_summary(
            inventory_item_id=inventory_item_id,
            limit=limit
        )
        
        return ForecastListResponse(
            forecasts=summaries,
            total=len(summaries)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list forecasts: {str(e)}"
        )


@router.get("/forecasts/{forecast_id}")
async def get_forecast_details(
    forecast_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed forecast information.
    
    Returns complete forecast data including all data points,
    model metadata, and risk assessment if available.
    """
    try:
        from sqlalchemy import select
        from sangam_api.models.forecast import Forecast
        
        result = await db.execute(
            select(Forecast).where(Forecast.id == forecast_id)
        )
        forecast = result.scalar_one_or_none()
        
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forecast not found"
            )
        
        # Convert data points to list
        data_points = [
            {
                "date": dp.forecast_date.isoformat(),
                "predicted_demand": dp.predicted_demand,
                "lower_bound": dp.lower_bound,
                "upper_bound": dp.upper_bound
            }
            for dp in forecast.data_points
        ]
        
        return {
            "id": str(forecast.id),
            "inventory_item_id": str(forecast.inventory_item_id),
            "model_type": forecast.model_type,
            "model_version": forecast.model_version,
            "horizon_days": forecast.forecast_horizon_days,
            "confidence_level": forecast.confidence_level,
            "accuracy_score": forecast.accuracy_score,
            "model_metadata": forecast.model_metadata,
            "risk_assessment": forecast.risk_assessment,
            "status": forecast.status,
            "created_at": forecast.created_at.isoformat(),
            "data_points": data_points,
            "data_points_count": len(data_points)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get forecast details: {str(e)}"
        )


@router.get("/models")
async def list_available_models():
    """
    List available forecasting models.
    
    Returns information about available model types,
    their capabilities, and when to use each.
    """
    models = [
        {
            "type": "baseline",
            "name": "Baseline Forecast Model",
            "version": "1.0.0",
            "description": "Weighted moving average baseline model",
            "use_case": "Default model for most forecasting needs. Good balance of simplicity and accuracy.",
            "data_requirements": {
                "min_data_points": 7,
                "min_days": 7,
                "recommended_data_points": 30,
                "recommended_days": 30
            },
            "features": [
                "Weighted moving average",
                "Confidence intervals",
                "Handles missing data",
                "Fast inference"
            ]
        },
        {
            "type": "naive",
            "name": "Naive Forecast Model",
            "version": "1.0.0",
            "description": "Uses last observed value for all predictions",
            "use_case": "Simple baseline for comparison. Use when data is very limited or stable.",
            "data_requirements": {
                "min_data_points": 1,
                "min_days": 1,
                "recommended_data_points": 7,
                "recommended_days": 7
            },
            "features": [
                "Extremely simple",
                "No training required",
                "Fast inference",
                "Good for stable demand"
            ]
        }
    ]
    
    return {
        "models": models,
        "total": len(models),
        "note": "All models use synthetic data for demonstration. Real-world performance may vary."
    }

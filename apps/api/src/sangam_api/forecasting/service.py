"""
Forecasting Service
Orchestrates forecasting operations and shortage risk analysis.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import pandas as pd
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sangam_api.forecasting.models import ForecastModel, BaselineForecastModel
from sangam_api.forecasting.preprocessing import DataPreprocessor
from sangam_api.forecasting.shortage_risk import ShortageRiskAnalyzer
from sangam_api.models.forecast import Forecast, ForecastDataPoint
from sangam_api.models.inventory import InventoryItem
from sangam_api.models.shipment import Shipment
from sangam_api.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class ForecastingService:
    """
    Service for forecasting and shortage risk analysis.
    
    Orchestrates:
    - Data retrieval and preprocessing
    - Model training and prediction
    - Shortage risk assessment
    - Result persistence
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.preprocessor = DataPreprocessor()
        self.risk_analyzer = ShortageRiskAnalyzer()
        
    async def generate_forecast(
        self,
        inventory_item_id: UUID,
        horizon_days: int = 30,
        model_type: str = "baseline",
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Generate demand forecast for an inventory item.
        
        Args:
            inventory_item_id: ID of inventory item to forecast
            horizon_days: Number of days to forecast
            model_type: Type of model to use ('baseline', 'naive')
            confidence_level: Confidence level for intervals
            
        Returns:
            Forecast results with metadata
        """
        logger.info(f"Generating forecast for item {inventory_item_id}, horizon={horizon_days}d")
        
        # Retrieve inventory item
        item = await self._get_inventory_item(inventory_item_id)
        
        # Retrieve historical consumption data
        historical_data = await self._get_historical_consumption(inventory_item_id)
        
        # Check data sufficiency
        sufficiency = self.preprocessor.check_data_sufficiency(historical_data)
        
        if not sufficiency['sufficient']:
            logger.warning(f"Insufficient data: {sufficiency['reason']}")
            return {
                'status': 'insufficient_data',
                'message': sufficiency['reason'],
                'data_assessment': sufficiency,
                'inventory_item_id': str(inventory_item_id)
            }
        
        # Preprocess data
        cleaned_data = self.preprocessor.clean_consumption_data(historical_data)
        
        # Select and fit model
        model = self._get_model(model_type)
        model_info = model.fit(cleaned_data)
        
        # Generate predictions
        forecast_df = model.predict(horizon_days)
        
        # Evaluate model if test data available
        evaluation_metrics = None
        if len(cleaned_data) >= 30:
            train_data, test_data = self.preprocessor.split_train_test(cleaned_data, test_size=0.2)
            model.fit(train_data)
            evaluation_metrics = model.evaluate(test_data)
        
        # Save forecast to database
        forecast_record = await self._save_forecast(
            inventory_item_id=inventory_item_id,
            model_type=model_type,
            model_version=model_info.get('version', '1.0.0'),
            horizon_days=horizon_days,
            confidence_level=confidence_level,
            forecast_data=forecast_df,
            model_metadata=model_info,
            evaluation_metrics=evaluation_metrics
        )
        
        # Prepare response
        result = {
            'status': 'success',
            'forecast_id': str(forecast_record.id),
            'inventory_item_id': str(inventory_item_id),
            'model_info': model_info,
            'forecast_data': forecast_df.to_dict('records'),
            'evaluation_metrics': evaluation_metrics,
            'data_assessment': sufficiency,
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Forecast generated successfully: {forecast_record.id}")
        
        return result
    
    async def analyze_shortage_risk(
        self,
        inventory_item_id: UUID,
        forecast_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Analyze shortage risk for an inventory item.
        
        Args:
            inventory_item_id: ID of inventory item
            forecast_id: Optional specific forecast to use (uses latest if None)
            
        Returns:
            Comprehensive risk assessment
        """
        logger.info(f"Analyzing shortage risk for item {inventory_item_id}")
        
        # Retrieve inventory item
        item = await self._get_inventory_item(inventory_item_id)
        
        # Get or generate forecast
        if forecast_id:
            forecast = await self._get_forecast(forecast_id)
        else:
            forecast = await self._get_latest_forecast(inventory_item_id)
        
        if not forecast:
            # Generate forecast if none exists
            logger.info("No forecast found, generating new forecast")
            forecast_result = await self.generate_forecast(inventory_item_id)
            
            if forecast_result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': 'Cannot analyze risk without forecast',
                    'forecast_error': forecast_result
                }
            
            forecast_id = UUID(forecast_result['forecast_id'])
            forecast = await self._get_forecast(forecast_id)
        
        # Convert forecast data to DataFrame
        forecast_data = pd.DataFrame([
            {
                'date': dp.forecast_date,
                'predicted_demand': dp.predicted_demand,
                'lower_bound': dp.lower_bound,
                'upper_bound': dp.upper_bound
            }
            for dp in forecast.data_points
        ])
        
        # Get historical data
        historical_data = await self._get_historical_consumption(inventory_item_id)
        
        # Get incoming shipments
        incoming_shipments = await self._get_incoming_shipments(inventory_item_id)
        
        # Calculate current stock
        current_stock = item.quantity_on_hand - item.quantity_reserved
        
        # Generate risk assessment
        risk_assessment = self.risk_analyzer.generate_risk_assessment(
            current_stock=current_stock,
            forecast_data=forecast_data,
            historical_data=historical_data if len(historical_data) > 0 else None,
            incoming_shipments=incoming_shipments if len(incoming_shipments) > 0 else None
        )
        
        # Save risk assessment to forecast record
        forecast.risk_assessment = str(risk_assessment)  # Store as JSON string
        await self.db.commit()
        
        result = {
            'status': 'success',
            'inventory_item_id': str(inventory_item_id),
            'forecast_id': str(forecast.id),
            'risk_assessment': risk_assessment,
            'current_stock': current_stock,
            'analyzed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Risk assessment complete. Risk level: {risk_assessment['risk_level']}")
        
        return result
    
    async def get_forecast_summary(
        self,
        inventory_item_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get summary of recent forecasts.
        
        Args:
            inventory_item_id: Optional filter by item
            limit: Maximum number of forecasts to return
            
        Returns:
            List of forecast summaries
        """
        query = select(Forecast).order_by(Forecast.created_at.desc())
        
        if inventory_item_id:
            query = query.where(Forecast.inventory_item_id == inventory_item_id)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        forecasts = result.scalars().all()
        
        summaries = []
        for forecast in forecasts:
            summary = {
                'id': str(forecast.id),
                'inventory_item_id': str(forecast.inventory_item_id),
                'model_type': forecast.model_type,
                'model_version': forecast.model_version,
                'horizon_days': forecast.horizon_days,
                'confidence_level': forecast.confidence_level,
                'accuracy_score': forecast.accuracy_score,
                'status': forecast.status,
                'created_at': forecast.created_at.isoformat(),
                'data_points_count': len(forecast.data_points)
            }
            summaries.append(summary)
        
        return summaries
    
    async def _get_inventory_item(self, item_id: UUID) -> InventoryItem:
        """Retrieve inventory item by ID."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundException("Inventory item", str(item_id))
        
        return item
    
    async def _get_historical_consumption(self, item_id: UUID, days: int = 90) -> pd.DataFrame:
        """
        Retrieve historical consumption data for an item.
        
        For demonstration, generates synthetic data if no real data exists.
        """
        # In production, this would query actual consumption records
        # For now, generate synthetic data
        
        logger.info(f"Retrieving historical consumption for item {item_id}")
        
        # Generate synthetic historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic consumption pattern
        base_demand = 50  # Base daily demand
        trend = 0.1  # Slight upward trend
        seasonality = 10  # Seasonal variation
        noise = 5  # Random noise
        
        consumption = []
        for i, date in enumerate(dates):
            # Trend component
            trend_component = trend * i
            
            # Seasonal component (weekly pattern)
            seasonal_component = seasonality * (0.5 if date.dayofweek < 5 else -0.3)
            
            # Random noise
            noise_component = (hash(str(date)) % 100 - 50) / 10 * noise
            
            # Total consumption
            daily_consumption = max(0, base_demand + trend_component + seasonal_component + noise_component)
            consumption.append(daily_consumption)
        
        historical_df = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        logger.info(f"Generated {len(historical_df)} days of synthetic consumption data")
        
        return historical_df
    
    async def _get_incoming_shipments(self, item_id: UUID) -> pd.DataFrame:
        """
        Retrieve incoming shipments for an item.
        
        For demonstration, generates synthetic data.
        """
        logger.info(f"Retrieving incoming shipments for item {item_id}")
        
        # Generate synthetic incoming shipments
        today = datetime.now()
        shipments = []
        
        # Create 2-3 incoming shipments over next 14 days
        for i in range(2):
            shipment_date = today + timedelta(days=5 + i * 7)
            quantity = 200 + (hash(str(shipment_date)) % 100)
            
            shipments.append({
                'date': shipment_date,
                'quantity': quantity
            })
        
        shipments_df = pd.DataFrame(shipments)
        
        logger.info(f"Generated {len(shipments_df)} synthetic incoming shipments")
        
        return shipments_df
    
    def _get_model(self, model_type: str) -> ForecastModel:
        """Get forecasting model instance."""
        if model_type == 'baseline':
            return BaselineForecastModel(window_size=7)
        elif model_type == 'naive':
            from sangam_api.forecasting.models import NaiveForecastModel
            return NaiveForecastModel()
        else:
            raise ValidationException(f"Unknown model type: {model_type}")
    
    async def _get_forecast(self, forecast_id: UUID) -> Forecast:
        """Retrieve forecast by ID."""
        result = await self.db.execute(
            select(Forecast).where(Forecast.id == forecast_id)
        )
        forecast = result.scalar_one_or_none()
        
        if not forecast:
            raise NotFoundException("Forecast", str(forecast_id))
        
        return forecast
    
    async def _get_latest_forecast(self, inventory_item_id: UUID) -> Optional[Forecast]:
        """Retrieve latest forecast for an item."""
        result = await self.db.execute(
            select(Forecast)
            .where(Forecast.inventory_item_id == inventory_item_id)
            .order_by(Forecast.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def _save_forecast(
        self,
        inventory_item_id: UUID,
        model_type: str,
        model_version: str,
        horizon_days: int,
        confidence_level: float,
        forecast_data: pd.DataFrame,
        model_metadata: Dict[str, Any],
        evaluation_metrics: Optional[Dict[str, float]] = None
    ) -> Forecast:
        """Save forecast to database."""
        import json
        
        # Create forecast record
        forecast = Forecast(
            inventory_item_id=inventory_item_id,
            model_type=model_type,
            model_version=model_version,
            forecast_horizon_days=horizon_days,
            confidence_level=confidence_level,
            accuracy_score=evaluation_metrics.get('mae') if evaluation_metrics else None,
            model_metadata=json.dumps(model_metadata),
            status='active'
        )
        
        self.db.add(forecast)
        await self.db.flush()
        
        # Create data points
        for _, row in forecast_data.iterrows():
            data_point = ForecastDataPoint(
                forecast_id=forecast.id,
                forecast_date=row['date'],
                predicted_demand=row['predicted_demand'],
                lower_bound=row['lower_bound'],
                upper_bound=row['upper_bound']
            )
            self.db.add(data_point)
        
        await self.db.commit()
        await self.db.refresh(forecast)
        
        logger.info(f"Saved forecast {forecast.id} with {len(forecast_data)} data points")
        
        return forecast

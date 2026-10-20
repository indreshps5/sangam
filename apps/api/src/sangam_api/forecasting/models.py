"""
Forecast Model Interface and Implementations
Defines the contract for forecasting models and provides baseline implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ForecastModel(ABC):
    """
    Abstract interface for forecasting models.
    
    All forecasting models must implement this interface to ensure
    consistency and allow easy swapping of implementations.
    """
    
    @abstractmethod
    def fit(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train the model on historical data.
        
        Args:
            historical_data: DataFrame with columns:
                - date: datetime
                - consumption: float (units consumed per day)
                - stock_level: float (stock at end of day)
            
        Returns:
            Dictionary containing model metadata and training info
        """
        pass
    
    @abstractmethod
    def predict(self, horizon_days: int) -> pd.DataFrame:
        """
        Generate forecasts for the specified horizon.
        
        Args:
            horizon_days: Number of days to forecast
            
        Returns:
            DataFrame with columns:
                - date: datetime
                - predicted_demand: float
                - lower_bound: float (confidence interval)
                - upper_bound: float (confidence interval)
        """
        pass
    
    @abstractmethod
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model performance on test data.
        
        Args:
            test_data: DataFrame with actual consumption data
            
        Returns:
            Dictionary of evaluation metrics (MAE, RMSE, MAPE, etc.)
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model metadata and configuration.
        
        Returns:
            Dictionary containing model name, version, parameters, etc.
        """
        pass


class BaselineForecastModel(ForecastModel):
    """
    Baseline forecasting model using weighted moving average.
    
    This is a simple, interpretable model that serves as:
    1. A baseline for comparison with more complex models
    2. A fallback when data is insufficient for complex models
    3. A demonstration of the ForecastModel interface
    """
    
    def __init__(self, window_size: int = 7, weights: Optional[List[float]] = None):
        """
        Initialize baseline model.
        
        Args:
            window_size: Number of historical periods to consider
            weights: Optional custom weights (default: linear decay)
        """
        self.window_size = window_size
        self.weights = weights
        self.historical_data: Optional[pd.DataFrame] = None
        self.model_params: Dict[str, Any] = {}
        self.is_fitted = False
        
    def fit(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Fit the baseline model on historical data.
        
        For baseline model, this validates data and stores it.
        """
        logger.info(f"Fitting baseline model with {len(historical_data)} data points")
        
        # Validate input data
        required_columns = ['date', 'consumption']
        missing_cols = [col for col in required_columns if col not in historical_data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Sort by date
        self.historical_data = historical_data.sort_values('date').copy()
        
        # Handle missing values
        if self.historical_data['consumption'].isna().any():
            logger.warning("Found NaN values in consumption data, filling with forward fill")
            self.historical_data['consumption'] = self.historical_data['consumption'].fillna(method='ffill')
            self.historical_data['consumption'] = self.historical_data['consumption'].fillna(0)
        
        # Set default weights if not provided (linear decay)
        if self.weights is None:
            self.weights = np.linspace(1, 0.5, self.window_size).tolist()
            self.weights = [w / sum(self.weights) for w in self.weights]
        
        # Calculate baseline statistics
        recent_data = self.historical_data.tail(self.window_size)
        self.model_params = {
            'mean_consumption': float(self.historical_data['consumption'].mean()),
            'std_consumption': float(self.historical_data['consumption'].std()),
            'recent_mean': float(recent_data['consumption'].mean()),
            'recent_std': float(recent_data['consumption'].std()),
            'data_points': len(self.historical_data),
            'date_range': {
                'start': self.historical_data['date'].min().isoformat(),
                'end': self.historical_data['date'].max().isoformat()
            }
        }
        
        self.is_fitted = True
        logger.info(f"Baseline model fitted. Mean consumption: {self.model_params['mean_consumption']:.2f}")
        
        return {
            'model_name': 'BaselineForecastModel',
            'version': '1.0.0',
            'parameters': self.model_params,
            'status': 'fitted'
        }
    
    def predict(self, horizon_days: int) -> pd.DataFrame:
        """
        Generate forecasts using weighted moving average.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before prediction")
        
        logger.info(f"Generating {horizon_days}-day forecast")
        
        # Get recent data for weighted average
        recent_data = self.historical_data.tail(self.window_size)
        
        # Calculate weighted average
        if len(recent_data) < self.window_size:
            # Adjust weights for available data
            available_weights = self.weights[-len(recent_data):]
            available_weights = [w / sum(available_weights) for w in available_weights]
        else:
            available_weights = self.weights
        
        weighted_avg = sum(
            weight * value 
            for weight, value in zip(available_weights, recent_data['consumption'].values)
        )
        
        # Generate forecast dates
        last_date = self.historical_data['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(horizon_days)]
        
        # Calculate confidence intervals based on historical variance
        std_dev = self.model_params['recent_std']
        if std_dev == 0:
            std_dev = self.model_params['std_consumption']
        
        # Generate predictions with confidence intervals
        predictions = []
        for i, date in enumerate(forecast_dates):
            # Add slight trend component (optional)
            trend_factor = 1.0  # Could be calculated from trend analysis
            
            predicted = weighted_avg * trend_factor
            
            # Confidence intervals widen with horizon
            horizon_factor = 1 + (i / horizon_days) * 0.5
            lower = max(0, predicted - 1.96 * std_dev * horizon_factor)
            upper = predicted + 1.96 * std_dev * horizon_factor
            
            predictions.append({
                'date': date,
                'predicted_demand': float(predicted),
                'lower_bound': float(lower),
                'upper_bound': float(upper)
            })
        
        forecast_df = pd.DataFrame(predictions)
        logger.info(f"Generated forecast with mean demand: {forecast_df['predicted_demand'].mean():.2f}")
        
        return forecast_df
    
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model performance using standard metrics.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before evaluation")
        
        logger.info(f"Evaluating model on {len(test_data)} test data points")
        
        # Validate test data
        if 'date' not in test_data.columns or 'consumption' not in test_data.columns:
            raise ValueError("Test data must contain 'date' and 'consumption' columns")
        
        # Generate predictions for test period
        test_data = test_data.sort_values('date')
        
        # For baseline model, use the same prediction for all test points
        # (In practice, you'd generate predictions for each date)
        recent_data = self.historical_data.tail(self.window_size)
        available_weights = self.weights[-len(recent_data):]
        available_weights = [w / sum(available_weights) for w in available_weights]
        
        weighted_avg = sum(
            weight * value 
            for weight, value in zip(available_weights, recent_data['consumption'].values)
        )
        
        predictions = np.full(len(test_data), weighted_avg)
        actuals = test_data['consumption'].values
        
        # Calculate metrics
        mae = float(np.mean(np.abs(actuals - predictions)))
        rmse = float(np.sqrt(np.mean((actuals - predictions) ** 2)))
        
        # MAPE (handle zero actuals)
        non_zero_mask = actuals != 0
        if non_zero_mask.any():
            mape = float(np.mean(np.abs((actuals[non_zero_mask] - predictions[non_zero_mask]) / actuals[non_zero_mask])) * 100)
        else:
            mape = float('inf')
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'test_samples': len(test_data),
            'mean_actual': float(np.mean(actuals)),
            'mean_predicted': float(np.mean(predictions))
        }
        
        logger.info(f"Evaluation complete. MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%")
        
        return metrics
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model metadata.
        """
        return {
            'model_name': 'BaselineForecastModel',
            'version': '1.0.0',
            'type': 'weighted_moving_average',
            'parameters': {
                'window_size': self.window_size,
                'weights': self.weights
            },
            'training_info': self.model_params if self.is_fitted else None,
            'is_fitted': self.is_fitted,
            'description': 'Simple weighted moving average baseline model'
        }


class NaiveForecastModel(ForecastModel):
    """
    Naive forecasting model - uses last observed value.
    
    Useful as a simple baseline and for testing.
    """
    
    def __init__(self):
        self.last_value: Optional[float] = None
        self.historical_data: Optional[pd.DataFrame] = None
        self.is_fitted = False
        
    def fit(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Store the last observed value."""
        if 'consumption' not in historical_data.columns:
            raise ValueError("Data must contain 'consumption' column")
        
        self.historical_data = historical_data.sort_values('date').copy()
        self.last_value = float(self.historical_data['consumption'].iloc[-1])
        self.is_fitted = True
        
        return {
            'model_name': 'NaiveForecastModel',
            'version': '1.0.0',
            'last_value': self.last_value,
            'status': 'fitted'
        }
    
    def predict(self, horizon_days: int) -> pd.DataFrame:
        """Predict using last observed value."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before prediction")
        
        last_date = self.historical_data['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(horizon_days)]
        
        predictions = [{
            'date': date,
            'predicted_demand': self.last_value,
            'lower_bound': self.last_value * 0.8,
            'upper_bound': self.last_value * 1.2
        } for date in forecast_dates]
        
        return pd.DataFrame(predictions)
    
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """Evaluate using last value for all predictions."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before evaluation")
        
        predictions = np.full(len(test_data), self.last_value)
        actuals = test_data['consumption'].values
        
        mae = float(np.mean(np.abs(actuals - predictions)))
        rmse = float(np.sqrt(np.mean((actuals - predictions) ** 2)))
        
        return {
            'mae': mae,
            'rmse': rmse,
            'test_samples': len(test_data)
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata."""
        return {
            'model_name': 'NaiveForecastModel',
            'version': '1.0.0',
            'type': 'naive',
            'last_value': self.last_value,
            'is_fitted': self.is_fitted
        }

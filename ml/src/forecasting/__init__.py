"""
Demand forecasting module.
Provides unified interface for multiple forecasting models.
"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class ForecastingModel(ABC):
    """Abstract base class for all forecasting models."""

    @abstractmethod
    def fit(self, data: pd.DataFrame, target_column: str) -> None:
        """Train the model on historical data."""
        ...

    @abstractmethod
    def predict(self, horizon: int) -> pd.DataFrame:
        """Generate predictions for the given horizon (in days)."""
        ...

    @abstractmethod
    def evaluate(self, test_data: pd.DataFrame) -> dict:
        """Evaluate model performance on test data."""
        ...


class DemandForecaster:
    """
    Unified forecasting interface.
    Delegates to specific model implementations.
    """

    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self._model: Optional[ForecastingModel] = None
        self._is_fitted = False

    def fit(self, historical_data: pd.DataFrame, target_column: str = "demand") -> None:
        """Fit the forecasting model on historical data."""
        # TODO: Implement model selection and training
        self._is_fitted = True

    def predict(self, horizon_days: int = 30) -> pd.DataFrame:
        """Generate demand predictions."""
        if not self._is_fitted:
            raise RuntimeError("Model must be fitted before prediction")

        # TODO: Implement actual prediction
        dates = pd.date_range(
            start=datetime.now(),
            periods=horizon_days,
            freq="D"
        )
        return pd.DataFrame({
            "date": dates,
            "predicted_demand": np.random.normal(100, 20, horizon_days),
            "lower_bound": np.random.normal(80, 15, horizon_days),
            "upper_bound": np.random.normal(120, 15, horizon_days),
        })

    def get_metrics(self) -> dict:
        """Return model performance metrics."""
        # TODO: Implement actual metrics
        return {
            "mape": 0.0,
            "rmse": 0.0,
            "mae": 0.0,
            "model_type": self.model_type,
        }

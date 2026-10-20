"""
Model evaluation utilities.
Provides standardized metrics for comparing forecasting models.
"""

from typing import Dict
import numpy as np
import pandas as pd


def calculate_mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean Absolute Percentage Error."""
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100


def calculate_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Root Mean Squared Error."""
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    return np.sqrt(np.mean((actual - predicted) ** 2))


def calculate_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean Absolute Error."""
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    return np.mean(np.abs(actual - predicted))


def evaluate_forecast(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> Dict[str, float]:
    """
    Comprehensive forecast evaluation.
    Returns multiple metrics for model comparison.
    """
    return {
        "mape": calculate_mape(actual, predicted),
        "rmse": calculate_rmse(actual, predicted),
        "mae": calculate_mae(actual, predicted),
    }

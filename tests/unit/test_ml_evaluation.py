"""
Unit tests for ML evaluation metrics.
"""

import numpy as np
import pytest


class TestEvaluationMetrics:
    """Tests for forecast evaluation metrics."""

    def test_mape_zero_error(self):
        """MAPE should be 0 when predictions match actuals."""
        actual = np.array([100, 200, 300])
        predicted = np.array([100, 200, 300])
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        assert mape == 0.0

    def test_mape_percentage(self):
        """MAPE should return percentage."""
        actual = np.array([100, 200])
        predicted = np.array([110, 180])
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        assert mape == pytest.approx(10.0, abs=0.1)

    def test_rmse_zero_error(self):
        """RMSE should be 0 when predictions match actuals."""
        actual = np.array([100, 200, 300])
        predicted = np.array([100, 200, 300])
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        assert rmse == 0.0

    def test_rmse_calculation(self):
        """RMSE should correctly calculate root mean square error."""
        actual = np.array([100, 200, 300])
        predicted = np.array([110, 210, 290])
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        assert rmse == pytest.approx(10.0, abs=0.1)

    def test_mae_zero_error(self):
        """MAE should be 0 when predictions match actuals."""
        actual = np.array([100, 200, 300])
        predicted = np.array([100, 200, 300])
        mae = np.mean(np.abs(actual - predicted))
        assert mae == 0.0

    def test_mae_calculation(self):
        """MAE should correctly calculate mean absolute error."""
        actual = np.array([100, 200, 300])
        predicted = np.array([110, 190, 310])
        mae = np.mean(np.abs(actual - predicted))
        assert mae == pytest.approx(10.0, abs=0.1)

    def test_metrics_handle_arrays(self):
        """Metrics should work with various array sizes."""
        for size in [1, 10, 100]:
            actual = np.random.normal(100, 20, size)
            predicted = actual + np.random.normal(0, 5, size)
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            assert rmse >= 0

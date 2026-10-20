"""
Tests for forecasting models.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from sangam_api.forecasting.models import (
    ForecastModel,
    BaselineForecastModel,
    NaiveForecastModel
)


class TestBaselineForecastModel:
    """Tests for BaselineForecastModel."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample historical data."""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        consumption = np.random.normal(50, 10, 30)
        consumption = np.maximum(consumption, 0)  # Ensure non-negative
        
        return pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
    
    @pytest.fixture
    def model(self):
        """Create baseline model instance."""
        return BaselineForecastModel(window_size=7)
    
    def test_fit_success(self, model, sample_data):
        """Test successful model fitting."""
        result = model.fit(sample_data)
        
        assert result['model_name'] == 'BaselineForecastModel'
        assert result['status'] == 'fitted'
        assert 'parameters' in result
        assert model.is_fitted
    
    def test_fit_missing_columns(self, model):
        """Test fitting with missing required columns."""
        bad_data = pd.DataFrame({'date': [datetime.now()]})
        
        with pytest.raises(ValueError, match="Missing required columns"):
            model.fit(bad_data)
    
    def test_fit_handles_nan(self, model):
        """Test that fitting handles NaN values."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [50.0, np.nan, 60.0, np.nan, 55.0, 45.0, 50.0, 60.0, 55.0, 50.0]
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        result = model.fit(data)
        assert result['status'] == 'fitted'
        assert model.is_fitted
    
    def test_predict_before_fit(self, model):
        """Test prediction before fitting raises error."""
        with pytest.raises(RuntimeError, match="Model must be fitted"):
            model.predict(7)
    
    def test_predict_success(self, model, sample_data):
        """Test successful prediction."""
        model.fit(sample_data)
        forecast = model.predict(7)
        
        assert len(forecast) == 7
        assert 'date' in forecast.columns
        assert 'predicted_demand' in forecast.columns
        assert 'lower_bound' in forecast.columns
        assert 'upper_bound' in forecast.columns
        
        # Check predictions are non-negative
        assert (forecast['predicted_demand'] >= 0).all()
        
        # Check confidence intervals are valid
        assert (forecast['lower_bound'] <= forecast['predicted_demand']).all()
        assert (forecast['upper_bound'] >= forecast['predicted_demand']).all()
    
    def test_predict_different_horizons(self, model, sample_data):
        """Test prediction with different horizons."""
        model.fit(sample_data)
        
        for horizon in [1, 7, 14, 30]:
            forecast = model.predict(horizon)
            assert len(forecast) == horizon
    
    def test_evaluate_before_fit(self, model, sample_data):
        """Test evaluation before fitting raises error."""
        with pytest.raises(RuntimeError, match="Model must be fitted"):
            model.evaluate(sample_data)
    
    def test_evaluate_success(self, model, sample_data):
        """Test successful model evaluation."""
        # Split data
        train_data = sample_data.iloc[:20]
        test_data = sample_data.iloc[20:]
        
        model.fit(train_data)
        metrics = model.evaluate(test_data)
        
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert 'test_samples' in metrics
        assert metrics['test_samples'] == len(test_data)
        assert metrics['mae'] >= 0
        assert metrics['rmse'] >= 0
    
    def test_get_model_info(self, model, sample_data):
        """Test getting model information."""
        info = model.get_model_info()
        
        assert info['model_name'] == 'BaselineForecastModel'
        assert info['version'] == '1.0.0'
        assert info['is_fitted'] is False
        
        model.fit(sample_data)
        info = model.get_model_info()
        
        assert info['is_fitted'] is True
        assert info['training_info'] is not None
    
    def test_custom_weights(self, sample_data):
        """Test model with custom weights."""
        custom_weights = [0.5, 0.3, 0.2]
        model = BaselineForecastModel(window_size=3, weights=custom_weights)
        
        model.fit(sample_data)
        forecast = model.predict(7)
        
        assert len(forecast) == 7
    
    def test_zero_consumption(self):
        """Test model with zero consumption data."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [0.0] * 10
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        model = BaselineForecastModel(window_size=7)
        model.fit(data)
        forecast = model.predict(7)
        
        # Should predict zero or near-zero
        assert forecast['predicted_demand'].mean() < 1.0


class TestNaiveForecastModel:
    """Tests for NaiveForecastModel."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample historical data."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [50.0, 55.0, 60.0, 58.0, 62.0, 65.0, 63.0, 67.0, 70.0, 72.0]
        
        return pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
    
    @pytest.fixture
    def model(self):
        """Create naive model instance."""
        return NaiveForecastModel()
    
    def test_fit_success(self, model, sample_data):
        """Test successful model fitting."""
        result = model.fit(sample_data)
        
        assert result['model_name'] == 'NaiveForecastModel'
        assert result['status'] == 'fitted'
        assert result['last_value'] == 72.0  # Last value
        assert model.is_fitted
    
    def test_fit_missing_column(self, model):
        """Test fitting with missing consumption column."""
        bad_data = pd.DataFrame({'date': [datetime.now()]})
        
        with pytest.raises(ValueError, match="must contain 'consumption'"):
            model.fit(bad_data)
    
    def test_predict_before_fit(self, model):
        """Test prediction before fitting raises error."""
        with pytest.raises(RuntimeError, match="Model must be fitted"):
            model.predict(7)
    
    def test_predict_uses_last_value(self, model, sample_data):
        """Test that prediction uses last observed value."""
        model.fit(sample_data)
        forecast = model.predict(5)
        
        # All predictions should be the last value
        assert (forecast['predicted_demand'] == 72.0).all()
    
    def test_predict_confidence_intervals(self, model, sample_data):
        """Test confidence intervals in prediction."""
        model.fit(sample_data)
        forecast = model.predict(5)
        
        # Check intervals are 80% to 120% of last value
        assert (forecast['lower_bound'] == 72.0 * 0.8).all()
        assert (forecast['upper_bound'] == 72.0 * 1.2).all()
    
    def test_evaluate_success(self, model, sample_data):
        """Test successful model evaluation."""
        train_data = sample_data.iloc[:7]
        test_data = sample_data.iloc[7:]
        
        model.fit(train_data)
        metrics = model.evaluate(test_data)
        
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert metrics['test_samples'] == len(test_data)
    
    def test_get_model_info(self, model, sample_data):
        """Test getting model information."""
        model.fit(sample_data)
        info = model.get_model_info()
        
        assert info['model_name'] == 'NaiveForecastModel'
        assert info['type'] == 'naive'
        assert info['last_value'] == 72.0
        assert info['is_fitted'] is True


class TestForecastModelInterface:
    """Tests for ForecastModel interface compliance."""
    
    def test_baseline_implements_interface(self):
        """Test that BaselineForecastModel implements ForecastModel."""
        model = BaselineForecastModel()
        assert isinstance(model, ForecastModel)
        
        # Check all required methods exist
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
        assert hasattr(model, 'evaluate')
        assert hasattr(model, 'get_model_info')
    
    def test_naive_implements_interface(self):
        """Test that NaiveForecastModel implements ForecastModel."""
        model = NaiveForecastModel()
        assert isinstance(model, ForecastModel)
        
        # Check all required methods exist
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
        assert hasattr(model, 'evaluate')
        assert hasattr(model, 'get_model_info')
    
    def test_models_are_interchangeable(self):
        """Test that different models can be used interchangeably."""
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        consumption = np.random.normal(50, 10, 20)
        consumption = np.maximum(consumption, 0)
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        models = [
            BaselineForecastModel(window_size=7),
            NaiveForecastModel()
        ]
        
        for model in models:
            # All models should work the same way
            model.fit(data)
            forecast = model.predict(7)
            assert len(forecast) == 7
            
            metrics = model.evaluate(data.iloc[-5:])
            assert 'mae' in metrics
            
            info = model.get_model_info()
            assert 'model_name' in info

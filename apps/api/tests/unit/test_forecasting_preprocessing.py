"""
Tests for data preprocessing.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from sangam_api.forecasting.preprocessing import DataPreprocessor


class TestDataPreprocessor:
    """Tests for DataPreprocessor."""
    
    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance."""
        return DataPreprocessor()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample consumption data."""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        consumption = np.random.normal(50, 10, 30)
        consumption = np.maximum(consumption, 0)
        
        return pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
    
    def test_validate_consumption_data_success(self, preprocessor, sample_data):
        """Test validation of valid data."""
        is_valid, error = preprocessor.validate_consumption_data(sample_data)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_missing_columns(self, preprocessor):
        """Test validation with missing columns."""
        bad_data = pd.DataFrame({'date': [datetime.now()]})
        
        is_valid, error = preprocessor.validate_consumption_data(bad_data)
        
        assert is_valid is False
        assert "Missing required columns" in error
    
    def test_validate_insufficient_data(self, preprocessor):
        """Test validation with insufficient data points."""
        dates = pd.date_range(start='2024-01-01', periods=2, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'consumption': [50.0, 60.0]
        })
        
        is_valid, error = preprocessor.validate_consumption_data(data)
        
        assert is_valid is False
        assert "Insufficient data points" in error
    
    def test_clean_consumption_data_ffill(self, preprocessor):
        """Test cleaning with forward fill."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [50.0, np.nan, np.nan, 60.0, np.nan, 55.0, 45.0, 50.0, 60.0, 55.0]
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data, fill_method='ffill')
        
        # Check no NaN values
        assert not cleaned['consumption'].isna().any()
        
        # Check forward fill worked
        assert cleaned['consumption'].iloc[1] == 50.0
        assert cleaned['consumption'].iloc[2] == 50.0
    
    def test_clean_consumption_data_mean(self, preprocessor):
        """Test cleaning with mean fill."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [50.0, np.nan, 60.0, np.nan, 55.0, 45.0, 50.0, 60.0, 55.0, 50.0]
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data, fill_method='mean')
        
        # Check no NaN values
        assert not cleaned['consumption'].isna().any()
    
    def test_clean_consumption_data_negative_values(self, preprocessor):
        """Test cleaning handles negative values."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [50.0, -10.0, 60.0, -5.0, 55.0, 45.0, 50.0, 60.0, 55.0, 50.0]
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data)
        
        # Check no negative values
        assert (cleaned['consumption'] >= 0).all()
    
    def test_clean_consumption_data_outliers(self, preprocessor):
        """Test cleaning handles outliers."""
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        consumption = [50.0] * 19 + [500.0]  # One extreme outlier
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data, remove_outliers=True)
        
        # Outlier should be capped
        assert cleaned['consumption'].iloc[-1] < 500.0
    
    def test_generate_features(self, preprocessor, sample_data):
        """Test feature generation."""
        features = preprocessor.generate_features(sample_data)
        
        # Check time-based features
        assert 'day_of_week' in features.columns
        assert 'day_of_month' in features.columns
        assert 'month' in features.columns
        assert 'is_weekend' in features.columns
        
        # Check lag features
        assert 'lag_1' in features.columns
        assert 'lag_7' in features.columns
        
        # Check rolling features
        assert 'rolling_mean_7' in features.columns
        assert 'rolling_std_7' in features.columns
        
        # Check no NaN values
        assert not features.isna().any().any()
    
    def test_split_train_test(self, preprocessor, sample_data):
        """Test train/test split."""
        train, test = preprocessor.split_train_test(sample_data, test_size=0.2)
        
        # Check sizes
        assert len(train) == 24  # 80% of 30
        assert len(test) == 6    # 20% of 30
        
        # Check no overlap
        assert train['date'].max() < test['date'].min()
    
    def test_split_train_test_custom_size(self, preprocessor, sample_data):
        """Test train/test split with custom size."""
        train, test = preprocessor.split_train_test(sample_data, test_size=0.3)
        
        assert len(train) == 21  # 70% of 30
        assert len(test) == 9    # 30% of 30
    
    def test_check_data_sufficiency_sufficient(self, preprocessor, sample_data):
        """Test sufficiency check with sufficient data."""
        result = preprocessor.check_data_sufficiency(sample_data)
        
        assert result['sufficient'] is True
        assert result['data_points'] == 30
        assert result['days_covered'] == 29
    
    def test_check_data_sufficiency_insufficient_points(self, preprocessor):
        """Test sufficiency check with insufficient data points."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'consumption': [50.0] * 10
        })
        
        result = preprocessor.check_data_sufficiency(data, min_data_points=20)
        
        assert result['sufficient'] is False
        assert 'Insufficient data points' in result['reason']
    
    def test_check_data_sufficiency_insufficient_days(self, preprocessor):
        """Test sufficiency check with insufficient time coverage."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'consumption': [50.0] * 10
        })
        
        result = preprocessor.check_data_sufficiency(data, min_days=30)
        
        assert result['sufficient'] is False
        assert 'Insufficient time coverage' in result['reason']
    
    def test_check_data_sufficiency_empty_data(self, preprocessor):
        """Test sufficiency check with empty data."""
        data = pd.DataFrame({'date': [], 'consumption': []})
        
        result = preprocessor.check_data_sufficiency(data)
        
        assert result['sufficient'] is False
        assert result['data_points'] == 0
        assert 'No data available' in result['reason']
    
    def test_resample_to_daily(self, preprocessor):
        """Test resampling to daily frequency."""
        # Create hourly data
        dates = pd.date_range(start='2024-01-01', periods=48, freq='H')
        consumption = [10.0] * 48
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        daily = preprocessor.resample_to_daily(data)
        
        # Should have 2 days of data
        assert len(daily) == 2
        
        # Each day should sum to 240 (24 hours * 10)
        assert daily['consumption'].iloc[0] == 240.0
        assert daily['consumption'].iloc[1] == 240.0
    
    def test_resample_fills_missing_dates(self, preprocessor):
        """Test that resampling fills missing dates."""
        # Create data with gaps
        dates = [datetime(2024, 1, 1), datetime(2024, 1, 3), datetime(2024, 1, 5)]
        consumption = [50.0, 60.0, 55.0]
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        daily = preprocessor.resample_to_daily(data)
        
        # Should have 5 days (1st to 5th)
        assert len(daily) == 5
        
        # Missing days should be filled with 0
        assert daily['consumption'].iloc[1] == 0.0  # Jan 2
        assert daily['consumption'].iloc[3] == 0.0  # Jan 4


class TestEdgeCases:
    """Tests for edge cases in preprocessing."""
    
    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance."""
        return DataPreprocessor()
    
    def test_all_zero_consumption(self, preprocessor):
        """Test handling of all zero consumption."""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        consumption = [0.0] * 30
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data)
        
        assert (cleaned['consumption'] == 0.0).all()
    
    def test_single_data_point(self, preprocessor):
        """Test handling of single data point."""
        data = pd.DataFrame({
            'date': [datetime(2024, 1, 1)],
            'consumption': [50.0]
        })
        
        is_valid, error = preprocessor.validate_consumption_data(data)
        
        assert is_valid is False
        assert "Insufficient data points" in error
    
    def test_duplicate_dates(self, preprocessor):
        """Test handling of duplicate dates."""
        dates = [datetime(2024, 1, 1)] * 5
        consumption = [50.0, 60.0, 55.0, 65.0, 70.0]
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data)
        
        # Should keep only last value for each date
        assert len(cleaned) == 1
        assert cleaned['consumption'].iloc[0] == 70.0
    
    def test_very_large_values(self, preprocessor):
        """Test handling of very large consumption values."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [1e6] * 10  # Very large values
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data)
        
        # Should handle large values without error
        assert len(cleaned) == 10
        assert not cleaned['consumption'].isna().any()
    
    def test_mixed_positive_negative(self, preprocessor):
        """Test handling of mixed positive and negative values."""
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        consumption = [50.0, -10.0, 60.0, -20.0, 55.0, -5.0, 50.0, 60.0, -15.0, 55.0]
        
        data = pd.DataFrame({
            'date': dates,
            'consumption': consumption
        })
        
        cleaned = preprocessor.clean_consumption_data(data)
        
        # All negative values should be converted to 0
        assert (cleaned['consumption'] >= 0).all()

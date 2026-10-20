"""
Tests for shortage risk analysis.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from sangam_api.forecasting.shortage_risk import (
    ShortageRiskAnalyzer,
    ShortageRiskLevel
)


class TestShortageRiskAnalyzer:
    """Tests for ShortageRiskAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance with default parameters."""
        return ShortageRiskAnalyzer(
            lead_time_days=7,
            safety_stock_days=3,
            reorder_threshold_days=14
        )
    
    @pytest.fixture
    def sample_forecast(self):
        """Create sample forecast data."""
        dates = [datetime.now() + timedelta(days=i) for i in range(1, 31)]
        predicted_demand = [50.0] * 30
        
        return pd.DataFrame({
            'date': dates,
            'predicted_demand': predicted_demand,
            'lower_bound': [40.0] * 30,
            'upper_bound': [60.0] * 30
        })
    
    def test_calculate_days_of_stock_adequate(self, analyzer, sample_forecast):
        """Test days of stock calculation with adequate stock."""
        current_stock = 1500.0  # 30 days at 50/day
        
        result = analyzer.calculate_days_of_stock(current_stock, sample_forecast)
        
        assert result['days_of_stock'] == 30.0
        assert result['status'] == 'adequate'
        assert result['current_stock'] == 1500.0
    
    def test_calculate_days_of_stock_low(self, analyzer, sample_forecast):
        """Test days of stock calculation with low stock."""
        current_stock = 500.0  # 10 days at 50/day
        
        result = analyzer.calculate_days_of_stock(current_stock, sample_forecast)
        
        assert result['days_of_stock'] == 10.0
        assert result['status'] == 'low'
    
    def test_calculate_days_of_stock_critical(self, analyzer, sample_forecast):
        """Test days of stock calculation with critical stock."""
        current_stock = 100.0  # 2 days at 50/day
        
        result = analyzer.calculate_days_of_stock(current_stock, sample_forecast)
        
        assert result['days_of_stock'] == 2.0
        assert result['status'] == 'critical'
    
    def test_calculate_days_of_stock_depleted(self, analyzer, sample_forecast):
        """Test days of stock calculation with depleted stock."""
        current_stock = 0.0
        
        result = analyzer.calculate_days_of_stock(current_stock, sample_forecast)
        
        assert result['days_of_stock'] == 0
        assert result['status'] == 'depleted'
    
    def test_calculate_days_of_stock_with_incoming(self, analyzer, sample_forecast):
        """Test days of stock calculation with incoming shipments."""
        current_stock = 500.0  # 10 days without incoming
        
        # Add incoming shipments
        incoming = pd.DataFrame({
            'date': [datetime.now() + timedelta(days=5)],
            'quantity': [500.0]  # 10 more days
        })
        
        result = analyzer.calculate_days_of_stock(current_stock, sample_forecast, incoming)
        
        # Should have 20 days total (10 from stock + 10 from incoming)
        assert result['days_of_stock'] == 20.0
        assert result['incoming_shipments_total'] == 500.0
    
    def test_classify_risk_level_critical(self, analyzer):
        """Test risk level classification - critical."""
        assert analyzer.classify_risk_level(0) == ShortageRiskLevel.CRITICAL
        assert analyzer.classify_risk_level(1) == ShortageRiskLevel.CRITICAL
        assert analyzer.classify_risk_level(2.9) == ShortageRiskLevel.CRITICAL
    
    def test_classify_risk_level_high(self, analyzer):
        """Test risk level classification - high."""
        assert analyzer.classify_risk_level(3) == ShortageRiskLevel.HIGH
        assert analyzer.classify_risk_level(5) == ShortageRiskLevel.HIGH
        assert analyzer.classify_risk_level(6.9) == ShortageRiskLevel.HIGH
    
    def test_classify_risk_level_medium(self, analyzer):
        """Test risk level classification - medium."""
        assert analyzer.classify_risk_level(7) == ShortageRiskLevel.MEDIUM
        assert analyzer.classify_risk_level(10) == ShortageRiskLevel.MEDIUM
        assert analyzer.classify_risk_level(13.9) == ShortageRiskLevel.MEDIUM
    
    def test_classify_risk_level_low(self, analyzer):
        """Test risk level classification - low."""
        assert analyzer.classify_risk_level(14) == ShortageRiskLevel.LOW
        assert analyzer.classify_risk_level(20) == ShortageRiskLevel.LOW
        assert analyzer.classify_risk_level(29.9) == ShortageRiskLevel.LOW
    
    def test_classify_risk_level_adequate(self, analyzer):
        """Test risk level classification - adequate."""
        assert analyzer.classify_risk_level(30) == ShortageRiskLevel.ADEQUATE
        assert analyzer.classify_risk_level(60) == ShortageRiskLevel.ADEQUATE
        assert analyzer.classify_risk_level(100) == ShortageRiskLevel.ADEQUATE
    
    def test_estimate_shortage_quantity_no_shortage(self, analyzer, sample_forecast):
        """Test shortage estimation with no shortage."""
        current_stock = 2000.0  # More than 30 days
        
        result = analyzer.estimate_shortage_quantity(
            current_stock, sample_forecast, horizon_days=30
        )
        
        assert result['shortage_quantity'] == 0.0
        assert result['has_shortage'] is False
        assert result['total_demand_forecast'] == 1500.0  # 30 days * 50
    
    def test_estimate_shortage_quantity_with_shortage(self, analyzer, sample_forecast):
        """Test shortage estimation with shortage."""
        current_stock = 500.0  # Only 10 days
        
        result = analyzer.estimate_shortage_quantity(
            current_stock, sample_forecast, horizon_days=30
        )
        
        # Need 1500, have 500, shortage = 1000
        assert result['shortage_quantity'] == 1000.0
        assert result['has_shortage'] is True
    
    def test_estimate_shortage_quantity_with_incoming(self, analyzer, sample_forecast):
        """Test shortage estimation with incoming shipments."""
        current_stock = 500.0
        
        incoming = pd.DataFrame({
            'date': [datetime.now() + timedelta(days=5)],
            'quantity': [600.0]
        })
        
        result = analyzer.estimate_shortage_quantity(
            current_stock, sample_forecast, horizon_days=30, incoming_shipments=incoming
        )
        
        # Need 1500, have 500 + 600 = 1100, shortage = 400
        assert result['shortage_quantity'] == 400.0
    
    def test_recommend_reorder_timing_immediate(self, analyzer):
        """Test reorder recommendation - immediate."""
        days_of_stock = 5.0  # Less than lead time (7)
        
        result = analyzer.recommend_reorder_timing(days_of_stock)
        
        assert result['should_reorder'] is True
        assert result['urgency'] == 'immediate'
        assert result['days_until_reorder'] == 0
    
    def test_recommend_reorder_timing_soon(self, analyzer):
        """Test reorder recommendation - soon."""
        days_of_stock = 10.0  # Less than reorder point (10) but > lead time
        
        result = analyzer.recommend_reorder_timing(days_of_stock)
        
        assert result['should_reorder'] is True
        assert result['urgency'] == 'soon'
        assert result['days_until_reorder'] == 0
    
    def test_recommend_reorder_timing_not_yet(self, analyzer):
        """Test reorder recommendation - not yet."""
        days_of_stock = 20.0  # More than reorder point (10)
        
        result = analyzer.recommend_reorder_timing(days_of_stock)
        
        assert result['should_reorder'] is False
        assert result['urgency'] == 'not_yet'
        assert result['days_until_reorder'] == 10.0  # 20 - 10
    
    def test_analyze_contributing_factors_low_stock(self, analyzer, sample_forecast):
        """Test contributing factors analysis - low stock."""
        current_stock = 100.0  # Very low
        
        factors = analyzer.analyze_contributing_factors(
            current_stock, sample_forecast
        )
        
        # Should identify low stock as a factor
        factor_names = [f['factor'] for f in factors]
        assert 'low_stock_level' in factor_names or 'stock_depleted' in factor_names
    
    def test_analyze_contributing_factors_no_incoming(self, analyzer, sample_forecast):
        """Test contributing factors analysis - no incoming shipments."""
        current_stock = 500.0
        
        factors = analyzer.analyze_contributing_factors(
            current_stock, sample_forecast, incoming_shipments=None
        )
        
        # Should identify no incoming shipments
        factor_names = [f['factor'] for f in factors]
        assert 'no_incoming_shipments' in factor_names
    
    def test_analyze_contributing_factors_increasing_demand(self, analyzer):
        """Test contributing factors analysis - increasing demand."""
        # Create forecast with increasing demand
        dates = [datetime.now() + timedelta(days=i) for i in range(1, 31)]
        predicted_demand = [40.0 + i * 2 for i in range(30)]  # Increasing
        
        forecast = pd.DataFrame({
            'date': dates,
            'predicted_demand': predicted_demand,
            'lower_bound': [d - 10 for d in predicted_demand],
            'upper_bound': [d + 10 for d in predicted_demand]
        })
        
        current_stock = 500.0
        
        factors = analyzer.analyze_contributing_factors(
            current_stock, forecast
        )
        
        # Should identify increasing demand
        factor_names = [f['factor'] for f in factors]
        assert 'increasing_demand' in factor_names
    
    def test_generate_risk_assessment_comprehensive(self, analyzer, sample_forecast):
        """Test comprehensive risk assessment generation."""
        current_stock = 500.0
        
        assessment = analyzer.generate_risk_assessment(
            current_stock=current_stock,
            forecast_data=sample_forecast
        )
        
        # Check all required fields
        assert 'risk_level' in assessment
        assert 'risk_score' in assessment
        assert 'days_of_stock' in assessment
        assert 'shortage_estimate' in assessment
        assert 'reorder_recommendation' in assessment
        assert 'contributing_factors' in assessment
        assert 'summary' in assessment
        assert 'assessment_timestamp' in assessment
        
        # Check risk level is valid
        assert assessment['risk_level'] in ['critical', 'high', 'medium', 'low', 'adequate']
        
        # Check risk score is in range
        assert 0 <= assessment['risk_score'] <= 100
        
        # Check summary is not empty
        assert len(assessment['summary']) > 0
    
    def test_generate_risk_assessment_critical(self, analyzer, sample_forecast):
        """Test risk assessment with critical risk."""
        current_stock = 50.0  # 1 day of stock
        
        assessment = analyzer.generate_risk_assessment(
            current_stock=current_stock,
            forecast_data=sample_forecast
        )
        
        assert assessment['risk_level'] == 'critical'
        assert assessment['risk_score'] >= 80
        assert 'CRITICAL' in assessment['summary']
    
    def test_generate_risk_assessment_adequate(self, analyzer, sample_forecast):
        """Test risk assessment with adequate stock."""
        current_stock = 2000.0  # 40 days of stock
        
        assessment = analyzer.generate_risk_assessment(
            current_stock=current_stock,
            forecast_data=sample_forecast
        )
        
        assert assessment['risk_level'] == 'adequate'
        assert assessment['risk_score'] <= 30
        assert 'ADEQUATE' in assessment['summary']


class TestShortageRiskLevel:
    """Tests for ShortageRiskLevel enum."""
    
    def test_enum_values(self):
        """Test enum has correct values."""
        assert ShortageRiskLevel.CRITICAL.value == "critical"
        assert ShortageRiskLevel.HIGH.value == "high"
        assert ShortageRiskLevel.MEDIUM.value == "medium"
        assert ShortageRiskLevel.LOW.value == "low"
        assert ShortageRiskLevel.ADEQUATE.value == "adequate"
        assert ShortageRiskLevel.UNKNOWN.value == "unknown"
    
    def test_enum_string_conversion(self):
        """Test enum can be converted to string."""
        assert str(ShortageRiskLevel.CRITICAL) == "ShortageRiskLevel.CRITICAL"
        assert ShortageRiskLevel.CRITICAL.value == "critical"


class TestEdgeCases:
    """Tests for edge cases in shortage risk analysis."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return ShortageRiskAnalyzer()
    
    def test_zero_forecast_demand(self, analyzer):
        """Test with zero forecast demand."""
        dates = [datetime.now() + timedelta(days=i) for i in range(1, 31)]
        forecast = pd.DataFrame({
            'date': dates,
            'predicted_demand': [0.0] * 30,
            'lower_bound': [0.0] * 30,
            'upper_bound': [0.0] * 30
        })
        
        current_stock = 100.0
        
        result = analyzer.calculate_days_of_stock(current_stock, forecast)
        
        # With zero demand, stock should last forever (or very long)
        assert result['days_of_stock'] >= 30.0
    
    def test_very_high_demand(self, analyzer):
        """Test with very high demand."""
        dates = [datetime.now() + timedelta(days=i) for i in range(1, 31)]
        forecast = pd.DataFrame({
            'date': dates,
            'predicted_demand': [1000.0] * 30,
            'lower_bound': [900.0] * 30,
            'upper_bound': [1100.0] * 30
        })
        
        current_stock = 100.0
        
        result = analyzer.calculate_days_of_stock(current_stock, forecast)
        
        # Should deplete in 0.1 days
        assert result['days_of_stock'] < 1.0
        assert result['status'] == 'critical'
    
    def test_empty_forecast(self, analyzer):
        """Test with empty forecast data."""
        forecast = pd.DataFrame({
            'date': [],
            'predicted_demand': [],
            'lower_bound': [],
            'upper_bound': []
        })
        
        current_stock = 100.0
        
        result = analyzer.calculate_days_of_stock(current_stock, forecast)
        
        # With no forecast, should return some default
        assert 'days_of_stock' in result
    
    def test_single_day_forecast(self, analyzer):
        """Test with single day forecast."""
        forecast = pd.DataFrame({
            'date': [datetime.now() + timedelta(days=1)],
            'predicted_demand': [50.0],
            'lower_bound': [40.0],
            'upper_bound': [60.0]
        })
        
        current_stock = 100.0
        
        result = analyzer.calculate_days_of_stock(current_stock, forecast)
        
        # Should handle single day gracefully
        assert result['days_of_stock'] >= 1.0

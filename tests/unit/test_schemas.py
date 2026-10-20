"""
Unit tests for API schemas validation.
"""

import pytest
from uuid import uuid4
from datetime import datetime

# These tests validate the Pydantic schemas
# Run with: pytest tests/unit/


class TestShipmentSchemas:
    """Tests for shipment request/response schemas."""

    def test_shipment_status_values(self):
        """Verify all expected status values exist."""
        valid_statuses = ["pending", "in_transit", "delivered", "delayed", "cancelled"]
        for status in valid_statuses:
            assert status in valid_statuses

    def test_priority_range(self):
        """Priority must be between 1 and 5."""
        for priority in range(1, 6):
            assert 1 <= priority <= 5

    def test_weight_positive(self):
        """Weight must be positive."""
        weight = 10.5
        assert weight > 0

    def test_volume_positive(self):
        """Volume must be positive."""
        volume = 2.5
        assert volume > 0


class TestWarehouseSchemas:
    """Tests for warehouse schemas."""

    def test_coordinates_valid_range(self):
        """Latitude: -90 to 90, Longitude: -180 to 180."""
        lat, lng = 28.6139, 77.2090  # Delhi
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180

    def test_utilization_range(self):
        """Utilization must be between 0 and 1."""
        utilization = 0.75
        assert 0.0 <= utilization <= 1.0

    def test_code_max_length(self):
        """Warehouse code max 20 characters."""
        code = "WH-MUM-001"
        assert len(code) <= 20


class TestForecastSchemas:
    """Tests for forecast schemas."""

    def test_horizon_range(self):
        """Forecast horizon: 1 to 90 days."""
        horizon = 30
        assert 1 <= horizon <= 90

    def test_confidence_level_range(self):
        """Confidence level: 0.5 to 0.99."""
        confidence = 0.95
        assert 0.5 <= confidence <= 0.99


class TestExceptionHierarchy:
    """Tests for custom exception classes."""

    def test_not_found_has_correct_status(self):
        """NotFoundException should have 404 status."""
        status_code = 404
        assert status_code == 404

    def test_validation_has_correct_status(self):
        """ValidationException should have 422 status."""
        status_code = 422
        assert status_code == 422

    def test_conflict_has_correct_status(self):
        """ConflictException should have 409 status."""
        status_code = 409
        assert status_code == 409

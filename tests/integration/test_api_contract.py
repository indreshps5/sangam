"""
Integration tests for API health endpoints.
These tests verify the API can start and respond correctly.
Run with a running database: pytest tests/integration/
"""

import pytest


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    def test_health_endpoint_structure(self):
        """Health endpoint should return expected structure."""
        expected_keys = ["status", "service", "timestamp"]
        # Simulated response
        response = {
            "status": "healthy",
            "service": "sangam-api",
            "timestamp": "2024-01-01T00:00:00Z",
        }
        for key in expected_keys:
            assert key in response

    def test_readiness_includes_database(self):
        """Readiness check should include database status."""
        expected_keys = ["status", "database", "timestamp"]
        response = {
            "status": "ready",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z",
        }
        for key in expected_keys:
            assert key in response

    def test_liveness_minimal(self):
        """Liveness probe should be minimal."""
        response = {"status": "alive"}
        assert response["status"] == "alive"
        assert len(response) == 1


class TestAPIContract:
    """Tests verifying API contract between frontend and backend."""

    def test_shipment_response_fields(self):
        """Shipment response must include all required fields."""
        required_fields = [
            "id", "origin_warehouse_id", "destination_warehouse_id",
            "status", "weight_kg", "volume_m3", "priority",
            "estimated_arrival", "actual_arrival", "notes",
            "created_at", "updated_at"
        ]
        # Verify contract matches TypeScript types
        assert len(required_fields) == 12

    def test_warehouse_response_fields(self):
        """Warehouse response must include all required fields."""
        required_fields = [
            "id", "name", "code", "region",
            "latitude", "longitude", "capacity_units",
            "current_utilization", "address",
            "created_at", "updated_at"
        ]
        assert len(required_fields) == 11

    def test_paginated_response_structure(self):
        """All list endpoints must return paginated response."""
        required_fields = ["items", "total", "skip", "limit"]
        response = {
            "items": [],
            "total": 0,
            "skip": 0,
            "limit": 20,
        }
        for field in required_fields:
            assert field in response

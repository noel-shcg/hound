import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAPI:
    """Tests for API endpoints."""
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hound API", "version": "0.1.0"}
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    def test_unprotected_dashboard_endpoint(self):
        """Test that dashboard endpoint doesn't require authentication."""
        response = client.get("/api/dashboard/summary")
        # Should not return 401
        assert response.status_code != 401
    
    def test_protected_endpoint_without_auth(self):
        """Test that protected endpoints require authentication."""
        response = client.get("/api/settings/")
        assert response.status_code == 401

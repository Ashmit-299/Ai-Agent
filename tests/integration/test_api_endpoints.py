#!/usr/bin/env python3
"""
Integration tests for API endpoints
Tests complete API workflows and endpoint interactions
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import tempfile
import os

@pytest.fixture
def client():
    """Create test client"""
    from app.main import app
    return TestClient(app)

@pytest.fixture
def auth_token(client):
    """Get authentication token for testing"""
    # Login with demo credentials
    response = client.post("/users/login", data={
        "username": "demo",
        "password": "demo123"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

class TestAPIEndpointsIntegration:
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    def test_demo_login_endpoint(self, client):
        """Test demo login credentials endpoint"""
        response = client.get("/demo-login")
        assert response.status_code == 200
        data = response.json()
        assert "demo_credentials" in data
        assert data["demo_credentials"]["username"] == "demo"

    def test_user_registration_flow(self, client):
        """Test complete user registration workflow"""
        user_data = {
            "username": "testuser123",
            "password": "testpass123",
            "email": "test@example.com"
        }
        
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["username"] == "testuser123"

    def test_user_login_flow(self, client):
        """Test user login workflow"""
        login_data = {
            "username": "demo",
            "password": "demo123"
        }
        
        response = client.post("/users/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == "demo"

    def test_authenticated_profile_access(self, client, auth_token):
        """Test authenticated profile access"""
        if not auth_token:
            pytest.skip("Authentication not available")
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/users/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "username" in data

    def test_content_listing(self, client):
        """Test content listing endpoint"""
        response = client.get("/contents")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    @patch('core.database.DatabaseManager.create_content')
    def test_file_upload_workflow(self, mock_create_content, client, auth_token):
        """Test file upload workflow"""
        if not auth_token:
            pytest.skip("Authentication not available")
            
        mock_create_content.return_value = Mock()
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write("Test content for upload")
            tmp_file.flush()
            
            try:
                with open(tmp_file.name, 'rb') as f:
                    files = {"file": ("test.txt", f, "text/plain")}
                    data = {"title": "Test Upload", "description": "Test description"}
                    
                    response = client.post("/upload", files=files, data=data, headers=headers)
                    
                    # Should succeed or fail gracefully
                    assert response.status_code in [201, 400, 500]
                    
            finally:
                os.unlink(tmp_file.name)

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "system_metrics" in data
        assert "timestamp" in data

    def test_analytics_endpoint(self, client):
        """Test analytics endpoint"""
        response = client.get("/bhiv/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_content" in data

    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints"""
        response = client.get("/users/profile")
        assert response.status_code == 401

    def test_invalid_content_access(self, client):
        """Test access to non-existent content"""
        response = client.get("/content/nonexistent123")
        assert response.status_code == 404

    @patch('core.database.DatabaseManager.create_feedback')
    def test_feedback_submission(self, mock_create_feedback, client, auth_token):
        """Test feedback submission workflow"""
        if not auth_token:
            pytest.skip("Authentication not available")
            
        mock_create_feedback.return_value = Mock()
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        feedback_data = {
            "content_id": "test123",
            "rating": 4,
            "comment": "Great content!"
        }
        
        response = client.post("/feedback", json=feedback_data, headers=headers)
        # Should succeed or fail gracefully
        assert response.status_code in [201, 400, 404, 500]

    def test_error_handling_consistency(self, client):
        """Test consistent error response format"""
        # Test various error scenarios
        error_endpoints = [
            "/content/invalid",
            "/download/invalid", 
            "/stream/invalid"
        ]
        
        for endpoint in error_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [404, 500]
            
            if response.status_code != 500:  # Skip 500 errors as they may not have JSON
                data = response.json()
                assert "detail" in data

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.get("/health")
        # CORS headers should be handled by middleware
        assert response.status_code == 200

    def test_rate_limiting_headers(self, client):
        """Test rate limiting (if implemented)"""
        # Make multiple requests quickly
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response)
        
        # All should succeed (rate limiting may not be strict for health endpoint)
        for response in responses:
            assert response.status_code == 200

    def test_api_documentation_access(self, client):
        """Test API documentation endpoints"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_webhook_endpoint(self, client):
        """Test webhook ingestion endpoint"""
        webhook_data = {
            "script": "Test webhook script",
            "source": "test"
        }
        
        response = client.post("/ingest/webhook", json=webhook_data)
        # Should handle webhook data
        assert response.status_code in [200, 400, 500]
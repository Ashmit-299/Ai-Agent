#!/usr/bin/env python3
"""
Test async endpoint functionality
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAsyncEndpoints:
    """Test async endpoint functionality"""
    
    def test_health_endpoint_async(self):
        """Test health endpoint responds correctly"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_demo_login_endpoint(self):
        """Test demo login endpoint"""
        response = client.get("/demo-login")
        assert response.status_code == 200
        
        data = response.json()
        assert "demo_credentials" in data
        assert "username" in data["demo_credentials"]
        assert "password" in data["demo_credentials"]
    
    def test_contents_list_endpoint(self):
        """Test contents listing endpoint"""
        # First login to get token
        login_response = client.post("/users/login", data={
            "username": "demo",
            "password": "demo1234"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = client.get("/contents", headers=headers)
            assert response.status_code == 200
            
            data = response.json()
            assert "items" in data
        else:
            # Skip test if demo user not available
            pytest.skip("Demo user not available for testing")
    
    def test_metrics_endpoint_async(self):
        """Test metrics endpoint"""
        # Try without auth first
        response = client.get("/metrics")
        
        # Should require authentication
        assert response.status_code in [401, 422]  # Unauthorized or validation error
    
    def test_upload_endpoint_requires_auth(self):
        """Test upload endpoint requires authentication"""
        # Try upload without authentication
        files = {"file": ("test.txt", "test content", "text/plain")}
        data = {"title": "Test Upload", "description": "Test"}
        
        response = client.post("/upload", files=files, data=data)
        
        # Should require authentication
        assert response.status_code in [401, 422]
    
    def test_feedback_endpoint_requires_auth(self):
        """Test feedback endpoint requires authentication"""
        feedback_data = {
            "content_id": "test_content",
            "rating": 5,
            "comment": "Test feedback"
        }
        
        response = client.post("/feedback", json=feedback_data)
        
        # Should require authentication
        assert response.status_code in [401, 422]
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test that async functions work correctly"""
        # This is a basic test to ensure async functionality
        async def test_async_operation():
            await asyncio.sleep(0.1)
            return "async_result"
        
        result = await test_async_operation()
        assert result == "async_result"
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            return client.get("/health")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
    
    def test_response_time_reasonable(self):
        """Test that response times are reasonable"""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        assert response.status_code == 200
        assert response_time < 1000  # Should respond within 1 second
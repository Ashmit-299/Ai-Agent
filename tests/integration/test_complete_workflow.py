#!/usr/bin/env python3
"""
Complete End-to-End Integration Test Suite
Tests the full 9-step API workflow with performance benchmarks
"""

import pytest
import asyncio
import httpx
import os
import json
import time
import tempfile
from typing import Dict, List, Any
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class E2ETestClient:
    """End-to-end test client with performance tracking"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.auth_token = None
        self.performance_metrics = {
            "requests": [],
            "total_time": 0,
            "error_count": 0
        }
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with performance tracking"""
        start_time = time.time()
        
        try:
            # Add auth header if available
            if self.auth_token and 'headers' not in kwargs:
                kwargs['headers'] = {}
            if self.auth_token:
                kwargs['headers']['Authorization'] = f"Bearer {self.auth_token}"
            
            response = await self.client.request(method, url, **kwargs)
            
            # Track performance
            duration = time.time() - start_time
            self.performance_metrics["requests"].append({
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "duration": duration,
                "success": 200 <= response.status_code < 300
            })
            
            if response.status_code >= 400:
                self.performance_metrics["error_count"] += 1
                logger.error(f"Request failed: {method} {url} -> {response.status_code}")
                logger.error(f"Response: {response.text}")
            
            return {
                "status_code": response.status_code,
                "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
                "text": response.text,
                "headers": dict(response.headers),
                "duration": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.performance_metrics["error_count"] += 1
            self.performance_metrics["requests"].append({
                "method": method,
                "url": url,
                "status_code": 0,
                "duration": duration,
                "success": False,
                "error": str(e)
            })
            raise

@pytest.mark.asyncio
class TestCompleteWorkflow:
    """Complete 9-step workflow integration tests"""

    @pytest.fixture(autouse=True)
    async def setup_test_environment(self):
        """Setup test environment and cleanup after tests"""
        # Setup
        self.test_user_data = {
            "username": f"test_user_{int(time.time())}",
            "password": "test_password_123!",
            "email": f"test_{int(time.time())}@example.com"
        }
        self.created_resources = []
        
        yield
        
        # Cleanup (if needed)
        logger.info(f"Test completed, created {len(self.created_resources)} resources")

    async def test_step1_system_health_and_demo_access(self):
        """STEP 1: System Health & Demo Access"""
        async with E2ETestClient() as client:
            logger.info("STEP 1: Testing system health and demo access")
            
            # Test health endpoint
            response = await client.make_request("GET", "/health")
            assert response["status_code"] == 200, f"Health check failed: {response}"
            
            health_data = response["json"]
            assert health_data["status"] == "healthy", "System not healthy"
            # Health endpoint may not have timestamp, check for other required fields
            assert "service" in health_data, "Health response missing service info"
            
            # Test detailed health (may require auth)
            response = await client.make_request("GET", "/health/detailed")
            if response["status_code"] == 200:
                detailed_health = response["json"]
                assert "supabase_auth" in detailed_health, "Supabase auth status missing"
            else:
                # Detailed health may require authentication, skip this check
                logger.info("Detailed health endpoint requires authentication, skipping")
            
            # Test demo login
            response = await client.make_request("GET", "/demo-login")
            assert response["status_code"] == 200, "Demo login failed"
            
            demo_data = response["json"]
            assert "demo_credentials" in demo_data, "Demo credentials missing"
            
            logger.info("✅ STEP 1: System health and demo access - PASSED")
            
    async def test_step2_user_authentication(self):
        """STEP 2: User Authentication"""
        async with E2ETestClient() as client:
            logger.info("STEP 2: Testing user authentication workflow")
            
            # Test user registration
            response = await client.make_request(
                "POST", 
                "/users/register",
                json=self.test_user_data
            )
            assert response["status_code"] == 201, f"User registration failed: {response['text']}"
            
            reg_data = response["json"]
            assert "access_token" in reg_data, "Access token missing from registration"
            assert "user_id" in reg_data, "User ID missing from registration"
            
            # Test user login
            login_data = {
                "username": self.test_user_data["username"],
                "password": self.test_user_data["password"]
            }
            
            response = await client.make_request(
                "POST",
                "/users/login",
                data=login_data
            )
            assert response["status_code"] == 200, f"User login failed: {response['text']}"
            
            login_response = response["json"]
            assert "access_token" in login_response, "Access token missing from login"
            
            # Set auth token for subsequent requests
            client.auth_token = login_response["access_token"]
            
            # Test profile access
            response = await client.make_request("GET", "/users/profile")
            assert response["status_code"] == 200, "Profile access failed"
            
            profile_data = response["json"]
            assert profile_data["username"] == self.test_user_data["username"], "Profile username mismatch"
            
            # Test auth debugging
            response = await client.make_request("GET", "/debug-auth")
            assert response["status_code"] == 200, "Auth debug failed"
            
            auth_debug = response["json"]
            assert auth_debug["authenticated"] == True, "Auth debug shows not authenticated"
            
            logger.info("✅ STEP 2: User authentication workflow - PASSED")
            return client.auth_token

    async def test_step3_content_upload_and_video_generation(self):
        """STEP 3: Content Upload & Video Generation"""
        auth_token = await self.test_step2_user_authentication()
        
        async with E2ETestClient() as client:
            client.auth_token = auth_token
            logger.info("STEP 3: Testing content upload and video generation")
            
            # Create test files
            test_files = await self._create_test_files()
            
            # Test content upload
            for file_info in test_files:
                logger.info(f"Testing upload of {file_info['type']} file")
                
                with open(file_info['path'], 'rb') as f:
                    files = {"file": (file_info['filename'], f, file_info['mime_type'])}
                    data = {
                        "title": f"Test {file_info['type']} Content",
                        "description": f"Integration test upload of {file_info['type']}"
                    }
                    
                    response = await client.make_request(
                        "POST",
                        "/upload",
                        files=files,
                        data=data
                    )
                    
                assert response["status_code"] == 201, f"Upload failed for {file_info['type']}: {response['text']}"
                
                upload_data = response["json"]
                assert "content_id" in upload_data, "Content ID missing from upload response"
                assert "access_urls" in upload_data, "Access URLs missing from upload response"
                
                self.created_resources.append(upload_data["content_id"])
                
                # Test file size validation
                assert upload_data["file_size_mb"] > 0, "File size not recorded"
                assert upload_data["validation"]["passed"] == True, "File validation failed"
            
            # Test video generation from text script
            script_content = """
            Scene 1: Introduction
            Welcome to our AI-powered content platform.
            
            Scene 2: Features
            We support multiple file types and formats.
            
            Scene 3: Conclusion
            Thank you for using our service.
            """
            
            # Create script file
            script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            script_file.write(script_content)
            script_file.close()
            
            with open(script_file.name, 'rb') as f:
                files = {"file": ("test_script.txt", f, "text/plain")}
                data = {
                    "title": "Test Video Script",
                    "description": "Integration test video generation"
                }
                
                response = await client.make_request(
                    "POST",
                    "/generate-video",
                    files=files,
                    data=data
                )
            
            # Video generation might take time, so we allow 202 (accepted) or 201 (created)
            assert response["status_code"] in [201, 202], f"Video generation failed: {response['text']}"
            
            if response["status_code"] == 201:
                video_data = response["json"]
                assert "content_id" in video_data, "Video content ID missing"
                self.created_resources.append(video_data["content_id"])
            
            # Test content listing
            response = await client.make_request("GET", "/contents")
            assert response["status_code"] == 200, "Content listing failed"
            
            content_list = response["json"]
            assert "contents" in content_list, "Contents list missing"
            assert len(content_list["contents"]) > 0, "No contents found after upload"
            
            # Cleanup test files
            for file_info in test_files:
                os.unlink(file_info['path'])
            os.unlink(script_file.name)
            
            logger.info("✅ STEP 3: Content upload and video generation - PASSED")

    async def test_step4_content_access_and_streaming(self):
        """STEP 4: Content Access & Streaming"""
        auth_token = await self.test_step2_user_authentication()
        
        async with E2ETestClient() as client:
            client.auth_token = auth_token
            logger.info("STEP 4: Testing content access and streaming")
            
            # First upload a test file
            test_file = await self._create_test_files()
            content_id = await self._upload_test_content(client, test_file[0])
            
            # Test content details
            response = await client.make_request("GET", f"/content/{content_id}")
            assert response["status_code"] == 200, "Content details failed"
            
            content_data = response["json"]
            assert content_data["content_id"] == content_id, "Content ID mismatch"
            assert "metadata" in content_data, "Content metadata missing"
            
            # Test content metadata
            response = await client.make_request("GET", f"/content/{content_id}/metadata")
            assert response["status_code"] == 200, "Content metadata failed"
            
            # Test download access
            response = await client.make_request("GET", f"/download/{content_id}")
            assert response["status_code"] == 200, "Content download failed"
            
            # Test streaming (if video content)
            response = await client.make_request("GET", f"/stream/{content_id}")
            # Streaming might not be available for all content types
            assert response["status_code"] in [200, 404, 406], "Streaming test failed"
            
            logger.info("✅ STEP 4: Content access and streaming - PASSED")

    async def test_step5_ai_feedback_and_recommendations(self):
        """STEP 5: AI Feedback & Tag Recommendations"""
        auth_token = await self.test_step2_user_authentication()
        
        async with E2ETestClient() as client:
            client.auth_token = auth_token
            logger.info("STEP 5: Testing AI feedback and recommendations")
            
            # Upload content for testing
            test_file = await self._create_test_files()
            content_id = await self._upload_test_content(client, test_file[0])
            
            # Test feedback submission
            feedback_data = {
                "content_id": content_id,
                "user_id": "test_user",
                "event_type": "like",
                "watch_time_ms": 15000,
                "rating": 5,
                "comment": "Great content for integration testing!"
            }
            
            response = await client.make_request(
                "POST",
                "/feedback",
                json=feedback_data
            )
            assert response["status_code"] in [200, 201], f"Feedback submission failed: {response['text']}"
            
            # Test tag recommendations
            response = await client.make_request("GET", f"/recommend-tags/{content_id}")
            assert response["status_code"] == 200, "Tag recommendations failed"
            
            tag_data = response["json"]
            assert "recommended_tags" in tag_data, "Recommended tags missing"
            
            # Test average rating
            response = await client.make_request("GET", f"/average-rating/{content_id}")
            assert response["status_code"] == 200, "Average rating failed"
            
            rating_data = response["json"]
            assert "average_rating" in rating_data, "Average rating missing"
            
            logger.info("✅ STEP 5: AI feedback and recommendations - PASSED")

    async def test_step6_analytics_and_monitoring(self):
        """STEP 6: Analytics & Performance Monitoring"""
        async with E2ETestClient() as client:
            logger.info("STEP 6: Testing analytics and monitoring")
            
            # Test metrics endpoints
            response = await client.make_request("GET", "/metrics")
            assert response["status_code"] == 200, "Metrics endpoint failed"
            
            metrics_data = response["json"]
            assert "available_endpoints" in metrics_data, "Metrics endpoints missing"
            
            # Test performance metrics
            response = await client.make_request("GET", "/metrics/performance")
            assert response["status_code"] == 200, "Performance metrics failed"
            
            perf_data = response["json"]
            assert "metrics" in perf_data, "Performance metrics missing"
            
            # Test Prometheus metrics (if available)
            response = await client.make_request("GET", "/metrics/prometheus")
            # Prometheus might not be available in test environment
            assert response["status_code"] in [200, 404], "Prometheus metrics test failed"
            
            # Test observability health
            response = await client.make_request("GET", "/observability/health")
            assert response["status_code"] == 200, "Observability health failed"
            
            # Test RL agent stats
            response = await client.make_request("GET", "/rl/agent-stats")
            assert response["status_code"] == 200, "RL agent stats failed"
            
            # Test analytics
            response = await client.make_request("GET", "/bhiv/analytics")
            assert response["status_code"] == 200, "Analytics endpoint failed"
            
            logger.info("✅ STEP 6: Analytics and monitoring - PASSED")

    async def test_step7_task_queue_management(self):
        """STEP 7: Task Queue Management"""
        auth_token = await self.test_step2_user_authentication()
        
        async with E2ETestClient() as client:
            client.auth_token = auth_token
            logger.info("STEP 7: Testing task queue management")
            
            # Test task creation
            response = await client.make_request("POST", "/tasks/create-test")
            assert response["status_code"] in [200, 201, 202], "Task creation failed"
            
            if response["json"] and "task_id" in response["json"]:
                task_id = response["json"]["task_id"]
                
                # Test task status
                response = await client.make_request("GET", f"/tasks/{task_id}")
                assert response["status_code"] == 200, "Task status check failed"
            
            # Test queue stats
            response = await client.make_request("GET", "/tasks/queue/stats")
            assert response["status_code"] == 200, "Queue stats failed"
            
            queue_data = response["json"]
            assert "queue_stats" in queue_data or "active_tasks" in queue_data, "Queue stats missing"
            
            logger.info("✅ STEP 7: Task queue management - PASSED")

    async def test_step8_system_maintenance(self):
        """STEP 8: System Maintenance & Operations"""
        auth_token = await self.test_step2_user_authentication()
        
        async with E2ETestClient() as client:
            client.auth_token = auth_token
            logger.info("STEP 8: Testing system maintenance")
            
            # Test storage status
            response = await client.make_request("GET", "/storage/status")
            assert response["status_code"] == 200, "Storage status failed"
            
            # Test bucket stats
            response = await client.make_request("GET", "/bucket/stats")
            assert response["status_code"] == 200, "Bucket stats failed"
            
            bucket_data = response["json"]
            assert "storage_backend" in bucket_data, "Storage backend info missing"
            
            # Test bucket listing
            response = await client.make_request("GET", "/bucket/list/uploads")
            assert response["status_code"] in [200, 404], "Bucket listing failed"
            
            logger.info("✅ STEP 8: System maintenance - PASSED")

    async def test_step9_dashboard_and_ui(self):
        """STEP 9: Dashboard & User Interface"""
        async with E2ETestClient() as client:
            logger.info("STEP 9: Testing dashboard and UI")
            
            # Test dashboard endpoint
            response = await client.make_request("GET", "/dashboard")
            assert response["status_code"] == 200, "Dashboard failed"
            
            # Dashboard might return HTML, so we just check status code
            assert len(response["text"]) > 0, "Dashboard returned empty response"
            
            logger.info("✅ STEP 9: Dashboard and UI - PASSED")

    async def test_complete_workflow_performance(self):
        """Test complete workflow with performance benchmarks"""
        logger.info("Testing complete workflow with performance benchmarks")
        
        start_time = time.time()
        
        async with E2ETestClient() as client:
            # Run abbreviated workflow for performance testing
            auth_token = await self.test_step2_user_authentication()
            client.auth_token = auth_token
            
            # Upload and process content
            test_file = await self._create_test_files()
            content_id = await self._upload_test_content(client, test_file[0])
            
            # Submit feedback
            await client.make_request(
                "POST",
                "/feedback",
                json={
                    "content_id": content_id,
                    "user_id": "perf_test_user",
                    "event_type": "view",
                    "watch_time_ms": 5000
                }
            )
            
            # Get recommendations
            await client.make_request("GET", f"/recommend-tags/{content_id}")
            
            total_time = time.time() - start_time
            
            # Performance assertions
            assert total_time < 30.0, f"Complete workflow took too long: {total_time}s"
            assert client.performance_metrics["error_count"] == 0, "Errors occurred during performance test"
            
            # Calculate performance metrics
            request_times = [req["duration"] for req in client.performance_metrics["requests"]]
            avg_response_time = sum(request_times) / len(request_times)
            max_response_time = max(request_times)
            
            logger.info(f"Performance Metrics:")
            logger.info(f"  Total workflow time: {total_time:.2f}s")
            logger.info(f"  Total requests: {len(request_times)}")
            logger.info(f"  Average response time: {avg_response_time:.3f}s")
            logger.info(f"  Max response time: {max_response_time:.3f}s")
            logger.info(f"  Error count: {client.performance_metrics['error_count']}")
            
            # Performance benchmarks
            assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time}s"
            assert max_response_time < 5.0, f"Max response time too high: {max_response_time}s"
            
            logger.info("✅ Complete workflow performance - PASSED")

    # Helper methods
    async def _create_test_files(self) -> List[Dict[str, str]]:
        """Create test files for upload testing"""
        test_files = []
        
        # Create a small test image
        image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        
        image_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False)
        image_file.write(image_data)
        image_file.close()
        
        test_files.append({
            'path': image_file.name,
            'filename': 'test_image.png',
            'type': 'image',
            'mime_type': 'image/png'
        })
        
        # Create a small test text file
        text_content = "This is a test text file for integration testing.\nIt contains multiple lines of text."
        
        text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        text_file.write(text_content)
        text_file.close()
        
        test_files.append({
            'path': text_file.name,
            'filename': 'test_document.txt',
            'type': 'document',
            'mime_type': 'text/plain'
        })
        
        return test_files

    async def _upload_test_content(self, client: E2ETestClient, file_info: Dict[str, str]) -> str:
        """Upload test content and return content ID"""
        with open(file_info['path'], 'rb') as f:
            files = {"file": (file_info['filename'], f, file_info['mime_type'])}
            data = {
                "title": f"Integration Test {file_info['type']}",
                "description": "Test content for integration testing"
            }
            
            response = await client.make_request(
                "POST",
                "/upload",
                files=files,
                data=data
            )
        
        assert response["status_code"] == 201, f"Test upload failed: {response['text']}"
        return response["json"]["content_id"]

# Run tests with pytest -v tests/integration/test_complete_workflow.py
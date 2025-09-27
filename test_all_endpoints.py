#!/usr/bin/env python3
"""
Complete API Test Suite - Tests all endpoints and populates Supabase database
"""

import requests
import json
import time
import os
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser123",
    "password": "TestPass123!",
    "email": "test@example.com"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.content_ids = []
        
    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def test_health(self):
        """Test health endpoint"""
        self.log("Testing health endpoint...")
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        self.log(f"Health check: {response.json()['status']}")
        
    def test_demo_login(self):
        """Get demo credentials"""
        self.log("Getting demo credentials...")
        response = self.session.get(f"{BASE_URL}/demo-login")
        assert response.status_code == 200
        demo_creds = response.json()["demo_credentials"]
        self.log(f"Demo credentials: {demo_creds['username']}")
        return demo_creds
        
    def test_register(self):
        """Test user registration"""
        self.log("Testing user registration...")
        
        # Check if auth endpoints exist
        try:
            response = self.session.post(f"{BASE_URL}/users/register", json=TEST_USER)
            if response.status_code == 201:
                self.log("User registered successfully")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                self.log("User already exists")
                return True
        except:
            self.log("Registration endpoint not available, using demo user")
            return False
            
    def test_login(self):
        """Test user login"""
        self.log("Testing user login...")
        
        # Try test user first
        try:
            response = self.session.post(f"{BASE_URL}/users/login", json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            })
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.user_id = token_data.get("user_id", "testuser123")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log(f"Logged in as {TEST_USER['username']}")
                return True
        except:
            pass
            
        # Fallback to demo user
        demo_creds = self.test_demo_login()
        try:
            response = self.session.post(f"{BASE_URL}/users/login", json=demo_creds)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.user_id = token_data.get("user_id", "demo001")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log(f"Logged in as demo user")
                return True
        except Exception as e:
            self.log(f"Login failed, continuing without auth: {e}")
            self.user_id = "anonymous"
            return False
            
    def test_upload_content(self):
        """Test content upload"""
        self.log("Testing content upload...")
        
        # Create test file
        test_content = "This is a test script for video generation.\nSecond line of the script.\nThird line with more content."
        
        files = {
            'file': ('test_script.txt', BytesIO(test_content.encode()), 'text/plain')
        }
        data = {
            'title': 'Test Script Upload',
            'description': 'A test script file for API testing'
        }
        
        response = self.session.post(f"{BASE_URL}/upload", files=files, data=data)
        if response.status_code == 201:
            content_data = response.json()
            content_id = content_data["content_id"]
            self.content_ids.append(content_id)
            self.log(f"Content uploaded: {content_id}")
            return content_id
        else:
            self.log(f"Upload failed: {response.status_code} - {response.text}")
            return None
            
    def test_generate_video(self):
        """Test video generation"""
        self.log("Testing video generation...")
        
        # Create test script
        script_content = """Welcome to our AI video generation test.
This is the second scene of our video.
Here we demonstrate the video creation process.
Finally, we conclude with this last scene."""
        
        files = {
            'file': ('video_script.txt', BytesIO(script_content.encode()), 'text/plain')
        }
        data = {
            'title': 'Generated Test Video'
        }
        
        response = self.session.post(f"{BASE_URL}/generate-video", files=files, data=data)
        if response.status_code == 202:
            video_data = response.json()
            content_id = video_data["content_id"]
            self.content_ids.append(content_id)
            self.log(f"Video generated: {content_id}")
            return content_id
        else:
            self.log(f"Video generation failed: {response.status_code}")
            return None
            
    def test_list_contents(self):
        """Test content listing"""
        self.log("Testing content listing...")
        
        response = self.session.get(f"{BASE_URL}/contents?limit=10")
        if response.status_code == 200:
            contents = response.json()
            self.log(f"Listed {len(contents['items'])} contents")
            return contents
        else:
            self.log(f"Content listing failed: {response.status_code}")
            return None
            
    def test_content_details(self, content_id):
        """Test content details"""
        if not content_id:
            return
            
        self.log(f"Testing content details for {content_id}...")
        
        response = self.session.get(f"{BASE_URL}/content/{content_id}")
        if response.status_code == 200:
            self.log(f"Got content details for {content_id}")
            
            # Test metadata endpoint
            response = self.session.get(f"{BASE_URL}/content/{content_id}/metadata")
            if response.status_code == 200:
                self.log(f"Got content metadata for {content_id}")
        else:
            self.log(f"Content details failed: {response.status_code}")
            
    def test_feedback(self, content_id):
        """Test feedback submission"""
        if not content_id:
            return
            
        self.log(f"Testing feedback for {content_id}...")
        
        feedback_data = {
            "content_id": content_id,
            "rating": 4,
            "comment": "Great content! Very helpful for testing."
        }
        
        response = self.session.post(f"{BASE_URL}/feedback", json=feedback_data)
        if response.status_code == 201:
            self.log(f"Feedback submitted for {content_id}")
        else:
            self.log(f"Feedback failed: {response.status_code}")
            
    def test_tag_recommendations(self, content_id):
        """Test tag recommendations"""
        if not content_id:
            return
            
        self.log(f"Testing tag recommendations for {content_id}...")
        
        response = self.session.get(f"{BASE_URL}/recommend-tags/{content_id}")
        if response.status_code == 200:
            tags = response.json()
            self.log(f"Got tag recommendations: {tags.get('recommended_tags', [])}")
        else:
            self.log(f"Tag recommendations failed: {response.status_code}")
            
    def test_analytics_events(self):
        """Test analytics event logging"""
        self.log("Testing analytics events...")
        
        events = [
            {
                "event_type": "user_session_start",
                "metadata": {"device": "desktop", "browser": "chrome"}
            },
            {
                "event_type": "api_test_run",
                "metadata": {"test_suite": "complete", "timestamp": time.time()}
            },
            {
                "event_type": "content_interaction",
                "content_id": self.content_ids[0] if self.content_ids else None,
                "metadata": {"action": "view", "duration_ms": 5000}
            }
        ]
        
        for event in events:
            response = self.session.post(f"{BASE_URL}/analytics/event", json=event)
            if response.status_code == 200:
                self.log(f"Analytics event logged: {event['event_type']}")
            else:
                self.log(f"Analytics event failed: {response.status_code}")
                
    def test_analytics_summary(self):
        """Test analytics summary"""
        self.log("Testing analytics summary...")
        
        response = self.session.get(f"{BASE_URL}/analytics/summary?days=7")
        if response.status_code == 200:
            summary = response.json()
            self.log(f"Analytics summary: {summary.get('analytics_summary', {}).get('total_events', 0)} events")
        else:
            self.log(f"Analytics summary failed: {response.status_code}")
            
    def test_metrics(self):
        """Test system metrics"""
        self.log("Testing system metrics...")
        
        response = self.session.get(f"{BASE_URL}/metrics")
        if response.status_code == 200:
            metrics = response.json()
            system_metrics = metrics.get("system_metrics", {})
            self.log(f"System metrics - Users: {system_metrics.get('total_users', 0)}, Content: {system_metrics.get('total_contents', 0)}")
        else:
            self.log(f"Metrics failed: {response.status_code}")
            
    def test_bhiv_analytics(self):
        """Test advanced analytics"""
        self.log("Testing BHIV analytics...")
        
        response = self.session.get(f"{BASE_URL}/bhiv/analytics")
        if response.status_code == 200:
            analytics = response.json()
            self.log(f"BHIV analytics - Engagement rate: {analytics.get('engagement_rate', 0)}%")
        else:
            self.log(f"BHIV analytics failed: {response.status_code}")
            
    def test_database_debug(self):
        """Test database debug info"""
        self.log("Testing database debug...")
        
        response = self.session.get(f"{BASE_URL}/debug/database")
        if response.status_code == 200:
            debug_info = response.json()
            self.log(f"Database debug - Type: {debug_info.get('database_type', 'unknown')}")
        else:
            self.log(f"Database debug failed: {response.status_code}")
            
    def run_complete_test(self):
        """Run complete test suite"""
        self.log("Starting complete API test suite...")
        
        try:
            # Step 1: Health check
            self.test_health()
            
            # Step 2: Authentication
            self.test_register()
            self.test_login()
            
            # Step 3: Content operations
            content_id1 = self.test_upload_content()
            content_id2 = self.test_generate_video()
            self.test_list_contents()
            
            # Step 4: Content access
            self.test_content_details(content_id1)
            self.test_content_details(content_id2)
            
            # Step 5: Feedback and AI
            self.test_feedback(content_id1)
            self.test_feedback(content_id2)
            self.test_tag_recommendations(content_id1)
            
            # Step 6: Analytics
            self.test_analytics_events()
            self.test_analytics_summary()
            self.test_metrics()
            self.test_bhiv_analytics()
            
            # Step 7: Debug
            self.test_database_debug()
            
            self.log("Complete test suite finished!")
            self.log(f"Generated content IDs: {self.content_ids}")
            self.log("Check your Supabase database for all the test data!")
            
        except Exception as e:
            self.log(f"Test suite failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("AI Agent Complete API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("Server not responding. Start with: uvicorn app.main:app --reload")
            exit(1)
    except:
        print("Server not running. Start with: uvicorn app.main:app --reload")
        exit(1)
    
    # Run tests
    tester = APITester()
    tester.run_complete_test()
    
    print("\nNext steps:")
    print("1. Check your Supabase dashboard for new data")
    print("2. Visit http://localhost:8000/docs to explore API")
    print("3. Check http://localhost:8000/dashboard for system overview")
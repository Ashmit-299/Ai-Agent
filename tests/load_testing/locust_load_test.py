#!/usr/bin/env python3
"""
Load testing with Locust for 100 concurrent users
"""
import os
import json
import time
import random
from locust import HttpUser, task, between, events
from locust.exception import StopUser

class AIAgentUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user_id = None
        self.username = None
        self.content_ids = []
    
    def on_start(self):
        """Called when user starts - login or use demo credentials"""
        self.login()
    
    def login(self):
        """Login with demo credentials or create test user"""
        try:
            # Try demo login first
            response = self.client.post("/users/login", data={
                "username": "demo",
                "password": "demo1234"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.username = data.get("username")
                
                # Set headers for authenticated requests
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                print(f"✅ Logged in as {self.username}")
                return
        except Exception as e:
            print(f"Demo login failed: {e}")
        
        # Fallback: create random test user
        try:
            random_id = random.randint(1000, 9999)
            test_username = f"loadtest_user_{random_id}"
            
            register_response = self.client.post("/users/register", json={
                "username": test_username,
                "password": "testpass123",
                "email": f"{test_username}@loadtest.com"
            })
            
            if register_response.status_code == 201:
                data = register_response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.username = data.get("username")
                
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                print(f"✅ Created and logged in as {self.username}")
            else:
                print(f"❌ Registration failed: {register_response.status_code}")
                raise StopUser()
                
        except Exception as e:
            print(f"❌ User creation failed: {e}")
            raise StopUser()
    
    @task(10)  # 10% of requests
    def check_health(self):
        """Check system health"""
        self.client.get("/health", name="health_check")
    
    @task(5)  # 5% of requests
    def get_demo_login(self):
        """Get demo login info"""
        self.client.get("/demo-login", name="demo_login_info")
    
    @task(8)  # 8% of requests
    def list_contents(self):
        """List available content"""
        self.client.get("/contents", name="list_contents")
    
    @task(15)  # 15% of requests
    def get_metrics(self):
        """Get system metrics"""
        response = self.client.get("/metrics", name="system_metrics")
        if response.status_code != 200:
            print(f"Metrics failed: {response.status_code}")
    
    @task(12)  # 12% of requests
    def get_analytics(self):
        """Get analytics data"""
        self.client.get("/bhiv/analytics", name="analytics")
    
    @task(3)  # 3% of requests
    def upload_content(self):
        """Upload test content"""
        try:
            # Create test script content
            script_content = f"""
            Test script for load testing - User {self.username}
            Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}
            
            Scene 1: Introduction
            This is a test script for load testing purposes.
            
            Scene 2: Content
            Testing the video generation system under load.
            
            Scene 3: Conclusion  
            Load testing completed successfully.
            """
            
            files = {
                'file': ('test_script.txt', script_content, 'text/plain')
            }
            
            data = {
                'title': f'Load Test Script - {self.username} - {int(time.time())}',
                'description': 'Automated load testing upload'
            }
            
            response = self.client.post("/upload", 
                files=files, 
                data=data, 
                name="upload_content",
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                content_id = data.get("content_id")
                if content_id:
                    self.content_ids.append(content_id)
                    print(f"✅ Uploaded content: {content_id}")
            else:
                print(f"Upload failed: {response.status_code}")
                
        except Exception as e:
            print(f"Upload error: {e}")
    
    @task(2)  # 2% of requests  
    def generate_video(self):
        """Generate video from script"""
        try:
            script_content = f"""
            Video generation test - {self.username}
            Scene 1: Testing video generation under load.
            Scene 2: Multiple users generating videos simultaneously.
            Scene 3: System should handle concurrent requests gracefully.
            """
            
            files = {
                'file': ('video_script.txt', script_content, 'text/plain')
            }
            
            data = {
                'title': f'Load Test Video - {self.username} - {int(time.time())}'
            }
            
            response = self.client.post("/generate-video",
                files=files,
                data=data, 
                name="generate_video",
                timeout=60
            )
            
            if response.status_code == 202:
                data = response.json()
                content_id = data.get("content_id")
                if content_id:
                    self.content_ids.append(content_id)
                    print(f"✅ Generated video: {content_id}")
            else:
                print(f"Video generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"Video generation error: {e}")
    
    @task(8)  # 8% of requests
    def submit_feedback(self):
        """Submit feedback on content"""
        if not self.content_ids:
            return  # No content to rate
        
        try:
            # Pick random content ID
            content_id = random.choice(self.content_ids)
            rating = random.randint(1, 5)
            
            feedback_data = {
                "content_id": content_id,
                "rating": rating,
                "comment": f"Load test feedback from {self.username} - Rating: {rating}/5"
            }
            
            response = self.client.post("/feedback",
                json=feedback_data,
                name="submit_feedback"
            )
            
            if response.status_code == 201:
                print(f"✅ Submitted feedback: {rating}/5 for {content_id}")
            else:
                print(f"Feedback failed: {response.status_code}")
                
        except Exception as e:
            print(f"Feedback error: {e}")
    
    @task(6)  # 6% of requests
    def get_content_details(self):
        """Get content details"""
        if not self.content_ids:
            return
        
        try:
            content_id = random.choice(self.content_ids)
            response = self.client.get(f"/content/{content_id}", name="get_content_details")
            
            if response.status_code == 200:
                print(f"✅ Got content details: {content_id}")
                
        except Exception as e:
            print(f"Content details error: {e}")
    
    @task(4)  # 4% of requests
    def get_recommendations(self):
        """Get tag recommendations"""
        if not self.content_ids:
            return
        
        try:
            content_id = random.choice(self.content_ids)
            response = self.client.get(f"/recommend-tags/{content_id}", name="get_recommendations")
            
            if response.status_code == 200:
                print(f"✅ Got recommendations: {content_id}")
                
        except Exception as e:
            print(f"Recommendations error: {e}")
    
    @task(3)  # 3% of requests
    def check_user_profile(self):
        """Check user profile"""
        try:
            response = self.client.get("/users/profile", name="user_profile")
            
            if response.status_code == 200:
                print(f"✅ Got user profile: {self.username}")
                
        except Exception as e:
            print(f"Profile error: {e}")
    
    @task(2)  # 2% of requests
    def check_task_queue(self):
        """Check task queue status"""
        try:
            response = self.client.get("/tasks/queue/stats", name="task_queue_stats")
            
            if response.status_code == 200:
                print(f"✅ Got task queue stats")
                
        except Exception as e:
            print(f"Task queue error: {e}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("🚀 STARTING LOAD TEST - 100 CONCURRENT USERS")
    print("=" * 60)
    print(f"Target URL: {environment.host}")
    print(f"Test duration: Check Locust UI for details")
    print("=" * 60)

@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "=" * 60)
    print("🏁 LOAD TEST COMPLETED")
    
    # Print summary statistics
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Error rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print("=" * 60)

if __name__ == "__main__":
    print("""
    To run this load test:
    
    1. Install locust: pip install locust
    2. Start your AI Agent server: python scripts/start_server.py
    3. Run load test: locust -f tests/load_testing/locust_load_test.py --host=http://localhost:9000
    4. Open http://localhost:8089 to configure test (100 users, 10 spawn rate)
    5. Monitor results in real-time
    
    For automated headless test:
    locust -f tests/load_testing/locust_load_test.py --host=http://localhost:9000 --users 100 --spawn-rate 10 --run-time 10m --headless
    """)
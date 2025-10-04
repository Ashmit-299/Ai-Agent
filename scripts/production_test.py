#!/usr/bin/env python3
"""
Production Environment Testing Script
Tests with 5-10 users as per Task 5 requirements
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
import random

class ProductionTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    async def create_test_user(self, session, user_id):
        """Create and test a user session"""
        user_data = {
            "username": f"testuser{user_id}",
            "password": "testpass123",
            "email": f"test{user_id}@example.com"
        }
        
        try:
            # Register user
            async with session.post(f"{self.base_url}/users/register", json=user_data) as resp:
                if resp.status == 201:
                    user_info = await resp.json()
                    token = user_info["access_token"]
                    
                    # Test authenticated operations
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Upload content
                    test_content = "This is test content from user " + str(user_id)
                    data = aiohttp.FormData()
                    data.add_field('title', f'Test Content {user_id}')
                    data.add_field('description', 'Automated test content')
                    data.add_field('file', test_content.encode(), filename='test.txt', content_type='text/plain')
                    
                    async with session.post(f"{self.base_url}/upload", data=data, headers=headers) as upload_resp:
                        if upload_resp.status == 201:
                            content_info = await upload_resp.json()
                            content_id = content_info["content_id"]
                            
                            # Submit feedback
                            feedback_data = {
                                "content_id": content_id,
                                "rating": random.randint(3, 5),
                                "comment": f"Test feedback from user {user_id}"
                            }
                            
                            async with session.post(f"{self.base_url}/feedback", json=feedback_data, headers=headers) as feedback_resp:
                                feedback_success = feedback_resp.status == 201
                                
                            return {
                                "user_id": user_id,
                                "registration": True,
                                "upload": True,
                                "feedback": feedback_success,
                                "content_id": content_id
                            }
                    
                    return {
                        "user_id": user_id,
                        "registration": True,
                        "upload": False,
                        "feedback": False
                    }
                    
        except Exception as e:
            return {
                "user_id": user_id,
                "registration": False,
                "upload": False,
                "feedback": False,
                "error": str(e)
            }
    
    async def test_concurrent_users(self, num_users=5):
        """Test with multiple concurrent users"""
        print(f"🧪 Testing with {num_users} concurrent users...")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(1, num_users + 1):
                task = self.create_test_user(session, i)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_users = 0
            for result in results:
                if isinstance(result, dict) and result.get("registration"):
                    successful_users += 1
                    self.results.append(result)
            
            print(f"✅ {successful_users}/{num_users} users completed successfully")
            return successful_users
    
    async def test_system_load(self):
        """Test system under load"""
        print("📊 Testing system load...")
        
        async with aiohttp.ClientSession() as session:
            # Test health endpoint under load
            tasks = []
            for _ in range(20):
                task = session.get(f"{self.base_url}/health")
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_requests = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            
            print(f"📈 Load test: {successful_requests}/20 requests successful")
            print(f"📈 Total time: {end_time - start_time:.2f}s")
            
            return successful_requests >= 18  # 90% success rate
    
    def generate_test_report(self):
        """Generate production test report"""
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_users_tested": len(self.results),
            "successful_registrations": sum(1 for r in self.results if r.get("registration")),
            "successful_uploads": sum(1 for r in self.results if r.get("upload")),
            "successful_feedback": sum(1 for r in self.results if r.get("feedback")),
            "user_results": self.results
        }
        
        with open("production_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("📋 Production test report saved to production_test_report.json")
        return report

async def main():
    """Main production testing workflow"""
    print("🚀 Production Environment Testing")
    print("=" * 50)
    
    # Get production URL
    url = input("Enter production URL: ").strip()
    if not url.startswith("http"):
        url = f"https://{url}"
    
    tester = ProductionTester(url)
    
    # Test with 5 users first
    success_count = await tester.test_concurrent_users(5)
    
    if success_count >= 3:  # At least 60% success
        print("✅ Initial user test passed, testing with 10 users...")
        await tester.test_concurrent_users(10)
    
    # Test system load
    load_test_passed = await tester.test_system_load()
    
    if load_test_passed:
        print("✅ Load test passed!")
    else:
        print("⚠️ Load test showed performance issues")
    
    # Generate report
    report = tester.generate_test_report()
    
    print(f"\n📊 Final Results:")
    print(f"Users tested: {report['total_users_tested']}")
    print(f"Successful registrations: {report['successful_registrations']}")
    print(f"Successful uploads: {report['successful_uploads']}")
    print(f"Successful feedback: {report['successful_feedback']}")

if __name__ == "__main__":
    asyncio.run(main())
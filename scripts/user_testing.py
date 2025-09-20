#!/usr/bin/env python3
"""
User testing script for alpha release
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict

BASE_URL = "http://127.0.0.1:9000"

class AlphaUserTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_users = []
        self.results = []
    
    async def create_test_users(self, count: int = 5) -> List[Dict]:
        """Create test users for alpha testing"""
        users = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(count):
                user_data = {
                    "username": f"alpha_user_{i+1}",
                    "password": f"testpass{i+1}",
                    "email": f"alpha{i+1}@test.com"
                }
                
                try:
                    async with session.post(
                        f"{self.base_url}/users/register",
                        json=user_data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            users.append({
                                "username": user_data["username"],
                                "password": user_data["password"],
                                "token": result["access_token"],
                                "user_id": result["user_id"]
                            })
                            print(f"✅ Created user: {user_data['username']}")
                        else:
                            print(f"❌ Failed to create user: {user_data['username']}")
                except Exception as e:
                    print(f"❌ Error creating user {user_data['username']}: {e}")
        
        self.test_users = users
        return users
    
    async def test_user_workflow(self, user: Dict) -> Dict:
        """Test complete user workflow"""
        results = {
            "username": user["username"],
            "tests": {},
            "success_count": 0,
            "total_tests": 0
        }
        
        headers = {"Authorization": f"Bearer {user['token']}"}
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Get user profile
            try:
                async with session.get(f"{self.base_url}/users/profile", headers=headers) as response:
                    results["tests"]["profile"] = response.status == 200
                    results["total_tests"] += 1
                    if response.status == 200:
                        results["success_count"] += 1
            except Exception as e:
                results["tests"]["profile"] = False
                results["total_tests"] += 1
            
            # Test 2: Upload content
            try:
                form = aiohttp.FormData()
                form.add_field('title', f'Test Upload by {user["username"]}')
                form.add_field('description', 'Alpha testing upload')
                form.add_field('file', 'Test content for alpha testing', 
                              filename='test.txt', content_type='text/plain')
                
                async with session.post(f"{self.base_url}/upload", 
                                      data=form, headers=headers) as response:
                    results["tests"]["upload"] = response.status == 200
                    results["total_tests"] += 1
                    if response.status == 200:
                        results["success_count"] += 1
                        upload_result = await response.json()
                        results["content_id"] = upload_result.get("content_id")
            except Exception as e:
                results["tests"]["upload"] = False
                results["total_tests"] += 1
            
            # Test 3: Submit feedback
            if results.get("content_id"):
                try:
                    feedback_data = {
                        "content_id": results["content_id"],
                        "user_id": user["user_id"],
                        "rating": 4,
                        "comment": f"Great content from {user['username']}!"
                    }
                    
                    async with session.post(f"{self.base_url}/bhiv/feedback",
                                          json=feedback_data, headers=headers) as response:
                        results["tests"]["feedback"] = response.status == 200
                        results["total_tests"] += 1
                        if response.status == 200:
                            results["success_count"] += 1
                except Exception as e:
                    results["tests"]["feedback"] = False
                    results["total_tests"] += 1
            
            # Test 4: View analytics
            try:
                async with session.get(f"{self.base_url}/bhiv/analytics", headers=headers) as response:
                    results["tests"]["analytics"] = response.status == 200
                    results["total_tests"] += 1
                    if response.status == 200:
                        results["success_count"] += 1
            except Exception as e:
                results["tests"]["analytics"] = False
                results["total_tests"] += 1
            
            # Test 5: View dashboard
            try:
                async with session.get(f"{self.base_url}/dashboard") as response:
                    results["tests"]["dashboard"] = response.status == 200
                    results["total_tests"] += 1
                    if response.status == 200:
                        results["success_count"] += 1
            except Exception as e:
                results["tests"]["dashboard"] = False
                results["total_tests"] += 1
        
        results["success_rate"] = (results["success_count"] / results["total_tests"]) * 100
        return results
    
    async def run_alpha_test(self, num_users: int = 5):
        """Run complete alpha test with multiple users"""
        print(f"🚀 Starting Alpha User Testing with {num_users} users")
        
        # Create test users
        users = await self.create_test_users(num_users)
        if not users:
            print("❌ No users created, aborting test")
            return
        
        print(f"\n📊 Testing user workflows...")
        
        # Test each user workflow
        tasks = [self.test_user_workflow(user) for user in users]
        user_results = await asyncio.gather(*tasks)
        
        # Analyze results
        total_success = sum(r["success_count"] for r in user_results)
        total_tests = sum(r["total_tests"] for r in user_results)
        overall_success_rate = (total_success / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 Alpha Test Results:")
        print(f"   Total Users: {len(users)}")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful Tests: {total_success}")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        
        print(f"\n👥 Individual User Results:")
        for result in user_results:
            print(f"   {result['username']}: {result['success_rate']:.1f}% ({result['success_count']}/{result['total_tests']})")
        
        # Test summary by feature
        feature_results = {}
        for result in user_results:
            for test_name, success in result["tests"].items():
                if test_name not in feature_results:
                    feature_results[test_name] = {"success": 0, "total": 0}
                feature_results[test_name]["total"] += 1
                if success:
                    feature_results[test_name]["success"] += 1
        
        print(f"\n🔧 Feature Test Results:")
        for feature, stats in feature_results.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            print(f"   {feature.title()}: {success_rate:.1f}% ({stats['success']}/{stats['total']})")
        
        return {
            "overall_success_rate": overall_success_rate,
            "user_results": user_results,
            "feature_results": feature_results
        }

async def main():
    """Main testing function"""
    tester = AlphaUserTester()
    
    try:
        results = await tester.run_alpha_test(5)
        
        if results["overall_success_rate"] >= 80:
            print(f"\n🎉 Alpha test PASSED! Ready for user onboarding.")
            return 0
        else:
            print(f"\n⚠️ Alpha test needs improvement. Success rate: {results['overall_success_rate']:.1f}%")
            return 1
            
    except Exception as e:
        print(f"❌ Alpha test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
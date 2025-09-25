#!/usr/bin/env python3
"""
Render.com Deployment Script
Automated deployment verification and monitoring
"""

import requests
import time
import json
import os
from datetime import datetime

class RenderDeployment:
    def __init__(self):
        self.base_url = None  # Will be set after deployment
        self.deployment_status = "pending"
        
    def verify_deployment(self, url):
        """Verify deployment is successful"""
        self.base_url = url
        
        print(f"🚀 Verifying deployment at: {url}")
        
        # Test health endpoint
        try:
            response = requests.get(f"{url}/health", timeout=30)
            if response.status_code == 200:
                print("✅ Health check passed")
                self.deployment_status = "healthy"
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        if not self.base_url:
            print("❌ No deployment URL set")
            return False
            
        endpoints = [
            "/health",
            "/demo-login", 
            "/contents",
            "/metrics"
        ]
        
        print("🧪 Testing API endpoints...")
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401]:  # 401 is OK for auth-required endpoints
                    print(f"✅ {endpoint}: {response.status_code}")
                else:
                    print(f"❌ {endpoint}: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
                return False
        
        return True
    
    def test_user_workflow(self):
        """Test complete user workflow"""
        if not self.base_url:
            return False
            
        print("👥 Testing user workflow...")
        
        try:
            # Get demo credentials
            response = requests.get(f"{self.base_url}/demo-login")
            if response.status_code != 200:
                print("❌ Demo login endpoint failed")
                return False
                
            demo_creds = response.json()
            username = demo_creds["demo_credentials"]["username"]
            password = demo_creds["demo_credentials"]["password"]
            
            # Login
            login_data = {"username": username, "password": password}
            response = requests.post(f"{self.base_url}/users/login", data=login_data)
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                print("✅ User login successful")
                
                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{self.base_url}/users/profile", headers=headers)
                
                if response.status_code == 200:
                    print("✅ Authenticated request successful")
                    return True
                    
            print("❌ User workflow failed")
            return False
            
        except Exception as e:
            print(f"❌ User workflow error: {e}")
            return False
    
    def monitor_performance(self, duration_minutes=5):
        """Monitor deployment performance"""
        if not self.base_url:
            return
            
        print(f"📊 Monitoring performance for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        response_times = []
        errors = 0
        
        while time.time() < end_time:
            try:
                start = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=10)
                response_time = time.time() - start
                
                if response.status_code == 200:
                    response_times.append(response_time)
                else:
                    errors += 1
                    
            except Exception:
                errors += 1
                
            time.sleep(30)  # Check every 30 seconds
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            print(f"📈 Average response time: {avg_response:.2f}s")
            print(f"📈 Total requests: {len(response_times) + errors}")
            print(f"📈 Error rate: {errors}/{len(response_times) + errors}")
        
    def generate_deployment_report(self):
        """Generate deployment verification report"""
        report = {
            "deployment_url": self.base_url,
            "status": self.deployment_status,
            "timestamp": datetime.now().isoformat(),
            "verification_steps": [
                "Health check",
                "API endpoints test", 
                "User workflow test",
                "Performance monitoring"
            ]
        }
        
        with open("deployment_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print("📋 Deployment report saved to deployment_report.json")

def main():
    """Main deployment verification workflow"""
    print("🚀 Render.com Deployment Verification")
    print("=" * 50)
    
    deployment = RenderDeployment()
    
    # Get deployment URL from user
    url = input("Enter your Render.com deployment URL: ").strip()
    if not url.startswith("http"):
        url = f"https://{url}"
    
    # Verify deployment
    if deployment.verify_deployment(url):
        print("\n✅ Deployment verification successful!")
        
        # Test API endpoints
        if deployment.test_api_endpoints():
            print("\n✅ API endpoints test passed!")
            
            # Test user workflow
            if deployment.test_user_workflow():
                print("\n✅ User workflow test passed!")
                
                # Monitor performance
                deployment.monitor_performance(2)  # 2 minutes for quick test
                
                print("\n🎉 All deployment tests passed!")
            else:
                print("\n⚠️ User workflow test failed")
        else:
            print("\n⚠️ API endpoints test failed")
    else:
        print("\n❌ Deployment verification failed")
    
    # Generate report
    deployment.generate_deployment_report()

if __name__ == "__main__":
    main()
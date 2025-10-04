#!/usr/bin/env python3
"""
Auto-register test users for onboarding
"""

import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def register_user(username, password, email):
    """Register a single user"""
    try:
        response = requests.post(f"{BASE_URL}/users/register", json={
            "username": username,
            "password": password,
            "email": email
        })
        
        if response.status_code in [200, 201]:
            data = response.json()
            return {
                "success": True,
                "username": username,
                "token": data.get("access_token"),
                "user_id": data.get("user_id")
            }
        elif response.status_code == 400:
            return {"success": False, "error": "User already exists"}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def onboard_test_users():
    """Create multiple test users"""
    print("=== User Onboarding Script ===")
    
    test_users = [
        ("testuser1", "Test@123", "test1@example.com"),
        ("testuser2", "Test@123", "test2@example.com"),
        ("testuser3", "Test@123", "test3@example.com"),
        ("beta_user1", "Beta@123", "beta1@example.com"),
        ("beta_user2", "Beta@123", "beta2@example.com"),
    ]
    
    results = []
    
    for username, password, email in test_users:
        print(f"Registering {username}...")
        result = register_user(username, password, email)
        results.append(result)
        
        if result["success"]:
            print(f"[OK] {username} registered successfully")
        else:
            print(f"[ERROR] {username}: {result['error']}")
        
        time.sleep(0.5)  # Small delay between registrations
    
    return results

def test_user_login(username, password):
    """Test user login"""
    try:
        response = requests.post(f"{BASE_URL}/users/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data.get("access_token"),
                "user_id": data.get("user_id")
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def simulate_user_activity(token, username):
    """Simulate basic user activity"""
    headers = {"Authorization": f"Bearer {token}"}
    
    activities = []
    
    # Try to upload content
    try:
        response = requests.post(f"{BASE_URL}/upload",
                               files={"file": ("test.txt", f"Test content from {username}", "text/plain")},
                               data={"title": f"Test Upload by {username}"},
                               headers=headers)
        activities.append(("upload", response.status_code))
    except Exception as e:
        activities.append(("upload", f"error: {e}"))
    
    # Try to get metrics
    try:
        response = requests.get(f"{BASE_URL}/metrics", headers=headers)
        activities.append(("metrics", response.status_code))
    except Exception as e:
        activities.append(("metrics", f"error: {e}"))
    
    return activities

def main():
    """Main onboarding process"""
    print("AI Content Uploader - User Onboarding")
    print("=" * 40)
    print("Note: Ensure the API server is running")
    print("Command: python start_server.py")
    print()
    
    # Register users
    results = onboard_test_users()
    
    print(f"\n=== Registration Summary ===")
    successful_users = [r for r in results if r["success"]]
    failed_users = [r for r in results if not r["success"]]
    
    print(f"Successful registrations: {len(successful_users)}")
    print(f"Failed registrations: {len(failed_users)}")
    
    # Test login and activity for successful users
    if successful_users:
        print(f"\n=== Testing User Activity ===")
        
        for user_result in successful_users[:2]:  # Test first 2 users
            username = user_result["username"]
            print(f"Testing activity for {username}...")
            
            # Login test
            login_result = test_user_login(username, "Test@123")
            if login_result["success"]:
                print(f"[OK] {username} login successful")
                
                # Simulate activity
                activities = simulate_user_activity(login_result["token"], username)
                for activity, status in activities:
                    print(f"  - {activity}: {status}")
            else:
                print(f"[ERROR] {username} login failed: {login_result['error']}")
    
    print(f"\n=== Onboarding Complete ===")
    print("Users are ready for testing and feedback collection")
    
    # Save results for integration tests
    with open("onboarding_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to onboarding_results.json")

if __name__ == "__main__":
    main()
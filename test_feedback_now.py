#!/usr/bin/env python3
"""
Test feedback endpoint now
"""
import requests
import json

def test_feedback():
    url = "http://localhost:9000/feedback"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2htIiwidXNlcl9pZCI6IjU0NDk1MTY4NjBmOSIsImV4cCI6MTc1OTY1NDE1NCwiaWF0IjoxNzU5NTY3NzU0LCJ0eXBlIjoiYWNjZXNzIiwianRpIjoiSWk5b0lsY2dzbllRdjRnUG03eU1VUSJ9.Iyi2mpL-kOtUTc8ExWRsDFd_4PV-I21jZIEFwcKqW24"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "content_id": "9a2b35e14d7c_30df5d",
        "rating": 5,
        "comment": "great"
    }
    
    print("Testing feedback endpoint...")
    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_feedback()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
#!/usr/bin/env python3
"""Force deployment by making a dummy change"""

import requests
import time

# Test current production status
def test_production():
    try:
        response = requests.get("https://ai-agent-aff6.onrender.com/health", timeout=10)
        print(f"Production health: {response.status_code}")
        
        response = requests.get("https://ai-agent-aff6.onrender.com/metrics", timeout=10)
        data = response.json()
        print(f"Current metrics: {data['system_metrics']}")
        
        # Test database connection directly
        response = requests.get("https://ai-agent-aff6.onrender.com/contents", timeout=10)
        contents = response.json()
        print(f"Contents endpoint: {len(contents.get('items', []))} items")
        
    except Exception as e:
        print(f"Production test failed: {e}")

if __name__ == "__main__":
    test_production()
#!/usr/bin/env python3
"""Test the debug database endpoint"""

import requests
import time
import json

def test_debug_endpoint():
    print("Waiting for deployment...")
    time.sleep(90)
    
    print("Testing debug database endpoint...")
    try:
        response = requests.get("https://ai-agent-aff6.onrender.com/debug/database", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Debug response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_debug_endpoint()
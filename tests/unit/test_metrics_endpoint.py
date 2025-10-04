#!/usr/bin/env python3
"""Test the metrics endpoint directly"""

import requests
import json

def test_metrics_endpoint():
    """Test the /metrics endpoint"""
    try:
        # Test local server first
        url = "http://127.0.0.1:8000/metrics"
        print(f"Testing {url}...")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Metrics response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Local server not running, testing production...")
        
        # Test production server
        url = "https://ai-agent-aff6.onrender.com/metrics"
        print(f"Testing {url}...")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Production metrics response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Production test failed: {e}")
    
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_metrics_endpoint()
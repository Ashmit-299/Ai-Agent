#!/usr/bin/env python3
"""Wait for deployment and test metrics"""

import requests
import time

def wait_and_test():
    print("Waiting 60 seconds for deployment...")
    time.sleep(60)
    
    print("Testing production metrics...")
    try:
        response = requests.get("https://ai-agent-aff6.onrender.com/metrics", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('system_metrics', {})
            print(f"Metrics: {metrics}")
            
            if metrics.get('total_contents', 0) > 0:
                print("SUCCESS: Metrics now showing real data!")
            else:
                print("STILL FAILING: Metrics showing zero")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    wait_and_test()
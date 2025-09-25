#!/usr/bin/env python3
"""Verify that the metrics fix is working in production"""

import requests
import json
import time

def verify_metrics_fix():
    """Verify the metrics endpoint shows correct data"""
    print("Waiting for deployment to complete...")
    time.sleep(30)  # Wait for deployment
    
    url = "https://ai-agent-aff6.onrender.com/metrics"
    
    for attempt in range(5):
        try:
            print(f"Attempt {attempt + 1}: Testing {url}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if metrics show real data
                system_metrics = data.get('system_metrics', {})
                total_contents = system_metrics.get('total_contents', 0)
                total_feedback = system_metrics.get('total_feedback', 0)
                total_users = system_metrics.get('total_users', 0)
                
                print(f"System metrics:")
                print(f"  Total contents: {total_contents}")
                print(f"  Total feedback: {total_feedback}")
                print(f"  Total users: {total_users}")
                
                if total_contents > 0 or total_feedback > 0 or total_users > 0:
                    print("✅ SUCCESS: Metrics are now showing real data!")
                    print(json.dumps(data, indent=2))
                    return True
                else:
                    print("❌ Still showing zero values, waiting for deployment...")
                    time.sleep(60)  # Wait 1 minute between attempts
            else:
                print(f"HTTP {response.status_code}: {response.text}")
                time.sleep(30)
                
        except Exception as e:
            print(f"Request failed: {e}")
            time.sleep(30)
    
    print("❌ FAILED: Metrics still showing zero after all attempts")
    return False

if __name__ == "__main__":
    verify_metrics_fix()
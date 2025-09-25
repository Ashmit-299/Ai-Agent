#!/usr/bin/env python3
"""Final test of all endpoints after metrics fix"""

import requests
import time
import json

def final_test():
    print("Waiting for final deployment...")
    time.sleep(120)  # Wait 2 minutes for deployment
    
    base_url = "https://ai-agent-aff6.onrender.com"
    
    endpoints_to_test = [
        ("/health", "Health check"),
        ("/contents", "Content listing"),
        ("/metrics", "System metrics"),
        ("/bhiv/analytics", "Analytics"),
        ("/debug/database", "Database debug")
    ]
    
    print("Testing all endpoints...")
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            print(f"\n{description} ({endpoint}):")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if endpoint == "/contents":
                    items = data.get('items', [])
                    print(f"  Content items: {len(items)}")
                
                elif endpoint == "/metrics":
                    metrics = data.get('system_metrics', {})
                    print(f"  Users: {metrics.get('total_users', 0)}")
                    print(f"  Content: {metrics.get('total_contents', 0)}")
                    print(f"  Feedback: {metrics.get('total_feedback', 0)}")
                    
                    if metrics.get('total_contents', 0) > 0:
                        print("  ✅ SUCCESS: Metrics showing real data!")
                    else:
                        print("  ❌ FAIL: Metrics still zero")
                
                elif endpoint == "/bhiv/analytics":
                    print(f"  Users: {data.get('total_users', 0)}")
                    print(f"  Content: {data.get('total_content', 0)}")
                    print(f"  Feedback: {data.get('total_feedback', 0)}")
                    
                    if data.get('total_content', 0) > 0:
                        print("  ✅ SUCCESS: Analytics showing real data!")
                    else:
                        print("  ❌ FAIL: Analytics still zero")
                
                elif endpoint == "/debug/database":
                    if data.get('status') == 'success':
                        results = data.get('direct_query_results', {})
                        print(f"  Direct DB - Users: {results.get('users', 0)}")
                        print(f"  Direct DB - Content: {results.get('content', 0)}")
                        print(f"  Direct DB - Feedback: {results.get('feedback', 0)}")
                    else:
                        print(f"  Debug status: {data.get('status', 'unknown')}")
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{description} ({endpoint}): ERROR - {e}")
    
    print("\n" + "="*50)
    print("FINAL VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    final_test()
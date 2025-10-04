#!/usr/bin/env python3
"""Test database connection directly"""

import requests
import json

def test_db_connection():
    """Test database connection and queries"""
    base_url = "https://ai-agent-aff6.onrender.com"
    
    # Test contents endpoint (this works)
    print("Testing /contents endpoint...")
    response = requests.get(f"{base_url}/contents", timeout=30)
    if response.status_code == 200:
        data = response.json()
        print(f"Contents: {len(data.get('items', []))} items found")
        if data.get('items'):
            print(f"Sample item: {data['items'][0].get('content_id', 'N/A')}")
    
    # Test metrics endpoint (this fails)
    print("\nTesting /metrics endpoint...")
    response = requests.get(f"{base_url}/metrics", timeout=30)
    if response.status_code == 200:
        data = response.json()
        metrics = data.get('system_metrics', {})
        print(f"Metrics: Users={metrics.get('total_users', 0)}, Content={metrics.get('total_contents', 0)}")
    
    # Test analytics endpoint
    print("\nTesting /bhiv/analytics endpoint...")
    response = requests.get(f"{base_url}/bhiv/analytics", timeout=30)
    if response.status_code == 200:
        data = response.json()
        print(f"Analytics: Users={data.get('total_users', 0)}, Content={data.get('total_content', 0)}")

if __name__ == "__main__":
    test_db_connection()
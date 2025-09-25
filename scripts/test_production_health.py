#!/usr/bin/env python3
"""
Test production observability health endpoint
"""

import requests
import json
import time

def test_production_health():
    """Test production health endpoint"""
    
    production_url = "https://ai-agent-aff6.onrender.com"
    
    print("Testing Production Observability Health")
    print("=" * 50)
    
    # Test basic health
    try:
        print("\n1. Testing basic health endpoint...")
        response = requests.get(f"{production_url}/health", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Basic health: OK")
        else:
            print(f"Basic health failed: {response.text}")
    except Exception as e:
        print(f"Basic health error: {e}")
    
    # Test detailed health
    try:
        print("\n2. Testing detailed health endpoint...")
        response = requests.get(f"{production_url}/health/detailed", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print("Detailed health response:")
            print(json.dumps(health_data, indent=2))
            
            # Check observability services
            services = health_data.get("services", {})
            observability = services.get("observability", {})
            
            print(f"\nObservability Status:")
            print(f"Sentry enabled: {observability.get('sentry', {}).get('enabled', False)}")
            print(f"Sentry DSN configured: {observability.get('sentry', {}).get('dsn_configured', False)}")
            print(f"PostHog enabled: {observability.get('posthog', {}).get('enabled', False)}")
            print(f"PostHog API key configured: {observability.get('posthog', {}).get('api_key_configured', False)}")
            
        else:
            print(f"Detailed health failed: {response.text}")
            
    except Exception as e:
        print(f"Detailed health error: {e}")
    
    # Test metrics endpoint
    try:
        print("\n3. Testing metrics endpoint...")
        response = requests.get(f"{production_url}/metrics", timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Metrics endpoint: OK")
        else:
            print(f"Metrics failed: {response.text}")
    except Exception as e:
        print(f"Metrics error: {e}")

if __name__ == "__main__":
    print("Waiting 2 minutes for deployment to complete...")
    time.sleep(120)  # Wait for deployment
    test_production_health()
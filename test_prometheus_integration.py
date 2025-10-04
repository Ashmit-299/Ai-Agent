#!/usr/bin/env python3
"""
Test Prometheus metrics integration
"""

import requests
import time
import sys

def test_prometheus_endpoints():
    """Test Prometheus metrics endpoints"""
    base_url = "http://localhost:9000"
    
    print("Testing Prometheus Metrics Integration...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("ERROR: Server not healthy")
            return False
        print("OK: Server is running and healthy")
    except requests.exceptions.ConnectionError:
        print("ERROR: Server not running on port 9000")
        print("Start with: python scripts/start_server.py")
        return False
    
    # Test 2: Check metrics info endpoint
    try:
        response = requests.get(f"{base_url}/metrics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK: Metrics info endpoint working")
            print(f"Prometheus enabled: {data.get('prometheus_enabled')}")
            print(f"Available endpoints: {list(data.get('available_endpoints', {}).keys())}")
        else:
            print(f"ERROR: Metrics info endpoint - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Metrics info test failed: {e}")
    
    # Test 3: Check Prometheus metrics endpoint
    try:
        response = requests.get(f"{base_url}/metrics/prometheus", timeout=10)
        if response.status_code == 200:
            metrics_text = response.text
            print("OK: Prometheus metrics endpoint working")
            
            # Check for common Prometheus metrics
            expected_metrics = [
                "fastapi_requests_total",
                "fastapi_request_duration_seconds",
                "fastapi_responses_total"
            ]
            
            found_metrics = []
            for metric in expected_metrics:
                if metric in metrics_text:
                    found_metrics.append(metric)
            
            print(f"Found metrics: {found_metrics}")
            print(f"Metrics content length: {len(metrics_text)} characters")
            
            # Show sample metrics
            lines = metrics_text.split('\n')[:10]
            print("Sample metrics:")
            for line in lines:
                if line and not line.startswith('#'):
                    print(f"  {line}")
                    break
            
        else:
            print(f"ERROR: Prometheus metrics endpoint - {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Prometheus metrics test failed: {e}")
        return False
    
    # Test 4: Generate some traffic and check metrics
    try:
        print("\nGenerating test traffic...")
        
        # Make some requests to generate metrics
        test_endpoints = ["/health", "/metrics/performance", "/debug-auth"]
        
        for endpoint in test_endpoints:
            try:
                requests.get(f"{base_url}{endpoint}", timeout=5)
            except:
                pass  # Ignore errors, just generating traffic
        
        time.sleep(1)  # Wait for metrics to update
        
        # Check metrics again
        response = requests.get(f"{base_url}/metrics/prometheus", timeout=10)
        if response.status_code == 200:
            metrics_text = response.text
            
            # Look for request counts
            request_lines = [line for line in metrics_text.split('\n') 
                           if 'fastapi_requests_total' in line and not line.startswith('#')]
            
            if request_lines:
                print("OK: Traffic metrics captured")
                print(f"Request metrics found: {len(request_lines)} entries")
            else:
                print("WARNING: No request metrics found yet")
        
    except Exception as e:
        print(f"WARNING: Traffic generation test failed: {e}")
    
    # Test 5: Check performance metrics endpoint
    try:
        response = requests.get(f"{base_url}/metrics/performance", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK: Performance metrics endpoint working")
            print(f"Prometheus available: {data.get('prometheus_available')}")
            print(f"Prometheus endpoint: {data.get('prometheus_endpoint')}")
        else:
            print(f"ERROR: Performance metrics endpoint - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Performance metrics test failed: {e}")
    
    return True

def test_prometheus_module():
    """Test Prometheus module import"""
    print("\nTesting Prometheus Module...")
    print("=" * 30)
    
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        print("OK: Prometheus FastAPI instrumentator imported")
        
        # Test instrumentator creation
        instrumentator = Instrumentator()
        print("OK: Instrumentator instance created")
        
        return True
    except ImportError:
        print("ERROR: Prometheus FastAPI instrumentator not installed")
        return False
    except Exception as e:
        print(f"ERROR: Prometheus module test failed: {e}")
        return False

def main():
    """Run all Prometheus tests"""
    print("Prometheus Integration Test Suite")
    print("=" * 50)
    
    # Test module import
    module_ok = test_prometheus_module()
    
    if not module_ok:
        print("\nModule test failed - install with:")
        print("pip install prometheus-fastapi-instrumentator==6.1.0")
        return 1
    
    # Test endpoints
    endpoints_ok = test_prometheus_endpoints()
    
    print("\nTest Summary:")
    print("=" * 30)
    print(f"Module Import: {'PASS' if module_ok else 'FAIL'}")
    print(f"Endpoints: {'PASS' if endpoints_ok else 'FAIL'}")
    
    if module_ok and endpoints_ok:
        print("\nAll Prometheus integration tests passed!")
        print("Metrics available at: http://localhost:9000/metrics/prometheus")
        return 0
    else:
        print("\nSome tests failed - check configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Check monitoring endpoints to verify integration status
"""

import requests
import json
import time

def check_local_monitoring():
    """Check local monitoring endpoints"""
    print("Checking local monitoring endpoints...")
    
    base_url = "http://localhost:9000"
    
    endpoints = [
        "/health",
        "/health/detailed", 
        "/monitoring-status",
        "/test-monitoring",
        "/metrics/performance",
        "/observability/health"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    "status": "OK",
                    "data": data
                }
                print(f"OK: {endpoint} - {response.status_code}")
            else:
                results[endpoint] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                print(f"ERROR: {endpoint} - {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            results[endpoint] = {
                "status": "SERVER_NOT_RUNNING",
                "error": "Connection refused"
            }
            print(f"ERROR: {endpoint} - Server not running")
        except Exception as e:
            results[endpoint] = {
                "status": "ERROR", 
                "error": str(e)
            }
            print(f"ERROR: {endpoint} - {e}")
    
    return results

def check_production_monitoring():
    """Check production monitoring endpoints"""
    print("\nChecking production monitoring endpoints...")
    
    base_url = "https://ai-agent-aff6.onrender.com"
    
    endpoints = [
        "/health",
        "/health/detailed",
        "/metrics",
        "/observability/health"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    "status": "OK",
                    "data": data
                }
                print(f"OK: {endpoint} - {response.status_code}")
            else:
                results[endpoint] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                print(f"ERROR: {endpoint} - {response.status_code}")
                
        except Exception as e:
            results[endpoint] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"ERROR: {endpoint} - {e}")
    
    return results

def analyze_monitoring_data(local_results, prod_results):
    """Analyze monitoring data for integration status"""
    print("\nAnalyzing monitoring data...")
    
    # Check local health data
    if "/health/detailed" in local_results and local_results["/health/detailed"]["status"] == "OK":
        health_data = local_results["/health/detailed"]["data"]
        print(f"Local Health Status: {health_data.get('status', 'unknown')}")
        
        if "observability" in health_data:
            obs_data = health_data["observability"]
            print(f"Local Sentry: {obs_data.get('sentry', {}).get('enabled', 'unknown')}")
            print(f"Local PostHog: {obs_data.get('posthog', {}).get('enabled', 'unknown')}")
    
    # Check production health data
    if "/health/detailed" in prod_results and prod_results["/health/detailed"]["status"] == "OK":
        health_data = prod_results["/health/detailed"]["data"]
        print(f"Production Health Status: {health_data.get('status', 'unknown')}")
        
        if "observability" in health_data:
            obs_data = health_data["observability"]
            print(f"Production Sentry: {obs_data.get('sentry', {}).get('enabled', 'unknown')}")
            print(f"Production PostHog: {obs_data.get('posthog', {}).get('enabled', 'unknown')}")

def main():
    """Run monitoring endpoint checks"""
    print("AI Agent Monitoring Endpoint Check")
    print("=" * 40)
    
    local_results = check_local_monitoring()
    prod_results = check_production_monitoring()
    
    analyze_monitoring_data(local_results, prod_results)
    
    print("\nSummary:")
    print("=" * 40)
    
    local_working = sum(1 for r in local_results.values() if r["status"] == "OK")
    prod_working = sum(1 for r in prod_results.values() if r["status"] == "OK")
    
    print(f"Local endpoints working: {local_working}/{len(local_results)}")
    print(f"Production endpoints working: {prod_working}/{len(prod_results)}")
    
    if local_working == 0:
        print("NOTE: Start local server with 'python scripts/start_server.py' to test local endpoints")
    
    return 0

if __name__ == "__main__":
    exit(main())
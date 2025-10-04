#!/usr/bin/env python3
"""
Check port status and update all references to use port 9000
"""

import requests

def check_ports():
    """Check which ports are active"""
    
    ports = [8000, 9000]
    
    print("Port Status Check")
    print("=" * 30)
    
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"Port {port}: ACTIVE")
                data = response.json()
                print(f"  Service: {data.get('service', 'Unknown')}")
            else:
                print(f"Port {port}: HTTP {response.status_code}")
        except:
            print(f"Port {port}: OFFLINE")
    
    print("\nCorrect URLs:")
    print("- Main Server: http://localhost:9000")
    print("- API Docs: http://localhost:9000/docs") 
    print("- Monitoring: http://localhost:9000/monitoring-status")
    print("- Test Monitoring: http://localhost:9000/test-monitoring")

if __name__ == "__main__":
    check_ports()
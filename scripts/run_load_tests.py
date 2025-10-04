#!/usr/bin/env python3
"""
Load testing runner script
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_server_running(host="localhost", port=9000):
    """Check if the server is running"""
    try:
        import requests
        response = requests.get(f"http://{host}:{port}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def run_locust_test(users=100, spawn_rate=10, run_time="10m", host="http://localhost:9000"):
    """Run Locust load test"""
    
    print(f"🚀 Starting Locust load test:")
    print(f"  Users: {users}")
    print(f"  Spawn rate: {spawn_rate}/sec")
    print(f"  Duration: {run_time}")
    print(f"  Target: {host}")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    locust_file = project_root / "tests" / "load_testing" / "locust_load_test.py"
    
    if not locust_file.exists():
        print(f"❌ Locust file not found: {locust_file}")
        return False
    
    try:
        # Install locust if not present
        subprocess.run([sys.executable, "-m", "pip", "install", "locust"], 
                      check=True, capture_output=True)
        
        # Run locust test
        cmd = [
            sys.executable, "-m", "locust",
            "-f", str(locust_file),
            "--host", host,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", run_time,
            "--headless",
            "--html", "load_test_report.html"
        ]
        
        print("Running command:", " ".join(cmd))
        
        result = subprocess.run(cmd, cwd=project_root, text=True)
        
        if result.returncode == 0:
            print("✅ Locust load test completed successfully")
            
            # Check if report was generated
            report_path = project_root / "load_test_report.html"
            if report_path.exists():
                print(f"📊 Load test report: {report_path}")
            
            return True
        else:
            print(f"❌ Locust test failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Load test execution failed: {e}")
        return False

def run_stress_test():
    """Run async stress test"""
    
    print("\n🔥 Starting async stress test...")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    stress_file = project_root / "tests" / "load_testing" / "stress_test.py"
    
    if not stress_file.exists():
        print(f"❌ Stress test file not found: {stress_file}")
        return False
    
    try:
        # Install aiohttp if not present
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"], 
                      check=True, capture_output=True)
        
        # Run stress test
        cmd = [sys.executable, str(stress_file)]
        
        result = subprocess.run(cmd, cwd=project_root, text=True)
        
        if result.returncode == 0:
            print("✅ Stress test completed successfully")
            
            # Check if results were generated
            results_path = project_root / "stress_test_results.json"
            if results_path.exists():
                print(f"📊 Stress test results: {results_path}")
            
            return True
        else:
            print(f"❌ Stress test failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Stress test execution failed: {e}")
        return False

def main():
    """Main load testing function"""
    
    print("🧪 AI AGENT LOAD TESTING SUITE")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Server not running on http://localhost:9000")
        print("💡 Start server with: python scripts/start_server.py")
        return 1
    
    print("✅ Server is running and responding")
    
    # Run Locust load test
    locust_success = run_locust_test(
        users=100,
        spawn_rate=10,
        run_time="5m",  # Shorter for demo
        host="http://localhost:9000"
    )
    
    # Run stress test
    stress_success = run_stress_test()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 LOAD TESTING SUMMARY")
    print("=" * 60)
    
    print(f"🚀 Locust Load Test: {'✅ PASSED' if locust_success else '❌ FAILED'}")
    print(f"🔥 Async Stress Test: {'✅ PASSED' if stress_success else '❌ FAILED'}")
    
    if locust_success and stress_success:
        print("\n🎉 ALL LOAD TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
        return 0
    else:
        print("\n⚠️ SOME LOAD TESTS FAILED - REVIEW PERFORMANCE")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
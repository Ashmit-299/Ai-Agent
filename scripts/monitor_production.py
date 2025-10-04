#!/usr/bin/env python3
"""
Production Monitoring Script
Monitors logs and performance in production environment
"""

import requests
import time
import json
from datetime import datetime, timedelta
import asyncio
import aiohttp

class ProductionMonitor:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.metrics_history = []
        
    def check_health(self):
        """Check application health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_metrics(self):
        """Get system metrics from API"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Metrics unavailable: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_analytics(self):
        """Get analytics data"""
        try:
            response = requests.get(f"{self.base_url}/bhiv/analytics", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Analytics unavailable: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_database_connectivity(self):
        """Check database connectivity through API"""
        try:
            response = requests.get(f"{self.base_url}/contents?limit=1", timeout=10)
            return {
                "database_accessible": response.status_code in [200, 401],
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "database_accessible": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def performance_test(self, duration_minutes=5):
        """Run performance test"""
        print(f"📊 Running performance test for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        response_times = []
        error_count = 0
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    start = time.time()
                    async with session.get(f"{self.base_url}/health") as response:
                        response_time = time.time() - start
                        
                        if response.status == 200:
                            response_times.append(response_time)
                        else:
                            error_count += 1
                            
                except Exception:
                    error_count += 1
                
                await asyncio.sleep(10)  # Test every 10 seconds
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            min_response = min(response_times)
            
            return {
                "total_requests": len(response_times) + error_count,
                "successful_requests": len(response_times),
                "error_count": error_count,
                "error_rate": error_count / (len(response_times) + error_count) * 100,
                "avg_response_time": avg_response,
                "max_response_time": max_response,
                "min_response_time": min_response,
                "duration_minutes": duration_minutes
            }
        
        return {"error": "No successful requests"}
    
    def monitor_session(self, duration_minutes=10):
        """Run monitoring session"""
        print(f"🔍 Starting monitoring session for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        monitoring_data = []
        
        while time.time() < end_time:
            # Collect metrics
            health = self.check_health()
            metrics = self.get_system_metrics()
            analytics = self.get_analytics()
            db_check = self.check_database_connectivity()
            
            data_point = {
                "timestamp": datetime.now().isoformat(),
                "health": health,
                "metrics": metrics,
                "analytics": analytics,
                "database": db_check
            }
            
            monitoring_data.append(data_point)
            self.metrics_history.append(data_point)
            
            # Print status
            status = health.get("status", "unknown")
            response_time = health.get("response_time", 0)
            print(f"⏱️ {datetime.now().strftime('%H:%M:%S')} - Status: {status}, Response: {response_time:.2f}s")
            
            time.sleep(60)  # Check every minute
        
        return monitoring_data
    
    def generate_monitoring_report(self, monitoring_data, performance_data=None):
        """Generate comprehensive monitoring report"""
        report = {
            "monitoring_period": {
                "start": monitoring_data[0]["timestamp"] if monitoring_data else None,
                "end": monitoring_data[-1]["timestamp"] if monitoring_data else None,
                "duration_minutes": len(monitoring_data)
            },
            "health_summary": {
                "total_checks": len(monitoring_data),
                "healthy_checks": sum(1 for d in monitoring_data if d["health"].get("status") == "healthy"),
                "error_checks": sum(1 for d in monitoring_data if d["health"].get("status") == "error")
            },
            "performance_data": performance_data,
            "detailed_data": monitoring_data[-10:] if len(monitoring_data) > 10 else monitoring_data  # Last 10 data points
        }
        
        # Calculate uptime percentage
        if report["health_summary"]["total_checks"] > 0:
            uptime = (report["health_summary"]["healthy_checks"] / report["health_summary"]["total_checks"]) * 100
            report["uptime_percentage"] = round(uptime, 2)
        
        with open("production_monitoring_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("📋 Monitoring report saved to production_monitoring_report.json")
        return report

async def main():
    """Main monitoring workflow"""
    print("📊 Production Monitoring")
    print("=" * 50)
    
    # Get production URL
    url = input("Enter production URL: ").strip()
    if not url.startswith("http"):
        url = f"https://{url}"
    
    monitor = ProductionMonitor(url)
    
    # Initial health check
    health = monitor.check_health()
    print(f"Initial health check: {health['status']}")
    
    if health["status"] != "healthy":
        print("⚠️ Application appears to be unhealthy")
        return
    
    # Run performance test
    print("\n🚀 Running performance test...")
    performance_data = await monitor.performance_test(2)  # 2 minutes
    
    if "error" not in performance_data:
        print(f"📈 Performance test results:")
        print(f"  Success rate: {100 - performance_data['error_rate']:.1f}%")
        print(f"  Avg response time: {performance_data['avg_response_time']:.2f}s")
    
    # Run monitoring session
    print("\n🔍 Starting monitoring session...")
    monitoring_data = monitor.monitor_session(5)  # 5 minutes
    
    # Generate report
    report = monitor.generate_monitoring_report(monitoring_data, performance_data)
    
    print(f"\n📊 Monitoring Summary:")
    print(f"Uptime: {report.get('uptime_percentage', 0)}%")
    print(f"Total checks: {report['health_summary']['total_checks']}")
    print(f"Healthy checks: {report['health_summary']['healthy_checks']}")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Stress testing script for AI Agent endpoints
"""
import asyncio
import aiohttp
import time
import json
import random
from concurrent.futures import ThreadPoolExecutor
import statistics

class StressTest:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url
        self.results = []
        self.token = None
    
    async def login(self, session):
        """Login to get authentication token"""
        try:
            async with session.post(f"{self.base_url}/users/login", data={
                "username": "demo",
                "password": "demo1234"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("access_token")
                    return True
        except Exception as e:
            print(f"Login failed: {e}")
        return False
    
    async def make_request(self, session, method, endpoint, **kwargs):
        """Make HTTP request and record timing"""
        start_time = time.time()
        
        headers = kwargs.get('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            kwargs['headers'] = headers
        
        try:
            async with session.request(method, f"{self.base_url}{endpoint}", **kwargs) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                result = {
                    'endpoint': endpoint,
                    'method': method,
                    'status': response.status,
                    'response_time': response_time,
                    'success': 200 <= response.status < 400,
                    'timestamp': start_time
                }
                
                self.results.append(result)
                return result
                
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e),
                'timestamp': start_time
            }
            
            self.results.append(result)
            return result
    
    async def test_health_endpoints(self, session, iterations=50):
        """Test health check endpoints"""
        tasks = []
        
        for _ in range(iterations):
            tasks.append(self.make_request(session, 'GET', '/health'))
            tasks.append(self.make_request(session, 'GET', '/demo-login'))
            
        await asyncio.gather(*tasks)
    
    async def test_content_endpoints(self, session, iterations=30):
        """Test content-related endpoints"""
        tasks = []
        
        for _ in range(iterations):
            tasks.append(self.make_request(session, 'GET', '/contents'))
            tasks.append(self.make_request(session, 'GET', '/metrics'))
            tasks.append(self.make_request(session, 'GET', '/bhiv/analytics'))
            
        await asyncio.gather(*tasks)
    
    async def test_upload_simulation(self, session, iterations=10):
        """Simulate file uploads"""
        tasks = []
        
        for i in range(iterations):
            # Create test content
            test_content = f"Test script {i} - {time.time()}"
            
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_content, filename='test.txt', content_type='text/plain')
            form_data.add_field('title', f'Stress Test Upload {i}')
            form_data.add_field('description', 'Automated stress test upload')
            
            tasks.append(self.make_request(session, 'POST', '/upload', data=form_data))
            
        await asyncio.gather(*tasks)
    
    async def run_stress_test(self, concurrent_users=50, duration_seconds=60):
        """Run comprehensive stress test"""
        print(f"🚀 Starting stress test: {concurrent_users} users for {duration_seconds}s")
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Login first
            await self.login(session)
            
            start_time = time.time()
            tasks = []
            
            # Create concurrent user tasks
            for user_id in range(concurrent_users):
                task = self.simulate_user_behavior(session, user_id, duration_seconds)
                tasks.append(task)
            
            # Run all tasks concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            print(f"✅ Stress test completed in {total_time:.2f}s")
    
    async def simulate_user_behavior(self, session, user_id, duration_seconds):
        """Simulate realistic user behavior"""
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            # Random user actions
            action = random.choice([
                'health_check',
                'list_content', 
                'get_metrics',
                'get_analytics',
                'upload_content'
            ])
            
            try:
                if action == 'health_check':
                    await self.make_request(session, 'GET', '/health')
                elif action == 'list_content':
                    await self.make_request(session, 'GET', '/contents')
                elif action == 'get_metrics':
                    await self.make_request(session, 'GET', '/metrics')
                elif action == 'get_analytics':
                    await self.make_request(session, 'GET', '/bhiv/analytics')
                elif action == 'upload_content':
                    # Simulate upload
                    test_content = f"User {user_id} test - {time.time()}"
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', test_content, filename='test.txt', content_type='text/plain')
                    form_data.add_field('title', f'User {user_id} Upload')
                    form_data.add_field('description', 'Stress test upload')
                    
                    await self.make_request(session, 'POST', '/upload', data=form_data)
                
                # Random delay between requests
                await asyncio.sleep(random.uniform(0.1, 2.0))
                
            except Exception as e:
                print(f"User {user_id} error: {e}")
    
    def analyze_results(self):
        """Analyze stress test results"""
        if not self.results:
            print("❌ No results to analyze")
            return
        
        print("\n📊 STRESS TEST ANALYSIS")
        print("=" * 60)
        
        # Overall statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_requests}")
        print(f"Failed: {failed_requests}")
        print(f"Success Rate: {success_rate:.2f}%")
        
        # Response time statistics
        response_times = [r['response_time'] for r in self.results if r['success']]
        
        if response_times:
            print(f"\n⏱️ Response Time Statistics:")
            print(f"Average: {statistics.mean(response_times):.2f}ms")
            print(f"Median: {statistics.median(response_times):.2f}ms")
            print(f"Min: {min(response_times):.2f}ms")
            print(f"Max: {max(response_times):.2f}ms")
            print(f"95th Percentile: {sorted(response_times)[int(len(response_times) * 0.95)]:.2f}ms")
        
        # Endpoint breakdown
        endpoint_stats = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'total': 0, 'success': 0, 'times': []}
            
            endpoint_stats[endpoint]['total'] += 1
            if result['success']:
                endpoint_stats[endpoint]['success'] += 1
                endpoint_stats[endpoint]['times'].append(result['response_time'])
        
        print(f"\n🎯 Endpoint Performance:")
        for endpoint, stats in endpoint_stats.items():
            success_rate = (stats['success'] / stats['total']) * 100
            avg_time = statistics.mean(stats['times']) if stats['times'] else 0
            print(f"  {endpoint}: {success_rate:.1f}% success, {avg_time:.2f}ms avg")
        
        # Performance assessment
        print(f"\n🏆 Performance Assessment:")
        if success_rate >= 95 and statistics.mean(response_times) < 1000:
            print("✅ EXCELLENT - System handles load very well")
        elif success_rate >= 90 and statistics.mean(response_times) < 2000:
            print("✅ GOOD - System performs well under load")
        elif success_rate >= 80:
            print("⚠️ ACCEPTABLE - Some performance degradation under load")
        else:
            print("❌ POOR - System struggles under load, optimization needed")

async def main():
    """Main stress testing function"""
    stress_test = StressTest()
    
    # Run stress test
    await stress_test.run_stress_test(concurrent_users=50, duration_seconds=60)
    
    # Analyze results
    stress_test.analyze_results()
    
    # Save results to file
    with open('stress_test_results.json', 'w') as f:
        json.dump(stress_test.results, f, indent=2)
    
    print(f"\n💾 Results saved to: stress_test_results.json")

if __name__ == "__main__":
    print("""
    🔥 AI Agent Stress Testing Tool
    
    This script will:
    1. Simulate 50 concurrent users
    2. Run for 60 seconds
    3. Test all major endpoints
    4. Analyze performance metrics
    
    Make sure your server is running on http://localhost:9000
    """)
    
    asyncio.run(main())
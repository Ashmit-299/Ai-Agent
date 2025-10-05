#!/usr/bin/env python3
"""
Performance Benchmark Test Suite
Tests system performance under various load conditions
"""

import pytest
import asyncio
import httpx
import time
import statistics
from typing import List, Dict, Any
import logging
import concurrent.futures
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Performance benchmark result"""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    requests_per_second: float
    error_rate: float

class PerformanceBenchmark:
    """Performance benchmarking suite"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.results: List[BenchmarkResult] = []
    
    async def run_concurrent_requests(
        self, 
        url: str, 
        method: str = "GET",
        concurrent_users: int = 10,
        requests_per_user: int = 5,
        headers: Dict[str, str] = None,
        **kwargs
    ) -> BenchmarkResult:
        """Run concurrent requests and measure performance"""
        
        async def make_single_request(session: httpx.AsyncClient) -> Dict[str, Any]:
            """Make a single request and track timing"""
            start_time = time.time()
            try:
                response = await session.request(method, url, headers=headers, **kwargs)
                duration = time.time() - start_time
                return {
                    "success": 200 <= response.status_code < 400,
                    "status_code": response.status_code,
                    "duration": duration,
                    "error": None
                }
            except Exception as e:
                duration = time.time() - start_time
                return {
                    "success": False,
                    "status_code": 0,
                    "duration": duration,
                    "error": str(e)
                }
        
        async def user_session(user_id: int) -> List[Dict[str, Any]]:
            """Simulate a user making multiple requests"""
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                tasks = []
                for _ in range(requests_per_user):
                    tasks.append(make_single_request(client))
                return await asyncio.gather(*tasks)
        
        # Run benchmark
        start_time = time.time()
        logger.info(f"Starting benchmark: {concurrent_users} users x {requests_per_user} requests")
        
        # Create user sessions
        user_tasks = []
        for user_id in range(concurrent_users):
            user_tasks.append(user_session(user_id))
        
        # Execute all user sessions concurrently
        user_results = await asyncio.gather(*user_tasks)
        total_time = time.time() - start_time
        
        # Flatten results
        all_results = []
        for user_result in user_results:
            all_results.extend(user_result)
        
        # Calculate metrics
        successful_requests = sum(1 for r in all_results if r["success"])
        failed_requests = len(all_results) - successful_requests
        response_times = [r["duration"] for r in all_results]
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max_response_time
        requests_per_second = len(all_results) / total_time if total_time > 0 else 0
        error_rate = (failed_requests / len(all_results)) * 100 if all_results else 0
        
        result = BenchmarkResult(
            test_name=f"{method} {url}",
            total_requests=len(all_results),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )
        
        self.results.append(result)
        logger.info(f"Benchmark completed: {result.requests_per_second:.1f} RPS, {result.error_rate:.1f}% error rate")
        return result

@pytest.mark.asyncio
class TestPerformanceBenchmarks:
    """Performance benchmark test suite"""
    
    @pytest.fixture(autouse=True)
    def setup_benchmark(self):
        """Setup benchmark testing"""
        self.benchmark = PerformanceBenchmark()
        self.benchmark_results = []
    
    async def test_health_endpoint_performance(self):
        """Benchmark health endpoint under load"""
        logger.info("Testing health endpoint performance")
        
        result = await self.benchmark.run_concurrent_requests(
            "/health",
            concurrent_users=20,
            requests_per_user=10
        )
        
        # Performance assertions (adjusted for realistic expectations)
        assert result.error_rate < 1.0, f"Health endpoint error rate too high: {result.error_rate}%"
        assert result.avg_response_time < 2.0, f"Health endpoint too slow: {result.avg_response_time}s"
        assert result.requests_per_second > 10, f"Health endpoint RPS too low: {result.requests_per_second}"
        
        self.benchmark_results.append(result)

    async def test_authentication_performance(self):
        """Benchmark authentication endpoints"""
        logger.info("Testing authentication performance")
        
        # Test login performance
        login_data = {
            "username": "demo",
            "password": "demo1234"
        }
        
        result = await self.benchmark.run_concurrent_requests(
            "/users/login",
            method="POST",
            concurrent_users=10,
            requests_per_user=5,
            data=login_data
        )
        
        # Authentication should handle moderate load
        assert result.error_rate < 5.0, f"Login error rate too high: {result.error_rate}%"
        assert result.avg_response_time < 2.0, f"Login too slow: {result.avg_response_time}s"
        
        self.benchmark_results.append(result)

    async def test_content_listing_performance(self):
        """Benchmark content listing endpoint"""
        logger.info("Testing content listing performance")
        
        result = await self.benchmark.run_concurrent_requests(
            "/contents",
            concurrent_users=15,
            requests_per_user=8
        )
        
        # Content listing should be reasonably fast
        assert result.error_rate < 5.0, f"Content listing error rate too high: {result.error_rate}%"
        assert result.avg_response_time < 3.0, f"Content listing too slow: {result.avg_response_time}s"
        assert result.requests_per_second > 5, f"Content listing RPS too low: {result.requests_per_second}"
        
        self.benchmark_results.append(result)

    async def test_metrics_endpoint_performance(self):
        """Benchmark metrics endpoints"""
        logger.info("Testing metrics endpoint performance")
        
        result = await self.benchmark.run_concurrent_requests(
            "/metrics",
            concurrent_users=12,
            requests_per_user=6
        )
        
        # Metrics should be reasonably fast
        assert result.error_rate < 5.0, f"Metrics error rate too high: {result.error_rate}%"
        assert result.avg_response_time < 3.0, f"Metrics too slow: {result.avg_response_time}s"
        
        self.benchmark_results.append(result)

    async def test_mixed_workload_performance(self):
        """Test mixed workload performance"""
        logger.info("Testing mixed workload performance")
        
        # Simulate mixed workload
        endpoints = ["/health", "/contents", "/metrics"]
        
        async def mixed_workload():
            results = []
            for endpoint in endpoints:
                result = await self.benchmark.run_concurrent_requests(
                    endpoint,
                    concurrent_users=5,
                    requests_per_user=3
                )
                results.append(result)
            return results
        
        results = await mixed_workload()
        
        # Overall system should handle mixed load well
        total_requests = sum(r.total_requests for r in results)
        total_errors = sum(r.failed_requests for r in results)
        overall_error_rate = (total_errors / total_requests) * 100 if total_requests > 0 else 0
        
        assert overall_error_rate < 3.0, f"Mixed workload error rate too high: {overall_error_rate}%"
        
        self.benchmark_results.extend(results)

    async def test_stress_test_performance(self):
        """Stress test with high concurrent load"""
        logger.info("Running stress test")
        
        # High load stress test
        result = await self.benchmark.run_concurrent_requests(
            "/health",
            concurrent_users=50,
            requests_per_user=4
        )
        
        # Under stress, we allow higher error rates but system should not fail completely
        assert result.error_rate < 10.0, f"Stress test error rate too high: {result.error_rate}%"
        assert result.successful_requests > 0, "System failed completely under stress"
        
        logger.info(f"Stress test result: {result.successful_requests}/{result.total_requests} successful")
        self.benchmark_results.append(result)

    async def test_generate_performance_report(self):
        """Generate comprehensive performance report"""
        logger.info("Generating performance report")
        
        if not self.benchmark_results:
            pytest.skip("No benchmark results to report")
        
        print("\n" + "="*80)
        print("PERFORMANCE BENCHMARK REPORT")
        print("="*80)
        
        for result in self.benchmark_results:
            print(f"\n{result.test_name}")
            print(f"   Total Requests: {result.total_requests}")
            print(f"   Successful: {result.successful_requests} ({100-result.error_rate:.1f}%)")
            print(f"   Failed: {result.failed_requests} ({result.error_rate:.1f}%)")
            print(f"   Requests/Second: {result.requests_per_second:.1f}")
            print(f"   Avg Response Time: {result.avg_response_time:.3f}s")
            print(f"   95th Percentile: {result.p95_response_time:.3f}s")
            print(f"   Min/Max: {result.min_response_time:.3f}s / {result.max_response_time:.3f}s")
        
        # Overall statistics
        total_requests = sum(r.total_requests for r in self.benchmark_results)
        total_successful = sum(r.successful_requests for r in self.benchmark_results)
        overall_error_rate = ((total_requests - total_successful) / total_requests) * 100 if total_requests > 0 else 0
        avg_rps = statistics.mean([r.requests_per_second for r in self.benchmark_results])
        avg_response_time = statistics.mean([r.avg_response_time for r in self.benchmark_results])
        
        print(f"\nOVERALL PERFORMANCE SUMMARY")
        print(f"   Total Requests Processed: {total_requests}")
        print(f"   Overall Success Rate: {100-overall_error_rate:.1f}%")
        print(f"   Average Requests/Second: {avg_rps:.1f}")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        
        # Performance benchmarks
        print(f"\nPERFORMANCE BENCHMARKS")
        print(f"   ✓ Error Rate < 5%: {'PASS' if overall_error_rate < 5.0 else 'FAIL'}")
        print(f"   ✓ Avg Response Time < 2s: {'PASS' if avg_response_time < 2.0 else 'FAIL'}")
        print(f"   ✓ Min RPS > 10: {'PASS' if avg_rps > 10 else 'FAIL'}")
        
        print("="*80)
        
        # Assert overall performance meets requirements
        assert overall_error_rate < 5.0, f"Overall error rate too high: {overall_error_rate}%"
        assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time}s"
        assert avg_rps > 10, f"Average RPS too low: {avg_rps}"

# Run with: pytest -v tests/integration/test_performance_benchmarks.py -s
#!/usr/bin/env python3
"""
Comprehensive test coverage script - ensure 70%+ coverage
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def run_coverage_test():
    """Run pytest with coverage reporting"""
    
    print("🧪 RUNNING COMPREHENSIVE TEST COVERAGE")
    print("=" * 60)
    
    try:
        # Install coverage if not present
        subprocess.run([sys.executable, "-m", "pip", "install", "coverage", "pytest-cov"], 
                      check=True, capture_output=True)
        
        # Run tests with coverage
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=app",
            "--cov=core", 
            "--cov=video",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=json:coverage.json",
            "--cov-fail-under=70",
            "-v",
            "tests/"
        ]
        
        print("Running command:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Parse coverage results
        if os.path.exists("coverage.json"):
            with open("coverage.json", "r") as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data["totals"]["percent_covered"]
            
            print(f"\n📊 COVERAGE RESULTS")
            print(f"Total Coverage: {total_coverage:.1f}%")
            
            # Module breakdown
            print("\n📁 MODULE BREAKDOWN:")
            for file_path, file_data in coverage_data["files"].items():
                module_coverage = file_data["summary"]["percent_covered"]
                missing_lines = len(file_data["missing_lines"])
                print(f"  {file_path}: {module_coverage:.1f}% ({missing_lines} lines missing)")
            
            # Check if we meet the 70% threshold
            if total_coverage >= 70.0:
                print(f"\n✅ Coverage target met: {total_coverage:.1f}% >= 70%")
                return True
            else:
                print(f"\n❌ Coverage target not met: {total_coverage:.1f}% < 70%")
                print("\n💡 To improve coverage, focus on:")
                
                # Find files with lowest coverage
                low_coverage_files = []
                for file_path, file_data in coverage_data["files"].items():
                    module_coverage = file_data["summary"]["percent_covered"]
                    if module_coverage < 60:
                        low_coverage_files.append((file_path, module_coverage))
                
                low_coverage_files.sort(key=lambda x: x[1])
                for file_path, coverage in low_coverage_files[:5]:
                    print(f"  - {file_path}: {coverage:.1f}%")
                
                return False
        else:
            print("❌ Coverage report not generated")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        print(f"Return code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Coverage analysis failed: {e}")
        return False

def generate_coverage_report():
    """Generate detailed HTML coverage report"""
    
    print("\n📋 GENERATING DETAILED COVERAGE REPORT")
    print("=" * 60)
    
    try:
        # Generate HTML report
        cmd = [
            sys.executable, "-m", "coverage", "html",
            "--directory=htmlcov",
            "--title=AI Agent Coverage Report"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ HTML coverage report generated: htmlcov/index.html")
            
            # Try to open the report
            html_path = Path("htmlcov/index.html").absolute()
            if html_path.exists():
                print(f"📂 Report location: {html_path}")
                print("💡 Open this file in your browser to view detailed coverage")
            
            return True
        else:
            print(f"❌ HTML report generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return False

def run_specific_tests():
    """Run specific test categories"""
    
    print("\n🎯 RUNNING SPECIFIC TEST CATEGORIES")
    print("=" * 60)
    
    test_categories = [
        ("Unit Tests", "tests/unit/"),
        ("Integration Tests", "tests/integration/"),
        ("Load Tests", "tests/load_testing/")
    ]
    
    results = {}
    
    for category, path in test_categories:
        if os.path.exists(path):
            print(f"\n🧪 Running {category}...")
            
            try:
                cmd = [sys.executable, "-m", "pytest", path, "-v", "--tb=short"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"✅ {category}: PASSED")
                    results[category] = "PASSED"
                else:
                    print(f"❌ {category}: FAILED")
                    print(f"Error output: {result.stdout[-500:]}")  # Last 500 chars
                    results[category] = "FAILED"
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {category}: TIMEOUT")
                results[category] = "TIMEOUT"
            except Exception as e:
                print(f"❌ {category}: ERROR - {e}")
                results[category] = "ERROR"
        else:
            print(f"⚠️ {category}: Directory not found - {path}")
            results[category] = "NOT_FOUND"
    
    return results

def main():
    """Main coverage testing function"""
    
    print("🚀 AI AGENT COMPREHENSIVE TESTING SUITE")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Run specific tests first
    test_results = run_specific_tests()
    
    # Run coverage analysis
    coverage_success = run_coverage_test()
    
    # Generate detailed report
    report_success = generate_coverage_report()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TESTING SUMMARY")
    print("=" * 60)
    
    print("\n🧪 Test Results:")
    for category, result in test_results.items():
        status_emoji = "✅" if result == "PASSED" else "❌"
        print(f"  {status_emoji} {category}: {result}")
    
    print(f"\n📈 Coverage Analysis: {'✅ PASSED' if coverage_success else '❌ FAILED'}")
    print(f"📋 HTML Report: {'✅ GENERATED' if report_success else '❌ FAILED'}")
    
    # Overall status
    overall_success = (
        coverage_success and 
        report_success and 
        all(result in ["PASSED", "NOT_FOUND"] for result in test_results.values())
    )
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - REVIEW RESULTS BEFORE DEPLOYMENT")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
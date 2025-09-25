#!/usr/bin/env python3
"""Verify Sentry and PostHog integrations with real data"""

import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_sentry_integration():
    """Test Sentry with real error and message"""
    print("\n=== SENTRY INTEGRATION TEST ===")
    
    try:
        from app.observability import sentry_manager
        
        if not sentry_manager.initialized:
            print("FAIL: Sentry not initialized")
            return False
            
        print("SUCCESS: Sentry manager initialized")
        
        # Test 1: Send info message
        sentry_manager.capture_message(
            "AI Agent Integration Test - Info Message", 
            level="info",
            extra_data={
                "test_type": "integration_verification",
                "timestamp": datetime.now().isoformat(),
                "component": "sentry_test"
            }
        )
        print("SUCCESS: Info message sent to Sentry")
        
        # Test 2: Send warning
        sentry_manager.capture_message(
            "AI Agent Integration Test - Warning Message", 
            level="warning",
            extra_data={
                "test_type": "integration_verification",
                "warning_reason": "This is a test warning"
            }
        )
        print("SUCCESS: Warning message sent to Sentry")
        
        # Test 3: Send real exception
        try:
            # Create a realistic error scenario
            test_data = {"user_id": "test_123", "action": "upload_file"}
            if test_data["user_id"] == "invalid_user":
                raise ValueError("Invalid user ID provided")
            # Simulate another error
            raise ConnectionError("Database connection failed during test")
        except Exception as e:
            sentry_manager.capture_exception(e, extra_data={
                "test_scenario": "database_connection_error",
                "user_context": test_data,
                "error_type": "integration_test"
            })
            print("SUCCESS: Exception sent to Sentry")
        
        # Test 4: Set user context
        sentry_manager.set_user_context(
            user_id="test_user_123",
            username="integration_tester",
            email="test@aiagent.com"
        )
        print("SUCCESS: User context set in Sentry")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Sentry integration error: {e}")
        return False

def test_posthog_integration():
    """Test PostHog with real analytics events"""
    print("\n=== POSTHOG INTEGRATION TEST ===")
    
    try:
        from app.observability import posthog_manager
        
        if not posthog_manager.initialized:
            print("FAIL: PostHog not initialized")
            return False
            
        print("SUCCESS: PostHog manager initialized")
        
        # Test 1: User signup event
        posthog_manager.track_event(
            user_id="test_user_123",
            event="user_signup",
            properties={
                "signup_method": "email",
                "source": "integration_test",
                "timestamp": datetime.now().isoformat(),
                "user_agent": "AI Agent Test Suite"
            }
        )
        print("SUCCESS: User signup event sent to PostHog")
        
        # Test 2: File upload event
        posthog_manager.track_event(
            user_id="test_user_123",
            event="file_uploaded",
            properties={
                "file_type": "text",
                "file_size": 1024,
                "processing_time_ms": 250,
                "success": True,
                "feature": "content_upload"
            }
        )
        print("SUCCESS: File upload event sent to PostHog")
        
        # Test 3: Video generation event
        posthog_manager.track_event(
            user_id="test_user_123",
            event="video_generated",
            properties={
                "video_duration": 30,
                "generation_time_ms": 5000,
                "quality": "HD",
                "success": True,
                "ai_model": "test_model"
            }
        )
        print("SUCCESS: Video generation event sent to PostHog")
        
        # Test 4: User identification
        posthog_manager.identify_user(
            user_id="test_user_123",
            traits={
                "email": "test@aiagent.com",
                "username": "integration_tester",
                "signup_date": datetime.now().isoformat(),
                "plan": "free",
                "integration_test": True
            }
        )
        print("SUCCESS: User identified in PostHog")
        
        # Test 5: Feature usage tracking
        posthog_manager.track_feature_usage(
            user_id="test_user_123",
            feature="ai_content_analysis",
            success=True,
            duration_ms=1500,
            metadata={
                "content_type": "text",
                "analysis_score": 0.85,
                "tags_generated": 5
            }
        )
        print("SUCCESS: Feature usage tracked in PostHog")
        
        return True
        
    except Exception as e:
        print(f"FAIL: PostHog integration error: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring integration"""
    print("\n=== PERFORMANCE MONITORING TEST ===")
    
    try:
        from app.observability import performance_monitor
        
        # Test operation measurement
        with performance_monitor.measure_operation("test_database_query", "test_user_123"):
            time.sleep(0.2)  # Simulate database query
        
        print("SUCCESS: Database query operation measured")
        
        # Test slow operation
        with performance_monitor.measure_operation("test_slow_operation", "test_user_123"):
            time.sleep(1.5)  # Simulate slow operation
        
        print("SUCCESS: Slow operation measured and reported")
        
        # Get performance summary
        summary = performance_monitor.get_performance_summary()
        print(f"SUCCESS: Performance summary generated: {len(summary.get('metrics', {}))} metrics")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Performance monitoring error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("AI AGENT OBSERVABILITY INTEGRATION VERIFICATION")
    print("=" * 60)
    
    # Show configuration
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Sentry DSN: {os.getenv('SENTRY_DSN', 'Not set')[:50]}...")
    print(f"PostHog Key: {os.getenv('POSTHOG_API_KEY', 'Not set')[:20]}...")
    print(f"PostHog Host: {os.getenv('POSTHOG_HOST', 'Not set')}")
    
    # Run tests
    results = {
        "sentry": test_sentry_integration(),
        "posthog": test_posthog_integration(), 
        "performance": test_performance_monitoring()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST RESULTS:")
    
    all_passed = True
    for service, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{service.upper()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: All observability services integrated and working!")
        print("\nNext steps:")
        print("1. Check Sentry dashboard: https://sentry.io")
        print("2. Check PostHog dashboard: https://app.posthog.com")
        print("3. Look for events from user 'test_user_123'")
        print("4. Verify error reports and analytics data")
    else:
        print("FAILURE: Some services need attention")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
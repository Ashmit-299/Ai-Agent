#!/usr/bin/env python3
"""
Full integration test with Sentry, PostHog, and Supabase
Tests actual data flow through all systems
"""

import requests
import json
import time
import tempfile
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:8000"

def test_user_registration_flow():
    """Test complete user registration with observability"""
    print("Testing user registration flow...")
    
    try:
        # Generate unique test user
        timestamp = int(time.time())
        test_user = {
            "username": f"testuser_{timestamp}",
            "password": "TestPass123!",
            "email": f"test_{timestamp}@example.com"
        }
        
        # Register user
        response = requests.post(f"{BASE_URL}/users/register", json=test_user, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            print(f"  [OK] User registered: {test_user['username']}")
            print(f"  [OK] Token received: {data['access_token'][:20]}...")
            return data['access_token'], test_user['username']
        else:
            print(f"  [FAIL] Registration failed: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"  [FAIL] Registration error: {e}")
        return None, None

def test_content_upload_flow(token, username):
    """Test content upload with observability tracking"""
    print("Testing content upload flow...")
    
    try:
        # Create test script file
        test_script = """
        Welcome to our AI video generation system.
        This is a test script for integration testing.
        We will create a video from this text content.
        Each sentence will become a frame in the video.
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            temp_file_path = f.name
        
        try:
            # Upload file
            headers = {"Authorization": f"Bearer {token}"}
            
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("test_script.txt", f, "text/plain")}
                data = {"title": f"Integration Test Script - {username}", "description": "Test upload for integration verification"}
                
                response = requests.post(f"{BASE_URL}/upload", headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code == 201:
                upload_data = response.json()
                print(f"  [OK] File uploaded: {upload_data['content_id']}")
                print(f"  [OK] Authenticity score: {upload_data['authenticity_score']}")
                print(f"  [OK] Tags generated: {len(upload_data['tags'])}")
                return upload_data['content_id']
            else:
                print(f"  [FAIL] Upload failed: {response.status_code}")
                print(f"  [FAIL] Response: {response.text[:200]}")
                return None
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        print(f"  [FAIL] Upload error: {e}")
        return None

def test_video_generation_flow(token, username):
    """Test video generation with observability"""
    print("Testing video generation flow...")
    
    try:
        # Create test script for video generation
        test_script = """
        This is a test video generation.
        Each line will become a video frame.
        Testing the complete pipeline integration.
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            temp_file_path = f.name
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("video_script.txt", f, "text/plain")}
                data = {"title": f"Integration Test Video - {username}"}
                
                response = requests.post(f"{BASE_URL}/generate-video", headers=headers, files=files, data=data, timeout=60)
            
            if response.status_code == 202:
                video_data = response.json()
                print(f"  [OK] Video generation started: {video_data['content_id']}")
                print(f"  [OK] Video path: {video_data['video_path']}")
                print(f"  [OK] Total scenes: {video_data['storyboard_stats']['total_scenes']}")
                return video_data['content_id']
            else:
                print(f"  [FAIL] Video generation failed: {response.status_code}")
                print(f"  [FAIL] Response: {response.text[:200]}")
                return None
                
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        print(f"  [FAIL] Video generation error: {e}")
        return None

def test_feedback_flow(token, content_id, username):
    """Test feedback submission with RL agent training"""
    print("Testing feedback flow...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        feedback_data = {
            "content_id": content_id,
            "rating": 4,
            "comment": f"Great integration test content from {username}!"
        }
        
        response = requests.post(f"{BASE_URL}/feedback", headers=headers, json=feedback_data, timeout=30)
        
        if response.status_code == 201:
            feedback_response = response.json()
            print(f"  [OK] Feedback submitted: Rating {feedback_response['rating']}")
            print(f"  [OK] RL training: {feedback_response['rl_training']['agent_trained']}")
            print(f"  [OK] Event type: {feedback_response['event_type']}")
            return True
        else:
            print(f"  [FAIL] Feedback failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Feedback error: {e}")
        return False

def test_analytics_flow():
    """Test analytics and metrics collection"""
    print("Testing analytics flow...")
    
    try:
        # Test system metrics
        response = requests.get(f"{BASE_URL}/metrics", timeout=15)
        if response.status_code == 200:
            metrics = response.json()
            print(f"  [OK] System metrics retrieved")
            print(f"  [OK] Total users: {metrics['system_metrics']['total_users']}")
            print(f"  [OK] Total content: {metrics['system_metrics']['total_contents']}")
        else:
            print(f"  [FAIL] Metrics failed: {response.status_code}")
            return False
        
        # Test BHIV analytics
        response = requests.get(f"{BASE_URL}/bhiv/analytics", timeout=15)
        if response.status_code == 200:
            analytics = response.json()
            print(f"  [OK] BHIV analytics retrieved")
            print(f"  [OK] Average rating: {analytics['average_rating']}")
            print(f"  [OK] Engagement rate: {analytics['engagement_rate']}%")
        else:
            print(f"  [FAIL] BHIV analytics failed: {response.status_code}")
            return False
        
        # Test observability health
        response = requests.get(f"{BASE_URL}/observability/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"  [OK] Observability health checked")
            print(f"  [OK] Sentry enabled: {health['observability_health']['sentry']['enabled']}")
            print(f"  [OK] PostHog enabled: {health['observability_health']['posthog']['enabled']}")
        else:
            print(f"  [FAIL] Observability health failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Analytics error: {e}")
        return False

def test_direct_integrations():
    """Test direct integration with observability services"""
    print("Testing direct integrations...")
    
    try:
        from app.observability import sentry_manager, posthog_manager
        
        # Test Sentry
        if sentry_manager.initialized:
            sentry_manager.capture_message("Full integration test completed", "info", {
                "test_type": "full_integration",
                "timestamp": time.time(),
                "components_tested": ["registration", "upload", "video_generation", "feedback", "analytics"]
            })
            print("  [OK] Sentry message sent")
        else:
            print("  [FAIL] Sentry not initialized")
            return False
        
        # Test PostHog
        if posthog_manager.initialized:
            posthog_manager.track_event("integration_test_user", "full_integration_test_completed", {
                "test_duration": time.time(),
                "all_components_tested": True,
                "success": True
            })
            print("  [OK] PostHog event tracked")
        else:
            print("  [FAIL] PostHog not initialized")
            return False
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Direct integration error: {e}")
        return False

def main():
    """Run complete integration test"""
    print("=== Full Integration Test ===")
    print("Testing Sentry, PostHog, and Supabase with real data flow")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    # Test flow
    results = {}
    
    # 1. User Registration
    token, username = test_user_registration_flow()
    results["registration"] = bool(token)
    
    if not token:
        print("\n[CRITICAL] Cannot continue without authentication token")
        return
    
    # 2. Content Upload
    content_id = test_content_upload_flow(token, username)
    results["upload"] = bool(content_id)
    
    # 3. Video Generation
    video_content_id = test_video_generation_flow(token, username)
    results["video_generation"] = bool(video_content_id)
    
    # 4. Feedback (use upload content_id if video failed)
    feedback_content_id = video_content_id or content_id
    if feedback_content_id:
        results["feedback"] = test_feedback_flow(token, feedback_content_id, username)
    else:
        results["feedback"] = False
    
    # 5. Analytics
    results["analytics"] = test_analytics_flow()
    
    # 6. Direct Integrations
    results["direct_integrations"] = test_direct_integrations()
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print()
    print("=== Integration Test Results ===")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    print()
    print(f"Overall: {passed_tests}/{total_tests} tests passed")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Duration: {duration:.1f} seconds")
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] All integrations working perfectly!")
        print("✓ Sentry error tracking active")
        print("✓ PostHog analytics tracking active") 
        print("✓ Supabase database operations working")
        print("✓ All endpoints integrated with observability")
    else:
        print(f"\n[WARNING] {total_tests - passed_tests} integration(s) need attention")
    
    # Save comprehensive report
    report = {
        "timestamp": time.time(),
        "duration": duration,
        "test_results": results,
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests/total_tests)*100
        },
        "test_user": {
            "username": username,
            "content_created": bool(content_id),
            "video_generated": bool(video_content_id)
        }
    }
    
    try:
        os.makedirs("data/reports", exist_ok=True)
        with open("data/reports/full_integration_test.json", "w") as f:
            json.dump(report, f, indent=2)
        print("\n[SAVED] Full report saved to data/reports/full_integration_test.json")
    except Exception as e:
        print(f"\n[FAIL] Failed to save report: {e}")

if __name__ == "__main__":
    main()
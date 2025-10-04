#!/usr/bin/env python3
"""
Test PostHog events to verify dashboard integration
"""

import os
import posthog
import time
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

def test_posthog_events():
    """Send test events to PostHog"""
    
    api_key = os.getenv("POSTHOG_API_KEY")
    if not api_key:
        print("ERROR: POSTHOG_API_KEY not found")
        return
    
    # Initialize PostHog
    posthog.api_key = api_key
    posthog.host = 'https://app.posthog.com'
    
    print(f"Sending test events to PostHog...")
    print(f"API Key: {api_key[:10]}...")
    
    # Test events
    test_user_id = f"test_user_{int(time.time())}"
    
    try:
        # Event 1: User registration
        posthog.capture(
            distinct_id=test_user_id,
            event='user_registered',
            properties={
                'username': 'test_user',
                'source': 'ai_agent_test',
                'timestamp': datetime.now().isoformat()
            }
        )
        print("[OK] Sent: user_registered")
        
        # Event 2: Content upload
        posthog.capture(
            distinct_id=test_user_id,
            event='content_uploaded',
            properties={
                'content_type': 'video',
                'file_size': 1024000,
                'source': 'ai_agent_test'
            }
        )
        print("[OK] Sent: content_uploaded")
        
        # Event 3: Video generation
        posthog.capture(
            distinct_id=test_user_id,
            event='video_generated',
            properties={
                'duration': 30.5,
                'success': True,
                'resolution': '1920x1080'
            }
        )
        print("[OK] Sent: video_generated")
        
        # Event 4: Feedback
        posthog.capture(
            distinct_id=test_user_id,
            event='feedback_submitted',
            properties={
                'rating': 5,
                'sentiment': 'positive',
                'content_id': 'test_content_123'
            }
        )
        print("[OK] Sent: feedback_submitted")
        
        # Identify user
        posthog.identify(
            distinct_id=test_user_id,
            properties={
                'email': 'test@example.com',
                'name': 'Test User',
                'plan': 'free'
            }
        )
        print("[OK] Sent: user_identify")
        
        print(f"\n[SUCCESS] Successfully sent 5 test events!")
        print(f"User ID: {test_user_id}")
        print(f"Check dashboard: https://app.posthog.com")
        print(f"Events may take 1-2 minutes to appear")
        
    except Exception as e:
        print(f"[ERROR] Error sending events: {e}")

if __name__ == "__main__":
    test_posthog_events()
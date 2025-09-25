#!/usr/bin/env python3
"""
PostHog Analytics Integration for AI Agent
"""

import os
import posthog
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PostHogAnalytics:
    def __init__(self):
        self.api_key = os.getenv("POSTHOG_API_KEY")
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            posthog.api_key = self.api_key
            posthog.host = 'https://app.posthog.com'
            logger.info("PostHog analytics enabled")
        else:
            logger.warning("PostHog API key not found - analytics disabled")
    
    def track_event(self, user_id: str, event: str, properties: Dict[str, Any] = None):
        """Track an event in PostHog"""
        if not self.enabled:
            return
        
        try:
            posthog.capture(
                distinct_id=user_id,
                event=event,
                properties=properties or {}
            )
        except Exception as e:
            logger.error(f"PostHog tracking failed: {e}")
    
    def identify_user(self, user_id: str, properties: Dict[str, Any] = None):
        """Identify a user in PostHog"""
        if not self.enabled:
            return
        
        try:
            posthog.identify(
                distinct_id=user_id,
                properties=properties or {}
            )
        except Exception as e:
            logger.error(f"PostHog identify failed: {e}")

# Global analytics instance
analytics = PostHogAnalytics()

# Event tracking functions
def track_user_registration(user_id: str, username: str):
    analytics.track_event(user_id, "user_registered", {
        "username": username,
        "source": "ai_agent"
    })

def track_content_upload(user_id: str, content_type: str, file_size: int):
    analytics.track_event(user_id, "content_uploaded", {
        "content_type": content_type,
        "file_size": file_size
    })

def track_video_generation(user_id: str, duration: float, success: bool):
    analytics.track_event(user_id, "video_generated", {
        "duration": duration,
        "success": success
    })

def track_feedback(user_id: str, content_id: str, rating: int, sentiment: str):
    analytics.track_event(user_id, "feedback_submitted", {
        "content_id": content_id,
        "rating": rating,
        "sentiment": sentiment
    })
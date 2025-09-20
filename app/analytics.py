#!/usr/bin/env python3
"""
Analytics endpoints for BHIV platform
"""

from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, Optional
import time
import sqlite3

router = APIRouter(prefix="/bhiv", tags=["STEP 6: BHIV Analytics"])

# Database connection
DB_PATH = 'data.db'

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@router.get("/analytics")
async def get_bhiv_analytics() -> Dict[str, Any]:
    """STEP 6C: Get comprehensive BHIV analytics with sentiment and engagement data"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get basic stats
        cur.execute('SELECT COUNT(*) FROM contents')
        total_content = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM users')
        total_users = cur.fetchone()[0]
        
        # Get average rating
        cur.execute('SELECT AVG((reward * 2) + 3) FROM feedback WHERE reward IS NOT NULL')
        avg_rating = cur.fetchone()[0] or 0.0
        
        # Get sentiment breakdown (simulated)
        cur.execute('SELECT event_type, COUNT(*) FROM feedback GROUP BY event_type')
        sentiment_rows = cur.fetchall()
        sentiment_breakdown = {}
        for event_type, count in sentiment_rows:
            if event_type == 'like':
                sentiment_breakdown['positive'] = count
            elif event_type == 'dislike':
                sentiment_breakdown['negative'] = count
            else:
                sentiment_breakdown['neutral'] = sentiment_breakdown.get('neutral', 0) + count
        
        # Get content type breakdown
        cur.execute('SELECT content_type, COUNT(*) FROM contents GROUP BY content_type')
        content_types = dict(cur.fetchall())
        
        conn.close()
        
        # Calculate engagement metrics
        engagement_rate = (total_feedback / max(total_content, 1)) * 100
        
        analytics_data = {
            "total_content": total_content,
            "total_feedback": total_feedback,
            "total_users": total_users,
            "average_rating": round(avg_rating, 2),
            "engagement_rate": round(engagement_rate, 2),
            "sentiment_breakdown": sentiment_breakdown,
            "content_types": content_types,
            "timestamp": time.time(),
            "formatted_time": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return {
            "status": "success",
            "analytics": analytics_data,
            "next_step": "Use this data for dashboard visualization and insights"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "analytics": {
                "total_content": 0,
                "total_feedback": 0,
                "total_users": 0,
                "average_rating": 0.0,
                "engagement_rate": 0.0,
                "sentiment_breakdown": {"positive": 0, "negative": 0, "neutral": 0},
                "content_types": {},
                "timestamp": time.time(),
                "formatted_time": time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

@router.post("/feedback")
async def enhanced_feedback(
    content_id: str = Form(...),
    user_id: str = Form(...),
    rating: Optional[int] = Form(None),
    comment: Optional[str] = Form(None),
    watch_time_ms: int = Form(0)
) -> Dict[str, Any]:
    """STEP 6D: Enhanced feedback endpoint with sentiment analysis"""
    try:
        # Validate rating
        if rating and not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Simple sentiment analysis
        sentiment = "neutral"
        engagement_score = 0.5
        
        if comment:
            comment_lower = comment.lower()
            positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'awesome']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'poor']
            
            pos_count = sum(1 for word in positive_words if word in comment_lower)
            neg_count = sum(1 for word in negative_words if word in comment_lower)
            
            if pos_count > neg_count:
                sentiment = "positive"
                engagement_score = 0.8
            elif neg_count > pos_count:
                sentiment = "negative"
                engagement_score = 0.3
        
        # Adjust sentiment based on rating
        if rating:
            if rating >= 4:
                sentiment = "positive"
                engagement_score = max(engagement_score, 0.7)
            elif rating <= 2:
                sentiment = "negative"
                engagement_score = min(engagement_score, 0.4)
        
        # Calculate reward
        reward = (rating - 3) / 2.0 if rating else 0.0
        
        # Determine event type
        if rating and rating >= 4:
            event_type = 'like'
        elif rating and rating <= 2:
            event_type = 'dislike'
        else:
            event_type = 'view'
        
        # Store feedback in database
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('INSERT INTO feedback(content_id,user_id,event_type,watch_time_ms,reward,rating,comment,sentiment,engagement_score,timestamp) VALUES (?,?,?,?,?,?,?,?,?,?)',
                   (content_id, user_id, event_type, watch_time_ms, reward, rating, comment, sentiment, engagement_score, time.time()))
        feedback_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "content_id": content_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "sentiment": sentiment,
            "engagement_score": round(engagement_score, 2),
            "reward": reward,
            "event_type": event_type,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "next_step": "GET /bhiv/analytics to see updated analytics data"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }


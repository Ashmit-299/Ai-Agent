"""
Minimal feedback endpoint
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import time

router = APIRouter()

class FeedbackRequest(BaseModel):
    content_id: str
    rating: int
    comment: str = ""

@router.post('/feedback-minimal')
def feedback_minimal(f: FeedbackRequest):
    """Minimal feedback endpoint"""
    try:
        if not (1 <= f.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be 1-5")
        
        # Save to database
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        reward = (f.rating - 3) / 2.0
        event_type = 'like' if f.rating >= 4 else 'view'
        
        cur.execute("""
            INSERT INTO feedback (content_id, user_id, event_type, rating, comment, reward, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (f.content_id, "anonymous", event_type, f.rating, f.comment, reward, time.time()))
        
        feedback_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "rating": f.rating,
            "message": "Feedback saved"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
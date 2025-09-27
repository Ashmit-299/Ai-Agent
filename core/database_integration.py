#!/usr/bin/env python3
"""
Enhanced Database Integration for Supabase Tables
Connects all tables: user, script, videos, systemlogs, feedback, analytics, alembic_version
"""

import os
import time
import json
import logging
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Session, select, func, and_, or_
from core.database import engine, get_session
from core.models import User, Content, Feedback, Script, Analytics, SystemLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIntegration:
    """Enhanced database operations with full table integration"""
    
    def __init__(self):
        self.engine = engine
    
    def create_user_with_analytics(self, user_data: dict) -> User:
        """Create user and log analytics event"""
        with Session(self.engine) as session:
            user = User(**user_data)
            session.add(user)
            session.commit()
            session.refresh(user)
            
            self.log_analytics_event(
                event_type="user_created",
                user_id=user.user_id,
                metadata={"registration_method": "api"}
            )
            
            return user
    
    def create_content_with_relationships(self, content_data: dict, script_data: dict = None) -> Dict[str, Any]:
        """Create content with optional script relationship"""
        with Session(self.engine) as session:
            content = Content(**content_data)
            session.add(content)
            session.flush()
            
            script = None
            if script_data:
                script_data['content_id'] = content.content_id
                script = Script(**script_data)
                session.add(script)
                session.flush()
            
            session.commit()
            session.refresh(content)
            if script:
                session.refresh(script)
            
            return {
                "content": content,
                "script": script,
                "relationships": {
                    "has_script": script is not None,
                    "script_id": script.script_id if script else None
                }
            }
    
    def get_content_with_relationships(self, content_id: str) -> Dict[str, Any]:
        """Get content with all related data"""
        with Session(self.engine) as session:
            content = session.get(Content, content_id)
            if not content:
                return None
            
            script = session.exec(
                select(Script).where(Script.content_id == content_id)
            ).first()
            
            feedback_stats = session.exec(
                select(
                    func.count(Feedback.id),
                    func.avg(Feedback.rating),
                    func.sum(Feedback.watch_time_ms)
                ).where(Feedback.content_id == content_id)
            ).first()
            
            return {
                "content": content,
                "script": script,
                "feedback_stats": {
                    "total_feedback": feedback_stats[0] or 0,
                    "average_rating": round(feedback_stats[1] or 0, 2),
                    "total_watch_time_ms": feedback_stats[2] or 0
                },
                "relationships": {
                    "has_script": script is not None,
                    "has_feedback": (feedback_stats[0] or 0) > 0
                }
            }
    
    def create_feedback_with_analytics(self, feedback_data: dict) -> Feedback:
        """Create feedback and log comprehensive analytics"""
        with Session(self.engine) as session:
            feedback = Feedback(**feedback_data)
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            
            self.log_analytics_event(
                event_type="feedback_submitted",
                user_id=feedback.user_id,
                content_id=feedback.content_id,
                metadata={
                    "rating": feedback.rating,
                    "event_type": feedback.event_type,
                    "reward": feedback.reward
                }
            )
            
            return feedback
    
    def get_content_feedback_analysis(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive feedback analysis for content"""
        with Session(self.engine) as session:
            feedback_list = session.exec(
                select(Feedback).where(Feedback.content_id == content_id)
            ).all()
            
            if not feedback_list:
                return {"content_id": content_id, "feedback_count": 0}
            
            ratings = [f.rating for f in feedback_list if f.rating is not None]
            rating_dist = {i: ratings.count(i) for i in range(1, 6)}
            
            return {
                "content_id": content_id,
                "feedback_count": len(feedback_list),
                "rating_stats": {
                    "average": round(sum(ratings) / len(ratings), 2) if ratings else 0,
                    "distribution": rating_dist,
                    "total_ratings": len(ratings)
                },
                "sentiment_stats": {
                    "distribution": {},
                    "total_sentiments": 0
                }
            }
    
    def log_analytics_event(self, event_type: str, user_id: str = None, content_id: str = None, 
                          metadata: dict = None, ip_address: str = None) -> Analytics:
        """Log analytics event with metadata"""
        try:
            with Session(self.engine) as session:
                analytics = Analytics(
                    event_type=event_type,
                    user_id=user_id,
                    content_id=content_id,
                    event_data=json.dumps(metadata) if metadata else None,
                    timestamp=time.time(),
                    ip_address=ip_address
                )
                session.add(analytics)
                session.commit()
                session.refresh(analytics)
                return analytics
        except Exception as e:
            logger.error(f"Failed to log analytics event: {e}")
            return None
    
    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        with Session(self.engine) as session:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            event_types = session.exec(
                select(Analytics.event_type, func.count(Analytics.id))
                .where(Analytics.timestamp >= cutoff_time)
                .group_by(Analytics.event_type)
            ).all()
            
            daily_events = session.exec(
                select(func.count(Analytics.id))
                .where(Analytics.timestamp >= cutoff_time)
            ).first()
            
            return {
                "period_days": days,
                "total_events": daily_events or 0,
                "event_types": dict(event_types)
            }
    
    def log_system_event(self, level: str, message: str, module: str = None, user_id: str = None) -> SystemLog:
        """Log system event"""
        try:
            with Session(self.engine) as session:
                log_entry = SystemLog(
                    level=level,
                    message=message,
                    module=module,
                    timestamp=time.time(),
                    user_id=user_id
                )
                session.add(log_entry)
                session.commit()
                session.refresh(log_entry)
                return log_entry
        except Exception as e:
            logger.error(f"Failed to log system event: {e}")
            return None
    
    def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics from logs"""
        with Session(self.engine) as session:
            recent_time = time.time() - 3600
            
            log_levels = session.exec(
                select(SystemLog.level, func.count(SystemLog.id))
                .where(SystemLog.timestamp >= recent_time)
                .group_by(SystemLog.level)
            ).all()
            
            total_logs = session.exec(
                select(func.count(SystemLog.id))
                .where(SystemLog.timestamp >= recent_time)
            ).first() or 0
            
            error_logs = session.exec(
                select(func.count(SystemLog.id))
                .where(and_(SystemLog.timestamp >= recent_time, SystemLog.level == "ERROR"))
            ).first() or 0
            
            error_rate = (error_logs / total_logs * 100) if total_logs > 0 else 0
            
            return {
                "period": "last_hour",
                "total_logs": total_logs,
                "log_levels": dict(log_levels),
                "error_rate_percent": round(error_rate, 2),
                "health_status": "healthy" if error_rate < 5 else "warning" if error_rate < 15 else "critical"
            }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data integrating all tables"""
        with Session(self.engine) as session:
            user_count = session.exec(select(func.count(User.user_id))).first() or 0
            content_count = session.exec(select(func.count(Content.content_id))).first() or 0
            script_count = session.exec(select(func.count(Script.script_id))).first() or 0
            feedback_count = session.exec(select(func.count(Feedback.id))).first() or 0
            
            recent_time = time.time() - 86400
            recent_content = session.exec(
                select(func.count(Content.content_id))
                .where(Content.uploaded_at >= recent_time)
            ).first() or 0
            
            avg_rating = session.exec(
                select(func.avg(Feedback.rating))
                .where(Feedback.rating.is_not(None))
            ).first() or 0
            
            health_metrics = self.get_system_health_metrics()
            
            return {
                "overview": {
                    "total_users": user_count,
                    "total_content": content_count,
                    "total_scripts": script_count,
                    "total_feedback": feedback_count,
                    "average_rating": round(avg_rating, 2)
                },
                "recent_activity": {
                    "new_content_24h": recent_content
                },
                "system_health": health_metrics,
                "timestamp": time.time()
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics and health info"""
        with Session(self.engine) as session:
            stats = {}
            
            tables = ['user', 'content', 'script', 'feedback', 'analytics', 'system_logs']
            for table in tables:
                try:
                    if table == 'user':
                        count = session.exec(select(func.count(User.user_id))).first()
                    elif table == 'content':
                        count = session.exec(select(func.count(Content.content_id))).first()
                    elif table == 'script':
                        count = session.exec(select(func.count(Script.script_id))).first()
                    elif table == 'feedback':
                        count = session.exec(select(func.count(Feedback.id))).first()
                    elif table == 'analytics':
                        count = session.exec(select(func.count(Analytics.id))).first()
                    elif table == 'system_logs':
                        count = session.exec(select(func.count(SystemLog.id))).first()
                    
                    stats[f"{table}_count"] = count or 0
                except Exception as e:
                    stats[f"{table}_count"] = f"Error: {str(e)}"
            
            return {
                "table_statistics": stats,
                "database_type": "PostgreSQL" if "postgresql" in str(self.engine.url) else "SQLite",
                "timestamp": time.time()
            }

# Global instance
db_integration = DatabaseIntegration()
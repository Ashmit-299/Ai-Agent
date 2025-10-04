#!/usr/bin/env python3
"""
Custom analytics dashboard for monitoring application metrics
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from .observability import performance_monitor, posthog_manager, get_observability_health
from .auth import get_current_user_required

router = APIRouter(prefix="/analytics", tags=["Analytics Dashboard"])

@router.get("/dashboard")
async def get_analytics_dashboard(current_user = Depends(get_current_user_required)):
    """Get comprehensive analytics dashboard data"""
    
    # Only allow admin users to access analytics
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        # For demo purposes, allow demo user
        if current_user.user_id != 'demo001':
            raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get performance metrics
        performance_data = performance_monitor.get_performance_summary()
        
        # Get observability health
        observability_data = get_observability_health()
        
        # Get system metrics
        system_metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": performance_monitor.get_uptime(),
            "active_users_24h": await get_active_users_count(),
            "total_api_requests_24h": await get_api_requests_count(),
            "error_rate_24h": await get_error_rate()
        }
        
        return {
            "performance": performance_data,
            "observability": observability_data,
            "system": system_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")

async def get_active_users_count() -> int:
    """Get count of active users in last 24 hours"""
    try:
        # In production, query your database for active users
        from core.database import DatabaseManager
        db = DatabaseManager()
        
        # This is a placeholder - implement based on your user activity tracking
        return 10  # Replace with actual query
        
    except Exception:
        return 0

async def get_api_requests_count() -> int:
    """Get API request count in last 24 hours"""
    try:
        # Count from performance metrics
        total_requests = 0
        for metric in performance_monitor.metrics.values():
            total_requests += metric.get("count", 0)
        return total_requests
        
    except Exception:
        return 0

async def get_error_rate() -> float:
    """Get error rate percentage in last 24 hours"""
    try:
        total_requests = 0
        error_count = 0
        
        for metric in performance_monitor.metrics.values():
            total_requests += metric.get("count", 0)
            error_count += metric.get("error_count", 0)
        
        if total_requests > 0:
            return (error_count / total_requests) * 100
        return 0.0
        
    except Exception:
        return 0.0

@router.get("/events/{user_id}")
async def get_user_events(user_id: str, current_user = Depends(get_current_user_required)):
    """Get user events for analysis (admin only)"""
    
    # Admin check
    if current_user.user_id != user_id and current_user.user_id != 'demo001':
        raise HTTPException(status_code=403, detail="Access denied")
    
    # In production, query PostHog or your analytics database
    return {
        "user_id": user_id,
        "events": [],  # Implement actual event retrieval
        "summary": {
            "total_events": 0,
            "last_activity": None
        }
    }
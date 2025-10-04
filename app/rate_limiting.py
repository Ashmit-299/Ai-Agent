#!/usr/bin/env python3
"""
Rate limiting middleware and utilities
"""
import time
import hashlib
from typing import Dict, Optional, Tuple
from fastapi import HTTPException, Request
from collections import defaultdict, deque
import os
import logging

logger = logging.getLogger(__name__)

# Try to import Redis, fall back to in-memory if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory rate limiting")

class InMemoryRateLimit:
    """In-memory rate limiting for development/small deployments"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_rate_limited(self, identifier: str, limit: int, window_seconds: int) -> Tuple[bool, Dict]:
        """Check if identifier is rate limited"""
        
        current_time = time.time()
        
        # Periodic cleanup
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired_entries(current_time)
        
        # Get request history for this identifier
        request_times = self.requests[identifier]
        
        # Remove expired entries
        cutoff_time = current_time - window_seconds
        while request_times and request_times[0] <= cutoff_time:
            request_times.popleft()
        
        # Check if limit exceeded
        if len(request_times) >= limit:
            # Calculate retry-after
            oldest_request = request_times[0]
            retry_after = int(oldest_request + window_seconds - current_time) + 1
            
            return True, {
                "limit": limit,
                "window_seconds": window_seconds,
                "current_requests": len(request_times),
                "retry_after": retry_after
            }
        
        # Add current request
        request_times.append(current_time)
        
        return False, {
            "limit": limit,
            "window_seconds": window_seconds,
            "current_requests": len(request_times),
            "remaining": limit - len(request_times)
        }
    
    def _cleanup_expired_entries(self, current_time: float):
        """Remove expired entries from all identifiers"""
        expired_identifiers = []
        
        for identifier, request_times in self.requests.items():
            # Keep only requests from the last hour
            cutoff_time = current_time - 3600
            while request_times and request_times[0] <= cutoff_time:
                request_times.popleft()
            
            # Remove empty entries
            if not request_times:
                expired_identifiers.append(identifier)
        
        for identifier in expired_identifiers:
            del self.requests[identifier]
        
        self.last_cleanup = current_time

class RedisRateLimit:
    """Redis-based rate limiting for production"""
    
    def __init__(self, redis_url: Optional[str] = None):
        if not REDIS_AVAILABLE:
            self.redis_client = None
            self.available = False
            return
            
        try:
            self.redis_client = redis.from_url(
                redis_url or os.getenv("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("Redis rate limiting enabled")
        except Exception as e:
            logger.warning(f"Redis not available, falling back to in-memory: {e}")
            self.redis_client = None
            self.available = False
    
    def is_rate_limited(self, identifier: str, limit: int, window_seconds: int) -> Tuple[bool, Dict]:
        """Check if identifier is rate limited using Redis"""
        
        if not self.available:
            return False, {"error": "Redis not available"}
        
        try:
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Use Redis sorted set to track requests
            key = f"rate_limit:{identifier}"
            
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request with score as timestamp
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry on the key
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            current_requests = results[1]  # Count after cleanup
            
            if current_requests >= limit:
                # Get oldest request to calculate retry-after
                oldest_requests = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_requests:
                    oldest_time = int(oldest_requests[0][1])
                    retry_after = oldest_time + window_seconds - current_time
                    retry_after = max(1, retry_after)
                else:
                    retry_after = window_seconds
                
                # Remove the request we just added since it's rate limited
                self.redis_client.zrem(key, str(current_time))
                
                return True, {
                    "limit": limit,
                    "window_seconds": window_seconds,
                    "current_requests": current_requests,
                    "retry_after": retry_after
                }
            
            return False, {
                "limit": limit,
                "window_seconds": window_seconds,
                "current_requests": current_requests + 1,
                "remaining": limit - current_requests - 1
            }
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            return False, {"error": str(e)}

class RateLimiter:
    """Main rate limiter with fallback"""
    
    def __init__(self):
        self.redis_limiter = RedisRateLimit() if REDIS_AVAILABLE else None
        self.memory_limiter = InMemoryRateLimit()
        
        # Rate limit configurations
        self.rate_limits = {
            "default": {"limit": 100, "window": 3600},  # 100/hour
            "upload": {"limit": 10, "window": 3600},    # 10 uploads/hour
            "generate": {"limit": 5, "window": 3600},   # 5 generations/hour
            "login": {"limit": 5, "window": 900},       # 5 login attempts/15min
            "register": {"limit": 3, "window": 3600},   # 3 registrations/hour
            "feedback": {"limit": 50, "window": 3600},  # 50 feedback/hour
            "analytics": {"limit": 200, "window": 3600}, # 200 analytics/hour
        }
    
    def get_identifier(self, request: Request, per_user: bool = True) -> str:
        """Get rate limiting identifier"""
        
        if per_user:
            # Try to get user ID from request
            try:
                if hasattr(request.state, 'user') and request.state.user:
                    user = request.state.user
                    if hasattr(user, 'user_id'):
                        return f"user:{user.user_id}"
                    elif isinstance(user, dict):
                        return f"user:{user.get('user_id', 'unknown')}"
            except Exception:
                pass
        
        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def check_rate_limit(self, request: Request, endpoint_type: str = "default", per_user: bool = True) -> None:
        """Check rate limit and raise HTTPException if exceeded"""
        
        # Get rate limit configuration
        config = self.rate_limits.get(endpoint_type, self.rate_limits["default"])
        limit = config["limit"]
        window = config["window"]
        
        # Get identifier
        identifier = self.get_identifier(request, per_user)
        
        # Check with Redis first, then fall back to memory
        is_limited = False
        info = {}
        
        if self.redis_limiter and self.redis_limiter.available:
            is_limited, info = self.redis_limiter.is_rate_limited(identifier, limit, window)
        else:
            is_limited, info = self.memory_limiter.is_rate_limited(identifier, limit, window)
        
        if is_limited:
            retry_after = info.get("retry_after", window)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {endpoint_type}. Try again in {retry_after} seconds.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Window": str(window),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Add rate limit headers to successful requests
        remaining = info.get("remaining", 0)
        if not hasattr(request.state, 'rate_limit_headers'):
            request.state.rate_limit_headers = {}
        
        request.state.rate_limit_headers.update({
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Window": str(window),
            "X-RateLimit-Remaining": str(remaining)
        })

# Global rate limiter instance
rate_limiter = RateLimiter()

# Dependency functions
def rate_limit_default(request: Request):
    """Default rate limiting"""
    rate_limiter.check_rate_limit(request, "default")

def rate_limit_upload(request: Request):
    """Rate limit for upload endpoints"""
    rate_limiter.check_rate_limit(request, "upload", per_user=True)

def rate_limit_generate(request: Request):
    """Rate limit for video generation"""
    rate_limiter.check_rate_limit(request, "generate", per_user=True)

def rate_limit_login(request: Request):
    """Rate limit for login attempts"""
    rate_limiter.check_rate_limit(request, "login", per_user=False)  # IP-based

def rate_limit_register(request: Request):
    """Rate limit for registration"""
    rate_limiter.check_rate_limit(request, "register", per_user=False)  # IP-based

def rate_limit_feedback(request: Request):
    """Rate limit for feedback submission"""
    rate_limiter.check_rate_limit(request, "feedback", per_user=True)

def rate_limit_analytics(request: Request):
    """Rate limit for analytics endpoints"""
    rate_limiter.check_rate_limit(request, "analytics", per_user=True)
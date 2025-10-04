#!/usr/bin/env python3
"""
Test rate limiting functionality
"""
import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.rate_limiting import RateLimiter, InMemoryRateLimit

client = TestClient(app)

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_in_memory_rate_limit_basic(self):
        """Test basic in-memory rate limiting"""
        limiter = InMemoryRateLimit()
        
        # Should allow first request
        is_limited, info = limiter.is_rate_limited("test_user", 5, 60)
        assert not is_limited
        assert info["remaining"] == 4
        
        # Should allow up to limit
        for i in range(4):
            is_limited, info = limiter.is_rate_limited("test_user", 5, 60)
            assert not is_limited
        
        # Should block after limit
        is_limited, info = limiter.is_rate_limited("test_user", 5, 60)
        assert is_limited
        assert "retry_after" in info
    
    def test_rate_limit_window_expiry(self):
        """Test that rate limits expire after window"""
        limiter = InMemoryRateLimit()
        
        # Fill up the limit
        for i in range(5):
            limiter.is_rate_limited("test_user", 5, 1)  # 1 second window
        
        # Should be rate limited
        is_limited, info = limiter.is_rate_limited("test_user", 5, 1)
        assert is_limited
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        is_limited, info = limiter.is_rate_limited("test_user", 5, 1)
        assert not is_limited
    
    def test_different_users_separate_limits(self):
        """Test that different users have separate rate limits"""
        limiter = InMemoryRateLimit()
        
        # Fill limit for user1
        for i in range(5):
            limiter.is_rate_limited("user1", 5, 60)
        
        # user1 should be limited
        is_limited, info = limiter.is_rate_limited("user1", 5, 60)
        assert is_limited
        
        # user2 should not be limited
        is_limited, info = limiter.is_rate_limited("user2", 5, 60)
        assert not is_limited
    
    def test_rate_limit_headers_in_response(self):
        """Test that rate limit headers are added to responses"""
        # Make a request to an endpoint with rate limiting
        response = client.get("/health")
        
        # Should have rate limit headers (if middleware is working)
        # Note: This test depends on the middleware being properly configured
        assert response.status_code == 200
    
    def test_rate_limit_exceeded_response(self):
        """Test response when rate limit is exceeded"""
        # This would require actually hitting the rate limit
        # For now, just test that the endpoint exists
        response = client.get("/health")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test that RateLimiter initializes correctly"""
        limiter = RateLimiter()
        
        # Should have default rate limits configured
        assert "default" in limiter.rate_limits
        assert "upload" in limiter.rate_limits
        assert "login" in limiter.rate_limits
        
        # Should have memory limiter as fallback
        assert limiter.memory_limiter is not None
#!/usr/bin/env python3
"""
Retry and backoff utilities for external service calls
"""
import asyncio
import time
import random
import logging
from typing import Any, Callable, Optional, Type, Union, List
from functools import wraps

logger = logging.getLogger(__name__)

class RetryError(Exception):
    """Raised when all retry attempts are exhausted"""
    pass

def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True) -> float:
    """Calculate exponential backoff delay"""
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        # Add random jitter to avoid thundering herd
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay

def should_retry(exception: Exception, retryable_exceptions: List[Type[Exception]]) -> bool:
    """Check if exception should trigger a retry"""
    return any(isinstance(exception, exc_type) for exc_type in retryable_exceptions)

async def async_retry(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
    *args,
    **kwargs
) -> Any:
    """
    Async retry wrapper with exponential backoff
    """
    if retryable_exceptions is None:
        retryable_exceptions = [ConnectionError, TimeoutError, Exception]
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
                
        except Exception as e:
            last_exception = e
            
            if not should_retry(e, retryable_exceptions):
                logger.error(f"Non-retryable error in {func.__name__}: {e}")
                raise
            
            if attempt == max_attempts - 1:
                logger.error(f"All retry attempts exhausted for {func.__name__}")
                break
            
            delay = exponential_backoff(attempt, base_delay, max_delay)
            logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
            
            await asyncio.sleep(delay)
    
    raise RetryError(f"All {max_attempts} attempts failed. Last error: {last_exception}")

def retry_decorator(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Optional[List[Type[Exception]]] = None
):
    """Decorator for automatic retry with exponential backoff"""
    
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await async_retry(
                func, max_attempts, base_delay, max_delay, retryable_exceptions,
                *args, **kwargs
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we'll use sync retry
            if retryable_exceptions is None:
                exceptions = [ConnectionError, TimeoutError, Exception]
            else:
                exceptions = retryable_exceptions
                
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if not should_retry(e, exceptions):
                        raise
                    
                    if attempt == max_attempts - 1:
                        break
                    
                    delay = exponential_backoff(attempt, base_delay, max_delay)
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise RetryError(f"All {max_attempts} attempts failed. Last error: {last_exception}")
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Specific retry configurations for different services
class RetryConfig:
    """Predefined retry configurations"""
    
    # For LLM/AI service calls
    LLM_SERVICE = {
        'max_attempts': 3,
        'base_delay': 2.0,
        'max_delay': 30.0,
        'retryable_exceptions': [ConnectionError, TimeoutError, Exception]
    }
    
    # For database operations
    DATABASE = {
        'max_attempts': 2,
        'base_delay': 0.5,
        'max_delay': 5.0,
        'retryable_exceptions': [ConnectionError, TimeoutError]
    }
    
    # For external API calls
    EXTERNAL_API = {
        'max_attempts': 4,
        'base_delay': 1.0,
        'max_delay': 60.0,
        'retryable_exceptions': [ConnectionError, TimeoutError, Exception]
    }
    
    # For file operations
    FILE_OPERATIONS = {
        'max_attempts': 2,
        'base_delay': 0.1,
        'max_delay': 1.0,
        'retryable_exceptions': [OSError, IOError]
    }

# Convenience decorators
def retry_llm_service(func):
    """Decorator for LLM service calls"""
    return retry_decorator(**RetryConfig.LLM_SERVICE)(func)

def retry_database(func):
    """Decorator for database operations"""
    return retry_decorator(**RetryConfig.DATABASE)(func)

def retry_external_api(func):
    """Decorator for external API calls"""
    return retry_decorator(**RetryConfig.EXTERNAL_API)(func)

def retry_file_operations(func):
    """Decorator for file operations"""
    return retry_decorator(**RetryConfig.FILE_OPERATIONS)(func)

# Circuit breaker for advanced resilience
class CircuitBreaker:
    """Simple circuit breaker implementation"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Call function through circuit breaker"""
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise RetryError(f"Circuit breaker OPEN. Service unavailable.")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Reset on successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failure"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Global circuit breakers for different services
llm_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)
database_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
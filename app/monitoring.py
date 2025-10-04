#!/usr/bin/env python3
"""
Monitoring and error tracking integration
"""

import os
import logging
from typing import Optional

# Sentry integration with fallback
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)

def init_sentry(dsn: Optional[str] = None, environment: str = "development"):
    """Initialize Sentry error tracking"""
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry not available - using fallback error logging")
        return False
    
    sentry_dsn = dsn or os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logger.info("No Sentry DSN provided - error tracking disabled")
        return False
    
    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% of transactions
            environment=environment,
            release=os.getenv("APP_VERSION", "1.0.0"),
        )
        logger.info(f"Sentry initialized for environment: {environment}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False

def capture_exception(error: Exception, extra_data: dict = None):
    """Capture exception with Sentry or fallback logging"""
    if SENTRY_AVAILABLE:
        try:
            if extra_data:
                sentry_sdk.set_extra("additional_data", extra_data)
            sentry_sdk.capture_exception(error)
        except Exception:
            # Fallback to logging if Sentry fails
            logger.exception(f"Error captured: {error}")
            if extra_data:
                logger.error(f"Additional data: {extra_data}")
    else:
        # Fallback logging
        logger.exception(f"Error captured: {error}")
        if extra_data:
            logger.error(f"Additional data: {extra_data}")

def capture_message(message: str, level: str = "info", extra_data: dict = None):
    """Capture message with Sentry or fallback logging"""
    if SENTRY_AVAILABLE:
        try:
            if extra_data:
                sentry_sdk.set_extra("additional_data", extra_data)
            sentry_sdk.capture_message(message, level=level)
        except Exception:
            # Fallback to logging
            getattr(logger, level, logger.info)(f"Message: {message}")
            if extra_data:
                logger.info(f"Additional data: {extra_data}")
    else:
        # Fallback logging
        getattr(logger, level, logger.info)(f"Message: {message}")
        if extra_data:
            logger.info(f"Additional data: {extra_data}")

class ErrorTracker:
    """Error tracking utility class"""
    
    def __init__(self):
        self.sentry_enabled = init_sentry()
    
    def track_error(self, error: Exception, context: dict = None):
        """Track error with context"""
        capture_exception(error, context)
    
    def track_performance(self, operation: str, duration: float, success: bool = True):
        """Track performance metrics"""
        data = {
            "operation": operation,
            "duration_ms": duration * 1000,
            "success": success
        }
        
        if success:
            capture_message(f"Operation completed: {operation}", "info", data)
        else:
            capture_message(f"Operation failed: {operation}", "warning", data)
    
    def track_user_action(self, user_id: str, action: str, metadata: dict = None):
        """Track user actions for analytics"""
        data = {
            "user_id": user_id,
            "action": action,
            "metadata": metadata or {}
        }
        capture_message(f"User action: {action}", "info", data)

# Global error tracker instance
error_tracker = ErrorTracker()

# Structured logging configuration
def setup_structured_logging():
    """Setup structured logging with JSON format"""
    import json
    from datetime import datetime
    
    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_entry)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add structured handler
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(handler)
    
    return root_logger

# Performance monitoring decorator
def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_tracker.track_error(e, {"operation": operation_name})
                raise
            finally:
                duration = time.time() - start_time
                error_tracker.track_performance(operation_name, duration, success)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_tracker.track_error(e, {"operation": operation_name})
                raise
            finally:
                duration = time.time() - start_time
                error_tracker.track_performance(operation_name, duration, success)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
#!/usr/bin/env python3
"""
Structured logging configuration
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any

# Create logs directory
os.makedirs('logs', exist_ok=True)

class StructuredFormatter(logging.Formatter):
    """JSON structured logging formatter"""
    
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

def setup_logging():
    """Setup structured logging"""
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with structured format
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler for app logs
    try:
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    except Exception:
        pass  # Continue without file logging if it fails
    
    # Security logger
    security_logger = logging.getLogger('security')
    try:
        security_handler = logging.FileHandler('logs/security.log')
        security_handler.setFormatter(StructuredFormatter())
        security_logger.addHandler(security_handler)
    except Exception:
        pass
    
    # RL Agent logger
    rl_logger = logging.getLogger('rl_agent')
    
    return root_logger, security_logger, rl_logger

def log_security_event(event_type: str, details: Dict[str, Any], client_ip: str = "unknown"):
    """Log security events"""
    security_logger = logging.getLogger('security')
    event_data = {
        "event_type": event_type,
        "client_ip": client_ip,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    security_logger.info(json.dumps(event_data))
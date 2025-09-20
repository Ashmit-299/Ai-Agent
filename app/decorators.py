#!/usr/bin/env python3
"""
Error handling decorators for BHIV Core pipeline operations
"""

import functools
import time
import traceback
import json
from typing import Dict, Any, Callable
from datetime import datetime

def safe_job(operation_name: str = None, retry_count: int = 0):
    """
    Decorator for safe job execution with standardized error handling
    
    Args:
        operation_name: Name of the operation for logging
        retry_count: Number of retries on failure (0 = no retry)
    
    Returns:
        Standardized response dict with success/error status
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            for attempt in range(retry_count + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful operation
                    _log_operation_result(op_name, "success", {
                        "duration_seconds": round(time.time() - start_time, 3),
                        "attempt": attempt + 1,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    })
                    
                    # Return standardized success response
                    if isinstance(result, dict):
                        result["operation_status"] = "success"
                        result["operation_name"] = op_name
                        return result
                    else:
                        return {
                            "operation_status": "success",
                            "operation_name": op_name,
                            "result": result
                        }
                        
                except Exception as e:
                    error_details = {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "attempt": attempt + 1,
                        "max_attempts": retry_count + 1,
                        "duration_seconds": round(time.time() - start_time, 3),
                        "traceback": traceback.format_exc()
                    }
                    
                    # Log failed attempt
                    _log_operation_result(op_name, "error", error_details)
                    
                    # If this is the last attempt, return error response
                    if attempt == retry_count:
                        return {
                            "operation_status": "error",
                            "operation_name": op_name,
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "attempts": retry_count + 1,
                            "duration_seconds": round(time.time() - start_time, 3)
                        }
                    
                    # Wait before retry (exponential backoff)
                    if attempt < retry_count:
                        time.sleep(0.5 * (2 ** attempt))
            
        return wrapper
    return decorator

def _log_operation_result(operation_name: str, status: str, details: Dict[str, Any]):
    """Log operation result to bucket logs"""
    try:
        import bhiv_bucket
        
        log_entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "operation": operation_name,
            "status": status,
            "details": details
        }
        
        # Create log filename with date
        log_date = datetime.now().strftime("%Y%m%d")
        log_filename = f"bhiv_operations_{log_date}.log"
        
        # Append to log file
        log_path = bhiv_bucket.get_bucket_path("logs", log_filename)
        
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception:
            # Fallback to bucket save_log if append fails
            try:
                existing_content = ""
                if bhiv_bucket.STORAGE_BACKEND == "local":
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            existing_content = f.read()
                    except FileNotFoundError:
                        pass
                
                new_content = existing_content + json.dumps(log_entry, ensure_ascii=False) + '\n'
                bhiv_bucket.save_log(new_content, log_filename)
            except Exception:
                pass  # Don't fail operation due to logging errors
                
    except Exception:
        pass  # Don't fail operation due to logging errors

def archive_failure(operation_type: str, error: str, metadata: Dict[str, Any]):
    """Archive operation failure for debugging"""
    try:
        import os
        
        failure_record = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "operation_type": operation_type,
            "error": error,
            "metadata": metadata
        }
        
        # Save to reports/failed_operations
        os.makedirs("reports/failed_operations", exist_ok=True)
        filename = f"{operation_type}_failed_{int(time.time())}_{hash(error) % 10000}.json"
        filepath = f"reports/failed_operations/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(failure_record, f, indent=2)
            
    except Exception:
        pass  # Don't fail on archival failure
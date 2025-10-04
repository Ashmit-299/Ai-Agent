#!/usr/bin/env python3
"""
BHIV LM Client - LLM Interface for Adaptive Storyboard Enhancement
Provides async API client methods for LLM-powered storyboard suggestion and improvement.
Falls back to local heuristics when LLM service is unavailable.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
import httpx
from datetime import datetime
from app.decorators import safe_job

# Optional tenacity import with fallback
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    # Fallback decorator that doesn't retry
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    stop_after_attempt = wait_exponential = retry_if_exception_type = lambda x: x

class LMError(Exception):
    pass

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration from environment variables
BHIV_LM_URL = os.getenv("BHIV_LM_URL", "http://localhost:8001")
API_KEY = os.getenv("BHIV_LM_API_KEY", "demo_api_key_123")
REQUEST_TIMEOUT = int(os.getenv("BHIV_LM_TIMEOUT", "30"))

async def call_lm_async(prompt: str, timeout: int = 30) -> dict:
    """Call LM API with retries and backoff"""
    if TENACITY_AVAILABLE:
        return await _call_lm_with_retry(prompt, timeout)
    else:
        return await _call_lm_simple(prompt, timeout)

if TENACITY_AVAILABLE:
    @retry(retry=retry_if_exception_type(LMError),
           stop=stop_after_attempt(5),
           wait=wait_exponential(multiplier=1, min=1, max=30),
           reraise=True)
    async def _call_lm_with_retry(prompt: str, timeout: int = 30) -> dict:
        """Call LM API with tenacity retries"""
        return await _call_lm_simple(prompt, timeout)
else:
    async def _call_lm_with_retry(prompt: str, timeout: int = 30) -> dict:
        """Call LM API without retries (fallback)"""
        return await _call_lm_simple(prompt, timeout)

async def _call_lm_simple(prompt: str, timeout: int = 30) -> dict:
    """Simple LM API call without retries"""
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(BHIV_LM_URL, json={"prompt": prompt}, headers=headers)
            if resp.status_code == 429:
                raise LMError("rate_limited")
            if resp.status_code >= 500:
                raise LMError("server_error")
            if resp.status_code != 200:
                raise LMError(f"unexpected_status_{resp.status_code}")
            return resp.json()
    except Exception as e:
        if not isinstance(e, LMError):
            raise LMError(f"api_error: {e}")
        raise

async def suggest_storyboard(script_text: str) -> Dict[str, Any]:
    """
    Call BHIV LLM API for storyboard suggestion or fallback to local heuristic
    """
    try:
        if not BHIV_LM_URL:
            return await _fallback_suggest_storyboard(script_text)
        
        result = await call_lm_async(f"Generate storyboard for: {script_text}")
        await _log_lm_interaction("suggest_storyboard", "success", {
            "script_length": len(script_text),
            "response_scenes": len(result.get("scenes", []))
        })
        return result
                
    except (httpx.TimeoutException, LMError):
        await _log_lm_interaction("suggest_storyboard", "timeout", {"fallback_used": True})
        return await _fallback_suggest_storyboard(script_text)
    except Exception as e:
        await _log_lm_interaction("suggest_storyboard", "error", {
            "error": str(e),
            "fallback_used": True
        })
        return await _fallback_suggest_storyboard(script_text)

async def improve_storyboard(storyboard_json: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send storyboard + user feedback to LLM for improvement or use local heuristic
    """
    try:
        if not BHIV_LM_URL:
            return await _fallback_improve_storyboard(storyboard_json, feedback)
        
        prompt = f"Improve storyboard based on feedback: {feedback}"
        result = await call_lm_async(prompt)
        await _log_lm_interaction("improve_storyboard", "success", {
            "original_scenes": len(storyboard_json.get("scenes", [])),
            "improved_scenes": len(result.get("scenes", [])),
            "feedback_rating": feedback.get("rating", 0)
        })
        return result
                
    except (httpx.TimeoutException, LMError):
        await _log_lm_interaction("improve_storyboard", "timeout", {"fallback_used": True})
        return await _fallback_improve_storyboard(storyboard_json, feedback)
    except Exception as e:
        await _log_lm_interaction("improve_storyboard", "error", {
            "error": str(e),
            "fallback_used": True
        })
        return await _fallback_improve_storyboard(storyboard_json, feedback)

async def _fallback_suggest_storyboard(script_text: str) -> Dict[str, Any]:
    """
    Local heuristic fallback for storyboard suggestion
    """
    try:
        from video.storyboard import generate_storyboard_from_text
        
        loop = asyncio.get_event_loop()
        storyboard = await loop.run_in_executor(
            None, 
            generate_storyboard_from_text, 
            script_text
        )
        
        storyboard["generation_method"] = "local_heuristic"
        storyboard["llm_enhanced"] = False
        
        return storyboard
        
    except Exception as e:
        return {
            "version": "1.0",
            "generation_method": "minimal_fallback",
            "llm_enhanced": False,
            "total_duration": 10.0,
            "scenes": [
                {
                    "id": "scene_1",
                    "start_time": 0,
                    "duration": 10.0,
                    "frames": [
                        {
                            "id": "frame_1_1",
                            "text": script_text[:200] if script_text else "Content unavailable",
                            "background_color": "#000000",
                            "text_position": "center"
                        }
                    ]
                }
            ]
        }

async def _fallback_improve_storyboard(storyboard_json: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Local heuristic fallback for storyboard improvement
    """
    try:
        improved_storyboard = storyboard_json.copy()
        rating = feedback.get("rating", 3)
        
        if rating <= 2:
            for scene in improved_storyboard.get("scenes", []):
                scene["duration"] = min(scene.get("duration", 5.0) * 1.2, 8.0)
            
            improved_storyboard["total_duration"] = sum(
                scene.get("duration", 5.0) for scene in improved_storyboard.get("scenes", [])
            )
            
        elif rating >= 4:
            for scene in improved_storyboard.get("scenes", []):
                scene["duration"] = max(scene.get("duration", 5.0) * 0.9, 3.0)
            
            improved_storyboard["total_duration"] = sum(
                scene.get("duration", 5.0) for scene in improved_storyboard.get("scenes", [])
            )
        
        improved_storyboard["generation_method"] = "local_heuristic_improved"
        improved_storyboard["llm_enhanced"] = False
        improved_storyboard["improvement_applied"] = True
        improved_storyboard["feedback_rating"] = rating
        
        return improved_storyboard
        
    except Exception as e:
        storyboard_json["improvement_error"] = str(e)
        return storyboard_json

async def _log_lm_interaction(operation: str, status: str, metadata: Dict[str, Any]):
    """
    Log LLM interaction for monitoring and debugging
    """
    try:
        import bhiv_bucket
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "status": status,
            "metadata": metadata,
            "llm_url": BHIV_LM_URL or "not_configured",
            "api_key_configured": bool(API_KEY and API_KEY != "default_api_key")
        }
        
        log_date = datetime.now().strftime("%Y%m%d")
        log_filename = f"bhiv_lm_{log_date}.log"
        log_path = bhiv_bucket.get_bucket_path("logs", log_filename)
        
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception:
            bhiv_bucket.save_log(json.dumps(log_entry, ensure_ascii=False), log_filename)
        
    except Exception as e:
        print(f"Warning: Failed to log LM interaction {operation}: {e}")

def is_llm_configured() -> bool:
    """Check if LLM service is properly configured"""
    return bool(BHIV_LM_URL and API_KEY and API_KEY not in ["default_api_key", "demo_api_key_123"])

def get_llm_config() -> Dict[str, Any]:
    """Get current LLM configuration (without sensitive data)"""
    return {
        "llm_url_configured": bool(BHIV_LM_URL),
        "api_key_configured": bool(API_KEY and API_KEY != "default_api_key"),
        "timeout_seconds": REQUEST_TIMEOUT,
        "fallback_enabled": True
    }
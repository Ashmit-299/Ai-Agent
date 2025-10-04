#!/usr/bin/env python3
"""
BHIV Core Orchestrator Layer
Single integration point for storage bucket, storyboard generation, video rendering, and event logging.
"""

import uuid
import json
import time
import os
import logging
import sqlite3
import threading
import tempfile
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import bucket storage functions
from . import bhiv_bucket
from .bhiv_bucket import (
    save_script, save_storyboard, save_video, save_log, get_bucket_path,
    save_rating, get_script, get_storyboard, get_video_bytes, save_json, save_text
)

# Import video processing functions
from video.storyboard import generate_storyboard_from_text, validate_storyboard
from video.generator import render_video_from_storyboard

# Import LM client for LLM-enhanced processing
from . import bhiv_lm_client

# Import decorators for error handling
from app.decorators import safe_job

# Path to sqlite DB used by the project
ROOT_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")

def _get_db_conn():
    """Return sqlite3 connection and ensure ratings table exists."""
    conn = sqlite3.connect(ROOT_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id TEXT NOT NULL,
        rating INTEGER,
        user_id TEXT,
        comment TEXT,
        created_at INTEGER
    )""")
    conn.commit()
    return conn

async def _run_blocking(fn, *args, **kwargs):
    """Run blocking function in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fn, *args, **kwargs)

async def process_script_upload_async(file_path: Optional[str] = None,
                                      script_text: Optional[str] = None,
                                      content_id: Optional[str] = None,
                                      uploader: Optional[str] = None) -> Dict[str, Any]:
    """
    Async wrapper that schedules the pipeline. This should NOT block.
    It will start job in background and return job meta.
    """
    # quick validation
    if not (file_path or script_text):
        return {"status": "error", "reason": "no_input"}

    # create a lightweight job record
    job_id = f"job_{int(time.time()*1000)}"
    # schedule heavy work and store task reference
    task = asyncio.create_task(_process_script_pipeline(file_path, script_text, content_id, uploader, job_id))
    # Don't await here to keep it non-blocking, but ensure proper cleanup
    task.add_done_callback(lambda t: logger.info(f"Pipeline task {job_id} completed"))
    return {"status": "enqueued", "job_id": job_id, "task_id": id(task)}

async def _process_script_pipeline(file_path, script_text, content_id, uploader, job_id):
    """Background pipeline processing"""
    try:
        # run blocking script->storyboard->render steps in thread
        result = await _run_blocking(_blocking_pipeline, file_path, script_text, content_id, uploader)
        logger.info("Pipeline finished job=%s result=%s", job_id, result)
        return result
    except asyncio.CancelledError:
        logger.info("Pipeline cancelled for job=%s", job_id)
        raise
    except Exception:
        logger.exception("Pipeline failed for job=%s", job_id)
        raise

def _blocking_pipeline(file_path, script_text, content_id, uploader):
    """Synchronous pipeline implementation"""
    if not content_id:
        content_id = uuid.uuid4().hex[:12]
    
    # Handle script input
    if script_text:
        # Create temp file from script text
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(script_text)
            file_path = f.name
    
    try:
        # Save script
        script_name = f"{content_id}_script.txt"
        script_bucket_path = save_script(file_path, dest_name=script_name)
        
        # Read script content
        with open(file_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Generate storyboard (fallback to local)
        from video.storyboard import generate_storyboard_from_text
        storyboard = generate_storyboard_from_text(script_content)
        
        # Save storyboard
        storyboard_filename = f"{content_id}_storyboard.json"
        save_storyboard(storyboard, storyboard_filename)
        
        return {"ok": True, "content_id": content_id}
    finally:
        # Clean up temp file if created
        if script_text and file_path:
            try:
                os.unlink(file_path)
            except:
                pass

@safe_job("script_upload_pipeline", retry_count=1)
async def process_script_upload(script_local_path: str, uploader_id: str = None, title: str = None) -> Dict[str, Any]:
    """
    Orchestrate complete script-to-video pipeline
    """
    content_id = uuid.uuid4().hex[:12]
    timestamp = time.time()
    
    try:
        # Step 1: Save script to bucket
        script_name = f"{content_id}_script.txt"
        script_bucket_path = save_script(script_local_path, dest_name=script_name)
        
        # Read script content for storyboard generation
        with open(script_local_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Step 2: Generate storyboard from script content
        try:
            storyboard = await bhiv_lm_client.suggest_storyboard(script_content)
        except Exception as e:
            logger.warning(f"LLM storyboard generation failed: {e}, using fallback")
            # Fallback to local generation
            from video.storyboard import generate_storyboard_from_text
            storyboard = generate_storyboard_from_text(script_content)
        
        # Validate storyboard
        if not validate_storyboard(storyboard):
            raise ValueError("Generated storyboard failed validation")
        
        # Step 3: Save storyboard to bucket
        storyboard_filename = f"{content_id}_storyboard.json"
        storyboard_bucket_path = save_storyboard(storyboard, storyboard_filename)
        
        # Step 4: Render video from storyboard
        video_filename = f"{content_id}.mp4"
        video_bucket_path = render_video_from_storyboard(storyboard, video_filename)
        
        # Create metadata
        metadata = {
            "content_id": content_id,
            "uploader_id": uploader_id or "anonymous",
            "title": title or f"Generated Content {content_id}",
            "timestamp": timestamp,
            "created_at": datetime.fromtimestamp(timestamp).isoformat(),
            "paths": {
                "script": script_bucket_path,
                "storyboard": storyboard_bucket_path,
                "video": video_bucket_path
            },
            "storyboard_stats": {
                "total_scenes": len(storyboard.get("scenes", [])),
                "total_duration": storyboard.get("total_duration", 10.0),
                "version": storyboard.get("version", "1.0")
            },
            "processing_status": "completed"
        }
        
        # Write JSON metadata to bucket/logs/<id>.json as per Day 2 requirements
        try:
            metadata_filename = f"{content_id}.json"
            save_json("logs", metadata_filename, metadata)
        except Exception as e:
            print(f"Warning: Failed to save metadata to bucket/logs/{content_id}.json: {e}")
        
        # Also log to daily log file for debugging
        log_processing_event(content_id, "script_upload_completed", metadata)
        return metadata
        
    except Exception as e:
        error_metadata = {
            "content_id": content_id,
            "uploader_id": uploader_id,
            "timestamp": timestamp,
            "error": str(e),
            "processing_status": "failed"
        }
        
        # Write error metadata to bucket/logs/<id>.json as per Day 2 requirements
        try:
            metadata_filename = f"{content_id}.json"
            save_json("logs", metadata_filename, error_metadata)
        except Exception as save_error:
            print(f"Warning: Failed to save error metadata to bucket/logs/{content_id}.json: {save_error}")
        
        # Also log to daily log file for debugging
        log_processing_event(content_id, "script_upload_failed", error_metadata)
        raise ValueError(f"Script processing failed for {content_id}: {e}")

def log_processing_event(content_id: str, event_type: str, metadata: Dict[str, Any]):
    """
    Log processing events to bucket/logs/
    """
    try:
        log_entry = {
            "content_id": content_id,
            "event_type": event_type,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        log_date = datetime.now().strftime("%Y%m%d")
        log_filename = f"bhiv_core_{log_date}.log"
        log_path = get_bucket_path("logs", log_filename)
        
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception:
            save_log(json.dumps(log_entry, ensure_ascii=False), log_filename)
        
    except Exception as e:
        print(f"Warning: Failed to log event {event_type} for {content_id}: {e}")

def get_content_metadata(content_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve content metadata from logs - first try per-ID JSON file, then daily logs
    """
    try:
        # First try to read from per-ID JSON file (Day 2 requirement)
        try:
            metadata_filename = f"{content_id}.json"
            metadata_path = get_bucket_path("logs", metadata_filename)
            if Path(metadata_path).exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Fallback to daily log files
        for days_back in range(7):
            log_date = datetime.fromtimestamp(time.time() - days_back * 86400).strftime("%Y%m%d")
            log_filename = f"bhiv_core_{log_date}.log"
            log_path = get_bucket_path("logs", log_filename)
            
            if Path(log_path).exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line.strip())
                                if (entry.get("content_id") == content_id and 
                                    entry.get("event_type") in ["script_upload_completed", "video_upload_completed"]):
                                    return entry.get("metadata")
                            except:
                                continue
        return None
        
    except Exception as e:
        print(f"Warning: Failed to retrieve metadata for {content_id}: {e}")
        return None

def notify_on_rate(content_id: str, rating_payload: Dict[str, Any], regen_threshold: int = 2) -> Dict[str, Any]:
    """
    Persist rating (bucket + sqlite), compute aggregate, and optionally trigger regeneration.
    rating_payload example: {"rating": 1, "user_id": "u1", "comment": "too fast"}
    """
    # parse rating
    try:
        rating = int(rating_payload.get("rating", 0))
    except Exception:
        rating = 0

    user_id = rating_payload.get("user_id")
    comment = rating_payload.get("comment")
    ts = int(time.time())
    
    # Analyze sentiment and engagement
    sentiment = "neutral"
    engagement_score = 0.5
    try:
        from .sentiment_analyzer import analyzer
        sentiment, engagement_score = analyzer.analyze_sentiment(comment or "", rating)
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
    
    # Always trigger storyboard improvement via LM client
    improvement_result = {"status": "processing", "method": "lm_client"}
    try:
        import asyncio
        from . import bhiv_lm_client
        
        # Create mock storyboard if none exists
        storyboard = get_storyboard(content_id)
        if not storyboard:
            storyboard = {
                "scenes": [{"text": "Generated content", "duration": 5.0}],
                "total_duration": 5.0,
                "version": "1.0"
            }
        
        feedback_data = {
            "rating": rating,
            "user_id": user_id,
            "comment": comment,
            "timestamp": ts
        }
        
        # Call improve_storyboard with proper async handling
        try:
            import concurrent.futures
            
            def run_improve_storyboard():
                return asyncio.run(bhiv_lm_client.improve_storyboard(storyboard, feedback_data))
            
            # Run in thread pool to avoid event loop conflicts
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_improve_storyboard)
                improved_storyboard = future.result(timeout=30)
                
        except Exception as async_error:
            logger.warning(f"Storyboard improvement failed: {async_error}")
            improved_storyboard = {"improvement_applied": False, "error": str(async_error)}
        
        # Process improved storyboard result
        if improved_storyboard and isinstance(improved_storyboard, dict):
            if improved_storyboard.get("improvement_applied"):
                try:
                    storyboard_filename = f"{content_id}_storyboard_improved.json"
                    save_storyboard(improved_storyboard, storyboard_filename)
                    improvement_result = {"status": "improved", "method": "lm_client", "changes": improved_storyboard.get("changes", [])}
                except Exception as save_error:
                    improvement_result = {"status": "processed", "method": "lm_client", "message": f"Improvement generated but save failed: {save_error}"}
            elif improved_storyboard.get("error"):
                improvement_result = {"status": "error", "method": "lm_client", "error": improved_storyboard["error"]}
            else:
                improvement_result = {"status": "analyzed", "method": "lm_client", "message": "No improvements needed"}
        else:
            improvement_result = {"status": "processed", "method": "lm_client", "message": "Storyboard processed successfully"}
            
    except Exception as e:
        logger.exception("Failed to improve storyboard for %s: %s", content_id, e)
        improvement_result = {"status": "error", "error": str(e), "method": "lm_client"}

    # persist to bucket (for raw traceability)
    try:
        rating_filename = f"{content_id}_{ts}.json"
        save_rating({
            "content_id": content_id,
            "rating": rating,
            "user_id": user_id,
            "comment": comment,
            "sentiment": sentiment,
            "engagement_score": engagement_score,
            "ts": ts
        }, rating_filename)
    except Exception:
        logger.exception("Failed to save rating to bucket for content=%s", content_id)

    # persist to sqlite and compute aggregates
    conn = _get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ratings (content_id, rating, user_id, comment, created_at) VALUES (?, ?, ?, ?, ?)",
            (content_id, rating, user_id, comment, ts)
        )
        conn.commit()

        cur.execute("SELECT AVG(rating) as avg_rating, COUNT(*) as cnt FROM ratings WHERE content_id = ?", (content_id,))
        row = cur.fetchone()
        avg_rating = row["avg_rating"] if row and row["avg_rating"] is not None else None
        total = row["cnt"] if row else 0

        logger.info("Saved rating for %s: rating=%s avg=%s count=%s", content_id, rating, avg_rating, total)
    except Exception:
        logger.exception("Failed to persist rating to sqlite for content=%s", content_id)
        avg_rating = None
        total = 0
    finally:
        conn.close()

    # Always check regeneration logic
    regen_triggered = False
    regen_mode = None
    try:
        if rating and rating <= regen_threshold:
            # Prefer to enqueue via app.task_queue.enqueue if available
            try:
                # import dynamically to avoid circular imports at module load time
                from importlib import import_module
                tq = import_module("app.task_queue")
                if hasattr(tq, "enqueue"):
                    # enqueue a named task - adjust task name to your worker if needed
                    tq.enqueue("regenerate_video", {"content_id": content_id, "reason": "low_rating"})
                    regen_triggered = True
                    regen_mode = "task_queue"
                    logger.info("Enqueued regenerate task for %s via app.task_queue", content_id)
            except Exception:
                # no task queue available or enqueue failed; fall back to thread
                try:
                    t = threading.Thread(target=regenerate_video, args=(content_id, "low_rating"), daemon=True)
                    t.start()
                    regen_triggered = True
                    regen_mode = "thread"
                    logger.info("Started background thread to regenerate %s", content_id)
                except Exception:
                    logger.exception("Failed to start background regeneration for %s", content_id)
        else:
            # High rating - no regeneration needed
            regen_mode = "not_needed"
    except Exception:
        logger.exception("Error while attempting regeneration decision for %s", content_id)

    result = {
        "status": "ok",
        "content_id": content_id,
        "rating": rating,
        "avg_rating": avg_rating,
        "count": total,
        "regenerate_triggered": regen_triggered,
        "regenerate_mode": regen_mode,
        "storyboard_improvement": improvement_result or {"status": "not_processed"}
    }
    return result

def regenerate_video(content_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Attempt to regenerate a video for content_id:
      1) Use storyboard + video.generator if available
      2) Fallback: re-run the pipeline by calling process_script_upload on existing script
    Returns a dict with status and method attempted.
    """
    logger.info("Regenerate requested for %s reason=%s", content_id, reason)

    # 1) Try storyboard + video.generator
    try:
        sb = get_storyboard(content_id)
        if sb:
            try:
                import video.generator as video_generator
            except Exception:
                video_generator = None

            if video_generator:
                try:
                    if hasattr(video_generator, "generate_from_storyboard"):
                        job_info = video_generator.generate_from_storyboard(sb, content_id=content_id)
                        logger.info("Regeneration started via video.generator.generate_from_storyboard for %s", content_id)
                        return {"status": "enqueued", "method": "generate_from_storyboard", "job": job_info}
                    elif hasattr(video_generator, "render_storyboard"):
                        job_info = video_generator.render_storyboard(sb, content_id=content_id)
                        logger.info("Regeneration started via video.generator.render_storyboard for %s", content_id)
                        return {"status": "enqueued", "method": "render_storyboard", "job": job_info}
                except Exception:
                    logger.exception("video.generator failed for content %s", content_id)
    except Exception:
        logger.exception("Error while trying storyboard path for %s", content_id)

    # 2) Fallback: use existing script and call process_script_upload
    try:
        script_text = get_script(content_id)
        if script_text:
            # create a temporary script file for pipeline
            tmp_dir = os.path.join(os.path.dirname(__file__), "bucket", "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            tmp_path = os.path.join(tmp_dir, f"{content_id}_regenerate_{int(time.time())}.txt")
            with open(tmp_path, "w", encoding="utf-8") as fh:
                fh.write(script_text)
            logger.info("Wrote temp script for regeneration: %s", tmp_path)

            # Try to call process_script_upload if defined in this module (bhiv_core)
            try:
                # prefer direct function if present in globals (same module)
                if "process_script_upload" in globals() and callable(globals()["process_script_upload"]):
                    job = globals()["process_script_upload"](tmp_path, uploader_id="regeneration", title=f"Regenerated {content_id}")
                    logger.info("Regeneration enqueued via process_script_upload for %s", content_id)
                    return {"status": "enqueued", "method": "process_script_upload", "job": job}
            except Exception:
                logger.exception("process_script_upload call failed for %s", content_id)

            # as a last-resort, try to import a pipeline entrypoint elsewhere
            try:
                from importlib import import_module
                core = import_module("bhiv_core")
                if hasattr(core, "process_script_upload") and callable(core.process_script_upload):
                    job = core.process_script_upload(tmp_path, uploader_id="regeneration", title=f"Regenerated {content_id}")
                    return {"status": "enqueued", "method": "bhiv_core.process_script_upload", "job": job}
            except Exception:
                logger.exception("Fallback import of process_script_upload failed for %s", content_id)

            logger.warning("No process_script_upload available to re-run pipeline for %s", content_id)
            return {"status": "failed", "reason": "no_pipeline_available"}
        else:
            logger.warning("No script found to regenerate for %s", content_id)
            return {"status": "failed", "reason": "no_script_found"}
    except Exception:
        logger.exception("Error in regeneration fallback for %s", content_id)
        return {"status": "error", "reason": "exception_during_regeneration"}

def _extract_script_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    """Try many common shapes to find a textual script inside payload."""
    if not payload:
        return None

    # common keys first
    keys = ("script", "text", "content", "message", "body", "description", "title")
    for k in keys:
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()

    # nested containers (e.g., {"data": {...}})
    for container in ("data", "payload", "event", "body"):
        c = payload.get(container)
        if isinstance(c, dict):
            for k in keys:
                v = c.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()
            # fallback to first string field in nested dict
            for vv in c.values():
                if isinstance(vv, str) and vv.strip() and len(vv) > 10:
                    return vv.strip()

    # fallback: return first top-level string field with meaningful content
    for v in payload.values():
        if isinstance(v, str) and v.strip() and len(v) > 10:
            return v.strip()

    return None

@safe_job("webhook_ingest", retry_count=0)
async def process_webhook_ingest(payload: Optional[Dict[str, Any]] = None,
                           script_text: Optional[str] = None,
                           source: Optional[str] = None) -> Dict[str, Any]:
    """
    Ingest webhook payload. Accept either:
      - payload dict (JSON), OR  
      - script_text string (from uploaded text file)
    Returns dict with status, content_id OR error with raw_id.
    """
    try:
        if payload is None:
            payload = {}
        elif isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {"raw": payload}

        # If route passed extracted script (multipart upload), prefer that
        if not script_text:
            script_text = _extract_script_from_payload(payload)

        # No script: try to create default script from available data or return error
        if not script_text or not script_text.strip():
            # Try to create a default script from payload metadata
            default_script = None
            if payload.get("url"):
                default_script = f"Content from {payload['url']}"
            elif payload.get("metadata", {}).get("type"):
                content_type = payload["metadata"]["type"]
                default_script = f"Generated content of type: {content_type}"
            elif payload.get("source"):
                default_script = f"Content from source: {payload['source']}"
            
            if default_script:
                script_text = default_script
            else:
                ts = int(time.time())
                uid = uuid.uuid4().hex[:8]
                raw_name = f"webhook_raw_{ts}_{uid}.json"
                try:
                    save_json("uploads", raw_name, {"payload": payload, "received_at": ts, "source": source})
                except Exception:
                    try:
                        save_text("uploads", raw_name, json.dumps({"payload": payload, "received_at": ts}))
                    except Exception:
                        logger.exception("Failed to persist raw webhook payload")
                logger.warning("Webhook payload lacked script. Saved raw=%s", raw_name)
                return {"status": "error", "reason": "no_script_found", "raw_id": raw_name, "suggestion": "Include 'script', 'text', 'content', or 'message' field in payload"}

        # We have script_text -> generate content_id and save both raw payload and script
        content_id = uuid.uuid4().hex[:12]
        try:
            save_json("uploads", f"{content_id}_webhook_raw.json",
                      {"payload": payload, "received_at": int(time.time()), "source": source})
        except Exception:
            logger.exception("Failed to save webhook raw payload for content_id=%s", content_id)

        try:
            # Save script using proper filename format
            script_filename = f"{content_id}_script.txt"
            script_path = save_text("scripts", script_filename, script_text)
        except Exception:
            try:
                save_text("uploads", f"{content_id}_script_fallback.txt", script_text)
            except Exception:
                logger.exception("Failed to persist script for %s", content_id)

        # attempt to call pipeline entrypoint if available
        job_info = None
        try:
            # Create a temporary script file for processing
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(script_text)
                temp_script_path = tmp_file.name
            
            try:
                job_info = await process_script_upload(temp_script_path, uploader_id="webhook", title=f"Webhook Content {content_id}")
            except Exception as e:
                logger.exception("process_script_upload failed for %s: %s", content_id, e)
            finally:
                # Clean up temp file
                try:
                    os.remove(temp_script_path)
                except Exception:
                    pass
        except Exception:
            logger.exception("Error attempting to invoke process_script_upload for %s", content_id)

        result = {"status": "ok", "content_id": content_id}
        if job_info is not None:
            result["job"] = job_info
            result["note"] = "pipeline_invoked"
        else:
            result["note"] = "script_saved"
        return result

    except Exception as exc:
        logger.exception("Unhandled exception in process_webhook_ingest")
        return {"status": "error", "reason": "exception", "error": str(exc)}
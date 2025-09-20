#!/usr/bin/env python3
"""
Async task queue for background feedback processing
Handles LLM calls and feedback improvement with retry logic
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Task:
    id: str
    task_type: str
    payload: Dict[str, Any]
    status: TaskStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class AsyncTaskQueue:
    def __init__(self, max_concurrent_tasks: int = 3):
        self.tasks: Dict[str, Task] = {}
        self.pending_queue = asyncio.Queue()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks = set()
        self.workers_started = False
        
    async def start_workers(self):
        """Start background worker tasks"""
        if self.workers_started:
            return
            
        self.workers_started = True
        for i in range(self.max_concurrent_tasks):
            asyncio.create_task(self._worker(f"worker_{i}"))
    
    async def add_task(self, task_type: str, payload: Dict[str, Any], max_retries: int = 3) -> str:
        """Add a task to the queue"""
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        
        task = Task(
            id=task_id,
            task_type=task_type,
            payload=payload,
            status=TaskStatus.PENDING,
            created_at=time.time(),
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        await self.pending_queue.put(task_id)
        
        # Log task creation
        await self._log_task_event(task_id, "task_created", {
            "task_type": task_type,
            "payload_keys": list(payload.keys()),
            "max_retries": max_retries
        })
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and result"""
        task = self.tasks.get(task_id)
        if not task:
            return None
            
        return {
            "id": task.id,
            "task_type": task.task_type,
            "status": task.status.value,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "error": task.error,
            "result": task.result
        }
    
    async def _worker(self, worker_name: str):
        """Background worker to process tasks"""
        while True:
            try:
                # Get next task from queue
                task_id = await self.pending_queue.get()
                task = self.tasks.get(task_id)
                
                if not task or task.status != TaskStatus.PENDING:
                    continue
                
                # Mark task as running
                task.status = TaskStatus.RUNNING
                task.started_at = time.time()
                self.running_tasks.add(task_id)
                
                await self._log_task_event(task_id, "task_started", {
                    "worker": worker_name,
                    "retry_count": task.retry_count
                })
                
                try:
                    # Process the task
                    result = await self._process_task(task)
                    
                    # Mark as completed
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = time.time()
                    task.result = result
                    
                    await self._log_task_event(task_id, "task_completed", {
                        "worker": worker_name,
                        "duration_seconds": task.completed_at - task.started_at,
                        "retry_count": task.retry_count
                    })
                    
                except Exception as e:
                    # Handle task failure
                    task.error = str(e)
                    
                    if task.retry_count < task.max_retries:
                        # Retry the task
                        task.retry_count += 1
                        task.status = TaskStatus.RETRYING
                        
                        # Add back to queue with delay
                        await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                        await self.pending_queue.put(task_id)
                        
                        await self._log_task_event(task_id, "task_retrying", {
                            "worker": worker_name,
                            "error": str(e),
                            "retry_count": task.retry_count,
                            "next_retry_delay": 2 ** task.retry_count
                        })
                    else:
                        # Max retries exceeded
                        task.status = TaskStatus.FAILED
                        task.completed_at = time.time()
                        
                        await self._log_task_event(task_id, "task_failed", {
                            "worker": worker_name,
                            "error": str(e),
                            "retry_count": task.retry_count,
                            "max_retries_exceeded": True
                        })
                
                finally:
                    self.running_tasks.discard(task_id)
                    
            except Exception as e:
                print(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
    
    async def _process_task(self, task: Task) -> Dict[str, Any]:
        """Process a specific task based on its type"""
        if task.task_type == "feedback_improvement":
            return await self._process_feedback_improvement(task.payload)
        elif task.task_type == "storyboard_generation":
            return await self._process_storyboard_generation(task.payload)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
    
    async def _process_feedback_improvement(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process feedback improvement task"""
        try:
            from core import bhiv_lm_client
        except ImportError:
            # Fallback when LLM client not available
            return {
                "content_id": payload["content_id"],
                "rating": payload["rating"],
                "improvement_applied": False,
                "error": "LLM client not available",
                "processing_time": time.time()
            }
        
        content_id = payload["content_id"]
        rating = payload["rating"]
        feedback_data = payload["feedback_data"]
        
        # Get current storyboard
        storyboard_path = payload.get("storyboard_path")
        if not storyboard_path:
            return {
                "content_id": content_id,
                "rating": rating,
                "improvement_applied": False,
                "error": "Storyboard path not provided",
                "processing_time": time.time()
            }
        
        try:
            # Load storyboard
            with open(storyboard_path, 'r', encoding='utf-8') as f:
                current_storyboard = json.load(f)
            
            # Call LLM improvement
            improved_storyboard = await bhiv_lm_client.improve_storyboard(
                current_storyboard, 
                feedback_data
            )
            
            return {
                "content_id": content_id,
                "rating": rating,
                "improvement_applied": improved_storyboard != current_storyboard,
                "improved_storyboard": improved_storyboard,
                "processing_time": time.time()
            }
        except Exception as e:
            return {
                "content_id": content_id,
                "rating": rating,
                "improvement_applied": False,
                "error": str(e),
                "processing_time": time.time()
            }
    
    async def _process_storyboard_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process storyboard generation task"""
        try:
            from core import bhiv_lm_client
        except ImportError:
            # Fallback when LLM client not available
            return {
                "storyboard": {"error": "LLM client not available"},
                "script_length": len(payload.get("script_text", "")),
                "processing_time": time.time()
            }
        
        script_text = payload["script_text"]
        
        try:
            # Call LLM for storyboard generation
            storyboard = await bhiv_lm_client.suggest_storyboard(script_text)
            
            return {
                "storyboard": storyboard,
                "script_length": len(script_text),
                "processing_time": time.time()
            }
        except Exception as e:
            return {
                "storyboard": {"error": str(e)},
                "script_length": len(script_text),
                "processing_time": time.time()
            }
    
    async def _log_task_event(self, task_id: str, event_type: str, metadata: Dict[str, Any]):
        """Log task processing events"""
        try:
            from core import bhiv_bucket
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "event_type": event_type,
                "metadata": metadata
            }
            
            # Get today's task log file
            log_date = datetime.now().strftime("%Y%m%d")
            log_filename = f"bhiv_task_queue_{log_date}.log"
            
            # Append to log file
            log_path = bhiv_bucket.get_bucket_path("logs", log_filename)
            
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            except Exception:
                # Fallback to bucket save_log
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
                    pass
                    
        except Exception as e:
            print(f"Warning: Failed to log task event {event_type} for {task_id}: {e}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        status_counts = {}
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": len(self.tasks),
            "status_breakdown": status_counts,
            "pending_queue_size": self.pending_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "workers_started": self.workers_started,
            "max_concurrent_tasks": self.max_concurrent_tasks
        }

# Global task queue instance
task_queue = AsyncTaskQueue(max_concurrent_tasks=2)
# app/streaming_metrics.py
import time
import json
import os
from typing import Dict, List
from pathlib import Path

class StreamingMetrics:
    def __init__(self):
        self.metrics_file = "reports/streaming_performance.json"
        os.makedirs("reports", exist_ok=True)
    
    def log_stream_start(self, content_id: str, client_ip: str, range_header: str = None):
        """Log streaming session start"""
        import html
        import uuid
        
        # Generate unique session ID to prevent collisions
        session_id = f"{html.escape(str(content_id))}_{uuid.uuid4().hex[:8]}"
        
        # Sanitize inputs to prevent XSS
        safe_content_id = html.escape(str(content_id))
        safe_client_ip = html.escape(str(client_ip)) if client_ip else "unknown"
        safe_range_header = html.escape(str(range_header)) if range_header else None
        
        metrics = {
            "session_id": session_id,
            "content_id": safe_content_id,
            "client_ip": safe_client_ip,
            "start_time": time.time(),
            "start_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "range_header": safe_range_header,
            "status": "started"
        }
        
        self._append_metrics(metrics)
        return session_id
    
    def log_stream_end(self, session_id: str, bytes_served: int, status_code: int):
        """Log streaming session end with performance data"""
        end_time = time.time()
        
        # Read existing metrics to find start time
        start_time = self._get_start_time(session_id)
        duration = end_time - start_time if start_time else 0
        
        metrics = {
            "session_id": session_id,
            "end_time": end_time,
            "end_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": round(duration, 3),
            "bytes_served": bytes_served,
            "status_code": status_code,
            "throughput_mbps": round((bytes_served * 8) / (duration * 1024 * 1024), 2) if duration > 0.001 else 0,  # Prevent unrealistic values
            "status": "completed"
        }
        
        self._append_metrics(metrics)
    
    def log_buffering_event(self, session_id: str, buffer_duration_ms: int):
        """Log buffering events for latency analysis"""
        metrics = {
            "session_id": session_id,
            "event_type": "buffering",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "buffer_duration_ms": buffer_duration_ms
        }
        
        self._append_metrics(metrics)
    
    def get_performance_summary(self) -> Dict:
        """Get streaming performance summary"""
        try:
            with open(self.metrics_file, 'r') as f:
                all_metrics = [json.loads(line) for line in f if line.strip()]
            
            completed_sessions = [m for m in all_metrics if m.get('status') == 'completed']
            
            if not completed_sessions:
                return {"message": "No completed streaming sessions"}
            
            total_sessions = len(completed_sessions)
            avg_duration = sum(m.get('duration_seconds', 0) for m in completed_sessions) / total_sessions
            avg_throughput = sum(m.get('throughput_mbps', 0) for m in completed_sessions) / total_sessions
            total_bytes = sum(m.get('bytes_served', 0) for m in completed_sessions)
            
            return {
                "total_sessions": total_sessions,
                "average_duration_seconds": round(avg_duration, 3),
                "average_throughput_mbps": round(avg_throughput, 2),
                "total_bytes_served": total_bytes,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except FileNotFoundError:
            return {"message": "No streaming metrics available"}
    
    def _append_metrics(self, metrics: Dict):
        """Append metrics to file"""
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
    
    def _get_start_time(self, session_id: str) -> float:
        """Get start time for a session"""
        try:
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get('session_id') == session_id and data.get('status') == 'started':
                            return data.get('start_time', 0)
        except FileNotFoundError:
            pass
        return 0

# Global instance
streaming_metrics = StreamingMetrics()
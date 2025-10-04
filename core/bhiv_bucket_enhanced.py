#!/usr/bin/env python3
"""
Enhanced Bucket System with S3/MinIO Integration
"""
import os
import time
import json
import hashlib
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import shutil

# Import existing functionality
from .bhiv_bucket import (
    BUCKET_ROOT, STORAGE_BACKEND, S3_BUCKET_NAME, S3_REGION, B2_ENDPOINT,
    _get_s3_client, init_bucket
)

try:
    from .s3_storage import get_s3_adapter
    s3_adapter = get_s3_adapter()
except ImportError:
    s3_adapter = None
    def get_s3_adapter():
        return None

logger = logging.getLogger(__name__)

class EnhancedBucketManager:
    """Enhanced bucket manager with S3 fallback"""
    
    def __init__(self):
        self.local_bucket_path = "bucket"
        self.use_s3 = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
        self.segments = ["uploads", "videos", "scripts", "storyboards", "ratings", "logs", "tmp"]
        
        # Ensure local directories exist
        for segment in self.segments:
            os.makedirs(self.get_local_path(segment), exist_ok=True)
    
    def get_local_path(self, segment: str) -> str:
        """Get local storage path for segment"""
        return os.path.join(self.local_bucket_path, segment)
    
    def save_upload(self, file_data: bytes, filename: str, content_type: str = None) -> str:
        """Save uploaded file with S3 fallback"""
        if self.use_s3 and s3_adapter and s3_adapter.bucket_exists:
            # Save to S3 first
            s3_key = f"uploads/{filename}"
            s3_url = s3_adapter.upload_file(
                file_data, 
                s3_key, 
                content_type,
                metadata={
                    'upload_timestamp': str(time.time()),
                    'original_filename': filename
                }
            )
            
            if s3_url:
                # Save local copy as backup
                local_path = os.path.join(self.get_local_path("uploads"), filename)
                with open(local_path, 'wb') as f:
                    f.write(file_data)
                logger.info(f"File saved to S3: {s3_url} with local backup")
                return s3_url
        
        # Fallback to local storage
        local_path = os.path.join(self.get_local_path("uploads"), filename)
        with open(local_path, 'wb') as f:
            f.write(file_data)
        logger.info(f"File saved locally: {local_path}")
        return local_path
    
    def save_video(self, file_path: str, filename: str) -> str:
        """Save video file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        if self.use_s3 and s3_adapter and s3_adapter.bucket_exists:
            s3_key = f"videos/{filename}"
            s3_url = s3_adapter.upload_file(
                file_data, 
                s3_key, 
                "video/mp4",
                metadata={
                    'generation_timestamp': str(time.time()),
                    'original_source': file_path
                }
            )
            
            if s3_url:
                # Save local copy
                local_path = os.path.join(self.get_local_path("videos"), filename) 
                with open(local_path, 'wb') as f:
                    f.write(file_data)
                return s3_url
        
        # Local storage fallback
        local_path = os.path.join(self.get_local_path("videos"), filename)
        with open(local_path, 'wb') as f:
            f.write(file_data)
        return local_path
    
    def save_script(self, script_content: str, filename: str) -> str:
        """Save script content"""
        if isinstance(script_content, str):
            file_data = script_content.encode('utf-8')
        else:
            file_data = script_content
        
        if self.use_s3 and s3_adapter and s3_adapter.bucket_exists:
            s3_key = f"scripts/{filename}"
            s3_url = s3_adapter.upload_file(
                file_data, 
                s3_key, 
                "text/plain",
                metadata={'script_timestamp': str(time.time())}
            )
            
            if s3_url:
                # Save local backup
                local_path = os.path.join(self.get_local_path("scripts"), filename)
                with open(local_path, 'wb') as f:
                    f.write(file_data)
                return s3_url
        
        # Local fallback
        local_path = os.path.join(self.get_local_path("scripts"), filename)
        with open(local_path, 'wb') as f:
            f.write(file_data)
        return local_path
    
    def save_json(self, segment: str, filename: str, data: dict) -> str:
        """Save JSON data to bucket"""
        json_data = json.dumps(data, indent=2).encode('utf-8')
        
        if self.use_s3 and s3_adapter and s3_adapter.bucket_exists:
            s3_key = f"{segment}/{filename}"
            s3_url = s3_adapter.upload_file(
                json_data, 
                s3_key, 
                "application/json",
                metadata={'data_type': segment}
            )
            
            if s3_url:
                # Local backup
                local_path = os.path.join(self.get_local_path(segment), filename)
                with open(local_path, 'wb') as f:
                    f.write(json_data)
                return s3_url
        
        # Local fallback
        local_path = os.path.join(self.get_local_path(segment), filename)
        with open(local_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return local_path
    
    def generate_presigned_upload_url(self, filename: str, content_type: str = None) -> Optional[Dict[str, Any]]:
        """Generate pre-signed URL for direct frontend uploads"""
        if not (self.use_s3 and s3_adapter and s3_adapter.bucket_exists):
            return None
        
        # Generate unique key
        timestamp = int(time.time())
        safe_filename = "".join(c for c in filename if c.isalnum() or c in '.-_')
        s3_key = f"uploads/{timestamp}_{safe_filename}"
        
        return s3_adapter.generate_presigned_upload_url(s3_key, content_type)
    
    def generate_presigned_download_url(self, s3_key: str) -> Optional[str]:
        """Generate pre-signed URL for downloads"""
        if not (self.use_s3 and s3_adapter and s3_adapter.bucket_exists):
            return None
        
        return s3_adapter.generate_presigned_download_url(s3_key)
    
    def cleanup_old_files(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up files older than specified days"""
        cutoff_time = time.time() - (days_old * 24 * 3600)
        cleanup_results = {}
        
        for segment in self.segments:
            segment_path = self.get_local_path(segment)
            deleted_count = 0
            
            if os.path.exists(segment_path):
                for filename in os.listdir(segment_path):
                    filepath = os.path.join(segment_path, filename)
                    
                    if os.path.isfile(filepath):
                        file_mtime = os.path.getmtime(filepath)
                        
                        if file_mtime < cutoff_time:
                            try:
                                os.remove(filepath)
                                deleted_count += 1
                                logger.info(f"Cleaned up old file: {filepath}")
                            except Exception as e:
                                logger.warning(f"Failed to delete {filepath}: {e}")
            
            cleanup_results[segment] = deleted_count
        
        return cleanup_results

# Global enhanced bucket manager
enhanced_bucket = EnhancedBucketManager()

# Backward compatibility functions - preserve all existing functionality
def save_upload(file_path: str, filename: str) -> str:
    """Backward compatibility for save_upload"""
    with open(file_path, 'rb') as f:
        return enhanced_bucket.save_upload(f.read(), filename)

def save_video(file_path: str, filename: str) -> str:
    """Backward compatibility for save_video"""
    return enhanced_bucket.save_video(file_path, filename)

def save_script(script_content: str, filename: str) -> str:
    """Backward compatibility for save_script"""
    return enhanced_bucket.save_script(script_content, filename)

def save_rating(rating_data: dict, filename: str) -> str:
    """Backward compatibility for save_rating"""
    return enhanced_bucket.save_json("ratings", filename, rating_data)

def save_json(segment: str, filename: str, data: dict) -> str:
    """Backward compatibility for save_json"""
    return enhanced_bucket.save_json(segment, filename, data)

def get_bucket_path(segment: str, filename: str = "") -> str:
    """Backward compatibility for get_bucket_path"""
    path = enhanced_bucket.get_local_path(segment)
    return os.path.join(path, filename) if filename else path

def list_bucket_files(segment: str) -> List[str]:
    """Backward compatibility for list_bucket_files"""
    segment_path = enhanced_bucket.get_local_path(segment)
    if os.path.exists(segment_path):
        return [f for f in os.listdir(segment_path) if os.path.isfile(os.path.join(segment_path, f))]
    return []

def cleanup_old_files(days_old: int = 30) -> Dict[str, int]:
    """Backward compatibility for cleanup_old_files"""
    return enhanced_bucket.cleanup_old_files(days_old)

def rotate_logs() -> Dict[str, Any]:
    """Simple log rotation implementation"""
    logs_path = enhanced_bucket.get_local_path("logs")
    if not os.path.exists(logs_path):
        return {"status": "no_logs_to_rotate"}
    
    timestamp = int(time.time())
    rotated_files = []
    
    for filename in os.listdir(logs_path):
        if filename.endswith('.log'):
            old_path = os.path.join(logs_path, filename)
            new_filename = f"{filename}.{timestamp}"
            new_path = os.path.join(logs_path, new_filename)
            
            try:
                os.rename(old_path, new_path)
                rotated_files.append(new_filename)
            except Exception as e:
                logger.warning(f"Failed to rotate {filename}: {e}")
    
    return {"status": "completed", "rotated_files": rotated_files}

# Import all existing functions to maintain compatibility
from .bhiv_bucket import (
    save_storyboard, read_storyboard, save_log, cleanup_temp_files,
    get_storage_stats, get_script, get_storyboard, get_video_bytes,
    save_text, init_bucket
)
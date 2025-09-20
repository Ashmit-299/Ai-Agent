#!/usr/bin/env python3
"""
BHIV Bucket Storage Abstraction
Provides pluggable storage system for scripts, storyboards, videos, logs, ratings, and temp files.
Supports both local filesystem and AWS S3 backends.
"""

from pathlib import Path
import shutil
import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

# Storage configuration
STORAGE_BACKEND = os.getenv("BHIV_STORAGE_BACKEND", "local")  # "local" or "s3"
BUCKET_ROOT = Path(os.getenv("BHIV_BUCKET_PATH", "bucket"))
S3_BUCKET_NAME = os.getenv("B2_BUCKET") or os.getenv("BHIV_S3_BUCKET", "bhiv-content")
S3_REGION = os.getenv("BHIV_S3_REGION", "us-east-1")
B2_ENDPOINT = os.getenv("B2_ENDPOINT")

# S3 client (lazy initialization)
_s3_client = None

def _get_s3_client():
    """Get or create S3 client"""
    global _s3_client
    if _s3_client is None:
        try:
            import boto3
            if B2_ENDPOINT:
                # Use B2-specific credentials if available
                session = boto3.session.Session()
                _s3_client = session.client(
                    service_name="s3",
                    endpoint_url=B2_ENDPOINT,
                    aws_access_key_id=os.getenv("B2_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("B2_APP_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
                )
            else:
                _s3_client = boto3.client('s3', region_name=S3_REGION)
        except ImportError:
            raise ImportError("boto3 is required for S3 backend. Install with: pip install boto3")
    return _s3_client

def init_bucket():
    """Initialize bucket directory structure"""
    segments = ["scripts", "storyboards", "videos", "logs", "ratings", "tmp", "uploads"]
    for segment in segments:
        (BUCKET_ROOT / segment).mkdir(parents=True, exist_ok=True)

def save_script(local_path: str, dest_name: Optional[str] = None) -> str:
    """
    Copy local script file to bucket/scripts/
    """
    try:
        if dest_name:
            dest_name = os.path.basename(dest_name)
        else:
            dest_name = os.path.basename(local_path)
        
        if not dest_name or dest_name in ['.', '..'] or '/' in dest_name or '\\' in dest_name:
            raise ValueError("Invalid destination filename")
        
        if STORAGE_BACKEND == "s3":
            s3_key = f"scripts/{dest_name}"
            s3_client = _get_s3_client()
            s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / "scripts" / dest_name
            
            if not str(dest.resolve()).startswith(str(BUCKET_ROOT.resolve())):
                raise ValueError("Destination path outside bucket")
            
            shutil.copy(local_path, dest)
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save script: {e}")

def save_storyboard(storyboard_dict: Dict[str, Any], filename: str) -> str:
    """
    Save storyboard dictionary as JSON to bucket/storyboards/
    """
    try:
        content = json.dumps(storyboard_dict, ensure_ascii=False, indent=2)
        
        if STORAGE_BACKEND == "s3":
            s3_key = f"storyboards/{filename}"
            s3_client = _get_s3_client()
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType='application/json'
            )
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / "storyboards" / filename
            dest.write_text(content, encoding="utf-8")
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save storyboard: {e}")

def save_video(local_video_path: str, filename: Optional[str] = None) -> str:
    """
    Copy local video file to bucket/videos/
    """
    try:
        filename = filename or Path(local_video_path).name
        
        if STORAGE_BACKEND == "s3":
            s3_key = f"videos/{filename}"
            s3_client = _get_s3_client()
            s3_client.upload_file(local_video_path, S3_BUCKET_NAME, s3_key)
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / "videos" / filename
            shutil.copy(local_video_path, dest)
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save video: {e}")

def save_upload(local_file_path: str, filename: Optional[str] = None) -> str:
    """
    Copy uploaded file to bucket/uploads/
    """
    try:
        filename = filename or Path(local_file_path).name
        
        if STORAGE_BACKEND == "s3":
            s3_key = f"uploads/{filename}"
            s3_client = _get_s3_client()
            s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_key)
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / "uploads" / filename
            shutil.copy(local_file_path, dest)
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save upload: {e}")

def read_storyboard(path: str) -> Dict[str, Any]:
    """
    Read storyboard JSON file from bucket
    """
    try:
        if STORAGE_BACKEND == "s3" and path.startswith("s3://"):
            # Parse S3 URL: s3://bucket/key
            s3_key = path.replace(f"s3://{S3_BUCKET_NAME}/", "")
            s3_client = _get_s3_client()
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        elif STORAGE_BACKEND == "s3":
            # Assume it's a filename in storyboards/
            s3_key = f"storyboards/{path}"
            s3_client = _get_s3_client()
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        else:
            file_path = Path(path)
            if not file_path.is_absolute():
                file_path = BUCKET_ROOT / "storyboards" / path
            return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to read storyboard: {e}")

def save_log(log_content: str, filename: str) -> str:
    """Save log content to bucket/logs/"""
    try:
        if STORAGE_BACKEND == "s3":
            s3_key = f"logs/{filename}"
            s3_client = _get_s3_client()
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=log_content.encode('utf-8'),
                ContentType='text/plain'
            )
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / "logs" / filename
            dest.write_text(log_content, encoding="utf-8")
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save log: {e}")

def save_rating(rating_data: Dict[str, Any], filename: str) -> str:
    """Save rating data to bucket/ratings/"""
    try:
        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in ['.', '..']:
            raise ValueError("Invalid filename")
        
        content = json.dumps(rating_data, ensure_ascii=False, indent=2)
        
        if STORAGE_BACKEND == "s3":
            s3_key = f"ratings/{safe_filename}"
            s3_client = _get_s3_client()
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType='application/json'
            )
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / "ratings" / safe_filename
            
            if not str(dest.resolve()).startswith(str(BUCKET_ROOT.resolve())):
                raise ValueError("Destination path outside bucket")
            
            dest.write_text(content, encoding="utf-8")
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save rating: {e}")

def get_bucket_path(segment: str, filename: str = "") -> str:
    """Get full path for bucket segment and optional filename"""
    init_bucket()
    
    allowed_segments = ["scripts", "storyboards", "videos", "logs", "ratings", "tmp", "uploads"]
    if segment not in allowed_segments:
        raise ValueError(f"Invalid segment. Allowed: {', '.join(allowed_segments)}")
    
    if filename:
        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in ['.', '..']:
            raise ValueError("Invalid filename")
        
        path = BUCKET_ROOT / segment / safe_filename
        
        if not str(path.resolve()).startswith(str(BUCKET_ROOT.resolve())):
            raise ValueError("Path outside bucket")
        
        return str(path)
    
    return str(BUCKET_ROOT / segment)

def cleanup_temp_files(max_age_hours: int = 24) -> int:
    """Clean up temporary files older than max_age_hours"""
    try:
        cleaned_count = 0
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        if STORAGE_BACKEND == "s3":
            s3_client = _get_s3_client()
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix="tmp/"
            )
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].timestamp() < cutoff_time:
                    s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                    cleaned_count += 1
        else:
            init_bucket()
            tmp_path = BUCKET_ROOT / "tmp"
            if tmp_path.exists():
                for file_path in tmp_path.iterdir():
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
        
        return cleaned_count
    except Exception:
        return 0

def cleanup_old_files(max_age_days: int = 30) -> Dict[str, int]:
    """Clean up old files from all segments"""
    try:
        results = {}
        cutoff_time = time.time() - (max_age_days * 86400)
        segments = ["tmp", "logs", "ratings"]
        
        for segment in segments:
            cleaned_count = 0
            
            if STORAGE_BACKEND == "s3":
                s3_client = _get_s3_client()
                response = s3_client.list_objects_v2(
                    Bucket=S3_BUCKET_NAME,
                    Prefix=f"{segment}/"
                )
                
                for obj in response.get('Contents', []):
                    if obj['LastModified'].timestamp() < cutoff_time:
                        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                        cleaned_count += 1
            else:
                init_bucket()
                segment_path = BUCKET_ROOT / segment
                if segment_path.exists():
                    for file_path in segment_path.iterdir():
                        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                            file_path.unlink()
                            cleaned_count += 1
            
            results[segment] = cleaned_count
        
        return results
    except Exception as e:
        return {"error": str(e)}

def rotate_logs(max_age_days: int = 7) -> Dict[str, Any]:
    """Archive old log files"""
    try:
        archived_count = 0
        cutoff_time = time.time() - (max_age_days * 86400)  # Convert days to seconds
        
        if STORAGE_BACKEND == "s3":
            s3_client = _get_s3_client()
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix="logs/"
            )
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].timestamp() < cutoff_time:
                    # Move to archive by copying with new key
                    old_key = obj['Key']
                    archive_key = old_key.replace('logs/', 'archive/logs/')
                    
                    s3_client.copy_object(
                        Bucket=S3_BUCKET_NAME,
                        CopySource={'Bucket': S3_BUCKET_NAME, 'Key': old_key},
                        Key=archive_key
                    )
                    s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=old_key)
                    archived_count += 1
        else:
            init_bucket()
            logs_path = BUCKET_ROOT / "logs"
            archive_path = BUCKET_ROOT / "archive" / "logs"
            archive_path.mkdir(parents=True, exist_ok=True)
            
            if logs_path.exists():
                for file_path in logs_path.iterdir():
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        archive_file = archive_path / file_path.name
                        shutil.move(str(file_path), str(archive_file))
                        archived_count += 1
        
        return {
            "archived_count": archived_count,
            "max_age_days": max_age_days,
            "backend": STORAGE_BACKEND
        }
    except Exception as e:
        return {"error": str(e), "archived_count": 0}

def get_storage_stats() -> Dict[str, Any]:
    """Get storage backend statistics"""
    try:
        stats = {
            "backend": STORAGE_BACKEND,
            "segments": ["scripts", "storyboards", "videos", "logs", "ratings", "tmp", "uploads"],
            "timestamp": datetime.now().isoformat()
        }
        
        if STORAGE_BACKEND == "s3":
            stats.update({
                "s3_bucket": S3_BUCKET_NAME,
                "s3_region": S3_REGION,
                "endpoint": B2_ENDPOINT or "AWS S3"
            })
        else:
            stats["local_path"] = str(BUCKET_ROOT)
        
        return stats
    except Exception as e:
        return {"error": str(e), "backend": STORAGE_BACKEND}

def list_bucket_files(segment: str) -> list:
    """List all files in a bucket segment"""
    try:
        allowed_segments = ["scripts", "storyboards", "videos", "logs", "ratings", "tmp", "uploads"]
        if segment not in allowed_segments:
            raise ValueError(f"Invalid segment. Allowed: {', '.join(allowed_segments)}")
        
        if STORAGE_BACKEND == "s3":
            s3_client = _get_s3_client()
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix=f"{segment}/"
            )
            
            files = []
            for obj in response.get('Contents', []):
                # Extract filename from key (remove segment prefix)
                filename = obj['Key'].replace(f"{segment}/", "")
                if filename and '/' not in filename:  # Only direct files, not subdirectories
                    files.append(filename)
            return files
        else:
            init_bucket()
            segment_path = BUCKET_ROOT / segment
            if segment_path.exists():
                return [f.name for f in segment_path.iterdir() if f.is_file()]
            return []
    except Exception as e:
        raise ValueError(f"Failed to list files: {e}")

def get_script(content_id: str) -> Optional[str]:
    """Get script content by content_id"""
    try:
        script_filename = f"{content_id}_script.txt"
        if STORAGE_BACKEND == "s3":
            s3_key = f"scripts/{script_filename}"
            s3_client = _get_s3_client()
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            return response['Body'].read().decode('utf-8')
        else:
            init_bucket()
            script_path = BUCKET_ROOT / "scripts" / script_filename
            if script_path.exists():
                return script_path.read_text(encoding="utf-8")
            return None
    except Exception:
        return None

def get_storyboard(content_id: str) -> Optional[Dict[str, Any]]:
    """Get storyboard by content_id"""
    try:
        storyboard_filename = f"{content_id}_storyboard.json"
        return read_storyboard(storyboard_filename)
    except Exception:
        return None

def get_video_bytes(content_id: str) -> Optional[bytes]:
    """Get video bytes by content_id"""
    try:
        video_filename = f"{content_id}.mp4"
        if STORAGE_BACKEND == "s3":
            s3_key = f"videos/{video_filename}"
            s3_client = _get_s3_client()
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            return response['Body'].read()
        else:
            init_bucket()
            video_path = BUCKET_ROOT / "videos" / video_filename
            if video_path.exists():
                return video_path.read_bytes()
            return None
    except Exception:
        return None

def save_json(segment: str, filename: str, data: Dict[str, Any]) -> str:
    """Save JSON data to specified bucket segment"""
    try:
        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in ['.', '..']:
            raise ValueError("Invalid filename")
        
        allowed_segments = ["scripts", "storyboards", "videos", "logs", "ratings", "tmp", "uploads"]
        if segment not in allowed_segments:
            raise ValueError(f"Invalid segment. Allowed: {', '.join(allowed_segments)}")
        
        content = json.dumps(data, ensure_ascii=False, indent=2)
        
        if STORAGE_BACKEND == "s3":
            s3_key = f"{segment}/{safe_filename}"
            s3_client = _get_s3_client()
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType='application/json'
            )
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / segment / safe_filename
            
            if not str(dest.resolve()).startswith(str(BUCKET_ROOT.resolve())):
                raise ValueError("Destination path outside bucket")
            
            dest.write_text(content, encoding="utf-8")
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save JSON: {e}")

def save_text(segment: str, filename: str, content: str) -> str:
    """Save text content to specified bucket segment"""
    try:
        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in ['.', '..']:
            raise ValueError("Invalid filename")
        
        allowed_segments = ["scripts", "storyboards", "videos", "logs", "ratings", "tmp", "uploads"]
        if segment not in allowed_segments:
            raise ValueError(f"Invalid segment. Allowed: {', '.join(allowed_segments)}")
        
        if STORAGE_BACKEND == "s3":
            s3_key = f"{segment}/{safe_filename}"
            s3_client = _get_s3_client()
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
            return f"s3://{S3_BUCKET_NAME}/{s3_key}"
        else:
            init_bucket()
            dest = BUCKET_ROOT / segment / safe_filename
            
            if not str(dest.resolve()).startswith(str(BUCKET_ROOT.resolve())):
                raise ValueError("Destination path outside bucket")
            
            dest.write_text(content, encoding="utf-8")
            return str(dest)
    except Exception as e:
        raise ValueError(f"Failed to save text: {e}")
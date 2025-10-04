#!/usr/bin/env python3
"""
Pre-signed URL API for direct frontend uploads
"""
import os
import uuid
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel

# Import authentication
try:
    from .auth import get_current_user_required
except ImportError:
    async def get_current_user_required(request: Request):
        class DemoUser:
            def __init__(self):
                self.user_id = "demo_user"
                self.username = "demo"
        return DemoUser()

try:
    from .request_middleware import audit_logger
except ImportError:
    class MockAuditLogger:
        def log_action(self, **kwargs):
            pass
    audit_logger = MockAuditLogger()

from core.s3_storage_adapter import storage_adapter

router = APIRouter(prefix="/presigned", tags=["Pre-signed URLs"])

class PreSignedUploadRequest(BaseModel):
    filename: str
    content_type: str
    segment: str = "uploads"

class PreSignedUploadResponse(BaseModel):
    upload_url: str
    file_key: str
    expiration_seconds: int
    fields: Optional[dict] = None

class PreSignedDownloadResponse(BaseModel):
    download_url: str
    expiration_seconds: int

@router.post("/upload", response_model=PreSignedUploadResponse)
async def generate_upload_url(
    request: Request,
    request_data: PreSignedUploadRequest,
    current_user = Depends(get_current_user_required)
):
    """Generate pre-signed URL for direct file upload"""
    
    # Validate segment
    allowed_segments = ['uploads', 'scripts', 'videos', 'images']
    if request_data.segment not in allowed_segments:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid segment. Allowed: {allowed_segments}"
        )
    
    # Validate file type
    allowed_extensions = {
        'uploads': ['.txt', '.pdf', '.jpg', '.jpeg', '.png', '.mp4', '.mp3', '.wav'],
        'scripts': ['.txt'],
        'videos': ['.mp4', '.avi', '.mov'],
        'images': ['.jpg', '.jpeg', '.png', '.gif']
    }
    
    file_ext = os.path.splitext(request_data.filename)[1].lower()
    if file_ext not in allowed_extensions.get(request_data.segment, []):
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed for {request_data.segment}"
        )
    
    # Generate unique filename
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    user_id = current_user.user_id
    
    # Clean original filename
    clean_filename = "".join(c for c in request_data.filename if c.isalnum() or c in '.-_')
    
    unique_filename = f"{timestamp}_{user_id}_{unique_id}_{clean_filename}"
    
    # Generate pre-signed URL
    expiration = 3600  # 1 hour
    
    upload_url = storage_adapter.generate_presigned_url(
        segment=request_data.segment,
        filename=unique_filename,
        expiration=expiration,
        operation='put_object'
    )
    
    if not upload_url:
        raise HTTPException(
            status_code=500,
            detail="Could not generate upload URL. S3/MinIO not available."
        )
    
    # Log the pre-signed URL generation
    audit_logger.log_action(
        user_id=current_user.user_id,
        action="generate_presigned_upload_url",
        resource_type="presigned_url",
        resource_id=unique_filename,
        details={
            "segment": request_data.segment,
            "filename": request_data.filename,
            "content_type": request_data.content_type,
            "expiration": expiration
        }
    )
    
    return PreSignedUploadResponse(
        upload_url=upload_url,
        file_key=unique_filename,
        expiration_seconds=expiration
    )

@router.get("/download/{segment}/{filename}", response_model=PreSignedDownloadResponse)
async def generate_download_url(
    segment: str,
    filename: str,
    request: Request,
    expiration: int = Query(default=3600, ge=300, le=86400),
    current_user = Depends(get_current_user_required)
):
    """Generate pre-signed URL for file download"""
    
    # Validate segment
    allowed_segments = ['uploads', 'scripts', 'videos', 'storyboards', 'images']
    if segment not in allowed_segments:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid segment. Allowed: {allowed_segments}"
        )
    
    # Generate pre-signed download URL
    download_url = storage_adapter.generate_presigned_url(
        segment=segment,
        filename=filename,
        expiration=expiration,
        operation='get_object'
    )
    
    if not download_url:
        # Fallback for local storage
        file_url = storage_adapter.get_file_url(segment, filename)
        if not os.path.exists(file_url):
            raise HTTPException(status_code=404, detail="File not found")
        
        # For local files, return the local path
        download_url = f"/api/files/{segment}/{filename}"
    
    # Log the download URL generation
    audit_logger.log_action(
        user_id=current_user.user_id,
        action="generate_presigned_download_url", 
        resource_type="presigned_url",
        resource_id=filename,
        details={
            "segment": segment,
            "expiration": expiration
        }
    )
    
    return PreSignedDownloadResponse(
        download_url=download_url,
        expiration_seconds=expiration
    )

@router.get("/list/{segment}")
async def list_user_files(
    segment: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    current_user = Depends(get_current_user_required)
):
    """List user's files in a segment"""
    
    allowed_segments = ['uploads', 'scripts', 'videos', 'storyboards']
    if segment not in allowed_segments:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid segment. Allowed: {allowed_segments}"
        )
    
    try:
        files = storage_adapter.list_files(segment, max_keys=limit)
        
        # Filter files by user (if filename contains user_id)
        user_id = current_user.user_id
        user_files = []
        
        for file_info in files:
            # Check if file belongs to user (simple check by filename pattern)
            if user_id in file_info['filename'] or segment == 'videos':  # Videos can be public
                # Generate download URL for each file
                download_url = storage_adapter.generate_presigned_url(
                    segment=segment,
                    filename=file_info['filename'],
                    expiration=3600
                )
                
                file_info['download_url'] = download_url
                user_files.append(file_info)
        
        return {
            "segment": segment,
            "files": user_files,
            "total_count": len(user_files),
            "user_id": current_user.user_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )

@router.delete("/{segment}/{filename}")
async def delete_user_file(
    segment: str,
    filename: str,
    request: Request,
    current_user = Depends(get_current_user_required)
):
    """Delete user's file"""
    
    allowed_segments = ['uploads', 'scripts', 'storyboards']  # Videos should not be deletable
    if segment not in allowed_segments:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid segment. Allowed: {allowed_segments}"
        )
    
    user_id = current_user.user_id
    
    # Security check: only allow users to delete their own files
    if user_id not in filename:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own files"
        )
    
    try:
        success = storage_adapter.delete_file(segment, filename)
        
        if success:
            # Log the deletion
            audit_logger.log_action(
                user_id=user_id,
                action="delete_file",
                resource_type="file",
                resource_id=filename,
                details={
                    "segment": segment,
                    "filename": filename
                }
            )
            
            return {"message": f"File {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )

# Health check for storage system
@router.get("/health")
async def storage_health_check(
    request: Request,
    current_user = Depends(get_current_user_required)
):
    """Check storage system health"""
    
    # Force reload environment variables
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Read current environment variables directly
    use_s3 = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
    bucket_name = os.getenv("S3_BUCKET_NAME", "ai-agent-files")
    region = os.getenv("S3_REGION", "ap-south-1")
    endpoint_url = os.getenv("S3_ENDPOINT_URL")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    health_status = {
        "s3_enabled": use_s3,
        "bucket_name": bucket_name,
        "endpoint_url": endpoint_url,
        "region": region,
        "has_credentials": bool(aws_access_key and aws_secret_key),
        "local_fallback": True,
        "timestamp": time.time()
    }
    
    # Test S3 connection directly
    if use_s3 and aws_access_key and aws_secret_key:
        try:
            import boto3
            from botocore.config import Config
            
            config = Config(retries={'max_attempts': 3, 'mode': 'adaptive'})
            
            s3_client = boto3.client(
                's3',
                config=config,
                region_name=region,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Test bucket access
            s3_client.head_bucket(Bucket=bucket_name)
            health_status["s3_client_available"] = True
            health_status["s3_connection"] = "healthy"
            
        except Exception as e:
            health_status["s3_client_available"] = False
            health_status["s3_connection"] = f"failed: {str(e)}"
    else:
        health_status["s3_client_available"] = False
        health_status["s3_connection"] = "disabled_or_missing_credentials"
    
    return health_status
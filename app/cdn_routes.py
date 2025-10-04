#!/usr/bin/env python3
"""
CDN Integration and Pre-signed URL Routes
"""
import os
import time
import logging
import secrets
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Form, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse

from .auth import get_current_user_required, get_current_user_optional
from core.bhiv_bucket_enhanced import enhanced_bucket

# Fallback logging functions
try:
    from core.system_logger import log_api_request, log_user_action
except ImportError:
    def log_api_request(endpoint, method, user_id, data):
        logger.info(f"API Request: {method} {endpoint} by {user_id}")
    
    def log_user_action(action, user_id, data):
        logger.info(f"User Action: {action} by {user_id}")

logger = logging.getLogger(__name__)

cdn_router = APIRouter(prefix="/cdn", tags=["CDN & Pre-signed URLs"])

@cdn_router.get("/upload-url")
async def generate_upload_url(
    filename: str,
    content_type: str = "application/octet-stream",
    current_user = Depends(get_current_user_required)
):
    """Generate upload URL - works with Supabase, S3, or local storage"""
    
    try:
        # Log request
        log_api_request('/cdn/upload-url', 'GET', current_user.user_id, {
            'filename': filename,
            'content_type': content_type
        })
        
        # Validate filename
        try:
            from .security import InputSanitizer
            if not InputSanitizer.validate_filename(filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid filename"
                )
        except ImportError:
            # Basic filename validation fallback
            if not filename or '..' in filename or '/' in filename or '\\' in filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid filename"
                )
        
        # Check Supabase Storage first
        use_supabase = os.getenv("USE_SUPABASE_STORAGE", "false").lower() == "true"
        if use_supabase:
            try:
                from core.supabase_storage import get_supabase_adapter
                supabase_adapter = get_supabase_adapter()
                if supabase_adapter:
                    upload_data = supabase_adapter.generate_presigned_upload_url(filename, content_type)
                    if upload_data:
                        log_user_action('supabase_upload_url_generated', current_user.user_id, {
                            'filename': filename,
                            'expires_in': upload_data['expires_in']
                        })
                        return {
                            "method": "supabase_presigned",
                            "upload_url": upload_data["upload_url"],
                            "fields": upload_data.get("fields", {}),
                            "expires_in": upload_data["expires_in"],
                            "max_file_size": upload_data["max_file_size"],
                            "instructions": {
                                "1": "Use the upload_url as your POST endpoint",
                                "2": "Include all fields in your form data",
                                "3": "Add your file as 'file' field",
                                "4": "Submit as multipart/form-data"
                            }
                        }
            except Exception as e:
                logger.warning(f"Supabase upload URL generation failed: {e}")
        
        # Try S3 if enabled
        upload_data = enhanced_bucket.generate_presigned_upload_url(filename, content_type)
        if upload_data:
            log_user_action('s3_upload_url_generated', current_user.user_id, {
                'filename': filename,
                'expires_in': upload_data['expires_in']
            })
            return {
                "method": "s3_presigned",
                "upload_url": upload_data["upload_url"],
                "fields": upload_data["fields"],
                "expires_in": upload_data["expires_in"],
                "max_file_size": upload_data["max_file_size"],
                "instructions": {
                    "1": "Use the upload_url as your POST endpoint",
                    "2": "Include all fields in your form data",
                    "3": "Add your file as 'file' field",
                    "4": "Submit as multipart/form-data"
                }
            }
        
        # Generate upload token for direct API upload
        import secrets
        upload_token = secrets.token_urlsafe(32)
        
        # Store upload token temporarily (in-memory cache)
        if not hasattr(generate_upload_url, '_upload_tokens'):
            generate_upload_url._upload_tokens = {}
        
        generate_upload_url._upload_tokens[upload_token] = {
            'user_id': current_user.user_id,
            'filename': filename,
            'content_type': content_type,
            'expires_at': time.time() + 3600  # 1 hour
        }
        
        # Clean expired tokens
        current_time = time.time()
        expired_tokens = [token for token, data in generate_upload_url._upload_tokens.items() 
                         if data['expires_at'] < current_time]
        for token in expired_tokens:
            del generate_upload_url._upload_tokens[token]
        
        log_user_action('direct_upload_token_generated', current_user.user_id, {
            'filename': filename,
            'upload_token': upload_token[:8] + '...'  # Log partial token for debugging
        })
        
        return {
            "method": "direct_api",
            "upload_url": f"/cdn/direct-upload/{upload_token}",
            "expires_in": 3600,
            "max_file_size": 100 * 1024 * 1024,
            "instructions": {
                "1": "POST your file to the upload_url",
                "2": "Use multipart/form-data",
                "3": "File field name: 'file'",
                "4": "Include Authorization header with your JWT token"
            },
            "example_curl": f"curl -X POST '{os.getenv('BASE_URL', 'http://localhost:9000')}/cdn/direct-upload/{upload_token}' -H 'Authorization: Bearer YOUR_JWT_TOKEN' -F 'file=@{filename}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload URL generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )

@cdn_router.get("/download-url/{content_id}")
async def generate_download_url(
    content_id: str,
    expires_in: int = 3600,
    current_user = Depends(get_current_user_optional)
):
    """Generate pre-signed URL for content downloads"""
    
    try:
        # Get content from database
        from core.database import DatabaseManager
        db = DatabaseManager()
        content = db.get_content_by_id(content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        file_path = content.file_path
        
        # Check if file is in S3
        if file_path.startswith("s3://"):
            # Extract S3 key from S3 URL
            if enhanced_bucket.s3_adapter:
                s3_key = file_path.replace(f"s3://{enhanced_bucket.s3_adapter.bucket_name}/", "")
            else:
                s3_key = file_path.replace("s3://", "").split("/", 1)[1] if "/" in file_path else file_path
            
            # Generate pre-signed download URL
            download_url = enhanced_bucket.generate_presigned_download_url(s3_key)
            
            if download_url:
                # Log download URL generation
                if current_user:
                    log_user_action('presigned_download_url_generated', current_user.user_id, {
                        'content_id': content_id,
                        'expires_in': expires_in
                    })
                
                return {
                    "method": "presigned_url",
                    "download_url": download_url,
                    "expires_in": expires_in,
                    "content_id": content_id,
                    "filename": os.path.basename(file_path)
                }
        
        # Fallback to regular download endpoint
        return {
            "method": "fallback",
            "download_url": f"/download/{content_id}",
            "message": "Direct download via API endpoint",
            "expires_in": None,
            "content_id": content_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download URL generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )

@cdn_router.get("/stream-url/{content_id}")
async def generate_stream_url(
    content_id: str,
    expires_in: int = 7200,  # 2 hours for streaming
    current_user = Depends(get_current_user_optional)
):
    """Generate optimized streaming URL with CDN support"""
    
    try:
        # Get content from database
        from core.database import DatabaseManager
        db = DatabaseManager()
        content = db.get_content_by_id(content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check if content is video
        if not content.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is not a video file"
            )
        
        file_path = content.file_path
        
        # CDN URL generation (Cloudflare example)
        cdn_domain = os.getenv("CDN_DOMAIN")  # e.g., "cdn.yourdomain.com"
        
        if cdn_domain and file_path.startswith("s3://"):
            # Generate CDN URL
            if enhanced_bucket.s3_adapter:
                s3_key = file_path.replace(f"s3://{enhanced_bucket.s3_adapter.bucket_name}/", "")
            else:
                s3_key = file_path.replace("s3://", "").split("/", 1)[1] if "/" in file_path else file_path
            cdn_url = f"https://{cdn_domain}/{s3_key}"
            
            # For Cloudflare, you might add signed URLs
            # This is a simplified example
            return {
                "method": "cdn_stream",
                "stream_url": cdn_url,
                "cdn_provider": "cloudflare",
                "expires_in": expires_in,
                "content_id": content_id,
                "optimizations": {
                    "edge_caching": True,
                    "compression": True,
                    "adaptive_bitrate": True
                }
            }
        
        elif file_path.startswith("s3://"):
            # S3 pre-signed URL for streaming
            if enhanced_bucket.s3_adapter:
                s3_key = file_path.replace(f"s3://{enhanced_bucket.s3_adapter.bucket_name}/", "")
            else:
                s3_key = file_path.replace("s3://", "").split("/", 1)[1] if "/" in file_path else file_path
            stream_url = enhanced_bucket.generate_presigned_download_url(s3_key)
            
            if stream_url:
                return {
                    "method": "s3_presigned",
                    "stream_url": stream_url,
                    "expires_in": expires_in,
                    "content_id": content_id,
                    "supports_range_requests": True
                }
        
        # Fallback to regular streaming endpoint
        return {
            "method": "api_stream",
            "stream_url": f"/stream/{content_id}",
            "message": "Direct streaming via API endpoint",
            "expires_in": None,
            "content_id": content_id,
            "supports_range_requests": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream URL generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate stream URL"
        )

@cdn_router.get("/assets/{asset_type}/{filename}")
async def serve_static_assets(asset_type: str, filename: str):
    """Serve static assets with CDN redirect"""
    
    try:
        # Validate asset type
        allowed_types = ["css", "js", "images", "fonts"]
        if asset_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset type not found"
            )
        
        # CDN redirect if available
        cdn_domain = os.getenv("CDN_DOMAIN")
        if cdn_domain:
            cdn_url = f"https://{cdn_domain}/assets/{asset_type}/{filename}"
            return RedirectResponse(url=cdn_url, status_code=302)
        
        # Fallback to local serving
        asset_path = os.path.join("static", asset_type, filename)
        if os.path.exists(asset_path):
            from fastapi.responses import FileResponse
            return FileResponse(asset_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Asset serving failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serve asset"
        )

@cdn_router.post("/direct-upload/{upload_token}")
async def direct_upload(
    upload_token: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user_required)
):
    """Direct file upload using upload token"""
    
    try:
        # Validate upload token
        if not hasattr(generate_upload_url, '_upload_tokens'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid upload token"
            )
        
        token_data = generate_upload_url._upload_tokens.get(upload_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired upload token"
            )
        
        # Check token expiry
        if time.time() > token_data['expires_at']:
            del generate_upload_url._upload_tokens[upload_token]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Upload token expired"
            )
        
        # Verify user
        if token_data['user_id'] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token belongs to different user"
            )
        
        # Validate file size
        max_size = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {max_size} bytes"
            )
        
        # Save file using enhanced bucket
        saved_path = enhanced_bucket.save_upload(file_content, file.filename, file.content_type)
        
        # Store in database
        from core.database import DatabaseManager
        db = DatabaseManager()
        
        content_data = {
            'user_id': current_user.user_id,
            'filename': file.filename,
            'file_path': saved_path,
            'content_type': file.content_type,
            'file_size': len(file_content),
            'upload_method': 'direct_api'
        }
        
        content_id = db.save_content(content_data)
        
        # Clean up token
        del generate_upload_url._upload_tokens[upload_token]
        
        log_user_action('direct_upload_completed', current_user.user_id, {
            'content_id': content_id,
            'filename': file.filename,
            'file_size': len(file_content)
        })
        
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "content_id": content_id,
            "filename": file.filename,
            "file_size": len(file_content),
            "file_path": saved_path,
            "download_url": f"/download/{content_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Direct upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed"
        )

@cdn_router.get("/purge-cache/{content_id}")
async def purge_cdn_cache(
    content_id: str,
    current_user = Depends(get_current_user_required),
    admin_key: str = None
):
    """Purge CDN cache for specific content (admin only)"""
    
    # Admin check
    if admin_key != "admin_cdn_2025":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Get content
        from core.database import DatabaseManager
        db = DatabaseManager()
        content = db.get_content_by_id(content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # CDN cache purging (example for Cloudflare)
        cloudflare_zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
        cloudflare_api_key = os.getenv("CLOUDFLARE_API_KEY")
        
        if cloudflare_zone_id and cloudflare_api_key:
            import requests
            
            # Construct URLs to purge
            file_path = content.file_path
            if file_path.startswith("s3://"):
                if enhanced_bucket.s3_adapter:
                    s3_key = file_path.replace(f"s3://{enhanced_bucket.s3_adapter.bucket_name}/", "")
                else:
                    s3_key = file_path.replace("s3://", "").split("/", 1)[1] if "/" in file_path else file_path
                cdn_domain = os.getenv("CDN_DOMAIN")
                if cdn_domain:
                    urls_to_purge = [f"https://{cdn_domain}/{s3_key}"]
                    
                    # Cloudflare cache purge API call
                    headers = {
                        "Authorization": f"Bearer {cloudflare_api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    data = {"files": urls_to_purge}
                    
                    response = requests.post(
                        f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}/purge_cache",
                        headers=headers,
                        json=data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        log_user_action('cdn_cache_purged', current_user.user_id, {
                            'content_id': content_id,
                            'urls_purged': urls_to_purge
                        })
                        
                        return {
                            "status": "success",
                            "message": "CDN cache purged successfully",
                            "content_id": content_id,
                            "urls_purged": urls_to_purge
                        }
                    else:
                        return {
                            "status": "error",
                            "message": "CDN cache purge failed",
                            "error": response.text
                        }
        
        return {
            "status": "not_configured",
            "message": "CDN cache purge not configured"
        }
        
    except Exception as e:
        logger.error(f"CDN cache purge failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purge CDN cache"
        )
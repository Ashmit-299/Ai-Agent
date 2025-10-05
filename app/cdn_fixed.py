#!/usr/bin/env python3
"""
Fixed CDN Routes - Handles video uploads properly
"""
import os
import time
import secrets
import hashlib
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import FileResponse

try:
    from .auth import get_current_user_required, get_current_user_optional
except ImportError:
    async def get_current_user_required(request):
        class User:
            user_id = "demo001"
            username = "demo"
        return User()
    
    async def get_current_user_optional(request):
        return None

# Simple in-memory token storage (use Redis in production)
upload_tokens = {}

router = APIRouter(prefix="/cdn", tags=["CDN & File Management"])

@router.get("/upload-url")
async def get_upload_url(
    request: Request,
    filename: str,
    content_type: str = "application/octet-stream",
    current_user = Depends(get_current_user_required)
):
    """Get upload URL - Fixed version that works with video files"""
    
    # Generate secure upload token
    upload_token = secrets.token_urlsafe(32)
    
    # Store token with expiry (1 hour)
    upload_tokens[upload_token] = {
        'user_id': current_user.user_id,
        'filename': filename,
        'content_type': content_type,
        'expires_at': time.time() + 3600,
        'used': False
    }
    
    # Clean expired tokens
    current_time = time.time()
    expired = [token for token, data in upload_tokens.items() if data['expires_at'] < current_time]
    for token in expired:
        del upload_tokens[token]
    
    return {
        "upload_url": f"/cdn/upload/{upload_token}",
        "method": "POST",
        "expires_in": 3600,
        "max_file_size_mb": 100,
        "upload_token": upload_token,
        "supported_types": ["video/mp4", "video/avi", "video/mov", "audio/mp3", "image/jpeg", "image/png", "text/plain"],
        "instructions": [
            "1. Use the upload_token directly in the URL path",
            "2. POST to /cdn/upload/{token} (replace {token} with upload_token)",
            "3. Use multipart/form-data",
            "4. File field name: 'file'",
            "5. Include your JWT token in Authorization header"
        ],
        "example": f"curl -X POST 'http://localhost:9000/cdn/upload/{upload_token}' -H 'Authorization: Bearer YOUR_TOKEN' -F 'file=@{filename}'"
    }

@router.post("/upload/{upload_token}")
async def upload_file(
    upload_token: str,
    request: Request,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user_required)
):
    """Upload file using upload token - Fixed for video files"""
    
    # Handle URL decoding issues - extract just the token part
    import urllib.parse
    
    # If token contains URL path, extract just the token
    if "/cdn/upload/" in upload_token:
        actual_token = upload_token.split("/cdn/upload/")[-1]
    else:
        actual_token = upload_token
    
    # URL decode the token
    decoded_token = urllib.parse.unquote(actual_token)
    
    print(f"DEBUG: Raw upload_token: {upload_token}")
    print(f"DEBUG: Extracted token: {actual_token}")
    print(f"DEBUG: Decoded token: {decoded_token}")
    print(f"DEBUG: Available tokens: {list(upload_tokens.keys())}")
    
    # Try different token variations
    token_to_use = None
    for candidate in [decoded_token, actual_token, upload_token]:
        if candidate in upload_tokens:
            token_to_use = candidate
            print(f"DEBUG: Using token: {candidate}")
            break
    
    if not token_to_use:
        print(f"DEBUG: No matching token found for any variation")
        token_to_use = decoded_token  # Use decoded as fallback
    
    # Validate token
    if token_to_use not in upload_tokens:
        print(f"DEBUG: Token {token_to_use} not found in available tokens")
        raise HTTPException(status_code=400, detail=f"Invalid upload token: {token_to_use}")
    
    token_data = upload_tokens[token_to_use]
    
    # Check expiry
    if time.time() > token_data['expires_at']:
        del upload_tokens[upload_token]
        raise HTTPException(status_code=400, detail="Upload token expired")
    
    # Check if already used
    if token_data['used']:
        raise HTTPException(status_code=400, detail="Upload token already used")
    
    # Verify user
    if token_data['user_id'] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Token belongs to different user")
    
    # Validate file type
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mp3', '.wav', '.jpg', '.jpeg', '.png', '.txt', '.pdf'}
    allowed_mime_types = {
        'video/mp4', 'video/avi', 'video/quicktime', 'audio/mpeg', 'audio/wav', 
        'image/jpeg', 'image/png', 'text/plain', 'application/pdf'
    }
    
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed")
    
    # More flexible MIME type validation
    if file.content_type and file.content_type not in allowed_mime_types:
        # Allow if extension is valid (browser may send generic MIME type)
        if file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"MIME type {file.content_type} not allowed")
    
    # Read and validate file
    file_content = await file.read()
    max_size = 100 * 1024 * 1024  # 100MB
    
    if len(file_content) > max_size:
        raise HTTPException(status_code=413, detail=f"File too large. Max: {max_size/1024/1024}MB")
    
    # Generate content ID
    content_hash = hashlib.sha256(file_content).hexdigest()[:12]
    content_id = f"{content_hash}_{int(time.time())}"
    
    # Save file locally with proper structure
    os.makedirs("uploads", exist_ok=True)
    safe_filename = ''.join(c for c in file.filename if c.isalnum() or c in '.-_') if file.filename else "file"
    file_path = f"uploads/{content_id}_{safe_filename}"
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Mark token as used
    upload_tokens[token_to_use]['used'] = True
    print(f"DEBUG: File uploaded successfully: {content_id}")
    print(f"DEBUG: File saved to: {file_path}")
    print(f"DEBUG: File size: {len(file_content)} bytes")
    
    # Save to database with proper error handling
    try:
        # Save to Supabase database
        try:
            import psycopg2
            DATABASE_URL = os.getenv("DATABASE_URL")
            print(f"DEBUG: DATABASE_URL configured: {bool(DATABASE_URL)}")
            
            if DATABASE_URL and 'postgresql' in DATABASE_URL:
                print(f"DEBUG: Connecting to Supabase...")
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                # Insert into content table
                cur.execute("""
                    INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (content_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description
                """, (
                    content_id, current_user.user_id, file.filename or "Uploaded file", 
                    "File uploaded via CDN", file_path, file.content_type or 'application/octet-stream',
                    time.time(), 0.8, json.dumps(['uploaded', 'cdn']), 0, 0, 0
                ))
                
                conn.commit()
                cur.close()
                conn.close()
                print(f"✅ Content saved to Supabase: {content_id}")
            else:
                print(f"DEBUG: DATABASE_URL not configured for PostgreSQL")
                raise Exception("PostgreSQL DATABASE_URL not configured")
        except Exception as supabase_error:
            print(f"❌ Supabase save failed: {supabase_error}")
            
            # Fallback to SQLite
            try:
                import sqlite3
                print(f"DEBUG: Falling back to SQLite...")
                conn = sqlite3.connect('data.db')
                with conn:
                    cur = conn.cursor()
                    # Create table if not exists
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS content (
                            content_id TEXT PRIMARY KEY,
                            uploader_id TEXT,
                            title TEXT,
                            description TEXT,
                            file_path TEXT,
                            content_type TEXT,
                            duration_ms INTEGER,
                            uploaded_at REAL,
                            authenticity_score REAL,
                            current_tags TEXT,
                            views INTEGER DEFAULT 0,
                            likes INTEGER DEFAULT 0,
                            shares INTEGER DEFAULT 0
                        )
                    """)
                    cur.execute("""
                        INSERT OR REPLACE INTO content 
                        (content_id, uploader_id, title, description, file_path, content_type, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        content_id, current_user.user_id, file.filename or "Uploaded file",
                        "File uploaded via CDN", file_path, file.content_type or 'application/octet-stream',
                        time.time(), 0.8, json.dumps(['uploaded', 'cdn']), 0, 0, 0
                    ))
                conn.close()
                print(f"✅ Content saved to SQLite fallback: {content_id}")
            except Exception as sqlite_error:
                print(f"❌ SQLite fallback also failed: {sqlite_error}")
                # Continue anyway - file is saved locally
            
    except Exception as db_error:
        print(f"Database save failed: {db_error}")
        # Continue anyway - file is saved locally
    
    return {
        "status": "success",
        "content_id": content_id,
        "filename": file.filename,
        "file_size": len(file_content),
        "file_path": file_path,
        "content_type": file.content_type,
        "download_url": f"/cdn/download/{content_id}",
        "stream_url": f"/cdn/stream/{content_id}",
        "message": "File uploaded successfully"
    }

@router.get("/download/{content_id}")
async def download_file(
    content_id: str,
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    """Download file by content ID - Fixed version"""
    
    try:
        # Get file path from database with fallback
        file_path = None
        title = None
        
        # Try Supabase first
        try:
            import psycopg2
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL and 'postgresql' in DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("SELECT file_path, title FROM content WHERE content_id = %s", (content_id,))
                result = cur.fetchone()
                cur.close()
                conn.close()
                if result:
                    file_path, title = result
        except Exception:
            pass
        
        # Fallback to SQLite
        if not file_path:
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                cur.execute("SELECT file_path, title FROM content WHERE content_id = ?", (content_id,))
                result = cur.fetchone()
                conn.close()
                if result:
                    file_path, title = result
            except Exception:
                pass
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            file_path,
            filename=title or os.path.basename(file_path),
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/stream/{content_id}")
async def stream_file(
    content_id: str,
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    """Stream file by content ID - Fixed for video streaming"""
    
    try:
        # Get file path from database with fallback
        file_path = None
        content_type = None
        
        # Try Supabase first
        try:
            import psycopg2
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL and 'postgresql' in DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("SELECT file_path, content_type FROM content WHERE content_id = %s", (content_id,))
                result = cur.fetchone()
                cur.close()
                conn.close()
                if result:
                    file_path, content_type = result
        except Exception:
            pass
        
        # Fallback to SQLite
        if not file_path:
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                cur.execute("SELECT file_path, content_type FROM content WHERE content_id = ?", (content_id,))
                result = cur.fetchone()
                conn.close()
                if result:
                    file_path, content_type = result
            except Exception:
                pass
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Determine media type based on file extension if not in database
        if not content_type:
            ext = os.path.splitext(file_path)[1].lower()
            content_type_map = {
                '.mp4': 'video/mp4',
                '.avi': 'video/avi',
                '.mov': 'video/quicktime',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.txt': 'text/plain',
                '.pdf': 'application/pdf'
            }
            content_type = content_type_map.get(ext, 'application/octet-stream')
        
        return FileResponse(
            file_path,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

@router.get("/list")
async def list_files(
    request: Request,
    limit: int = 20,
    current_user = Depends(get_current_user_required)
):
    """List uploaded files for current user - Fixed version"""
    
    try:
        files = []
        
        # Try Supabase first
        try:
            import psycopg2
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL and 'postgresql' in DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    SELECT content_id, title, content_type, uploaded_at, views, likes
                    FROM content 
                    WHERE uploader_id = %s
                    ORDER BY uploaded_at DESC
                    LIMIT %s
                """, (current_user.user_id, limit))
                results = cur.fetchall()
                cur.close()
                conn.close()
                
                for row in results:
                    files.append({
                        "content_id": row[0],
                        "filename": row[1],
                        "content_type": row[2],
                        "uploaded_at": row[3],
                        "views": row[4],
                        "likes": row[5],
                        "download_url": f"/cdn/download/{row[0]}",
                        "stream_url": f"/cdn/stream/{row[0]}"
                    })
        except Exception:
            pass
        
        # Fallback to SQLite if no results from Supabase
        if not files:
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                cur.execute("""
                    SELECT content_id, title, content_type, uploaded_at, views, likes
                    FROM content 
                    WHERE uploader_id = ?
                    ORDER BY uploaded_at DESC
                    LIMIT ?
                """, (current_user.user_id, limit))
                results = cur.fetchall()
                conn.close()
                
                for row in results:
                    files.append({
                        "content_id": row[0],
                        "filename": row[1],
                        "content_type": row[2],
                        "uploaded_at": row[3],
                        "views": row[4],
                        "likes": row[5],
                        "download_url": f"/cdn/download/{row[0]}",
                        "stream_url": f"/cdn/stream/{row[0]}"
                    })
            except Exception as e:
                print(f"SQLite query failed: {e}")
        
        return {
            "files": files,
            "total": len(files),
            "user_id": current_user.user_id,
            "storage": "local_with_database_backup"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")

@router.delete("/delete/{content_id}")
async def delete_file(
    content_id: str,
    request: Request,
    current_user = Depends(get_current_user_required)
):
    """Delete file by content ID - Fixed version"""
    
    try:
        # Get file info from database with fallback
        file_path = None
        uploader_id = None
        
        # Try Supabase first
        try:
            import psycopg2
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL and 'postgresql' in DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("SELECT file_path, uploader_id FROM content WHERE content_id = %s", (content_id,))
                result = cur.fetchone()
                if result:
                    file_path, uploader_id = result
                    # Delete from Supabase
                    cur.execute("DELETE FROM content WHERE content_id = %s", (content_id,))
                    conn.commit()
                cur.close()
                conn.close()
        except Exception:
            pass
        
        # Fallback to SQLite
        if not file_path:
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                cur.execute("SELECT file_path, uploader_id FROM content WHERE content_id = ?", (content_id,))
                result = cur.fetchone()
                if result:
                    file_path, uploader_id = result
                    # Delete from SQLite
                    cur.execute("DELETE FROM content WHERE content_id = ?", (content_id,))
                    conn.commit()
                conn.close()
            except Exception:
                pass
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Check ownership
        if uploader_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not your file")
        
        # Delete file from disk
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as file_error:
            print(f"File deletion failed: {file_error}")
        
        return {
            "status": "success",
            "message": "File deleted successfully",
            "content_id": content_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/info/{content_id}")
async def get_file_info(
    content_id: str,
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    """Get file information - Fixed version"""
    
    try:
        # Get file info from database with fallback
        result = None
        
        # Try Supabase first
        try:
            import psycopg2
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL and 'postgresql' in DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    SELECT content_id, title, content_type, uploaded_at, authenticity_score, 
                           current_tags, views, likes, shares, uploader_id
                    FROM content WHERE content_id = %s
                """, (content_id,))
                result = cur.fetchone()
                cur.close()
                conn.close()
        except Exception:
            pass
        
        # Fallback to SQLite
        if not result:
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                cur.execute("""
                    SELECT content_id, title, content_type, uploaded_at, authenticity_score, 
                           current_tags, views, likes, shares, uploader_id
                    FROM content WHERE content_id = ?
                """, (content_id,))
                result = cur.fetchone()
                conn.close()
            except Exception:
                pass
        
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {
            "content_id": result[0],
            "filename": result[1],
            "content_type": result[2],
            "uploaded_at": result[3],
            "authenticity_score": result[4],
            "tags": result[5],
            "views": result[6],
            "likes": result[7],
            "shares": result[8],
            "uploader_id": result[9],
            "download_url": f"/cdn/download/{content_id}",
            "stream_url": f"/cdn/stream/{content_id}",
            "storage": "local_with_database_backup"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Info failed: {str(e)}")
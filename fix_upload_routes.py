#!/usr/bin/env python3
"""
Fix upload routes to save data to Supabase database
"""

def create_fixed_upload_function():
    """Create a fixed upload function that saves to both bucket and database"""
    
    upload_code = '''
@step3_router.post('/upload')
async def upload_content(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...)
):
    """Upload content and save to both bucket and Supabase database"""
    
    try:
        # Get user info
        try:
            current_user = await get_current_user_optional(request)
            user_id = current_user.user_id if current_user else 'anonymous'
        except:
            user_id = 'anonymous'
        
        # Generate content ID
        content_id = f"content_{int(time.time())}_{user_id}"
        
        # Save file to bucket
        file_content = await file.read()
        file_path = f"uploads/{content_id}_{file.filename}"
        
        # Save to local bucket
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Prepare content data for database
        content_data = {
            'content_id': content_id,
            'uploader_id': user_id,
            'title': title,
            'description': description,
            'file_path': file_path,
            'content_type': file.content_type or 'application/octet-stream',
            'duration_ms': len(file_content),  # Use file size as duration
            'uploaded_at': time.time(),
            'authenticity_score': 0.8,  # Default score
            'current_tags': '',
            'views': 0,
            'likes': 0,
            'shares': 0
        }
        
        # Save to Supabase database
        database_saved = False
        try:
            DATABASE_URL = os.getenv("DATABASE_URL")
            if DATABASE_URL and "postgresql" in DATABASE_URL:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                # Insert content
                cur.execute("""
                    INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (content_id) DO NOTHING
                """, (
                    content_data['content_id'], content_data['uploader_id'], content_data['title'],
                    content_data['description'], content_data['file_path'], content_data['content_type'],
                    content_data['duration_ms'], content_data['uploaded_at'], content_data['authenticity_score'],
                    content_data['current_tags'], content_data['views'], content_data['likes'], content_data['shares']
                ))
                
                # Log the upload
                cur.execute("""
                    INSERT INTO system_logs (level, message, module, timestamp, user_id, request_path)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('INFO', f'File uploaded: {title}', 'upload', time.time(), user_id, '/upload'))
                
                # Track analytics
                cur.execute("""
                    INSERT INTO analytics (event_type, user_id, content_id, event_data, timestamp, ip_address)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('file_upload', user_id, content_id, 
                      json.dumps({'filename': file.filename, 'size': len(file_content)}),
                      time.time(), request.client.host if request.client else 'unknown'))
                
                conn.commit()
                cur.close()
                conn.close()
                database_saved = True
                print(f"[OK] Upload saved to Supabase: {content_id}")
                
        except Exception as db_error:
            print(f"[WARN] Database save failed: {db_error}")
            # Continue with bucket-only save
        
        # Track with monitoring
        try:
            if 'posthog_manager' in globals():
                posthog_manager.track_event(user_id, 'content_upload', {
                    'content_id': content_id,
                    'filename': file.filename,
                    'size': len(file_content),
                    'database_saved': database_saved
                })
        except:
            pass
        
        return {
            'content_id': content_id,
            'message': 'Upload successful',
            'file_path': file_path,
            'database_saved': database_saved,
            'bucket_saved': True,
            'size': len(file_content),
            'timestamp': time.time()
        }
        
    except Exception as e:
        # Log error
        try:
            if 'sentry_manager' in globals():
                sentry_manager.capture_exception(e, {'endpoint': '/upload'})
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
'''
    
    with open('fixed_upload_route.py', 'w') as f:
        f.write(upload_code)
    
    print("[OK] Created fixed upload route")

if __name__ == "__main__":
    create_fixed_upload_function()
    print("Fixed upload function created - integrate into your routes.py")
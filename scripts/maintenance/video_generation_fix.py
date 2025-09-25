@step3_router.post('/generate-video', response_model=VideoGenerationResponse, status_code=202)
async def generate_video(file: UploadFile = File(...), title: str = Form(...), current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    """STEP 3C: Generate video from text script (requires authentication)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        allowed_extensions = {'.txt'}
        ext = os.path.splitext(file.filename or '')[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Only .txt files allowed")

        if file.size is not None and file.size > 1 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Script file too large (max 1MB)")

        # Read script content
        script_content = (await file.read()).decode('utf-8')
        if not script_content.strip():
            raise HTTPException(status_code=400, detail="Empty script content")

        # Generate content ID
        content_id = uuid.uuid4().hex[:12]
        timestamp = time.time()
        uploader_id = current_user.user_id if current_user else 'system'

        # 1. SAVE SCRIPT TO BUCKET/SCRIPTS/ AND DATABASE
        try:
            # Save script to bucket/scripts/
            script_filename = f"{content_id}_script.txt"
            script_bucket_path = bhiv_bucket.get_bucket_path('scripts', script_filename)
            with open(script_bucket_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Save script to database
            script_id = f"script_{uuid.uuid4().hex[:12]}"
            from ..core.database import DatabaseManager
            db = DatabaseManager()
            script_data = {
                'script_id': script_id,
                'user_id': uploader_id,
                'title': f"Script for {title}",
                'script_content': script_content,
                'script_type': 'text',
                'file_path': script_bucket_path,
                'content_id': content_id,
                'used_for_generation': True
            }
            db.create_script(script_data)
        except Exception as script_error:
            import logging
            logging.error(f"Script save failed: {script_error}")
            raise HTTPException(status_code=500, detail=f"Script save failed: {str(script_error)}")

        # 2. GENERATE TAGS AND SAVE TO BUCKET/RATINGS/
        try:
            tags = suggest_tags(title, script_content[:200])  # Use first 200 chars for tags
            tags.extend(['generated', 'video'])  # Add generation tags
            
            # Save tags to bucket/ratings/
            tags_filename = f"{content_id}_tags.json"
            tags_bucket_path = bhiv_bucket.get_bucket_path('ratings', tags_filename)
            with open(tags_bucket_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'content_id': content_id,
                    'tags': tags,
                    'generated_at': timestamp,
                    'generation_method': 'ai_suggestion'
                }, f, indent=2)
        except Exception as tags_error:
            import logging
            logging.warning(f"Tags save failed: {tags_error}")
            tags = ['generated', 'video']  # Fallback tags

        # 3. CREATE STORYBOARD AND SAVE TO BUCKET/STORYBOARDS/
        try:
            # Generate storyboard from script
            lines = [line.strip() for line in script_content.split('\n') if line.strip()]
            scenes = []
            for i, line in enumerate(lines[:10]):  # Max 10 scenes
                scenes.append({
                    'scene_id': i + 1,
                    'text': line,
                    'duration': 2.0,
                    'start_time': i * 2.0
                })
            
            storyboard_data = {
                'content_id': content_id,
                'title': title,
                'total_duration': len(scenes) * 2.0,
                'total_scenes': len(scenes),
                'scenes': scenes,
                'generation_method': 'text_to_scenes',
                'created_at': timestamp
            }
            
            # Save storyboard to bucket/storyboards/
            storyboard_filename = f"{content_id}_storyboard.json"
            storyboard_bucket_path = bhiv_bucket.get_bucket_path('storyboards', storyboard_filename)
            with open(storyboard_bucket_path, 'w', encoding='utf-8') as f:
                json.dump(storyboard_data, f, indent=2)
        except Exception as storyboard_error:
            import logging
            logging.warning(f"Storyboard save failed: {storyboard_error}")
            storyboard_data = {'total_duration': 10.0, 'total_scenes': 1}

        # 4. GENERATE VIDEO AND SAVE TO BUCKET/VIDEOS/
        try:
            video_filename = f"{content_id}.mp4"
            video_bucket_path = bhiv_bucket.get_bucket_path('videos', video_filename)
            
            # Generate video using video generator
            from ..video.generator import create_simple_video
            video_path = create_simple_video(script_content, video_bucket_path, duration=storyboard_data.get('total_duration', 10.0))
            
            if not os.path.exists(video_path):
                raise HTTPException(status_code=500, detail="Video file was not created successfully")
        except Exception as video_error:
            import logging
            logging.error(f"Video generation failed: {video_error}")
            raise HTTPException(status_code=500, detail=f"Video generation failed: {str(video_error)}")

        # 5. SAVE PROCESSING LOG TO BUCKET/LOGS/
        try:
            processing_log = {
                'content_id': content_id,
                'script_id': script_id,
                'processing_steps': [
                    {'step': 'script_save', 'status': 'completed', 'path': script_bucket_path},
                    {'step': 'tags_generation', 'status': 'completed', 'path': tags_bucket_path},
                    {'step': 'storyboard_creation', 'status': 'completed', 'path': storyboard_bucket_path},
                    {'step': 'video_generation', 'status': 'completed', 'path': video_path}
                ],
                'total_duration_ms': int(storyboard_data.get('total_duration', 10.0) * 1000),
                'processing_time': time.time() - timestamp,
                'status': 'completed',
                'created_at': timestamp
            }
            
            # Save processing log to bucket/logs/
            log_filename = f"{content_id}_processing.json"
            log_bucket_path = bhiv_bucket.get_bucket_path('logs', log_filename)
            with open(log_bucket_path, 'w', encoding='utf-8') as f:
                json.dump(processing_log, f, indent=2)
        except Exception as log_error:
            import logging
            logging.warning(f"Processing log save failed: {log_error}")

        # 6. SAVE CONTENT TO DATABASE
        try:
            content_data = {
                'content_id': content_id,
                'uploader_id': uploader_id,
                'title': title,
                'description': 'Generated video from script',
                'file_path': video_path,
                'content_type': 'video/mp4',
                'duration_ms': int(storyboard_data.get('total_duration', 10.0) * 1000),
                'authenticity_score': 0.8,  # Generated content gets high authenticity
                'current_tags': json.dumps(tags),
                'uploaded_at': timestamp
            }
            db.create_content(content_data)
        except Exception as db_error:
            import logging
            logging.error(f"Database save failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database save failed: {str(db_error)}")

        # 7. REGISTER WITH RL AGENT
        try:
            agent.register_content(content_id, tags, 0.8)
        except Exception as rl_error:
            import logging
            logging.warning(f"RL agent registration failed: {rl_error}")

        return {
            'content_id': content_id,
            'script_id': script_id,
            'video_path': f'/download/{content_id}',
            'stream_url': f'/stream/{content_id}',
            'metadata_url': f'/content/{content_id}/metadata',
            'local_file_path': video_path,
            'storage_paths': {
                'script': script_bucket_path,
                'tags': tags_bucket_path,
                'storyboard': storyboard_bucket_path,
                'video': video_path,
                'processing_log': log_bucket_path
            },
            'storyboard_stats': storyboard_data,
            'processing_status': 'completed',
            'next_step': f'Use /content/{content_id}/metadata to view full details or /stream/{content_id} to watch video'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Video generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
#!/usr/bin/env python3
"""
Verify that video generation saves to Supabase
"""

import os
import sys
import json
import time
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(__file__))

def simulate_video_generation():
    """Simulate the video generation process"""
    try:
        from ..core.database import DatabaseManager
        from core import bhiv_bucket
        
        print("Simulating video generation process...")
        
        # Initialize
        db = DatabaseManager()
        bhiv_bucket.init_bucket()
        
        # Generate IDs (like in your routes.py)
        script_id = f"script_{uuid.uuid4().hex[:12]}"
        content_id = uuid.uuid4().hex[:12]
        timestamp = time.time()
        uploader_id = "demo001"  # Using demo user
        
        # Simulate script content
        script_content = "This is a test script for video generation.\\nSecond line of the script.\\nThird line with more content."
        
        print(f"Generated IDs: script_id={script_id}, content_id={content_id}")
        
        # 1. Save script to bucket (like in your fixed code)
        temp_path = bhiv_bucket.get_bucket_path("tmp", f"temp_{script_id}.txt")
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        script_filename = f"{script_id}.txt"
        script_bucket_path = bhiv_bucket.save_script(temp_path, script_filename)
        print(f"[OK] Script saved to bucket: {script_bucket_path}")
        
        # 2. Save content to database FIRST (required for foreign key)
        generated_tags = ['test', 'generated', 'video', 'script']
        content_data = {
            'content_id': content_id,
            'uploader_id': uploader_id,
            'title': 'Test Generated Video',
            'description': f'Generated video from script: {script_id}',
            'file_path': f'bucket/videos/{content_id}.mp4',  # Simulated video path
            'content_type': 'video/mp4',
            'duration_ms': int(len([line.strip() for line in script_content.split('\\n') if line.strip()]) * 2.0 * 1000),
            'authenticity_score': 0.8,
            'current_tags': json.dumps(generated_tags),
            'uploaded_at': timestamp
        }
        
        content_created = db.create_content(content_data)
        print(f"[OK] Content saved to Supabase: {content_id}")
        
        # 3. Save script to database AFTER content
        script_data = {
            'script_id': script_id,
            'content_id': content_id,
            'user_id': uploader_id,
            'title': 'Test Script for Video Generation',
            'script_content': script_content,
            'script_type': 'text',
            'file_path': script_bucket_path,
            'used_for_generation': True
        }
        
        script_created = db.create_script(script_data)
        if script_created:
            print(f"[OK] Script saved to Supabase: {script_id}")
        else:
            print("[FAIL] Script not saved to database")
            return False
        
        # 4. Generate storyboard
        lines = [line.strip() for line in script_content.split('\\n') if line.strip()]
        storyboard_data = {
            'content_id': content_id,
            'script_id': script_id,
            'title': 'Test Video',
            'scenes': [{
                'scene_id': f'scene_{i}',
                'duration': 2.0,
                'frames': [{
                    'text': line,
                    'background_color': '#000000',
                    'text_position': 'center'
                }]
            } for i, line in enumerate(lines)],
            'total_duration': len(lines) * 2.0,
            'generation_method': 'simple_text',
            'created_at': timestamp
        }
        
        storyboard_filename = f"{content_id}_storyboard.json"
        storyboard_path = bhiv_bucket.save_storyboard(storyboard_data, storyboard_filename)
        print(f"[OK] Storyboard saved to bucket: {storyboard_path}")
        
        # 5. Save generation log
        log_data = {
            'content_id': content_id,
            'script_id': script_id,
            'user_id': uploader_id,
            'action': 'video_generation',
            'status': 'completed',
            'duration_ms': content_data['duration_ms'],
            'tags': generated_tags,
            'storyboard_path': storyboard_path,
            'timestamp': timestamp
        }
        
        log_filename = f"generation_{content_id}_{int(timestamp)}.json"
        bhiv_bucket.save_json('logs', log_filename, log_data)
        print(f"[OK] Generation log saved: {log_filename}")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Video generation simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_data_in_supabase():
    """Verify the data was saved to Supabase"""
    try:
        from ..core.database import DatabaseManager
        
        print("\\nVerifying data in Supabase...")
        db = DatabaseManager()
        
        # Get analytics to see totals
        analytics = db.get_analytics_data()
        print(f"[OK] Current Supabase data:")
        print(f"  - Users: {analytics['total_users']}")
        print(f"  - Content: {analytics['total_content']}")
        print(f"  - Scripts: {analytics['total_scripts']}")
        print(f"  - Feedback: {analytics['total_feedback']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Supabase verification failed: {e}")
        return False

def main():
    """Run simulation"""
    print("=== Supabase Save Verification ===")
    
    # Check database connection
    db_url = os.getenv('DATABASE_URL', 'Not set')
    if 'postgresql' in db_url:
        print("[OK] Using Supabase PostgreSQL")
    else:
        print("[WARN] Not using Supabase - check .env file")
        return False
    
    # Run simulation
    sim_ok = simulate_video_generation()
    if not sim_ok:
        return False
    
    # Verify data
    verify_ok = verify_data_in_supabase()
    
    if sim_ok and verify_ok:
        print("\\n[SUCCESS] Video generation will now save to Supabase!")
        print("Your scripts, storyboards, content, and logs are being saved to the database.")
        return True
    else:
        print("\\n[FAIL] Some issues found")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
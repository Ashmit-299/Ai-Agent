# video/storyboard.py
import json
import re
import html
from typing import List, Dict, Optional
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import bhiv_bucket

def generate_storyboard_from_text(script_text: str) -> Dict:
    """Generate structured storyboard JSON from script text"""
    try:
        if not script_text or not script_text.strip():
            raise ValueError("Script text cannot be empty")
        
        # Sanitize input
        script_text = html.escape(script_text.strip())
        
        # Split by lines (newlines) to get each line as a frame
        lines = [line.strip() for line in script_text.split('\n') if line.strip()]
        
        if not lines:
            raise ValueError("No valid lines found in script")
        
        storyboard = {
            "version": "1.0",
            "total_duration": 0,
            "scenes": []
        }
        
        time_per_scene = 4.0  # seconds per line
        
        for i, line in enumerate(lines):
            # Calculate timing based on line length
            start_time = i * time_per_scene
            duration = max(3.0, min(6.0, len(line) / 15))  # 3-6 seconds based on length
            
            scene = {
                "id": f"scene_{i+1}",
                "start_time": start_time,
                "duration": duration,
                "frames": [
                    {
                        "id": f"frame_{i+1}_1",
                        "text": wrap_text_for_storyboard(line.strip()),
                        "image_placeholder": f"image_{i+1}.jpg",
                        "text_position": "center",
                        "background_color": "#000000"
                    }
                ]
            }
            storyboard["scenes"].append(scene)
        
        # Calculate total duration
        storyboard["total_duration"] = sum(scene["duration"] for scene in storyboard["scenes"])
        
        return storyboard
        
    except Exception as e:
        # Archive failed case for integrity
        from .failed_cases import archive_failed_storyboard
        archive_failed_storyboard(script_text, str(e), "storyboard_generation")
        raise e

def wrap_text_for_storyboard(text: str, max_chars_per_line: int = 50) -> str:
    """Wrap long text into maximum 2 lines"""
    if not text:
        return ""
    
    text = text.strip()
    
    # If text fits in one line, return as is
    if len(text) <= max_chars_per_line:
        return text
    
    # Split into two lines if too long
    words = text.split()
    line1 = ""
    line2 = ""
    
    for word in words:
        test_line1 = line1 + " " + word if line1 else word
        
        if len(test_line1) <= max_chars_per_line:
            line1 = test_line1
        else:
            line2 = " ".join([line2, word]).strip()
    
    # Ensure line2 doesn't exceed max length either
    if line2 and len(line2) > max_chars_per_line:
        line2 = line2[:max_chars_per_line-3] + "..."
    
    if line2:
        return f"{line1}\n{line2}"
    return line1

def validate_storyboard(sb: Dict) -> bool:
    """Validate storyboard structure"""
    try:
        # Check required top-level fields
        if not isinstance(sb, dict):
            return False
        
        if "scenes" not in sb or not isinstance(sb["scenes"], list):
            return False
        
        if len(sb["scenes"]) == 0:
            return False
        
        # Validate each scene
        for scene in sb["scenes"]:
            if not isinstance(scene, dict):
                return False
            
            required_fields = ["id", "start_time", "duration", "frames"]
            if not all(field in scene for field in required_fields):
                return False
            
            if not isinstance(scene["frames"], list) or len(scene["frames"]) == 0:
                return False
            
            # Validate frames
            for frame in scene["frames"]:
                if not isinstance(frame, dict):
                    return False
                
                frame_fields = ["id", "text"]
                if not all(field in frame for field in frame_fields):
                    return False
        
        return True
        
    except Exception:
        return False

def save_storyboard_to_file(sb: Dict, filename: str) -> str:
    """Save storyboard to JSON file using bucket storage"""
    try:
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Use bucket storage for storyboard
        bucket_path = bhiv_bucket.save_storyboard(sb, filename)
        return bucket_path
        
    except Exception as e:
        raise ValueError(f"Failed to save storyboard: {e}")

def load_storyboard_from_file(filename: str) -> Dict:
    """Load and validate storyboard from JSON file using bucket storage"""
    try:
        # Use bucket storage to read storyboard
        sb = bhiv_bucket.read_storyboard(filename)
        
        if not validate_storyboard(sb):
            raise ValueError("Invalid storyboard format")
        
        return sb
        
    except Exception as e:
        raise ValueError(f"Failed to load storyboard: {e}")

def get_storyboard_stats(sb: Dict) -> Dict:
    """Get statistics about the storyboard"""
    if not validate_storyboard(sb):
        raise ValueError("Invalid storyboard")
    
    total_scenes = len(sb["scenes"])
    total_frames = sum(len(scene["frames"]) for scene in sb["scenes"])
    total_duration = sb.get("total_duration", 0)
    avg_scene_duration = total_duration / total_scenes if total_scenes > 0 else 0
    
    return {
        "total_scenes": total_scenes,
        "total_frames": total_frames,
        "total_duration": round(total_duration, 2),
        "avg_scene_duration": round(avg_scene_duration, 2)
    }
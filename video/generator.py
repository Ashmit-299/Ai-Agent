# video/generator.py
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core import bhiv_bucket
except ImportError:
    bhiv_bucket = None

def render_video_from_storyboard(storyboard: Dict, output_path: str, width: int = 1280, height: int = 720) -> str:
    """Create text representation of storyboard"""
    try:
        if not storyboard.get("scenes"):
            raise ValueError("No scenes in storyboard")
        
        content = f"""STORYBOARD CONTENT
{'=' * 50}

Resolution: {width}x{height}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}
SCENES:
{'=' * 50}

"""
        
        for i, scene in enumerate(storyboard["scenes"], 1):
            duration = scene.get("duration", 3.0)
            content += f"Scene {i} (Duration: {duration}s):\n"
            content += "-" * 30 + "\n"
            
            for j, frame in enumerate(scene.get("frames", []), 1):
                text = frame.get("text", "Sample Text")
                content += f"  Frame {j}: {text}\n"
            content += "\n"
        
        content += "\n" + "="*50 + "\nEND OF STORYBOARD\n" + "="*50
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"Storyboard text creation failed: {e}")

def create_simple_video(text: str, output_path: str, duration: float = 5.0) -> str:
    """Create a simple text file as video placeholder"""
    try:
        # Create a formatted text file instead of video
        text = str(text)[:1000] if text else "Sample Text"
        
        # Create HTML-like content for better presentation
        content = f"""VIDEO SCRIPT CONTENT
{'=' * 50}

Title: Generated Video
Duration: {duration} seconds
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}
SCRIPT CONTENT:
{'=' * 50}

{text}

{'=' * 50}
END OF SCRIPT
{'=' * 50}

Note: This is a text representation of the video content.
Video generation requires MoviePy which is not available.
"""
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"Text file creation failed: {e}")

def get_video_info(video_path: str) -> Dict:
    """Get basic information about generated video"""
    try:
        video_file = Path(video_path)
        
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        file_size = video_file.stat().st_size
        
        # Try to get video duration using moviepy
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(str(video_file)) as clip:
                duration = clip.duration
                fps = clip.fps
                size = clip.size
        except ImportError:
            # MoviePy not available, use fallback values
            duration = 0
            fps = 24
            size = (1920, 1080)
        except Exception:
            # Fallback values
            duration = 0
            fps = 24
            size = (1920, 1080)
        
        return {
            "file_path": str(video_file),
            "file_size_bytes": file_size,
            "duration_seconds": round(duration, 2),
            "fps": fps,
            "resolution": f"{size[0]}x{size[1]}" if size else "1920x1080"
        }
        
    except Exception as e:
        raise ValueError(f"Failed to get video info: {e}")
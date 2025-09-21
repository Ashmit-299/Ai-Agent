# video/generator.py
import os
from pathlib import Path
from typing import Dict, Optional
import textwrap
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core import bhiv_bucket
except ImportError:
    bhiv_bucket = None

# Simplified MoviePy configuration
try:
    import moviepy.config as config
    # Try to find ImageMagick automatically
    imagemagick_paths = [
        r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe",
        r"C:\Program Files\ImageMagick\magick.exe",
        "magick",  # System PATH
        "convert"  # Fallback
    ]
    for path in imagemagick_paths:
        if os.path.exists(path) or path in ["magick", "convert"]:
            config.IMAGEMAGICK_BINARY = path
            break
except:
    pass

def render_video_from_storyboard(storyboard: Dict, output_path: str, width: int = 1280, height: int = 720) -> str:
    """Simplified storyboard video rendering"""
    try:
        from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip
        
        if not storyboard.get("scenes"):
            raise ValueError("No scenes in storyboard")
        
        clips = []
        for scene in storyboard["scenes"]:
            duration = scene.get("duration", 3.0)
            
            for frame in scene.get("frames", []):
                text = frame.get("text", "Sample Text")[:100]
                
                # Create simple clip
                bg_clip = ColorClip(size=(width, height), color=(0, 0, 0), duration=duration)
                txt_clip = TextClip(
                    text,
                    fontsize=40,
                    color='white',
                    font='Arial'
                ).set_duration(duration).set_position('center')
                
                comp_clip = CompositeVideoClip([bg_clip, txt_clip])
                clips.append(comp_clip)
        
        if clips:
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(output_path, fps=24, verbose=False, logger=None)
            final_clip.close()
            for clip in clips:
                clip.close()
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"Storyboard rendering failed: {e}")

def create_simple_video(text: str, output_path: str, duration: float = 5.0) -> str:
    """Create a simple video with text overlay"""
    try:
        from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
        
        # Sanitize text
        text = str(text)[:500] if text else "Sample Text"
        
        # Create black background
        bg_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration)
        
        # Create text clip
        txt_clip = TextClip(
            text,
            fontsize=50,
            color='white',
            font='Arial',
            size=(1200, 600)
        ).set_duration(duration).set_position('center')
        
        # Composite video
        video = CompositeVideoClip([bg_clip, txt_clip])
        
        # Write video file
        video.write_videofile(
            output_path,
            fps=24,
            verbose=False,
            logger=None
        )
        
        # Clean up
        video.close()
        bg_clip.close()
        txt_clip.close()
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"Video creation failed: {e}")

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
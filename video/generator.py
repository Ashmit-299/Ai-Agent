# video/generator.py
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add the parent directory to sys.path to import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
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

def create_simple_video(text: str, output_path: str, duration: float = 10.0) -> str:
    """Create multi-frame video with each line in separate 3-second frame"""
    
    # First, try to import MoviePy
    try:
        import moviepy.editor as mp
        from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips
        moviepy_available = True
    except ImportError as import_error:
        moviepy_available = False
        import_error_msg = str(import_error)
    
    # If MoviePy is not available, create a text file instead
    if not moviepy_available:
        text_path = output_path.replace('.mp4', '.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Video Script: {text}\n\nVideo generation failed: {import_error_msg}")
        return text_path
    
    try:
        # Configure MoviePy to use ImageMagick
        import moviepy.config as config
        config.IMAGEMAGICK_BINARY = "magick"
        
        # Split text into sentences, remove \n characters
        text = str(text).replace('\n', ' ').replace('\\n', ' ') if text else "No content"
        # Split by sentence endings
        import re
        sentences = re.split(r'[.!?]+', text)
        lines = [sentence.strip() for sentence in sentences if sentence.strip()]
        if not lines:
            lines = [text]
        
        # Ensure output path ends with .mp4
        if not output_path.endswith('.mp4'):
            output_path = output_path.replace('.txt', '.mp4')
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        clips = []
        frame_duration = 3.0  # 3 seconds per frame
        
        for line in lines:
            # Wrap text to fit screen with margins
            words = line.split()
            wrapped_lines = []
            current_line = ""
            max_chars = 50  # Approximate characters per line
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) <= max_chars:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                        current_line = word
                    else:
                        wrapped_lines.append(word)
            
            if current_line:
                wrapped_lines.append(current_line)
            
            wrapped_text = '\n'.join(wrapped_lines)
            
            # Create background
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=frame_duration)
            
            # Create text clip using MoviePy with ImageMagick
            txt_clip = TextClip(
                wrapped_text,
                fontsize=80,
                color='white',
                font='Arial-Bold',
                align='center',
                size=(1720, None),
                method='caption'
            ).set_duration(frame_duration).set_position('center')
            
            # Composite the clips
            comp_clip = CompositeVideoClip([bg_clip, txt_clip])
            clips.append(comp_clip)
        
        # Concatenate all clips
        final_video = concatenate_videoclips(clips)
        
        # Export video
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_video.close()
        for clip in clips:
            clip.close()
        
        return str(output_path)
        
    except Exception as e:
        # Fallback to text file if video generation fails
        text_path = output_path.replace('.mp4', '.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Video Script: {text}\n\nVideo generation failed: {str(e)}")
        return text_path

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
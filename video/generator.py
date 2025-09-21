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
    """Create MP4 video with bold text, one sentence per frame"""
    try:
        from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips
        import re
        
        # Split text into sentences
        text = str(text)[:2000] if text else "Sample Text"
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            sentences = [line.strip() for line in text.split('\n') if line.strip()]
        if not sentences:
            sentences = ["Sample Text"]
        
        # Ensure output path ends with .mp4
        if not output_path.endswith('.mp4'):
            output_path = output_path.replace('.txt', '.mp4')
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        clips = []
        frame_duration = 3.0  # 3 seconds per sentence
        
        # Create a video clip for each sentence
        for sentence in sentences:
            # Create black background
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=frame_duration)
            
            # Create bold text clip
            try:
                txt_clip = TextClip(
                    sentence,
                    fontsize=80,
                    color='white',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(1700, 900)
                ).set_duration(frame_duration).set_position('center')
                
                # Composite the clips
                comp_clip = CompositeVideoClip([bg_clip, txt_clip])
                clips.append(comp_clip)
                
            except Exception:
                # Fallback: create simple text without bold
                try:
                    txt_clip = TextClip(
                        sentence,
                        fontsize=70,
                        color='white',
                        font='Arial'
                    ).set_duration(frame_duration).set_position('center')
                    
                    comp_clip = CompositeVideoClip([bg_clip, txt_clip])
                    clips.append(comp_clip)
                except:
                    # Last fallback: just background
                    clips.append(bg_clip)
        
        # Concatenate all clips
        final_video = concatenate_videoclips(clips)
        
        # Write video file
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_video.close()
        for clip in clips:
            clip.close()
        
        return output_path
        
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
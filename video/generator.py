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

# Configure paths for video generation
try:
    import moviepy.config as config  # type: ignore
    # Set the correct ImageMagick path for Windows
    imagemagick_path = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
    if os.path.exists(imagemagick_path):
        config.IMAGEMAGICK_BINARY = imagemagick_path
except ImportError:
    pass

# Check for FFmpeg availability
def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def render_video_from_storyboard(storyboard: Dict, output_path: str, width: int = 1920, height: int = 1080) -> str:
    """Render video from storyboard JSON using moviepy"""
    try:
        # Import moviepy with error handling
        try:
            from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip, VideoFileClip, AudioFileClip  # type: ignore
        except ImportError:
            raise ImportError("moviepy is required for video generation. Install with: pip install moviepy")
        
        # Validate inputs
        if not isinstance(storyboard, dict) or "scenes" not in storyboard:
            raise ValueError("Invalid storyboard format")
        
        if not storyboard["scenes"]:
            raise ValueError("No scenes found in storyboard")
        
        # Validate and sanitize output path
        safe_output_path = Path(output_path).resolve()
        if not str(safe_output_path).endswith('.mp4'):
            raise ValueError("Output file must have .mp4 extension")
        
        # Ensure output path is within allowed directories
        allowed_dirs = [Path('bucket').resolve(), Path('uploads').resolve(), Path('tmp').resolve()]
        if not any(str(safe_output_path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs):
            # If not in allowed dirs, use bucket/videos as default
            safe_output_path = Path('bucket/videos').resolve() / Path(output_path).name
        
        # Create output directory
        safe_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        clips = []
        
        for scene in storyboard["scenes"]:
            # Validate scene structure
            if not isinstance(scene, dict) or "frames" not in scene or not isinstance(scene["frames"], list):
                raise ValueError("Invalid scene structure in storyboard")
            duration = scene.get("duration", 5.0)
            audio_path = scene.get("audio_path")
            
            for frame in scene.get("frames", []):
                # Get frame properties
                text = frame.get("text", "")[:200]  # Limit text length
                bg_color = frame.get("background_color", "#000000")
                text_pos = frame.get("text_position", "center")
                
                # Convert hex color to RGB tuple
                if bg_color.startswith("#"):
                    bg_color = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                else:
                    bg_color = (0, 0, 0)  # Default black
                
                # Create background clip
                bg_clip = ColorClip(size=(width, height), color=bg_color, duration=duration)
                
                # Create text clip with ImageMagick
                if not text or text.strip() == "":
                    text = "Sample Text"
                
                # Wrap text properly
                wrapped_text = textwrap.fill(text, width=40)
                
                try:
                    txt_clip = TextClip(
                        wrapped_text,
                        fontsize=80,
                        color='white',
                        font='Arial-Bold',
                        align='center',
                        size=(width-200, height-200)  # Leave margin to prevent cutoff
                    ).set_duration(duration).set_position('center')
                    
                    # Composite video
                    comp_clip = CompositeVideoClip([bg_clip, txt_clip])
                    clips.append(comp_clip)
                    
                except Exception as e:
                    import logging
                    logging.warning(f"Text rendering failed, using background only: {e}")
                    clips.append(bg_clip)
        
        if not clips:
            raise ValueError("No valid clips generated")
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(clips)

        # Add background audio if specified in the storyboard
        if audio_path and os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(audio_path).set_duration(final_clip.duration)
                final_clip = final_clip.set_audio(audio_clip)
            except Exception as audio_e:
                import logging
                logging.warning(f"Could not add audio from {audio_path}: {audio_e}")
        
        # Use bucket storage for video output if available
        if bhiv_bucket:
            temp_output = bhiv_bucket.get_bucket_path("tmp", f"temp_{Path(safe_output_path).name}")
        else:
            temp_output = str(safe_output_path)
        
        # Write video file to temp location first
        final_clip.write_videofile(
            temp_output,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        # Move to final location in video bucket
        if bhiv_bucket:
            final_path = bhiv_bucket.save_video(temp_output, Path(safe_output_path).name)
            # Clean up temp file
            try:
                os.remove(temp_output)
            except (OSError, FileNotFoundError) as e:
                import logging
                logging.warning(f"Failed to clean up temp file {temp_output}: {e}")
            return final_path
        else:
            return str(safe_output_path)
        
    except Exception as e:
        raise ValueError(f"Video generation failed: {e}")

def create_simple_video(text: str, output_path: str, duration: float = 5.0) -> str:
    """Create a simple video with each line as a separate frame using FFmpeg"""
    import subprocess
    import tempfile
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Split text into lines
    text = str(text)[:1000] if text else "No content"
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        lines = [text]
    
    # Each frame lasts 3 seconds
    frame_duration = 3
    
    try:
        # Try FFmpeg approach first
        with tempfile.TemporaryDirectory() as temp_dir:
            video_parts = []
            
            for i, line in enumerate(lines):
                # Create a simple black video with text overlay using FFmpeg
                part_video = os.path.join(temp_dir, f"part_{i}.mp4")
                
                # Escape text for FFmpeg
                safe_text = line.replace("'", "\\'").replace('"', '\\"').replace(':', '\\:')[:50]
                
                try:
                    # Create video part with text overlay
                    cmd = [
                        'ffmpeg', '-y',
                        '-f', 'lavfi',
                        '-i', f'color=black:size=1280x720:duration={frame_duration}',
                        '-vf', f"drawtext=text='{safe_text}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2",
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        part_video
                    ]
                    
                    subprocess.run(cmd, check=True, capture_output=True)
                    video_parts.append(part_video)
                    
                except subprocess.CalledProcessError:
                    # If text overlay fails, create simple black video
                    cmd = [
                        'ffmpeg', '-y',
                        '-f', 'lavfi',
                        '-i', f'color=black:size=1280x720:duration={frame_duration}',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        part_video
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    video_parts.append(part_video)
            
            if video_parts:
                # Create concat file
                concat_file = os.path.join(temp_dir, 'concat.txt')
                with open(concat_file, 'w') as f:
                    for part in video_parts:
                        f.write(f"file '{part}'\n")
                
                # Concatenate all parts
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file,
                    '-c', 'copy',
                    output_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                return str(output_path)
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        # FFmpeg not available or failed, try MoviePy
        try:
            from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips  # type: ignore
            
            clips = []
            for line in lines:
                try:
                    bg_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=3.0)
                    txt_clip = TextClip(
                        line,
                        fontsize=50,
                        color='white',
                        align='center',
                        size=(1200, 600)
                    ).set_duration(3.0).set_position('center')
                    
                    frame_clip = CompositeVideoClip([bg_clip, txt_clip])
                    clips.append(frame_clip)
                except Exception:
                    bg_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=3.0)
                    clips.append(bg_clip)
            
            if clips:
                final_clip = concatenate_videoclips(clips)
                final_clip.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio=False,
                    verbose=False,
                    logger=None
                )
                final_clip.close()
                for clip in clips:
                    clip.close()
                return str(output_path)
                
        except ImportError:
            pass
    
    # Last resort - create placeholder
    text_path = str(Path(output_path).with_suffix('.txt'))
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(f"Video Content:\n{text}\n\n")
        f.write("Note: Video generation unavailable - FFmpeg and MoviePy not available")
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
        except:
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
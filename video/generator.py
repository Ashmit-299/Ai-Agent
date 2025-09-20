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

# Configure ImageMagick path for MoviePy
try:
    import moviepy.config as config
    # Set the correct ImageMagick path
    imagemagick_path = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
    if os.path.exists(imagemagick_path):
        config.IMAGEMAGICK_BINARY = imagemagick_path
except:
    pass

def render_video_from_storyboard(storyboard: Dict, output_path: str, width: int = 1920, height: int = 1080) -> str:
    """Render video from storyboard JSON using moviepy"""
    try:
        # Import moviepy with error handling
        try:
            from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip, VideoFileClip, AudioFileClip
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
    """Create a simple video with each line as a separate frame"""
    try:
        from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips
        
        # Validate and sanitize inputs
        text = str(text)[:1000] if text else "No content"
        
        # Split text into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            lines = [text]
        
        # Calculate duration per frame (2 seconds per line)
        frame_duration = 2.0
        
        # Use bucket storage for video output if available
        if bhiv_bucket:
            temp_output = bhiv_bucket.get_bucket_path("tmp", f"temp_{Path(output_path).name}")
        else:
            temp_output = f"tmp_temp_{Path(output_path).name}"
        
        clips = []
        
        # Create a clip for each line
        for line in lines:
            # Create background
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=frame_duration)
            
            # Create text clip with automatic line wrapping
            txt_clip = TextClip(
                line,
                fontsize=80,
                color='white',
                font='Arial-Bold',
                align='center',
                size=(1720, None),
                method='caption'
            ).set_duration(frame_duration).set_position('center')
            
            # Composite frame
            frame_clip = CompositeVideoClip([bg_clip, txt_clip])
            clips.append(frame_clip)
        
        # Concatenate all frames
        final_clip = concatenate_videoclips(clips)
        
        # Export video
        final_clip.write_videofile(
            temp_output,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        
        final_clip.close()
        for clip in clips:
            clip.close()
        
        # Move to final location
        if bhiv_bucket:
            final_path = bhiv_bucket.save_video(temp_output, Path(output_path).name)
            try:
                os.remove(temp_output)
            except (OSError, FileNotFoundError) as e:
                import logging
                logging.warning(f"Failed to clean up temp file {temp_output}: {e}")
            return final_path
        else:
            return str(output_path)
        
    except Exception as e:
        raise ValueError(f"Simple video creation failed: {e}")

def get_video_info(video_path: str) -> Dict:
    """Get basic information about generated video"""
    try:
        video_file = Path(video_path)
        
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        file_size = video_file.stat().st_size
        
        # Try to get video duration using moviepy
        try:
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
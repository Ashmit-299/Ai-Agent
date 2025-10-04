# video/generator.py
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add the parent directory to sys.path to import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Debug check for MoviePy
try:
    import moviepy.editor
    print("MoviePy successfully imported")
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    print(f"MoviePy import failed: {e}")
    MOVIEPY_AVAILABLE = False

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
        

        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"Storyboard text creation failed: {e}")

def create_simple_video(text: str, output_path: str, duration: float = 10.0) -> str:
    """Create a video with each sentence as a separate frame"""
    
    # Early check for MoviePy
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy is not installed. Run: pip install moviepy==1.0.3")
    
    try:
        from moviepy.editor import ColorClip, CompositeVideoClip, concatenate_videoclips
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        from moviepy.video.VideoClip import ImageClip
        import re
        
        # Clean text
        text = str(text) if text else "No content"
        
        # Split by both line breaks AND sentence endings - each gets its own frame
        parts = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # Split line by sentence endings
                line_parts = re.split(r'[.!?]', line)
                for part in line_parts:
                    part = part.strip()
                    if part:
                        parts.append(part)
        sentences = parts if parts else [text]
        
        # Each sentence gets 3 seconds
        frame_duration = 3.0
        clips = []
        
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 80)
            except:
                font = ImageFont.load_default()
        
        for sentence in sentences:
            # Create background clip for this sentence
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=frame_duration)
            
            # Create text image using PIL
            img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Try to keep sentence on single line first
            bbox = draw.textbbox((0, 0), sentence, font=font)
            max_width = 1600  # Leave margins
            
            if bbox[2] - bbox[0] <= max_width:
                # Sentence fits on one line
                text_lines = [sentence]
            else:
                # Only wrap if sentence exceeds frame width
                words = re.findall(r'\S+', sentence)
                text_lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            text_lines.append(current_line)
                        current_line = word
                
                if current_line:
                    text_lines.append(current_line)
            
            # Draw text centered
            text_to_draw = "\n".join(text_lines)
            bbox = draw.multiline_textbbox((0, 0), text_to_draw, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (1920 - text_width) // 2
            y = (1080 - text_height) // 2
            
            draw.multiline_text((x, y), text_to_draw, font=font, fill=(255, 255, 255, 255), align='center')
            
            # Convert PIL image to numpy array
            img_array = np.array(img)
            
            # Create ImageClip from the array
            text_clip = ImageClip(img_array, duration=frame_duration)
            
            # Composite the clips
            frame_clip = CompositeVideoClip([bg_clip, text_clip])
            clips.append(frame_clip)
        
        # Concatenate all sentence clips
        final_clip = concatenate_videoclips(clips)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export as MP4
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            verbose=False,
            logger=None
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        # Verify MP4 file was created
        if not os.path.exists(output_path) or not output_path.endswith('.mp4'):
            raise ValueError(f"Failed to create MP4 file: {output_path}")
            
        return str(output_path)
        
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

def create_multi_frame_video(text: str, output_path: str, frame_duration: float = 3.0) -> str:
    """
    Create a video where each sentence becomes its own frame.
    Each sentence stays on single line unless it exceeds frame width.
    """
    try:
        from moviepy.editor import ColorClip, CompositeVideoClip, concatenate_videoclips
        from moviepy.video.VideoClip import ImageClip
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        import re
    except ImportError:
        raise ImportError("moviepy and PIL are required: pip install moviepy==1.0.3 Pillow")

    # Split text by lines first, then by sentences - ensure no content is skipped
    sentences = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            # Split by sentence endings
            parts = re.split(r'[.!?]+', line)
            for part in parts:
                part = part.strip()
                if part:  # Only add non-empty parts
                    sentences.append(part)
    
    if not sentences:
        sentences = ["No content"]

    clips = []
    
    # Try to load a system font
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 80)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/calibri.ttf", 80)
            except:
                font = ImageFont.load_default()
    
    max_width = 1600  # Leave margins
    
    for sentence in sentences:
        # Create background clip
        bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=frame_duration)
        
        # Create text image using PIL
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Check if sentence fits on single line
        bbox = draw.textbbox((0, 0), sentence, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            # Single line
            display_text = sentence
        else:
            # Wrap text properly - handle all words
            words = sentence.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_bbox = draw.textbbox((0, 0), test_line, font=font)
                
                if test_bbox[2] - test_bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            display_text = "\n".join(lines)
        
        # Get final text dimensions
        bbox = draw.multiline_textbbox((0, 0), display_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2
        
        # Draw bold text with special characters support
        # Create bold effect by drawing text multiple times with slight offsets
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                draw.multiline_text((x+dx, y+dy), display_text, font=font, fill=(255, 255, 255, 255), align='center')
        # Draw main text on top for extra boldness
        draw.multiline_text((x, y), display_text, font=font, fill=(255, 255, 255, 255), align='center')
        
        # Convert PIL image to numpy array
        img_array = np.array(img)
        
        # Create ImageClip from the array
        text_clip = ImageClip(img_array, duration=frame_duration)
        
        # Composite the clips
        frame_clip = CompositeVideoClip([bg_clip, text_clip])
        clips.append(frame_clip)

    final_clip = concatenate_videoclips(clips, method="compose")
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

    if not os.path.exists(output_path):
        raise ValueError(f"Failed to create MP4 file: {output_path}")
    return output_path

def generate_from_storyboard(storyboard: Dict, content_id: str = None) -> Dict:
    """Generate video from storyboard data"""
    try:
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        # Extract text from storyboard scenes
        text_content = ""
        for scene in storyboard.get("scenes", []):
            for frame in scene.get("frames", []):
                frame_text = frame.get("text", "")
                if frame_text:
                    text_content += frame_text + "\n"
        
        if not text_content.strip():
            text_content = "Generated video content"
        
        # Create output filename
        output_filename = f"{content_id or job_id}.mp4"
        
        return {
            "job_id": job_id,
            "status": "enqueued",
            "content_id": content_id,
            "output_file": output_filename,
            "text_content": text_content.strip(),
            "total_duration": storyboard.get("total_duration", 10.0)
        }
        
    except Exception as e:
        return {
            "job_id": "error",
            "status": "failed",
            "error": str(e)
        }
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
    """Create a simple video with text overlay - No ImageMagick required"""
    
    # Early check for MoviePy
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy is not installed. Run: pip install moviepy==1.0.3")
    
    try:
        from moviepy.editor import ColorClip, CompositeVideoClip
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        from moviepy.video.VideoClip import ImageClip
        
        # Clean text
        text = str(text) if text else "No content"
        
        # Create background clip
        bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)
        
        # Create text image using PIL (no ImageMagick needed)
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 80)
            except:
                font = ImageFont.load_default()
        
        # Word wrap text
        words = text.split()
        lines = []
        current_line = ""
        max_width = 1600  # Leave margins
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw text centered
        text_to_draw = "\n".join(lines)
        bbox = draw.multiline_textbbox((0, 0), text_to_draw, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2
        
        draw.multiline_text((x, y), text_to_draw, font=font, fill=(255, 255, 255, 255), align='center')
        
        # Convert PIL image to numpy array
        img_array = np.array(img)
        
        # Create ImageClip from the array
        text_clip = ImageClip(img_array, duration=duration)
        
        # Composite the clips
        final_clip = CompositeVideoClip([bg_clip, text_clip])
        
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
        text_clip.close()
        bg_clip.close()
        
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
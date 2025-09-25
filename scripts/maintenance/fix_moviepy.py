#!/usr/bin/env python3

import sys
import subprocess
import os

def fix_moviepy():
    print("Fixing MoviePy installation...")
    
    # Install specific version that works
    subprocess.run([sys.executable, "-m", "pip", "install", "moviepy==1.0.3", "--force-reinstall"])
    
    # Test import
    try:
        from moviepy.editor import VideoClip, ImageClip
        print("✓ MoviePy 1.0.3 working!")
        return True
    except ImportError as e:
        print(f"✗ Still failing: {e}")
        return False

if __name__ == "__main__":
    fix_moviepy()
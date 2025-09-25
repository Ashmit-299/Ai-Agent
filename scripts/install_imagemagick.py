#!/usr/bin/env python3

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

def install_imagemagick():
    print("Installing ImageMagick...")
    
    # Create imagemagick directory
    im_dir = os.path.join(os.getcwd(), "imagemagick")
    os.makedirs(im_dir, exist_ok=True)
    
    # Download portable ImageMagick
    url = "https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-portable-Q16-x64.zip"
    zip_path = os.path.join(im_dir, "imagemagick.zip")
    
    try:
        print("Downloading ImageMagick...")
        urllib.request.urlretrieve(url, zip_path)
        
        print("Extracting ImageMagick...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(im_dir)
        
        # Find magick.exe
        magick_exe = None
        for root, dirs, files in os.walk(im_dir):
            if "magick.exe" in files:
                magick_exe = os.path.join(root, "magick.exe")
                break
        
        if magick_exe:
            print(f"ImageMagick installed at: {magick_exe}")
            
            # Configure MoviePy to use this ImageMagick
            config_content = f'''
import os
IMAGEMAGICK_BINARY = r"{magick_exe}"
'''
            
            # Write config to moviepy config
            try:
                import moviepy.config as config
                config.IMAGEMAGICK_BINARY = magick_exe
                print("MoviePy configured to use ImageMagick")
            except:
                pass
            
            return magick_exe
        else:
            print("Could not find magick.exe after extraction")
            return None
            
    except Exception as e:
        print(f"Failed to install ImageMagick: {e}")
        return None

if __name__ == "__main__":
    install_imagemagick()
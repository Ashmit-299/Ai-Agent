#!/usr/bin/env python3
"""
Dashboard Launcher - Start the futuristic Streamlit dashboard
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    packages = ['streamlit', 'plotly', 'pandas', 'requests']
    
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def main():
    print("Starting BHIV Analytics Dashboard...")
    
    # Install requirements
    install_requirements()
    
    # Run Streamlit dashboard
    dashboard_path = os.path.join(os.getcwd(), 'streamlit_dashboard_fixed.py')
    
    print("Launching futuristic dashboard...")
    print("Dashboard will open in your browser")
    print("Features: Real-time analytics, AI insights, Interactive charts")
    
    subprocess.run([
        sys.executable, '-m', 'streamlit', 'run', dashboard_path,
        '--server.port', '8501',
        '--server.headless', 'false'
    ])

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple CI Test - Only tests imports
"""

import sys

def test_imports():
    """Test essential imports"""
    try:
        import streamlit
        import plotly
        import pandas
        import fastapi
        import uvicorn
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    """Run CI tests"""
    print("CI Import Test")
    print("=" * 20)
    
    if test_imports():
        print("SUCCESS: Ready for CI/CD")
        return 0
    else:
        print("FAILED: Missing dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())
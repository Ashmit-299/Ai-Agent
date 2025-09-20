import subprocess
import sys
import os

# Install psycopg2-binary in current environment
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.10"])
    print("✅ psycopg2-binary installed successfully")
except Exception as e:
    print(f"❌ Installation failed: {e}")
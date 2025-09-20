#!/usr/bin/env python3
"""
MinIO Setup Script - Free S3-compatible storage
No credit card required, unlimited storage
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def download_minio():
    """Download MinIO server for Windows"""
    print("📥 Downloading MinIO server...")
    
    minio_url = "https://dl.min.io/server/minio/release/windows-amd64/minio.exe"
    minio_path = Path("minio.exe")
    
    if minio_path.exists():
        print("✅ MinIO already downloaded")
        return str(minio_path)
    
    try:
        response = requests.get(minio_url, stream=True)
        response.raise_for_status()
        
        with open(minio_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✅ MinIO downloaded successfully")
        return str(minio_path)
        
    except Exception as e:
        print(f"❌ Failed to download MinIO: {e}")
        return None

def setup_minio_data():
    """Create MinIO data directory"""
    data_dir = Path("minio-data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Created data directory: {data_dir}")
    return str(data_dir)

def update_env_file():
    """Update .env file with MinIO configuration"""
    env_path = Path(".env")
    
    minio_config = """
# MinIO Configuration (Free S3-compatible storage)
BHIV_STORAGE_BACKEND=minio
BHIV_MINIO_ENDPOINT=localhost:9000
BHIV_MINIO_ACCESS_KEY=minioadmin
BHIV_MINIO_SECRET_KEY=minioadmin
BHIV_MINIO_BUCKET=bhiv-content
"""
    
    if env_path.exists():
        content = env_path.read_text()
        if "BHIV_STORAGE_BACKEND=minio" not in content:
            with open(env_path, 'a') as f:
                f.write(minio_config)
            print("✅ Updated .env file with MinIO configuration")
        else:
            print("✅ MinIO configuration already in .env")
    else:
        env_path.write_text(minio_config.strip())
        print("✅ Created .env file with MinIO configuration")

def install_dependencies():
    """Install MinIO Python client"""
    print("📦 Installing MinIO Python client...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "minio"], check=True)
        print("✅ MinIO client installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install MinIO client: {e}")

def test_minio_connection():
    """Test MinIO connection"""
    print("🧪 Testing MinIO connection...")
    try:
        from minio import Minio
        
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        # Test connection
        buckets = list(client.list_buckets())
        print("✅ MinIO connection successful!")
        
        # Create bucket if it doesn't exist
        bucket_name = "bhiv-content"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        else:
            print(f"✅ Bucket exists: {bucket_name}")
            
        return True
        
    except ImportError:
        print("❌ MinIO client not installed. Run: pip install minio")
        return False
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")
        print("💡 Make sure MinIO server is running")
        return False

def create_start_script():
    """Create script to start MinIO server"""
    script_content = """@echo off
echo Starting MinIO server...
echo Web Console: http://localhost:9001
echo API Endpoint: http://localhost:9000
echo Login: minioadmin / minioadmin
echo.
minio.exe server minio-data --console-address ":9001"
"""
    
    script_path = Path("start_minio.bat")
    script_path.write_text(script_content)
    print(f"✅ Created start script: {script_path}")

def main():
    """Main setup function"""
    print("🚀 Setting up MinIO (Free S3-compatible storage)")
    print("📋 No credit card required, unlimited storage!")
    print()
    
    # Step 1: Download MinIO
    minio_exe = download_minio()
    if not minio_exe:
        return False
    
    # Step 2: Setup data directory
    setup_minio_data()
    
    # Step 3: Install Python client
    install_dependencies()
    
    # Step 4: Update configuration
    update_env_file()
    
    # Step 5: Create start script
    create_start_script()
    
    print()
    print("🎉 MinIO setup complete!")
    print()
    print("📋 Next steps:")
    print("1. Run: start_minio.bat")
    print("2. Open: http://localhost:9001")
    print("3. Login: minioadmin / minioadmin")
    print("4. Start your app: python start_server_venv.py")
    print()
    print("💡 Your app will now use MinIO for storage!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
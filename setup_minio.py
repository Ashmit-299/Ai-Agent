#!/usr/bin/env python3
"""
Setup MinIO - Self-hosted S3-compatible storage (Free)
"""
import os
import subprocess

def setup_minio():
    """Setup MinIO with Docker"""
    
    print("🔧 MinIO Setup (Self-hosted S3)")
    print("=" * 40)
    
    print("\n1. Install Docker Desktop:")
    print("   https://www.docker.com/products/docker-desktop/")
    
    print("\n2. Run MinIO Container:")
    docker_command = """
docker run -d \\
  --name minio \\
  -p 9001:9000 \\
  -p 9002:9001 \\
  -e MINIO_ROOT_USER=minioadmin \\
  -e MINIO_ROOT_PASSWORD=minioadmin123 \\
  -v minio-data:/data \\
  quay.io/minio/minio server /data --console-address ":9001"
    """
    print(docker_command)
    
    print("\n3. Access MinIO Console:")
    print("   http://localhost:9002")
    print("   Username: minioadmin")
    print("   Password: minioadmin123")
    
    print("\n4. Create Bucket:")
    print("   Buckets → Create Bucket → 'ai-agent-storage'")
    
    print("\n5. Add to .env:")
    print("""
# MinIO Configuration
USE_S3_STORAGE=true
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin123
S3_BUCKET_NAME=ai-agent-storage
S3_REGION=us-east-1
S3_ENDPOINT_URL=http://localhost:9001
    """)

def start_minio():
    """Start MinIO container"""
    try:
        # Check if container exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=minio'], 
                              capture_output=True, text=True)
        
        if 'minio' in result.stdout:
            # Start existing container
            subprocess.run(['docker', 'start', 'minio'])
            print("✅ MinIO container started")
        else:
            # Create new container
            cmd = [
                'docker', 'run', '-d',
                '--name', 'minio',
                '-p', '9001:9000',
                '-p', '9002:9001',
                '-e', 'MINIO_ROOT_USER=minioadmin',
                '-e', 'MINIO_ROOT_PASSWORD=minioadmin123',
                '-v', 'minio-data:/data',
                'quay.io/minio/minio',
                'server', '/data', '--console-address', ':9001'
            ]
            subprocess.run(cmd)
            print("✅ MinIO container created and started")
        
        print("🌐 MinIO Console: http://localhost:9002")
        print("🔑 Username: minioadmin")
        print("🔑 Password: minioadmin123")
        
    except Exception as e:
        print(f"❌ Failed to start MinIO: {e}")
        print("💡 Make sure Docker is installed and running")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        start_minio()
    else:
        setup_minio()
#!/usr/bin/env python3
"""
Setup Cloudflare R2 - Free 10GB S3-Compatible Storage
"""
import os
from dotenv import load_dotenv

load_dotenv()

def setup_cloudflare_r2():
    """Setup Cloudflare R2 (Free 10GB)"""
    
    print("🔧 Cloudflare R2 Setup Instructions")
    print("=" * 40)
    
    print("\n1. Create Cloudflare Account (Free):")
    print("   https://dash.cloudflare.com/sign-up")
    
    print("\n2. Enable R2 Storage:")
    print("   Dashboard → R2 Object Storage → Create Bucket")
    print("   Bucket name: ai-agent-storage")
    
    print("\n3. Get API Credentials:")
    print("   R2 → Manage R2 API tokens → Create API token")
    print("   Permissions: Object Read & Write")
    
    print("\n4. Add to .env file:")
    print("""
# Cloudflare R2 Configuration
USE_S3_STORAGE=true
AWS_ACCESS_KEY_ID=your_r2_access_key
AWS_SECRET_ACCESS_KEY=your_r2_secret_key
S3_BUCKET_NAME=ai-agent-storage
S3_REGION=auto
S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
    """)
    
    print("\n5. Test Connection:")
    print("   python test_r2_connection.py")

def test_r2_connection():
    """Test R2 connection"""
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    if not all([access_key, secret_key, endpoint_url, bucket_name]):
        print("❌ R2 credentials not configured in .env")
        return False
    
    try:
        import boto3
        
        # Create R2 client
        r2_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )
        
        # Test upload
        test_content = "R2 connection test"
        test_key = "test-connection.txt"
        
        r2_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8')
        )
        
        print("✅ R2 upload successful")
        
        # Test download
        response = r2_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded = response['Body'].read().decode('utf-8')
        
        if downloaded == test_content:
            print("✅ R2 download successful")
            
            # Cleanup
            r2_client.delete_object(Bucket=bucket_name, Key=test_key)
            print("✅ R2 cleanup successful")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ R2 connection failed: {e}")
        return False

if __name__ == "__main__":
    if os.getenv('S3_ENDPOINT_URL') and 'r2.cloudflarestorage.com' in os.getenv('S3_ENDPOINT_URL', ''):
        test_r2_connection()
    else:
        setup_cloudflare_r2()
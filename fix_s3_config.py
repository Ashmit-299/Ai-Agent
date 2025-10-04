#!/usr/bin/env python3
"""
Fix S3 configuration by forcing reload
"""
import os
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

# Print current config
print("Current S3 Configuration:")
print(f"USE_S3_STORAGE: {os.getenv('USE_S3_STORAGE')}")
print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')[:20]}...")
print(f"AWS_SECRET_ACCESS_KEY: {os.getenv('AWS_SECRET_ACCESS_KEY')[:20]}...")
print(f"S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME')}")
print(f"S3_REGION: {os.getenv('S3_REGION')}")
print(f"S3_ENDPOINT_URL: {os.getenv('S3_ENDPOINT_URL')}")

# Test boto3 connection
try:
    import boto3
    from botocore.config import Config
    
    config = Config(
        retries={'max_attempts': 3, 'mode': 'adaptive'},
        max_pool_connections=50
    )
    
    s3_client = boto3.client(
        's3',
        config=config,
        region_name=os.getenv('S3_REGION'),
        endpoint_url=os.getenv('S3_ENDPOINT_URL')
    )
    
    # Test connection
    bucket_name = os.getenv('S3_BUCKET_NAME')
    response = s3_client.head_bucket(Bucket=bucket_name)
    print(f"\n✅ S3 Connection successful!")
    print(f"Bucket '{bucket_name}' is accessible")
    
except Exception as e:
    print(f"\n❌ S3 Connection failed: {e}")
    print("This might be normal if using Supabase storage with JWT tokens")

print("\nTo fix the issue, restart your server:")
print("python scripts/start_server.py")
#!/usr/bin/env python3
"""
S3/MinIO Storage Adapter for Production Storage
"""
import os
import boto3
import time
import hashlib
import json
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

logger = logging.getLogger(__name__)

class S3StorageAdapter:
    """S3/MinIO storage adapter for production file storage"""
    
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "ai-agent-storage")
        self.region = os.getenv("S3_REGION", "us-east-1")
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL")  # For MinIO
        
        # Initialize S3 client
        self.s3_client = self._init_s3_client()
        self.bucket_exists = self._ensure_bucket_exists()
        
    def _init_s3_client(self):
        """Initialize S3 client with proper configuration"""
        try:
            config = Config(
                region_name=self.region,
                signature_version='s3v4',
                retries={'max_attempts': 3}
            )
            
            client_kwargs = {
                'config': config,
                'aws_access_key_id': os.getenv("AWS_ACCESS_KEY_ID"),
                'aws_secret_access_key': os.getenv("AWS_SECRET_ACCESS_KEY")
            }
            
            # Add endpoint for MinIO
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
                
            return boto3.client('s3', **client_kwargs)
            
        except Exception as e:
            logger.error(f"S3 client initialization failed: {e}")
            return None
    
    def _ensure_bucket_exists(self) -> bool:
        """Ensure S3 bucket exists"""
        if not self.s3_client:
            return False
            
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket '{self.bucket_name}' exists")
            return True
            
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                try:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                    logger.info(f"Created S3 bucket '{self.bucket_name}'")
                    return True
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    return False
            else:
                logger.error(f"Bucket check failed: {e}")
                return False
    
    def upload_file(self, file_data: bytes, key: str, content_type: str = None, metadata: Dict[str, str] = None) -> Optional[str]:
        """Upload file to S3 with metadata"""
        if not self.bucket_exists or not self.s3_client:
            logger.warning("S3 not available, falling back to local storage")
            return None
            
        try:
            extra_args = {}
            
            if content_type:
                extra_args['ContentType'] = content_type
                
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Add server-side encryption
            extra_args['ServerSideEncryption'] = 'AES256'
            
            # Upload file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                **extra_args
            )
            
            # Return S3 URL
            s3_url = f"s3://{self.bucket_name}/{key}"
            logger.info(f"File uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return None
    
    def generate_presigned_upload_url(self, key: str, content_type: str = None, expires_in: int = 3600) -> Optional[Dict[str, Any]]:
        """Generate pre-signed URL for direct frontend uploads"""
        if not self.bucket_exists or not self.s3_client:
            return None
            
        try:
            conditions = [
                {"bucket": self.bucket_name},
                ["starts-with", "$key", key],
                ["content-length-range", 1, 100 * 1024 * 1024]  # 1 byte to 100MB
            ]
            
            if content_type:
                conditions.append({"Content-Type": content_type})
            
            # Generate presigned POST
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                Fields={"Content-Type": content_type} if content_type else None,
                Conditions=conditions,
                ExpiresIn=expires_in
            )
            
            return {
                "upload_url": response["url"],
                "fields": response["fields"],
                "expires_in": expires_in,
                "max_file_size": 100 * 1024 * 1024
            }
            
        except Exception as e:
            logger.error(f"Pre-signed URL generation failed: {e}")
            return None
    
    def generate_presigned_download_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate pre-signed URL for file downloads"""
        if not self.bucket_exists or not self.s3_client:
            return None
            
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
            
        except Exception as e:
            logger.error(f"Pre-signed download URL generation failed: {e}")
            return None
    
    def delete_file(self, key: str) -> bool:
        """Delete file from S3"""
        if not self.bucket_exists or not self.s3_client:
            return False
            
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"File deleted from S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List files in S3 bucket"""
        if not self.bucket_exists or not self.s3_client:
            return []
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'].strip('"')
                })
            
            return files
            
        except Exception as e:
            logger.error(f"S3 list failed: {e}")
            return []

# Global storage adapter instance with lazy initialization
s3_adapter = None

def get_s3_adapter():
    """Get S3 adapter with lazy initialization"""
    global s3_adapter
    if s3_adapter is None:
        try:
            s3_adapter = S3StorageAdapter()
        except Exception as e:
            logger.warning(f"S3 adapter initialization failed: {e}")
            s3_adapter = False  # Mark as failed
    return s3_adapter if s3_adapter is not False else None
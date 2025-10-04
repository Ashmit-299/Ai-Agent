#!/usr/bin/env python3
"""
S3/MinIO Storage Adapter - Production replacement for bhiv_bucket
"""
import os
import boto3
import json
import time
import uuid
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from pathlib import Path
import logging

# Import retry utils with fallback
try:
    from app.retry_utils import retry_external_api, RetryError
except ImportError:
    # Fallback decorator if retry_utils not available
    def retry_external_api(func):
        return func
    
    class RetryError(Exception):
        pass

logger = logging.getLogger(__name__)

class S3StorageAdapter:
    """S3/MinIO storage adapter with pre-signed URL support"""
    
    def __init__(self):
        self.use_s3 = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "ai-agent-storage")
        self.region = os.getenv("S3_REGION", "us-east-1")
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL")  # For MinIO
        
        # Fallback paths
        self.local_bucket_path = os.getenv("BHIV_BUCKET_PATH", "bucket")
        
        # Initialize S3 client if enabled
        self.s3_client = None
        if self.use_s3:
            self._initialize_s3_client()
        
        # Create local directories as fallback
        self._ensure_local_directories()
    
    def _initialize_s3_client(self):
        """Initialize S3/MinIO client"""
        try:
            config = Config(
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                max_pool_connections=50
            )
            
            # S3 configuration
            kwargs = {
                'config': config,
                'region_name': self.region
            }
            
            # Add endpoint URL for MinIO
            if self.endpoint_url:
                kwargs['endpoint_url'] = self.endpoint_url
            
            self.s3_client = boto3.client('s3', **kwargs)
            
            # Test connection and create bucket if needed
            self._ensure_bucket_exists()
            
            logger.info(f"S3/MinIO client initialized successfully. Bucket: {self.bucket_name}")
            
        except (NoCredentialsError, ClientError) as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.use_s3 = False
            logger.warning("Falling back to local storage")
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                # Bucket doesn't exist, create it
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    
                    # Set public read policy for videos (optional)
                    self._set_bucket_policy()
                    
                    logger.info(f"Created bucket {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error accessing bucket: {e}")
                raise
    
    def _set_bucket_policy(self):
        """Set bucket policy for public read access to videos"""
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/videos/*"
                    }
                ]
            }
            
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(policy)
            )
            logger.info("Set bucket policy for public video access")
            
        except ClientError as e:
            logger.warning(f"Could not set bucket policy: {e}")
    
    def _ensure_local_directories(self):
        """Create local directory structure"""
        segments = ['uploads', 'videos', 'scripts', 'storyboards', 'ratings', 'logs']
        for segment in segments:
            path = Path(self.local_bucket_path) / segment
            path.mkdir(parents=True, exist_ok=True)
    
    def _get_s3_key(self, segment: str, filename: str) -> str:
        """Generate S3 key from segment and filename"""
        return f"{segment}/{filename}"
    
    def _get_local_path(self, segment: str, filename: str) -> str:
        """Generate local file path"""
        return os.path.join(self.local_bucket_path, segment, filename)
    
    @retry_external_api
    def upload_file(self, local_file_path: str, segment: str, filename: str) -> str:
        """Upload file to S3/MinIO or local storage"""
        
        if self.use_s3 and self.s3_client:
            try:
                s3_key = self._get_s3_key(segment, filename)
                
                # Add metadata
                metadata = {
                    'uploaded_at': str(time.time()),
                    'segment': segment,
                    'original_filename': filename
                }
                
                # Set content type based on extension
                content_type = self._get_content_type(filename)
                
                extra_args = {
                    'Metadata': metadata,
                    'ContentType': content_type
                }
                
                # Make videos publicly readable
                if segment == 'videos':
                    extra_args['ACL'] = 'public-read'
                
                self.s3_client.upload_file(
                    local_file_path,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args
                )
                
                # Return S3 URL
                if self.endpoint_url:  # MinIO
                    return f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"
                else:  # AWS S3
                    return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
                
            except Exception as e:
                logger.error(f"S3 upload failed: {e}")
                # Fall back to local storage
                return self._upload_local(local_file_path, segment, filename)
        else:
            return self._upload_local(local_file_path, segment, filename)
    
    def _upload_local(self, local_file_path: str, segment: str, filename: str) -> str:
        """Upload to local storage as fallback"""
        destination = self._get_local_path(segment, filename)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(local_file_path, destination)
        
        return destination
    
    def upload_content(self, content: bytes, segment: str, filename: str) -> str:
        """Upload content directly from bytes"""
        
        if self.use_s3 and self.s3_client:
            try:
                s3_key = self._get_s3_key(segment, filename)
                
                metadata = {
                    'uploaded_at': str(time.time()),
                    'segment': segment,
                    'size': str(len(content))
                }
                
                content_type = self._get_content_type(filename)
                
                extra_args = {
                    'Metadata': metadata,
                    'ContentType': content_type
                }
                
                if segment == 'videos':
                    extra_args['ACL'] = 'public-read'
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=content,
                    **extra_args
                )
                
                if self.endpoint_url:
                    return f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"
                else:
                    return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
                
            except Exception as e:
                logger.error(f"S3 content upload failed: {e}")
                return self._upload_content_local(content, segment, filename)
        else:
            return self._upload_content_local(content, segment, filename)
    
    def _upload_content_local(self, content: bytes, segment: str, filename: str) -> str:
        """Upload content to local storage"""
        destination = self._get_local_path(segment, filename)
        
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        with open(destination, 'wb') as f:
            f.write(content)
        
        return destination
    
    def generate_presigned_url(self, segment: str, filename: str, expiration: int = 3600, operation: str = 'get_object') -> Optional[str]:
        """Generate pre-signed URL for direct upload/download"""
        
        if not self.use_s3 or not self.s3_client:
            logger.warning("Pre-signed URLs not available without S3")
            return None
        
        try:
            s3_key = self._get_s3_key(segment, filename)
            
            if operation == 'put_object':
                # For uploads
                extra_params = {
                    'Bucket': self.bucket_name,
                    'Key': s3_key,
                    'ContentType': self._get_content_type(filename)
                }
                
                if segment == 'videos':
                    extra_params['ACL'] = 'public-read'
            else:
                # For downloads
                extra_params = {
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                }
            
            url = self.s3_client.generate_presigned_url(
                operation,
                Params=extra_params,
                ExpiresIn=expiration
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate pre-signed URL: {e}")
            return None
    
    def delete_file(self, segment: str, filename: str) -> bool:
        """Delete file from S3/MinIO or local storage"""
        
        if self.use_s3 and self.s3_client:
            try:
                s3_key = self._get_s3_key(segment, filename)
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
                logger.info(f"Deleted {s3_key} from S3")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete from S3: {e}")
        
        # Also try local deletion
        try:
            local_path = self._get_local_path(segment, filename)
            if os.path.exists(local_path):
                os.remove(local_path)
                logger.info(f"Deleted local file: {local_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete local file: {e}")
        
        return False
    
    def list_files(self, segment: str, max_keys: int = 100) -> List[Dict[str, Any]]:
        """List files in segment"""
        
        if self.use_s3 and self.s3_client:
            try:
                prefix = f"{segment}/"
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix,
                    MaxKeys=max_keys
                )
                
                files = []
                for obj in response.get('Contents', []):
                    files.append({
                        'key': obj['Key'],
                        'filename': obj['Key'].replace(prefix, ''),
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'storage_class': obj.get('StorageClass', 'STANDARD')
                    })
                
                return files
                
            except Exception as e:
                logger.error(f"Failed to list S3 objects: {e}")
        
        # Fallback to local listing
        try:
            local_dir = Path(self.local_bucket_path) / segment
            if local_dir.exists():
                files = []
                for file_path in local_dir.glob("*"):
                    if file_path.is_file():
                        stat = file_path.stat()
                        files.append({
                            'key': f"{segment}/{file_path.name}",
                            'filename': file_path.name,
                            'size': stat.st_size,
                            'last_modified': stat.st_mtime,
                            'storage_class': 'LOCAL'
                        })
                return files
        except Exception as e:
            logger.error(f"Failed to list local files: {e}")
        
        return []
    
    def get_file_url(self, segment: str, filename: str) -> str:
        """Get public URL for file"""
        
        if self.use_s3 and self.s3_client and segment == 'videos':
            # Return public URL for videos
            s3_key = self._get_s3_key(segment, filename)
            if self.endpoint_url:
                return f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"
            else:
                return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
        
        # For non-public files or local storage, return local path
        return self._get_local_path(segment, filename)
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename"""
        ext = Path(filename).suffix.lower()
        
        content_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.csv': 'text/csv'
        }
        
        return content_types.get(ext, 'application/octet-stream')

# Global storage instance
storage_adapter = S3StorageAdapter()

# Backward compatibility functions
def save_upload(file_path: str, filename: str) -> str:
    """Save uploaded file"""
    return storage_adapter.upload_file(file_path, 'uploads', filename)

def save_script(content: bytes, filename: str) -> str:
    """Save script content"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return storage_adapter.upload_content(content, 'scripts', filename)

def save_video(file_path: str, filename: str) -> str:
    """Save video file"""
    return storage_adapter.upload_file(file_path, 'videos', filename)

def save_json(segment: str, filename: str, data: Dict[str, Any]) -> str:
    """Save JSON data"""
    content = json.dumps(data, indent=2).encode('utf-8')
    return storage_adapter.upload_content(content, segment, filename)

def get_bucket_path(segment: str, filename: str) -> str:
    """Get bucket path - backward compatibility"""
    return storage_adapter._get_local_path(segment, filename)
# S3/MinIO Storage Setup Guide

## Overview

The AI Agent now supports S3/MinIO storage for production deployments with automatic fallback to local storage.

## Features

- **Dual Storage**: Local storage with S3 backup
- **Presigned URLs**: Direct frontend uploads to S3
- **Automatic Fallback**: Falls back to local storage if S3 unavailable
- **Backward Compatibility**: All existing functionality preserved

## Environment Variables

Add these to your `.env` file:

```bash
# S3 Storage Configuration
USE_S3_STORAGE=true
S3_BUCKET_NAME=ai-agent-storage
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# For MinIO (optional)
S3_ENDPOINT_URL=https://your-minio-endpoint.com
```

## AWS S3 Setup

1. **Create S3 Bucket**:
   ```bash
   aws s3 mb s3://ai-agent-storage --region us-east-1
   ```

2. **Set Bucket Policy** (replace bucket name):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {"AWS": "arn:aws:iam::YOUR-ACCOUNT:user/ai-agent"},
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:DeleteObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::ai-agent-storage",
           "arn:aws:s3:::ai-agent-storage/*"
         ]
       }
     ]
   }
   ```

3. **Create IAM User**:
   ```bash
   aws iam create-user --user-name ai-agent
   aws iam attach-user-policy --user-name ai-agent --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
   aws iam create-access-key --user-name ai-agent
   ```

## MinIO Setup

1. **Install MinIO**:
   ```bash
   docker run -p 9000:9000 -p 9001:9001 \
     -e "MINIO_ROOT_USER=minioadmin" \
     -e "MINIO_ROOT_PASSWORD=minioadmin" \
     minio/minio server /data --console-address ":9001"
   ```

2. **Environment Variables**:
   ```bash
   USE_S3_STORAGE=true
   S3_BUCKET_NAME=ai-agent-storage
   S3_REGION=us-east-1
   S3_ENDPOINT_URL=http://localhost:9000
   AWS_ACCESS_KEY_ID=minioadmin
   AWS_SECRET_ACCESS_KEY=minioadmin
   ```

## API Endpoints

### Storage Status
```bash
GET /storage/status
```

### Generate Presigned Upload URL
```bash
POST /storage/presigned-upload
{
  "filename": "example.mp4",
  "content_type": "video/mp4"
}
```

## Testing

1. **Install Dependencies**:
   ```bash
   pip install boto3 botocore
   ```

2. **Test Storage**:
   ```bash
   curl http://localhost:9000/storage/status
   ```

3. **Test Upload**:
   ```bash
   curl -X POST http://localhost:9000/storage/presigned-upload \
     -H "Content-Type: application/json" \
     -d '{"filename": "test.txt", "content_type": "text/plain"}'
   ```

## File Organization

```
S3 Bucket Structure:
├── uploads/          # User uploaded files
├── videos/           # Generated videos
├── scripts/          # Script files
├── storyboards/      # Storyboard data
├── ratings/          # User ratings
└── logs/             # System logs
```

## Security Features

- **Server-side encryption** (AES256)
- **Presigned URL expiration** (1 hour default)
- **File size limits** (100MB max)
- **Content type validation**
- **Secure filename generation**

## Monitoring

Check storage status:
```bash
GET /storage/status
GET /bucket/stats
```

## Troubleshooting

1. **S3 Connection Issues**:
   - Verify AWS credentials
   - Check bucket permissions
   - Confirm region settings

2. **MinIO Issues**:
   - Ensure MinIO is running
   - Check endpoint URL
   - Verify access credentials

3. **Fallback Mode**:
   - System automatically falls back to local storage
   - Check logs for S3 connection errors
   - Files saved locally as backup

## Migration

Existing local files remain unchanged. New uploads will use S3 when enabled.
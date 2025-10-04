# Storage Backends Guide - AI Agent Platform

## Overview

The AI Agent Platform supports multiple storage backends for flexible deployment across different environments and requirements.

## Supported Storage Backends

### 1. 🗄️ **Supabase Storage** (Recommended for Production)

**Features:**
- Integrated with Supabase database
- Built-in CDN and global distribution
- Automatic image optimization
- Public/private bucket support
- 1GB free tier, then pay-as-you-go

**Configuration:**
```bash
# .env
USE_SUPABASE_STORAGE=true
BHIV_STORAGE_BACKEND=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET_NAME=ai-agent-files
```

**Setup:**
```bash
# Run Supabase storage setup
python setup_supabase_storage.py

# Create bucket and set policies
python setup_supabase_bucket.py
```

**Endpoints:**
- Upload: `POST /cdn/upload/{token}`
- Download: `GET /cdn/download/{id}`
- Stream: `GET /cdn/stream/{id}`
- List: `GET /cdn/list`

---

### 2. ☁️ **AWS S3** (Enterprise Production)

**Features:**
- Unlimited scalability
- Global CDN with CloudFront
- Advanced security and compliance
- Lifecycle management
- Pay-per-use pricing

**Configuration:**
```bash
# .env
USE_S3_STORAGE=true
BHIV_STORAGE_BACKEND=s3
S3_BUCKET_NAME=ai-agent-storage
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Setup:**
```bash
# Install AWS CLI
pip install boto3

# Configure S3 bucket
python setup_s3_bucket.py

# Test S3 connection
python test_s3_connection.py
```

**Features:**
- Presigned URLs for direct uploads
- Automatic multipart uploads for large files
- Server-side encryption
- Cross-region replication

---

### 3. 🏠 **MinIO** (Self-Hosted S3-Compatible)

**Features:**
- S3-compatible API
- Self-hosted control
- High performance
- Kubernetes native
- No vendor lock-in

**Configuration:**
```bash
# .env
USE_S3_STORAGE=true
BHIV_STORAGE_BACKEND=minio
S3_BUCKET_NAME=ai-agent-storage
S3_REGION=us-east-1
S3_ENDPOINT_URL=http://localhost:9000  # MinIO endpoint
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
```

**Setup:**
```bash
# Install and run MinIO
python setup_minio.py

# Configure MinIO bucket
python setup_minio_bucket.py
```

---

### 4. 💾 **Local File System** (Development)

**Features:**
- Simple file system storage
- No external dependencies
- Fast for development
- Easy debugging

**Configuration:**
```bash
# .env
USE_S3_STORAGE=false
USE_SUPABASE_STORAGE=false
BHIV_STORAGE_BACKEND=local
BHIV_BUCKET_PATH=bucket
```

**Structure:**
```
bucket/
├── uploads/     # User uploaded files
├── videos/      # Generated videos
├── scripts/     # Text scripts
├── storyboards/ # Video storyboards
├── ratings/     # User feedback
└── logs/        # System logs
```

---

## Storage Adapter Architecture

### Core Components

#### `core/s3_storage_adapter.py`
- Unified interface for all storage backends
- Automatic fallback mechanisms
- Async/sync operation support
- Error handling and retry logic

#### Key Methods:
```python
# Upload content
storage_adapter.upload_content(data, segment, filename)

# Download content
storage_adapter.download_content(segment, filename)

# List files
storage_adapter.list_files(segment, max_keys=100)

# Delete files
storage_adapter.delete_content(segment, filename)

# Generate presigned URLs
storage_adapter.generate_presigned_upload_url(filename, content_type)
```

### Multi-Backend Support

The platform automatically selects the appropriate backend based on configuration:

```python
# Automatic backend selection
if USE_SUPABASE_STORAGE:
    backend = SupabaseStorageAdapter()
elif USE_S3_STORAGE:
    backend = S3StorageAdapter()
else:
    backend = LocalStorageAdapter()
```

---

## API Endpoints by Storage Type

### Universal Endpoints (All Backends)
- `GET /storage/status` - Storage backend status
- `GET /bucket/stats` - Storage statistics
- `GET /bucket/list/{segment}` - List files in segment

### CDN Endpoints (Supabase/S3/MinIO)
- `GET /cdn/upload-url` - Generate upload URL
- `POST /cdn/upload/{token}` - Upload with token
- `GET /cdn/download/{id}` - CDN download
- `GET /cdn/stream/{id}` - CDN streaming

### Presigned URLs (S3/MinIO)
- `POST /storage/presigned-upload` - Generate S3 presigned URLs

---

## Performance Comparison

| Backend | Upload Speed | Download Speed | Scalability | Cost | Setup Complexity |
|---------|-------------|----------------|-------------|------|------------------|
| **Supabase** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **AWS S3** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **MinIO** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Local** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Configuration Examples

### Production (Supabase)
```bash
# High-performance production setup
USE_SUPABASE_STORAGE=true
BHIV_STORAGE_BACKEND=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET_NAME=ai-agent-files
MAX_UPLOAD_SIZE_MB=100
```

### Enterprise (AWS S3)
```bash
# Enterprise-grade setup with CloudFront
USE_S3_STORAGE=true
BHIV_STORAGE_BACKEND=s3
S3_BUCKET_NAME=ai-agent-production
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
CLOUDFRONT_DOMAIN=d123456789.cloudfront.net
```

### Self-Hosted (MinIO)
```bash
# Self-hosted with full control
USE_S3_STORAGE=true
BHIV_STORAGE_BACKEND=minio
S3_BUCKET_NAME=ai-agent-storage
S3_ENDPOINT_URL=https://minio.yourcompany.com
AWS_ACCESS_KEY_ID=your_minio_access_key
AWS_SECRET_ACCESS_KEY=your_minio_secret_key
```

### Development (Local)
```bash
# Simple development setup
USE_S3_STORAGE=false
USE_SUPABASE_STORAGE=false
BHIV_STORAGE_BACKEND=local
BHIV_BUCKET_PATH=bucket
```

---

## Migration Between Backends

### Supabase to S3
```bash
# Export from Supabase
python scripts/export_supabase_storage.py

# Import to S3
python scripts/import_to_s3.py
```

### Local to Cloud
```bash
# Sync local files to cloud storage
python scripts/sync_local_to_cloud.py --backend=supabase
```

---

## Security & Access Control

### Supabase Storage Policies
```sql
-- Allow authenticated users to upload
CREATE POLICY "Allow authenticated uploads" ON storage.objects
FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Allow users to access their own files
CREATE POLICY "Allow user file access" ON storage.objects
FOR SELECT USING (auth.uid()::text = (storage.foldername(name))[1]);
```

### S3 Bucket Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::ACCOUNT:user/ai-agent"},
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::ai-agent-storage/*"
    }
  ]
}
```

---

## Monitoring & Analytics

### Storage Metrics
- `GET /bucket/stats` - File counts and sizes
- `GET /storage/status` - Backend health and configuration
- `GET /observability/performance` - Storage performance metrics

### Key Metrics Tracked:
- Upload success/failure rates
- Download speeds
- Storage utilization
- Error rates by backend
- Cost analysis (for cloud backends)

---

## Troubleshooting

### Common Issues

#### Supabase Connection Issues
```bash
# Test Supabase connection
python test_supabase_simple.py

# Check bucket policies
python scripts/maintenance/verify_supabase_connection.py
```

#### S3 Permission Issues
```bash
# Test S3 credentials
python test_s3_connection.py

# Verify bucket permissions
aws s3 ls s3://your-bucket-name
```

#### Local Storage Issues
```bash
# Check disk space
df -h

# Verify permissions
ls -la bucket/
```

### Debug Commands
```bash
# Test all storage backends
python test_all_storage_backends.py

# Storage backend diagnostics
python debug_storage_backends.py

# Performance benchmarking
python benchmark_storage_performance.py
```

---

## Best Practices

### 1. **Production Setup**
- Use Supabase or S3 for production
- Enable CDN for global distribution
- Set up proper backup strategies
- Monitor storage costs

### 2. **Security**
- Use presigned URLs for direct uploads
- Implement proper access controls
- Enable encryption at rest
- Regular security audits

### 3. **Performance**
- Use appropriate file formats
- Implement caching strategies
- Monitor upload/download speeds
- Optimize file sizes

### 4. **Cost Optimization**
- Set up lifecycle policies
- Monitor storage usage
- Use appropriate storage classes
- Regular cleanup of unused files

---

**Last Updated**: 2025-01-02  
**Supported Backends**: 4 (Supabase, S3, MinIO, Local)  
**Max File Size**: 100MB  
**Supported Formats**: Video, Audio, Images, Documents
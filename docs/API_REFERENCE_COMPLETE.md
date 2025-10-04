# Complete API Reference - AI Agent Platform

## Overview

The AI Agent Platform provides 60+ REST API endpoints organized into 9 systematic steps, covering content management, video generation, AI-powered recommendations, and comprehensive analytics.

**Base URLs:**
- **Production**: `https://ai-agent-aff6.onrender.com`
- **Local Development**: `http://localhost:9000`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

### Getting Started
1. Get demo credentials: `GET /demo-login`
2. Login: `POST /users/login`
3. Use the returned `access_token` for authenticated requests

## API Endpoints by Category

### 🔍 **Debug & System Endpoints**

#### `GET /debug-routes`
Lists all available routes and identifies conflicts.
- **Auth**: Not required
- **Response**: Route enumeration with methods and paths

#### `GET /debug-auth`
Tests authentication status and token validity.
- **Auth**: Optional (for testing)
- **Response**: Authentication status and user info

#### `GET /health`
System health check with environment validation.
- **Auth**: Not required
- **Response**: Health status and system info

#### `GET /test`
Basic server functionality test.
- **Auth**: Not required
- **Response**: Server status and available endpoints

---

### 👤 **STEP 1: System Health & Demo Access**

#### `GET /demo-login`
Get demo credentials for testing.
- **Auth**: Not required
- **Response**: Demo username/password and login instructions

#### `GET /health`
Detailed system health with systematic organization info.
- **Auth**: Not required
- **Response**: Health status with 9-step workflow info

---

### 🔐 **STEP 2: User Authentication**

#### `POST /users/register`
Register a new user account.
- **Auth**: Not required
- **Body**: `{"username": "string", "password": "string", "email": "string"}`
- **Response**: User creation confirmation

#### `POST /users/login`
Login and receive JWT tokens.
- **Auth**: Not required
- **Body**: `{"username": "string", "password": "string"}`
- **Response**: `{"access_token": "jwt", "refresh_token": "jwt", "token_type": "bearer"}`

#### `GET /users/profile`
Get current user profile information.
- **Auth**: Required
- **Response**: User profile data

#### `POST /users/refresh`
Refresh JWT access token.
- **Auth**: Refresh token required
- **Response**: New access token

#### `POST /invite-user`
Send user invitation (admin feature).
- **Auth**: Required
- **Body**: `{"email": "string"}`
- **Response**: Invitation status

---

### 📁 **STEP 3: Content Upload & Video Generation**

#### `GET /contents`
Browse existing content with pagination.
- **Auth**: Required
- **Query**: `limit` (default: 20)
- **Response**: List of content items with metadata

#### `POST /upload`
Upload content files (images, videos, documents).
- **Auth**: Required
- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `file`: File upload (max 100MB)
  - `title`: Content title
  - `description`: Content description (optional)
- **Response**: Content metadata with authenticity score and AI-generated tags

#### `POST /generate-video`
Generate video from text script.
- **Auth**: Required
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file`: Text script file (.txt, max 1MB)
  - `title`: Video title
- **Response**: Generated video metadata and download URLs

---

### 🎬 **STEP 4: Content Access & Streaming**

#### `GET /content/{content_id}`
Get content details and access URLs.
- **Auth**: Required
- **Response**: Content metadata with download/stream URLs

#### `GET /content/{content_id}/metadata`
Get detailed content metadata including stats.
- **Auth**: Optional
- **Response**: Comprehensive content information with feedback stats

#### `GET /download/{content_id}`
Download content file.
- **Auth**: Required
- **Response**: File download

#### `GET /stream/{content_id}`
Stream video content with range support.
- **Auth**: Required
- **Headers**: `Range` (optional for partial content)
- **Response**: Video stream with range support

---

### 🤖 **STEP 5: AI Feedback & Tag Recommendations**

#### `POST /feedback`
Submit feedback to train the Q-Learning RL agent.
- **Auth**: Required
- **Body**: `{"content_id": "string", "rating": 1-5, "comment": "string"}`
- **Response**: Feedback confirmation with RL agent training results

#### `GET /recommend-tags/{content_id}`
Get AI-powered tag recommendations.
- **Auth**: Optional (personalized if authenticated)
- **Response**: Recommended tags with RL agent confidence metrics

#### `GET /average-rating/{content_id}`
Get average rating for content.
- **Auth**: Optional
- **Response**: Average rating and total rating count

---

### 📊 **STEP 6: Analytics & Performance Monitoring**

#### `GET /metrics`
System metrics including RL agent performance.
- **Auth**: Required
- **Response**: System statistics and RL agent metrics

#### `GET /rl/agent-stats`
Detailed Q-Learning agent statistics.
- **Auth**: Optional
- **Response**: Q-table insights and learning status

#### `GET /bhiv/analytics`
Advanced analytics with sentiment analysis.
- **Auth**: Optional
- **Response**: User engagement, sentiment breakdown, analytics

#### `GET /streaming-performance`
Real-time streaming analytics.
- **Auth**: Optional
- **Response**: Streaming statistics and performance metrics

#### `GET /observability/health`
Observability system health status.
- **Auth**: Optional
- **Response**: Sentry/PostHog status and performance metrics

#### `GET /observability/performance`
Detailed system performance metrics.
- **Auth**: Required
- **Response**: CPU, memory, disk usage, and application metrics

#### `GET /bucket/stats`
Storage backend statistics.
- **Auth**: Optional
- **Response**: File counts across storage segments

#### `GET /bucket/list/{segment}`
List files in storage segment.
- **Auth**: Optional
- **Path**: `segment` (uploads, videos, scripts, storyboards, ratings, logs)
- **Query**: `limit` (default: 20)
- **Response**: File list with metadata

---

### 🌐 **CDN & File Management**

#### `GET /cdn/upload-url`
Generate presigned upload URL for direct uploads.
- **Auth**: Required
- **Query**: `filename`, `content_type`
- **Response**: Upload URL and token

#### `POST /cdn/upload/{upload_token}`
Upload file using presigned URL token.
- **Auth**: Required
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (file upload)
- **Response**: Upload confirmation with content ID

#### `GET /cdn/download/{content_id}`
Download file via CDN.
- **Auth**: Optional
- **Response**: File download

#### `GET /cdn/stream/{content_id}`
Stream file via CDN.
- **Auth**: Optional
- **Response**: File stream

#### `GET /cdn/list`
List user's uploaded files.
- **Auth**: Required
- **Query**: `limit` (default: 20)
- **Response**: User's file list

#### `DELETE /cdn/delete/{content_id}`
Delete uploaded file.
- **Auth**: Required
- **Response**: Deletion confirmation

#### `GET /cdn/info/{content_id}`
Get file information.
- **Auth**: Optional
- **Response**: File metadata and URLs

---

### 🛡️ **GDPR & Privacy Compliance**

#### `GET /gdpr/privacy-policy`
Privacy policy and GDPR information.
- **Auth**: Not required
- **Response**: HTML privacy policy page

#### `GET /gdpr/export-data`
Export all user data (GDPR Article 20).
- **Auth**: Required
- **Response**: Complete user data export in JSON format

#### `DELETE /gdpr/delete-data`
Delete all user data (GDPR Article 17).
- **Auth**: Required
- **Response**: Data deletion confirmation

#### `GET /gdpr/data-summary`
Summary of stored user data.
- **Auth**: Required
- **Response**: Data categories and retention information

---

### ⚙️ **STEP 7: Task Queue Management**

#### `GET /tasks/{task_id}`
Get background task status.
- **Auth**: Optional
- **Response**: Task status and progress

#### `GET /tasks/queue/stats`
Task queue statistics.
- **Auth**: Optional
- **Response**: Queue metrics and worker status

#### `POST /tasks/create-test`
Create test background task.
- **Auth**: Optional
- **Response**: Test task creation confirmation

---

### 🔧 **STEP 8: System Maintenance (Admin)**

#### `POST /bucket/cleanup`
Clean up old files from storage.
- **Auth**: Required (Admin)
- **Query**: `admin_key`
- **Response**: Cleanup results

#### `POST /bucket/rotate-logs`
Rotate system log files.
- **Auth**: Required (Admin)
- **Query**: `admin_key`
- **Response**: Log rotation results

#### `GET /maintenance/failed-operations`
List failed system operations.
- **Auth**: Required (Admin)
- **Query**: `admin_key`
- **Response**: Failed operations list

---

### 🎛️ **STEP 9: User Interface & Dashboard**

#### `GET /dashboard`
HTML dashboard for system monitoring.
- **Auth**: Optional
- **Response**: Interactive HTML dashboard

---

### 🗄️ **Storage & Multi-Backend Support**

#### `GET /storage/status`
Multi-backend storage system status.
- **Auth**: Required
- **Response**: Storage backend configuration and status

#### `POST /storage/presigned-upload`
Generate S3 presigned upload URLs.
- **Auth**: Required
- **Body**: `{"filename": "string", "content_type": "string"}`
- **Response**: Presigned upload URL and metadata

---

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {...},
  "timestamp": "2025-01-02T10:30:00Z"
}
```

### Error Response
```json
{
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2025-01-02T10:30:00Z"
}
```

### Content Upload Response
```json
{
  "content_id": "abc123def456",
  "title": "My Content",
  "description": "Content description",
  "file_path": "/path/to/file",
  "content_type": "image/jpeg",
  "authenticity_score": 0.85,
  "tags": ["tag1", "tag2", "tag3"],
  "next_step": "Use /content/abc123def456 to view details"
}
```

### Feedback Response
```json
{
  "status": "success",
  "rating": 4,
  "event_type": "like",
  "reward": 0.5,
  "rl_training": {
    "agent_trained": true,
    "current_epsilon": 0.2,
    "q_states": 12,
    "avg_recent_reward": 0.3
  }
}
```

## Rate Limits

- **Default**: 60 requests per minute per IP
- **Upload**: 10 uploads per minute per user
- **Feedback**: 30 feedback submissions per minute per user
- **Analytics**: 100 requests per minute per user

## File Upload Limits

- **Max file size**: 100MB
- **Supported formats**: 
  - **Video**: MP4, AVI, MOV
  - **Audio**: MP3, WAV
  - **Images**: JPEG, PNG
  - **Documents**: TXT, PDF

## Storage Backends

1. **Supabase Storage** (Default)
2. **AWS S3** (Production)
3. **MinIO** (Self-hosted)
4. **Local File System** (Development)

## Error Codes

- **400**: Bad Request - Invalid input
- **401**: Unauthorized - Authentication required
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource not found
- **413**: Payload Too Large - File too large
- **429**: Too Many Requests - Rate limit exceeded
- **500**: Internal Server Error - Server error

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post('http://localhost:9000/users/login', json={
    'username': 'demo',
    'password': 'demo1234'
})
token = response.json()['access_token']

# Upload file
headers = {'Authorization': f'Bearer {token}'}
files = {'file': open('example.jpg', 'rb')}
data = {'title': 'My Image', 'description': 'Test upload'}
response = requests.post('http://localhost:9000/upload', 
                        headers=headers, files=files, data=data)
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch('http://localhost:9000/users/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'demo', password: 'demo1234'})
});
const {access_token} = await loginResponse.json();

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('title', 'My File');

const uploadResponse = await fetch('http://localhost:9000/upload', {
  method: 'POST',
  headers: {'Authorization': `Bearer ${access_token}`},
  body: formData
});
```

### cURL
```bash
# Get demo credentials
curl http://localhost:9000/demo-login

# Login
curl -X POST http://localhost:9000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'

# Upload file
curl -X POST http://localhost:9000/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@example.jpg" \
  -F "title=My Image"
```

## Testing & Development

### Interactive API Testing
- **Swagger UI**: [http://localhost:9000/docs](http://localhost:9000/docs)
- **Route Debug**: [http://localhost:9000/debug-routes](http://localhost:9000/debug-routes)
- **Auth Test**: [http://localhost:9000/debug-auth](http://localhost:9000/debug-auth)

### Load Testing
```bash
# Run comprehensive load tests
python scripts/run_load_tests.py

# Interactive Locust testing (100 users)
locust -f tests/load_testing/locust_load_test.py --host=http://localhost:9000
```

---

**Last Updated**: 2025-01-02  
**API Version**: 2.0.0  
**Total Endpoints**: 60+  
**Documentation**: Complete
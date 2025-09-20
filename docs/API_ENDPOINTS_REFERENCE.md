# 🚀 AI Content Uploader Agent - API Endpoints Reference

## 📋 Table of Contents
- [System Health & Status](#-system-health--status)
- [Authentication & User Management](#-authentication--user-management)
- [Content Management](#-content-management)
- [Content Access & Streaming](#-content-access--streaming)
- [AI Learning & Recommendations](#-ai-learning--recommendations)
- [Analytics & Monitoring](#-analytics--monitoring)
- [BHIV Core Integration](#-bhiv-core-integration)
- [Bucket Management & Maintenance](#-bucket-management--maintenance)
- [Maintenance Utilities](#-maintenance-utilities)
- [Dashboard & UI](#-dashboard--ui)

---

## 🔍 System Health & Status

### `GET /health`
**System health check - Start here to verify system is running**
- **Response**: System status and next steps
- **Usage**: First endpoint to test when setting up

---

## 🔐 Authentication & User Management

### `GET /demo-login`
**Get demo credentials for quick testing**
- **Response**: Demo username/password for testing
- **Usage**: Quick access for development/testing

### `POST /register`
**Register new user account**
- **Body**: `username` (form), `password` (form), `email` (form, optional)
- **Response**: User ID and next steps
- **Usage**: Create new user accounts

### `POST /login`
**Login with username/password - Get JWT token**
- **Body**: `username` (form), `password` (form)
- **Response**: JWT access token and user info
- **Usage**: Authenticate users and get access tokens

### Advanced Authentication (JWT-based)
- `POST /users/register` - Advanced user registration
- `POST /users/login` - Advanced user login
- `GET /users/profile` - Get user profile (requires auth)

---

## 📁 Content Management

### `GET /contents`
**List all content - Browse available content**
- **Query**: `limit` (default: 50), `offset` (default: 0)
- **Response**: Paginated list of content with metadata
- **Usage**: Browse and discover uploaded content

### `POST /upload`
**Upload files (images, videos, PDFs, text)**
- **Body**: `file` (multipart), `title` (form), `description` (form), `uploader_id` (form)
- **Response**: Content ID, authenticity score, suggested tags
- **Supported**: .mp4, .mp3, .wav, .jpg, .jpeg, .png, .txt, .pdf
- **Usage**: Upload various file types for processing

### `POST /generate-video`
**Generate video from text script using AI**
- **Body**: `file` (.txt script), `title` (form)
- **Response**: Generated video details and streaming URLs
- **Usage**: Convert text scripts into videos automatically

---

## 🎥 Content Access & Streaming

### `GET /content/{content_id}`
**Get content metadata and statistics**
- **Path**: `content_id` - Unique content identifier
- **Response**: Complete content details, tags, stats
- **Usage**: View detailed information about specific content

### `GET /download/{content_id}`
**Secure file download**
- **Path**: `content_id` - Content to download
- **Response**: File download with security validation
- **Usage**: Download original uploaded files

### `GET /stream/{content_id}`
**HTTP range video streaming**
- **Path**: `content_id` - Video content to stream
- **Headers**: Supports `Range` requests for efficient streaming
- **Response**: Video stream with range support
- **Usage**: Stream videos with seek/resume capability

---

## 🤖 AI Learning & Recommendations

### `POST /feedback`
**Submit video rating (1-5 stars) to train AI**
- **Body**: JSON with `content_id`, `user_id`, `rating` (1-5), `watch_time_ms`, `comment`
- **Response**: Feedback confirmation and AI improvement status
- **Usage**: Train the RL agent with user preferences

### `GET /recommend-tags/{content_id}`
**AI-powered tag suggestions**
- **Path**: `content_id` - Content to get recommendations for
- **Response**: AI-generated tag recommendations
- **Usage**: Get intelligent content tagging suggestions

### `POST /rate/{content_id}`
**Rate content and trigger feedback logic**
- **Path**: `content_id` - Content to rate
- **Body**: `rating` (1-5), `comment` (optional)
- **Response**: Rating confirmation and processing status
- **Usage**: Alternative rating endpoint with BHIV Core integration

### `GET /average-rating/{content_id}`
**Get average rating for content**
- **Path**: `content_id` - Content to check rating for
- **Response**: Average rating and rating count
- **Usage**: View content popularity metrics

---

## 📊 Analytics & Monitoring

### `POST /ingest/webhook`
**Webhook endpoint for external integrations**
- **Body**: JSON payload or multipart form with script
- **Response**: Processing status and content ID
- **Usage**: Integrate with external systems for automated content processing

### `GET /core/stats`
**Get basic processing statistics**
- **Response**: Content counts, feedback stats, processing status
- **Usage**: Monitor system activity and usage

### `GET /core/metadata/{content_id}`
**Get BHIV core processing metadata**
- **Path**: `content_id` - Content to get metadata for
- **Response**: Database and core processing metadata
- **Usage**: Debug and track content processing pipeline

### `GET /lm/stats`
**Get LLM integration status**
- **Response**: LLM configuration and availability status
- **Usage**: Monitor AI/LLM service connectivity

---

## 🔧 BHIV Core Integration

### `GET /metrics`
**Comprehensive system metrics**
- **Response**: RL agent metrics, system stats, database metrics, LLM status
- **Usage**: Monitor overall system health and performance

### `GET /logs`
**System logs for observability**
- **Query**: `log_type` (app/security/rl_agent/errors/system), `lines` (default: 100), `admin_key` (required)
- **Response**: Recent log entries
- **Usage**: Debug issues and monitor system activity
- **Admin Key**: `admin_logs_2024`

### `GET /streaming-performance`
**Real-time streaming analytics**
- **Response**: Streaming performance metrics and statistics
- **Usage**: Monitor video streaming performance

### `GET /reports/storyboard-stats`
**Video generation statistics**
- **Response**: Storyboard generation success rates and counts
- **Usage**: Monitor AI video generation performance

### `GET /reports/video-stats`
**Comprehensive video analytics**
- **Response**: Video counts, durations, views, likes
- **Usage**: Analyze video content performance

---

## 🗄️ Bucket Management & Maintenance

### `GET /bucket/stats`
**Storage backend statistics**
- **Response**: Storage configuration and usage statistics
- **Usage**: Monitor storage system health

### `POST /bucket/cleanup`
**Clean up temporary files**
- **Query**: `max_age_hours` (default: 24, range: 1-168)
- **Response**: Cleanup results and file counts
- **Usage**: Maintain storage by removing old temporary files

### `POST /bucket/rotate-logs`
**Archive old log files**
- **Query**: `max_age_days` (default: 7, range: 1-30)
- **Response**: Log rotation results
- **Usage**: Manage log file storage and archiving

### `GET /bucket/list/{segment}`
**List files in storage segments**
- **Path**: `segment` - One of: scripts, storyboards, videos, logs, ratings, uploads
- **Response**: File list for specified storage segment
- **Usage**: Browse and audit stored files

---

## 🛠️ Maintenance Utilities

### `GET /maintenance/failed-operations`
**Get recent failed operations for debugging**
- **Query**: `limit` (default: 50)
- **Response**: List of failed operations with error details
- **Usage**: Debug system issues and monitor failures

### `GET /tasks/{task_id}`
**Get status of async task**
- **Path**: `task_id` - Task identifier to check
- **Response**: Task status, progress, and results
- **Usage**: Monitor background task execution

### `GET /tasks/queue/stats`
**Get task queue statistics**
- **Response**: Queue status, task counts, worker information
- **Usage**: Monitor background processing system

### `POST /tasks/create-test`
**Create a test task for demonstration**
- **Response**: Test task ID and status
- **Usage**: Test background task processing system

---

## 🎛️ Dashboard & UI

### `GET /dashboard`
**Analytics dashboard interface**
- **Response**: HTML dashboard with real-time metrics
- **Features**: User counts, content stats, sentiment analysis, engagement metrics
- **Usage**: Web interface for monitoring system status

---

## 🔗 Quick Start Workflow

1. **Health Check**: `GET /health`
2. **Authentication**: `POST /login` (use demo credentials from `/demo-login`)
3. **Upload Content**: `POST /upload` or `POST /generate-video`
4. **Access Content**: `GET /content/{id}` → `GET /stream/{id}`
5. **Provide Feedback**: `POST /feedback`
6. **Get Recommendations**: `GET /recommend-tags/{id}`
7. **Monitor System**: `GET /metrics` and `GET /dashboard`

## 📝 Notes

- **Authentication**: Most endpoints work without auth, but some require JWT tokens
- **Rate Limiting**: 100 requests per hour per IP
- **File Limits**: 100MB max upload size
- **Admin Access**: Some endpoints require admin key: `admin_logs_2024`
- **API Documentation**: Available at `/docs` (Swagger UI) and `/redoc`

## 🌐 Base URLs

- **Development**: `http://localhost:9000`
- **Production**: `https://ai-uploader.local`
- **API Docs**: `{base_url}/docs`
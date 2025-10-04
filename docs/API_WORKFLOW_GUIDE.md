# 🔄 API Workflow Guide - Step-by-Step User Journey

## **Complete User Workflow in Logical Sequence**

### **Step 1: System Check & Authentication**
| Method | Endpoint | Description | Next Step |
|--------|----------|-------------|-----------|
| **GET** | `/health` | ✅ Check if system is running | Go to Step 2 |
| **POST** | `/login` | 🔐 Get JWT token for secure access | Go to Step 2 |

### **Step 2: Content Management**
| Method | Endpoint | Description | Next Step |
|--------|----------|-------------|-----------|
| **POST** | `/upload` | 📤 Upload files (images, videos, PDFs, etc.) | Go to Step 3 |
| **POST** | `/generate-video` | 🎬 Create video from text script | Go to Step 3 |
| **GET** | `/contents` | 📋 List all uploaded content | Select content for Step 3 |

### **Step 3: Content Access & Interaction**
| Method | Endpoint | Description | Next Step |
|--------|----------|-------------|-----------|
| **GET** | `/content/{id}` | 📊 Get content details & metadata | Use content_id for Step 4 |
| **GET** | `/download/{id}` | ⬇️ Download content file | Optional: Go to Step 4 |
| **GET** | `/stream/{id}` | 🎥 Stream video with range requests | Optional: Go to Step 4 |

### **Step 4: AI Learning & Recommendations**
| Method | Endpoint | Description | Next Step |
|--------|----------|-------------|-----------|
| **POST** | `/feedback` | 🤖 Submit user feedback (like/view/share) | Trains RL agent |
| **GET** | `/recommend-tags/{id}` | 🏷️ Get AI-powered tag suggestions | Improves with feedback |

### **Step 5: Monitoring & Analytics**
| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| **GET** | `/metrics` | 📈 RL agent & system performance | Monitor AI learning |
| **GET** | `/streaming-performance` | 🚀 Video streaming analytics | Optimize delivery |
| **GET** | `/reports/storyboard-stats` | 📊 Video generation statistics | Track success rates |
| **GET** | `/reports/video-stats` | 🎬 Comprehensive video analytics | Performance insights |
| **GET** | `/logs` | 📝 System logs for debugging | Troubleshooting |

### **Step 6: Storage & Maintenance**
| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| **GET** | `/bucket/stats` | 🗄️ Storage backend configuration | Check S3/local setup |
| **GET** | `/bucket/list/{segment}` | 📋 List files in bucket segment | Browse stored content |
| **POST** | `/bucket/cleanup` | 🧹 Clean up temporary files | Maintenance tasks |
| **POST** | `/bucket/rotate-logs` | 📦 Archive old log files | Log management |
| **GET** | `/maintenance/failed-operations` | 🔍 View failed operations | Debug issues |

---

## 🚀 Complete User Journey Example

### **1. System Health Check**
```bash
# Check if system is running
curl "http://127.0.0.1:8000/health"
```

### **2. Authentication (Optional)**
```bash
# Get JWT token for secure operations
curl -X POST "http://127.0.0.1:8000/login" \
  -F "username=admin" \
  -F "password=change_me_in_production"
```

### **3. Upload Content**
```bash
# Upload an image file
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@example.jpg" \
  -F "title=Sample Image" \
  -F "description=Testing upload functionality"

# Generate video from script
curl -X POST "http://127.0.0.1:8000/generate-video" \
  -F "file=@scripts/sample_video_script.txt" \
  -F "title=Demo Video"
```

### **4. Browse & Access Content**
```bash
# List all content
curl "http://127.0.0.1:8000/contents"

# Get specific content details
curl "http://127.0.0.1:8000/content/abc123def456_789012"

# Stream video content
curl "http://127.0.0.1:8000/stream/abc123def456_789012"
```

### **5. Provide Feedback (Trains AI)**
```bash
# Submit user feedback
curl -X POST "http://127.0.0.1:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "abc123def456_789012",
    "user_id": "user123",
    "event_type": "like",
    "watch_time_ms": 15000
  }'
```

### **6. Get AI Recommendations**
```bash
# Get AI-powered tag suggestions
curl "http://127.0.0.1:8000/recommend-tags/abc123def456_789012"
```

### **7. Monitor Performance**
```bash
# Check system metrics
curl "http://127.0.0.1:8000/metrics"

# View streaming performance
curl "http://127.0.0.1:8000/streaming-performance"

# Get video statistics
curl "http://127.0.0.1:8000/reports/video-stats"
```

### **8. Storage Management**
```bash
# Check storage backend configuration
curl "http://127.0.0.1:8000/bucket/stats"

# List files in videos segment
curl "http://127.0.0.1:8000/bucket/list/videos"

# Clean up temporary files older than 24 hours
curl -X POST "http://127.0.0.1:8000/bucket/cleanup?max_age_hours=24"

# Archive logs older than 7 days
curl -X POST "http://127.0.0.1:8000/bucket/rotate-logs?max_age_days=7"

# View failed operations for debugging
curl "http://127.0.0.1:8000/maintenance/failed-operations"
```

---

## 🎯 Recommended User Flow

1. **Start Here**: `/health` → Verify system is operational
2. **Authentication**: `/login` → Get access token (if needed)
3. **Create Content**: `/upload` or `/generate-video` → Add content to system
4. **Explore Content**: `/contents` → Browse available content
5. **Interact**: `/content/{id}`, `/stream/{id}` → Access specific content
6. **Train AI**: `/feedback` → Provide feedback to improve recommendations
7. **Get Suggestions**: `/recommend-tags/{id}` → See AI-powered recommendations
8. **Monitor**: `/metrics`, `/reports/*` → Track system performance

## 📱 Interactive Testing

Visit the **Swagger UI** at `http://127.0.0.1:8000/docs` to test all endpoints interactively with a user-friendly interface.
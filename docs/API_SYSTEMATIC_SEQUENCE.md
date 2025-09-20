# API ENDPOINTS - SYSTEMATIC WORKFLOW SEQUENCE

## 🔄 **SYSTEMATIC USER JOURNEY**

### **1. SYSTEM HEALTH & STATUS**
```
GET  /health                    # ✅ Verify system is running
```

### **2. AUTHENTICATION & USER MANAGEMENT**
```
GET  /demo-login               # 🔐 Get demo credentials
POST /register                 # 👤 Create new account
POST /login                    # 🔑 Get JWT token
```

### **3. CONTENT MANAGEMENT**
```
GET  /contents                 # 📋 Browse available content
POST /upload                   # 📤 Upload files (images, videos, PDFs)
POST /generate-video           # 🎬 Generate video from text script
```

### **4. CONTENT ACCESS & STREAMING**
```
GET  /content/{id}             # 📊 Get content metadata & stats
GET  /download/{id}            # ⬇️ Secure file download
GET  /stream/{id}              # 🎥 HTTP range video streaming
```

### **5. AI LEARNING & RECOMMENDATIONS**
```
POST /feedback                 # 🤖 Submit feedback (trains RL agent)
GET  /recommend-tags/{id}      # 🏷️ AI-powered tag suggestions
POST /rate/{content_id}        # ⭐ Rate content (alternative feedback)
```

### **6. ANALYTICS & MONITORING**
```
GET  /metrics                  # 📈 RL agent performance metrics
GET  /logs                     # 📝 System logs (admin access)
GET  /streaming-performance    # 🚀 Real-time streaming analytics
GET  /reports/storyboard-stats # 📊 Video generation statistics
GET  /reports/video-stats      # 🎬 Comprehensive video analytics
```

### **7. BHIV CORE INTEGRATION**
```
POST /ingest/webhook           # 🔗 External content ingestion
GET  /core/stats               # ⚙️ Core processing statistics
GET  /core/metadata/{id}       # 📋 Core processing metadata
GET  /lm/stats                 # 🧠 LLM client configuration
```

### **8. BUCKET MANAGEMENT & MAINTENANCE**
```
GET  /bucket/stats             # 💾 Storage backend statistics
POST /bucket/cleanup           # 🧹 Clean temporary files
POST /bucket/rotate-logs       # 📦 Archive old log files
GET  /bucket/list/{segment}    # 📁 List files in bucket segment
```

### **9. MAINTENANCE UTILITIES**
```
GET  /maintenance/failed-operations  # 🔧 Debug failed operations
GET  /tasks/{task_id}               # ⏳ Async task status
GET  /tasks/queue/stats             # 📊 Task queue statistics
```

## 🎯 **RECOMMENDED WORKFLOW SEQUENCE**

1. **Start** → `GET /health`
2. **Authenticate** → `POST /login` (or `/demo-login` for testing)
3. **Upload Content** → `POST /upload` or `POST /generate-video`
4. **Access Content** → `GET /content/{id}` → `GET /stream/{id}`
5. **Provide Feedback** → `POST /feedback`
6. **Get Recommendations** → `GET /recommend-tags/{id}`
7. **Monitor Performance** → `GET /metrics` → `GET /streaming-performance`

## 📊 **ENDPOINT CATEGORIES**

- **Core User Flow**: `/health` → `/login` → `/upload` → `/stream` → `/feedback`
- **Content Discovery**: `/contents` → `/content/{id}` → `/recommend-tags/{id}`
- **Video Generation**: `/generate-video` → `/reports/storyboard-stats`
- **System Monitoring**: `/metrics` → `/logs` → `/streaming-performance`
- **Advanced Features**: `/ingest/webhook` → `/bucket/stats` → `/tasks/{id}`
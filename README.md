# 🤖 AI Content Uploader Agent with Reinforcement Learning

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-blue.svg)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade AI-powered content management system with Q-Learning reinforcement learning for intelligent content analysis, video generation, and personalized recommendations.

## 🎯 Project Overview

### Core Capabilities
- **🧠 AI-Powered Content Analysis** - Intelligent content classification and authenticity scoring
- **🎬 Automated Video Generation** - Text-to-video synthesis with storyboard creation
- **🔄 Reinforcement Learning** - Q-Learning agent for adaptive tag recommendations
- **📊 Real-time Analytics** - Comprehensive system monitoring and user insights
- **🔒 Enterprise Security** - JWT authentication, rate limiting, and input validation
- **☁️ Cloud-Native Storage** - Supabase PostgreSQL with local bucket fallback

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Supabase) + SQLite fallback
- **AI/ML**: Q-Learning RL Agent, LLM Integration (Ollama/Perplexity)
- **Video Processing**: MoviePy, ImageMagick
- **Analytics**: Streamlit Dashboard
- **Storage**: Local bucket system with S3 compatibility
- **Monitoring**: Sentry, PostHog, structured logging

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or use included SQLite)
- ImageMagick (for video generation)
- Git

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Ai-Agent-main

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Initialize database
python -c "from core.database import create_db_and_tables; create_db_and_tables()"

# 6. Start API server
python start_server.py
```

### Access Points
- **API Documentation**: http://127.0.0.1:8000/docs
- **Analytics Dashboard**: http://localhost:8501 (run `python start_dashboard.py`)
- **Admin Logs**: `GET /logs?admin_key=logs_2025`

## 📋 System Architecture

### 9-Step Workflow Organization

| Step | Component | Description | Key Endpoints |
|------|-----------|-------------|---------------|
| **1** | System Health | Status checks and demo access | `/health`, `/demo-login` |
| **2** | Authentication | User management and security | `/users/register`, `/users/login` |
| **3** | Content Upload | File upload and video generation | `/upload`, `/generate-video` |
| **4** | Content Access | Streaming and downloads | `/content/{id}`, `/stream/{id}` |
| **5** | AI Feedback | RL training and recommendations | `/feedback`, `/recommend-tags/{id}` |
| **6** | Analytics | System metrics and monitoring | `/metrics`, `/bhiv/analytics` |
| **7** | Task Queue | Background processing | `/tasks/{id}`, `/tasks/queue/stats` |
| **8** | Maintenance | System operations | `/bucket/cleanup`, `/logs` |
| **9** | Dashboard | Web interface | `/dashboard` |

### Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File Upload   │───▶│  Content Analysis │───▶│  RL Agent       │
│   (Multi-modal) │    │  & Classification │    │  (Q-Learning)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Bucket Storage  │    │ Supabase Database│    │ Tag Recommendations
│ (Local/S3)      │    │ (PostgreSQL)     │    │ & Personalization│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🗂️ Storage System

### Bucket Organization
```
bucket/
├── scripts/          # Uploaded and generated scripts (.txt)
├── storyboards/      # Video storyboard JSON files
├── videos/           # Generated video files (.mp4)
├── uploads/          # All uploaded content files
├── ratings/          # User feedback and ratings
├── logs/             # System operation logs
└── tmp/              # Temporary files (auto-cleaned)
```

### Database Schema
- **Users**: Authentication and profile data
- **Content**: File metadata, tags, and analytics
- **Scripts**: Text scripts for video generation
- **Feedback**: User ratings and RL training data

## 🎬 Video Generation Pipeline

1. **Script Upload** → Text file processing and validation
2. **Content Analysis** → Tag generation and authenticity scoring
3. **Storyboard Creation** → Scene breakdown and frame planning
4. **Video Synthesis** → MoviePy rendering with text overlays
5. **Storage & Database** → Multi-location persistence
6. **RL Integration** → Agent learning from user feedback

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Security
JWT_SECRET_KEY=your-secret-key

# AI Services
PERPLEXITY_API_KEY=your-api-key
BHIV_LM_URL=http://localhost:8001

# Storage
BHIV_STORAGE_BACKEND=local  # or 's3'
BHIV_BUCKET_PATH=bucket

# Monitoring
SENTRY_DSN=your-sentry-dsn
POSTHOG_API_KEY=your-posthog-key
```

## 🧪 Testing & Verification

```bash
# Test bucket functionality
python simple_test.py

# Test Supabase connection
python test_supabase.py

# Verify video generation pipeline
python verify_supabase_save.py

# Run full test suite
python -m pytest tests/
```

## 📊 Key Features

### 🤖 Reinforcement Learning
- **Q-Learning Algorithm**: Adaptive tag recommendation system
- **User Feedback Integration**: Continuous learning from ratings
- **Personalization**: Content recommendations based on user behavior
- **Performance Metrics**: Epsilon-greedy exploration with reward tracking

### 🎥 Video Generation
- **Text-to-Video**: Automatic video creation from script files
- **Storyboard Generation**: Scene planning and frame composition
- **Multi-format Support**: MP4 output with customizable parameters
- **Batch Processing**: Queue-based video generation

### 📈 Analytics & Monitoring
- **Real-time Metrics**: System performance and user engagement
- **Sentiment Analysis**: Content feedback classification
- **Usage Analytics**: Content popularity and user patterns
- **Performance Monitoring**: API response times and error tracking

### 🔐 Security Features
- **JWT Authentication**: Secure user sessions
- **Rate Limiting**: API abuse prevention
- **Input Validation**: XSS and injection protection
- **File Type Restrictions**: Safe upload handling
- **Admin Access Controls**: Privileged operation protection

## 🚀 Deployment

### Production Checklist
- [ ] Configure PostgreSQL database
- [ ] Set up environment variables
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificates
- [ ] Configure monitoring (Sentry/PostHog)
- [ ] Set up backup procedures
- [ ] Configure log rotation

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📚 API Documentation

### Core Endpoints

#### Content Management
- `POST /upload` - Upload multi-modal content files
- `POST /generate-video` - Create video from text script
- `GET /content/{id}` - Retrieve content metadata
- `GET /stream/{id}` - Stream video content with range support

#### AI & Learning
- `POST /feedback` - Submit user feedback for RL training
- `GET /recommend-tags/{id}` - Get AI-powered tag suggestions
- `GET /rl/agent-stats` - View RL agent performance metrics

#### Analytics
- `GET /metrics` - System performance metrics
- `GET /bhiv/analytics` - Advanced analytics with sentiment analysis
- `GET /streaming-performance` - Video streaming statistics

#### Administration
- `GET /logs?admin_key=logs_2025` - Access system logs
- `POST /bucket/cleanup` - Clean up old files
- `GET /bucket/stats` - Storage usage statistics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/README.md](docs/README.md)
- **API Reference**: http://127.0.0.1:8000/docs
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Built with ❤️ using FastAPI, PostgreSQL, and AI/ML technologies**
# AI-Agent: Advanced Content Management & Video Generation Platform

[![CI/CD Status](https://github.com/Ashmit-299/Ai-Agent/actions/workflows/ci-cd-production.yml/badge.svg)](https://github.com/Ashmit-299/Ai-Agent/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenAPI Docs](https://img.shields.io/badge/api-docs-brightgreen)](http://localhost:9000/docs)
[![GDPR Compliant](https://img.shields.io/badge/GDPR-Compliant-blue.svg)](docs/privacy.md)
[![Load Tested](https://img.shields.io/badge/Load%20Tested-100%20Users-green.svg)](tests/load_testing/)

---

## Table of Contents

- [Features](#features)
- [Live Demo & Dashboards](#live-demo--dashboards)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running Locally](#running-locally)
- [Environment Configuration](#environment-configuration)
- [Database & Migrations](#database--migrations)
- [Testing & Quality](#testing--quality)
- [Deployment: CI/CD & Cloud](#deployment-cicd--cloud)
- [Observability & Monitoring](#observability--monitoring)
- [Security Practices](#security-practices)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### 🚀 **Core Platform**
- **9-Step AI Workflow**: Systematic content processing pipeline (upload → analysis → generation → feedback)
- **Multi-Storage Support**: Supabase Storage, AWS S3, MinIO, and local file system
- **Advanced Authentication**: JWT with refresh tokens, rate limiting, brute-force protection
- **Database Flexibility**: PostgreSQL (Supabase), SQLite fallback with auto-migration
- **Video Generation**: MoviePy-powered multi-frame video creation from scripts
- **Q-Learning RL Agent**: AI-powered content recommendations and tag suggestions

### 🔒 **Security & Compliance**
- **GDPR Compliance**: Complete data export, deletion, and privacy controls
- **Advanced Rate Limiting**: Redis-based with in-memory fallback, per-user and IP limits
- **Security Middleware**: CORS, input validation, file type restrictions
- **Audit Logging**: Comprehensive tracking of all data processing activities
- **Data Retention**: Automated cleanup based on retention policies

### 📊 **Monitoring & Analytics**
- **Observability**: Sentry error tracking, PostHog user analytics
- **Performance Monitoring**: Real-time metrics, load testing (100+ concurrent users)
- **Streaming Analytics**: Video streaming performance and user engagement
- **System Health**: Detailed health checks and performance metrics

### 🌐 **API & Integration**
- **REST/Async API**: 60+ endpoints with auto-generated documentation
- **CDN Integration**: Presigned URLs, direct uploads, streaming optimization
- **Webhook Support**: External content ingestion and processing
- **Load Balancing**: Auto-scaling with health monitoring

---

## Live Demo & Dashboards

### Production (Render Cloud)
- **Production Backend API:** [https://ai-agent-aff6.onrender.com](https://ai-agent-aff6.onrender.com)
- **API Docs (Swagger/OpenAPI):** [https://ai-agent-aff6.onrender.com/docs](https://ai-agent-aff6.onrender.com/docs)
- **AI Agent Dashboard:** [https://ai-agent-aff6.onrender.com/dashboard](https://ai-agent-aff6.onrender.com/dashboard)
- **Detailed Health & Metrics:** [https://ai-agent-aff6.onrender.com/health/detailed](https://ai-agent-aff6.onrender.com/health/detailed)
- **GDPR Privacy Portal:** [https://ai-agent-aff6.onrender.com/gdpr/privacy-policy](https://ai-agent-aff6.onrender.com/gdpr/privacy-policy)
- **CDN Upload Portal:** [https://ai-agent-aff6.onrender.com/cdn/upload-url](https://ai-agent-aff6.onrender.com/cdn/upload-url)

### Local Development (Port 9000) - Complete Testing Endpoints

#### **🏠 Core System Endpoints**
- **Main API:** [http://localhost:9000](http://localhost:9000)
- **API Documentation:** [http://localhost:9000/docs](http://localhost:9000/docs)
- **OpenAPI Schema:** [http://localhost:9000/openapi.json](http://localhost:9000/openapi.json)
- **Health Check:** [http://localhost:9000/health](http://localhost:9000/health)
- **Detailed Health:** [http://localhost:9000/health/detailed](http://localhost:9000/health/detailed)

#### **🔍 Debug & Testing Endpoints**
- **Debug Routes:** [http://localhost:9000/debug-routes](http://localhost:9000/debug-routes)
- **Auth Debug:** [http://localhost:9000/debug-auth](http://localhost:9000/debug-auth)
- **Demo Login:** [http://localhost:9000/demo-login](http://localhost:9000/demo-login)
- **Test Server:** [http://localhost:9000/test](http://localhost:9000/test)
- **Data Saving Test:** [http://localhost:9000/test-data-saving](http://localhost:9000/test-data-saving)

#### **🔐 Authentication Endpoints**
- **User Registration:** [http://localhost:9000/users/register](http://localhost:9000/users/register)
- **User Login:** [http://localhost:9000/users/login](http://localhost:9000/users/login)
- **User Profile:** [http://localhost:9000/users/profile](http://localhost:9000/users/profile)
- **Refresh Token:** [http://localhost:9000/users/refresh](http://localhost:9000/users/refresh)
- **Supabase Auth Health:** [http://localhost:9000/users/supabase-auth-health](http://localhost:9000/users/supabase-auth-health)

#### **📊 Metrics & Monitoring Endpoints**
- **Metrics Info:** [http://localhost:9000/metrics](http://localhost:9000/metrics)
- **Prometheus Metrics:** [http://localhost:9000/metrics/prometheus](http://localhost:9000/metrics/prometheus)
- **Performance Metrics:** [http://localhost:9000/metrics/performance](http://localhost:9000/metrics/performance)
- **Observability Health:** [http://localhost:9000/observability/health](http://localhost:9000/observability/health)
- **Monitoring Status:** [http://localhost:9000/monitoring-status](http://localhost:9000/monitoring-status)

#### **📁 Content & Upload Endpoints**
- **Upload Content:** [http://localhost:9000/upload](http://localhost:9000/upload)
- **Generate Video:** [http://localhost:9000/generate-video](http://localhost:9000/generate-video)
- **Browse Content:** [http://localhost:9000/contents](http://localhost:9000/contents)
- **Content Details:** [http://localhost:9000/content/{id}](http://localhost:9000/content/)
- **Download Content:** [http://localhost:9000/download/{id}](http://localhost:9000/download/)
- **Stream Content:** [http://localhost:9000/stream/{id}](http://localhost:9000/stream/)

#### **🌐 CDN & File Management Endpoints**
- **CDN Upload URL:** [http://localhost:9000/cdn/upload-url](http://localhost:9000/cdn/upload-url)
- **CDN Upload:** [http://localhost:9000/cdn/upload/{token}](http://localhost:9000/cdn/upload/)
- **CDN Download:** [http://localhost:9000/cdn/download/{id}](http://localhost:9000/cdn/download/)
- **CDN Stream:** [http://localhost:9000/cdn/stream/{id}](http://localhost:9000/cdn/stream/)
- **CDN List Files:** [http://localhost:9000/cdn/list](http://localhost:9000/cdn/list)
- **CDN File Info:** [http://localhost:9000/cdn/info/{id}](http://localhost:9000/cdn/info/)

#### **🤖 AI & Analytics Endpoints**
- **Submit Feedback:** [http://localhost:9000/feedback](http://localhost:9000/feedback)
- **Tag Recommendations:** [http://localhost:9000/recommend-tags/{id}](http://localhost:9000/recommend-tags/)
- **Average Rating:** [http://localhost:9000/average-rating/{id}](http://localhost:9000/average-rating/)
- **RL Agent Stats:** [http://localhost:9000/rl/agent-stats](http://localhost:9000/rl/agent-stats)
- **Analytics:** [http://localhost:9000/bhiv/analytics](http://localhost:9000/bhiv/analytics)

#### **🔒 GDPR & Privacy Endpoints**
- **Privacy Policy:** [http://localhost:9000/gdpr/privacy-policy](http://localhost:9000/gdpr/privacy-policy)
- **Export Data:** [http://localhost:9000/gdpr/export-data](http://localhost:9000/gdpr/export-data)
- **Delete Data:** [http://localhost:9000/gdpr/delete-data](http://localhost:9000/gdpr/delete-data)
- **Data Summary:** [http://localhost:9000/gdpr/data-summary](http://localhost:9000/gdpr/data-summary)

#### **⚙️ System Management Endpoints**
- **Task Status:** [http://localhost:9000/tasks/{id}](http://localhost:9000/tasks/)
- **Queue Stats:** [http://localhost:9000/tasks/queue/stats](http://localhost:9000/tasks/queue/stats)
- **Storage Status:** [http://localhost:9000/storage/status](http://localhost:9000/storage/status)
- **Bucket Stats:** [http://localhost:9000/bucket/stats](http://localhost:9000/bucket/stats)
- **Dashboard:** [http://localhost:9000/dashboard](http://localhost:9000/dashboard)

### Monitoring Dashboards
- **Sentry Error Tracking:** [https://blackhole-ig.sentry.io/insights/projects/python/](https://blackhole-ig.sentry.io/insights/projects/python/)
- **PostHog User Analytics:** [https://us.posthog.com/project/222470](https://us.posthog.com/project/222470)

---

## Architecture Overview

flowchart TD
subgraph Pipeline
A[Uploader/API] --> B[Script Storage]
B --> C[Storyboard Generator]
C --> D[Video Generator]
D --> E[Content Store]
E --> F[AI RL Agent]
F --> G[Analytics/Feedback]
end
E -- API --> H[Streaming/Download]
G -- API --> I[Dashboard/Monitoring]

text

- **Backend:** FastAPI (async, modular)
- **Database:** PostgreSQL (production/Supabase), SQLite (dev), SQLModel+Alembic
- **Auth:** JWT/refresh tokens, strong password hashing, lockout protection
- **Deployment:** Docker, Render, GitHub Actions CI/CD
- **Monitoring:** Sentry for error reporting; PostHog for user analytics

---

### System Components
```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│  🌐 Render Cloud Platform                                   │
│  ├── 🔒 SSL/HTTPS Termination                              │
│  ├── ⚡ Auto-scaling & Load Balancing                      │
│  └── 📊 Health Monitoring                                  │
├─────────────────────────────────────────────────────────────────┤
│  🐍 FastAPI Application Server                             │
│  ├── 🔐 JWT Authentication Layer                           │
│  ├── 🛡️ Security Middleware (CORS, Rate Limiting)          │
│  ├── 📁 Multi-modal Content Processing                     │
│  ├── 🤖 Q-Learning RL Agent                               │
│  ├── 🎬 Video Generation Pipeline                          │
│  └── 📈 Analytics & Monitoring                            │
├─────────────────────────────────────────────────────────────────┤
│  🗄️ Data Layer                                             │
│  ├── 🐘 Supabase PostgreSQL (Primary)                     │
│  ├── 💾 SQLite (Fallback)                                 │
│  ├── 🪣 Bucket Storage System                             │
│  └── 📊 Analytics Data Store                              │
└─────────────────────────────────────────────────────────────────┘

## Project Structure

```
ai-agent/
├── 📁 ROOT CONFIGURATION
│   ├── .env.example                    # Environment variables template
│   ├── .gitignore                      # Git ignore rules
│   ├── .python-version                 # Python version specification
│   ├── agent_state.json                # Agent state persistence
│   ├── alembic.ini                     # Database migration config
│   ├── Dockerfile                      # Production container
│   ├── LICENSE                         # MIT license
│   ├── pytest.ini                     # Test configuration
│   ├── README.md                       # Project documentation
│   ├── render.yaml                     # Deployment configuration
│   ├── requirements.txt                # Python dependencies
│   └── runtime.txt                     # Runtime specification
│
├── 📁 app/                             # FastAPI Application
│   ├── __init__.py
│   ├── main.py                         # FastAPI main application
│   ├── routes.py                       # API route definitions
│   ├── models.py                       # Pydantic models
│   ├── auth.py                         # Authentication system
│   ├── security.py                     # Security utilities
│   ├── agent.py                        # AI agent logic
│   ├── observability.py                # Monitoring integration
│   ├── streaming_metrics.py            # Streaming analytics
│   ├── task_queue.py                   # Background tasks
│   ├── streamlit_dashboard.py          # Dashboard interface
│   └── templates/                      # HTML templates
│
├── 📁 core/                            # Core Business Logic
│   ├── __init__.py
│   ├── database.py                     # Database management
│   ├── models.py                       # SQLModel database models
│   ├── bhiv_bucket.py                  # Storage system
│   ├── bhiv_core.py                    # Core functionality
│   ├── bhiv_lm_client.py               # Language model client
│   └── sentiment_analyzer.py           # Sentiment analysis
│
├── 📁 video/                           # Video Generation Pipeline
│   ├── __init__.py
│   ├── generator.py                    # Video generation logic
│   ├── storyboard.py                   # Storyboard creation
│   └── failed_cases.py                 # Error handling
│
├── 📁 scripts/                         # Utility Scripts
│   ├── __init__.py
│   ├── start_server.py                 # Server startup
│   ├── start_dashboard.py              # Dashboard startup
│   ├── setup_project.py                # Project setup
│   ├── health-check.py                 # Health monitoring
│   ├── maintenance/                    # Maintenance scripts
│   │   ├── debug_*.py                  # Debug utilities
│   │   ├── fix_*.py                    # Fix scripts
│   │   ├── verify_*.py                 # Verification tools
│   │   └── test_*.py                   # Test utilities
│   ├── deployment/                     # Deployment scripts
│   │   ├── deploy.py                   # Deployment automation
│   │   ├── build.sh                    # Build scripts
│   │   └── force_deployment.py         # Force deployment
│   └── migration/                      # Database migrations
│       ├── run_migrations.py           # Migration runner
│       └── migrate_*.py                # Migration scripts
│
├── 📁 tests/                           # Test Suite
│   ├── __init__.py
│   ├── conftest.py                     # pytest configuration
│   ├── integration/                    # Integration tests
│   │   ├── test_auth_flow.py           # Authentication tests
│   │   ├── test_supabase.py            # Database tests
│   │   └── test_demo_login.py          # Demo functionality
│   ├── unit/                          # Unit tests
│   │   ├── test_database.py            # Database unit tests
│   │   ├── test_observability.py       # Monitoring tests
│   │   └── test_*.py                   # Component tests
│   ├── load_testing/                  # Load & Performance tests
│   │   ├── locust_load_test.py         # Locust load testing (100 users)
│   │   └── stress_test.py              # Async stress testing
│   └── fixtures/                      # Test fixtures
│       ├── test_output.txt             # Test data
│       └── test_user_credentials.json  # Test credentials
│
├── 📁 docs/                            # Documentation
│   ├── __init__.py
│   ├── endpoint_security_guide.md      # Security documentation
│   ├── testing_instructions.md         # Testing guide
│   ├── privacy.md                      # Privacy policy & GDPR compliance
│   ├── deployment/                     # Deployment docs
│   │   └── render_deploy.md            # Render deployment
│   └── reports/                       # Generated reports
│       ├── DEPLOYMENT_GUIDE.md         # Deployment reports
│       ├── TEST_SUMMARY.md             # Test reports
│       └── *.md                       # Various reports
│
├── 📁 data/                            # Data Files
│   ├── __init__.py
│   ├── data.db-*                       # SQLite database files
│   └── reports/                       # Data reports
│       ├── health-check-*.json         # Health check reports
│       └── *.json                     # Various data reports
│
├── 📁 migrations/                      # Database Migrations
│   ├── README                          # Migration instructions
│   ├── env.py                          # Alembic environment
│   ├── script.py.mako                  # Migration template
│   └── versions/                      # Migration versions
│
├── 📁 .github/                         # CI/CD Workflows
│   └── workflows/
│       └── ci-cd-production.yml        # GitHub Actions
│
├── 📁 docker/                          # Container Configuration
│   └── docker-compose.yml              # Docker setup
│
├── 📁 bucket/                          # Local Storage
│   ├── logs/                           # Application logs
│   ├── ratings/                        # User ratings
│   ├── scripts/                        # Stored scripts
│   └── storyboards/                    # Generated storyboards
│
└── 📁 uploads/                         # File uploads
    └── (uploaded content files)
```

---

## Setup & Installation

Clone the project and enter the directory
git clone https://github.com/Ashmit-299/Ai-Agent.git && cd Ai-Agent

Create and activate Python virtual environment
python3 -m venv env
source env/bin/activate

Install all Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

Set up your .env file
cp .env.example .env

Fill out DATABASE_URL, JWT_SECRET_KEY, SENTRY_DSN, POSTHOG_API_KEY, etc.
text

---

#### Installation

```bash
# 1. Clone repository
git clone https://github.com/Ashmit-299/Ai-Agent.git
cd Ai-Agent

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

# 6. Start API server (Port 9000)
python scripts/start_server.py

# 7. Verify monitoring connection
python final_monitoring_check.py

# 8. Start Streamlit dashboard (optional)
python scripts/start_dashboard.py
```

#### Docker Deployment
```bash
# Quick start with Docker
docker-compose up -d

# Or build manually
docker build -t ai-agent .
docker run -p 9000:9000 ai-agent

## Running Locally

### Quick Start
```bash
# Start the main server on port 9000
python scripts/start_server.py
```

### Manual Start
```bash
# Start with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

### 🧪 **Complete Testing Guide**

#### **Step 1: Basic System Test**
```bash
# Test server health
curl http://localhost:9000/health

# Get demo credentials
curl http://localhost:9000/demo-login

# Test authentication
curl http://localhost:9000/debug-auth
```

#### **Step 2: Authentication Test**
```bash
# Login with demo credentials
curl -X POST http://localhost:9000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo1234"

# Test Supabase auth health
curl http://localhost:9000/users/supabase-auth-health
```

#### **Step 3: Metrics & Monitoring Test**
```bash
# Check metrics info
curl http://localhost:9000/metrics

# Get Prometheus metrics
curl http://localhost:9000/metrics/prometheus

# Check performance metrics
curl http://localhost:9000/metrics/performance

# Test observability
curl http://localhost:9000/observability/health
```

#### **Step 4: Content & Upload Test**
```bash
# Get CDN upload URL
curl http://localhost:9000/cdn/upload-url

# Browse existing content
curl http://localhost:9000/contents

# Test analytics
curl http://localhost:9000/bhiv/analytics
```

#### **Step 5: GDPR & Privacy Test**
```bash
# Check privacy policy
curl http://localhost:9000/gdpr/privacy-policy

# Test data summary (requires auth)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:9000/gdpr/data-summary
```

### 🔧 **Automated Testing Scripts**
```bash
# Run integration tests
python check_integrations.py

# Test live connections
python test_live_connections.py

# Test Prometheus integration
python test_prometheus_integration.py

# Test JWKS authentication
python test_jwks_integration.py

# Test all endpoints
python test_auth_endpoints.py
```

text

---

## Environment Configuration

Put all secrets and config in `.env`:

# Database Configuration
DATABASE_URL=postgresql://postgres:<password>@<host>:5432/ai_agent

# Authentication & Security
JWT_SECRET_KEY=<your-very-secure-jwt-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Observability & Monitoring
SENTRY_DSN=https://blackhole-ig.sentry.io/xxx
POSTHOG_API_KEY=phc_...
POSTHOG_HOST=https://us.posthog.com
ENVIRONMENT=development

# Storage Configuration (Multi-backend support)
USE_S3_STORAGE=false
USE_SUPABASE_STORAGE=true
BHIV_STORAGE_BACKEND=supabase  # Options: local, s3, supabase

# S3/MinIO Storage (if USE_S3_STORAGE=true)
S3_BUCKET_NAME=ai-agent-storage
S3_REGION=us-east-1
S3_ENDPOINT_URL=  # For MinIO, leave empty for AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Supabase Storage (if USE_SUPABASE_STORAGE=true)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET_NAME=ai-agent-files

# Local Storage
BHIV_BUCKET_PATH=bucket

# Rate Limiting & Performance
REDIS_URL=redis://localhost:6379
MAX_UPLOAD_SIZE_MB=100
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# GDPR & Privacy
DATA_RETENTION_DAYS=365
AUTO_DELETE_EXPIRED_DATA=true
GDPR_CONTACT_EMAIL=privacy@yourcompany.com

text

---

## Database & Migrations

Apply migrations (any environment):

python scripts/migration/run_migrations.py upgrade

text

- Create DB schema (dev only):  
  `python -c "from core.database import create_db_and_tables; create_db_and_tables()"`
- Rollback (optional):  
  `python scripts/migration/run_migrations.py rollback <revision>`

---

## Testing & Quality

```bash
# Run all tests with coverage
python scripts/test_coverage.py

# Individual test categories
pytest tests/unit/           # unit tests only
pytest tests/integration/    # integration tests only

# Load testing (requires server running)
python scripts/run_load_tests.py

# Manual load testing with Locust UI
locust -f tests/load_testing/locust_load_test.py --host=http://localhost:9000
# Then open http://localhost:8089 for interactive testing

# Coverage reporting
pytest --cov=app --cov=core --cov=video --cov-report=html
```

### Load Testing
- **100 Concurrent Users**: Locust-based load testing
- **Stress Testing**: Async performance analysis
- **Coverage Target**: 70%+ code coverage
- **Performance Metrics**: Response times, error rates, throughput

Code style is enforced using Black/isort/flake8, security scan via Trivy/Bandit in CI/CD.

---

## Deployment: CI/CD & Cloud

### Automated (Production)
- **Production API:** [https://ai-agent-aff6.onrender.com](https://ai-agent-aff6.onrender.com)
- Full pipeline: GitHub Actions → Docker image → Render → auto-migrate → health-check → monitor Sentry/PostHog

### Manual (Dev)
docker-compose up --build

text

---

## Observability & Monitoring

### Production Monitoring
- **Sentry Error Tracking:** [https://blackhole-ig.sentry.io/insights/projects/python/](https://blackhole-ig.sentry.io/insights/projects/python/)
- **PostHog User Analytics:** [https://us.posthog.com/project/222470](https://us.posthog.com/project/222470)
- **Production Health:** [https://ai-agent-aff6.onrender.com/health/detailed](https://ai-agent-aff6.onrender.com/health/detailed)
- **Production Metrics:** [https://ai-agent-aff6.onrender.com/metrics](https://ai-agent-aff6.onrender.com/metrics)

### Local Monitoring (Port 9000)
- **Local Monitoring Status:** [http://localhost:9000/monitoring-status](http://localhost:9000/monitoring-status)
- **Test Monitoring Connection:** [http://localhost:9000/test-monitoring](http://localhost:9000/test-monitoring)
- **Local Health Check:** [http://localhost:9000/health](http://localhost:9000/health)
- **Performance Metrics:** [http://localhost:9000/metrics/performance](http://localhost:9000/metrics/performance)

### Configuration
Sentry DSN and PostHog API key must be set in `.env`:
```bash
SENTRY_DSN=https://0d595f5827bf2a4ae5da7d1ed1a09338@o4509949438328832.ingest.us.sentry.io/4510035576946688
POSTHOG_API_KEY=phc_lmGvuDZ7JiyjDmkL1T6Wy3TvDHgFdjt1zlH02fVziwU
```

---

## Security Practices

- JWT & refresh tokens, secure password hashing (bcrypt)
- **Advanced Rate Limiting**: Redis-based with in-memory fallback, per-user and IP-based limits
- **Async Endpoints**: High-performance async processing for uploads, feedback, and analytics
- Input validation, rate limiting, lockout on brute force
- CORS and secure-headers middleware enabled
- Production secrets never checked into repo—use `.env` config
- Security checks (Trivy, Bandit) run in CI
- **GDPR Compliance**: Complete data export, deletion, and privacy controls
- **Audit Logging**: Comprehensive tracking of all data processing activities
- **Data Retention**: Automated cleanup based on retention policies

---

## API Reference

### 📚 **API Documentation**
- **Production Swagger:** [https://ai-agent-aff6.onrender.com/docs](https://ai-agent-aff6.onrender.com/docs)
- **Local Swagger:** [http://localhost:9000/docs](http://localhost:9000/docs)
- **OpenAPI Schema:** [http://localhost:9000/openapi.json](http://localhost:9000/openapi.json)

### 🔍 **Debug & Testing Endpoints**
- **Route Enumeration:** `GET /debug-routes` - List all available routes
- **Auth Testing:** `GET /debug-auth` - Test authentication status
- **Server Status:** `GET /test` - Basic server functionality test
- **Health Check:** `GET /health` - System health status
- **Demo Credentials:** `GET /demo-login` - Get test login credentials

### 🎯 **Core API Endpoints (60+ total)**

#### **STEP 1: System Health & Demo Access**
- `GET /health` - System health check
- `GET /demo-login` - Get demo credentials
- `GET /debug-auth` - Authentication debugging

#### **STEP 2: User Authentication**
- `POST /users/register` - User registration
- `POST /users/login` - User login (JWT tokens)
- `GET /users/profile` - User profile
- `POST /users/refresh` - Refresh JWT token

#### **STEP 3: Content Upload & Video Generation**
- `POST /upload` - Upload content files (100MB max)
- `POST /generate-video` - Generate video from script
- `GET /contents` - Browse existing content

#### **STEP 4: Content Access & Streaming**
- `GET /content/{id}` - Get content details
- `GET /content/{id}/metadata` - Detailed content metadata
- `GET /download/{id}` - Download content file
- `GET /stream/{id}` - Stream video content (range support)

#### **STEP 5: AI Feedback & Tag Recommendations**
- `POST /feedback` - Submit content feedback (trains RL agent)
- `GET /recommend-tags/{id}` - AI-powered tag recommendations
- `GET /average-rating/{id}` - Get content average rating

#### **STEP 6: Analytics & Performance Monitoring**
- `GET /metrics` - System metrics and RL agent performance
- `GET /rl/agent-stats` - Detailed Q-Learning agent statistics
- `GET /bhiv/analytics` - Advanced analytics with sentiment analysis
- `GET /streaming-performance` - Real-time streaming analytics
- `GET /observability/health` - Observability system status
- `GET /observability/performance` - Detailed performance metrics

#### **CDN & File Management**
- `GET /cdn/upload-url` - Generate presigned upload URL
- `POST /cdn/upload/{token}` - Upload file using token
- `GET /cdn/download/{id}` - CDN file download
- `GET /cdn/stream/{id}` - CDN file streaming
- `GET /cdn/list` - List user's uploaded files
- `DELETE /cdn/delete/{id}` - Delete uploaded file
- `GET /cdn/info/{id}` - Get file information

#### **GDPR & Privacy Compliance**
- `GET /gdpr/privacy-policy` - Privacy policy and GDPR information
- `GET /gdpr/export-data` - Export all user data (requires auth)
- `DELETE /gdpr/delete-data` - Delete all user data (requires auth)
- `GET /gdpr/data-summary` - Summary of stored user data (requires auth)

#### **Task Queue & Background Processing**
- `GET /tasks/{id}` - Get task status
- `GET /tasks/queue/stats` - Task queue statistics
- `POST /tasks/create-test` - Create test background task

#### **System Maintenance (Admin)**
- `POST /bucket/cleanup` - Clean up old files (admin)
- `POST /bucket/rotate-logs` - Rotate log files (admin)
- `GET /maintenance/failed-operations` - List failed operations (admin)

#### **Storage & Bucket Management**
- `GET /storage/status` - Multi-backend storage status
- `POST /storage/presigned-upload` - Generate S3 presigned URLs
- `GET /bucket/stats` - Storage statistics
- `GET /bucket/list/{segment}` - List files in storage segment

---

## Contributing

Pull Requests are welcome!

- All new code must pass tests, linter, and security pipelines.
- Please add or update documentation and your tests.
- See `CONTRIBUTING.md` for style/contribution guidelines.

---

## Quick Reference

### 🚀 Local Development URLs (Port 9000)
```
Main Server:        http://localhost:9000
API Documentation:  http://localhost:9000/docs
Health Check:       http://localhost:9000/health
Monitoring Status:  http://localhost:9000/monitoring-status
Test Monitoring:    http://localhost:9000/test-monitoring
Dashboard:          http://localhost:9000/dashboard
```

### 🌐 Production URLs
```
Production API:     https://ai-agent-aff6.onrender.com
Production Docs:    https://ai-agent-aff6.onrender.com/docs
Production Health:  https://ai-agent-aff6.onrender.com/health/detailed
```

### 📊 **Access Your Dashboards:**

#### **🌐 Production Dashboards**
- **Sentry Error Tracking:** [https://blackhole-ig.sentry.io/insights/projects/python/](https://blackhole-ig.sentry.io/insights/projects/python/)
- **PostHog User Analytics:** [https://us.posthog.com/project/222470](https://us.posthog.com/project/222470)
- **Production API:** [https://ai-agent-aff6.onrender.com](https://ai-agent-aff6.onrender.com)
- **Production Health:** [https://ai-agent-aff6.onrender.com/health/detailed](https://ai-agent-aff6.onrender.com/health/detailed)

#### **🏠 Local Development Dashboards**
- **Local Health Check:** [http://localhost:9000/health/detailed](http://localhost:9000/health/detailed)
- **Prometheus Metrics:** [http://localhost:9000/metrics/prometheus](http://localhost:9000/metrics/prometheus)
- **Performance Dashboard:** [http://localhost:9000/metrics/performance](http://localhost:9000/metrics/performance)
- **API Documentation:** [http://localhost:9000/docs](http://localhost:9000/docs)
- **System Dashboard:** [http://localhost:9000/dashboard](http://localhost:9000/dashboard)

#### **🔧 Monitoring Setup (Optional)**
```bash
# Set up Prometheus monitoring (requires Docker)
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Set up Grafana dashboards (requires Docker)
docker run -d -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana

# Access dashboards
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (admin/admin)"
```

### 🧪 **Complete Testing & Debugging Suite**

#### **🔍 Integration & Health Testing**
```bash
# Complete integration status check
python check_integrations.py

# Test live service connections
python test_live_connections.py

# Check monitoring endpoints
python check_monitoring_endpoints.py

# Server status and restart check
python test_server_restart.py
```

#### **🔐 Authentication & Security Testing**
```bash
# Test JWKS authentication integration
python test_jwks_integration.py

# Test all authentication endpoints
python test_auth_endpoints.py

# JWT token testing
python fix_auth_token.py

# Get demo authentication token
python get_token.py
```

#### **📊 Metrics & Monitoring Testing**
```bash
# Test Prometheus integration
python test_prometheus_integration.py

# Monitor system performance
python monitor_performance.py

# Check port status
python port_status.py

# Test all imports
python test_imports.py
```

#### **📁 Upload & Content Testing**
```bash
# Comprehensive upload route testing
python test_upload_routes.py

# CDN endpoint testing
python test_cdn_simple.py

# Server startup debugging
python debug_server_startup.py
```

#### **🔒 GDPR & Privacy Testing**
```bash
# Test all GDPR endpoints
python test_gdpr_all.py

# Test data deletion functionality
python test_gdpr_delete.py

# Test data export features
python test_gdpr_endpoints.py
```

#### **⚡ Load & Performance Testing**
```bash
# Run comprehensive load tests (100 users)
python scripts/run_load_tests.py

# Interactive Locust load testing
locust -f tests/load_testing/locust_load_test.py --host=http://localhost:9000

# Test coverage analysis
python scripts/test_coverage.py

# Rate limiting tests
pytest tests/test_rate_limiting.py
```

#### **🎯 Quick Test Commands**
```bash
# Test everything at once
python -c "import subprocess; [subprocess.run(['python', f]) for f in ['check_integrations.py', 'test_prometheus_integration.py', 'test_jwks_integration.py']]"

# Health check all services
curl -s http://localhost:9000/health && echo " - Health OK" && \
curl -s http://localhost:9000/metrics && echo " - Metrics OK" && \
curl -s http://localhost:9000/users/supabase-auth-health && echo " - Auth OK"

# Generate test traffic for metrics
for i in {1..10}; do curl -s http://localhost:9000/health > /dev/null; done && \
echo "Traffic generated - check metrics at http://localhost:9000/metrics/prometheus"
```

---

## 📈 **Performance & Scale**

- **Load Tested**: 100+ concurrent users
- **Response Time**: <200ms average API response
- **File Upload**: Up to 100MB per file
- **Storage**: Multi-backend (Supabase/S3/Local)
- **Database**: PostgreSQL with SQLite fallback
- **Caching**: Redis-based rate limiting
- **Monitoring**: Real-time metrics and alerts

## 🤝 **Contributing**

Pull requests welcome! Please ensure:
- All tests pass (`python scripts/test_coverage.py`)
- Code follows style guidelines (Black/isort/flake8)
- Security scans pass (Bandit/Trivy)
- Documentation is updated

## 📄 **License & Support**

**MIT License** - See [LICENSE](LICENSE) file

**Project by [Ashmit Pandey](https://github.com/Ashmit-299) and contributors.**

**Support:**
- 📧 Email: [Contact via GitHub](https://github.com/Ashmit-299)
- 🐛 Issues: [GitHub Issues](https://github.com/Ashmit-299/Ai-Agent/issues)
- 📖 Docs: [Project Documentation](docs/)
- 🔒 Privacy: [GDPR Compliance](docs/privacy.md)

> _Last updated: 2025-01-02 | Version: 2.0.0 | 60+ API Endpoints | GDPR Compliant_
# Complete Deployment Guide - AI Agent Platform

## Overview

This guide covers all deployment options for the AI Agent Platform, from local development to production cloud deployment with multiple storage backends and monitoring.

## 🚀 **Quick Start (5 Minutes)**

### Local Development Setup
```bash
# 1. Clone and setup
git clone https://github.com/Ashmit-299/Ai-Agent.git
cd Ai-Agent
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Initialize database
python -c "from core.database import create_db_and_tables; create_db_and_tables()"

# 5. Start server (Port 9000)
python scripts/start_server.py
```

**Access URLs:**
- API: http://localhost:9000
- Docs: http://localhost:9000/docs
- Dashboard: http://localhost:9000/dashboard

---

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│  🌐 Load Balancer (Render/Nginx)                              │
│  ├── 🔒 SSL/HTTPS Termination                                 │
│  ├── ⚡ Auto-scaling & Health Checks                          │
│  └── 📊 Request Routing                                       │
├─────────────────────────────────────────────────────────────────┤
│  🐍 FastAPI Application (Port 9000)                           │
│  ├── 🔐 JWT Authentication Layer                              │
│  ├── 🛡️ Security Middleware (CORS, Rate Limiting)             │
│  ├── 📁 Multi-modal Content Processing                        │
│  ├── 🤖 Q-Learning RL Agent                                  │
│  ├── 🎬 Video Generation Pipeline                             │
│  └── 📈 Analytics & Monitoring                               │
├─────────────────────────────────────────────────────────────────┤
│  🗄️ Data Layer                                                │
│  ├── 🐘 PostgreSQL (Supabase/AWS RDS)                        │
│  ├── 💾 SQLite (Development/Fallback)                        │
│  ├── 🪣 Multi-Storage (Supabase/S3/MinIO/Local)              │
│  └── 📊 Redis (Rate Limiting/Caching)                        │
├─────────────────────────────────────────────────────────────────┤
│  📊 Monitoring & Observability                                │
│  ├── 🚨 Sentry (Error Tracking)                              │
│  ├── 📈 PostHog (User Analytics)                             │
│  ├── 📋 System Logs (Structured Logging)                     │
│  └── 🔍 Health Checks & Metrics                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Environment Configuration**

### Complete .env Template
```bash
# =============================================================================
# AI AGENT PLATFORM - PRODUCTION CONFIGURATION
# =============================================================================

# Application Settings
ENVIRONMENT=production
DEBUG=false
PORT=9000
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/ai_agent
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Authentication & Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=8

# Storage Configuration (Choose one primary backend)
# Option 1: Supabase Storage (Recommended)
USE_SUPABASE_STORAGE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET_NAME=ai-agent-files

# Option 2: AWS S3 Storage
USE_S3_STORAGE=false
S3_BUCKET_NAME=ai-agent-storage
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_ENDPOINT_URL=  # Leave empty for AWS S3, set for MinIO

# Option 3: Local Storage (Development only)
BHIV_STORAGE_BACKEND=supabase  # Options: supabase, s3, local
BHIV_BUCKET_PATH=bucket

# Rate Limiting & Performance
REDIS_URL=redis://localhost:6379
MAX_UPLOAD_SIZE_MB=100
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_UPLOAD_PER_MINUTE=10
RATE_LIMIT_FEEDBACK_PER_MINUTE=30

# Observability & Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
POSTHOG_API_KEY=phc_your_posthog_api_key
POSTHOG_HOST=https://us.posthog.com
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# GDPR & Privacy
DATA_RETENTION_DAYS=365
AUTO_DELETE_EXPIRED_DATA=true
GDPR_CONTACT_EMAIL=privacy@yourcompany.com
AUDIT_LOG_RETENTION_DAYS=2555  # 7 years

# Video Generation
MOVIEPY_TEMP_DIR=/tmp/moviepy
VIDEO_GENERATION_TIMEOUT=300
MAX_VIDEO_DURATION_SECONDS=600

# AI & Machine Learning
RL_AGENT_EPSILON=0.2
RL_AGENT_LEARNING_RATE=0.1
RL_AGENT_DISCOUNT_FACTOR=0.9
ENABLE_AI_TRAINING=true

# External Services
ENABLE_WEBHOOKS=true
WEBHOOK_SECRET=your-webhook-secret
EXTERNAL_API_TIMEOUT=30

# Development & Testing
ENABLE_DEBUG_ROUTES=false  # Set to true for development
ENABLE_LOAD_TESTING=false
TEST_USER_CLEANUP_DAYS=7
```

---

## 🐳 **Docker Deployment**

### Dockerfile (Production-Ready)
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p bucket/uploads bucket/videos bucket/scripts bucket/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=9000

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Run application
CMD ["python", "scripts/start_server.py"]
```

### Docker Compose (Full Stack)
```yaml
version: '3.8'

services:
  ai-agent:
    build: .
    ports:
      - "9000:9000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ai_agent
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./bucket:/app/bucket
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_agent
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-agent
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Quick Docker Start
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f ai-agent

# Scale application
docker-compose up -d --scale ai-agent=3
```

---

## ☁️ **Cloud Deployment Options**

### 1. Render (Recommended for MVP)

**render.yaml**
```yaml
services:
  - type: web
    name: ai-agent-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python scripts/start_server.py
    envVars:
      - key: PORT
        value: 9000
      - key: DATABASE_URL
        fromDatabase:
          name: ai-agent-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: ai-agent-redis
          property: connectionString
    healthCheckPath: /health
    autoDeploy: true

  - type: postgres
    name: ai-agent-db
    databaseName: ai_agent
    user: ai_agent_user

  - type: redis
    name: ai-agent-redis
    maxmemoryPolicy: allkeys-lru
```

**Deployment Steps:**
```bash
# 1. Connect GitHub repository to Render
# 2. Create new Web Service
# 3. Configure environment variables
# 4. Deploy automatically on git push
```

### 2. AWS Deployment (Production Scale)

**AWS Architecture:**
- **ECS Fargate**: Container orchestration
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed Redis
- **S3**: File storage
- **CloudFront**: CDN
- **ALB**: Load balancer
- **Route 53**: DNS

**Terraform Configuration:**
```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# ECS Cluster
resource "aws_ecs_cluster" "ai_agent" {
  name = "ai-agent-cluster"
}

# RDS PostgreSQL
resource "aws_db_instance" "ai_agent_db" {
  identifier = "ai-agent-db"
  engine     = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  
  db_name  = "ai_agent"
  username = "ai_agent_user"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot = true
}

# S3 Bucket
resource "aws_s3_bucket" "ai_agent_storage" {
  bucket = "ai-agent-storage-${random_id.bucket_suffix.hex}"
}
```

### 3. Google Cloud Platform

**Cloud Run Deployment:**
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ai-agent', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ai-agent']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'ai-agent'
      - '--image'
      - 'gcr.io/$PROJECT_ID/ai-agent'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
```

### 4. Azure Container Instances

**Azure Deployment:**
```bash
# Create resource group
az group create --name ai-agent-rg --location eastus

# Deploy container
az container create \
  --resource-group ai-agent-rg \
  --name ai-agent \
  --image your-registry/ai-agent:latest \
  --ports 9000 \
  --environment-variables \
    DATABASE_URL="postgresql://..." \
    REDIS_URL="redis://..."
```

---

## 🗄️ **Database Setup**

### PostgreSQL (Production)
```sql
-- Create database and user
CREATE DATABASE ai_agent;
CREATE USER ai_agent_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_agent TO ai_agent_user;

-- Connect to ai_agent database
\c ai_agent;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Run migrations
-- This will be done automatically by the application
```

### Supabase Setup
```bash
# 1. Create Supabase project at https://supabase.com
# 2. Get connection string from Settings > Database
# 3. Create storage bucket
python setup_supabase_storage.py

# 4. Set up Row Level Security policies
python setup_supabase_policies.py
```

### Database Migrations
```bash
# Run migrations
python scripts/migration/run_migrations.py upgrade

# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Rollback migration
python scripts/migration/run_migrations.py rollback
```

---

## 🪣 **Storage Backend Setup**

### Supabase Storage
```bash
# Setup script
python setup_supabase_storage.py

# Test connection
python test_supabase_simple.py

# Configure bucket policies
python setup_supabase_bucket.py
```

### AWS S3 Setup
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Create S3 bucket
aws s3 mb s3://ai-agent-storage

# Set bucket policy
aws s3api put-bucket-policy --bucket ai-agent-storage --policy file://s3-policy.json

# Test connection
python test_s3_connection.py
```

### MinIO Setup (Self-Hosted)
```bash
# Install MinIO
python setup_minio.py

# Start MinIO server
minio server /data --console-address ":9001"

# Configure bucket
python setup_minio_bucket.py
```

---

## 📊 **Monitoring Setup**

### Sentry (Error Tracking)
```bash
# 1. Create Sentry project at https://sentry.io
# 2. Get DSN from project settings
# 3. Add to .env file
SENTRY_DSN=https://your-dsn@sentry.io/project-id

# 4. Test integration
python test_sentry_integration.py
```

### PostHog (Analytics)
```bash
# 1. Create PostHog project at https://posthog.com
# 2. Get API key from project settings
# 3. Add to .env file
POSTHOG_API_KEY=phc_your_api_key
POSTHOG_HOST=https://us.posthog.com

# 4. Test integration
python test_posthog_integration.py
```

### System Monitoring
```bash
# Install monitoring tools
pip install psutil prometheus-client

# Start metrics endpoint
# Metrics available at /metrics/performance

# Set up Grafana dashboard (optional)
docker run -d -p 3000:3000 grafana/grafana
```

---

## 🔒 **Security Configuration**

### SSL/TLS Setup
```bash
# Generate SSL certificate (Let's Encrypt)
certbot certonly --standalone -d yourdomain.com

# Configure Nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Configuration
```bash
# UFW (Ubuntu)
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable

# Block direct access to application port
ufw deny 9000
```

### Environment Security
```bash
# Secure .env file
chmod 600 .env
chown app:app .env

# Use secrets management (production)
# AWS Secrets Manager, Azure Key Vault, etc.
```

---

## 🧪 **Testing & Validation**

### Pre-Deployment Testing
```bash
# Run all tests
python scripts/test_coverage.py

# Load testing
python scripts/run_load_tests.py

# Security testing
bandit -r app/ core/
safety check

# Integration testing
python test_all_endpoints.py
```

### Post-Deployment Validation
```bash
# Health check
curl https://yourdomain.com/health

# API functionality
python test_production_endpoints.py

# Load testing against production
locust -f tests/load_testing/locust_load_test.py --host=https://yourdomain.com
```

---

## 📈 **Performance Optimization**

### Application Optimization
```python
# Enable async processing
ENABLE_ASYNC_PROCESSING=true

# Configure connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Enable caching
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=3600
```

### Infrastructure Optimization
```bash
# Enable gzip compression (Nginx)
gzip on;
gzip_types text/plain application/json application/javascript text/css;

# Configure CDN (CloudFront/Cloudflare)
# Set up proper caching headers

# Database optimization
# Configure connection pooling
# Set up read replicas for scaling
```

---

## 🔄 **CI/CD Pipeline**

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python scripts/test_coverage.py
      - name: Security scan
        run: bandit -r app/ core/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        uses: render-deploy-action@v1
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

---

## 🚨 **Troubleshooting**

### Common Issues

#### Database Connection Issues
```bash
# Test database connection
python -c "from core.database import DatabaseManager; print(DatabaseManager().test_connection())"

# Check connection string
echo $DATABASE_URL

# Verify network connectivity
telnet your-db-host 5432
```

#### Storage Issues
```bash
# Test storage backend
python test_storage_backends.py

# Check permissions
python test_storage_permissions.py

# Verify configuration
python debug_storage_config.py
```

#### Performance Issues
```bash
# Check system resources
python monitor_performance.py

# Analyze slow queries
python analyze_slow_queries.py

# Monitor memory usage
python memory_profiler.py
```

### Debug Commands
```bash
# Server startup debugging
python debug_server_startup.py

# Route debugging
curl http://localhost:9000/debug-routes

# Authentication debugging
curl -H "Authorization: Bearer token" http://localhost:9000/debug-auth

# Storage debugging
python debug_storage_backends.py
```

---

## 📋 **Deployment Checklist**

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Storage backend configured and tested
- [ ] SSL certificates installed
- [ ] Monitoring services configured
- [ ] Security scanning completed
- [ ] Load testing passed
- [ ] Backup strategy implemented

### Post-Deployment
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] File uploads working
- [ ] Authentication functioning
- [ ] Monitoring alerts configured
- [ ] Performance metrics baseline established
- [ ] Documentation updated
- [ ] Team notified

---

## 🆘 **Support & Maintenance**

### Regular Maintenance Tasks
```bash
# Weekly
python scripts/maintenance/cleanup_old_files.py
python scripts/maintenance/rotate_logs.py
python scripts/maintenance/update_dependencies.py

# Monthly
python scripts/maintenance/database_maintenance.py
python scripts/maintenance/security_audit.py
python scripts/maintenance/performance_review.py
```

### Monitoring & Alerts
- Set up alerts for error rates > 1%
- Monitor response times > 500ms
- Track storage usage > 80%
- Alert on failed deployments
- Monitor SSL certificate expiry

### Backup Strategy
```bash
# Database backups
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# File storage backups
aws s3 sync s3://ai-agent-storage s3://ai-agent-backups/$(date +%Y%m%d)/

# Configuration backups
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

---

**Last Updated**: 2025-01-02  
**Deployment Options**: 4+ (Render, AWS, GCP, Azure)  
**Storage Backends**: 4 (Supabase, S3, MinIO, Local)  
**Monitoring**: Sentry + PostHog + System Metrics
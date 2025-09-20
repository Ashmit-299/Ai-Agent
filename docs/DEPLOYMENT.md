# Deployment Guide

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd Ai-Agent
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start API server
python start_server.py
# API: http://127.0.0.1:8000/docs

# 4. Launch Analytics Dashboard
python start_dashboard.py
# Dashboard: http://localhost:8501
```

## Production Deployment

### Render.com
Use the included `docker/render.yaml` configuration for one-click deployment.

### Environment Variables
Copy `.env.example` to `.env` and configure:
- Database URL
- JWT Secret
- LLM API Keys
- Storage backend

## Monitoring
- Logs: `GET /logs?admin_key=logs_2025`
- Metrics: `GET /metrics`
- Analytics: `GET /bhiv/analytics`
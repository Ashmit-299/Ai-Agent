# AI-Agent: Modular Video Generation Platform

[![CI/CD Status](https://github.com/Ashmit-299/Ai-Agent/actions/workflows/ci-cd-production.yml/badge.svg)](https://github.com/Ashmit-299/Ai-Agent/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenAPI Docs](https://img.shields.io/badge/api-docs-brightgreen)](http://localhost:8000/docs)

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

- Modular FastAPI backend with clean 9-step AI workflow (script, storyboard, video, feedback, etc.)
- JWT authentication (refresh tokens, brute-force lockout)
- DB schema migrations powered by Alembic + SQLModel (PostgreSQL/Supabase/SQLite)
- Modern video generation pipeline with MoviePy
- RL-agent and analytics feedback loops
- Full CI/CD (GitHub Actions, Docker support, auto-migration)
- Observability: Sentry error tracking, PostHog user analytics, system dashboards
- REST/async API with auto docs (Swagger/OpenAPI)

---

## Live Demo & Dashboards

- **Production Backend API:** [https://ai-agent-aff6.onrender.com](https://ai-agent-aff6.onrender.com)
- **API Docs (Swagger/OpenAPI):** [https://ai-agent-aff6.onrender.com/docs](https://ai-agent-aff6.onrender.com/docs)
- **AI Agent Dashboard:** [https://ai-agent-aff6.onrender.com/dashboard](https://ai-agent-aff6.onrender.com/dashboard)
- **Detailed Health & Metrics:** [https://ai-agent-aff6.onrender.com/health/detailed](https://ai-agent-aff6.onrender.com/health/detailed)
- **Sentry Monitoring:** [https://blackhole-ig.sentry.io/insights/projects/python/](https://blackhole-ig.sentry.io/insights/projects/python/)
- **PostHog Analytics:** [https://us.posthog.com/project/222470](https://us.posthog.com/project/222470)

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

ai-agent/
├── app/ # FastAPI API, routes, models, security, main app
├── core/ # Core logic: DB, orchestration, RL, storage
├── video/ # Pipelines: storyboard, generation, error cases
├── scripts/ # Deploy, migration, health check/util scripts
├── docker/ # Docker Compose, Dockerfiles
├── migrations/ # Alembic migrations
├── tests/ # pytest: unit & integration
├── .github/ # CI/CD workflows
├── docs/ # Top-level technical docs and diagrams
├── requirements.txt
├── README.md
├── .env.example

text

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
git clone https://github.com/your-username/Ai-Agent-main.git
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

# 7. Start Streamlit dashboard (optional)
python start_dashboard.py
```

#### Docker Deployment
```bash
# Quick start with Docker
docker-compose up -d

# Or build manually
docker build -t ai-agent .
docker run -p 8000:8000 ai-agent

## Running Locally

To start the API server (auto reload for dev):
uvicorn app.main:app --reload

Access docs:
http://localhost:8000/docs

(If dashboard is enabled)
http://localhost:8000/dashboard

text

---

## Environment Configuration

Put all secrets and config in `.env`:

DATABASE_URL=postgresql://postgres:<password>@<host>:5432/ai_agent
JWT_SECRET_KEY=<your-very-secure-jwt-key>
SENTRY_DSN=https://blackhole-ig.sentry.io/xxx # use actual project DSN
POSTHOG_API_KEY=phc_...
POSTHOG_HOST=https://us.posthog.com
ENVIRONMENT=development

text

---

## Database & Migrations

Apply migrations (any environment):

python run_migrations.py upgrade

text

- Create DB schema (dev only):  
  `python -c "from core.database import create_db_and_tables; create_db_and_tables()"`
- Rollback (optional):  
  `python run_migrations.py rollback <revision>`

---

## Testing & Quality

pytest # all tests
pytest tests/unit/
pytest tests/integration/

text

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

- **Errors:** [View in Sentry](https://blackhole-ig.sentry.io/insights/projects/python/)
- **User Analytics:** [View in PostHog](https://us.posthog.com/project/222470)
- **Health:**  
  [https://ai-agent-aff6.onrender.com/health/detailed](https://ai-agent-aff6.onrender.com/health/detailed)
- **API Metrics:**  
  [https://ai-agent-aff6.onrender.com/metrics](https://ai-agent-aff6.onrender.com/metrics)

Sentry DSN and PostHog API key must be set in `.env` before running in production.

---

## Security Practices

- JWT & refresh tokens, secure password hashing (bcrypt)
- Input validation, rate limiting, lockout on brute force
- CORS and secure-headers middleware enabled
- Production secrets never checked into repo—use `.env` config
- Security checks (Trivy, Bandit) run in CI

---

## API Reference

- **Swagger/OpenAPI:** [https://ai-agent-aff6.onrender.com/docs](https://ai-agent-aff6.onrender.com/docs)
- **Redoc:** [https://ai-agent-aff6.onrender.com/redoc](https://ai-agent-aff6.onrender.com/redoc)
- **API Endpoints:** well-grouped and documented/finder in `/docs/` and auto-generated docs

---

## Contributing

Pull Requests are welcome!

- All new code must pass tests, linter, and security pipelines.
- Please add or update documentation and your tests.
- See `CONTRIBUTING.md` for style/contribution guidelines.

---

**Project by [Ashmit Pandey](https://github.com/Ashmit-299) and contributors.**

> _For questions, please open an issue or contact via GitHub. Last updated: 2025-09-25_
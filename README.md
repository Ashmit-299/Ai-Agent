# AI Content Uploader Agent with Reinforcement Learning

A production-grade FastAPI application implementing Q-Learning reinforcement learning for intelligent content analysis and recommendation.

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd Ai-Advance-Task-with-RL-main
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

## Admin Access

**Logs Access**: `GET /logs?admin_key=logs_2025`

## Features

- **Q-Learning Agent**: Adaptive content recommendation
- **Video Generation**: Text-to-video synthesis
- **Real-time Analytics**: Streamlit dashboard
- **Enterprise Security**: JWT auth, rate limiting
- **Multi-modal Content**: Video, audio, text, PDF support
- **HTTP Streaming**: Range request video delivery

## Key Endpoints

- `POST /upload` - Upload content
- `POST /generate-video` - Create video from script
- `POST /feedback` - Train AI with user feedback
- `GET /metrics` - System analytics
- `GET /bhiv/analytics` - Advanced analytics
- `GET /logs` - Admin logs (requires key)

## Architecture

- **FastAPI** backend with SQLite
- **Q-Learning** for tag recommendations
- **LLM Integration** (Ollama/Perplexity)
- **Streamlit** analytics dashboard
- **MoviePy** video generation
- **JWT** authentication

For detailed documentation, see [docs/README.md](docs/README.md)
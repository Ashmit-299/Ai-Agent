# 🚀 Quick Setup Guide

## Problem: Missing Files After Git Clone

Some files are excluded from git (in `.gitignore`) and need to be created locally:
- `bucket/` directories
- `agent_state.json`
- `.env` file
- Database files

## Solution: Run Setup Script

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run setup (creates missing files/directories)
python setup_project.py

# 3. Start server
python start_server.py
```

## Alternative: One Command Setup

```bash
# Setup and start server in one command
python run_with_setup.py
```

## Test Dashboard

```bash
# Test dashboard (will pass in CI, requires server locally)
python test_dashboard.py
```

## Files Created by Setup

- `bucket/` - Storage directories
- `agent_state.json` - RL agent state
- `.env` - Environment variables
- `data.db` - SQLite database
- Various log directories

## CI/CD Notes

The `test_dashboard.py` script automatically detects CI environments and only tests imports, not API connectivity.
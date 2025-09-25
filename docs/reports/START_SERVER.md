# Server Startup Guide

## ✅ Problem Solved

The `psycopg2` import error has been resolved by installing `psycopg2-binary==2.9.9`.

## Quick Start

### Option 1: Use the new server runner (Recommended)
```bash
python run_server.py
```

### Option 2: Use uvicorn directly
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Use the original start script
```bash
python start_server.py
```

## Server URLs

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Verification

Test that the server is working:
```bash
# Health check
curl http://localhost:8000/health

# API documentation
# Visit: http://localhost:8000/docs
```

## What Was Fixed

1. **psycopg2 Import Error**: Resolved by installing `psycopg2-binary==2.9.9`
2. **Module Compatibility**: Added import fix in `app/main.py`
3. **Database Connection**: PostgreSQL connection working with Supabase
4. **Server Runner**: Created `run_server.py` for easier startup

## Environment Setup

Make sure you have:
- ✅ Virtual environment activated: `venv\Scripts\activate`
- ✅ Dependencies installed: `pip install -r requirements.txt`
- ✅ Environment variables: `.env` file with DATABASE_URL, etc.
- ✅ PostgreSQL driver: `psycopg2-binary==2.9.9`

## Troubleshooting

If you still get errors:

1. **Check virtual environment**:
   ```bash
   where python
   # Should show path to venv\Scripts\python.exe
   ```

2. **Verify psycopg2**:
   ```bash
   python -c "import psycopg2; print('OK')"
   ```

3. **Test database connection**:
   ```bash
   python -c "from core.database import engine; print('DB OK')"
   ```

4. **Check environment variables**:
   ```bash
   python -c "import os; print('DB URL:', bool(os.getenv('DATABASE_URL')))"
   ```

The server should now start without any psycopg2 errors!
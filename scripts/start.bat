@echo off
echo AI Content Uploader Agent - Starting Server
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if psycopg2 is available
python -c "import psycopg2; print('psycopg2 OK')" 2>nul
if errorlevel 1 (
    echo Installing psycopg2-binary...
    pip install psycopg2-binary==2.9.9
)

REM Create directories
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "bucket\tmp" mkdir bucket\tmp

REM Start server
echo Starting server on http://localhost:8000
echo API docs: http://localhost:8000/docs
echo Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
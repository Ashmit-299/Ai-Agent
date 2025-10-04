@echo off
REM Production migration script for Windows with safety checks

echo 🚀 AI Agent Database Migration Script
echo ======================================

REM Check if DATABASE_URL is set
if "%DATABASE_URL%"=="" (
    echo ❌ ERROR: DATABASE_URL environment variable is not set
    exit /b 1
)

REM Check if we're in production
echo %DATABASE_URL% | findstr "postgresql" >nul
if %errorlevel%==0 (
    echo 📊 Production PostgreSQL database detected
    echo 🔒 Running in production mode with safety checks
    
    REM Backup before migration (for PostgreSQL)
    echo 💾 Creating backup before migration...
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
    set BACKUP_FILE=backup_%mydate%_%mytime%.sql
    
    REM Try to create backup
    pg_dump "%DATABASE_URL%" > "%BACKUP_FILE%" 2>nul
    if %errorlevel%==0 (
        echo ✅ Backup created: %BACKUP_FILE%
    ) else (
        echo ⚠️  Backup failed, but continuing with migration...
    )
) else (
    echo 🧪 Development SQLite database detected
)

REM Run migrations
echo ⬆️  Running database migrations...
python run_migrations.py upgrade

if %errorlevel%==0 (
    echo ✅ Database migration completed successfully!
    
    REM Verify migration
    echo 🔍 Verifying database state...
    python -c "import sys; sys.path.append('.'); from core.models import engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT 1')); print('✅ Database verification successful'); conn.close()"
    
    echo 🎉 Migration process completed!
) else (
    echo ❌ Migration failed!
    
    if exist "%BACKUP_FILE%" (
        echo 🔄 To rollback, you can restore from backup:
        echo    psql %%DATABASE_URL%% ^< %BACKUP_FILE%
    )
    
    exit /b 1
)
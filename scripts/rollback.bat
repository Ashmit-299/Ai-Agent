@echo off
REM Windows batch version of rollback system

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production

set ROLLBACK_TARGET=%2
if "%ROLLBACK_TARGET%"=="" set ROLLBACK_TARGET=previous

echo 🔄 Initiating rollback for %ENVIRONMENT% environment

REM Function to get previous version
:get_previous_version
for /f "tokens=*" %%i in ('git describe --tags --abbrev=0 HEAD~1 2^>nul') do set PREVIOUS_VERSION=%%i
if "%PREVIOUS_VERSION%"=="" (
    for /f "tokens=*" %%i in ('git rev-parse HEAD~1 2^>nul') do set PREVIOUS_VERSION=%%i
    if not "%PREVIOUS_VERSION%"=="" set PREVIOUS_VERSION=!PREVIOUS_VERSION:~0,8!
)
if "%PREVIOUS_VERSION%"=="" set PREVIOUS_VERSION=latest
goto :eof

REM Function to backup current state
:backup_current_state
echo 💾 Creating backup of current state...

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set BACKUP_DIR=backups\%timestamp%
mkdir %BACKUP_DIR% 2>nul

REM Backup logs if they exist
if exist logs (
    xcopy logs %BACKUP_DIR%\logs\ /E /I /Q >nul 2>&1
)

REM Store current version
for /f "tokens=*" %%i in ('git rev-parse HEAD 2^>nul') do echo %%i > %BACKUP_DIR%\current_version.txt

echo ✅ Backup created in %BACKUP_DIR%
goto :eof

REM Function to perform rollback
:perform_rollback
set target_version=%1
echo 🔄 Rolling back to version: %target_version%

if "%ENVIRONMENT%"=="production" (
    call :rollback_production %target_version%
) else if "%ENVIRONMENT%"=="staging" (
    call :rollback_staging %target_version%
) else (
    echo ❌ Rollback not configured for environment: %ENVIRONMENT%
    exit /b 1
)
goto :eof

REM Function to rollback production
:rollback_production
set version=%1
echo 🏭 Rolling back production deployment...

if not "%RENDER_API_KEY%"=="" if not "%RENDER_PRODUCTION_SERVICE_ID%"=="" (
    curl -X POST "https://api.render.com/v1/services/%RENDER_PRODUCTION_SERVICE_ID%/deploys" ^
        -H "Authorization: Bearer %RENDER_API_KEY%" ^
        -H "Content-Type: application/json" ^
        -d "{\"imageUrl\": \"ashmitpandey299/ai-uploader-agent:%version%\", \"clearCache\": \"clear\"}"
)
goto :eof

REM Function to rollback staging
:rollback_staging
set version=%1
echo 🧪 Rolling back staging deployment...

if not "%RENDER_API_KEY%"=="" if not "%RENDER_STAGING_SERVICE_ID%"=="" (
    curl -X POST "https://api.render.com/v1/services/%RENDER_STAGING_SERVICE_ID%/deploys" ^
        -H "Authorization: Bearer %RENDER_API_KEY%" ^
        -H "Content-Type: application/json" ^
        -d "{\"imageUrl\": \"ashmitpandey299/ai-uploader-agent:%version%\", \"clearCache\": \"clear\"}"
)
goto :eof

REM Function to verify rollback
:verify_rollback
set api_url=%1
echo 🔍 Verifying rollback...

timeout /t 60 /nobreak >nul

for /l %%i in (1,1,5) do (
    curl -f "%api_url%/health" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Health check passed (attempt %%i)
        goto :verify_success
    ) else (
        echo ⚠️ Health check failed (attempt %%i), retrying...
        timeout /t 30 /nobreak >nul
    )
)

echo ❌ Rollback verification failed!
exit /b 1

:verify_success
curl -f "%api_url%/docs" >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ API docs not accessible after rollback
    exit /b 1
)

echo ✅ Rollback verification successful
goto :eof

REM Main execution
echo 🚨 ROLLBACK INITIATED 🚨
echo Environment: %ENVIRONMENT%
echo Target: %ROLLBACK_TARGET%

if "%ROLLBACK_TARGET%"=="previous" (
    call :get_previous_version
    set TARGET_VERSION=!PREVIOUS_VERSION!
) else (
    set TARGET_VERSION=%ROLLBACK_TARGET%
)

if "%TARGET_VERSION%"=="" (
    echo ❌ Could not determine target version for rollback
    exit /b 1
)

echo Target version: %TARGET_VERSION%

set /p CONFIRM="⚠️ Are you sure you want to rollback to %TARGET_VERSION%? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo ❌ Rollback cancelled
    exit /b 1
)

call :backup_current_state
call :perform_rollback %TARGET_VERSION%

if "%ENVIRONMENT%"=="production" (
    set API_URL=https://ai-agent-aff6.onrender.com
) else (
    set API_URL=https://staging-ai-agent.onrender.com
)

call :verify_rollback %API_URL%
if !errorlevel! equ 0 (
    echo 🎉 Rollback completed successfully!
) else (
    echo ❌ Rollback verification failed!
    exit /b 1
)
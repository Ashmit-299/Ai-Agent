@echo off
REM Windows batch version of deploy-config.sh

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development

set CONFIG_DIR=config
set ACTION=%2
if "%ACTION%"=="" set ACTION=generate

echo 🔧 Setting up configuration for environment: %ENVIRONMENT%

REM Create config directory if it doesn't exist
if not exist %CONFIG_DIR% mkdir %CONFIG_DIR%

if "%ACTION%"=="generate" goto :generate
if "%ACTION%"=="apply" goto :apply
if "%ACTION%"=="validate" goto :validate
goto :usage

:generate
echo 📝 Generating config for %ENVIRONMENT% environment...

if "%ENVIRONMENT%"=="development" (
    (
        echo # Development Environment Configuration
        echo ENVIRONMENT=development
        echo DEBUG=true
        echo DATABASE_URL=sqlite:///./data.db
        echo JWT_SECRET_KEY=dev-secret-key-change-in-production
        echo SENTRY_DSN=
        echo POSTHOG_API_KEY=
        echo ENABLE_PERFORMANCE_MONITORING=true
        echo ENABLE_USER_ANALYTICS=false
        echo LOG_LEVEL=DEBUG
    ) > %CONFIG_DIR%\%ENVIRONMENT%.env
) else if "%ENVIRONMENT%"=="staging" (
    (
        echo # Staging Environment Configuration
        echo ENVIRONMENT=staging
        echo DEBUG=false
        echo DATABASE_URL=${STAGING_DATABASE_URL}
        echo JWT_SECRET_KEY=${STAGING_JWT_SECRET_KEY}
        echo SENTRY_DSN=${STAGING_SENTRY_DSN}
        echo POSTHOG_API_KEY=${STAGING_POSTHOG_API_KEY}
        echo ENABLE_PERFORMANCE_MONITORING=true
        echo ENABLE_USER_ANALYTICS=true
        echo LOG_LEVEL=INFO
    ) > %CONFIG_DIR%\%ENVIRONMENT%.env
) else if "%ENVIRONMENT%"=="production" (
    (
        echo # Production Environment Configuration
        echo ENVIRONMENT=production
        echo DEBUG=false
        echo DATABASE_URL=${PRODUCTION_DATABASE_URL}
        echo JWT_SECRET_KEY=${PRODUCTION_JWT_SECRET_KEY}
        echo SENTRY_DSN=${PRODUCTION_SENTRY_DSN}
        echo POSTHOG_API_KEY=${PRODUCTION_POSTHOG_API_KEY}
        echo ENABLE_PERFORMANCE_MONITORING=true
        echo ENABLE_USER_ANALYTICS=true
        echo LOG_LEVEL=WARNING
        echo SECURE_COOKIES=true
        echo HTTPS_ONLY=true
        echo HSTS_MAX_AGE=31536000
    ) > %CONFIG_DIR%\%ENVIRONMENT%.env
) else (
    echo ❌ Unknown environment: %ENVIRONMENT%
    exit /b 1
)

echo ✅ Config generated: %CONFIG_DIR%\%ENVIRONMENT%.env
goto :validate

:apply
set CONFIG_FILE=%CONFIG_DIR%\%ENVIRONMENT%.env
if exist %CONFIG_FILE% (
    echo 📋 Applying configuration from %CONFIG_FILE%
    copy %CONFIG_FILE% .env
    echo ✅ Configuration applied
) else (
    echo ❌ Configuration file not found: %CONFIG_FILE%
    exit /b 1
)
goto :end

:validate
set CONFIG_FILE=%CONFIG_DIR%\%ENVIRONMENT%.env
echo 🔍 Validating configuration for %ENVIRONMENT%...

findstr /B "ENVIRONMENT=" %CONFIG_FILE% >nul || (echo ❌ Missing ENVIRONMENT && exit /b 1)
findstr /B "DATABASE_URL=" %CONFIG_FILE% >nul || (echo ❌ Missing DATABASE_URL && exit /b 1)
findstr /B "JWT_SECRET_KEY=" %CONFIG_FILE% >nul || (echo ❌ Missing JWT_SECRET_KEY && exit /b 1)

echo ✅ Configuration validation passed
goto :end

:usage
echo Usage: %0 ^<environment^> ^<action^>
echo Environments: development, staging, production
echo Actions: generate, apply, validate
exit /b 1

:end
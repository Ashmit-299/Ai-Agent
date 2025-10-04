# Render Deployment Guide

## Fixed Python Version Issue

The deployment error was caused by inconsistent Python version specifications. Fixed by:

1. **Updated `runtime.txt`** to `python-3.11.0`
2. **Updated `docker/render.yaml`** runtime to `python-3.11.0`  
3. **Created `.python-version`** file with `3.11.0`

## Deployment Steps

1. **Push changes to your repository**
2. **In Render Dashboard:**
   - Go to your service settings
   - Clear build cache if needed
   - Redeploy

## Key Files for Render:
- `runtime.txt` - Python version specification
- `requirements.txt` - Dependencies
- `docker/render.yaml` - Service configuration
- `docker/Procfile` - Process commands

## Environment Variables Required:
- `DATABASE_URL` - PostgreSQL connection
- `JWT_SECRET_KEY` - Authentication secret
- `PERPLEXITY_API_KEY` - AI service key
- `SENTRY_DSN` - Error monitoring
- `POSTHOG_API_KEY` - Analytics

## Troubleshooting:
- If still getting Python version errors, clear Render's build cache
- Ensure all config files use `python-3.11.0` format
- Check Render's supported Python versions: https://render.com/docs/python-version
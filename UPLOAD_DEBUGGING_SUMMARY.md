# Upload Route Debugging Summary

## Issues Identified and Fixed

### 1. Route Conflicts
- **Problem**: Multiple routers with overlapping routes causing conflicts
- **Solution**: Added debug logging to identify route conflicts in `main.py`
- **Debug endpoint**: `GET /debug-routes` to enumerate all routes

### 2. Upload Endpoint Issues
- **Problem**: Undefined variables in upload route (`temp_path`, `bucket_path`, `safe_path`)
- **Solution**: Fixed variable references in `routes.py` upload endpoint
- **Enhanced**: Added debug logging to CDN upload endpoint in `cdn_fixed.py`

### 3. Authentication Flow
- **Problem**: Upload endpoints require authentication but token validation may fail
- **Solution**: Enhanced debug logging for authentication in upload endpoints
- **Debug endpoint**: `GET /debug-auth` to test authentication status

## Debug Tools Added

### 1. Route Debugging (`/debug-routes`)
```bash
curl http://localhost:9000/debug-routes
```
- Lists all available routes
- Identifies upload-related routes
- Shows route conflicts

### 2. Upload Route Testing (`test_upload_routes.py`)
```bash
python test_upload_routes.py
```
- Tests demo login flow
- Tests CDN upload URL generation
- Tests both CDN and main upload endpoints
- Provides detailed error reporting

### 3. Server Startup Debugging (`debug_server_startup.py`)
```bash
python debug_server_startup.py
```
- Checks import dependencies
- Identifies router conflicts
- Validates route registration

### 4. Enhanced CDN Upload Logging
- Added detailed debug logging to CDN upload endpoint
- Logs file details, authentication status, and processing steps
- Helps identify where upload process fails

## Router Organization

### Main Routers (in order of inclusion):
1. `router` - Default endpoints (/, /health, /test)
2. `step1_router` - System Health & Demo Access
3. `auth_router` - User Authentication (if available)
4. `step3_router` - Content Upload & Video Generation (**Main upload: POST /upload**)
5. `step4_router` - Content Access & Streaming
6. `step5_router` - AI Feedback & Tag Recommendations
7. `step6_router` - Analytics & Performance Monitoring
8. `step7_router` - Task Queue Management
9. `step8_router` - System Maintenance & Operations
10. `step9_router` - User Interface & Dashboard
11. `cdn_router` - CDN & Pre-signed URLs (**CDN upload: POST /cdn/upload/{token}**)

### Upload Endpoints:
- **Main Upload**: `POST /upload` (in step3_router)
- **CDN Upload**: `POST /cdn/upload/{token}` (in cdn_router with /cdn prefix)
- **CDN Upload URL**: `GET /cdn/upload-url` (generates upload token)

## Debugging Steps

### 1. Check Server Status
```bash
curl http://localhost:9000/health
```

### 2. Check Routes
```bash
curl http://localhost:9000/debug-routes
```

### 3. Test Authentication
```bash
# Get demo credentials
curl http://localhost:9000/demo-login

# Login with credentials
curl -X POST http://localhost:9000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'

# Test auth status
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:9000/debug-auth
```

### 4. Test Upload Flow
```bash
# Run comprehensive test
python test_upload_routes.py
```

## Common Issues and Solutions

### Issue: "Route not found"
- **Check**: Route enumeration with `/debug-routes`
- **Solution**: Verify router inclusion order in `main.py`

### Issue: "Authentication failed"
- **Check**: Token validity with `/debug-auth`
- **Solution**: Get fresh token from `/users/login`

### Issue: "Upload token invalid"
- **Check**: CDN upload token generation with `/cdn/upload-url`
- **Solution**: Ensure token is used immediately after generation

### Issue: "File upload fails"
- **Check**: Server logs for detailed error messages
- **Solution**: Verify file type, size, and authentication

## Next Steps

1. **Run debug script**: `python debug_server_startup.py`
2. **Start server**: `python scripts/start_server.py`
3. **Test routes**: `python test_upload_routes.py`
4. **Check logs**: Look for DEBUG messages in console output
5. **Use debug endpoints**: `/debug-routes`, `/debug-auth` for troubleshooting

## Files Modified

- `app/main.py` - Added route debugging and conflict detection
- `app/routes.py` - Fixed undefined variables in upload endpoint
- `app/cdn_fixed.py` - Enhanced debug logging for CDN upload
- `test_upload_routes.py` - Comprehensive upload testing script
- `debug_server_startup.py` - Server startup debugging tool

The debugging tools should help identify exactly where the upload route conflicts are occurring and provide detailed information about the routing setup.
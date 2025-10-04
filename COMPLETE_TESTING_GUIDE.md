# Complete Testing Guide - AI Agent Platform

**Updated:** 2025-01-02  
**All Localhost Endpoints for Comprehensive Testing**

## 🚀 **Quick Start Testing**

### **Start the Server**
```bash
# Start main server on port 9000
python scripts/start_server.py

# Or start manually
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

### **Verify Server is Running**
```bash
curl http://localhost:9000/health
```

---

## 🏠 **Complete Localhost Endpoints (Port 9000)**

### **🏠 Core System Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| Main API | [http://localhost:9000](http://localhost:9000) | Root API endpoint |
| API Documentation | [http://localhost:9000/docs](http://localhost:9000/docs) | Swagger UI documentation |
| OpenAPI Schema | [http://localhost:9000/openapi.json](http://localhost:9000/openapi.json) | OpenAPI JSON schema |
| Health Check | [http://localhost:9000/health](http://localhost:9000/health) | Basic health status |
| Detailed Health | [http://localhost:9000/health/detailed](http://localhost:9000/health/detailed) | Comprehensive health check |

### **🔍 Debug & Testing Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| Debug Routes | [http://localhost:9000/debug-routes](http://localhost:9000/debug-routes) | List all available routes |
| Auth Debug | [http://localhost:9000/debug-auth](http://localhost:9000/debug-auth) | Test authentication status |
| Demo Login | [http://localhost:9000/demo-login](http://localhost:9000/demo-login) | Get demo credentials |
| Test Server | [http://localhost:9000/test](http://localhost:9000/test) | Basic server functionality |
| Data Saving Test | [http://localhost:9000/test-data-saving](http://localhost:9000/test-data-saving) | Test data persistence |

### **🔐 Authentication Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| User Registration | [http://localhost:9000/users/register](http://localhost:9000/users/register) | Register new user |
| User Login | [http://localhost:9000/users/login](http://localhost:9000/users/login) | User authentication |
| User Profile | [http://localhost:9000/users/profile](http://localhost:9000/users/profile) | Get user profile |
| Refresh Token | [http://localhost:9000/users/refresh](http://localhost:9000/users/refresh) | Refresh JWT token |
| Supabase Auth Health | [http://localhost:9000/users/supabase-auth-health](http://localhost:9000/users/supabase-auth-health) | Supabase auth status |

### **📊 Metrics & Monitoring Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| Metrics Info | [http://localhost:9000/metrics](http://localhost:9000/metrics) | Available metrics endpoints |
| Prometheus Metrics | [http://localhost:9000/metrics/prometheus](http://localhost:9000/metrics/prometheus) | Prometheus format metrics |
| Performance Metrics | [http://localhost:9000/metrics/performance](http://localhost:9000/metrics/performance) | System performance data |
| Observability Health | [http://localhost:9000/observability/health](http://localhost:9000/observability/health) | Observability status |
| Monitoring Status | [http://localhost:9000/monitoring-status](http://localhost:9000/monitoring-status) | Monitoring system status |

### **📁 Content & Upload Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| Upload Content | [http://localhost:9000/upload](http://localhost:9000/upload) | Upload files |
| Generate Video | [http://localhost:9000/generate-video](http://localhost:9000/generate-video) | Create video from script |
| Browse Content | [http://localhost:9000/contents](http://localhost:9000/contents) | List all content |
| Content Details | [http://localhost:9000/content/{id}](http://localhost:9000/content/) | Get content by ID |
| Download Content | [http://localhost:9000/download/{id}](http://localhost:9000/download/) | Download file |
| Stream Content | [http://localhost:9000/stream/{id}](http://localhost:9000/stream/) | Stream video content |

### **🌐 CDN & File Management Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| CDN Upload URL | [http://localhost:9000/cdn/upload-url](http://localhost:9000/cdn/upload-url) | Get upload URL |
| CDN Upload | [http://localhost:9000/cdn/upload/{token}](http://localhost:9000/cdn/upload/) | Upload via CDN |
| CDN Download | [http://localhost:9000/cdn/download/{id}](http://localhost:9000/cdn/download/) | Download via CDN |
| CDN Stream | [http://localhost:9000/cdn/stream/{id}](http://localhost:9000/cdn/stream/) | Stream via CDN |
| CDN List Files | [http://localhost:9000/cdn/list](http://localhost:9000/cdn/list) | List user files |
| CDN File Info | [http://localhost:9000/cdn/info/{id}](http://localhost:9000/cdn/info/) | Get file information |

### **🤖 AI & Analytics Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| Submit Feedback | [http://localhost:9000/feedback](http://localhost:9000/feedback) | Submit content feedback |
| Tag Recommendations | [http://localhost:9000/recommend-tags/{id}](http://localhost:9000/recommend-tags/) | AI tag suggestions |
| Average Rating | [http://localhost:9000/average-rating/{id}](http://localhost:9000/average-rating/) | Content rating |
| RL Agent Stats | [http://localhost:9000/rl/agent-stats](http://localhost:9000/rl/agent-stats) | Q-Learning statistics |
| Analytics | [http://localhost:9000/bhiv/analytics](http://localhost:9000/bhiv/analytics) | Advanced analytics |

### **🔒 GDPR & Privacy Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| Privacy Policy | [http://localhost:9000/gdpr/privacy-policy](http://localhost:9000/gdpr/privacy-policy) | Privacy information |
| Export Data | [http://localhost:9000/gdpr/export-data](http://localhost:9000/gdpr/export-data) | Export user data |
| Delete Data | [http://localhost:9000/gdpr/delete-data](http://localhost:9000/gdpr/delete-data) | Delete user data |
| Data Summary | [http://localhost:9000/gdpr/data-summary](http://localhost:9000/gdpr/data-summary) | Data usage summary |

### **⚙️ System Management Endpoints**
| Endpoint | URL | Description |
|----------|-----|-------------|
| Task Status | [http://localhost:9000/tasks/{id}](http://localhost:9000/tasks/) | Background task status |
| Queue Stats | [http://localhost:9000/tasks/queue/stats](http://localhost:9000/tasks/queue/stats) | Task queue statistics |
| Storage Status | [http://localhost:9000/storage/status](http://localhost:9000/storage/status) | Storage system status |
| Bucket Stats | [http://localhost:9000/bucket/stats](http://localhost:9000/bucket/stats) | Storage statistics |
| Dashboard | [http://localhost:9000/dashboard](http://localhost:9000/dashboard) | System dashboard |

---

## 🧪 **Step-by-Step Testing Guide**

### **Step 1: Basic System Health**
```bash
# Test server health
curl http://localhost:9000/health

# Get detailed health information
curl http://localhost:9000/health/detailed

# Check all available routes
curl http://localhost:9000/debug-routes
```

### **Step 2: Authentication Testing**
```bash
# Get demo credentials
curl http://localhost:9000/demo-login

# Login with demo user
curl -X POST http://localhost:9000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo1234"

# Test authentication status
curl http://localhost:9000/debug-auth

# Test Supabase authentication health
curl http://localhost:9000/users/supabase-auth-health
```

### **Step 3: Metrics & Monitoring**
```bash
# Check available metrics endpoints
curl http://localhost:9000/metrics

# Get Prometheus metrics
curl http://localhost:9000/metrics/prometheus

# Check system performance
curl http://localhost:9000/metrics/performance

# Test observability system
curl http://localhost:9000/observability/health
```

### **Step 4: Content & Upload Testing**
```bash
# Get CDN upload URL
curl http://localhost:9000/cdn/upload-url

# Browse existing content
curl http://localhost:9000/contents

# Test analytics endpoint
curl http://localhost:9000/bhiv/analytics
```

### **Step 5: GDPR & Privacy**
```bash
# Check privacy policy
curl http://localhost:9000/gdpr/privacy-policy

# Test data summary (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:9000/gdpr/data-summary
```

---

## 🔧 **Automated Testing Scripts**

### **Integration Testing**
```bash
# Complete integration status check
python check_integrations.py

# Test live service connections
python test_live_connections.py

# Check monitoring endpoints
python check_monitoring_endpoints.py

# Server status and restart check
python test_server_restart.py
```

### **Authentication Testing**
```bash
# Test JWKS authentication integration
python test_jwks_integration.py

# Test all authentication endpoints
python test_auth_endpoints.py

# JWT token testing
python fix_auth_token.py

# Get demo authentication token
python get_token.py
```

### **Metrics & Monitoring Testing**
```bash
# Test Prometheus integration
python test_prometheus_integration.py

# Monitor system performance
python monitor_performance.py

# Check port status
python port_status.py

# Test all imports
python test_imports.py
```

### **Content & Upload Testing**
```bash
# Comprehensive upload route testing
python test_upload_routes.py

# CDN endpoint testing
python test_cdn_simple.py

# Server startup debugging
python debug_server_startup.py
```

### **GDPR & Privacy Testing**
```bash
# Test all GDPR endpoints
python test_gdpr_all.py

# Test data deletion functionality
python test_gdpr_delete.py

# Test data export features
python test_gdpr_endpoints.py
```

### **Load & Performance Testing**
```bash
# Run comprehensive load tests (100 users)
python scripts/run_load_tests.py

# Interactive Locust load testing
locust -f tests/load_testing/locust_load_test.py --host=http://localhost:9000

# Test coverage analysis
python scripts/test_coverage.py

# Rate limiting tests
pytest tests/test_rate_limiting.py
```

---

## 🎯 **Quick Test Commands**

### **Test Everything at Once**
```bash
python -c "import subprocess; [subprocess.run(['python', f]) for f in ['check_integrations.py', 'test_prometheus_integration.py', 'test_jwks_integration.py']]"
```

### **Health Check All Services**
```bash
curl -s http://localhost:9000/health && echo " - Health OK" && \
curl -s http://localhost:9000/metrics && echo " - Metrics OK" && \
curl -s http://localhost:9000/users/supabase-auth-health && echo " - Auth OK"
```

### **Generate Test Traffic for Metrics**
```bash
for i in {1..10}; do curl -s http://localhost:9000/health > /dev/null; done && \
echo "Traffic generated - check metrics at http://localhost:9000/metrics/prometheus"
```

### **Test Authentication Flow**
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:9000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo1234" | jq -r '.access_token')

# Test authenticated endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/users/profile
```

---

## 📊 **Monitoring & Dashboards**

### **Local Development Dashboards**
- **API Documentation:** [http://localhost:9000/docs](http://localhost:9000/docs)
- **Health Dashboard:** [http://localhost:9000/health/detailed](http://localhost:9000/health/detailed)
- **Prometheus Metrics:** [http://localhost:9000/metrics/prometheus](http://localhost:9000/metrics/prometheus)
- **Performance Dashboard:** [http://localhost:9000/metrics/performance](http://localhost:9000/metrics/performance)
- **System Dashboard:** [http://localhost:9000/dashboard](http://localhost:9000/dashboard)

### **Production Dashboards**
- **Sentry Error Tracking:** [https://blackhole-ig.sentry.io/insights/projects/python/](https://blackhole-ig.sentry.io/insights/projects/python/)
- **PostHog User Analytics:** [https://us.posthog.com/project/222470](https://us.posthog.com/project/222470)
- **Production API:** [https://ai-agent-aff6.onrender.com](https://ai-agent-aff6.onrender.com)
- **Production Health:** [https://ai-agent-aff6.onrender.com/health/detailed](https://ai-agent-aff6.onrender.com/health/detailed)

### **Optional Monitoring Setup**
```bash
# Set up Prometheus monitoring (requires Docker)
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Set up Grafana dashboards (requires Docker)
docker run -d -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana

# Access dashboards
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (admin/admin)"
```

---

## 🚨 **Troubleshooting**

### **Server Not Starting**
```bash
# Check if port 9000 is in use
netstat -an | findstr :9000

# Kill process on port 9000 (Windows)
for /f "tokens=5" %a in ('netstat -aon ^| findstr :9000') do taskkill /f /pid %a

# Start server with debug
python scripts/start_server.py --debug
```

### **Authentication Issues**
```bash
# Test authentication debug
curl http://localhost:9000/debug-auth

# Get fresh demo token
curl http://localhost:9000/demo-login

# Test token validity
python fix_auth_token.py
```

### **Metrics Not Available**
```bash
# Check Prometheus integration
python test_prometheus_integration.py

# Restart server to activate metrics
# Stop server (Ctrl+C) then:
python scripts/start_server.py
```

---

**Complete testing guide for AI Agent Platform - All 60+ endpoints ready for testing!**

*Last updated: 2025-01-02*
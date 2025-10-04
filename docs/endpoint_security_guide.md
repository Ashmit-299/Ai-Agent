# 🔒 Endpoint Security Control Guide

## 📍 **Primary Control Location: `app/main.py`**

### **Global Security Configuration (Lines 120-140)**

```python
def custom_openapi():
    # ... existing code ...
    
    # 🔒 GLOBAL SECURITY LOCK/UNLOCK
    # Comment out this line to UNLOCK all endpoints globally:
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # 🔓 To unlock specific endpoints, modify the routes individually
```

### **Per-Endpoint Security Control**

#### **Method 1: Router-Level Security (Recommended)**

**Location: `app/routes.py` - Each step router**

```python
# 🔒 LOCK endpoints by adding authentication dependency
@step3_router.post('/upload')
async def upload(current_user = Depends(get_current_user_required)):  # LOCKED
    # Endpoint requires authentication

# 🔓 UNLOCK endpoints by using optional authentication
@step3_router.get('/contents')
def list_contents(current_user = Depends(get_current_user)):  # UNLOCKED
    # Endpoint works without authentication
```

#### **Method 2: Individual Endpoint Security**

**Location: Any router file**

```python
# 🔒 LOCKED - Requires authentication
@router.post("/secure-endpoint", dependencies=[Depends(get_current_user_required)])
def secure_endpoint():
    pass

# 🔓 UNLOCKED - No authentication required
@router.get("/public-endpoint")
def public_endpoint():
    pass
```

## 📂 **Security Control Files**

### **1. Authentication Logic: `app/auth.py`**
- `get_current_user_required()` - Forces authentication
- `get_current_user_optional()` - Optional authentication
- `get_current_user()` - Backward compatibility

### **2. Security Middleware: `app/security.py`**
- `SecurityManager` class
- JWT token verification
- Rate limiting configuration

### **3. Route Definitions: `app/routes.py`**
- Individual endpoint security settings
- Step-by-step router configurations

## 🛠️ **Manual Lock/Unlock Methods**

### **Method A: Global Security Toggle**

**File: `app/main.py` (Line ~135)**

```python
# 🔒 LOCK ALL ENDPOINTS
openapi_schema["security"] = [{"BearerAuth": []}]

# 🔓 UNLOCK ALL ENDPOINTS  
# openapi_schema["security"] = []  # Comment out the line above
```

### **Method B: Per-Router Security**

**File: `app/routes.py`**

```python
# 🔒 LOCK specific router
step3_router = APIRouter(
    tags=["STEP 3: Content Upload & Video Generation"],
    dependencies=[Depends(get_current_user_required)]  # ADD THIS LINE
)

# 🔓 UNLOCK specific router
step3_router = APIRouter(
    tags=["STEP 3: Content Upload & Video Generation"]
    # Remove dependencies line
)
```

### **Method C: Individual Endpoint Control**

**File: `app/routes.py` - Modify specific endpoints**

```python
# 🔒 LOCK individual endpoint
@step3_router.post('/upload')
async def upload(current_user = Depends(get_current_user_required)):  # Change this
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

# 🔓 UNLOCK individual endpoint  
@step3_router.post('/upload')
async def upload(current_user = Depends(get_current_user)):  # Change to optional
    # Remove authentication check or make it optional
```

## 🎯 **Quick Security Toggles**

### **Unlock All Endpoints (Development Mode)**

1. **Edit `app/main.py`** (Line ~135):
```python
# Comment out this line:
# openapi_schema["security"] = [{"BearerAuth": []}]
```

2. **Edit `app/routes.py`** - Change all `get_current_user_required` to `get_current_user`

### **Lock All Endpoints (Production Mode)**

1. **Edit `app/main.py`** (Line ~135):
```python
# Ensure this line is active:
openapi_schema["security"] = [{"BearerAuth": []}]
```

2. **Edit `app/routes.py`** - Change all `get_current_user` to `get_current_user_required`

## 📋 **Current Endpoint Security Status**

### **🔓 UNLOCKED (Public Access)**
- `/health` - System health check
- `/demo-login` - Demo credentials
- `/contents` - Browse content (optional auth)
- `/content/{id}` - View content details
- `/stream/{id}` - Stream content
- `/metrics` - System metrics
- `/dashboard` - Web dashboard

### **🔒 LOCKED (Authentication Required)**
- `/upload` - File upload
- `/generate-video` - Video generation
- `/feedback` - Submit feedback
- `/users/register` - User registration
- `/users/login` - User login
- `/users/profile` - User profile
- `/bucket/cleanup` - Admin operations

## 🔧 **Security Configuration Files Summary**

| File | Purpose | Security Control |
|------|---------|------------------|
| `app/main.py` | Global OpenAPI security | Global lock/unlock |
| `app/auth.py` | Authentication logic | User verification |
| `app/security.py` | Security middleware | JWT, rate limiting |
| `app/routes.py` | Endpoint definitions | Per-endpoint control |

## ⚡ **Quick Commands**

### **Unlock All for Testing**
```bash
# Edit app/main.py line 135
# Comment out: openapi_schema["security"] = [{"BearerAuth": []}]
```

### **Lock All for Production**
```bash
# Edit app/main.py line 135  
# Ensure active: openapi_schema["security"] = [{"BearerAuth": []}]
```

### **Test Security Status**
```bash
curl http://localhost:8000/health  # Should work (unlocked)
curl http://localhost:8000/upload  # Should require auth (locked)
```
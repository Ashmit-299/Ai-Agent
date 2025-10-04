# 📁 Simplified CDN Endpoints Guide

## ✅ **Working CDN Endpoints - Easy to Use**

All CDN endpoints are now **simplified and working**. No complex configuration needed!

### **🔐 Authentication Required**
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## **📤 File Upload Workflow**

### **Step 1: Get Upload URL**
```http
GET /cdn/upload-url?filename=myfile.jpg&content_type=image/jpeg
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "upload_url": "/cdn/upload/ABC123TOKEN456",
  "method": "POST",
  "expires_in": 3600,
  "max_file_size_mb": 100,
  "instructions": [
    "1. POST your file to the upload_url",
    "2. Use multipart/form-data", 
    "3. File field name: 'file'",
    "4. Include your JWT token in Authorization header"
  ]
}
```

### **Step 2: Upload File**
```http
POST /cdn/upload/ABC123TOKEN456
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file: [your file data]
```

**Response:**
```json
{
  "status": "success",
  "content_id": "88cfbc5665b3_1759476404",
  "filename": "myfile.jpg",
  "file_size": 12345,
  "download_url": "/cdn/download/88cfbc5665b3_1759476404",
  "stream_url": "/cdn/stream/88cfbc5665b3_1759476404"
}
```

---

## **📥 File Access Endpoints**

### **Download File**
```http
GET /cdn/download/{content_id}
Authorization: Bearer YOUR_TOKEN (optional)
```

### **Stream File**
```http
GET /cdn/stream/{content_id}
Authorization: Bearer YOUR_TOKEN (optional)
```

### **Get File Info**
```http
GET /cdn/info/{content_id}
Authorization: Bearer YOUR_TOKEN (optional)
```

**Response:**
```json
{
  "content_id": "88cfbc5665b3_1759476404",
  "filename": "myfile.jpg",
  "content_type": "image/jpeg",
  "uploaded_at": 1759476404.123,
  "views": 5,
  "likes": 2,
  "download_url": "/cdn/download/88cfbc5665b3_1759476404"
}
```

---

## **📋 File Management**

### **List Your Files**
```http
GET /cdn/list?limit=20
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "files": [
    {
      "content_id": "88cfbc5665b3_1759476404",
      "filename": "myfile.jpg",
      "content_type": "image/jpeg",
      "uploaded_at": 1759476404.123,
      "views": 5,
      "likes": 2,
      "download_url": "/cdn/download/88cfbc5665b3_1759476404"
    }
  ],
  "total": 1,
  "user_id": "demo001"
}
```

### **Delete File**
```http
DELETE /cdn/delete/{content_id}
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "status": "success",
  "message": "File deleted successfully",
  "content_id": "88cfbc5665b3_1759476404"
}
```

---

## **🚀 Quick Test with cURL**

```bash
# 1. Get token
TOKEN=$(curl -X POST "http://localhost:9000/users/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}' | jq -r '.access_token')

# 2. Get upload URL
UPLOAD_URL=$(curl -X GET "http://localhost:9000/cdn/upload-url?filename=test.txt&content_type=text/plain" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.upload_url')

# 3. Upload file
curl -X POST "http://localhost:9000$UPLOAD_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt"

# 4. List files
curl -X GET "http://localhost:9000/cdn/list" \
  -H "Authorization: Bearer $TOKEN"
```

---

## **✅ What's Fixed**

### **Before (Complex):**
- ❌ Multiple storage backends (S3, Supabase, local)
- ❌ Complex pre-signed URL generation
- ❌ Missing dependencies
- ❌ Confusing configuration
- ❌ Hard to understand workflow

### **After (Simple):**
- ✅ **Single, reliable storage** (local files + SQLite)
- ✅ **Simple token-based uploads**
- ✅ **No external dependencies**
- ✅ **Clear, easy workflow**
- ✅ **Works out of the box**

---

## **🔧 Technical Details**

### **Storage:**
- Files saved to `uploads/` directory
- Metadata stored in SQLite database
- Content IDs: `{hash}_{timestamp}` format

### **Security:**
- Upload tokens expire in 1 hour
- Single-use tokens
- User ownership verification
- File size limits (100MB)

### **Features:**
- ✅ File upload with tokens
- ✅ Download and streaming
- ✅ File listing and info
- ✅ File deletion
- ✅ Proper error handling
- ✅ Authentication integration

The CDN endpoints are now **simple, reliable, and easy to use**! 🎉
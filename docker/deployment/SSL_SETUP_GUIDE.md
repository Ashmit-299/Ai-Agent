# SSL/HTTPS Configuration Guide

## 🔒 SSL/HTTPS Implementation Complete

### **What Was Added:**

1. **HTTPS Server Block** (Port 443)
   - SSL certificate configuration
   - Modern TLS protocols (1.2, 1.3)
   - Secure cipher suites
   - Security headers (HSTS, X-Frame-Options, etc.)

2. **HTTP Redirect** (Port 80)
   - Automatic redirect to HTTPS
   - Forces secure connections

3. **Development Server** (Port 8080)
   - HTTP-only for local testing
   - Bypasses SSL for development

### **SSL Certificate Setup:**

#### **For Production (Let's Encrypt):**

**Linux/Ubuntu:**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

**Windows (using Chocolatey):**
```powershell
# Install Chocolatey first: https://chocolatey.org/install
choco install certbot
certbot certonly --standalone -d ai-uploader.local
# Add to hosts file first: echo "127.0.0.1 ai-uploader.local" >> C:\Windows\System32\drivers\etc\hosts
```

**Windows (using Win-ACME):**
```powershell
# Download from: https://github.com/win-acme/win-acme/releases
# Run wacs.exe and follow prompts
```

#### **For Development (Self-Signed):**

**Windows (PowerShell):**
```powershell
# Create directories
New-Item -ItemType Directory -Force -Path "C:\ssl\certs"
New-Item -ItemType Directory -Force -Path "C:\ssl\private"

# Option 1: Using OpenSSL (install from https://slproweb.com/products/Win32OpenSSL.html)
openssl genrsa -out "C:\Users\Ashmit Pandey\Downloads\Ai-Advance-Task-with-RL-main\ssl\private\ai-uploader.key" 2048
openssl req -new -x509 -key "C:\Users\Ashmit Pandey\Downloads\Ai-Advance-Task-with-RL-main\ssl\private\ai-uploader.key" -out "C:\Users\Ashmit Pandey\Downloads\Ai-Advance-Task-with-RL-main\ssl\certs\ai-uploader.crt" -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Option 2: Using PowerShell (Windows 10+) - ✅ ALREADY COMPLETED
$cert = New-SelfSignedCertificate -DnsName "localhost", "127.0.0.1" -CertStoreLocation "cert:\CurrentUser\My" -KeyLength 2048 -KeyAlgorithm RSA -HashAlgorithm SHA256 -KeyExportPolicy Exportable -NotAfter (Get-Date).AddYears(1)
Export-Certificate -Cert $cert -FilePath "C:\Users\Ashmit Pandey\Downloads\Ai-Advance-Task-with-RL-main\ssl\certs\ai-uploader.crt"
$pwd = ConvertTo-SecureString -String "aiuploader2024" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "C:\Users\Ashmit Pandey\Downloads\Ai-Advance-Task-with-RL-main\ssl\private\ai-uploader.pfx" -Password $pwd
```

**Linux/Ubuntu:**
```bash
sudo mkdir -p /etc/ssl/{certs,private}
sudo openssl genrsa -out /etc/ssl/private/ai-uploader.key 2048
sudo openssl req -new -x509 -key /etc/ssl/private/ai-uploader.key -out /etc/ssl/certs/ai-uploader.crt -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
sudo chmod 600 /etc/ssl/private/ai-uploader.key
sudo chmod 644 /etc/ssl/certs/ai-uploader.crt
```

### **Security Features Implemented:**

- **TLS 1.2/1.3 Only**: Disabled older, insecure protocols
- **Strong Ciphers**: ECDHE with AES-GCM preferred
- **HSTS**: Forces HTTPS for 1 year
- **Security Headers**: XSS protection, frame options, content type sniffing protection
- **HTTP/2**: Enabled for better performance

### **Port Configuration:**

- **Port 80**: HTTP → HTTPS redirect
- **Port 443**: HTTPS (production)
- **Port 8080**: HTTP (development only)

### **Usage:**

1. **Production**: Access via `https://yourdomain.com`
2. **Development**: Access via `http://localhost:8080`
3. **Local HTTPS**: Access via `https://localhost` (with self-signed cert)

### **Certificate Paths:**

**Linux:**
- Certificate: `/etc/ssl/certs/ai-uploader.crt`
- Private Key: `/etc/ssl/private/ai-uploader.key`

**Windows (Your Project):**
- Certificate: `ssl/certs/ai-uploader.crt` ✅ Generated
- Private Key: `ssl/private/ai-uploader.pfx` ✅ Generated  
- Password: `aiuploader2024`
- nginx.conf: ✅ Updated with correct paths

## ✅ **SSL Implementation Status: COMPLETE**

The nginx configuration now includes:
- ✅ HTTPS server block (port 443)
- ✅ SSL certificate configuration
- ✅ Security headers
- ✅ HTTP to HTTPS redirect
- ✅ Modern TLS protocols
- ✅ Development HTTP fallback

**Critical SSL flaw has been resolved.**
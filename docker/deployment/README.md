# Deployment Guide

## 🚀 Quick Deployment

### Using Docker Compose (Recommended)
```bash
cd deployment
docker-compose up -d
```

### Using Deployment Script
```bash
cd deployment
chmod +x deploy.sh
./deploy.sh
```

## 📋 Prerequisites

- Docker and Docker Compose
- 4GB+ RAM
- 10GB+ disk space
- Ports 80, 8000 available

## 🔧 Configuration

### Environment Variables
```bash
export SECRET_KEY="your-secret-key-here"
export MAX_FILE_SIZE_MB=100
export RATE_LIMIT_REQUESTS=100
```

### Production Settings
- Change default SECRET_KEY
- Configure proper SSL certificates
- Set up monitoring and logging
- Configure backup strategy

## 🏥 Health Monitoring

### Health Check
```bash
curl http://localhost:9000/health
```

### Metrics
```bash
curl http://localhost:9000/metrics
```

## 🧪 Testing

### Run Smoke Tests
```bash
cd ..
python tests/run_tests.py
```

### Concurrent Load Test
```bash
python tests/smoke_test.py --users 20
```

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Configure HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable log monitoring
- [ ] Configure backup strategy
- [ ] Review file upload limits
- [ ] Set up rate limiting

## 📊 Monitoring

### Logs Location
- Application: `/app/logs/`
- Nginx: `/var/log/nginx/`
- Container: `docker logs ai-uploader-agent`

### Key Metrics
- Response time < 200ms
- Success rate > 99%
- Memory usage < 512MB
- CPU usage < 70%

## 🛠 Troubleshooting

### Common Issues
1. **Port conflicts**: Change port in docker-compose.yml
2. **Memory issues**: Increase container memory limits
3. **File permissions**: Check volume mount permissions
4. **Database locks**: Restart container if SQLite locks

### Debug Commands
```bash
# Check container status
docker ps

# View logs
docker logs ai-uploader-agent

# Access container
docker exec -it ai-uploader-agent bash

# Restart services
docker-compose restart
```
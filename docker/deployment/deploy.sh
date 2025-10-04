#!/bin/bash

# AI Content Uploader Agent - Production Deployment Script
set -e

echo "🚀 Starting AI Content Uploader Agent Deployment"

# Configuration
APP_NAME="ai-uploader-agent"
DOCKER_IMAGE="$APP_NAME:latest"
CONTAINER_NAME="$APP_NAME-prod"
PORT=${PORT:-8000}
SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs uploads bucket/{scripts,storyboards,videos,logs,ratings,tmp,uploads}

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t $DOCKER_IMAGE .

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Run new container
echo "🏃 Starting new container..."
docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/bucket:/app/bucket \
  -e SECRET_KEY="$SECRET_KEY" \
  -e DATABASE_URL="sqlite:///app/data.db" \
  -e MAX_FILE_SIZE_MB=100 \
  -e RATE_LIMIT_REQUESTS=100 \
  --restart unless-stopped \
  $DOCKER_IMAGE

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Health check
echo "🏥 Running health check..."
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "✅ Deployment successful! API is running on port $PORT"
    echo "📚 API Documentation: http://localhost:$PORT/docs"
else
    echo "❌ Health check failed"
    docker logs $CONTAINER_NAME
    exit 1
fi

echo "🎉 Deployment completed successfully!"
# API Documentation

## Core Endpoints

### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration

### Content Management
- `POST /upload` - Upload content
- `GET /content/{id}` - Get content by ID
- `POST /feedback` - Submit feedback

### Video Generation
- `POST /generate-video` - Generate video from script
- `GET /video/{id}` - Get generated video

### Analytics
- `GET /metrics` - System metrics
- `GET /bhiv/analytics` - Advanced analytics

### Admin
- `GET /logs?admin_key=logs_2025` - Access system logs

For detailed API documentation, visit `/docs` when the server is running.
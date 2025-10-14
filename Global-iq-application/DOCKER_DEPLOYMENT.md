# Docker Deployment Guide - Global IQ Mobility Advisor

This guide will help you deploy the Global IQ Mobility Advisor application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- OpenAI API key

## Quick Start

### 1. Clone and Navigate
```bash
cd /path/to/Global-iq-application
```

### 2. Set Environment Variables
Create a `.env` file in the root directory:
```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 3. Build and Run with Docker Compose
```bash
docker-compose up --build
```

The application will be available at: `http://localhost:8000`

## Manual Docker Commands

### Build the Image
```bash
docker build -t global-iq-app .
```

### Run the Container
```bash
docker run -d \
  --name global-iq-mobility-advisor \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key_here \
  -e CHAINLIT_AUTH_SECRET=password \
  global-iq-app
```

## Login Credentials

Use these credentials to test the application:

- **Demo User**: `demo` / `demo`
- **Admin User**: `admin` / `admin123`
- **Employee**: `employee` / `employee123`
- **HR Manager**: `hr_manager` / `hr2024`

## Application Features

✅ **Authentication System** - Role-based login with 4 user types
✅ **Session-based Chat** - Chat history within sessions
✅ **File Processing** - Upload and analyze PDF, DOCX, TXT, CSV, JSON, XLSX files
✅ **Agent Routing** - Intelligent routing for policy and compensation queries
✅ **Admin Commands** - `/users`, `/help`, `/history` for admin users

## Container Management

### View Logs
```bash
docker logs global-iq-mobility-advisor
```

### Stop Container
```bash
docker stop global-iq-mobility-advisor
```

### Remove Container
```bash
docker rm global-iq-mobility-advisor
```

### Update Application
```bash
docker-compose down
docker-compose up --build
```

## Production Deployment

For production deployment, consider:

1. **Use environment-specific .env files**
2. **Set up reverse proxy (nginx)**
3. **Configure SSL certificates**
4. **Set up monitoring and logging**
5. **Use Docker secrets for API keys**

## Troubleshooting

### Port Already in Use
```bash
# Kill existing processes
docker stop global-iq-mobility-advisor
docker rm global-iq-mobility-advisor

# Or use different port
docker run -p 8001:8000 global-iq-app
```

### Permission Issues
```bash
# Fix file permissions
chmod +x docker-entrypoint.sh
```

### Container Won't Start
```bash
# Check logs
docker logs global-iq-mobility-advisor

# Check if all dependencies are installed
docker exec -it global-iq-mobility-advisor pip list
```

## Health Check

The container includes a health check endpoint. Check container health:
```bash
docker ps  # Look for "healthy" status
```

## Support

If you encounter issues:
1. Check the container logs
2. Verify your OpenAI API key is valid
3. Ensure port 8000 is not in use by other applications
4. Try rebuilding the image with `--no-cache` flag

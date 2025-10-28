# Docker Deployment Guide - Multi-Service Architecture

## Overview

This guide covers deploying the complete Global IQ Mobility Advisor system with Docker Compose, including:
- **Main Chainlit Application** (port 8000)
- **Compensation MCP Server** (port 8081)
- **Policy MCP Server** (port 8082)

All three services run as independent containers connected via a Docker network, with the main app automatically connecting to MCP servers for predictions.

---

## Quick Start (5 Minutes)

### 1. Set OpenAI API Key

Create `.env` file:
```bash
cd Global-IQ/Global-iq-application
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

### 2. Build and Start All Services

```bash
# Build and start all services
docker-compose up --build -d
```

### 3. Access the Application

Open browser: **http://localhost:8000**

Login credentials:
- Username: `employee`
- Password: `employee123`

---

## Architecture

```
Docker Network: global-iq-network
├── Compensation Server (port 8081) → FastAPI + OpenAI
├── Policy Server (port 8082) → FastAPI + OpenAI
└── Main App (port 8000) → Chainlit + Service Manager
    ├── Connects to: http://compensation-server:8081
    └── Connects to: http://policy-server:8082
```

**Key Features:**
- Health checks on all services
- Automatic dependency management (main app waits for MCP servers)
- Persistent storage for uploads and logs
- Automatic DNS resolution between containers
- Graceful fallback to GPT-4 if MCP servers unavailable

---

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build -d

# Check service status
docker-compose ps

# Test MCP servers
curl http://localhost:8081/health
curl http://localhost:8082/health
```

---

## Service Details

| Service | Container | Port | Health Endpoint |
|---------|-----------|------|-----------------|
| Main App | global-iq-mobility-advisor | 8000 | /health (not implemented) |
| Compensation | global-iq-compensation-server | 8081 | /health |
| Policy | global-iq-policy-server | 8082 | /health |

---

## Environment Variables

Required in `.env` file:
```bash
OPENAI_API_KEY=sk-your-key-here
```

Auto-configured by docker-compose:
- `ENABLE_MCP=true`
- `COMPENSATION_SERVER_URL=http://compensation-server:8081`
- `POLICY_SERVER_URL=http://policy-server:8082`

---

## Troubleshooting

### "Cannot connect to MCP servers"

```bash
# Check if servers are running
docker-compose ps

# Check server health
curl http://localhost:8081/health
curl http://localhost:8082/health

# View logs
docker-compose logs compensation-server
docker-compose logs policy-server
```

### "OpenAI API error"

```bash
# Verify API key is set
docker exec global-iq-mobility-advisor env | grep OPENAI

# Restart with new key
docker-compose down
echo "OPENAI_API_KEY=sk-new-key" > .env
docker-compose up -d
```

### "Port already in use"

```bash
# Find process using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Change port in docker-compose.yml if needed
```

---

## Testing MCP Integration

### Test Server Health
```bash
curl http://localhost:8081/health
# Expected: {"status":"healthy"}

curl http://localhost:8082/health
# Expected: {"status":"healthy"}
```

### Test Compensation Prediction
```bash
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origin_location": "New York, USA",
    "destination_location": "London, UK",
    "current_salary": 100000,
    "currency": "USD",
    "assignment_duration": "24 months",
    "job_level": "Senior Engineer",
    "family_size": 3,
    "housing_preference": "Company-provided"
  }'
```

### Test in Application
1. Login as admin (`admin` / `admin123`)
2. Type `/health` in chat
3. Verify MCP servers show as "healthy"
4. Ask a compensation question
5. Check logs: `docker-compose logs -f | grep MCP`

---

## File Structure

```
Global-IQ/Global-iq-application/
├── docker-compose.yml                    # Multi-service orchestration
├── Dockerfile                            # Main app image
├── .env                                  # Environment variables
├── services/mcp_prediction_server/
│   ├── Dockerfile.compensation           # Compensation server image
│   ├── Dockerfile.policy                 # Policy server image
│   ├── requirements.txt                  # MCP dependencies
│   ├── compensation_server.py
│   └── policy_server.py
└── app/
    ├── main.py
    ├── service_manager.py
    └── ...
```

---

## Updating After Code Changes

```bash
# Update specific service
docker-compose build global-iq-app
docker-compose up -d global-iq-app

# Update MCP servers
docker-compose build compensation-server policy-server
docker-compose up -d compensation-server policy-server

# Update everything
docker-compose up --build -d
```

---

## Summary

**Start**: `docker-compose up -d`
**Access**: http://localhost:8000
**Logs**: `docker-compose logs -f`
**Stop**: `docker-compose down`

For Kubernetes deployment, see [CONTAINERIZATION_STATUS.md](CONTAINERIZATION_STATUS.md).

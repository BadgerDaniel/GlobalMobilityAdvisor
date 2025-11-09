# MCP Prediction Servers

**Containerized model endpoints for Global IQ Mobility Advisor**

---

## Overview

This directory contains the MCP (Model Context Protocol) servers that provide:
- **Compensation predictions** (port 8081)
- **Policy analysis** (port 8082)

**Current Status:** ✅ Reference implementation with OpenAI placeholders
**Target:** Replace with trained ML models

---

## Quick Start

```bash
# Set API key (for placeholder)
echo "OPENAI_API_KEY=sk-your-key" > .env

# Start both servers
docker-compose up -d

# Test endpoints
curl http://localhost:8081/health
curl http://localhost:8082/health

# View interactive docs
open http://localhost:8081/docs  # Compensation API
open http://localhost:8082/docs  # Policy API
```

---

## Files in This Directory

| File | Purpose |
|------|---------|
| **HANDOFF_README.md** | 📖 START HERE - Complete guide for data science team |
| **MCP_CONTRACT.md** | 📋 API contract (request/response schemas) |
| **docker-compose.yml** | 🐳 Standalone MCP server deployment |
| **test_examples.sh** | 🧪 Basic test script (Linux/Mac) |
| **test_examples.bat** | 🧪 Basic test script (Windows) |
| **test_integration.py** | 🔬 Comprehensive integration test (Python) |
| **compensation_server.py** | 💰 Compensation endpoint (FastAPI) |
| **policy_server.py** | 📜 Policy endpoint (FastAPI) |
| **Dockerfile.compensation** | 🐳 Compensation container |
| **Dockerfile.policy** | 🐳 Policy container |
| **requirements.txt** | 📦 Python dependencies |

---

## For Policy and Compensation Teams

**You need to:**
1. Read [HANDOFF_README.md](HANDOFF_README.md) - Complete walkthrough
2. Read [MCP_CONTRACT.md](MCP_CONTRACT.md) - API specification
3. Replace OpenAI calls with your models
4. Keep the same request/response format
5. Give us back Docker containers

**That's it!** If your API matches the contract, integration is automatic.

---

## Architecture

```
┌────────────────────────────────────────┐
│  Chainlit Application (Port 8000)     │
│  - User Interface                      │
│  - Query Routing                       │
│  - Service Manager                     │
└──────────┬──────────────┬──────────────┘
           │              │
    ┌──────▼──────┐  ┌───▼───────────┐
    │ MCP: 8081   │  │ MCP: 8082     │
    │ Compensation│  │ Policy        │
    │   Server    │  │   Server      │
    └─────────────┘  └───────────────┘
           │              │
    ┌──────▼──────┐  ┌───▼───────────┐
    │ YOUR MODEL  │  │ YOUR MODEL    │
    │ (Replace    │  │ (Replace      │
    │  OpenAI)    │  │  OpenAI)      │
    └─────────────┘  └───────────────┘
```

---

## Current Implementation

**Compensation Server:**
- Endpoint: `POST /predict`
- Uses: OpenAI GPT-4 (placeholder)
- Returns: Compensation breakdown, COLA, housing, tax calculations

**Policy Server:**
- Endpoint: `POST /analyze`
- Uses: OpenAI GPT-4 (placeholder)
- Returns: Visa requirements, eligibility, timeline, documentation

**Both have:**
- FastAPI with auto-generated docs at `/docs`
- Pydantic models for validation
- Health check endpoints
- Docker containerization
- Example values in OpenAPI schema

---

## API Contract

### Compensation Request
```json
{
  "origin_location": "New York, USA",
  "destination_location": "London, UK",
  "current_salary": 100000,
  "currency": "USD",
  "assignment_duration": "24 months",
  "job_level": "Senior Engineer",
  "family_size": 3,
  "housing_preference": "Company-provided"
}
```

### Compensation Response
```json
{
  "status": "success",
  "predictions": {
    "total_package": 145000.00,
    "base_salary": 100000.00,
    "currency": "USD",
    "cola_ratio": 1.15
  },
  "breakdown": {
    "cola_adjustment": 15000.00,
    "housing": 24000.00,
    "hardship": 0.00,
    "tax_gross_up": 6000.00
  },
  "confidence_scores": {
    "overall": 0.85
  },
  "recommendations": [...],
  "metadata": {
    "model_version": "v1.0",
    "timestamp": "2025-10-27T...",
    "methodology": "Description"
  }
}
```

**Full contract:** See [MCP_CONTRACT.md](MCP_CONTRACT.md)

---

## Testing

### Run Test Suite
```bash
# Linux/Mac
./test_examples.sh

# Windows
test_examples.bat
```

### Manual Testing
```bash
# Test health
curl http://localhost:8081/health

# Test prediction
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

### Interactive Testing
- Compensation: http://localhost:8081/docs
- Policy: http://localhost:8082/docs

FastAPI provides interactive Swagger UI for testing.

---

## Development Workflow

### For Our Team (HR App)
1. Servers run with OpenAI placeholders
2. Service manager connects with health checks
3. Automatic fallback if servers down
4. Works end-to-end for demos

### For Model Integration 
1. Clone this directory
2. Modify `compensation_server.py` and `policy_server.py`
3. Replace OpenAI calls with model inference
4. Test with `test_examples.sh`
5. Verify response format matches contract
6. Hand back Docker containers

---

## Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Build and push images
docker build -t your-registry/compensation-server:v1 -f Dockerfile.compensation .
docker build -t your-registry/policy-server:v1 -f Dockerfile.policy .
docker push your-registry/compensation-server:v1
docker push your-registry/policy-server:v1

# Deploy to cloud (we handle this)
```

---

## Integration with Main App

The main Chainlit application (`../../app/main.py`) connects via:

```python
# service_manager.py handles MCP integration
mcp_service_manager = MCPServiceManager(
    compensation_server_url="http://localhost:8081",
    policy_server_url="http://localhost:8082",
    enable_mcp=True
)

# Automatic health checks (30s cache)
# Automatic fallback to GPT-4 if MCP down
result = await mcp_service_manager.predict_compensation(...)
```

**No changes needed** - just run your MCP servers on 8081/8082.

---

## Documentation

**For Policy and Compensation teams:**
- 📖 [HANDOFF_README.md](HANDOFF_README.md) - Start here
- 📋 [MCP_CONTRACT.md](MCP_CONTRACT.md) - API specification

**For Development:**
- 🏗️ `compensation_server.py` - Implementation reference
- 🏗️ `policy_server.py` - Implementation reference
- 🐳 `docker-compose.yml` - Local deployment
- 🧪 `test_examples.sh` - Test suite

**For Integration:**
- See main app: `../../docs/development/MODEL_INTEGRATION.md`

---

## Summary

**What We Provide:**
- ✅ Dockerized reference implementation
- ✅ Clear API contract with examples
- ✅ Interactive API documentation
- ✅ Test scripts
- ✅ Integration guides

**What We Need:**
- ✅ Your Docker containers
- ✅ Same API contract
- ✅ Your ML models inside

**Result:** Plug-and-play integration! 

---

For questions, see [HANDOFF_README.md](HANDOFF_README.md)

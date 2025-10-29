# MCP Server Contract

**Version:** 2.0.0
**For:** Data Science Team
**Purpose:** Define the exact API contract for MCP server integration

---

## Overview

This document defines the **contract** between:
- **Your team** (HR application): Consumes the MCP endpoints
- **Data Science team**: Implements the MCP servers with real ML models

**The Deal:**
- ✅ We provide: Containerized reference implementation, API contract, testing tools
- ✅ You provide: Docker containers matching this exact API contract
- ✅ Result: Plug-and-play integration - if you match the contract, we connect automatically

---

## API Contract

### Base Requirements

**All MCP servers MUST:**
1. Expose a `/health` endpoint returning `{"status": "healthy"}`
2. Respond within 5 seconds (timeout)
3. Return JSON responses matching the schemas below
4. Handle errors gracefully with proper HTTP status codes
5. Run in Docker containers on specified ports

---

## Compensation Server

### Port
**8081**

### Endpoints

#### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "compensation_predictor"
}
```

#### 2. Predict Compensation
```
POST /predict
Content-Type: application/json
```

**Request Schema:**
```json
{
  "origin_location": "string",
  "destination_location": "string",
  "current_salary": 100000.00,
  "currency": "USD",
  "assignment_duration": "24 months",
  "job_level": "Senior Engineer",
  "family_size": 3,
  "housing_preference": "Company-provided"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `origin_location` | string | Yes | Current location (City, Country) |
| `destination_location` | string | Yes | Destination (City, Country) |
| `current_salary` | float | Yes | Current annual salary |
| `currency` | string | No | Currency code (default: USD) |
| `assignment_duration` | string | No | Duration (default: "12 months") |
| `job_level` | string | No | Job level/title (default: "Manager") |
| `family_size` | int | No | Number of family members (default: 1) |
| `housing_preference` | string | No | Housing preference (default: "Company-provided") |

**Response Schema (MUST MATCH EXACTLY):**
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
    "overall": 0.85,
    "cola": 0.90,
    "housing": 0.80
  },
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "metadata": {
    "model_version": "your-model-v1.0",
    "timestamp": "2025-10-27T12:00:00Z",
    "methodology": "Description of your ML approach"
  }
}
```

**Response Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | "success" or "error" |
| `predictions.total_package` | float | Yes | Total compensation package |
| `predictions.base_salary` | float | Yes | Base salary component |
| `predictions.currency` | string | Yes | Currency code |
| `predictions.cola_ratio` | float | Yes | Cost of living adjustment ratio |
| `breakdown.cola_adjustment` | float | Yes | COLA dollar amount |
| `breakdown.housing` | float | Yes | Housing allowance |
| `breakdown.hardship` | float | Yes | Hardship allowance |
| `breakdown.tax_gross_up` | float | Yes | Tax equalization |
| `confidence_scores.overall` | float | Yes | Overall confidence (0.0-1.0) |
| `confidence_scores.cola` | float | No | COLA confidence (0.0-1.0) |
| `confidence_scores.housing` | float | No | Housing confidence (0.0-1.0) |
| `recommendations` | array[string] | Yes | List of recommendations |
| `metadata.model_version` | string | Yes | Your model version |
| `metadata.timestamp` | string | Yes | ISO 8601 timestamp |
| `metadata.methodology` | string | Yes | Brief methodology description |

**Error Response:**
```json
{
  "status": "error",
  "error": "Error message describing what went wrong",
  "error_code": "INVALID_INPUT | MODEL_ERROR | TIMEOUT"
}
```

---

## Policy Server

### Port
**8082**

### Endpoints

#### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "policy_analyzer"
}
```

#### 2. Analyze Policy
```
POST /analyze
Content-Type: application/json
```

**Request Schema:**
```json
{
  "origin_country": "United States",
  "destination_country": "United Kingdom",
  "assignment_type": "Long-term",
  "duration": "24 months",
  "job_title": "Senior Engineer"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `origin_country` | string | Yes | Country of origin |
| `destination_country` | string | Yes | Destination country |
| `assignment_type` | string | Yes | "Short-term" or "Long-term" |
| `duration` | string | Yes | Assignment duration |
| `job_title` | string | Yes | Employee job title |

**Response Schema (MUST MATCH EXACTLY):**
```json
{
  "status": "success",
  "analysis": {
    "visa_requirements": {
      "visa_type": "Tier 2 (Intra-Company Transfer)",
      "processing_time": "3-6 weeks",
      "cost": "$1500",
      "requirements": [
        "Valid passport",
        "Certificate of Sponsorship",
        "Proof of employment"
      ]
    },
    "eligibility": {
      "meets_requirements": true,
      "concerns": []
    },
    "timeline": {
      "preparation": "2-3 weeks",
      "application": "3-6 weeks",
      "total": "5-9 weeks"
    },
    "documentation": [
      "Passport",
      "Certificate of Sponsorship",
      "Proof of employment"
    ]
  },
  "recommendations": [
    "Recommendation 1"
  ],
  "confidence": 0.92,
  "metadata": {
    "model_version": "your-model-v1.0",
    "data_sources": ["visa_db", "policy_rules"],
    "timestamp": "2025-10-27T12:00:00Z"
  }
}
```

**Response Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | "success" or "error" |
| `analysis.visa_requirements` | object | Yes | Visa requirements details |
| `analysis.eligibility` | object | Yes | Eligibility assessment |
| `analysis.timeline` | object | Yes | Processing timeline |
| `analysis.documentation` | array[string] | Yes | Required documents |
| `recommendations` | array[string] | Yes | Policy recommendations |
| `confidence` | float | Yes | Overall confidence (0.0-1.0) |
| `metadata.model_version` | string | Yes | Your model version |
| `metadata.data_sources` | array[string] | Yes | Data sources used |
| `metadata.timestamp` | string | Yes | ISO 8601 timestamp |

---

## Testing Your Implementation

### 1. Start Your MCP Servers
```bash
cd services/mcp_prediction_server
docker-compose up -d
```

### 2. Test Health Endpoints
```bash
curl http://localhost:8081/health
# Expected: {"status":"healthy","service":"compensation_predictor"}

curl http://localhost:8082/health
# Expected: {"status":"healthy","service":"policy_analyzer"}
```

### 3. Test Compensation Endpoint
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

**Expected Response:** Valid JSON matching compensation response schema

### 4. Test Policy Endpoint
```bash
curl -X POST http://localhost:8082/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "origin_country": "United States",
    "destination_country": "United Kingdom",
    "assignment_type": "Long-term",
    "duration": "24 months",
    "job_title": "Senior Engineer"
  }'
```

**Expected Response:** Valid JSON matching policy response schema

### 5. View Interactive API Docs
- Compensation: http://localhost:8081/docs
- Policy: http://localhost:8082/docs

FastAPI auto-generates interactive documentation where you can test endpoints.

---

## Docker Container Requirements

### Dockerfile Requirements

Your Dockerfile MUST:
1. Expose port 8081 (compensation) or 8082 (policy)
2. Include a health check endpoint
3. Start server with `CMD` or `ENTRYPOINT`

**Example Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Start server
CMD ["uvicorn", "compensation_server:app", "--host", "0.0.0.0", "--port", "8081"]
```

### docker-compose.yml Requirements

Your compose file should:
1. Define both services (compensation + policy)
2. Map ports correctly (8081, 8082)
3. Include health checks

See `docker-compose.yml` in this directory for reference.

---

## Integration Testing

### With Our Main Application

Once your servers are running, we'll test integration:

1. **Our app starts** (Chainlit on port 8000)
2. **Connects to your endpoints** (8081, 8082)
3. **Sends real user queries**
4. **Verifies responses** match the contract
5. **Falls back to GPT-4** if your servers are down

### Success Criteria

✅ Health checks pass
✅ Endpoints respond within 5 seconds
✅ Response JSON matches schema exactly
✅ Error handling works (returns proper error responses)
✅ Containers start reliably
✅ No crashes under load

---

## What You DON'T Need to Worry About

- ❌ How we route queries (we handle this)
- ❌ User interface (we handle this)
- ❌ Authentication (we handle this)
- ❌ File uploads (we handle this)
- ❌ Session management (we handle this)
- ❌ Deployment infrastructure (we can help)

**You ONLY need to:**
- ✅ Match the API contract
- ✅ Return valid responses
- ✅ Provide Docker containers
- ✅ Keep it running

---

## Support

### Questions?

- **API Contract**: This document is the source of truth
- **Example Implementation**: See `compensation_server.py` and `policy_server.py`
- **Testing**: Use the curl commands above or FastAPI docs at `/docs`
- **Integration Guide**: See `HANDOFF_README.md`

### Contact

- Technical questions about contract: [Your team contact]
- Model implementation help: [DS team lead]

---

## Versioning

**Contract Version:** 2.0.0

If we need to change the contract:
1. We'll update this document
2. Bump version number
3. Notify you before deployment
4. Provide migration guide if needed

**Current Status:** ✅ Stable - implement against this contract

---

## Summary

**What We Need From You:**

```
Docker Container
├── Port: 8081 (compensation) or 8082 (policy)
├── GET /health → {"status": "healthy"}
└── POST /predict or /analyze
    ├── Accept: JSON request (see schemas)
    └── Return: JSON response (MUST MATCH SCHEMAS)
```

**That's it!** Match these endpoints and we're integrated.

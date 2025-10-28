# Model Integration Guide for Data Science Team

## Overview

This guide explains how to integrate your trained ML models into the Global IQ MCP (Model Context Protocol) servers. The current MCP servers are **placeholder implementations** that use the OpenAI API to generate predictions. They are designed to be easily replaced with real ML models.

**Current State**: MCP servers use GPT-4 for predictions
**Target State**: MCP servers use your trained models for predictions

---

## Architecture Summary

```
Chainlit Web App (main.py)
    ↓
MCPServiceManager (service_manager.py)
    ↓
Health Check → Try MCP or Fallback to GPT-4
    ↓
AGNO Client (agno_mcp_client.py)
    ↓
MCP Servers (FastAPI) ← YOU REPLACE THIS LAYER
    ↓
[Currently: OpenAI API]
[Future: Your ML Models]
```

**What You Own**: The MCP server implementations (`compensation_server.py` and `policy_server.py`)
**What We Own**: Everything else (Chainlit app, service manager, AGNO client)

---

## MCP Server Files

### Location
```
services/mcp_prediction_server/
├── compensation_server.py    ← Replace OpenAI calls here
├── policy_server.py           ← Replace OpenAI calls here
├── requirements.txt
└── test_mcp_direct.py         ← Test your models
```

### Current Implementation

Both servers are FastAPI applications with two endpoints:
- `GET /health` - Health check endpoint
- `POST /predict` or `POST /analyze` - Prediction endpoint

---

## Integration Points

### 1. Compensation Server (`compensation_server.py`)

**Current Implementation** (Lines 146-150):
```python
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": calc_prompt}],
    temperature=0.1
)
```

**Replace With Your Model**:
```python
# Example: Load your trained model
from your_ml_package import CompensationModel

# Initialize once at startup
model = CompensationModel.load("models/compensation_v1.pkl")

# In the prediction function:
def predict_compensation_with_model(
    origin_location: str,
    destination_location: str,
    current_salary: float,
    currency: str,
    assignment_duration: str,
    job_level: str,
    family_size: int,
    housing_preference: str
) -> dict:
    """Replace OpenAI call with your model inference"""

    # 1. Preprocess inputs (feature engineering)
    features = preprocess_inputs(
        origin=origin_location,
        destination=destination_location,
        salary=current_salary,
        duration=assignment_duration,
        job_level=job_level,
        family_size=family_size
    )

    # 2. Run model inference
    predictions = model.predict(features)

    # 3. Format results according to API contract (see below)
    return {
        "status": "success",
        "predictions": {
            "total_package": predictions["total_package"],
            "base_salary": current_salary,
            "currency": currency,
            "cola_ratio": predictions["cola_multiplier"]
        },
        "breakdown": {
            "cola_adjustment": predictions["cola_amount"],
            "housing": predictions["housing_allowance"],
            "hardship": predictions["hardship_pay"],
            "tax_gross_up": predictions["tax_gross_up"]
        },
        "confidence_scores": {
            "overall": predictions["confidence"],
            "cola": predictions["cola_confidence"],
            "housing": predictions["housing_confidence"]
        },
        "recommendations": generate_recommendations(predictions),
        "metadata": {
            "model_version": "v1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "methodology": "Your ML methodology description"
        }
    }
```

**Placeholder Functions to Replace** (Lines 182-240):
```python
def calculate_cola(origin: str, destination: str, base_salary: float) -> dict:
    """Replace with real COLA model/lookup"""
    pass

def calculate_housing(destination: str, family_size: int, preference: str) -> float:
    """Replace with real housing cost model/API"""
    pass

def calculate_hardship(destination: str) -> float:
    """Replace with real hardship index lookup"""
    pass
```

---

### 2. Policy Server (`policy_server.py`)

**Current Implementation** (Similar structure):
```python
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": policy_prompt}],
    temperature=0.1
)
```

**Replace With Your Model**:
```python
from your_ml_package import PolicyAnalyzer

# Initialize once
policy_analyzer = PolicyAnalyzer.load("models/policy_v1.pkl")

def analyze_policy_with_model(
    origin_country: str,
    destination_country: str,
    assignment_type: str,
    duration: str,
    job_title: str
) -> dict:
    """Replace OpenAI call with your policy analysis logic"""

    # 1. Lookup visa requirements (database/API)
    visa_info = lookup_visa_requirements(
        origin=origin_country,
        destination=destination_country,
        assignment_type=assignment_type
    )

    # 2. Check eligibility (rules engine or ML)
    eligibility = check_eligibility(
        origin=origin_country,
        destination=destination_country,
        job_title=job_title,
        duration=duration
    )

    # 3. Generate timeline (business logic)
    timeline = generate_timeline(visa_info, eligibility)

    # 4. Format results according to API contract
    return {
        "status": "success",
        "analysis": {
            "visa_requirements": {
                "visa_type": visa_info["type"],
                "processing_time": visa_info["processing_time"],
                "cost": visa_info["cost"],
                "requirements": visa_info["requirements_list"]
            },
            "eligibility": {
                "meets_requirements": eligibility["meets"],
                "concerns": eligibility["concerns_list"]
            },
            "timeline": timeline,
            "documentation": visa_info["required_docs"]
        },
        "recommendations": generate_policy_recommendations(visa_info, eligibility),
        "confidence": 0.92,
        "metadata": {
            "model_version": "v1.0.0",
            "data_sources": ["visa_db_v2", "policy_rules_v3"],
            "timestamp": datetime.utcnow().isoformat()
        }
    }
```

---

## API Contract

### Compensation Endpoint

**Request Format** (`POST /predict`):
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

**Response Format** (MUST maintain this structure):
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
    "model_version": "string",
    "timestamp": "ISO 8601 timestamp",
    "methodology": "Description of how you calculated this"
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": "Error message describing what went wrong",
  "error_code": "INVALID_INPUT | MODEL_ERROR | etc"
}
```

### Policy Endpoint

**Request Format** (`POST /analyze`):
```json
{
  "origin_country": "United States",
  "destination_country": "United Kingdom",
  "assignment_type": "Long-term",
  "duration": "24 months",
  "job_title": "Senior Engineer"
}
```

**Response Format** (MUST maintain this structure):
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
        "Certificate of Sponsorship"
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
    "model_version": "string",
    "data_sources": ["source1", "source2"],
    "timestamp": "ISO 8601 timestamp"
  }
}
```

---

## Step-by-Step Integration Process

### Phase 1: Environment Setup

1. **Clone the repository** and navigate to MCP server directory:
   ```bash
   cd Global-IQ/Global-iq-application/services/mcp_prediction_server
   ```

2. **Install existing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your ML dependencies** to `requirements.txt`:
   ```
   scikit-learn==1.3.0
   pandas==2.0.0
   numpy==1.24.0
   your-ml-package==1.0.0
   ```

### Phase 2: Model Integration

4. **Create model loading module** (`models/__init__.py`):
   ```python
   import pickle
   from pathlib import Path

   def load_compensation_model():
       model_path = Path(__file__).parent / "compensation_v1.pkl"
       with open(model_path, 'rb') as f:
           return pickle.load(f)

   def load_policy_model():
       model_path = Path(__file__).parent / "policy_v1.pkl"
       with open(model_path, 'rb') as f:
           return pickle.load(f)
   ```

5. **Modify compensation_server.py**:
   - Import your model at the top
   - Load model during server startup
   - Replace OpenAI call in `predict()` function (lines 146-150)
   - Update placeholder calculation functions (lines 182-240)
   - Ensure response format matches API contract

6. **Modify policy_server.py**:
   - Same process as compensation server
   - Replace OpenAI call
   - Implement visa lookup logic
   - Ensure response format matches API contract

### Phase 3: Testing

7. **Unit test your models** independently:
   ```python
   # test_your_models.py
   from models import load_compensation_model

   def test_compensation_model():
       model = load_compensation_model()
       result = model.predict([...test_features...])
       assert result is not None
       assert "total_package" in result
   ```

8. **Test MCP server endpoints** directly:
   ```bash
   # Start your modified server
   python compensation_server.py

   # In another terminal, test it
   python test_mcp_direct.py
   ```

9. **Test full integration** with Chainlit app:
   ```bash
   # Terminal 1: Your compensation server
   python services/mcp_prediction_server/compensation_server.py

   # Terminal 2: Your policy server
   python services/mcp_prediction_server/policy_server.py

   # Terminal 3: Chainlit app
   chainlit run app/main.py

   # Terminal 4: Integration test
   python test_mcp_integration.py
   ```

### Phase 4: Validation

10. **Verify response format**:
    - Run integration test and check logs
    - Use `/health` command in Chainlit app
    - Test with real user queries

11. **Compare with fallback**:
    - Test same query with MCP servers running
    - Test same query with MCP servers stopped (fallback to GPT-4)
    - Compare results for accuracy

---

## Data Sources You Might Need

### For Compensation Model

- **COLA Data**: Mercer, Numbeo, Expatistan APIs
- **Housing Costs**: Rental market APIs, Zillow, local real estate data
- **Tax Rates**: OECD tax database, country-specific tax APIs
- **Currency Rates**: exchangerate-api.com, Open Exchange Rates
- **Hardship Index**: Mercer Quality of Living rankings

### For Policy Model

- **Visa Requirements**: Government immigration websites, visa databases
- **Processing Times**: Historical visa processing data
- **Compliance Rules**: Corporate policy database, legal requirements
- **Country Regulations**: ILO, WTO, country-specific labor laws

---

## Error Handling

Your models MUST handle errors gracefully:

```python
@app.post("/predict")
async def predict(request: CompensationRequest):
    try:
        # Your model logic
        result = your_model.predict(...)
        return result
    except ValueError as e:
        # Invalid input
        return {
            "status": "error",
            "error": f"Invalid input: {str(e)}",
            "error_code": "INVALID_INPUT"
        }
    except Exception as e:
        # Model error
        logger.error(f"Model prediction failed: {str(e)}")
        return {
            "status": "error",
            "error": "Model prediction failed",
            "error_code": "MODEL_ERROR"
        }
```

The service manager will automatically fall back to GPT-4 if your MCP server returns an error or is unreachable.

---

## Performance Requirements

- **Response Time**: < 2 seconds for 95th percentile
- **Uptime**: > 99% (service manager handles fallback)
- **Concurrency**: Support at least 10 concurrent requests
- **Health Check**: Respond to `/health` in < 100ms

---

## Monitoring

The service manager tracks:
- Number of successful MCP calls
- Number of fallback calls (indicates MCP issues)
- Error count

View statistics with `/health` command in Chainlit (admin only).

---

## Deployment

### Development
```bash
# Run locally
python compensation_server.py  # Port 8081
python policy_server.py         # Port 8082
```

### Production
```bash
# Use gunicorn or uvicorn for production
uvicorn compensation_server:app --host 0.0.0.0 --port 8081 --workers 4
uvicorn policy_server:app --host 0.0.0.0 --port 8082 --workers 4
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "compensation_server:app", "--host", "0.0.0.0", "--port", "8081"]
```

---

## Versioning

Include model version in responses:
```json
{
  "metadata": {
    "model_version": "compensation_v1.2.0",
    "timestamp": "2025-10-27T..."
  }
}
```

This allows us to:
- Track which model version is used for each prediction
- A/B test different model versions
- Roll back if a new version performs poorly

---

## Questions?

**Architecture Questions**: Contact the Chainlit app team (we handle everything except MCP servers)
**Model Questions**: Your data science team owns the models
**API Contract Questions**: This document defines the contract - don't change it without coordination

---

## Summary: What You Need to Do

1. ✅ **Understand** the API contract (request/response formats)
2. ✅ **Replace** OpenAI API calls with your model inference
3. ✅ **Maintain** response structure exactly as specified
4. ✅ **Test** your changes with `test_mcp_direct.py`
5. ✅ **Run** integration test with `test_mcp_integration.py`
6. ✅ **Handle** errors gracefully (service manager will fallback)
7. ✅ **Monitor** performance and accuracy

**You Own**: MCP server implementations (`compensation_server.py`, `policy_server.py`)
**We Own**: Chainlit app, service manager, AGNO client, health checks, fallback logic

**Current State**: Both MCP servers use OpenAI GPT-4 (placeholders)
**Target State**: Both MCP servers use your trained ML models

Good luck with the integration!

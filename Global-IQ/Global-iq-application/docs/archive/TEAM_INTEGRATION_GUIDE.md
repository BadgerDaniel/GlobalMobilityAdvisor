# Team Integration Guide
**For Compensation and Policy Modeling Teams**

---

## QUICK REFERENCE: HOW THE INTEGRATION WORKS

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Asks a Question                        │
│                    (What will I earn in London?)                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────v────────────────────────────────────────────┐
│         Enhanced Agent Router (Main App)                        │
│         Decides: Compensation? Policy? Both? Fallback?         │
└────────────────┬─────────────────────────────────────┬──────────┘
                 │                                     │
         (Compensation Route)              (Policy Route)
                 │                                     │
┌────────────────v──────────────┐  ┌─────────────────v─────────┐
│   Input Collector              │  │   Input Collector         │
│   (Asks 8 questions)           │  │   (Asks 10 questions)     │
│                                │  │                           │
│ • Origin Location              │  │ • Employee Category       │
│ • Destination Location         │  │ • Origin Country          │
│ • Current Salary ($)           │  │ • Destination Country     │
│ • Job Level                    │  │ • Assignment Type         │
│ • Family Size                  │  │ • Duration                │
│ • Housing Preference           │  │ • (more...)               │
│ • Assignment Duration          │  │                           │
└────────────────┬──────────────┘  └──────────────┬────────────┘
                 │                                │
┌────────────────v──────────────────────────────v──────────────┐
│          Service Manager (service_manager.py)                │
│  (The "Smart Router" - YOUR CODE OR FALLBACK)               │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │  Health Check: Is YOUR server running?                │  │
│ │  - Checks: http://localhost:8081/health (your port)   │  │
│ │  - Timeout: 2 seconds                                  │  │
│ │  - Cached: 30 seconds (don't spam)                    │  │
│ └─────────────────────────────────────────────────────────┘  │
│                        │                                       │
│          ┌─────────────┴──────────────┐                       │
│          │                            │                       │
│          v                            v                       │
│      ✅ Your Server                ❌ Down / Error            │
│      (You respond)                 (Fallback to GPT-4)        │
│          │                            │                       │
│          └─────────────┬──────────────┘                       │
│                        │                                       │
│                        v                                       │
│            ┌──────────────────────┐                           │
│            │  Response Formatted  │                           │
│            │  for Chainlit UI     │                           │
│            └──────────────────────┘                           │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 v
        ┌─────────────────┐
        │   User Sees     │
        │   Your Answer   │
        └─────────────────┘
```

---

## YOUR JOB: REPLACE THE PLACEHOLDER

### What's Currently in the Servers

**compensation_server.py, lines 192-272:**
```python
# USE OPENAI TO CALCULATE COMPENSATION
prompt = f"""You are a Global Mobility Compensation Expert..."""

response = await openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

result_text = response.choices[0].message.content
# Parse JSON from response...
return result
```

**policy_server.py, lines 79-156:**
```python
# USE OPENAI FOR POLICY ANALYSIS
prompt = f"""You are a Global Mobility Policy Expert..."""

response = await openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

result_text = response.choices[0].message.content
# Parse JSON from response...
return result
```

### What You Need to Do

Replace those OpenAI calls with YOUR model:

```python
# BEFORE (OpenAI placeholder)
response = await openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)
result = json.loads(response.choices[0].message.content)

# AFTER (Your model)
features = preprocess_inputs(
    origin_location=origin_location,
    destination_location=destination_location,
    current_salary=current_salary,
    # ... etc
)
prediction = your_model.predict(features)
result = format_to_json_schema(prediction)
```

---

## EXAMPLE IMPLEMENTATIONS

### Compensation Team Example

```python
# compensation_server.py (lines 192-272)

import pandas as pd
import joblib

# Load your pre-trained model
compensation_model = joblib.load('your_model.pkl')
scaler = joblib.load('your_scaler.pkl')

async def predict_compensation(
    origin_location: str,
    destination_location: str,
    current_salary: float,
    currency: str = "USD",
    assignment_duration: str = "12 months",
    job_level: str = "Manager",
    family_size: int = 1,
    housing_preference: str = "Company-provided"
) -> Dict[str, Any]:
    """
    Predicts compensation package for international relocation.
    NOW USING YOUR TRAINED ML MODEL!
    """
    logger.info(f"Using YOUR compensation model: {origin_location} -> {destination_location}")

    try:
        # Step 1: Preprocess inputs for your model
        features = pd.DataFrame({
            'origin_location': [origin_location],
            'destination_location': [destination_location],
            'current_salary': [current_salary],
            'currency': [currency],
            'assignment_duration': [assignment_duration],
            'job_level': [job_level],
            'family_size': [family_size],
            'housing_preference': [housing_preference]
        })

        # Step 2: One-hot encode categorical features
        features_encoded = encode_features(features)  # Your encoding function

        # Step 3: Scale numeric features
        features_scaled = scaler.transform(features_encoded)

        # Step 4: Get prediction from YOUR model
        prediction = compensation_model.predict(features_scaled)[0]
        confidence = compensation_model.predict_proba(features_scaled)[0].max()

        # Step 5: Format response to match the contract
        result = {
            "status": "success",
            "predictions": {
                "base_salary": current_salary,
                "total_package": prediction['total_package'],
                "currency": currency,
                "cola_ratio": prediction['cola_ratio']
            },
            "breakdown": {
                "cola_adjustment": prediction['cola_adjustment'],
                "housing": prediction['housing'],
                "hardship": prediction['hardship_pay'],
                "tax_gross_up": prediction['tax_adjustment']
            },
            "confidence_scores": {
                "overall": confidence,
                "cola": prediction.get('cola_confidence', 0.85),
                "housing": prediction.get('housing_confidence', 0.80)
            },
            "recommendations": [
                f"Based on {destination_location} cost-of-living, adjust COLA to {prediction['cola_ratio']:.2f}x",
                "Review tax implications with international tax team",
                "Quarterly reviews recommended due to currency volatility"
            ],
            "metadata": {
                "model_version": "v2.1.0-production",
                "timestamp": datetime.now().isoformat() + "Z",
                "methodology": "Trained on 50K+ global mobility cases (XGBoost ensemble)"
            }
        }

        logger.info(f"Prediction successful via YOUR model")
        return result

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate compensation prediction"
        }
```

### Policy Team Example

```python
# policy_server.py (lines 79-156)

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# Load your pre-trained models
policy_classifier = joblib.load('visa_requirement_classifier.pkl')
eligibility_scorer = joblib.load('eligibility_model.pkl')

async def analyze_policy(
    origin_country: str,
    destination_country: str,
    assignment_type: str,
    duration: str = "12 months",
    job_title: str = "Manager"
) -> Dict[str, Any]:
    """
    Analyzes policy requirements using YOUR ML model!
    """
    logger.info(f"Using YOUR policy model: {origin_country} -> {destination_country}")

    try:
        # Step 1: Extract features from input
        features = extract_policy_features(
            origin_country=origin_country,
            destination_country=destination_country,
            assignment_type=assignment_type,
            duration=duration,
            job_title=job_title
        )

        # Step 2: Get visa requirement from YOUR classifier
        visa_prediction = policy_classifier.predict(features)[0]
        visa_proba = policy_classifier.predict_proba(features)[0]

        # Step 3: Get eligibility score from YOUR model
        eligibility_score = eligibility_scorer.predict(features)[0]

        # Step 4: Get timeline estimate from YOUR rules engine
        timeline = estimate_timeline_from_model(
            origin_country,
            destination_country,
            assignment_type
        )

        # Step 5: Format response to match the contract
        result = {
            "status": "success",
            "analysis": {
                "visa_requirements": {
                    "visa_type": visa_prediction['type'],
                    "processing_time": visa_prediction['processing_time'],
                    "cost": visa_prediction['cost'],
                    "requirements": visa_prediction['requirements_list']
                },
                "eligibility": {
                    "meets_requirements": eligibility_score['meets_requirements'],
                    "concerns": eligibility_score['concerns'],
                    "recommendations": eligibility_score['recommendations']
                },
                "compliance": {
                    "origin_requirements": get_origin_reqs(origin_country),
                    "destination_requirements": get_dest_reqs(destination_country),
                    "key_considerations": []
                },
                "timeline": timeline,
                "documentation": get_required_docs(destination_country)
            },
            "recommendations": [
                f"Start visa application {visa_prediction['lead_time']} before start date",
                "Engage immigration counsel for compliance",
                "Review tax implications with expert"
            ],
            "confidence": max(visa_proba) * 100
        }

        logger.info("Policy analysis successful via YOUR model")
        return result

    except Exception as e:
        logger.error(f"Policy analysis failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to analyze policy requirements"
        }
```

---

## THE CONTRACT: WHAT YOU MUST MATCH

### Compensation Server

**Your Input (What Main App Sends):**
```python
{
    "origin_location": "New York, USA",        # String
    "destination_location": "London, UK",      # String
    "current_salary": 100000.0,                # Float
    "currency": "USD",                         # String (USD, GBP, EUR, JPY, etc.)
    "assignment_duration": "24 months",        # String
    "job_level": "Senior Engineer",            # String
    "family_size": 3,                          # Integer
    "housing_preference": "Company-provided"   # String
}
```

**Your Output (What Main App Expects):**
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
    "Consider housing allowance adjustments",
    "Review tax equalization policy",
    "Quarterly compensation reviews recommended"
  ],
  "metadata": {
    "model_version": "v2.0.0",
    "timestamp": "2025-10-29T12:34:56Z",
    "methodology": "Your approach here"
  }
}
```

### Policy Server

**Your Input (What Main App Sends):**
```python
{
    "origin_country": "USA",              # String
    "destination_country": "UK",          # String
    "assignment_type": "Long-term",       # String
    "duration": "24 months",              # String
    "job_title": "Senior Engineer"        # String
}
```

**Your Output (What Main App Expects):**
```json
{
  "status": "success",
  "analysis": {
    "visa_requirements": {
      "visa_type": "Tier 2 (General) Work Visa",
      "processing_time": "3-4 weeks",
      "cost": "£610",
      "requirements": [
        "Certificate of Sponsorship",
        "English language test",
        "Financial proof (£1,270 in bank)"
      ]
    },
    "eligibility": {
      "meets_requirements": true,
      "concerns": [],
      "recommendations": ["Assignment meets all eligibility criteria"]
    },
    "compliance": {
      "origin_requirements": ["US tax clearance", "..."],
      "destination_requirements": ["UK work authorization", "..."],
      "key_considerations": ["Tax residency implications"]
    },
    "timeline": {
      "visa_application": "Week 1-3",
      "visa_approval": "Week 4-6",
      "relocation_prep": "Week 7-8",
      "start_date": "Week 9-10"
    },
    "documentation": [
      "Passport (valid 6+ months)",
      "Employment contract",
      "Educational certificates",
      "Background check",
      "Medical examination results",
      "Tax clearance certificate"
    ]
  },
  "recommendations": [
    "Start visa process 4 months before planned start date",
    "Engage immigration counsel for complex cases",
    "Review tax implications with international tax team"
  ],
  "confidence": 0.85
}
```

---

## DEPLOYMENT: YOUR DOCKERFILE

Both teams get a Dockerfile. You modify requirements.txt to include your dependencies:

**Dockerfile.compensation (for Compensation Team):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY compensation_server.py .
COPY .env* ./

# Add your model files
COPY models/ ./models/

EXPOSE 8081

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

CMD ["uvicorn", "compensation_server:app", "--host", "0.0.0.0", "--port", "8081"]
```

**Updated requirements.txt (Compensation Team):**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
openai==1.3.7
python-dotenv==1.0.0
httpx==0.25.2

# YOUR DEPENDENCIES BELOW
scikit-learn==1.3.2
xgboost==2.0.0
pandas==2.1.1
joblib==1.3.2
numpy==1.24.3
```

---

## TESTING YOUR IMPLEMENTATION

### Local Testing (Docker)

```bash
# Start your server
docker-compose up --build compensation-server -d

# Wait for startup
sleep 5

# Check health
curl http://localhost:8081/health
# Expected: {"status":"healthy","service":"compensation_predictor"}

# View interactive docs
open http://localhost:8081/docs
# Try the /predict endpoint with test data

# Test with curl
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origin_location": "New York, USA",
    "destination_location": "London, UK",
    "current_salary": 100000,
    "currency": "USD",
    "assignment_duration": "24 months",
    "job_level": "Manager",
    "family_size": 1,
    "housing_preference": "Company-provided"
  }'

# Expected response:
{
  "status": "success",
  "predictions": {
    "total_package": 145000.00,
    "base_salary": 100000.00,
    "currency": "USD",
    "cola_ratio": 1.15
  },
  ...
}
```

### Performance Requirements

- Response time: < 2 seconds (p95)
- Concurrent requests: 10+
- Availability: 99%
- Error rate: < 1%

### Error Handling

If your model can't make a prediction:

```python
# Return error, main app falls back to GPT-4
return {
    "status": "error",
    "error": "Model requires origin_location",
    "error_code": "MISSING_REQUIRED_FIELD"
}
```

---

## INTEGRATION TESTING (When You Hand Over)

We'll test:

1. **Health Checks**
   - `curl http://localhost:8081/health` returns 200
   - `curl http://localhost:8082/health` returns 200

2. **Direct API Calls**
   - Send sample request
   - Verify response matches schema
   - Check confidence scores are reasonable

3. **Full User Flow**
   - User logs in
   - User asks compensation question
   - Input collector gathers data
   - Service manager calls your endpoint
   - Response displays correctly in UI

4. **Fallback Testing**
   - Stop your server
   - Ask a question
   - Should fall back to GPT-4 (not error)

5. **Load Testing**
   - Send 10 concurrent requests
   - All should respond < 2 seconds
   - No timeouts or errors

---

## COMMON PITFALLS TO AVOID

### 1. Wrong Response Format
**WRONG:**
```json
{
  "total_package": 145000,
  "status": "ok"
}
```

**RIGHT:**
```json
{
  "status": "success",
  "predictions": {
    "total_package": 145000,
    ...
  },
  "breakdown": {...},
  "confidence_scores": {...}
}
```

### 2. Port Conflicts
- **Compensation MUST be port 8081**
- **Policy MUST be port 8082**
- Don't change these!

### 3. Missing Endpoints
- **Compensation needs:** `/health` (GET) and `/predict` (POST)
- **Policy needs:** `/health` (GET) and `/analyze` (POST)
- Don't rename these!

### 4. Slow Responses
- Target: < 2 seconds per request
- If model is slow, optimize model loading (load once on startup)
- Use model caching if possible

### 5. Not Handling Missing Inputs
- Don't crash if you get unexpected input
- Return error with status="error"
- Let main app fallback to GPT-4

---

## SUPPORT & HANDOFF

### Before You Start
- Read HANDOFF_README.md (services/mcp_prediction_server/)
- Read this document (TEAM_INTEGRATION_GUIDE.md)
- Review the contract (MCP_CONTRACT.md)

### During Implementation
- Test locally with docker-compose
- Use interactive docs (/docs endpoint)
- Test with curl
- Check logs with `docker-compose logs compensation-server`

### When You're Done
Send us:
1. Your Docker image (or Dockerfile + requirements.txt)
2. Your model files (if needed)
3. Brief explanation of your approach
4. Performance metrics from your testing
5. Known limitations or special configuration

### Questions?
Contact: [Your Engineering Team]

---

## SUMMARY: YOUR 3-STEP PROCESS

### Step 1: Understand the Contract (30 minutes)
- Read this guide
- Review the request/response format
- Test the placeholder with docker-compose up

### Step 2: Implement Your Model (Days/Weeks)
- Replace OpenAI calls with your model
- Preprocess inputs → run model → format output
- Update requirements.txt with your dependencies
- Test locally

### Step 3: Hand Over (1 hour)
- Build Docker image
- Document your approach
- Provide requirements.txt
- Submit for integration testing

**You interact with us only through the HTTP API. We handle the rest.**


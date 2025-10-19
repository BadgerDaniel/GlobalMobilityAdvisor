# Quick Start Guide - AGNO MCP Integration

## TL;DR

Transform Global IQ from **LLM-only** to **hybrid AI system** with real prediction models using AGNO MCP.

---

## Current vs. Target Architecture

### **Current (LLM-Only)**
```
User → Chainlit → LangChain Router → GPT-4 → Text Response
```

**Problems:**
- No real predictions (just text generation)
- No confidence scores
- Can't integrate external data
- Everything tied to OpenAI

### **Target (Hybrid with MCP)**
```
User → Chainlit → MCP Gateway → ML Services → Structured Predictions
                                     ↓
                              External APIs (Currency, COLA, Visas)
```

**Benefits:**
- Real ML predictions with confidence scores
- Live external data integration
- Scalable, independent services
- Fallback to LLM if needed

---

## 3 Implementation Options

### **Option 1: Quick Prototype (Recommended to Start)**
**Timeline:** 1-2 weeks  
**Effort:** Low  
**Approach:** Wrap existing LLM logic in MCP services

```bash
# 1. Setup MCP Gateway
pip install agno-mcp
agno-mcp init --template basic

# 2. Create simple Flask service wrapping your LLM
# services/compensation_predictor/app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    # Call your existing _run_compensation_calculation logic
    result = calculate_compensation(data)
    return jsonify(result)

# 3. Update Chainlit to call MCP instead of direct LLM
# app/main.py
from mcp_client import MCPClient
mcp = MCPClient(gateway_url="http://localhost:8080")

async def _run_compensation_calculation(data, docs):
    response = mcp.predict_compensation(**data)
    return format_response(response)
```

**Pros:**
- Fast to implement
- Proves architecture works
- Easy rollback

**Cons:**
- Still using LLM (no real ML yet)
- No significant accuracy improvement

---

### **Option 2: Train Simple ML Models**
**Timeline:** 4-6 weeks  
**Effort:** Medium  
**Approach:** Train basic regression models for COLA, salary, housing

**Requirements:**
- Historical compensation data (at least 1000 records)
- City-to-city cost of living data
- Housing price datasets

```python
# Example: Train COLA predictor
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Load your data
df = pd.read_csv("historical_relocations.csv")

# Features: origin_city_id, dest_city_id, salary, job_level, family_size
X = df[['origin_id', 'dest_id', 'salary', 'job_level_encoded', 'family_size']]
y = df['cola_adjustment']  # Target: actual COLA given

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Save for deployment
import joblib
joblib.dump(model, 'models/cola_predictor.pkl')

# In your service:
model = joblib.load('models/cola_predictor.pkl')
prediction = model.predict(features)
```

**Pros:**
- Real ML predictions
- Better accuracy than LLM
- Confidence scores available

**Cons:**
- Requires data collection
- More complex deployment
- Need model monitoring

---

### **Option 3: Full Production System**
**Timeline:** 3-4 months  
**Effort:** High  
**Approach:** Complete ML pipeline with monitoring, versioning, A/B testing

**Includes:**
- Multiple trained models (COLA, salary, housing, visa timeline)
- Model versioning (MLflow or similar)
- A/B testing framework
- Monitoring dashboard (Grafana)
- Real-time external API integration
- Auto-retraining pipeline

**For when you're ready to scale seriously.**

---

## Recommended Path

### **Week 1-2: Proof of Concept**

#### Step 1: Install MCP Framework
```bash
cd Global-IQ/Global-iq-application

# Install MCP (adjust based on actual package)
pip install agno-mcp

# Or clone custom repo
git clone https://github.com/your-org/agno-mcp.git
cd agno-mcp && pip install -e .
```

#### Step 2: Create MCP Gateway Config
Create `mcp_config.yaml`:
```yaml
gateway:
  host: "localhost"
  port: 8080

services:
  - name: "compensation_predictor"
    endpoint: "http://localhost:8081/predict"
    timeout: 5000
    
  - name: "policy_analyzer"
    endpoint: "http://localhost:8082/analyze"
    timeout: 3000

logging:
  level: "INFO"
```

#### Step 3: Create Simple Prediction Service
`services/compensation_predictor/app.py`:
```python
from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/predict", methods=["POST"])
def predict_compensation():
    """
    For now, just wrap your existing LLM logic.
    Later, replace with real ML model.
    """
    data = request.json
    
    # Use your existing calculation prompt
    prompt = f"""Calculate compensation for:
    Origin: {data['origin_city']}
    Destination: {data['destination_city']}
    Salary: {data['current_salary']}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Structure the response
    result = {
        "predictions": {
            "total_package": 125000,  # Parse from LLM response
            "currency": "USD"
        },
        "confidence": {
            "overall": 0.85
        },
        "metadata": {
            "model_version": "llm-wrapper-v1.0",
            "timestamp": "2025-10-15T10:30:00Z"
        }
    }
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
```

#### Step 4: Create MCP Client in Chainlit
`app/mcp_client.py`:
```python
import requests
import os

class MCPClient:
    def __init__(self):
        self.gateway_url = os.getenv("MCP_GATEWAY_URL", "http://localhost:8080")
    
    def predict_compensation(self, origin_city, destination_city, 
                            current_salary, **kwargs):
        response = requests.post(
            f"{self.gateway_url}/api/v1/services/compensation_predictor/predict",
            json={
                "origin_city": origin_city,
                "destination_city": destination_city,
                "current_salary": current_salary,
                **kwargs
            },
            timeout=10
        )
        return response.json()
```

#### Step 5: Update Main.py
In `app/main.py`, modify:
```python
from mcp_client import MCPClient

mcp_client = MCPClient()

async def _run_compensation_calculation(collected_data, extracted_texts):
    """Now using MCP instead of direct LLM call."""
    try:
        # Extract data
        origin = collected_data.get("Origin Location", "")
        destination = collected_data.get("Destination Location", "")
        salary = parse_salary(collected_data.get("Current Compensation", "0"))
        
        # Call MCP service
        mcp_response = mcp_client.predict_compensation(
            origin_city=origin,
            destination_city=destination,
            current_salary=salary
        )
        
        # Format response
        predictions = mcp_response["predictions"]
        result = f"[RESULTS] Total Package: {predictions['total_package']:,.0f} {predictions['currency']}\n"
        result += f"\nModel Version: {mcp_response['metadata']['model_version']}"
        
        return result
        
    except Exception as e:
        # Fallback to original LLM method
        print(f"MCP failed: {e}, falling back to LLM")
        return await _run_compensation_calculation_original(collected_data, extracted_texts)
```

#### Step 6: Test Locally
```bash
# Terminal 1: Start prediction service
cd services/compensation_predictor
python app.py

# Terminal 2: Start MCP Gateway
agno-mcp start --config mcp_config.yaml

# Terminal 3: Start Chainlit app
cd Global-IQ/Global-iq-application
export MCP_GATEWAY_URL="http://localhost:8080"
chainlit run app/main.py

# Terminal 4: Test
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origin_city": "New York",
    "destination_city": "London",
    "current_salary": 100000
  }'
```

---

### **Week 3-4: Add Real Data Sources**

Once basic MCP works, enhance with external APIs:

```python
# In your prediction service
import requests

def get_cola_from_numbeo(origin, destination):
    """Get real cost of living data."""
    response = requests.get(
        "https://www.numbeo.com/api/city_prices",
        params={
            "api_key": os.getenv("NUMBEO_API_KEY"),
            "from": origin,
            "to": destination
        }
    )
    return response.json()["cola_ratio"]

def get_exchange_rate(from_currency, to_currency):
    """Get live exchange rates."""
    response = requests.get(
        f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    )
    return response.json()["rates"][to_currency]

@app.route("/predict", methods=["POST"])
def predict_compensation():
    data = request.json
    
    # Get real data
    cola_ratio = get_cola_from_numbeo(data["origin_city"], data["destination_city"])
    exchange_rate = get_exchange_rate("USD", "GBP")
    
    # Calculate
    adjusted_salary = data["current_salary"] * cola_ratio
    
    return jsonify({
        "predictions": {
            "adjusted_salary": adjusted_salary,
            "exchange_rate": exchange_rate
        },
        "data_sources": ["Numbeo", "ExchangeRate-API"]
    })
```

---

### **Week 5-8: Train Initial ML Models**

If you have data, start training:

```python
# train_cola_model.py
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

# Load historical data
df = pd.read_csv("data/historical_relocations.csv")

# Encode cities
city_encoder = LabelEncoder()
df['origin_encoded'] = city_encoder.fit_transform(df['origin_city'])
df['dest_encoded'] = city_encoder.transform(df['destination_city'])

# Features
X = df[['origin_encoded', 'dest_encoded', 'base_salary', 'job_level', 'family_size']]
y = df['cola_adjustment']

# Train
model = GradientBoostingRegressor(n_estimators=200, max_depth=5)
model.fit(X, y)

# Save
joblib.dump(model, 'models/cola_predictor.pkl')
joblib.dump(city_encoder, 'models/city_encoder.pkl')

print(f"Model R² score: {model.score(X, y):.3f}")
```

Replace LLM wrapper in service:
```python
import joblib

# Load trained model
model = joblib.load('models/cola_predictor.pkl')
city_encoder = joblib.load('models/city_encoder.pkl')

@app.route("/predict", methods=["POST"])
def predict_compensation():
    data = request.json
    
    # Encode inputs
    origin_id = city_encoder.transform([data["origin_city"]])[0]
    dest_id = city_encoder.transform([data["destination_city"]])[0]
    
    # Predict
    features = [[origin_id, dest_id, data["current_salary"], 
                 data["job_level_id"], data["family_size"]]]
    cola = model.predict(features)[0]
    
    return jsonify({
        "predictions": {
            "cola_adjustment": float(cola),
            "adjusted_salary": data["current_salary"] * (1 + cola)
        },
        "confidence": {
            "cola": 0.87  # Can calculate from model ensemble
        },
        "metadata": {
            "model_version": "gb-v1.0",
            "model_type": "GradientBoostingRegressor"
        }
    })
```

---

## Docker Deployment (Once Stable)

Create `docker-compose.mcp.yml`:
```yaml
version: '3.8'

services:
  mcp-gateway:
    image: agno-mcp/gateway:latest
    ports:
      - "8080:8080"
    environment:
      - MCP_CONFIG=/config/mcp_config.yaml
    volumes:
      - ./mcp_config.yaml:/config/mcp_config.yaml

  compensation-predictor:
    build: ./services/compensation_predictor
    ports:
      - "8081:8081"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NUMBEO_API_KEY=${NUMBEO_API_KEY}

  policy-analyzer:
    build: ./services/policy_analyzer
    ports:
      - "8082:8082"

  global-iq-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MCP_GATEWAY_URL=http://mcp-gateway:8080
    depends_on:
      - mcp-gateway
```

Deploy:
```bash
docker-compose -f docker-compose.mcp.yml up -d
```

---

## Monitoring & Debugging

### Check Service Health
```bash
# Gateway
curl http://localhost:8080/health

# Compensation service
curl http://localhost:8081/health

# Policy service
curl http://localhost:8082/health
```

### View Logs
```bash
# Gateway logs
docker logs mcp-gateway -f

# Service logs
docker logs compensation-predictor -f
```

### Test Individual Service
```bash
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origin_city": "San Francisco, USA",
    "destination_city": "Tokyo, Japan",
    "current_salary": 120000,
    "currency": "USD",
    "job_level": "Senior Engineer",
    "family_size": 2
  }' | jq .
```

---

## Common Issues & Solutions

### Issue 1: MCP Gateway Not Starting
```bash
# Check config syntax
agno-mcp validate --config mcp_config.yaml

# Check logs
agno-mcp start --config mcp_config.yaml --log-level DEBUG
```

### Issue 2: Service Connection Timeout
```bash
# Increase timeout in mcp_config.yaml
services:
  - name: "compensation_predictor"
    timeout: 10000  # 10 seconds instead of 5
```

### Issue 3: Model Loading Errors
```python
# Add error handling in service
try:
    model = joblib.load('models/cola_predictor.pkl')
except Exception as e:
    print(f"Model load failed: {e}")
    # Use fallback logic
```

---

## Next Actions

1. **Today**: Read full integration plan (`AGNO_MCP_INTEGRATION_PLAN.md`)
2. **This Week**: 
   - Install MCP framework
   - Create simple Flask service wrapping LLM
   - Test locally
3. **Next Week**:
   - Add MCP client to Chainlit
   - Test end-to-end flow
   - Deploy with Docker
4. **Month 2+**:
   - Collect historical data
   - Train ML models
   - Replace LLM wrappers with real models
   - Add monitoring

---

## Questions?

Review these documents:
- **Detailed Plan**: `AGNO_MCP_INTEGRATION_PLAN.md` (full technical details)
- **Project Overview**: `PROJECT_OVERVIEW.md` (system architecture)
- **Technical Summary**: `TECHNICAL_SUMMARY.txt` (current implementation)

Ready to start? Begin with **Option 1: Quick Prototype** above!


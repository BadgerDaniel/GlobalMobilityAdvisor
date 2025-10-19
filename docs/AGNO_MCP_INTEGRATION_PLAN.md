 # Global IQ Project Breakdown & AGNO MCP Integration Plan

## Executive Summary

The **Global IQ Mobility Advisor** is a Chainlit-based AI application that helps HR professionals and employees with global mobility decisions. It provides intelligent routing between policy analysis and compensation calculations through an LLM-powered router system.

This document outlines how to integrate **AGNO MCP (Model Context Protocol)** to prepare endpoints for connecting to prediction models, enabling the system to scale beyond simple LLM routing to include sophisticated ML-based predictions for compensation, cost-of-living, and policy recommendations.

---

## Current System Architecture

### 1. **Core Components**

#### **A. Authentication & Authorization** (`main.py`)
- **Role-Based Access Control (RBAC)**: 4 user roles
  - `admin` - Full system access
  - `hr_manager` - HR professional access
  - `employee` - Standard user access
  - `demo` - Demo/exploration access
- **Password hashing**: SHA-256
- **Session management**: User context stored in Chainlit sessions

#### **B. Intelligent Agent Router** (`enhanced_agent_router.py`)
- **Uses LangChain** with OpenAI GPT-4 for query routing
- **4 Route Destinations**:
  1. **Policy Route** - Immigration, visas, compliance, regulations
  2. **Compensation Route** - Salary, allowances, cost calculations
  3. **Both Policy & Compensation** - Complex scenarios requiring both
  4. **Guidance Fallback** - General help and unclear queries

- **Routing Methods**:
  - Direct keyword matching (simple queries)
  - LLM-based semantic routing (complex queries)
  - Keyword scoring with threshold-based decision

#### **C. Input Collection System** (`input_collector.py`)
- **Sequential Q&A System**: Collects structured data from users
- **Configuration-Driven**: Questions loaded from text files
- **AI-Powered Spell Checking**: Uses GPT-4o-mini for input validation
- **Multi-Step Confirmation**: Review → Confirm → Process workflow

#### **D. File Processing** (`main.py`)
- **Supported Formats**: PDF, DOCX, TXT, CSV, JSON, XLSX
- **Libraries Used**:
  - PyMuPDF (fitz) for PDFs
  - python-docx for Word documents
  - openpyxl for Excel files
- **Context Integration**: Extracted text is added to LLM prompts

#### **E. Calculation/Analysis Engines** (`main.py`)
- **Compensation Calculator**: `_run_compensation_calculation()`
  - Takes collected user data + uploaded documents
  - Generates salary adjustments, COLA, housing allowances, tax implications
  
- **Policy Analyzer**: `_run_policy_analysis()`
  - Analyzes eligibility, visa requirements, compliance
  - Provides structured policy guidance

---

## Current Limitations & Opportunities for AGNO MCP

### **Current Limitations**

1. **No Real Prediction Models**: Calculations are purely LLM-based text generation
   - No trained ML models for cost-of-living predictions
   - No historical data-driven compensation recommendations
   - No statistical confidence intervals or uncertainty quantification

2. **No Model Versioning**: No way to track or compare different model versions

3. **Limited Scalability**: All computations happen in-line, no async model serving

4. **No Real-Time Data Integration**: Can't pull live exchange rates, inflation data, housing costs

5. **No Analytics**: No tracking of prediction accuracy, user satisfaction, or model performance

6. **Hardcoded Logic**: Routing and analysis logic is embedded in code

---

## AGNO MCP Integration Architecture

### **What is AGNO MCP?**

**AGNO (Autonomous General Network Orchestration)** with **MCP (Model Context Protocol)** is a framework for:
- **Model Serving**: Deploy ML models as microservices with standardized APIs
- **Context Management**: Maintain conversation and user context across requests
- **Protocol Standardization**: Uniform interface for diverse prediction models
- **Orchestration**: Coordinate multiple models, data sources, and services

### **Why Use AGNO MCP for Global IQ?**

1. **Separate Concerns**: Decouple business logic (Chainlit app) from prediction logic (ML models)
2. **Scalability**: Run prediction models as independent services
3. **Flexibility**: Swap models without changing application code
4. **Monitoring**: Track model performance, latency, errors
5. **Real-Time Data**: Integrate external APIs (currency, cost-of-living, visa databases)

---

## Proposed Integration Design

### **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chainlit Application (Frontend)              │
│  - User Authentication                                          │
│  - File Upload & Processing                                     │
│  - Conversation Management                                      │
│  - Input Collection                                             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP/REST API Calls
                 │
┌────────────────▼────────────────────────────────────────────────┐
│              AGNO MCP Gateway (API Layer)                       │
│  - Request Routing                                              │
│  - Authentication & Rate Limiting                               │
│  - Context Management (Session State)                           │
│  - Response Aggregation                                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
         ┌───────┴───────┬────────────┬──────────────┐
         │               │            │              │
         ▼               ▼            ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────┐
│ Compensation│  │   Policy    │  │  Router  │  │  External    │
│   Predict   │  │   Predict   │  │  Model   │  │  Data APIs   │
│   Service   │  │   Service   │  │  Service │  │  - Currency  │
│             │  │             │  │          │  │  - COLA DB   │
│  - COLA     │  │ - Visa Req. │  │ - Intent │  │  - Housing   │
│  - Salary   │  │ - Eligibil. │  │  Classif │  │              │
│  - Housing  │  │ - Timeline  │  │          │  │              │
└─────────────┘  └─────────────┘  └──────────┘  └──────────────┘
```

---

## Step-by-Step Integration Plan

### **Phase 1: Setup AGNO MCP Infrastructure**

#### **1.1 Install AGNO MCP Framework**

```bash
pip install agno-mcp  # Hypothetical package name
# OR if AGNO MCP is custom:
git clone https://github.com/your-org/agno-mcp.git
cd agno-mcp
pip install -e .
```

#### **1.2 Create MCP Configuration**

Create `mcp_config.yaml`:

```yaml
gateway:
  host: "localhost"
  port: 8080
  api_version: "v1"
  auth:
    enabled: true
    method: "bearer_token"
    secret_key: "${MCP_SECRET_KEY}"

services:
  - name: "compensation_predictor"
    endpoint: "http://localhost:8081/predict"
    type: "ml_model"
    timeout: 5000  # milliseconds
    retry: 3
    
  - name: "policy_analyzer"
    endpoint: "http://localhost:8082/analyze"
    type: "ml_model"
    timeout: 3000
    retry: 2
    
  - name: "router_classifier"
    endpoint: "http://localhost:8083/classify"
    type: "ml_model"
    timeout: 1000
    retry: 2
    
  - name: "external_data"
    endpoint: "http://localhost:8084/data"
    type: "data_source"
    timeout: 2000
    retry: 1

context:
  storage: "redis"  # Or "memory", "postgres"
  ttl: 3600  # 1 hour session timeout
  
logging:
  level: "INFO"
  format: "json"
  destination: "file"
  file_path: "./logs/mcp.log"
```

#### **1.3 Start AGNO MCP Gateway**

```bash
# Terminal 1: Start the MCP Gateway
agno-mcp start --config mcp_config.yaml

# OR if custom implementation:
python -m agno_mcp.gateway --config mcp_config.yaml
```

---

### **Phase 2: Build Prediction Model Services**

#### **2.1 Compensation Prediction Service**

Create `services/compensation_predictor/app.py`:

```python
from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
from agno_mcp.service import MCPService

app = Flask(__name__)
mcp_service = MCPService(service_name="compensation_predictor")

# Load your trained ML models
cola_model = joblib.load("models/cola_predictor.pkl")
salary_model = joblib.load("models/salary_adjuster.pkl")
housing_model = joblib.load("models/housing_allowance.pkl")

@app.route("/predict", methods=["POST"])
@mcp_service.endpoint()  # MCP decorator for logging, auth, etc.
def predict_compensation():
    """
    Endpoint for compensation prediction.
    
    Expected Input:
    {
        "origin_city": "New York, USA",
        "destination_city": "London, UK",
        "current_salary": 100000,
        "currency": "USD",
        "assignment_duration": "12 months",
        "job_level": "Senior Manager",
        "family_size": 3,
        "context": {  # Optional: from user session
            "user_preferences": {...},
            "uploaded_docs": [...]
        }
    }
    
    Returns:
    {
        "predictions": {
            "cola_adjustment": 1.25,
            "adjusted_salary": 125000,
            "housing_allowance": 24000,
            "hardship_pay": 0,
            "total_package": 149000,
            "currency": "USD"
        },
        "confidence": {
            "cola": 0.87,
            "salary": 0.92,
            "housing": 0.78
        },
        "breakdown": {
            "base_salary": 100000,
            "cola_increase": 25000,
            "housing": 24000,
            "other": 0
        },
        "metadata": {
            "model_version": "v2.3.1",
            "data_sources": ["WorldBank", "Numbeo", "Internal HR Data"],
            "timestamp": "2025-10-15T10:30:00Z"
        }
    }
    """
    try:
        data = request.json
        
        # Extract features
        origin = data.get("origin_city")
        destination = data.get("destination_city")
        salary = data.get("current_salary", 0)
        currency = data.get("currency", "USD")
        duration = data.get("assignment_duration", "12 months")
        job_level = data.get("job_level", "Manager")
        family_size = data.get("family_size", 1)
        
        # Feature engineering (example)
        features = prepare_features(origin, destination, salary, job_level, family_size)
        
        # Run predictions
        cola = cola_model.predict(features)[0]
        adjusted_salary = salary_model.predict(features)[0]
        housing = housing_model.predict(features)[0]
        
        # Calculate confidence scores (from model probabilities or ensembles)
        confidence = {
            "cola": float(cola_model.predict_proba(features).max()),
            "salary": 0.92,  # Example
            "housing": 0.78
        }
        
        # Build response
        response = {
            "predictions": {
                "cola_adjustment": float(cola),
                "adjusted_salary": float(adjusted_salary),
                "housing_allowance": float(housing),
                "hardship_pay": 0.0,
                "total_package": float(adjusted_salary + housing),
                "currency": currency
            },
            "confidence": confidence,
            "breakdown": {
                "base_salary": salary,
                "cola_increase": float(adjusted_salary - salary),
                "housing": float(housing),
                "other": 0
            },
            "metadata": {
                "model_version": "v2.3.1",
                "data_sources": ["WorldBank", "Numbeo", "Internal HR Data"],
                "timestamp": pd.Timestamp.now().isoformat()
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def prepare_features(origin, destination, salary, job_level, family_size):
    """Convert inputs into model features."""
    # Example feature engineering
    # In reality, you'd use embeddings, lookups, etc.
    features = np.array([[
        hash(origin) % 1000,
        hash(destination) % 1000,
        salary / 100000,
        {"Junior": 1, "Manager": 2, "Senior Manager": 3}.get(job_level, 2),
        family_size
    ]])
    return features

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
```

**Create `services/compensation_predictor/Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8081

CMD ["python", "app.py"]
```

**Create `services/compensation_predictor/requirements.txt`:**

```
flask==3.0.0
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.26.2
joblib==1.3.2
agno-mcp>=1.0.0  # Your MCP SDK
```

---

#### **2.2 Policy Analyzer Service**

Create `services/policy_analyzer/app.py`:

```python
from flask import Flask, request, jsonify
from agno_mcp.service import MCPService
import requests

app = Flask(__name__)
mcp_service = MCPService(service_name="policy_analyzer")

# External APIs or databases
VISA_API_URL = "https://api.visa-requirements.io/v1/check"
POLICY_DB_URL = "http://internal-policy-db:5000/query"

@app.route("/analyze", methods=["POST"])
@mcp_service.endpoint()
def analyze_policy():
    """
    Endpoint for policy analysis.
    
    Expected Input:
    {
        "origin_country": "USA",
        "destination_country": "UK",
        "assignment_type": "Long-term assignment",
        "duration": "24 months",
        "job_title": "Senior Software Engineer",
        "context": {...}
    }
    
    Returns:
    {
        "analysis": {
            "visa_requirements": {
                "visa_type": "Tier 2 (General) Work Visa",
                "processing_time": "3 weeks",
                "cost": "£610",
                "requirements": ["Certificate of Sponsorship", "English test", "Financial proof"]
            },
            "eligibility": {
                "meets_requirements": true,
                "concerns": [],
                "recommendations": ["Start visa process 4 months before travel"]
            },
            "compliance": {
                "tax_implications": "UK tax resident after 183 days",
                "social_security": "Totalization agreement applies",
                "work_permits": "Required"
            },
            "timeline": {
                "visa_application": "Week 1-3",
                "approval_wait": "Week 4-6",
                "relocation": "Week 8-10"
            }
        },
        "metadata": {
            "policy_version": "2024.Q4",
            "last_updated": "2024-10-01",
            "data_sources": ["UK Home Office", "Internal HR Policy"]
        }
    }
    """
    try:
        data = request.json
        
        origin = data.get("origin_country")
        destination = data.get("destination_country")
        assignment_type = data.get("assignment_type")
        duration = data.get("duration")
        job_title = data.get("job_title")
        
        # Query external visa API
        visa_info = query_visa_requirements(origin, destination)
        
        # Query internal policy database
        policy_info = query_internal_policies(assignment_type, duration)
        
        # Build response
        response = {
            "analysis": {
                "visa_requirements": visa_info,
                "eligibility": {
                    "meets_requirements": True,
                    "concerns": [],
                    "recommendations": ["Start visa process 4 months before travel"]
                },
                "compliance": policy_info.get("compliance", {}),
                "timeline": policy_info.get("timeline", {})
            },
            "metadata": {
                "policy_version": "2024.Q4",
                "last_updated": "2024-10-01",
                "data_sources": ["UK Home Office", "Internal HR Policy"]
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def query_visa_requirements(origin, destination):
    """Query external visa API."""
    try:
        response = requests.get(
            VISA_API_URL,
            params={"from": origin, "to": destination},
            timeout=2
        )
        return response.json()
    except:
        return {"visa_type": "Unknown", "processing_time": "Varies"}

def query_internal_policies(assignment_type, duration):
    """Query internal policy database."""
    try:
        response = requests.post(
            POLICY_DB_URL,
            json={"type": assignment_type, "duration": duration},
            timeout=2
        )
        return response.json()
    except:
        return {"compliance": {}, "timeline": {}}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
```

---

#### **2.3 Router Classifier Service (Optional)**

Create `services/router_classifier/app.py`:

```python
from flask import Flask, request, jsonify
from transformers import pipeline
from agno_mcp.service import MCPService

app = Flask(__name__)
mcp_service = MCPService(service_name="router_classifier")

# Load fine-tuned classification model
classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"  # Replace with your model
)

INTENT_LABELS = {
    "LABEL_0": "policy",
    "LABEL_1": "compensation",
    "LABEL_2": "both_policy_and_compensation",
    "LABEL_3": "guidance_fallback"
}

@app.route("/classify", methods=["POST"])
@mcp_service.endpoint()
def classify_intent():
    """
    Classify user intent for routing.
    
    Input:
    {
        "query": "How much will I earn in London?"
    }
    
    Output:
    {
        "intent": "compensation",
        "confidence": 0.94,
        "alternatives": [
            {"intent": "both_policy_and_compensation", "confidence": 0.05},
            {"intent": "policy", "confidence": 0.01}
        ]
    }
    """
    try:
        data = request.json
        query = data.get("query", "")
        
        # Run classification
        result = classifier(query, return_all_scores=True)[0]
        
        # Sort by confidence
        sorted_results = sorted(result, key=lambda x: x["score"], reverse=True)
        
        response = {
            "intent": INTENT_LABELS.get(sorted_results[0]["label"], "guidance_fallback"),
            "confidence": sorted_results[0]["score"],
            "alternatives": [
                {
                    "intent": INTENT_LABELS.get(r["label"], "unknown"),
                    "confidence": r["score"]
                }
                for r in sorted_results[1:]
            ]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)
```

---

### **Phase 3: Modify Global IQ Chainlit App to Use MCP**

#### **3.1 Create MCP Client**

Create `app/mcp_client.py`:

```python
import os
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with AGNO MCP Gateway."""
    
    def __init__(self, gateway_url: str = None, api_key: str = None):
        self.gateway_url = gateway_url or os.getenv("MCP_GATEWAY_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("MCP_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
    
    def predict_compensation(
        self,
        origin_city: str,
        destination_city: str,
        current_salary: float,
        currency: str = "USD",
        assignment_duration: str = "12 months",
        job_level: str = "Manager",
        family_size: int = 1,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Call the compensation prediction service.
        
        Returns:
            Dictionary with predictions, confidence scores, and metadata
        """
        try:
            payload = {
                "origin_city": origin_city,
                "destination_city": destination_city,
                "current_salary": current_salary,
                "currency": currency,
                "assignment_duration": assignment_duration,
                "job_level": job_level,
                "family_size": family_size,
                "context": context or {}
            }
            
            response = requests.post(
                f"{self.gateway_url}/api/v1/services/compensation_predictor/predict",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP compensation prediction failed: {e}")
            raise
    
    def analyze_policy(
        self,
        origin_country: str,
        destination_country: str,
        assignment_type: str,
        duration: str,
        job_title: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Call the policy analysis service.
        
        Returns:
            Dictionary with policy analysis, requirements, and recommendations
        """
        try:
            payload = {
                "origin_country": origin_country,
                "destination_country": destination_country,
                "assignment_type": assignment_type,
                "duration": duration,
                "job_title": job_title,
                "context": context or {}
            }
            
            response = requests.post(
                f"{self.gateway_url}/api/v1/services/policy_analyzer/analyze",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP policy analysis failed: {e}")
            raise
    
    def classify_intent(self, query: str) -> Dict[str, Any]:
        """
        Call the router classification service.
        
        Returns:
            Dictionary with intent classification and confidence
        """
        try:
            payload = {"query": query}
            
            response = requests.post(
                f"{self.gateway_url}/api/v1/services/router_classifier/classify",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP intent classification failed: {e}")
            # Fallback to existing LLM routing
            return None
    
    def health_check(self) -> bool:
        """Check if MCP Gateway is healthy."""
        try:
            response = requests.get(
                f"{self.gateway_url}/health",
                headers=self.headers,
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
```

---

#### **3.2 Update Compensation Calculation to Use MCP**

Modify `app/main.py`:

```python
from mcp_client import MCPClient

# Initialize MCP Client
mcp_client = MCPClient()

async def _run_compensation_calculation(collected_data: dict, extracted_texts: list) -> str:
    """
    Enhanced compensation calculation using MCP prediction service.
    Falls back to LLM if MCP is unavailable.
    """
    try:
        # Check MCP availability
        if not mcp_client.health_check():
            logger.warning("MCP unavailable, falling back to LLM calculation")
            return await _run_compensation_calculation_llm(collected_data, extracted_texts)
        
        # Extract data from collected inputs
        origin = collected_data.get("Origin Location", "")
        destination = collected_data.get("Destination Location", "")
        salary_str = collected_data.get("Current Compensation", "0")
        
        # Parse salary (handle formats like "50k EUR", "$100,000", etc.)
        salary = parse_salary(salary_str)
        currency = extract_currency(salary_str)
        
        duration = collected_data.get("Assignment Duration", "12 months")
        job_level = collected_data.get("Job Level", "Manager")
        family_size = int(collected_data.get("Family Size", "1"))
        
        # Call MCP prediction service
        logger.info(f"Calling MCP compensation predictor for {origin} -> {destination}")
        
        mcp_response = mcp_client.predict_compensation(
            origin_city=origin,
            destination_city=destination,
            current_salary=salary,
            currency=currency,
            assignment_duration=duration,
            job_level=job_level,
            family_size=family_size,
            context={
                "collected_data": collected_data,
                "uploaded_docs": extracted_texts[:2] if extracted_texts else []
            }
        )
        
        # Format response for user
        predictions = mcp_response.get("predictions", {})
        confidence = mcp_response.get("confidence", {})
        breakdown = mcp_response.get("breakdown", {})
        metadata = mcp_response.get("metadata", {})
        
        result = f"[RESULTS] **Compensation Calculation Results**\n\n"
        result += f"**Total Estimated Package:** {predictions.get('total_package', 0):,.0f} {predictions.get('currency', currency)}\n\n"
        
        result += "**Breakdown:**\n"
        result += f"- Base Salary: {breakdown.get('base_salary', 0):,.0f} {currency}\n"
        result += f"- Cost of Living Adjustment: +{breakdown.get('cola_increase', 0):,.0f} {currency}\n"
        result += f"- Housing Allowance: +{breakdown.get('housing', 0):,.0f} {currency}\n"
        result += f"- Other Benefits: +{breakdown.get('other', 0):,.0f} {currency}\n\n"
        
        result += "**Confidence Scores:**\n"
        result += f"- Cost of Living: {confidence.get('cola', 0)*100:.1f}%\n"
        result += f"- Salary Adjustment: {confidence.get('salary', 0)*100:.1f}%\n"
        result += f"- Housing Estimate: {confidence.get('housing', 0)*100:.1f}%\n\n"
        
        result += "**Model Information:**\n"
        result += f"- Model Version: {metadata.get('model_version', 'Unknown')}\n"
        result += f"- Data Sources: {', '.join(metadata.get('data_sources', []))}\n"
        result += f"- Calculated: {metadata.get('timestamp', 'N/A')}\n\n"
        
        result += "[INFO] *This calculation is based on ML models trained on historical mobility data. "
        result += "Please consult with HR for final approval.*"
        
        return result
        
    except Exception as e:
        logger.error(f"MCP compensation calculation failed: {e}")
        # Fallback to LLM-based calculation
        return await _run_compensation_calculation_llm(collected_data, extracted_texts)

async def _run_compensation_calculation_llm(collected_data: dict, extracted_texts: list) -> str:
    """
    Original LLM-based compensation calculation as fallback.
    """
    # Original implementation from your code
    try:
        data_summary = "\n".join([f"- **{key}:** {value}" for key, value in collected_data.items()])
        
        context_info = ""
        if extracted_texts:
            context_info = "\n\nAdditional context from uploaded documents:\n"
            for item in extracted_texts:
                max_len = 1000
                truncated_content = item['content'][:max_len]
                if len(item['content']) > max_len:
                    truncated_content += "..."
                context_info += f"\n--- {item['name']} ---\n{truncated_content}\n"
        
        calc_prompt = f"""You are the Global IQ Compensation Calculator AI engine with years of mobility data and cost analysis experience.
        
Based on the following employee data, calculate a comprehensive compensation package for their international assignment:

{data_summary}{context_info}
        
Provide a detailed breakdown including:
1. Base salary adjustments
2. Cost of living adjustments
3. Housing allowances
4. Hardship pay (if applicable)
5. Tax implications
6. Total estimated package
7. Recommendations for optimization
        
Format your response professionally with clear financial breakdowns."""
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": calc_prompt}],
            temperature=0.3
        )
        
        result = f"[RESULTS] **Compensation Calculation Results (LLM Fallback)**\n\n{response.choices[0].message.content}"
        return result
        
    except Exception as e:
        return f"[ERROR] Sorry, I encountered an error during compensation calculation: {str(e)}"

def parse_salary(salary_str: str) -> float:
    """Extract numeric salary from string."""
    import re
    # Remove currency symbols and commas
    cleaned = re.sub(r'[^\d.]', '', salary_str.replace(',', ''))
    
    # Handle 'k' notation (50k = 50,000)
    if 'k' in salary_str.lower():
        return float(cleaned) * 1000
    
    return float(cleaned) if cleaned else 0.0

def extract_currency(salary_str: str) -> str:
    """Extract currency code from string."""
    currencies = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "¥": "JPY"
    }
    
    for symbol, code in currencies.items():
        if symbol in salary_str:
            return code
    
    # Check for currency codes
    import re
    match = re.search(r'\b(USD|EUR|GBP|JPY|CAD|AUD)\b', salary_str.upper())
    if match:
        return match.group(1)
    
    return "USD"  # Default
```

---

#### **3.3 Update Policy Analysis to Use MCP**

Similarly, modify `_run_policy_analysis()` in `app/main.py`:

```python
async def _run_policy_analysis(collected_data: dict, extracted_texts: list) -> str:
    """
    Enhanced policy analysis using MCP service.
    Falls back to LLM if MCP is unavailable.
    """
    try:
        # Check MCP availability
        if not mcp_client.health_check():
            logger.warning("MCP unavailable, falling back to LLM analysis")
            return await _run_policy_analysis_llm(collected_data, extracted_texts)
        
        # Extract data
        origin = collected_data.get("Origin Country", "")
        destination = collected_data.get("Destination Country", "")
        assignment_type = collected_data.get("Assignment Type", "Long-term")
        duration = collected_data.get("Duration", "12 months")
        job_title = collected_data.get("Job Title", "Manager")
        
        # Call MCP policy analysis service
        logger.info(f"Calling MCP policy analyzer for {origin} -> {destination}")
        
        mcp_response = mcp_client.analyze_policy(
            origin_country=origin,
            destination_country=destination,
            assignment_type=assignment_type,
            duration=duration,
            job_title=job_title,
            context={
                "collected_data": collected_data,
                "uploaded_docs": extracted_texts[:2] if extracted_texts else []
            }
        )
        
        # Format response
        analysis = mcp_response.get("analysis", {})
        visa = analysis.get("visa_requirements", {})
        eligibility = analysis.get("eligibility", {})
        compliance = analysis.get("compliance", {})
        timeline = analysis.get("timeline", {})
        metadata = mcp_response.get("metadata", {})
        
        result = f"[RESULTS] **Policy Analysis Results**\n\n"
        
        result += "**Visa Requirements:**\n"
        result += f"- Type: {visa.get('visa_type', 'TBD')}\n"
        result += f"- Processing Time: {visa.get('processing_time', 'Varies')}\n"
        result += f"- Cost: {visa.get('cost', 'Contact immigration')}\n"
        if visa.get('requirements'):
            result += f"- Documents Needed:\n"
            for req in visa['requirements']:
                result += f"  - {req}\n"
        result += "\n"
        
        result += "**Eligibility Assessment:**\n"
        result += f"- Meets Requirements: {'Yes' if eligibility.get('meets_requirements') else 'No'}\n"
        if eligibility.get('concerns'):
            result += "- Concerns:\n"
            for concern in eligibility['concerns']:
                result += f"  - [WARNING] {concern}\n"
        if eligibility.get('recommendations'):
            result += "- Recommendations:\n"
            for rec in eligibility['recommendations']:
                result += f"  - {rec}\n"
        result += "\n"
        
        result += "**Compliance Considerations:**\n"
        for key, value in compliance.items():
            result += f"- {key.replace('_', ' ').title()}: {value}\n"
        result += "\n"
        
        result += "**Estimated Timeline:**\n"
        for phase, timeframe in timeline.items():
            result += f"- {phase.replace('_', ' ').title()}: {timeframe}\n"
        result += "\n"
        
        result += "**Analysis Information:**\n"
        result += f"- Policy Version: {metadata.get('policy_version', 'N/A')}\n"
        result += f"- Last Updated: {metadata.get('last_updated', 'N/A')}\n"
        result += f"- Data Sources: {', '.join(metadata.get('data_sources', []))}\n\n"
        
        result += "[INFO] *This analysis is generated by ML models and external APIs. "
        result += "Please verify with legal/compliance team before finalizing plans.*"
        
        return result
        
    except Exception as e:
        logger.error(f"MCP policy analysis failed: {e}")
        return await _run_policy_analysis_llm(collected_data, extracted_texts)

async def _run_policy_analysis_llm(collected_data: dict, extracted_texts: list) -> str:
    """Original LLM-based policy analysis as fallback."""
    # Keep original implementation
    # ... (same as before)
```

---

### **Phase 4: Deployment & Orchestration**

#### **4.1 Docker Compose Setup**

Create `docker-compose.mcp.yml`:

```yaml
version: '3.8'

services:
  # AGNO MCP Gateway
  mcp-gateway:
    image: agno-mcp/gateway:latest
    ports:
      - "8080:8080"
    environment:
      - MCP_SECRET_KEY=${MCP_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./mcp_config.yaml:/etc/mcp/config.yaml
    depends_on:
      - redis
    networks:
      - mcp-network

  # Redis for session storage
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - mcp-network

  # Compensation Predictor Service
  compensation-predictor:
    build: ./services/compensation_predictor
    ports:
      - "8081:8081"
    environment:
      - MODEL_PATH=/models
    volumes:
      - ./models/compensation:/models
    networks:
      - mcp-network

  # Policy Analyzer Service
  policy-analyzer:
    build: ./services/policy_analyzer
    ports:
      - "8082:8082"
    environment:
      - VISA_API_KEY=${VISA_API_KEY}
      - POLICY_DB_URL=${POLICY_DB_URL}
    networks:
      - mcp-network

  # Router Classifier Service (Optional)
  router-classifier:
    build: ./services/router_classifier
    ports:
      - "8083:8083"
    environment:
      - MODEL_PATH=/models
    volumes:
      - ./models/router:/models
    networks:
      - mcp-network

  # Chainlit Application
  global-iq-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MCP_GATEWAY_URL=http://mcp-gateway:8080
      - MCP_API_KEY=${MCP_API_KEY}
    depends_on:
      - mcp-gateway
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

#### **4.2 Start All Services**

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export MCP_SECRET_KEY="your-secret-key"
export MCP_API_KEY="your-api-key"
export VISA_API_KEY="..."

# Start all services
docker-compose -f docker-compose.mcp.yml up -d

# Check health
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

---

## Benefits of This Architecture

### **1. Separation of Concerns**
- **Chainlit app** handles UI, authentication, file processing
- **MCP Gateway** handles routing, rate limiting, monitoring
- **Prediction services** focus solely on ML inference

### **2. Scalability**
- Scale services independently based on load
- Add more replicas of prediction services during peak times
- Cache predictions at gateway level

### **3. Flexibility**
- Swap out ML models without touching application code
- A/B test different model versions
- Add new prediction services (e.g., "travel cost estimator")

### **4. Monitoring & Observability**
- Track prediction latencies per service
- Monitor model confidence scores
- Log all requests/responses for debugging
- Alert on model degradation

### **5. Resilience**
- Graceful fallback to LLM if MCP is down
- Retry logic at gateway level
- Circuit breakers to prevent cascading failures

### **6. Real-Time Data Integration**
- Pull live currency exchange rates
- Query visa databases in real-time
- Integrate with HR systems for employee data

---

## Next Steps

### **Immediate Actions**

1. **Install AGNO MCP Framework**
   ```bash
   pip install agno-mcp  # Or custom installation
   ```

2. **Create Minimal MCP Gateway**
   - Start with single endpoint for compensation
   - Test with mock prediction service

3. **Build Simple Prediction Service**
   - Use existing LLM logic wrapped in Flask
   - Gradually replace with trained ML models

4. **Update Chainlit App**
   - Add `mcp_client.py`
   - Modify `_run_compensation_calculation()`
   - Test with local MCP gateway

5. **Deploy Locally**
   - Use `docker-compose.mcp.yml`
   - Test end-to-end flow

### **Long-Term Enhancements**

1. **Train Real ML Models**
   - Collect historical compensation data
   - Train regression models for COLA, housing, salary
   - Fine-tune classification models for routing

2. **Add More Services**
   - Travel cost estimator
   - Tax calculator
   - Housing search API integration
   - Currency exchange rate tracker

3. **Implement Monitoring**
   - Prometheus + Grafana for metrics
   - ELK stack for logs
   - Alerting on model performance

4. **Optimize Performance**
   - Model caching
   - Batch predictions
   - Async processing for long-running tasks

5. **Enhance Security**
   - OAuth2 for MCP authentication
   - Encrypt sensitive data in transit
   - Audit logging for compliance

---

## Summary

This integration plan transforms Global IQ from an **LLM-only solution** to a **hybrid AI system** leveraging:
- **LLMs** for conversational interface and fallback logic
- **ML Models** for data-driven predictions (COLA, salary, housing)
- **External APIs** for real-time data (visas, exchange rates, housing costs)
- **MCP Protocol** for orchestrating all these components seamlessly

The architecture is **modular**, **scalable**, and **resilient**, allowing you to incrementally improve each component without breaking the entire system.


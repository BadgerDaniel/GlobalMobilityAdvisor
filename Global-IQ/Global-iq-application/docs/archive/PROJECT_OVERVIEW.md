# Global IQ Mobility Advisor - Project Overview

## Quick Summary

**Global IQ** is an AI-powered HR assistant for international employee relocations. It helps:
- Calculate compensation packages (salary, COLA, housing allowances)
- Analyze mobility policies (visa requirements, compliance, eligibility)
- Process documents (PDF, DOCX, XLSX, CSV) for context
- Route queries intelligently to specialized agents

---

## Current Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend Framework** | Chainlit | Web UI for chat interface |
| **LLM** | OpenAI GPT-4 | Conversation, routing, calculations |
| **Routing** | LangChain | Intelligent query routing |
| **File Processing** | PyMuPDF, python-docx, openpyxl | Extract text from documents |
| **Authentication** | Chainlit Auth | Role-based access control |
| **Deployment** | Docker | Containerization |

---

## System Flow

```
User Login → Authenticate → Upload Files (optional) → Ask Question
                                                              |
                                                              ▼
                                          ┌─────────────────────────────────┐
                                          │   Enhanced Agent Router         │
                                          │   (LangChain + GPT-4)           │
                                          └─────────────┬───────────────────┘
                                                        |
                          ┌─────────────────────────────┼─────────────────────────────┐
                          |                             |                             |
                          ▼                             ▼                             ▼
                  ┌───────────────┐           ┌──────────────────┐          ┌────────────────┐
                  │ Policy Route  │           │ Compensation     │          │ Both / General │
                  │               │           │ Route            │          │ Route          │
                  └───────┬───────┘           └────────┬─────────┘          └────────┬───────┘
                          |                            |                              |
                          ▼                            ▼                              ▼
                  ┌───────────────┐           ┌──────────────────┐          ┌────────────────┐
                  │ Input         │           │ Input            │          │ Provide        │
                  │ Collector     │           │ Collector        │          │ Guidance       │
                  │ (Policy Qs)   │           │ (Comp Qs)        │          │                │
                  └───────┬───────┘           └────────┬─────────┘          └────────────────┘
                          |                            |
                          ▼                            ▼
                  ┌───────────────┐           ┌──────────────────┐
                  │ Policy        │           │ Compensation     │
                  │ Analysis      │           │ Calculation      │
                  │ (GPT-4)       │           │ (GPT-4)          │
                  └───────────────┘           └──────────────────┘
```

---

## Key Files & Directories

### **Application Code** (`app/`)

- **`main.py`** (678 lines)
  - Entry point
  - Authentication logic
  - File processing handlers (PDF, DOCX, XLSX, CSV, JSON, TXT)
  - Compensation & policy calculation functions
  - Chainlit event handlers (`@cl.on_chat_start`, `@cl.on_message`)

- **`enhanced_agent_router.py`** (246 lines)
  - LangChain-based query routing
  - 4 route destinations: policy, compensation, both, fallback
  - Keyword-based + LLM-based routing

- **`input_collector.py`** (375 lines)
  - Sequential Q&A system
  - Loads questions from config files
  - AI spell-check for user inputs
  - Confirmation workflow

- **`chat_history.py`** (222 lines)
  - Session-based chat history (not shown in detail, but likely handles persistence)

### **Configuration Files** (`app/agent_configs/`)

- `compensation_questions.txt` - Questions for compensation calculator
- `policy_questions.txt` - Questions for policy analyzer
- `intro_message.txt` - Welcome message
- `both_choice_message.txt` - Message when both routes needed
- `confirmation_messages.txt` - Confirmation prompts

### **Route Configuration**

- `route_config.json` - Route display info, keywords for routing

### **Deployment**

- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-container orchestration
- `deploy.sh` - Deployment script
- `requirements.txt` - Python dependencies

### **Documentation**

- `TECHNICAL_SUMMARY.txt` - Comprehensive technical overview
- `LOGIN_CREDENTIALS.md` - User credentials for demo
- `TEAM_DEPLOYMENT.md` / `TEAM_DEPLOYMENT_UPDATED.md` - Deployment guides
- `DOCKER_DEPLOYMENT.md` - Docker deployment instructions

---

## User Roles & Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Full system access, user management |
| HR Manager | `hr_manager` | `hr2024` | Policy + compensation access |
| Employee | `employee` | `employee123` | Personal relocation queries |
| Demo | `demo` | `demo` | Exploration/demo mode |

---

## Current Limitations

### **1. No Real ML Models**
- All "calculations" are LLM text generation
- No trained models for cost-of-living, salary adjustments
- No confidence scores or statistical validation

### **2. No External Data Integration**
- No live currency exchange rates
- No real-time visa/immigration databases
- No housing cost APIs

### **3. Scalability Constraints**
- All processing happens in-line (synchronous)
- No model serving infrastructure
- No caching or optimization

### **4. Monitoring Gaps**
- No model performance tracking
- No prediction accuracy metrics
- No user satisfaction feedback loop

---

## AGNO MCP Integration - High-Level Plan

### **What is AGNO MCP?**

**AGNO MCP (Model Context Protocol)** is a framework for:
- **Model Serving**: Deploy ML models as microservices
- **API Standardization**: Uniform interface for predictions
- **Context Management**: Maintain user sessions across requests
- **Orchestration**: Coordinate multiple models and data sources

### **Why Use It?**

| Current State | With AGNO MCP |
|---------------|---------------|
| LLM-only calculations | Real ML models for predictions |
| Embedded logic | Decoupled services |
| No versioning | Model version tracking |
| Single point of failure | Resilient with fallbacks |
| Limited scalability | Independent scaling per service |

### **Architecture After Integration**

```
┌──────────────────────────────────────────────────────────┐
│           Chainlit Application (Frontend)                │
│  - UI, Auth, File Processing, Conversation               │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌──────────────────────────────────────────────────────────┐
│              AGNO MCP Gateway (Orchestrator)             │
│  - Request Routing                                       │
│  - Authentication & Rate Limiting                        │
│  - Context/Session Management                            │
│  - Response Aggregation                                  │
└──────┬───────────────┬───────────────┬───────────────────┘
       │               │               │
       ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐
│Compensation│  │  Policy    │  │  Router    │  │  External    │
│ Predictor  │  │  Analyzer  │  │  Classifier│  │  Data APIs   │
│            │  │            │  │            │  │              │
│ - COLA     │  │ - Visa Req │  │ - Intent   │  │ - Currency   │
│ - Salary   │  │ - Eligibil │  │   Classif. │  │ - COLA DB    │
│ - Housing  │  │ - Timeline │  │            │  │ - Housing    │
└────────────┘  └────────────┘  └────────────┘  └──────────────┘
  (Port 8081)    (Port 8082)     (Port 8083)      (External)
```

### **Key Benefits**

1. **Real Predictions**: Replace LLM guesses with trained ML models
2. **Confidence Scores**: Get statistical confidence for each prediction
3. **Live Data**: Integrate real-time APIs (currency, housing costs, visa info)
4. **Scalability**: Scale prediction services independently
5. **Monitoring**: Track model performance, latency, accuracy
6. **A/B Testing**: Compare different model versions
7. **Resilience**: Fallback to LLM if models fail

---

## Example API Endpoints (After MCP Integration)

### **1. Compensation Prediction**

**Endpoint**: `POST /api/v1/services/compensation_predictor/predict`

**Request**:
```json
{
  "origin_city": "New York, USA",
  "destination_city": "London, UK",
  "current_salary": 100000,
  "currency": "USD",
  "assignment_duration": "12 months",
  "job_level": "Senior Manager",
  "family_size": 3
}
```

**Response**:
```json
{
  "predictions": {
    "cola_adjustment": 1.25,
    "adjusted_salary": 125000,
    "housing_allowance": 24000,
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
    "housing": 24000
  },
  "metadata": {
    "model_version": "v2.3.1",
    "data_sources": ["WorldBank", "Numbeo", "Internal HR Data"],
    "timestamp": "2025-10-15T10:30:00Z"
  }
}
```

### **2. Policy Analysis**

**Endpoint**: `POST /api/v1/services/policy_analyzer/analyze`

**Request**:
```json
{
  "origin_country": "USA",
  "destination_country": "UK",
  "assignment_type": "Long-term assignment",
  "duration": "24 months",
  "job_title": "Senior Software Engineer"
}
```

**Response**:
```json
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
    "timeline": {
      "visa_application": "Week 1-3",
      "approval_wait": "Week 4-6",
      "relocation": "Week 8-10"
    }
  },
  "metadata": {
    "policy_version": "2024.Q4",
    "last_updated": "2024-10-01"
  }
}
```

---

## Implementation Phases

### **Phase 1: Setup MCP Infrastructure** (Week 1-2)
- Install AGNO MCP framework
- Create MCP Gateway configuration
- Setup Redis for session storage
- Deploy gateway locally

### **Phase 2: Build Prediction Services** (Week 3-4)
- Create Flask apps for compensation & policy services
- Implement mock ML models (use existing LLM logic)
- Containerize services with Docker
- Test endpoints independently

### **Phase 3: Modify Chainlit App** (Week 5-6)
- Create `mcp_client.py` for API calls
- Update `_run_compensation_calculation()` to use MCP
- Update `_run_policy_analysis()` to use MCP
- Add fallback logic for resilience
- Test end-to-end flow

### **Phase 4: Deploy & Monitor** (Week 7-8)
- Create `docker-compose.mcp.yml`
- Deploy all services together
- Add logging and monitoring
- Load test the system

### **Phase 5: Train Real Models** (Month 3+)
- Collect historical compensation data
- Train regression models for COLA, housing, salary
- Fine-tune classification model for routing
- Replace mock models with trained ones
- A/B test model performance

---

## Getting Started with MCP

### **Quick Start Commands**

```bash
# 1. Install dependencies
cd Global-IQ/Global-iq-application
pip install -r requirements.txt
pip install agno-mcp  # Or your MCP framework

# 2. Create MCP configuration
vim mcp_config.yaml  # Use provided template

# 3. Start MCP Gateway
agno-mcp start --config mcp_config.yaml

# 4. Build prediction services
cd services/compensation_predictor
docker build -t compensation-predictor .
docker run -p 8081:8081 compensation-predictor

# 5. Update Chainlit app
# - Add mcp_client.py
# - Modify main.py as shown in integration plan

# 6. Test locally
chainlit run app/main.py

# 7. Deploy with Docker Compose
docker-compose -f docker-compose.mcp.yml up -d
```

---

## Resources

- **Full Integration Plan**: See `AGNO_MCP_INTEGRATION_PLAN.md`
- **Technical Details**: See `TECHNICAL_SUMMARY.txt`
- **Current Code**: `app/main.py`, `app/enhanced_agent_router.py`, `app/input_collector.py`
- **Deployment**: `Dockerfile`, `docker-compose.yml`, `deploy.sh`

---

## Questions to Consider

1. **Do you have access to historical compensation data?**
   - If yes, we can train real ML models
   - If no, we start with LLM-based predictions wrapped in MCP

2. **What external APIs do you want to integrate?**
   - Currency exchange rates (e.g., exchangerate-api.com)
   - Cost of living (e.g., Numbeo API, Teleport API)
   - Visa requirements (e.g., visa-requirements.io)
   - Housing costs (e.g., Zillow, local real estate APIs)

3. **What's your deployment environment?**
   - Local development
   - Cloud (AWS, Azure, GCP)
   - On-premises servers

4. **What's your priority?**
   - Quick prototype (start with mock models in MCP)
   - Production-ready (train real models, add monitoring)
   - Hybrid (use existing LLM, gradually replace with ML)

---

## Next Steps

1. **Review the Integration Plan**: Read `AGNO_MCP_INTEGRATION_PLAN.md`
2. **Choose Your Approach**:
   - Option A: Start with mock MCP services (faster prototype)
   - Option B: Train ML models first (better accuracy, slower)
   - Option C: Hybrid - use LLM via MCP, replace incrementally
3. **Set Up Development Environment**:
   - Install AGNO MCP framework
   - Create first prediction service
   - Test with Chainlit app locally
4. **Deploy & Iterate**:
   - Deploy to staging environment
   - Gather user feedback
   - Improve models based on data

Let's discuss which approach makes most sense for your timeline and requirements!


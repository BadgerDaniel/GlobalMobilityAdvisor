# System Architecture Overview

Complete architectural overview of the Global IQ Mobility Advisor system.

---

## High-Level Architecture

The system follows a microservices pattern with a main application orchestrating calls to specialized MCP servers.

**Flow:**
```
User → Chainlit Web App → Router → Input Collector → Service Manager
                                                          ↓
                                        ┌─────────────────┼──────────────────┐
                                        ↓                 ↓                  ↓
                               MCP Servers        Health Check      GPT-4 Fallback
                            (compensation + policy)
```

---

## Key Components

### 1. Chainlit Web Application
**File:** [app/main.py](../../app/main.py) (821 lines)

**Responsibilities:**
- User authentication and session management
- File upload processing (PDF, DOCX, XLSX, CSV, JSON, TXT)
- Message routing and orchestration
- Admin commands (`/health`, `/users`, `/help`, `/history`)

**Key Functions:**
- `@cl.password_auth_callback` - Role-based authentication
- `@cl.on_chat_start` - Session initialization
- `@cl.on_message` - Main message handler
- File processors for multiple formats

### 2. Enhanced Agent Router
**File:** [app/enhanced_agent_router.py](../../app/enhanced_agent_router.py) (246 lines)

**Purpose:** Intelligent query classification

**Routes:**
- `policy` - Visa, immigration, compliance
- `compensation` - Salary, allowances, COLA
- `both` - Complex strategic questions
- `fallback` - General guidance

**Routing Methods (in order):**
1. Direct match (exact keywords)
2. Keyword scoring (from route_config.json)
3. LLM routing (GPT-4 decision)

### 3. Service Manager
**File:** [app/service_manager.py](../../app/service_manager.py) (418 lines)

**Purpose:** MCP server orchestration with automatic fallback

**Features:**
- Health monitoring with 30s caching
- Automatic fallback to GPT-4 if MCP unavailable
- Usage statistics tracking
- Parameter mapping for MCP APIs

**Key Classes:**
- `ServiceHealthMonitor` - Health check caching
- `MCPServiceManager` - Main orchestrator

### 4. Conversational Collector
**File:** [app/conversational_collector.py](../../app/conversational_collector.py) (259 lines)

**Purpose:** Natural language input collection

**Process:**
1. Extract information from user message
2. Ask follow-up questions for missing data
3. Confirm all data with user
4. Return structured data for processing

### 5. AGNO MCP Client
**File:** [app/agno_mcp_client.py](../../app/agno_mcp_client.py) (283 lines)

**Purpose:** Bridge to MCP prediction servers

**Status:** Integrated via service_manager.py

### 6. MCP Servers (FastAPI)

**Compensation Server:**
- **File:** [services/mcp_prediction_server/compensation_server.py](../../services/mcp_prediction_server/compensation_server.py)
- **Port:** 8081
- **Endpoints:** `/health`, `/predict`
- **Current:** OpenAI GPT-4 placeholder
- **Target:** Real ML models

**Policy Server:**
- **File:** [services/mcp_prediction_server/policy_server.py](../../services/mcp_prediction_server/policy_server.py)
- **Port:** 8082
- **Endpoints:** `/health`, `/analyze`
- **Current:** OpenAI GPT-4 placeholder
- **Target:** Real policy engine

---

## Data Flow Example

**Query:** "How much will I earn in London?"

```
1. Login → employee/employee123
2. Message received → Router analyzes
3. Route determined → Compensation (keyword: "earn")
4. Input Collector:
   - Extracts: destination="London"
   - Asks: origin, salary, job level, family size
   - Confirms data
5. Service Manager:
   - Checks MCP health (30s cache)
   - Calls compensation server OR falls back to GPT-4
6. Response generated and displayed
```

---

## Request/Response Format

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
    "total_package": 145000,
    "base_salary": 100000,
    "currency": "USD",
    "cola_ratio": 1.15
  },
  "breakdown": {
    "cola_adjustment": 15000,
    "housing": 24000,
    "hardship": 0,
    "tax_gross_up": 6000
  },
  "confidence_scores": {
    "overall": 0.85
  },
  "metadata": {
    "model_version": "placeholder",
    "timestamp": "2025-10-27T...",
    "methodology": "OpenAI GPT-4"
  }
}
```

---

## Session Management

```python
cl.user_session = {
    "user": cl.User,           # Authenticated user
    "history": [],             # Chat history
    "user_data": {
        "conversational_mode": bool,
        "current_route": str,
        "collected_data": dict,
        "conversation_history": list
    },
    "extracted_texts": []      # From file uploads
}
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `route_config.json` | Routing keywords and display messages |
| `agent_configs/compensation_questions.txt` | Compensation questions |
| `agent_configs/policy_questions.txt` | Policy questions |
| `agent_configs/intro_message.txt` | Welcome message template |
| `.env` | Environment variables (API keys, URLs) |

---

## Deployment Options

### Local Development
- Single Python process
- Port 8000
- MCP fallback to GPT-4

### Docker Compose
- 3 containers: main app + 2 MCP servers
- Shared network with DNS
- Health checks and auto-restart

### Kubernetes
- LoadBalancer service
- 2 replicas for HA
- Persistent volumes for uploads/logs
- ConfigMaps and Secrets

---

## Technology Stack

**Frontend:**
- Chainlit (chat UI framework)

**Backend:**
- Python 3.11
- FastAPI (MCP servers)
- OpenAI GPT-4
- LangChain (routing)

**Infrastructure:**
- Docker & Docker Compose
- Kubernetes

---

## Security

**Authentication:**
- SHA-256 password hashing
- Session-based (Chainlit)
- Role-based access control (RBAC)

**Secrets Management:**
- `.env` file (local)
- Kubernetes Secrets (production)

---

## Performance

**Optimization:**
- Health check caching (30s TTL)
- Async operations (all I/O)
- Connection pooling

**Scaling:**
- Horizontal (Kubernetes replicas)
- Vertical (resource limits)

---

## Next Steps

- **Component Details**: [COMPONENTS.md](COMPONENTS.md) - Detailed component breakdown
- **MCP Integration**: [MCP_INTEGRATION.md](MCP_INTEGRATION.md) - How MCP works
- **Development**: [Development Guide](../development/README.md)
- **Deployment**: [Deployment Guide](../deployment/README.md)

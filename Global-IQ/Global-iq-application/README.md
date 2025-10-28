# Global IQ Mobility Advisor

> AI-powered HR assistant for international employee relocations

**Version:** 2.0 (MCP Integration Complete)
**Status:** Production Ready (Placeholder Models)

---

## What Is This?

Global IQ Mobility Advisor is a Chainlit-based chat application that helps HR professionals and employees with international relocations by providing:

- **Compensation Calculations**: Salary adjustments, COLA, housing allowances, tax calculations
- **Policy Analysis**: Visa requirements, compliance checks, eligibility assessments
- **Document Processing**: Upload PDF, DOCX, XLSX files for context
- **Intelligent Routing**: Automatic query classification to specialized agents

**Current Architecture**: MCP integration with service manager, health checks, and fallback logic. MCP servers currently use OpenAI GPT-4 as placeholders for real ML models.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export OPENAI_API_KEY="sk-your-key-here"  # Linux/Mac
set OPENAI_API_KEY=sk-your-key-here       # Windows

# 3. Run the app
chainlit run app/main.py

# 4. Open browser
# http://localhost:8000
```

**Login:** `employee` / `employee123` (see [User Credentials](docs/getting-started/USER_CREDENTIALS.md))

---

## Documentation

### 📚 Getting Started
- **[Quick Start Guide](docs/getting-started/README.md)** - Get up and running in 5 minutes
- **[Installation Guide](docs/getting-started/INSTALLATION.md)** - Detailed setup instructions
- **[User Credentials](docs/getting-started/USER_CREDENTIALS.md)** - Login credentials for all roles

### 🏗️ Architecture
- **[System Overview](docs/architecture/README.md)** - High-level architecture and components
- **[Component Guide](docs/architecture/COMPONENTS.md)** - Detailed breakdown of each component
- **[MCP Integration](docs/architecture/MCP_INTEGRATION.md)** - How the MCP integration works

### 🚀 Deployment
- **[Deployment Overview](docs/deployment/README.md)** - Choose your deployment method
- **[Docker Deployment](docs/deployment/DOCKER.md)** - Multi-service Docker Compose setup
- **[Kubernetes Deployment](docs/deployment/KUBERNETES.md)** - Production K8s deployment
- **[Kubernetes Quick Start](docs/deployment/KUBERNETES_QUICKSTART.md)** - Deploy to K8s in 10 minutes

### 💻 Development
- **[Development Guide](docs/development/README.md)** - How to contribute and modify the code
- **[Model Integration Guide](docs/development/MODEL_INTEGRATION.md)** - Replace OpenAI placeholders with real ML models
- **[Testing Guide](docs/development/TESTING.md)** - Run tests and add new test cases
- **[Next Steps](docs/development/NEXT_STEPS.md)** - Planned features and enhancements

---

## Project Structure

```
Global-IQ/Global-iq-application/
├── app/                          # Main application code
│   ├── main.py                   # Chainlit entry point
│   ├── service_manager.py        # MCP orchestration
│   ├── enhanced_agent_router.py  # Query routing
│   ├── conversational_collector.py # Input collection
│   └── agent_configs/            # Question configurations
├── services/                     # MCP servers
│   └── mcp_prediction_server/
│       ├── compensation_server.py # Compensation MCP server
│       ├── policy_server.py      # Policy MCP server
│       └── Dockerfile.*          # Server containers
├── tests/                        # Test suite
│   ├── test_service_manager.py
│   ├── test_agent_router.py
│   └── ...
├── k8s/                          # Kubernetes manifests
│   ├── deployment.yaml
│   ├── configmap.yaml
│   └── ...
├── docs/                         # Documentation (you are here)
│   ├── getting-started/
│   ├── architecture/
│   ├── deployment/
│   └── development/
├── docker-compose.yml            # Multi-service Docker setup
├── Dockerfile                    # Main app container
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Key Features

### ✅ Implemented
- Multi-route query classification (policy, compensation, both, fallback)
- Conversational input collection with AI validation
- Document processing (PDF, DOCX, XLSX, CSV, JSON, TXT)
- Role-based authentication (admin, HR, employee, demo)
- MCP server integration with health checks and fallback
- Service manager pattern for orchestration
- Docker multi-service deployment
- Kubernetes production-ready manifests
- Comprehensive test suite (pytest)
- Admin commands (`/health`, `/users`, `/help`, `/history`)

### ⚠️ Current Limitations
- **No Real ML Models**: MCP servers use OpenAI GPT-4 (placeholders)
- **No External Data**: No live COLA databases, visa APIs, or housing data
- **No Confidence Scores**: No statistical validation of predictions
- **Session-Only Storage**: Chat history not persisted across sessions

---

## Technology Stack

**Frontend:**
- Chainlit (Chat UI framework)

**Backend:**
- Python 3.11
- FastAPI (MCP servers)
- OpenAI GPT-4 (LLM)
- LangChain (Routing & orchestration)

**Storage:**
- File uploads (local/volume mounts)
- In-memory session state

**Deployment:**
- Docker & Docker Compose
- Kubernetes (manifests provided)

---

## User Roles

| Role | Username | Password | Capabilities |
|------|----------|----------|--------------|
| Admin | `admin` | `admin123` | Full access, user management, `/health`, `/users`, `/history` |
| HR Manager | `hr_manager` | `hr2024` | Policy & compensation access |
| Employee | `employee` | `employee123` | Personal relocation queries |
| Demo | `demo` | `demo` | Exploration mode |

---

## Deployment Options

### Option 1: Local Development
```bash
# Run app only (no MCP servers)
chainlit run app/main.py

# Falls back to GPT-4 for predictions
```

### Option 2: Docker (Recommended)
```bash
# Start all 3 services (app + 2 MCP servers)
docker-compose up -d

# Access at http://localhost:8000
```

### Option 3: Kubernetes
```bash
# Deploy to K8s cluster
kubectl apply -k k8s/

# Access via LoadBalancer or port-forward
```

See [Deployment Overview](docs/deployment/README.md) for details.

---

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Adding Features
1. Read [Development Guide](docs/development/README.md)
2. Modify code in `app/`
3. Add tests in `tests/`
4. Update relevant documentation
5. Test locally with `chainlit run app/main.py`

### Integrating Real Models
See [Model Integration Guide](docs/development/MODEL_INTEGRATION.md) for step-by-step instructions on replacing OpenAI placeholders with real ML models.

---

## Contributing

1. Create a feature branch
2. Make your changes
3. Add/update tests
4. Update documentation
5. Submit a pull request

---

## Support

- **Application Issues**: Check [docs/architecture/COMPONENTS.md](docs/architecture/COMPONENTS.md)
- **Deployment Issues**: Check [docs/deployment/README.md](docs/deployment/README.md)
- **Model Integration**: Check [docs/development/MODEL_INTEGRATION.md](docs/development/MODEL_INTEGRATION.md)
- **For Claude Code**: See [CLAUDE.md](../../CLAUDE.md) for project instructions

---

## License

School Project - Global IQ Mobility Advisor

---

## Changelog

### v2.0 (Current)
- ✅ MCP integration complete with service manager
- ✅ Health checks and automatic fallback
- ✅ Multi-service Docker Compose deployment
- ✅ Kubernetes manifests and deployment scripts
- ✅ Comprehensive test suite
- ✅ Complete documentation reorganization

### v1.0
- Initial Chainlit application
- Query routing with LangChain
- Document processing
- Authentication system

# Development Guide

Guide for developers working on the Global IQ Mobility Advisor codebase.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Git
- OpenAI API key
- Basic understanding of Chainlit and FastAPI

### Setup Development Environment
```bash
# Clone and setup
git clone <repo-url>
cd Global-IQ/Global-iq-application
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
echo "OPENAI_API_KEY=sk-your-key" > .env

# Run
chainlit run app/main.py
```

---

## Project Structure

```
app/
├── main.py                    # Entry point
├── service_manager.py         # MCP orchestration
├── enhanced_agent_router.py   # Query routing
├── conversational_collector.py # Input collection
├── agno_mcp_client.py         # MCP client
└── agent_configs/             # Question configs

services/mcp_prediction_server/
├── compensation_server.py     # Compensation MCP
├── policy_server.py           # Policy MCP
└── requirements.txt

tests/
├── test_service_manager.py
├── test_agent_router.py
└── ...

docs/                          # Documentation
k8s/                           # Kubernetes manifests
```

---

## Development Workflow

### 1. Make Changes
Edit files in `app/` or `services/`

### 2. Test Locally
```bash
chainlit run app/main.py
```

### 3. Run Tests
```bash
pytest
```

### 4. Build and Test with Docker
```bash
docker-compose up --build -d
docker-compose logs -f
```

### 5. Commit
```bash
git add .
git commit -m "Description of changes"
git push
```

---

## Key Development Tasks

### Adding a New Route

1. Update `route_config.json` with new route keywords
2. Add handler in `main.py`
3. Create question config in `agent_configs/`
4. Update router logic in `enhanced_agent_router.py`
5. Add tests

### Modifying Input Collection

1. Edit `conversational_collector.py`
2. Update required fields for route
3. Test extraction and validation
4. Add tests

### Integrating Real ML Models

See [Model Integration Guide](MODEL_INTEGRATION.md) for detailed instructions.

Key steps:
1. Modify MCP server (`compensation_server.py` or `policy_server.py`)
2. Replace OpenAI call with model inference
3. Maintain API contract
4. Test with integration tests
5. Deploy

---

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test
```bash
pytest tests/test_service_manager.py
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

See [Testing Guide](TESTING.md) for details.

---

## Documentation

### Update Documentation
When adding features, update:
- README.md (if public-facing change)
- Architecture docs (if structural change)
- This file (if dev workflow change)

### Generate API Docs
```bash
# For MCP servers
# Visit http://localhost:8081/docs (FastAPI auto-generated)
```

---

## Debugging

### Enable Debug Logging
```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check MCP Server Health
```bash
curl http://localhost:8081/health
curl http://localhost:8082/health
```

### View Docker Logs
```bash
docker-compose logs -f global-iq-app
docker-compose logs -f compensation-server
docker-compose logs -f policy-server
```

---

## Code Style

- **Format**: Follow PEP 8
- **Docstrings**: Use Google style
- **Type Hints**: Add where helpful
- **Comments**: Explain why, not what

---

## Resources

- **Model Integration**: [MODEL_INTEGRATION.md](MODEL_INTEGRATION.md)
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Next Steps**: [NEXT_STEPS.md](NEXT_STEPS.md)
- **Architecture**: [Architecture Overview](../architecture/README.md)

---

## Getting Help

- Check [Architecture Guide](../architecture/README.md) to understand the system
- Review existing code for patterns
- Check git history for context: `git log --oneline`

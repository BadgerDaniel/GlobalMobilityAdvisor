# Testing Guide

Complete guide to testing the Global IQ Mobility Advisor application.

---

## Test Suite Overview

The project uses **pytest** for testing with asyncio support.

**Coverage:**
- Service Manager (MCP orchestration)
- Agent Router (query classification)  
- Conversational Collector (input gathering)
- MCP Integration (end-to-end)

---

## Running Tests

### Quick Start
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with output
pytest -v

# Run specific test file
pytest tests/test_service_manager.py

# Run with coverage
pytest --cov=app --cov-report=html
# View: open htmlcov/index.html
```

### Test Options
```bash
# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run tests matching pattern
pytest -k "test_health"

# Run specific test
pytest tests/test_service_manager.py::test_health_check
```

---

## Test Files

| File | Purpose |
|------|---------|
| `test_service_manager.py` | MCP service manager tests |
| `test_agent_router.py` | Query routing tests |
| `test_conversational_collector.py` | Input collection tests |
| `test_mcp_integration.py` | End-to-end integration test |

---

## Writing Tests

### Example Test
```python
import pytest
from app.service_manager import MCPServiceManager

@pytest.mark.asyncio
async def test_compensation_prediction():
    """Test compensation prediction with MCP fallback"""
    manager = MCPServiceManager(
        openai_client=mock_client,
        enable_mcp=True
    )
    
    result = await manager.predict_compensation(
        collected_data={
            "origin_location": "NYC",
            "destination_location": "London",
            "current_salary": 100000,
            # ...
        },
        extracted_texts=[]
    )
    
    assert result is not None
    assert "compensation" in result.lower()
```

### Async Tests
Always use `@pytest.mark.asyncio` for async functions.

### Mocking
```python
from unittest.mock import Mock, AsyncMock

mock_client = Mock()
mock_client.chat.completions.create = AsyncMock(
    return_value=mock_response
)
```

---

## Integration Testing

### MCP Integration Test
```bash
# Ensure MCP servers are running
python services/mcp_prediction_server/compensation_server.py
python services/mcp_prediction_server/policy_server.py

# Run integration test
python test_mcp_integration.py
```

Expected output:
```
✅ OpenAI client initialized
✅ Service manager initialized
✅ Compensation prediction successful
✅ Policy analysis successful
✅ Health checks passed
```

---

## Manual Testing

### Test Different Routes

**Policy Route:**
```
User: "What visa do I need for UK?"
Expected: Policy route → collect info → analyze
```

**Compensation Route:**
```
User: "How much will I earn in London?"
Expected: Compensation route → collect info → calculate
```

**Both Route:**
```
User: "What's the best country to relocate to?"
Expected: Both routes → collect info → analyze + calculate
```

### Test Admin Commands

Login as `admin` / `admin123`:
- `/health` - Check MCP status
- `/users` - List all users
- `/help` - Show help
- `/history` - View chat history

### Test File Upload

Upload different file types:
- PDF: Policy documents
- DOCX: Assignment details
- XLSX: Salary data
- CSV: Cost of living data

Verify text extraction works.

---

## Continuous Integration

### GitHub Actions (Future)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
```

---

## Common Issues

### "Module not found" during tests
```bash
pip install pytest pytest-asyncio pytest-cov
```

### "Event loop closed" errors
Ensure you're using `@pytest.mark.asyncio`

### Tests timing out
Increase timeout or check MCP servers are running

---

## Next Steps

- Add more unit tests for individual functions
- Add integration tests for full workflows
- Set up CI/CD pipeline
- Add performance tests

---

## Resources

- pytest docs: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- Testing best practices: https://testdriven.io/

For test suite details, see archived docs in `docs/archive/`.

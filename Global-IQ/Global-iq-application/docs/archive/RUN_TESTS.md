# Quick Start: Running Tests

This guide will get you running tests in under 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Virtual environment activated
- Application dependencies installed

## Quick Setup

### Step 1: Install Test Dependencies

```bash
cd Global-IQ/Global-iq-application
pip install -r requirements-test.txt
```

### Step 2: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

That's it! You're testing.

## Common Commands

### Basic Testing

```bash
# All tests with verbose output
pytest -v

# Specific test file
pytest tests/test_enhanced_agent_router.py

# Specific test function
pytest tests/test_enhanced_agent_router.py::TestKeywordBasedRouting::test_keyword_routing_direct_matches
```

### Coverage Reports

```bash
# Terminal coverage report
pytest --cov=app

# Detailed coverage with missing lines
pytest --cov=app --cov-report=term-missing

# HTML coverage report (opens in browser)
pytest --cov=app --cov-report=html
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

### Test Filtering

```bash
# Run only router tests
pytest -m router

# Run only async tests
pytest -m async_test

# Run all except slow tests
pytest -m "not slow"

# Run specific test pattern
pytest -k "keyword_routing"
```

### Fast Testing

```bash
# Run tests in parallel (4 workers)
pytest -n 4

# Run only failed tests from last run
pytest --lf

# Stop on first failure
pytest -x
```

## Expected Output

### Successful Run

```
======================== test session starts ========================
platform win32 -- Python 3.11.0, pytest-7.4.0
collected 150 items

tests/test_enhanced_agent_router.py .................... [ 13%]
tests/test_conversational_collector.py ................. [ 26%]
tests/test_input_collector.py .......................... [ 44%]
tests/test_file_processing.py .......................... [ 66%]
tests/test_authentication.py ........................... [ 88%]

======================== 150 passed in 12.34s =======================
```

### With Coverage

```
----------- coverage: platform win32, python 3.11.0 -----------
Name                               Stmts   Miss  Cover   Missing
----------------------------------------------------------------
app/main.py                          450     45    90%   123-145, 234-256
app/enhanced_agent_router.py         180     18    90%   67-72, 145-150
app/conversational_collector.py      220     22    90%   189-195, 210-215
app/input_collector.py               250     25    90%   156-162, 234-240
----------------------------------------------------------------
TOTAL                               1100    110    90%
```

## Troubleshooting

### Problem: "No module named 'app'"

**Solution**: Run tests from the `Global-iq-application` directory:

```bash
cd Global-IQ/Global-iq-application
pytest
```

### Problem: Import errors for chainlit

**Solution**: This is expected. Tests mock chainlit. If you see this during normal test runs, check that `conftest.py` is in the tests directory.

### Problem: "fixture 'mock_openai_client' not found"

**Solution**: Ensure `conftest.py` exists in the `tests/` directory.

### Problem: Tests are slow

**Solution**: Run in parallel:

```bash
pytest -n auto  # Use all CPU cores
```

### Problem: Coverage report not generating

**Solution**: Install coverage:

```bash
pip install pytest-cov coverage
```

## What to Test First

When starting, run tests in this order:

1. **Authentication** (fastest, no external deps)
   ```bash
   pytest tests/test_authentication.py -v
   ```

2. **File Processing** (uses temp files)
   ```bash
   pytest tests/test_file_processing.py -v
   ```

3. **Input Collector** (sequential logic)
   ```bash
   pytest tests/test_input_collector.py -v
   ```

4. **Conversational Collector** (async tests)
   ```bash
   pytest tests/test_conversational_collector.py -v
   ```

5. **Enhanced Router** (complex routing logic)
   ```bash
   pytest tests/test_enhanced_agent_router.py -v
   ```

## Testing Checklist

Before committing code:

- [ ] All tests pass: `pytest`
- [ ] Coverage >85%: `pytest --cov=app --cov-report=term-missing`
- [ ] No test warnings: `pytest -v`
- [ ] Tests are fast: Complete in <30 seconds

## Next Steps

- Read full documentation: `tests/README.md`
- Add new tests for your features
- Run tests in CI/CD pipeline
- Set up pre-commit hooks

## Quick Reference Card

| Command | Purpose |
|---------|---------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Run last failed |
| `pytest -k router` | Run tests matching "router" |
| `pytest -m unit` | Run unit tests only |
| `pytest --cov=app` | Coverage report |
| `pytest -n 4` | Parallel execution |

## Getting Help

- Check `tests/README.md` for detailed documentation
- Review test examples in existing test files
- Check pytest docs: https://docs.pytest.org/
- Ask in team chat or create an issue

---

**Remember**: Tests should be fast, isolated, and maintainable. Happy testing!

# Global IQ Test Suite

Comprehensive pytest test suite for the Global IQ Mobility Advisor application.

## Overview

This test suite provides **unit tests** and **integration tests** for all major components of the Global IQ application:

- **Enhanced Agent Router**: Keyword routing, LLM routing, route decisions
- **Conversational Collector**: Data extraction, field validation, completion checking
- **Input Collector**: Sequential question flow, answer processing, confirmation handling
- **File Processing**: PDF, DOCX, XLSX, CSV, JSON, TXT handlers
- **Authentication**: Password hashing, user validation
- **Session Management**: State tracking, collection flow

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures and configuration
├── test_enhanced_agent_router.py   # Router tests (keyword + LLM)
├── test_conversational_collector.py # Conversational collector tests
├── test_input_collector.py         # Sequential collector tests
├── test_file_processing.py         # File handler tests
├── test_authentication.py          # Auth and session tests
└── README.md                        # This file
```

## Installation

### 1. Install Test Dependencies

```bash
cd Global-IQ/Global-iq-application
pip install -r requirements-test.txt
```

### 2. Verify Installation

```bash
pytest --version
```

You should see pytest 7.4.0 or higher.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_enhanced_agent_router.py
```

### Run Specific Test Class

```bash
pytest tests/test_enhanced_agent_router.py::TestKeywordBasedRouting
```

### Run Specific Test Function

```bash
pytest tests/test_enhanced_agent_router.py::TestKeywordBasedRouting::test_keyword_routing_direct_matches
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only router tests
pytest -m router

# Run only async tests
pytest -m async_test
```

### Run Tests with Coverage

```bash
# Basic coverage report
pytest --cov=app

# Coverage with missing lines
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report (after running above)
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Run Tests in Parallel

```bash
# Run tests using 4 CPU cores
pytest -n 4
```

### Run Only Failed Tests

```bash
# Run tests that failed in the last run
pytest --lf

# Run failed tests first, then others
pytest --ff
```

## Test Markers

Tests are organized with markers for easy filtering:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for component interactions
- `@pytest.mark.async_test` - Tests using async/await
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.openai` - Tests that interact with OpenAI API (mocked)
- `@pytest.mark.router` - Router-specific tests
- `@pytest.mark.collector` - Collector-specific tests
- `@pytest.mark.file_processing` - File processing tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.session` - Session management tests

### Example: Run Only Fast Tests

```bash
pytest -m "not slow"
```

## Test Coverage Goals

Target coverage metrics:

- **Overall**: >85%
- **Enhanced Router**: >90%
- **Conversational Collector**: >85%
- **Input Collector**: >85%
- **File Processing**: >80%
- **Authentication**: >95%

### Check Current Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

## Fixtures

Common fixtures are defined in `conftest.py`:

### OpenAI Mocks

- `mock_openai_client`: Mocked AsyncOpenAI client
- `mock_openai_response`: Factory for creating mock responses

### Router Fixtures

- `mock_router_config`: Mock router configuration
- `sample_routing_queries`: Sample queries for testing

### Collector Fixtures

- `sample_compensation_data`: Sample compensation data
- `sample_policy_data`: Sample policy data
- `sample_conversation_history`: Sample conversation history

### File Processing Fixtures

- `temp_pdf_file`: Temporary PDF file
- `temp_txt_file`: Temporary text file
- `temp_json_file`: Temporary JSON file
- `temp_csv_file`: Temporary CSV file

### Authentication Fixtures

- `sample_users_db`: Sample users database
- `valid_credentials`: Valid username/password pairs
- `invalid_credentials`: Invalid username/password pairs

### Session Fixtures

- `empty_session`: Empty user session
- `session_with_compensation_collection`: Session with compensation in progress
- `session_with_policy_collection`: Session with policy in progress
- `session_awaiting_confirmation`: Session awaiting user confirmation

## Writing New Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ComponentName>`
- Test functions: `test_<what_is_being_tested>`

### Example Test

```python
import pytest

class TestMyComponent:
    """Test my component functionality."""

    @pytest.fixture
    def my_component(self):
        """Create component instance for testing."""
        return MyComponent()

    def test_basic_functionality(self, my_component):
        """Test basic functionality."""
        result = my_component.do_something()
        assert result is not None

    @pytest.mark.asyncio
    async def test_async_functionality(self, my_component):
        """Test async functionality."""
        result = await my_component.do_something_async()
        assert result is not None
```

### Mocking OpenAI Calls

Always mock OpenAI API calls in tests:

```python
@pytest.mark.asyncio
async def test_with_openai_mock(self, mock_openai_client):
    """Test function that calls OpenAI."""
    from my_module import my_function

    result = await my_function(mock_openai_client)
    assert result is not None
```

### Testing File Processing

Use temporary files for file processing tests:

```python
def test_file_processing(self, temp_txt_file):
    """Test processing text file."""
    from main import process_txt

    result = process_txt(temp_txt_file)
    assert "content" in result
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run tests with coverage
      run: |
        pytest --cov=app --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the app directory is in your Python path:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
```

This is handled automatically in `conftest.py`.

### Async Test Errors

Make sure to use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Mock Not Working

Ensure you're mocking the correct import path. Mock where the object is used, not where it's defined:

```python
# If main.py imports: from module import function
# Mock it in main.py's namespace:
with patch('main.function'):
    ...
```

### File Not Found Errors

When testing file processing, use the provided fixtures or create temporary files:

```python
import tempfile

def test_with_temp_file():
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b"content")
        temp_path = f.name

    try:
        # Test with temp_path
        result = process_file(temp_path)
        assert result is not None
    finally:
        os.unlink(temp_path)
```

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use fixtures**: Reuse common test setup via fixtures
3. **Mock external dependencies**: Never make real API calls in tests
4. **Test edge cases**: Test error handling, empty inputs, large inputs
5. **Use parametrize**: Test multiple scenarios efficiently
6. **Write clear assertions**: Make test failures easy to understand
7. **Document complex tests**: Add docstrings explaining what's being tested
8. **Keep tests fast**: Mock slow operations, avoid file I/O when possible
9. **Test public interfaces**: Focus on testing behavior, not implementation
10. **Maintain tests**: Update tests when code changes

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=app`
4. Run linters: `ruff check .`
5. Format code: `black .`

Target: Every new feature should have >80% test coverage.

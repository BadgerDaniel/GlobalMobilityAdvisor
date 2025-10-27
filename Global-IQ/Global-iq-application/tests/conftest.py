# tests/conftest.py
"""
Pytest fixtures and configuration for Global IQ test suite.
Provides common test data, mocks, and utilities.
"""

import pytest
import os
import sys
import json
import tempfile
import hashlib
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, List

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Mock chainlit before importing app modules
sys.modules['chainlit'] = MagicMock()
sys.modules['chainlit.data'] = MagicMock()
sys.modules['chainlit.data.sql_alchemy'] = MagicMock()


# ==============================================================================
# OPENAI MOCK FIXTURES
# ==============================================================================

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    def _create_response(content: str, model: str = "gpt-4o"):
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = content
        response.model = model
        return response
    return _create_response


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Create a mock AsyncOpenAI client."""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()

    # Make create an async mock
    async def mock_create(*args, **kwargs):
        # Return different responses based on the prompt
        messages = kwargs.get('messages', [])
        if messages:
            content = messages[-1].get('content', '')

            # Handle routing responses
            if 'compensation' in content.lower():
                return mock_openai_response("compensation analysis")
            elif 'policy' in content.lower():
                return mock_openai_response("policy analysis")
            elif 'extract information' in content.lower() or 'extraction' in content.lower():
                # Return JSON for extraction
                extraction_result = {
                    "extracted_fields": {
                        "Origin Location": "Chicago, USA",
                        "Destination Location": "London, UK",
                        "Current Compensation": "100,000 USD"
                    },
                    "confidence": {
                        "Origin Location": 0.95,
                        "Destination Location": 0.95,
                        "Current Compensation": 0.90
                    },
                    "missing_fields": ["Assignment Duration", "Job Level/Title"],
                    "clarifications_needed": []
                }
                return mock_openai_response(json.dumps(extraction_result))
            else:
                return mock_openai_response("Generic response")

        return mock_openai_response("Default response")

    client.chat.completions.create = mock_create
    return client


# ==============================================================================
# ROUTER FIXTURES
# ==============================================================================

@pytest.fixture
def mock_router_config():
    """Create mock router configuration."""
    return {
        "route_messages": {
            "policy": {
                "title": "Policy Specialist",
                "description": "Policy analysis",
                "emoji": "📋"
            },
            "compensation": {
                "title": "Compensation Expert",
                "description": "Compensation calculation",
                "emoji": "💰"
            },
            "both_policy_and_compensation": {
                "title": "Strategic Advisor",
                "description": "Combined analysis",
                "emoji": "🎯"
            },
            "guidance_fallback": {
                "title": "General Assistant",
                "description": "General guidance",
                "emoji": "🤝"
            }
        },
        "routing_keywords": {
            "compensation": ["salary", "pay", "compensation", "allowance"],
            "policy": ["policy", "visa", "compliance", "immigration"],
            "both_policy_and_compensation": ["cheapest", "optimal", "best"],
            "guidance_fallback": ["help", "what can you do"]
        }
    }


@pytest.fixture
def sample_routing_queries():
    """Sample queries for routing tests."""
    return {
        "compensation": [
            "What will my salary be in London?",
            "Calculate compensation for Tokyo",
            "How much housing allowance?",
            "What's the pay package for Berlin?"
        ],
        "policy": [
            "What visa do I need for UK?",
            "Policy requirements for Germany",
            "Immigration rules for Japan",
            "Assignment compliance for France"
        ],
        "both_policy_and_compensation": [
            "What's the cheapest location to relocate?",
            "Best compensation and policy for senior manager",
            "Optimal assignment structure for engineer"
        ],
        "guidance_fallback": [
            "What can you do?",
            "Help me understand this system",
            "Hello, who are you?"
        ]
    }


# ==============================================================================
# COLLECTOR FIXTURES
# ==============================================================================

@pytest.fixture
def sample_compensation_data():
    """Sample compensation data for testing."""
    return {
        "Origin Location": "Chicago, USA",
        "Destination Location": "London, UK",
        "Current Compensation": "100,000 USD",
        "Assignment Duration": "2 years",
        "Job Level/Title": "Senior Engineer",
        "Family Size": "2",
        "Housing Preference": "Apartment"
    }


@pytest.fixture
def sample_policy_data():
    """Sample policy data for testing."""
    return {
        "Origin Country": "United States",
        "Destination Country": "United Kingdom",
        "Assignment Type": "Long-term",
        "Assignment Duration": "2 years",
        "Job Title": "Senior Engineer"
    }


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history."""
    return [
        {"role": "user", "content": "I need help with a relocation from Chicago to London"},
        {"role": "assistant", "content": "I can help with that. What's the employee's current salary?"},
        {"role": "user", "content": "They make 100k per year"}
    ]


# ==============================================================================
# FILE PROCESSING FIXTURES
# ==============================================================================

@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        # Note: This creates a text file with .pdf extension for testing
        # Real PDF processing would require PyMuPDF
        f.write("Sample PDF content for testing")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_txt_file():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Sample text content\nLine 2\nLine 3")
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump({"test": "data", "nested": {"key": "value"}}, f)
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
        f.write("Name,Location,Salary\n")
        f.write("John Doe,London,100000\n")
        f.write("Jane Smith,Paris,120000\n")
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.unlink(temp_path)


# ==============================================================================
# AUTHENTICATION FIXTURES
# ==============================================================================

@pytest.fixture
def sample_users_db():
    """Sample users database."""
    return {
        "admin": {
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
            "role": "admin",
            "name": "Administrator",
            "email": "admin@globaliq.com"
        },
        "hr_manager": {
            "password_hash": hashlib.sha256("hr2024".encode()).hexdigest(),
            "role": "hr_manager",
            "name": "HR Manager",
            "email": "hr@globaliq.com"
        },
        "employee": {
            "password_hash": hashlib.sha256("employee123".encode()).hexdigest(),
            "role": "employee",
            "name": "Employee User",
            "email": "employee@globaliq.com"
        }
    }


@pytest.fixture
def valid_credentials():
    """Valid username/password combinations."""
    return [
        ("admin", "admin123"),
        ("hr_manager", "hr2024"),
        ("employee", "employee123")
    ]


@pytest.fixture
def invalid_credentials():
    """Invalid username/password combinations."""
    return [
        ("admin", "wrongpassword"),
        ("nonexistent", "password"),
        ("", ""),
        ("admin", "")
    ]


# ==============================================================================
# SESSION MANAGEMENT FIXTURES
# ==============================================================================

@pytest.fixture
def empty_session():
    """Empty user session."""
    return {}


@pytest.fixture
def session_with_compensation_collection():
    """Session with compensation collection in progress."""
    return {
        "compensation_collection": {
            "current_question": 2,
            "answers": {
                "Origin Location": "Chicago, USA",
                "Destination Location": "London, UK"
            },
            "completed": False,
            "awaiting_confirmation": False
        }
    }


@pytest.fixture
def session_with_policy_collection():
    """Session with policy collection in progress."""
    return {
        "policy_collection": {
            "current_question": 1,
            "answers": {
                "Origin Country": "United States"
            },
            "completed": False,
            "awaiting_confirmation": False
        }
    }


@pytest.fixture
def session_awaiting_confirmation():
    """Session awaiting user confirmation."""
    return {
        "compensation_collection": {
            "current_question": 5,
            "answers": {
                "Origin Location": "Chicago, USA",
                "Destination Location": "London, UK",
                "Current Compensation": "100,000 USD",
                "Assignment Duration": "2 years",
                "Job Level/Title": "Senior Engineer"
            },
            "completed": False,
            "awaiting_confirmation": True
        }
    }


# ==============================================================================
# INTEGRATION TEST FIXTURES
# ==============================================================================

@pytest.fixture
def mock_chainlit_message():
    """Mock chainlit message."""
    message = Mock()
    message.content = "Test message"
    message.elements = []
    return message


@pytest.fixture
def mock_chainlit_user():
    """Mock chainlit user."""
    user = Mock()
    user.identifier = "test_user"
    user.metadata = {
        "role": "hr_manager",
        "name": "Test User",
        "email": "test@globaliq.com",
        "provider": "credentials"
    }
    return user


@pytest.fixture
def mock_chainlit_session(mock_chainlit_user):
    """Mock chainlit user session."""
    session_data = {
        "user": mock_chainlit_user,
        "history": [],
        "user_data": {}
    }

    def get(key, default=None):
        return session_data.get(key, default)

    def set_val(key, value):
        session_data[key] = value

    session = Mock()
    session.get = get
    session.set = set_val
    session.data = session_data

    return session


# ==============================================================================
# HELPER FIXTURES
# ==============================================================================

@pytest.fixture
def captured_logs():
    """Fixture to capture print statements and logs."""
    logs = []

    def capture(*args, **kwargs):
        logs.append(' '.join(str(arg) for arg in args))

    with patch('builtins.print', side_effect=capture):
        yield logs


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-api-key',
        'CHAINLIT_AUTH_SECRET': 'test-secret'
    }):
        yield


# ==============================================================================
# PARAMETRIZATION HELPERS
# ==============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )

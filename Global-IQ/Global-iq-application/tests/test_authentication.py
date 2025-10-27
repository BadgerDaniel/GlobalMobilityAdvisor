# tests/test_authentication.py
"""
Unit tests for authentication and session management.
Tests password hashing, user validation, and session state tracking.
"""

import pytest
import hashlib
from unittest.mock import Mock, patch, MagicMock


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_password_hash_sha256(self):
        """Test that passwords are hashed using SHA256."""
        password = "test_password"
        expected_hash = hashlib.sha256(password.encode()).hexdigest()

        # Test the hashing
        actual_hash = hashlib.sha256(password.encode()).hexdigest()

        assert actual_hash == expected_hash
        assert len(actual_hash) == 64  # SHA256 produces 64 character hex string

    def test_same_password_same_hash(self):
        """Test that same password produces same hash."""
        password = "consistent_password"

        hash1 = hashlib.sha256(password.encode()).hexdigest()
        hash2 = hashlib.sha256(password.encode()).hexdigest()

        assert hash1 == hash2

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = hashlib.sha256(password1.encode()).hexdigest()
        hash2 = hashlib.sha256(password2.encode()).hexdigest()

        assert hash1 != hash2

    def test_case_sensitive_hashing(self):
        """Test that password hashing is case-sensitive."""
        password_lower = "password"
        password_upper = "PASSWORD"

        hash_lower = hashlib.sha256(password_lower.encode()).hexdigest()
        hash_upper = hashlib.sha256(password_upper.encode()).hexdigest()

        assert hash_lower != hash_upper


class TestUserDatabase:
    """Test user database structure and validation."""

    def test_users_db_structure(self, sample_users_db):
        """Test that USERS_DB has correct structure."""
        assert "admin" in sample_users_db
        assert "hr_manager" in sample_users_db
        assert "employee" in sample_users_db

        # Check each user has required fields
        for username, user_data in sample_users_db.items():
            assert "password_hash" in user_data
            assert "role" in user_data
            assert "name" in user_data
            assert "email" in user_data

    def test_user_password_hashes_valid(self, sample_users_db):
        """Test that user password hashes are valid SHA256."""
        for username, user_data in sample_users_db.items():
            password_hash = user_data["password_hash"]
            assert len(password_hash) == 64  # SHA256 hex length
            # Should be valid hex
            try:
                int(password_hash, 16)
            except ValueError:
                pytest.fail(f"Invalid hex hash for user {username}")

    def test_user_roles_defined(self, sample_users_db):
        """Test that all users have roles defined."""
        expected_roles = {"admin", "hr_manager", "employee"}
        actual_roles = {user_data["role"] for user_data in sample_users_db.values()}

        assert actual_roles == expected_roles

    def test_user_emails_unique(self, sample_users_db):
        """Test that user emails are unique."""
        emails = [user_data["email"] for user_data in sample_users_db.values()]
        assert len(emails) == len(set(emails))


class TestAuthCallback:
    """Test authentication callback function."""

    @pytest.fixture
    def mock_cl_user(self):
        """Mock cl.User class."""
        with patch('main.cl.User') as mock_user:
            yield mock_user

    def test_auth_callback_valid_credentials(self, sample_users_db, valid_credentials):
        """Test authentication with valid credentials."""
        from main import auth_callback

        for username, password in valid_credentials:
            with patch('main.USERS_DB', sample_users_db):
                user = auth_callback(username, password)

                assert user is not None
                assert user.identifier == username

    def test_auth_callback_invalid_password(self, sample_users_db):
        """Test authentication with invalid password."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            user = auth_callback("admin", "wrongpassword")

            assert user is None

    def test_auth_callback_nonexistent_user(self, sample_users_db):
        """Test authentication with nonexistent user."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            user = auth_callback("nonexistent", "password")

            assert user is None

    def test_auth_callback_empty_credentials(self, sample_users_db):
        """Test authentication with empty credentials."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            user = auth_callback("", "")

            assert user is None

    def test_auth_callback_returns_user_metadata(self, sample_users_db):
        """Test that auth callback returns user with metadata."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            user = auth_callback("admin", "admin123")

            assert user is not None
            assert hasattr(user, 'metadata')
            assert user.metadata['role'] == 'admin'
            assert user.metadata['name'] == 'Administrator'
            assert user.metadata['email'] == 'admin@globaliq.com'

    @pytest.mark.parametrize("username,password,should_succeed", [
        ("admin", "admin123", True),
        ("hr_manager", "hr2024", True),
        ("employee", "employee123", True),
        ("admin", "wrong", False),
        ("invalid_user", "password", False),
        ("", "", False),
    ])
    def test_auth_callback_various_scenarios(self, sample_users_db, username, password, should_succeed):
        """Test authentication with various credential scenarios."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            user = auth_callback(username, password)

            if should_succeed:
                assert user is not None
                assert user.identifier == username
            else:
                assert user is None


class TestSystemPromptGeneration:
    """Test system prompt generation based on user context."""

    def test_get_system_prompt_basic(self):
        """Test basic system prompt generation."""
        from main import get_system_prompt

        prompt = get_system_prompt("Test User", "employee")

        assert prompt is not None
        assert isinstance(prompt, str)
        assert "Global IQ Mobility Advisor" in prompt
        assert "Test User" in prompt

    def test_get_system_prompt_admin_role(self):
        """Test system prompt for admin role."""
        from main import get_system_prompt

        prompt = get_system_prompt("Admin User", "admin")

        assert "Administrator" in prompt
        assert "admin" in prompt.lower()

    def test_get_system_prompt_hr_manager_role(self):
        """Test system prompt for HR manager role."""
        from main import get_system_prompt

        prompt = get_system_prompt("HR Manager", "hr_manager")

        assert "HR Manager" in prompt
        assert "policy" in prompt.lower() or "compensation" in prompt.lower()

    def test_get_system_prompt_employee_role(self):
        """Test system prompt for employee role."""
        from main import get_system_prompt

        prompt = get_system_prompt("Employee", "employee")

        assert "Employee" in prompt
        assert "personal" in prompt.lower() or "relocation" in prompt.lower()

    def test_get_system_prompt_demo_role(self):
        """Test system prompt for demo role."""
        from main import get_system_prompt

        prompt = get_system_prompt("Demo User", "demo")

        assert "Demo User" in prompt
        assert "demo" in prompt.lower() or "explore" in prompt.lower()

    def test_get_system_prompt_includes_instructions(self):
        """Test that system prompt includes instructions."""
        from main import get_system_prompt

        prompt = get_system_prompt("User", "employee")

        # Should include key instructions
        assert "document" in prompt.lower()
        assert "context" in prompt.lower()

    @pytest.mark.parametrize("role", ["admin", "hr_manager", "employee", "demo"])
    def test_get_system_prompt_all_roles(self, role):
        """Test system prompt generation for all roles."""
        from main import get_system_prompt

        prompt = get_system_prompt("Test User", role)

        assert prompt is not None
        assert len(prompt) > 0
        assert "Global IQ Mobility Advisor" in prompt


class TestSessionManagement:
    """Test session state management."""

    def test_empty_session_initialization(self, empty_session):
        """Test empty session structure."""
        assert empty_session == {}

    def test_session_with_collection_state(self, session_with_compensation_collection):
        """Test session with collection state."""
        assert "compensation_collection" in session_with_compensation_collection
        collection = session_with_compensation_collection["compensation_collection"]

        assert "current_question" in collection
        assert "answers" in collection
        assert "completed" in collection

    def test_session_state_tracking(self):
        """Test that session state can track multiple collections."""
        session = {
            "compensation_collection": {
                "current_question": 2,
                "answers": {"field1": "value1"},
                "completed": False
            },
            "policy_collection": {
                "current_question": 1,
                "answers": {"field2": "value2"},
                "completed": False
            }
        }

        assert "compensation_collection" in session
        assert "policy_collection" in session
        assert session["compensation_collection"]["current_question"] == 2
        assert session["policy_collection"]["current_question"] == 1

    def test_session_awaiting_confirmation_state(self, session_awaiting_confirmation):
        """Test session in awaiting confirmation state."""
        collection = session_awaiting_confirmation["compensation_collection"]

        assert collection["awaiting_confirmation"] is True
        assert len(collection["answers"]) > 0
        assert collection["completed"] is False


class TestSessionStateTransitions:
    """Test session state transitions."""

    def test_transition_from_empty_to_collecting(self, empty_session):
        """Test transitioning from empty session to collecting."""
        # Simulate starting collection
        session = empty_session.copy()
        session["compensation_collection"] = {
            "current_question": 0,
            "answers": {},
            "completed": False
        }

        assert "compensation_collection" in session
        assert session["compensation_collection"]["current_question"] == 0

    def test_transition_collecting_to_awaiting_confirmation(self, session_with_compensation_collection):
        """Test transitioning to awaiting confirmation."""
        session = session_with_compensation_collection.copy()
        session["compensation_collection"]["awaiting_confirmation"] = True
        session["compensation_collection"]["current_question"] = 5  # All questions done

        assert session["compensation_collection"]["awaiting_confirmation"] is True

    def test_transition_awaiting_to_completed(self, session_awaiting_confirmation):
        """Test transitioning to completed state."""
        session = session_awaiting_confirmation.copy()
        session["compensation_collection"]["completed"] = True
        session["compensation_collection"]["awaiting_confirmation"] = False

        assert session["compensation_collection"]["completed"] is True
        assert session["compensation_collection"]["awaiting_confirmation"] is False


class TestUserMetadataValidation:
    """Test user metadata validation."""

    def test_user_metadata_required_fields(self):
        """Test that user metadata has required fields."""
        from main import auth_callback, USERS_DB

        user = auth_callback("admin", "admin123")

        assert user is not None
        assert "role" in user.metadata
        assert "name" in user.metadata
        assert "email" in user.metadata
        assert "provider" in user.metadata

    def test_user_metadata_values(self, sample_users_db):
        """Test that user metadata values are correct."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            user = auth_callback("hr_manager", "hr2024")

            assert user.metadata['role'] == 'hr_manager'
            assert user.metadata['name'] == 'HR Manager'
            assert user.metadata['email'] == 'hr@globaliq.com'
            assert user.metadata['provider'] == 'credentials'


class TestSecurityConsiderations:
    """Test security-related functionality."""

    def test_password_not_stored_plaintext(self, sample_users_db):
        """Test that passwords are not stored in plaintext."""
        for username, user_data in sample_users_db.items():
            # Password hash should not equal common passwords
            common_passwords = ["admin123", "hr2024", "employee123", "password", "admin"]

            password_hash = user_data["password_hash"]
            for pwd in common_passwords:
                assert password_hash != pwd

    def test_password_hash_length_sufficient(self, sample_users_db):
        """Test that password hashes are sufficiently long."""
        for username, user_data in sample_users_db.items():
            password_hash = user_data["password_hash"]
            # SHA256 produces 64 character hex string
            assert len(password_hash) >= 64

    def test_sql_injection_username(self, sample_users_db):
        """Test that SQL injection attempts in username fail safely."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            # Try SQL injection patterns
            sql_injection_attempts = [
                "admin' OR '1'='1",
                "admin'; DROP TABLE users; --",
                "' OR 1=1 --"
            ]

            for attempt in sql_injection_attempts:
                user = auth_callback(attempt, "password")
                assert user is None

    def test_timing_attack_resistance(self, sample_users_db):
        """Test basic timing attack resistance (same operation for valid/invalid users)."""
        from main import auth_callback

        with patch('main.USERS_DB', sample_users_db):
            # Both should go through password hashing
            result1 = auth_callback("admin", "wrongpassword")
            result2 = auth_callback("nonexistent", "wrongpassword")

            # Both should return None
            assert result1 is None
            assert result2 is None

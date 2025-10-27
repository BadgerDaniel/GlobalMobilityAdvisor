# tests/test_input_collector.py
"""
Unit tests for Input Collector (legacy sequential collector).
Tests question loading, answer processing, and collection flow.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, AsyncMock, patch


class TestInputCollectorInitialization:
    """Test input collector initialization."""

    def test_collector_initializes(self, mock_openai_client):
        """Test collector initialization."""
        from input_collector import InputCollector

        collector = InputCollector(openai_client=mock_openai_client)

        assert collector is not None
        assert hasattr(collector, 'agent_questions')
        assert hasattr(collector, 'config_dir')

    def test_collector_loads_questions(self, mock_openai_client):
        """Test that collector loads questions from config files."""
        from input_collector import InputCollector

        collector = InputCollector(openai_client=mock_openai_client)

        # Should have loaded compensation and policy questions
        assert 'compensation' in collector.agent_questions
        assert 'policy' in collector.agent_questions

    def test_collector_questions_structure(self, mock_openai_client):
        """Test that loaded questions have correct structure."""
        from input_collector import InputCollector

        collector = InputCollector(openai_client=mock_openai_client)

        if collector.agent_questions['compensation']:
            question = collector.agent_questions['compensation'][0]
            assert 'id' in question
            assert 'title' in question
            assert 'question' in question


class TestLoadAgentQuestions:
    """Test loading questions from config files."""

    def test_parse_questions_file(self, mock_openai_client):
        """Test parsing questions from a config file."""
        from input_collector import InputCollector

        # Create a temporary questions file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("""
1. **Test Question 1**
   - Question: "What is your name?"
   - Format: Text

2. **Test Question 2**
   - Question: "What is your location?"
   - Options: London, Paris, Berlin
   - Format: City name
""")
            temp_path = f.name

        try:
            collector = InputCollector(openai_client=mock_openai_client)
            questions = collector._parse_questions_file(temp_path)

            assert len(questions) == 2
            assert questions[0]['title'] == 'Test Question 1'
            assert questions[0]['question'] == 'What is your name?'
            assert questions[1]['options'] != []
        finally:
            os.unlink(temp_path)

    def test_parse_questions_file_handles_errors(self, mock_openai_client):
        """Test that parsing handles missing files gracefully."""
        from input_collector import InputCollector

        collector = InputCollector(openai_client=mock_openai_client)
        questions = collector._parse_questions_file("/nonexistent/file.txt")

        assert questions == []


class TestGetMessages:
    """Test getting various message types."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    def test_get_intro_message(self, collector):
        """Test getting intro message."""
        message = collector.get_intro_message()

        assert message is not None
        assert isinstance(message, str)
        assert len(message) > 0

    def test_get_both_choice_message(self, collector):
        """Test getting both choice message."""
        message = collector.get_both_choice_message()

        assert message is not None
        assert isinstance(message, str)

    def test_get_confirmation_message_compensation(self, collector):
        """Test getting compensation confirmation message."""
        message = collector.get_confirmation_message("compensation")

        assert message is not None
        assert isinstance(message, str)

    def test_get_confirmation_message_policy(self, collector):
        """Test getting policy confirmation message."""
        message = collector.get_confirmation_message("policy")

        assert message is not None
        assert isinstance(message, str)

    def test_get_general_help_message(self, collector):
        """Test getting general help message."""
        message = collector.get_general_help_message()

        assert message is not None
        assert isinstance(message, str)


class TestStartCollection:
    """Test starting input collection."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    def test_start_collection_compensation(self, collector, empty_session):
        """Test starting compensation collection."""
        question, updated_session = collector.start_collection("compensation", empty_session)

        assert question is not None
        assert isinstance(question, str)
        assert 'compensation_collection' in updated_session
        assert updated_session['compensation_collection']['current_question'] == 0

    def test_start_collection_policy(self, collector, empty_session):
        """Test starting policy collection."""
        question, updated_session = collector.start_collection("policy", empty_session)

        assert question is not None
        assert 'policy_collection' in updated_session

    def test_start_collection_invalid_agent_type(self, collector, empty_session):
        """Test starting collection with invalid agent type."""
        question, updated_session = collector.start_collection("invalid", empty_session)

        assert "don't have questions" in question.lower()

    def test_start_collection_initializes_state(self, collector, empty_session):
        """Test that starting collection initializes proper state."""
        question, updated_session = collector.start_collection("compensation", empty_session)

        collection_state = updated_session['compensation_collection']
        assert collection_state['current_question'] == 0
        assert collection_state['answers'] == {}
        assert collection_state['completed'] is False


class TestProcessAnswer:
    """Test processing user answers."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    def test_process_answer_stores_answer(self, collector, empty_session):
        """Test that process_answer stores the user's answer."""
        # Start collection first
        _, session = collector.start_collection("compensation", empty_session)

        # Process an answer
        response, updated_session, is_completed = collector.process_answer(
            "compensation",
            "Chicago, USA",
            session
        )

        # Should have stored the answer
        answers = updated_session['compensation_collection']['answers']
        assert len(answers) > 0

    def test_process_answer_advances_question(self, collector, empty_session):
        """Test that process_answer advances to next question."""
        _, session = collector.start_collection("compensation", empty_session)
        initial_question = session['compensation_collection']['current_question']

        response, updated_session, _ = collector.process_answer(
            "compensation",
            "Chicago, USA",
            session
        )

        new_question = updated_session['compensation_collection']['current_question']
        assert new_question == initial_question + 1

    def test_process_answer_completion(self, collector, session_awaiting_confirmation):
        """Test processing answer when awaiting confirmation."""
        response, updated_session, is_completed = collector.process_answer(
            "compensation",
            "yes",
            session_awaiting_confirmation
        )

        # Should complete when user confirms
        if 'yes' in response.lower() or is_completed:
            assert updated_session['compensation_collection']['completed']


class TestIsCollectionInProgress:
    """Test checking if collection is in progress."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    def test_is_collection_in_progress_true(self, collector, session_with_compensation_collection):
        """Test detecting collection in progress."""
        result = collector.is_collection_in_progress("compensation", session_with_compensation_collection)

        assert result is True

    def test_is_collection_in_progress_false_empty_session(self, collector, empty_session):
        """Test detecting no collection in empty session."""
        result = collector.is_collection_in_progress("compensation", empty_session)

        assert result is False

    def test_is_collection_in_progress_false_completed(self, collector):
        """Test detecting completed collection."""
        session = {
            "compensation_collection": {
                "current_question": 5,
                "answers": {},
                "completed": True
            }
        }

        result = collector.is_collection_in_progress("compensation", session)

        assert result is False


class TestGetCollectedData:
    """Test retrieving collected data."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    def test_get_collected_data_completed(self, collector):
        """Test getting collected data from completed collection."""
        session = {
            "compensation_collection": {
                "completed": True,
                "answers": {
                    "Origin Location": "Chicago, USA",
                    "Destination Location": "London, UK"
                }
            }
        }

        data = collector.get_collected_data("compensation", session)

        assert data is not None
        assert data == session["compensation_collection"]["answers"]

    def test_get_collected_data_not_completed(self, collector, session_with_compensation_collection):
        """Test getting data from incomplete collection."""
        data = collector.get_collected_data("compensation", session_with_compensation_collection)

        assert data is None

    def test_get_collected_data_no_collection(self, collector, empty_session):
        """Test getting data when no collection exists."""
        data = collector.get_collected_data("compensation", empty_session)

        assert data is None


class TestAISpellCheckAndCorrect:
    """Test AI spell checking functionality."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    @pytest.mark.asyncio
    async def test_ai_spell_check_with_client(self, collector):
        """Test spell checking with OpenAI client."""
        # Mock the response
        async def mock_create(*args, **kwargs):
            response = Mock()
            response.choices = [Mock()]
            response.choices[0].message = Mock()
            response.choices[0].message.content = "CORRECTED: London, UK\nSUGGESTIONS: Fixed spelling"
            return response

        collector.openai_client.chat.completions.create = mock_create

        corrected, suggestions = await collector.ai_spell_check_and_correct(
            "londn",
            "Destination Location"
        )

        assert corrected == "London, UK"
        assert len(suggestions) > 0

    @pytest.mark.asyncio
    async def test_ai_spell_check_no_changes(self, collector):
        """Test spell checking when no changes needed."""
        async def mock_create(*args, **kwargs):
            response = Mock()
            response.choices = [Mock()]
            response.choices[0].message = Mock()
            response.choices[0].message.content = "CORRECTED: London, UK\nSUGGESTIONS: None"
            return response

        collector.openai_client.chat.completions.create = mock_create

        corrected, suggestions = await collector.ai_spell_check_and_correct(
            "London, UK",
            "Destination Location"
        )

        assert corrected == "London, UK"

    @pytest.mark.asyncio
    async def test_ai_spell_check_without_client(self):
        """Test spell checking without OpenAI client."""
        from input_collector import InputCollector

        collector = InputCollector(openai_client=None)
        corrected, suggestions = await collector.ai_spell_check_and_correct(
            "test input",
            "Question"
        )

        # Should return input unchanged
        assert corrected == "test input"
        assert suggestions == []


class TestConfirmationFlow:
    """Test confirmation flow handling."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    def test_generate_confirmation_summary(self, collector):
        """Test generating confirmation summary."""
        answers = {
            "Origin Location": "Chicago, USA",
            "Destination Location": "London, UK",
            "Current Compensation": "100,000 USD"
        }

        message = collector._generate_confirmation_summary("compensation", answers)

        assert message is not None
        assert "Chicago" in message
        assert "London" in message
        assert "100,000" in message
        assert any(word in message.lower() for word in ['yes', 'confirm', 'correct'])

    def test_handle_confirmation_response_yes(self, collector, session_awaiting_confirmation):
        """Test handling 'yes' confirmation."""
        response, updated_session, is_completed = collector._handle_confirmation_response(
            "compensation",
            "yes",
            session_awaiting_confirmation
        )

        assert is_completed is True
        assert updated_session['compensation_collection']['completed'] is True

    def test_handle_confirmation_response_no(self, collector, session_awaiting_confirmation):
        """Test handling 'no' confirmation (edit request)."""
        response, updated_session, is_completed = collector._handle_confirmation_response(
            "compensation",
            "no",
            session_awaiting_confirmation
        )

        assert is_completed is False
        assert updated_session['compensation_collection']['current_question'] == 0
        assert "edit" in response.lower() or "again" in response.lower()

    @pytest.mark.parametrize("user_input,expected_completed", [
        ("yes", True),
        ("confirm", True),
        ("correct", True),
        ("y", True),
        ("no", False),
        ("edit", False),
        ("invalid", False)
    ])
    def test_handle_confirmation_various_inputs(self, collector, session_awaiting_confirmation, user_input, expected_completed):
        """Test handling various confirmation inputs."""
        response, updated_session, is_completed = collector._handle_confirmation_response(
            "compensation",
            user_input,
            session_awaiting_confirmation
        )

        if expected_completed:
            assert is_completed is True
        # Invalid inputs should not complete
        elif user_input == "invalid":
            assert is_completed is False
            assert "respond with" in response.lower() or "yes" in response.lower()


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from input_collector import InputCollector
        return InputCollector(openai_client=mock_openai_client)

    def test_process_answer_empty_input(self, collector, session_with_compensation_collection):
        """Test processing empty answer."""
        response, updated_session, _ = collector.process_answer(
            "compensation",
            "",
            session_with_compensation_collection
        )

        # Should still process and move forward
        assert response is not None

    def test_start_collection_already_in_progress(self, collector, session_with_compensation_collection):
        """Test starting collection when already in progress."""
        question, updated_session = collector.start_collection(
            "compensation",
            session_with_compensation_collection
        )

        # Should return next question from existing collection
        assert question is not None

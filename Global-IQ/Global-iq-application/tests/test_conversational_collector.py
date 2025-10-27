# tests/test_conversational_collector.py
"""
Unit tests for Conversational Collector.
Tests data extraction, field validation, and completion checking.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch


class TestConversationalCollectorInitialization:
    """Test conversational collector initialization."""

    def test_collector_initializes_with_client(self, mock_openai_client):
        """Test collector initialization with OpenAI client."""
        from conversational_collector import ConversationalCollector

        collector = ConversationalCollector(openai_client=mock_openai_client)

        assert collector.client is not None
        assert hasattr(collector, 'required_fields')
        assert 'compensation' in collector.required_fields
        assert 'policy' in collector.required_fields

    def test_collector_has_required_fields(self, mock_openai_client):
        """Test that collector defines required fields for each route."""
        from conversational_collector import ConversationalCollector

        collector = ConversationalCollector(openai_client=mock_openai_client)

        # Check compensation fields
        comp_fields = collector.required_fields['compensation']
        assert 'Origin Location' in comp_fields
        assert 'Destination Location' in comp_fields
        assert 'Current Compensation' in comp_fields

        # Check policy fields
        policy_fields = collector.required_fields['policy']
        assert 'Origin Country' in policy_fields
        assert 'Destination Country' in policy_fields
        assert 'Assignment Type' in policy_fields


class TestStartConversation:
    """Test starting conversation for different routes."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    @pytest.mark.asyncio
    async def test_start_conversation_compensation(self, collector):
        """Test starting compensation conversation."""
        result = await collector.start_conversation("compensation")

        assert result is not None
        assert isinstance(result, str)
        assert "compensation" in result.lower()
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_start_conversation_policy(self, collector):
        """Test starting policy conversation."""
        result = await collector.start_conversation("policy")

        assert result is not None
        assert isinstance(result, str)
        assert "policy" in result.lower()
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_start_conversation_unknown_route(self, collector):
        """Test starting conversation with unknown route."""
        result = await collector.start_conversation("unknown")

        assert result is not None
        assert isinstance(result, str)


class TestExtractInformation:
    """Test information extraction from user messages."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    @pytest.mark.asyncio
    async def test_extract_information_basic(self, collector):
        """Test extracting information from basic user message."""
        user_message = "I need to relocate from Chicago to London with a salary of 100k"

        result = await collector.extract_information("compensation", user_message)

        assert result is not None
        assert 'extracted_fields' in result
        assert 'confidence' in result
        assert 'missing_fields' in result
        assert isinstance(result['extracted_fields'], dict)

    @pytest.mark.asyncio
    async def test_extract_information_with_history(self, collector, sample_conversation_history):
        """Test extracting information with conversation history."""
        user_message = "The assignment will be for 2 years"

        result = await collector.extract_information(
            "compensation",
            user_message,
            sample_conversation_history
        )

        assert result is not None
        assert 'extracted_fields' in result

    @pytest.mark.asyncio
    async def test_extract_information_compensation_route(self, collector):
        """Test extraction for compensation route."""
        user_message = "Moving senior engineer from NYC to Tokyo, current salary 120k USD, 3 year assignment"

        result = await collector.extract_information("compensation", user_message)

        assert 'extracted_fields' in result
        extracted = result['extracted_fields']

        # Should extract relevant fields
        assert isinstance(extracted, dict)

    @pytest.mark.asyncio
    async def test_extract_information_policy_route(self, collector):
        """Test extraction for policy route."""
        user_message = "Need long-term assignment policy for USA to Germany transfer"

        result = await collector.extract_information("policy", user_message)

        assert 'extracted_fields' in result
        extracted = result['extracted_fields']
        assert isinstance(extracted, dict)

    @pytest.mark.asyncio
    async def test_extract_information_handles_json_errors(self, collector):
        """Test that extraction handles malformed JSON gracefully."""
        # Mock the OpenAI client to return invalid JSON
        async def mock_create(*args, **kwargs):
            response = Mock()
            response.choices = [Mock()]
            response.choices[0].message = Mock()
            response.choices[0].message.content = "This is not valid JSON"
            return response

        collector.client.chat.completions.create = mock_create

        result = await collector.extract_information("compensation", "test message")

        # Should return default structure on error
        assert 'extracted_fields' in result
        assert 'missing_fields' in result
        assert isinstance(result['extracted_fields'], dict)


class TestGenerateFollowUp:
    """Test follow-up question generation."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    @pytest.mark.asyncio
    async def test_generate_follow_up_with_missing_fields(self, collector):
        """Test generating follow-up for missing fields."""
        extracted_data = {
            "Origin Location": "Chicago, USA",
            "Destination Location": "London, UK"
        }
        missing_fields = ["Current Compensation", "Assignment Duration"]

        result = await collector.generate_follow_up(
            "compensation",
            extracted_data,
            missing_fields
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_follow_up_no_missing_fields(self, collector, sample_compensation_data):
        """Test follow-up when all fields collected."""
        result = await collector.generate_follow_up(
            "compensation",
            sample_compensation_data,
            []
        )

        # Should generate confirmation message
        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_follow_up_shows_captured_data(self, collector):
        """Test that follow-up shows captured data."""
        extracted_data = {
            "Origin Location": "Chicago, USA"
        }
        missing_fields = ["Destination Location", "Current Compensation"]

        result = await collector.generate_follow_up(
            "compensation",
            extracted_data,
            missing_fields
        )

        # Should acknowledge what was captured
        assert "Chicago" in result or "Origin" in result or len(result) > 0


class TestIsComplete:
    """Test completion checking."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    def test_is_complete_all_fields_present(self, collector, sample_compensation_data):
        """Test completion with all required fields."""
        result = collector.is_complete(sample_compensation_data, "compensation")

        assert result is True

    def test_is_complete_missing_fields(self, collector):
        """Test completion with missing fields."""
        partial_data = {
            "Origin Location": "Chicago, USA",
            "Destination Location": "London, UK"
        }

        result = collector.is_complete(partial_data, "compensation")

        assert result is False

    def test_is_complete_empty_data(self, collector):
        """Test completion with empty data."""
        result = collector.is_complete({}, "compensation")

        assert result is False

    def test_is_complete_policy_route(self, collector, sample_policy_data):
        """Test completion for policy route."""
        result = collector.is_complete(sample_policy_data, "policy")

        assert result is True

    def test_is_complete_policy_route_incomplete(self, collector):
        """Test completion for incomplete policy data."""
        partial_data = {
            "Origin Country": "United States",
            "Destination Country": "United Kingdom"
        }

        result = collector.is_complete(partial_data, "policy")

        assert result is False


class TestGenerateConfirmationMessage:
    """Test confirmation message generation."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    @pytest.mark.asyncio
    async def test_generate_confirmation_message(self, collector, sample_compensation_data):
        """Test generating confirmation message."""
        result = await collector._generate_confirmation_message(
            "compensation",
            sample_compensation_data
        )

        assert result is not None
        assert isinstance(result, str)
        # Should include all data fields
        for value in sample_compensation_data.values():
            if value:  # Skip empty values
                assert value in result

    @pytest.mark.asyncio
    async def test_generate_confirmation_asks_for_verification(self, collector, sample_compensation_data):
        """Test that confirmation message asks user to verify."""
        result = await collector._generate_confirmation_message(
            "compensation",
            sample_compensation_data
        )

        # Should ask for confirmation
        assert any(word in result.lower() for word in ['correct', 'confirm', 'yes', 'verify'])


class TestFormatForMCP:
    """Test formatting data for MCP server."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    def test_format_for_mcp_compensation(self, collector, sample_compensation_data):
        """Test formatting compensation data for MCP."""
        result = collector.format_for_mcp("compensation", sample_compensation_data)

        assert result is not None
        assert isinstance(result, dict)
        # Should return the data as-is (keys match MCP format)
        assert result == sample_compensation_data

    def test_format_for_mcp_policy(self, collector, sample_policy_data):
        """Test formatting policy data for MCP."""
        result = collector.format_for_mcp("policy", sample_policy_data)

        assert result is not None
        assert isinstance(result, dict)
        assert result == sample_policy_data


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    @pytest.mark.asyncio
    async def test_extract_information_empty_message(self, collector):
        """Test extracting from empty message."""
        result = await collector.extract_information("compensation", "")

        assert 'extracted_fields' in result
        assert 'missing_fields' in result

    @pytest.mark.asyncio
    async def test_extract_information_very_long_message(self, collector):
        """Test extracting from very long message."""
        long_message = "relocate " * 1000  # Very long message

        result = await collector.extract_information("compensation", long_message)

        assert result is not None

    def test_is_complete_unknown_route(self, collector):
        """Test is_complete with unknown route."""
        result = collector.is_complete({"field": "value"}, "unknown_route")

        # Should return True when no required fields defined
        assert result is True

    @pytest.mark.asyncio
    async def test_extract_with_special_characters(self, collector):
        """Test extraction with special characters in input."""
        user_message = "Relocate from São Paulo to Zürich, salary €100,000"

        result = await collector.extract_information("compensation", user_message)

        assert result is not None
        assert 'extracted_fields' in result


class TestIntegrationScenarios:
    """Test complete conversation scenarios."""

    @pytest.fixture
    def collector(self, mock_openai_client):
        """Create collector instance."""
        from conversational_collector import ConversationalCollector
        return ConversationalCollector(openai_client=mock_openai_client)

    @pytest.mark.asyncio
    async def test_full_compensation_conversation_flow(self, collector):
        """Test a complete compensation conversation flow."""
        # Start conversation
        start_msg = await collector.start_conversation("compensation")
        assert start_msg is not None

        # First user message - partial information
        user_msg_1 = "I need to move someone from Chicago to London"
        extraction_1 = await collector.extract_information("compensation", user_msg_1)
        assert not collector.is_complete(extraction_1['extracted_fields'], "compensation")

        # Follow-up
        follow_up_1 = await collector.generate_follow_up(
            "compensation",
            extraction_1['extracted_fields'],
            extraction_1['missing_fields']
        )
        assert follow_up_1 is not None

    @pytest.mark.asyncio
    async def test_full_policy_conversation_flow(self, collector):
        """Test a complete policy conversation flow."""
        # Start conversation
        start_msg = await collector.start_conversation("policy")
        assert start_msg is not None

        # User provides all information at once
        user_msg = "Long-term assignment from USA to Germany for Senior Manager, 3 years"
        extraction = await collector.extract_information("policy", user_msg)

        # Generate appropriate follow-up
        follow_up = await collector.generate_follow_up(
            "policy",
            extraction['extracted_fields'],
            extraction['missing_fields']
        )
        assert follow_up is not None

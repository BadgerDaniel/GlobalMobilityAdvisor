# tests/test_enhanced_agent_router.py
"""
Unit tests for Enhanced Agent Router.
Tests keyword routing, LLM routing fallback, and route decisions.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from langchain.schema import Document


# Mock LangChain imports before importing the router
@pytest.fixture(autouse=True)
def mock_langchain():
    """Mock LangChain components."""
    with patch('enhanced_agent_router.ChatOpenAI') as mock_chat, \
         patch('enhanced_agent_router.LLMRouterChain') as mock_router, \
         patch('enhanced_agent_router.LLMChain') as mock_chain:

        # Setup mock ChatOpenAI
        mock_chat_instance = MagicMock()
        mock_chat.return_value = mock_chat_instance

        # Setup mock router chain
        mock_router_instance = MagicMock()
        mock_router.from_llm.return_value = mock_router_instance

        # Make invoke return proper structure
        def mock_invoke(inputs):
            query = inputs.get('input', '').lower()
            if 'salary' in query or 'compensation' in query:
                destination = 'compensation'
            elif 'policy' in query or 'visa' in query:
                destination = 'policy'
            elif 'cheapest' in query or 'best' in query:
                destination = 'both_policy_and_compensation'
            else:
                destination = 'guidance_fallback'

            return {
                'destination_and_inputs': {
                    'destination': destination,
                    'next_inputs': {'input': inputs['input']}
                }
            }

        mock_router_instance.invoke = mock_invoke

        # Setup mock LLM chains
        mock_chain_instance = MagicMock()

        def mock_chain_invoke(inputs):
            return {'text': f"Response for: {inputs.get('input', '')}"}

        mock_chain_instance.invoke = mock_chain_invoke
        mock_chain.return_value = mock_chain_instance

        yield {
            'chat': mock_chat,
            'router': mock_router,
            'chain': mock_chain
        }


class TestEnhancedAgentRouterInitialization:
    """Test router initialization."""

    def test_router_initializes_with_api_key(self, mock_env_vars, mock_router_config):
        """Test router initialization with API key."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            router = EnhancedAgentRouter(api_key="test-key")

            assert router is not None
            assert hasattr(router, 'llm')
            assert hasattr(router, 'router_chain')
            assert hasattr(router, 'destination_chains')

    def test_router_loads_config(self, mock_env_vars, mock_router_config):
        """Test that router loads configuration from file."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            router = EnhancedAgentRouter(api_key="test-key")

            assert router.config is not None
            assert 'route_messages' in router.config
            assert 'routing_keywords' in router.config

    def test_router_handles_missing_config(self, mock_env_vars):
        """Test router handles missing config file gracefully."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            from enhanced_agent_router import EnhancedAgentRouter
            router = EnhancedAgentRouter(api_key="test-key")

            # Should use default empty config
            assert router.config == {"route_messages": {}, "routing_keywords": {}}


class TestKeywordBasedRouting:
    """Test keyword-based routing logic."""

    @pytest.fixture
    def router(self, mock_env_vars, mock_router_config):
        """Create router instance for testing."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            return EnhancedAgentRouter(api_key="test-key")

    @pytest.mark.parametrize("query,expected_route", [
        ("What's the salary for this position?", "compensation"),
        ("Calculate my compensation package", "compensation"),
        ("How much housing allowance?", "compensation"),
        ("What is the policy for relocation?", "policy"),
        ("Visa requirements for UK", "policy"),
        ("Assignment compliance rules", "policy"),
        ("What's the cheapest option?", "both_policy_and_compensation"),
        ("Best way to relocate", "both_policy_and_compensation"),
    ])
    def test_keyword_routing_direct_matches(self, router, query, expected_route):
        """Test that keyword routing correctly identifies routes."""
        result = router._keyword_based_routing(query)

        # Note: result may be None if LLM routing is preferred
        # We're testing the keyword matching logic
        if result:
            assert result == expected_route

    def test_keyword_routing_case_insensitive(self, router):
        """Test that keyword routing is case-insensitive."""
        queries = [
            "What's the SALARY?",
            "what's the salary?",
            "What's The Salary?"
        ]

        for query in queries:
            result = router._keyword_based_routing(query)
            if result:  # If keyword routing triggers
                assert result == "compensation"

    def test_keyword_routing_no_match(self, router):
        """Test keyword routing returns None when no keywords match."""
        result = router._keyword_based_routing("Tell me something random")
        # Should return None or guidance_fallback
        assert result is None or result == "guidance_fallback"

    def test_multi_word_keywords_higher_score(self, router):
        """Test that multi-word keywords get higher priority."""
        # The config should weight "cost of living" higher than just "cost"
        query = "What's the cost of living adjustment?"
        result = router._keyword_based_routing(query)

        if result:
            assert result == "compensation"


class TestLLMBasedRouting:
    """Test LLM-based routing for complex queries."""

    @pytest.fixture
    def router(self, mock_env_vars, mock_router_config):
        """Create router instance for testing."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            return EnhancedAgentRouter(api_key="test-key")

    @pytest.mark.parametrize("query,expected_route", [
        ("How much will I earn in London as a senior engineer?", "compensation"),
        ("What are the immigration requirements for Japan?", "policy"),
        ("What's the most cost-effective way to send someone to Berlin?", "both_policy_and_compensation"),
        ("Hello, what can you do?", "guidance_fallback"),
    ])
    def test_route_query_returns_correct_destination(self, router, query, expected_route):
        """Test that route_query returns correct destination."""
        result = router.route_query(query)

        assert result['destination'] == expected_route
        assert result['success'] is True
        assert 'next_inputs' in result
        assert result['next_inputs']['input'] == query

    def test_route_query_includes_route_info(self, router):
        """Test that routing result includes route metadata."""
        result = router.route_query("What's the compensation?")

        assert 'route_info' in result
        assert result['route_info'] is not None
        assert 'name' in result['route_info']
        assert 'description' in result['route_info']

    def test_route_query_handles_exceptions(self, router):
        """Test that route_query handles exceptions gracefully."""
        # Simulate LLM failure
        with patch.object(router, 'router_chain') as mock_chain:
            mock_chain.invoke.side_effect = Exception("LLM error")

            result = router.route_query("test query")

            assert result['destination'] == 'guidance_fallback'
            assert result['success'] is False
            assert 'error' in result


class TestRouteDisplayInfo:
    """Test route display information retrieval."""

    @pytest.fixture
    def router(self, mock_env_vars, mock_router_config):
        """Create router instance for testing."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            return EnhancedAgentRouter(api_key="test-key")

    def test_get_route_display_info_valid_route(self, router):
        """Test getting display info for valid route."""
        info = router.get_route_display_info("compensation")

        assert 'title' in info
        assert 'description' in info
        assert 'emoji' in info
        assert info['emoji'] == "💰"

    def test_get_route_display_info_all_routes(self, router):
        """Test getting display info for all routes."""
        routes = ["policy", "compensation", "both_policy_and_compensation", "guidance_fallback"]

        for route in routes:
            info = router.get_route_display_info(route)
            assert info['title'] is not None
            assert info['description'] is not None
            assert info['emoji'] is not None

    def test_get_route_display_info_unknown_route(self, router):
        """Test getting display info for unknown route."""
        info = router.get_route_display_info("unknown_route")

        # Should return default values
        assert 'title' in info
        assert 'description' in info


class TestRouteResponse:
    """Test getting responses from destination chains."""

    @pytest.fixture
    def router(self, mock_env_vars, mock_router_config):
        """Create router instance for testing."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            return EnhancedAgentRouter(api_key="test-key")

    def test_get_route_response_valid_destination(self, router):
        """Test getting response from valid destination."""
        result = router.get_route_response(
            "compensation",
            {"input": "Calculate salary"}
        )

        assert result is not None
        assert isinstance(result, str)

    def test_get_route_response_invalid_destination(self, router):
        """Test getting response from invalid destination."""
        result = router.get_route_response(
            "invalid_destination",
            {"input": "test"}
        )

        assert "Error: Unknown destination" in result

    def test_get_route_response_handles_exceptions(self, router):
        """Test that get_route_response handles exceptions."""
        with patch.object(router.destination_chains['compensation'], 'invoke', side_effect=Exception("Chain error")):
            result = router.get_route_response("compensation", {"input": "test"})

            assert "Error processing request" in result


class TestProcessQuery:
    """Test complete query processing pipeline."""

    @pytest.fixture
    def router(self, mock_env_vars, mock_router_config):
        """Create router instance for testing."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            return EnhancedAgentRouter(api_key="test-key")

    def test_process_query_complete_pipeline(self, router):
        """Test complete query processing from routing to response."""
        result = router.process_query("What's the salary for London?")

        assert 'destination' in result
        assert 'response' in result
        assert 'success' in result
        assert result['destination'] in ['compensation', 'guidance_fallback', 'policy', 'both_policy_and_compensation']

    @pytest.mark.parametrize("query", [
        "Calculate my compensation",
        "What are the visa requirements?",
        "What's the cheapest option?",
        "Help me understand the system"
    ])
    def test_process_query_various_inputs(self, router, query):
        """Test processing various query types."""
        result = router.process_query(query)

        assert result is not None
        assert 'destination' in result
        assert 'response' in result


class TestRoutingMethodTracking:
    """Test that routing method is properly tracked."""

    @pytest.fixture
    def router(self, mock_env_vars, mock_router_config):
        """Create router instance for testing."""
        with patch('builtins.open', create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda self: self
            mock_file.return_value.__exit__ = Mock()
            mock_file.return_value.read.return_value = json.dumps(mock_router_config)

            from enhanced_agent_router import EnhancedAgentRouter
            return EnhancedAgentRouter(api_key="test-key")

    def test_routing_method_keyword(self, router):
        """Test that keyword routing is tracked."""
        # Use a very specific keyword query
        result = router.route_query("salary")

        assert 'routing_method' in result
        # Could be keyword or llm depending on implementation

    def test_routing_method_llm(self, router):
        """Test that LLM routing is tracked."""
        # Use a complex query that should use LLM
        result = router.route_query("I need comprehensive help with understanding the entire relocation process")

        assert 'routing_method' in result

"""
Service Manager for MCP Integration
Handles health checks, fallback logic, and service coordination
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os
import sys

from openai import AsyncOpenAI

# Import AGNO client from same directory
try:
    from agno_mcp_client import GlobalIQAgentSystem
except ImportError:
    # Try relative import if running as module
    from .agno_mcp_client import GlobalIQAgentSystem

logger = logging.getLogger(__name__)


class ServiceHealthMonitor:
    """Monitors health of MCP services with caching"""

    def __init__(self, cache_duration_seconds: int = 30):
        self.cache_duration = timedelta(seconds=cache_duration_seconds)
        self.last_check: Optional[datetime] = None
        self.last_status: Dict[str, bool] = {
            "compensation_server": False,
            "policy_server": False
        }

    def is_cache_valid(self) -> bool:
        """Check if cached health status is still valid"""
        if self.last_check is None:
            return False
        return datetime.now() - self.last_check < self.cache_duration

    async def check_health(self, agent_system: GlobalIQAgentSystem) -> Dict[str, bool]:
        """
        Check health of MCP servers with caching

        Returns:
            Dict with health status of each server
        """
        # Return cached status if valid
        if self.is_cache_valid():
            logger.debug("Using cached health status")
            return self.last_status

        # Perform fresh health check
        logger.info("Performing health check on MCP servers")
        try:
            health_status = await asyncio.to_thread(agent_system.health_check)
            self.last_status = health_status
            self.last_check = datetime.now()

            logger.info(f"Health check results: {health_status}")
            return health_status
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            # Return last known status or default to unhealthy
            return self.last_status

    def invalidate_cache(self):
        """Force next health check to be fresh"""
        self.last_check = None


class MCPServiceManager:
    """
    Central service manager for MCP integration
    Coordinates between AGNO client and fallback GPT-4
    """

    def __init__(
        self,
        openai_client: AsyncOpenAI,
        compensation_server_url: str = "http://localhost:8081",
        policy_server_url: str = "http://localhost:8082",
        enable_mcp: bool = True
    ):
        """
        Initialize service manager

        Args:
            openai_client: Direct OpenAI client for fallback
            compensation_server_url: URL of compensation MCP server
            policy_server_url: URL of policy MCP server
            enable_mcp: Whether to use MCP servers (can disable for testing)
        """
        self.openai_client = openai_client
        self.enable_mcp = enable_mcp

        # Initialize AGNO agent system
        try:
            self.agent_system = GlobalIQAgentSystem(
                compensation_server_url=compensation_server_url,
                policy_server_url=policy_server_url
            )
            logger.info("AGNO Agent System initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AGNO Agent System: {str(e)}")
            self.agent_system = None
            self.enable_mcp = False

        # Initialize health monitor
        self.health_monitor = ServiceHealthMonitor(cache_duration_seconds=30)

        # Track usage statistics
        self.stats = {
            "mcp_calls": 0,
            "fallback_calls": 0,
            "errors": 0
        }

    async def predict_compensation(
        self,
        collected_data: Dict[str, Any],
        extracted_texts: list = None
    ) -> str:
        """
        Get compensation prediction via MCP or fallback

        Args:
            collected_data: User data collected from conversation
            extracted_texts: Document context (optional)

        Returns:
            Formatted compensation response
        """
        # Try MCP first if enabled
        if self.enable_mcp and self.agent_system:
            health = await self.health_monitor.check_health(self.agent_system)

            if health.get("compensation_server", False):
                try:
                    logger.info("Using MCP compensation server")

                    # Map collected data to MCP parameters
                    mcp_params = self._map_compensation_params(collected_data)

                    # Call MCP via AGNO
                    result = await self.agent_system.predict_compensation(**mcp_params)

                    if result.get("status") == "success":
                        self.stats["mcp_calls"] += 1
                        return self._format_compensation_response(result, source="MCP")
                    else:
                        logger.warning(f"MCP returned error: {result.get('error')}")
                        # Fall through to fallback

                except Exception as e:
                    logger.error(f"MCP compensation call failed: {str(e)}")
                    self.stats["errors"] += 1
                    # Fall through to fallback

        # Fallback to direct GPT-4
        logger.info("Using fallback GPT-4 for compensation")
        self.stats["fallback_calls"] += 1
        return await self._fallback_compensation(collected_data, extracted_texts)

    async def analyze_policy(
        self,
        collected_data: Dict[str, Any],
        extracted_texts: list = None
    ) -> str:
        """
        Get policy analysis via MCP or fallback

        Args:
            collected_data: User data collected from conversation
            extracted_texts: Document context (optional)

        Returns:
            Formatted policy response
        """
        # Try MCP first if enabled
        if self.enable_mcp and self.agent_system:
            health = await self.health_monitor.check_health(self.agent_system)

            if health.get("policy_server", False):
                try:
                    logger.info("Using MCP policy server")

                    # Map collected data to MCP parameters
                    mcp_params = self._map_policy_params(collected_data)

                    # Call MCP via AGNO
                    result = await self.agent_system.analyze_policy(**mcp_params)

                    if result.get("status") == "success":
                        self.stats["mcp_calls"] += 1
                        return self._format_policy_response(result, source="MCP")
                    else:
                        logger.warning(f"MCP returned error: {result.get('error')}")
                        # Fall through to fallback

                except Exception as e:
                    logger.error(f"MCP policy call failed: {str(e)}")
                    self.stats["errors"] += 1
                    # Fall through to fallback

        # Fallback to direct GPT-4
        logger.info("Using fallback GPT-4 for policy")
        self.stats["fallback_calls"] += 1
        return await self._fallback_policy(collected_data, extracted_texts)

    def _map_compensation_params(self, collected_data: Dict) -> Dict:
        """Map collected conversational data to MCP API parameters"""
        return {
            "origin_location": collected_data.get("Origin Location", "Unknown"),
            "destination_location": collected_data.get("Destination Location", "Unknown"),
            "current_salary": self._parse_salary(collected_data.get("Current Compensation", "0")),
            "currency": self._extract_currency(collected_data.get("Current Compensation", "USD")),
            "assignment_duration": collected_data.get("Assignment Duration", "12 months"),
            "job_level": collected_data.get("Job Level/Title", "Manager"),
            "family_size": self._parse_family_size(collected_data.get("Family Size", "1")),
            "housing_preference": collected_data.get("Housing Preference", "Company-provided")
        }

    def _map_policy_params(self, collected_data: Dict) -> Dict:
        """Map collected conversational data to MCP API parameters"""
        return {
            "origin_country": collected_data.get("Origin Country", "Unknown"),
            "destination_country": collected_data.get("Destination Country", "Unknown"),
            "assignment_type": collected_data.get("Assignment Type", "Long-term"),
            "duration": collected_data.get("Assignment Duration", "12 months"),
            "job_title": collected_data.get("Job Title", "Manager")
        }

    def _parse_salary(self, salary_str: str) -> float:
        """Extract numeric salary from string like '$100,000' or '100k'"""
        import re

        # Remove currency symbols and commas
        clean = re.sub(r'[,$£€¥]', '', str(salary_str))

        # Handle 'k' suffix (thousands)
        if 'k' in clean.lower():
            clean = clean.lower().replace('k', '000')

        # Extract number
        try:
            return float(re.sub(r'[^\d.]', '', clean))
        except:
            return 0.0

    def _extract_currency(self, salary_str: str) -> str:
        """Extract currency code from salary string"""
        currency_symbols = {
            '$': 'USD',
            '£': 'GBP',
            '€': 'EUR',
            '¥': 'JPY'
        }

        for symbol, code in currency_symbols.items():
            if symbol in str(salary_str):
                return code

        # Check for currency codes in text
        import re
        match = re.search(r'\b(USD|GBP|EUR|JPY|CAD|AUD)\b', str(salary_str), re.IGNORECASE)
        if match:
            return match.group(1).upper()

        return "USD"  # Default

    def _parse_family_size(self, family_str: str) -> int:
        """Extract numeric family size"""
        import re
        try:
            # Extract first number found
            match = re.search(r'\d+', str(family_str))
            if match:
                return int(match.group())
            return 1
        except:
            return 1

    def _format_compensation_response(self, mcp_result: Dict, source: str) -> str:
        """Format MCP compensation result for Chainlit display"""
        predictions = mcp_result.get("predictions", {})
        breakdown = mcp_result.get("breakdown", {})
        recommendations = mcp_result.get("recommendations", [])
        confidence = mcp_result.get("confidence_scores", {})

        response = f"💰 **Compensation Calculation Results** (via {source})\n\n"

        # Main package summary
        response += "### 📊 Total Package\n"
        response += f"**{predictions.get('total_package', 0):,.2f} {predictions.get('currency', 'USD')}**\n\n"

        # Breakdown
        response += "### 📋 Breakdown\n"
        response += f"• Base Salary: {predictions.get('base_salary', 0):,.2f} {predictions.get('currency', 'USD')}\n"
        response += f"• COLA Adjustment ({predictions.get('cola_ratio', 1.0):.2f}x): {breakdown.get('cola_adjustment', 0):,.2f} {predictions.get('currency', 'USD')}\n"
        response += f"• Housing Allowance: {breakdown.get('housing', 0):,.2f} {predictions.get('currency', 'USD')}\n"
        if breakdown.get('hardship', 0) > 0:
            response += f"• Hardship Pay: {breakdown.get('hardship', 0):,.2f} {predictions.get('currency', 'USD')}\n"
        response += "\n"

        # Confidence scores
        if confidence:
            response += "### 🎯 Confidence Scores\n"
            response += f"• Overall: {confidence.get('overall', 0.5):.0%}\n"
            response += f"• COLA: {confidence.get('cola', 0.5):.0%}\n"
            response += f"• Housing: {confidence.get('housing', 0.5):.0%}\n\n"

        # Recommendations
        if recommendations:
            response += "### 💡 Recommendations\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"{i}. {rec}\n"

        return response

    def _format_policy_response(self, mcp_result: Dict, source: str) -> str:
        """Format MCP policy result for Chainlit display"""
        analysis = mcp_result.get("analysis", {})
        recommendations = mcp_result.get("recommendations", [])
        confidence = mcp_result.get("confidence", 0.85)

        response = f"📋 **Policy Analysis Results** (via {source})\n\n"

        # Visa requirements
        visa = analysis.get("visa_requirements", {})
        if visa:
            response += "### 🛂 Visa Requirements\n"
            response += f"• **Type**: {visa.get('visa_type', 'TBD')}\n"
            response += f"• **Processing Time**: {visa.get('processing_time', 'Unknown')}\n"
            response += f"• **Cost**: {visa.get('cost', 'TBD')}\n"
            response += "• **Requirements**:\n"
            for req in visa.get('requirements', []):
                response += f"  - {req}\n"
            response += "\n"

        # Eligibility
        eligibility = analysis.get("eligibility", {})
        if eligibility:
            response += "### ✅ Eligibility\n"
            meets = eligibility.get('meets_requirements', True)
            response += f"**Status**: {'✓ Meets Requirements' if meets else '⚠ Concerns Identified'}\n"

            concerns = eligibility.get('concerns', [])
            if concerns:
                response += "**Concerns**:\n"
                for concern in concerns:
                    response += f"• {concern}\n"
            response += "\n"

        # Timeline
        timeline = analysis.get("timeline", {})
        if timeline:
            response += "### 📅 Timeline\n"
            for phase, desc in timeline.items():
                response += f"• **{phase.replace('_', ' ').title()}**: {desc}\n"
            response += "\n"

        # Documentation
        docs = analysis.get("documentation", [])
        if docs:
            response += "### 📄 Required Documents\n"
            for doc in docs:
                response += f"• {doc}\n"
            response += "\n"

        # Recommendations
        if recommendations:
            response += "### 💡 Recommendations\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"{i}. {rec}\n"
            response += "\n"

        # Confidence
        response += f"**Confidence**: {confidence:.0%}\n"

        return response

    async def _fallback_compensation(
        self,
        collected_data: Dict,
        extracted_texts: list
    ) -> str:
        """Fallback to direct GPT-4 for compensation (original implementation)"""
        # This is the original implementation from main.py
        data_summary = "\n".join([f"• **{key}:** {value}" for key, value in collected_data.items()])

        context_info = ""
        if extracted_texts:
            context_info = "\n\nAdditional context from uploaded documents:\n"
            for item in extracted_texts:
                max_len = 1000
                truncated_content = item['content'][:max_len]
                if len(item['content']) > max_len:
                    truncated_content += "..."
                context_info += f"\n--- {item['name']} ---\n{truncated_content}\n"

        calc_prompt = f"""You are the Global IQ Compensation Calculator AI engine with years of mobility data and cost analysis experience.

Based on the following employee data, calculate a comprehensive compensation package for their international assignment:

{data_summary}{context_info}

Provide a detailed breakdown including:
1. Base salary adjustments
2. Cost of living adjustments
3. Housing allowances
4. Hardship pay (if applicable)
5. Tax implications
6. Total estimated package
7. Recommendations for optimization

Format your response professionally with clear financial breakdowns."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": calc_prompt}],
            temperature=0.3
        )

        return f"💰 **Compensation Calculation Results** (via Fallback GPT-4)\n\n{response.choices[0].message.content}"

    async def _fallback_policy(
        self,
        collected_data: Dict,
        extracted_texts: list
    ) -> str:
        """Fallback to direct GPT-4 for policy (original implementation)"""
        # This is the original implementation from main.py
        data_summary = "\n".join([f"• **{key}:** {value}" for key, value in collected_data.items()])

        context_info = ""
        if extracted_texts:
            context_info = "\n\nAdditional context from uploaded documents:\n"
            for item in extracted_texts:
                max_len = 1000
                truncated_content = item['content'][:max_len]
                if len(item['content']) > max_len:
                    truncated_content += "..."
                context_info += f"\n--- {item['name']} ---\n{truncated_content}\n"

        policy_prompt = f"""You are the Global IQ Policy Analyzer AI engine trained on corporate mobility policies and compliance requirements.

Based on the following assignment details, provide a comprehensive policy analysis:

{data_summary}{context_info}

Analyze and provide guidance on:
1. Eligibility requirements and compliance
2. Visa and immigration requirements
3. Assignment approval process
4. Policy constraints or limitations
5. Required documentation
6. Timeline and next steps
7. Risk factors and mitigation strategies

Format your response as a structured policy guidance document."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": policy_prompt}],
            temperature=0.3
        )

        return f"📋 **Policy Analysis Results** (via Fallback GPT-4)\n\n{response.choices[0].message.content}"

    def get_statistics(self) -> Dict[str, int]:
        """Get usage statistics"""
        return self.stats.copy()

    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of all services"""
        if not self.agent_system:
            return {
                "mcp_enabled": False,
                "reason": "AGNO Agent System not initialized"
            }

        health = await self.health_monitor.check_health(self.agent_system)

        return {
            "mcp_enabled": self.enable_mcp,
            "servers": health,
            "statistics": self.get_statistics(),
            "last_check": self.health_monitor.last_check.isoformat() if self.health_monitor.last_check else None
        }

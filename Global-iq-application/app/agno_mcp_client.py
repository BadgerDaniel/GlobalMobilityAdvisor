"""
AGNO MCP Client for Global IQ
Connects Chainlit app to MCP prediction servers via AGNO agents
"""

import asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters
from typing import Dict, Any
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalIQAgentSystem:
    """
    AGNO-based agent system for Global IQ
    Manages communication with MCP prediction servers
    """
    
    def __init__(
        self,
        compensation_server_url: str = "http://localhost:8081",
        policy_server_url: str = "http://localhost:8082"
    ):
        self.compensation_server_url = compensation_server_url
        self.policy_server_url = policy_server_url
        
        # Store agents (will be initialized when needed)
        self._compensation_agent = None
        self._policy_agent = None
        
        logger.info("Global IQ Agent System initialized")
    
    async def _get_compensation_agent(self) -> Agent:
        """Lazy initialization of compensation agent"""
        if self._compensation_agent is None:
            # Define MCP server parameters for compensation
            server_params = StdioServerParameters(
                command="python",
                args=[
                    os.path.join(
                        os.path.dirname(__file__),
                        "../services/mcp_prediction_server/compensation_server.py"
                    )
                ],
            )
            
            # Initialize MCP tools
            mcp_tools = MCPTools(server_params=server_params)
            
            # Create agent
            self._compensation_agent = Agent(
                model=OpenAIChat(id="gpt-4o"),
                tools=[mcp_tools],
                instructions=[
                    "You are a compensation calculation specialist.",
                    "Use the predict_compensation tool to generate accurate compensation packages.",
                    "Always provide detailed breakdowns and recommendations.",
                    "Return the raw JSON response from the tool without additional commentary."
                ],
                markdown=False,
                show_tool_calls=True
            )
            
            logger.info("Compensation agent initialized")
        
        return self._compensation_agent
    
    async def _get_policy_agent(self) -> Agent:
        """Lazy initialization of policy agent"""
        if self._policy_agent is None:
            # Define MCP server parameters for policy
            server_params = StdioServerParameters(
                command="python",
                args=[
                    os.path.join(
                        os.path.dirname(__file__),
                        "../services/mcp_prediction_server/policy_server.py"
                    )
                ],
            )
            
            # Initialize MCP tools
            mcp_tools = MCPTools(server_params=server_params)
            
            # Create agent
            self._policy_agent = Agent(
                model=OpenAIChat(id="gpt-4o"),
                tools=[mcp_tools],
                instructions=[
                    "You are a policy and compliance specialist.",
                    "Use the analyze_policy tool to check requirements and eligibility.",
                    "Always highlight compliance concerns and timeline considerations.",
                    "Return the raw JSON response from the tool without additional commentary."
                ],
                markdown=False,
                show_tool_calls=True
            )
            
            logger.info("Policy agent initialized")
        
        return self._policy_agent
    
    async def predict_compensation(
        self,
        origin_location: str,
        destination_location: str,
        current_salary: float,
        currency: str = "USD",
        assignment_duration: str = "12 months",
        job_level: str = "Manager",
        family_size: int = 1,
        housing_preference: str = "Company-provided"
    ) -> Dict[str, Any]:
        """
        Get compensation prediction from MCP server via AGNO agent
        
        Args:
            origin_location: Current location (City, Country)
            destination_location: Destination (City, Country)
            current_salary: Current annual salary
            currency: Currency code
            assignment_duration: Duration of assignment
            job_level: Job level/title
            family_size: Number of family members
            housing_preference: Housing preference
            
        Returns:
            Structured compensation prediction with breakdowns and recommendations
        """
        try:
            logger.info(f"Requesting compensation prediction: {origin_location} -> {destination_location}")
            
            # Get agent
            agent = await self._get_compensation_agent()
            
            # Prepare message for agent
            message = f"""Calculate compensation package for relocation:
- From: {origin_location}
- To: {destination_location}
- Current Salary: {current_salary} {currency}
- Duration: {assignment_duration}
- Job Level: {job_level}
- Family Size: {family_size}
- Housing: {housing_preference}

Use the predict_compensation tool with these parameters."""
            
            # Run agent
            response = await agent.arun(message)
            
            # Parse response
            if response and response.content:
                # Try to extract JSON from response
                content = response.content
                
                # If content is already a dict, return it
                if isinstance(content, dict):
                    logger.info("Compensation prediction successful")
                    return content
                
                # Try to parse as JSON
                try:
                    result = json.loads(content)
                    logger.info("Compensation prediction successful")
                    return result
                except json.JSONDecodeError:
                    # If not JSON, wrap in response
                    logger.warning("Response not in JSON format, wrapping")
                    return {
                        "status": "success",
                        "predictions": {"raw_response": content}
                    }
            else:
                raise Exception("No response from compensation agent")
                
        except Exception as e:
            logger.error(f"Compensation prediction failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get compensation prediction"
            }
    
    async def analyze_policy(
        self,
        origin_country: str,
        destination_country: str,
        assignment_type: str,
        duration: str,
        job_title: str
    ) -> Dict[str, Any]:
        """
        Get policy analysis from MCP server via AGNO agent
        
        Args:
            origin_country: Origin country
            destination_country: Destination country
            assignment_type: Type of assignment
            duration: Duration
            job_title: Job title
            
        Returns:
            Structured policy analysis with requirements and recommendations
        """
        try:
            logger.info(f"Requesting policy analysis: {origin_country} -> {destination_country}")
            
            # Get agent
            agent = await self._get_policy_agent()
            
            # Prepare message for agent
            message = f"""Analyze policy requirements for assignment:
- From: {origin_country}
- To: {destination_country}
- Type: {assignment_type}
- Duration: {duration}
- Job Title: {job_title}

Use the analyze_policy tool with these parameters."""
            
            # Run agent
            response = await agent.arun(message)
            
            # Parse response
            if response and response.content:
                content = response.content
                
                if isinstance(content, dict):
                    logger.info("Policy analysis successful")
                    return content
                
                try:
                    result = json.loads(content)
                    logger.info("Policy analysis successful")
                    return result
                except json.JSONDecodeError:
                    logger.warning("Response not in JSON format, wrapping")
                    return {
                        "status": "success",
                        "analysis": {"raw_response": content}
                    }
            else:
                raise Exception("No response from policy agent")
                
        except Exception as e:
            logger.error(f"Policy analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get policy analysis"
            }
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of MCP servers"""
        import requests
        
        health = {
            "compensation_server": False,
            "policy_server": False
        }
        
        try:
            resp = requests.get(f"{self.compensation_server_url}/health", timeout=2)
            health["compensation_server"] = resp.status_code == 200
        except:
            pass
        
        try:
            resp = requests.get(f"{self.policy_server_url}/health", timeout=2)
            health["policy_server"] = resp.status_code == 200
        except:
            pass
        
        return health



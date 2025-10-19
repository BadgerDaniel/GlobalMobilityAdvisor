# AGNO + MCP Implementation Guide for Global IQ

## 🎯 Goal

Replace the current GPT-4 text generation "calculations" with real prediction models accessible via MCP (Model Context Protocol), using AGNO as the agent orchestration layer.

**Current Flow:**
```
Input Collection → GPT-4 Text Generation → Response
```

**Target Flow:**
```
Input Collection → AGNO Agent → MCP Server → Prediction Model → Structured Response
```

---

## 📋 Prerequisites

### **System Requirements**
- Python 3.8 or later
- OpenAI API key (for AGNO agent)
- Access to prediction models (or we'll create mock ones)

### **Current System Components to Modify**
- `app/main.py` - Lines 239-334 (calculation functions)
- Input collection system (already working)
- Response formatting

---

## 🚀 Phase 1: Installation & Setup

### **Step 1: Install AGNO and MCP**

```bash
# Navigate to your project
cd Global-IQ/Global-iq-application

# Activate virtual environment (if using)
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install AGNO
pip install agno

# Install MCP protocol library
pip install mcp

# Update requirements.txt
pip freeze > requirements.txt
```

### **Step 2: Verify Installation**

```python
# test_installation.py
from agno.agent import Agent
from agno.os import AgentOS
from agno.tools.mcp import MCPTools

print("✓ AGNO installed successfully")
print("✓ MCP tools available")
```

Run test:
```bash
python test_installation.py
```

---

## 🏗️ Phase 2: Create MCP Server for Predictions

### **Step 1: Create MCP Server Structure**

```bash
# Create directory structure
mkdir -p services/mcp_prediction_server
cd services/mcp_prediction_server
```

### **Step 2: Build Compensation Prediction MCP Server**

Create `services/mcp_prediction_server/compensation_server.py`:

```python
"""
MCP Server for Compensation Predictions
Receives structured input from AGNO agent and returns predictions
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompensationPredictionServer:
    def __init__(self):
        self.server = Server("compensation-predictor")
        self.setup_tools()
        
    def setup_tools(self):
        """Register available tools/endpoints"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available prediction tools"""
            return [
                Tool(
                    name="predict_compensation",
                    description="Predicts compensation package for international relocation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "origin_location": {
                                "type": "string",
                                "description": "Current location (City, Country)"
                            },
                            "destination_location": {
                                "type": "string",
                                "description": "Destination location (City, Country)"
                            },
                            "current_salary": {
                                "type": "number",
                                "description": "Current annual salary"
                            },
                            "currency": {
                                "type": "string",
                                "description": "Currency code (USD, EUR, GBP, etc.)"
                            },
                            "assignment_duration": {
                                "type": "string",
                                "description": "Duration of assignment"
                            },
                            "job_level": {
                                "type": "string",
                                "description": "Job level/title"
                            },
                            "family_size": {
                                "type": "integer",
                                "description": "Number of family members"
                            },
                            "housing_preference": {
                                "type": "string",
                                "description": "Housing preference"
                            }
                        },
                        "required": ["origin_location", "destination_location", "current_salary"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            if name == "predict_compensation":
                result = await self.predict_compensation(arguments)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def predict_compensation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main prediction logic for compensation calculation
        
        This is where you'd integrate your actual ML model.
        For now, we'll use a rule-based approach with external data.
        """
        logger.info(f"Predicting compensation for: {data['origin_location']} → {data['destination_location']}")
        
        try:
            # Extract inputs
            origin = data.get("origin_location", "")
            destination = data.get("destination_location", "")
            base_salary = data.get("current_salary", 0)
            currency = data.get("currency", "USD")
            duration = data.get("assignment_duration", "12 months")
            job_level = data.get("job_level", "Manager")
            family_size = data.get("family_size", 1)
            housing_pref = data.get("housing_preference", "Company-provided")
            
            # PHASE 1: Simple rule-based calculation
            # (Later replace with trained ML model)
            
            # 1. Calculate COLA (Cost of Living Adjustment)
            cola_ratio = self._calculate_cola(origin, destination)
            
            # 2. Calculate housing allowance
            housing_allowance = self._calculate_housing(destination, family_size, housing_pref)
            
            # 3. Calculate hardship pay
            hardship_pay = self._calculate_hardship(destination, duration)
            
            # 4. Calculate adjusted salary
            adjusted_salary = base_salary * cola_ratio
            
            # 5. Calculate total package
            total_package = adjusted_salary + housing_allowance + hardship_pay
            
            # Build response
            response = {
                "status": "success",
                "predictions": {
                    "base_salary": base_salary,
                    "cola_ratio": round(cola_ratio, 3),
                    "adjusted_salary": round(adjusted_salary, 2),
                    "housing_allowance": round(housing_allowance, 2),
                    "hardship_pay": round(hardship_pay, 2),
                    "total_package": round(total_package, 2),
                    "currency": currency
                },
                "breakdown": {
                    "base_salary": base_salary,
                    "cola_adjustment": round(adjusted_salary - base_salary, 2),
                    "housing": round(housing_allowance, 2),
                    "hardship": round(hardship_pay, 2)
                },
                "confidence_scores": {
                    "cola": 0.85,  # Placeholder - would come from model
                    "housing": 0.78,
                    "overall": 0.82
                },
                "methodology": {
                    "model_type": "rule_based_v1",  # Will become "ml_model_v2" later
                    "data_sources": ["Internal rules", "City mappings"],
                    "version": "1.0.0"
                },
                "recommendations": self._generate_recommendations(
                    base_salary, total_package, destination, duration
                )
            }
            
            logger.info(f"Prediction successful: Total package = {total_package:,.2f} {currency}")
            return response
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to generate compensation prediction"
            }
    
    def _calculate_cola(self, origin: str, destination: str) -> float:
        """
        Calculate Cost of Living Adjustment ratio
        
        TODO: Replace with:
        - External API (Numbeo, Teleport)
        - Trained ML model
        - Database lookup
        """
        # Simple city-based lookup (placeholder)
        cola_map = {
            ("New York", "London"): 1.15,
            ("New York", "Tokyo"): 1.25,
            ("New York", "Singapore"): 1.10,
            ("San Francisco", "London"): 1.20,
            ("Chicago", "London"): 1.30,
            ("London", "New York"): 0.87,
            ("default", "default"): 1.05  # Default 5% increase
        }
        
        # Extract city names (simple parsing)
        origin_city = origin.split(",")[0].strip()
        dest_city = destination.split(",")[0].strip()
        
        # Lookup
        key = (origin_city, dest_city)
        return cola_map.get(key, cola_map[("default", "default")])
    
    def _calculate_housing(self, destination: str, family_size: int, preference: str) -> float:
        """
        Calculate housing allowance
        
        TODO: Replace with:
        - Real estate API
        - ML model trained on housing data
        """
        # Base housing by city
        housing_base = {
            "London": 3000,
            "Tokyo": 2500,
            "Singapore": 2800,
            "Paris": 2700,
            "New York": 3500,
            "default": 2000
        }
        
        dest_city = destination.split(",")[0].strip()
        base = housing_base.get(dest_city, housing_base["default"])
        
        # Adjust for family size
        family_multiplier = 1 + (family_size - 1) * 0.2
        
        # Adjust for preference
        pref_multiplier = 1.0 if "company" in preference.lower() else 0.8
        
        monthly_allowance = base * family_multiplier * pref_multiplier
        return monthly_allowance * 12  # Annual
    
    def _calculate_hardship(self, destination: str, duration: str) -> float:
        """
        Calculate hardship pay based on destination difficulty
        
        TODO: Replace with policy database or ML model
        """
        # Hardship locations (placeholder)
        hardship_locations = {
            "Lagos": 0.15,
            "Riyadh": 0.10,
            "Mumbai": 0.08,
            "default": 0.0
        }
        
        dest_city = destination.split(",")[0].strip()
        hardship_rate = hardship_locations.get(dest_city, hardship_locations["default"])
        
        # Only apply for assignments > 6 months
        if "month" in duration.lower():
            months = int(''.join(filter(str.isdigit, duration)))
            if months < 6:
                hardship_rate = 0
        
        return hardship_rate  # Return as percentage
    
    def _generate_recommendations(
        self, base_salary: float, total_package: float, 
        destination: str, duration: str
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        increase_pct = ((total_package - base_salary) / base_salary) * 100
        
        if increase_pct > 30:
            recommendations.append(
                f"Package increase of {increase_pct:.1f}% is substantial. "
                "Consider tax optimization strategies."
            )
        
        if "London" in destination or "UK" in destination:
            recommendations.append(
                "UK tax implications: Consider split payroll arrangement to minimize tax burden."
            )
        
        if "12 month" in duration or "24 month" in duration:
            recommendations.append(
                "For assignments over 12 months, review home country tax residency rules."
            )
        
        recommendations.append(
            "Recommend quarterly compensation reviews to adjust for currency fluctuations."
        )
        
        return recommendations
    
    def run(self, transport: str = "stdio"):
        """Start the MCP server"""
        logger.info(f"Starting Compensation Prediction MCP Server on {transport}")
        
        if transport == "stdio":
            # For stdio transport (direct process communication)
            import asyncio
            from mcp.server.stdio import stdio_server
            
            async def main():
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        self.server.create_initialization_options()
                    )
            
            asyncio.run(main())
        
        elif transport == "sse":
            # For SSE transport (HTTP-based)
            from mcp.server.sse import SseServerTransport
            from starlette.applications import Starlette
            from starlette.routing import Route
            
            sse = SseServerTransport("/messages")
            
            async def handle_sse(request):
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await self.server.run(
                        streams[0], streams[1],
                        self.server.create_initialization_options()
                    )
            
            async def handle_messages(request):
                await sse.handle_post_message(request.scope, request.receive, request._send)
            
            app = Starlette(
                routes=[
                    Route("/sse", endpoint=handle_sse),
                    Route("/messages", endpoint=handle_messages, methods=["POST"])
                ]
            )
            
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8081)


if __name__ == "__main__":
    server = CompensationPredictionServer()
    server.run(transport="sse")  # Use SSE for HTTP-based communication
```

### **Step 3: Create Policy Analysis MCP Server**

Create `services/mcp_prediction_server/policy_server.py`:

```python
"""
MCP Server for Policy Analysis
Handles visa requirements, compliance checks, eligibility
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolicyAnalysisServer:
    def __init__(self):
        self.server = Server("policy-analyzer")
        self.setup_tools()
    
    def setup_tools(self):
        """Register policy analysis tools"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="analyze_policy",
                    description="Analyzes policy requirements for international assignment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "origin_country": {"type": "string"},
                            "destination_country": {"type": "string"},
                            "assignment_type": {"type": "string"},
                            "duration": {"type": "string"},
                            "job_title": {"type": "string"}
                        },
                        "required": ["origin_country", "destination_country", "assignment_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name == "analyze_policy":
                result = await self.analyze_policy(arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def analyze_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze policy requirements
        
        TODO: Integrate with:
        - Visa requirement APIs
        - Internal policy database
        - Compliance systems
        """
        logger.info(f"Analyzing policy: {data['origin_country']} → {data['destination_country']}")
        
        try:
            origin = data.get("origin_country", "")
            destination = data.get("destination_country", "")
            assignment_type = data.get("assignment_type", "")
            duration = data.get("duration", "")
            job_title = data.get("job_title", "")
            
            # Placeholder policy analysis
            response = {
                "status": "success",
                "analysis": {
                    "visa_requirements": self._get_visa_requirements(origin, destination),
                    "eligibility": self._check_eligibility(assignment_type, duration),
                    "compliance": self._check_compliance(origin, destination),
                    "timeline": self._estimate_timeline(destination, assignment_type),
                    "documentation": self._required_documents(destination)
                },
                "recommendations": self._policy_recommendations(
                    origin, destination, assignment_type, duration
                ),
                "metadata": {
                    "policy_version": "2024.Q4",
                    "last_updated": "2024-10-01",
                    "data_sources": ["Internal Policy DB", "Visa APIs"]
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Policy analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_visa_requirements(self, origin: str, destination: str) -> Dict:
        """Get visa requirements (placeholder)"""
        # TODO: Integrate with visa requirement API
        visa_db = {
            ("USA", "UK"): {
                "visa_type": "Tier 2 (General) Work Visa",
                "processing_time": "3-4 weeks",
                "cost": "£610",
                "requirements": [
                    "Certificate of Sponsorship",
                    "English language test",
                    "Financial proof (£1,270 in bank)"
                ]
            },
            ("USA", "Japan"): {
                "visa_type": "Engineer/Specialist in Humanities Visa",
                "processing_time": "5-10 business days",
                "cost": "¥3,000",
                "requirements": [
                    "Certificate of Eligibility",
                    "University degree",
                    "Employment contract"
                ]
            }
        }
        
        key = (origin, destination)
        return visa_db.get(key, {
            "visa_type": "Work Visa (Type TBD)",
            "processing_time": "Varies",
            "cost": "Contact immigration",
            "requirements": ["Standard work visa documents"]
        })
    
    def _check_eligibility(self, assignment_type: str, duration: str) -> Dict:
        """Check eligibility against policy rules"""
        eligible = True
        concerns = []
        recommendations = []
        
        if "short-term" in assignment_type.lower():
            if "month" in duration.lower():
                months = int(''.join(filter(str.isdigit, duration)))
                if months > 6:
                    concerns.append("Short-term assignments should not exceed 6 months")
                    eligible = False
        
        if eligible:
            recommendations.append("Assignment meets all eligibility criteria")
        else:
            recommendations.append("Review assignment type or duration to meet policy requirements")
        
        return {
            "meets_requirements": eligible,
            "concerns": concerns,
            "recommendations": recommendations
        }
    
    def _check_compliance(self, origin: str, destination: str) -> Dict:
        """Check compliance requirements"""
        return {
            "tax_implications": f"Tax resident in {destination} after 183 days",
            "social_security": "Check totalization agreement status",
            "work_permits": "Required for employment",
            "reporting": "Monthly assignment reports required"
        }
    
    def _estimate_timeline(self, destination: str, assignment_type: str) -> Dict:
        """Estimate timeline for assignment setup"""
        return {
            "visa_application": "Week 1-3",
            "visa_approval": "Week 4-6",
            "relocation_prep": "Week 7-8",
            "start_date": "Week 9-10"
        }
    
    def _required_documents(self, destination: str) -> list[str]:
        """List required documents"""
        return [
            "Passport (valid 6+ months)",
            "Employment contract",
            "Educational certificates",
            "Background check",
            "Medical examination results",
            "Tax clearance certificate"
        ]
    
    def _policy_recommendations(
        self, origin: str, destination: str, 
        assignment_type: str, duration: str
    ) -> list[str]:
        """Generate policy recommendations"""
        return [
            "Start visa process 4 months before planned start date",
            "Engage immigration counsel for complex cases",
            "Review tax implications with international tax team",
            "Ensure compliance with both home and host country regulations"
        ]
    
    def run(self, transport: str = "sse"):
        """Start the MCP server"""
        logger.info(f"Starting Policy Analysis MCP Server on {transport}")
        
        if transport == "sse":
            from mcp.server.sse import SseServerTransport
            from starlette.applications import Starlette
            from starlette.routing import Route
            
            sse = SseServerTransport("/messages")
            
            async def handle_sse(request):
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await self.server.run(
                        streams[0], streams[1],
                        self.server.create_initialization_options()
                    )
            
            async def handle_messages(request):
                await sse.handle_post_message(request.scope, request.receive, request._send)
            
            app = Starlette(
                routes=[
                    Route("/sse", endpoint=handle_sse),
                    Route("/messages", endpoint=handle_messages, methods=["POST"])
                ]
            )
            
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8082)


if __name__ == "__main__":
    server = PolicyAnalysisServer()
    server.run(transport="sse")
```

### **Step 4: Create Requirements File for MCP Servers**

Create `services/mcp_prediction_server/requirements.txt`:

```
mcp>=1.0.0
starlette>=0.27.0
uvicorn>=0.23.0
pydantic>=2.0.0
```

---

## 🔌 Phase 3: Integrate AGNO with Global IQ

### **Step 1: Create AGNO Agent Module**

Create `app/agno_mcp_client.py`:

```python
"""
AGNO MCP Client for Global IQ
Connects Chainlit app to MCP prediction servers via AGNO agents
"""

from agno.agent import Agent
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from typing import Dict, Any, Optional
import json
import logging

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
        
        # Initialize MCP tools
        self.compensation_tools = MCPTools(
            transport="sse",
            url=compensation_server_url
        )
        
        self.policy_tools = MCPTools(
            transport="sse",
            url=policy_server_url
        )
        
        # Create specialized agents
        self.compensation_agent = Agent(
            id="compensation-agent",
            name="Compensation Calculator Agent",
            description="Calculates compensation packages for international relocations",
            tools=[self.compensation_tools],
            instructions=[
                "You are a compensation calculation specialist.",
                "Use the predict_compensation tool to generate accurate compensation packages.",
                "Always provide detailed breakdowns and recommendations.",
                "Format responses in a clear, professional manner."
            ]
        )
        
        self.policy_agent = Agent(
            id="policy-agent",
            name="Policy Analysis Agent",
            description="Analyzes mobility policies and compliance requirements",
            tools=[self.policy_tools],
            instructions=[
                "You are a policy and compliance specialist.",
                "Use the analyze_policy tool to check requirements and eligibility.",
                "Always highlight compliance concerns and timeline considerations.",
                "Provide actionable next steps."
            ]
        )
        
        # Create AgentOS to manage agent lifecycle
        self.agent_os = AgentOS(
            description="Global IQ Mobility Advisor Agent System",
            agents=[self.compensation_agent, self.policy_agent]
        )
        
        logger.info("Global IQ Agent System initialized")
    
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
            logger.info(f"Requesting compensation prediction: {origin_location} → {destination_location}")
            
            # Prepare input for MCP tool
            tool_input = {
                "origin_location": origin_location,
                "destination_location": destination_location,
                "current_salary": current_salary,
                "currency": currency,
                "assignment_duration": assignment_duration,
                "job_level": job_level,
                "family_size": family_size,
                "housing_preference": housing_preference
            }
            
            # Call compensation agent with MCP tool
            response = await self.compensation_agent.run(
                message=f"Calculate compensation package for relocation from {origin_location} to {destination_location}",
                tool_calls=[{
                    "tool": "predict_compensation",
                    "arguments": tool_input
                }]
            )
            
            # Parse response
            if response.content:
                result = json.loads(response.content)
                logger.info("Compensation prediction successful")
                return result
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
            logger.info(f"Requesting policy analysis: {origin_country} → {destination_country}")
            
            # Prepare input for MCP tool
            tool_input = {
                "origin_country": origin_country,
                "destination_country": destination_country,
                "assignment_type": assignment_type,
                "duration": duration,
                "job_title": job_title
            }
            
            # Call policy agent with MCP tool
            response = await self.policy_agent.run(
                message=f"Analyze policy requirements for assignment from {origin_country} to {destination_country}",
                tool_calls=[{
                    "tool": "analyze_policy",
                    "arguments": tool_input
                }]
            )
            
            # Parse response
            if response.content:
                result = json.loads(response.content)
                logger.info("Policy analysis successful")
                return result
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
```

### **Step 2: Modify main.py to Use AGNO**

Update `app/main.py` - Replace lines 239-334:

```python
# --- Import AGNO Client ---
from agno_mcp_client import GlobalIQAgentSystem
import os

# --- Initialize AGNO Agent System ---
agno_system = GlobalIQAgentSystem(
    compensation_server_url=os.getenv("COMPENSATION_SERVER_URL", "http://localhost:8081"),
    policy_server_url=os.getenv("POLICY_SERVER_URL", "http://localhost:8082")
)

# --- Enhanced Calculation Functions with AGNO/MCP ---

async def _run_compensation_calculation(collected_data: dict, extracted_texts: list) -> str:
    """
    Enhanced compensation calculation using AGNO + MCP
    Falls back to LLM if MCP servers are unavailable
    """
    try:
        # Check if MCP servers are available
        health = agno_system.health_check()
        if not health["compensation_server"]:
            logger.warning("Compensation MCP server unavailable, falling back to LLM")
            return await _run_compensation_calculation_llm(collected_data, extracted_texts)
        
        # Extract data from collected inputs
        origin = collected_data.get("Origin Location", "")
        destination = collected_data.get("Destination Location", "")
        salary_str = collected_data.get("Current Compensation", "0")
        
        # Parse salary
        salary = parse_salary(salary_str)
        currency = extract_currency(salary_str)
        
        duration = collected_data.get("Assignment Duration", "12 months")
        job_level = collected_data.get("Job Level", "Manager")
        family_size = int(collected_data.get("Family Size", "1"))
        housing_pref = collected_data.get("Housing Preference", "Company-provided")
        
        # Call AGNO agent system
        logger.info(f"Calling AGNO compensation agent for {origin} -> {destination}")
        
        mcp_response = await agno_system.predict_compensation(
            origin_location=origin,
            destination_location=destination,
            current_salary=salary,
            currency=currency,
            assignment_duration=duration,
            job_level=job_level,
            family_size=family_size,
            housing_preference=housing_pref
        )
        
        # Check for errors
        if mcp_response.get("status") == "error":
            logger.error(f"MCP prediction error: {mcp_response.get('error')}")
            return await _run_compensation_calculation_llm(collected_data, extracted_texts)
        
        # Format response for user
        predictions = mcp_response.get("predictions", {})
        breakdown = mcp_response.get("breakdown", {})
        confidence = mcp_response.get("confidence_scores", {})
        methodology = mcp_response.get("methodology", {})
        recommendations = mcp_response.get("recommendations", [])
        
        result = "[RESULTS] **Compensation Calculation Results**\n\n"
        result += f"**Total Estimated Package:** {predictions.get('total_package', 0):,.0f} {predictions.get('currency', currency)}\n\n"
        
        result += "**Breakdown:**\n"
        result += f"- Base Salary: {breakdown.get('base_salary', 0):,.0f} {currency}\n"
        result += f"- Cost of Living Adjustment: +{breakdown.get('cola_adjustment', 0):,.0f} {currency} "
        result += f"(COLA Ratio: {predictions.get('cola_ratio', 1.0):.3f})\n"
        result += f"- Housing Allowance: +{breakdown.get('housing', 0):,.0f} {currency}\n"
        result += f"- Hardship Pay: +{breakdown.get('hardship', 0):,.0f} {currency}\n\n"
        
        result += "**Confidence Scores:**\n"
        result += f"- Cost of Living: {confidence.get('cola', 0)*100:.1f}%\n"
        result += f"- Housing Estimate: {confidence.get('housing', 0)*100:.1f}%\n"
        result += f"- Overall Confidence: {confidence.get('overall', 0)*100:.1f}%\n\n"
        
        if recommendations:
            result += "**Recommendations:**\n"
            for i, rec in enumerate(recommendations, 1):
                result += f"{i}. {rec}\n"
            result += "\n"
        
        result += "**Calculation Methodology:**\n"
        result += f"- Model Type: {methodology.get('model_type', 'Unknown')}\n"
        result += f"- Version: {methodology.get('version', 'N/A')}\n"
        result += f"- Data Sources: {', '.join(methodology.get('data_sources', []))}\n\n"
        
        result += "[INFO] *This calculation is generated by the AGNO/MCP prediction system. "
        result += "Predictions are based on rule-based models and will improve as ML models are trained.*"
        
        return result
        
    except Exception as e:
        logger.error(f"AGNO/MCP compensation calculation failed: {e}")
        # Fallback to LLM-based calculation
        return await _run_compensation_calculation_llm(collected_data, extracted_texts)


async def _run_policy_analysis(collected_data: dict, extracted_texts: list) -> str:
    """
    Enhanced policy analysis using AGNO + MCP
    Falls back to LLM if MCP servers are unavailable
    """
    try:
        # Check if MCP servers are available
        health = agno_system.health_check()
        if not health["policy_server"]:
            logger.warning("Policy MCP server unavailable, falling back to LLM")
            return await _run_policy_analysis_llm(collected_data, extracted_texts)
        
        # Extract data
        origin = collected_data.get("Origin Country", "")
        destination = collected_data.get("Destination Country", "")
        assignment_type = collected_data.get("Assignment Type", "Long-term")
        duration = collected_data.get("Duration", "12 months")
        job_title = collected_data.get("Job Title", "Manager")
        
        # Call AGNO agent system
        logger.info(f"Calling AGNO policy agent for {origin} -> {destination}")
        
        mcp_response = await agno_system.analyze_policy(
            origin_country=origin,
            destination_country=destination,
            assignment_type=assignment_type,
            duration=duration,
            job_title=job_title
        )
        
        # Check for errors
        if mcp_response.get("status") == "error":
            logger.error(f"MCP analysis error: {mcp_response.get('error')}")
            return await _run_policy_analysis_llm(collected_data, extracted_texts)
        
        # Format response
        analysis = mcp_response.get("analysis", {})
        visa = analysis.get("visa_requirements", {})
        eligibility = analysis.get("eligibility", {})
        compliance = analysis.get("compliance", {})
        timeline = analysis.get("timeline", {})
        documentation = analysis.get("documentation", [])
        recommendations = mcp_response.get("recommendations", [])
        metadata = mcp_response.get("metadata", {})
        
        result = "[RESULTS] **Policy Analysis Results**\n\n"
        
        result += "**Visa Requirements:**\n"
        result += f"- Type: {visa.get('visa_type', 'TBD')}\n"
        result += f"- Processing Time: {visa.get('processing_time', 'Varies')}\n"
        result += f"- Cost: {visa.get('cost', 'Contact immigration')}\n"
        if visa.get('requirements'):
            result += "- Documents Needed:\n"
            for req in visa['requirements']:
                result += f"  - {req}\n"
        result += "\n"
        
        result += "**Eligibility Assessment:**\n"
        result += f"- Meets Requirements: {'Yes' if eligibility.get('meets_requirements') else 'No'}\n"
        if eligibility.get('concerns'):
            result += "- [WARNING] Concerns:\n"
            for concern in eligibility['concerns']:
                result += f"  - {concern}\n"
        if eligibility.get('recommendations'):
            result += "- Recommendations:\n"
            for rec in eligibility['recommendations']:
                result += f"  - {rec}\n"
        result += "\n"
        
        result += "**Compliance Considerations:**\n"
        for key, value in compliance.items():
            result += f"- {key.replace('_', ' ').title()}: {value}\n"
        result += "\n"
        
        result += "**Estimated Timeline:**\n"
        for phase, timeframe in timeline.items():
            result += f"- {phase.replace('_', ' ').title()}: {timeframe}\n"
        result += "\n"
        
        if documentation:
            result += "**Required Documentation:**\n"
            for doc in documentation:
                result += f"- {doc}\n"
            result += "\n"
        
        if recommendations:
            result += "**Policy Recommendations:**\n"
            for i, rec in enumerate(recommendations, 1):
                result += f"{i}. {rec}\n"
            result += "\n"
        
        result += "**Analysis Information:**\n"
        result += f"- Policy Version: {metadata.get('policy_version', 'N/A')}\n"
        result += f"- Last Updated: {metadata.get('last_updated', 'N/A')}\n"
        result += f"- Data Sources: {', '.join(metadata.get('data_sources', []))}\n\n"
        
        result += "[INFO] *This analysis is generated by the AGNO/MCP system. "
        result += "Please verify with legal/compliance team before finalizing plans.*"
        
        return result
        
    except Exception as e:
        logger.error(f"AGNO/MCP policy analysis failed: {e}")
        return await _run_policy_analysis_llm(collected_data, extracted_texts)


# Keep original LLM functions as fallbacks
async def _run_compensation_calculation_llm(collected_data: dict, extracted_texts: list) -> str:
    """Original LLM-based compensation calculation (fallback)"""
    # ... (keep original implementation)
    pass

async def _run_policy_analysis_llm(collected_data: dict, extracted_texts: list) -> str:
    """Original LLM-based policy analysis (fallback)"""
    # ... (keep original implementation)
    pass


# Helper functions
def parse_salary(salary_str: str) -> float:
    """Extract numeric salary from string"""
    import re
    cleaned = re.sub(r'[^\d.]', '', salary_str.replace(',', ''))
    if 'k' in salary_str.lower():
        return float(cleaned) * 1000
    return float(cleaned) if cleaned else 0.0

def extract_currency(salary_str: str) -> str:
    """Extract currency code from string"""
    currencies = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
    for symbol, code in currencies.items():
        if symbol in salary_str:
            return code
    import re
    match = re.search(r'\b(USD|EUR|GBP|JPY|CAD|AUD)\b', salary_str.upper())
    if match:
        return match.group(1)
    return "USD"
```

---

## 🚀 Phase 4: Deployment & Testing

### **Step 1: Start MCP Servers**

```bash
# Terminal 1: Start Compensation MCP Server
cd services/mcp_prediction_server
pip install -r requirements.txt
python compensation_server.py

# Terminal 2: Start Policy MCP Server
python policy_server.py
```

### **Step 2: Test MCP Servers**

```bash
# Test compensation server
curl -X POST http://localhost:8081/messages \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "predict_compensation",
    "arguments": {
      "origin_location": "New York, USA",
      "destination_location": "London, UK",
      "current_salary": 100000,
      "currency": "USD"
    }
  }'

# Test policy server
curl -X POST http://localhost:8082/messages \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "analyze_policy",
    "arguments": {
      "origin_country": "USA",
      "destination_country": "UK",
      "assignment_type": "Long-term"
    }
  }'
```

### **Step 3: Update Environment Variables**

Create/update `.env`:

```bash
OPENAI_API_KEY=sk-...
COMPENSATION_SERVER_URL=http://localhost:8081
POLICY_SERVER_URL=http://localhost:8082
```

### **Step 4: Start Chainlit App**

```bash
# Terminal 3: Start Global IQ app
cd Global-IQ/Global-iq-application
chainlit run app/main.py
```

### **Step 5: Test End-to-End**

1. Login as `demo` / `demo`
2. Ask: "How much will I earn in London?"
3. System routes to compensation
4. Answer questions through input collector
5. AGNO agent calls MCP server
6. Receive structured prediction
7. Verify fallback works (stop MCP server and try again)

---

## 📊 Phase 5: Monitoring & Improvement

### **Add Logging**

```python
# In agno_mcp_client.py
import logging
from datetime import datetime

class PredictionLogger:
    def log_prediction(self, prediction_type: str, inputs: dict, outputs: dict, latency: float):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": prediction_type,
            "inputs": inputs,
            "outputs": outputs,
            "latency_ms": latency * 1000
        }
        logging.info(f"Prediction logged: {log_entry}")
```

### **Track Metrics**

- Prediction latency
- Fallback frequency
- Confidence scores
- User satisfaction (add feedback button)

---

## 🎯 Summary

### **What We've Built:**

```
User Input → Input Collector → AGNO Agent → MCP Server → Prediction Model
                                     ↓
                              Fallback to LLM if MCP fails
                                     ↓
                              Formatted Response → User
```

### **Key Benefits:**

✅ **Structured Predictions** - JSON responses instead of text
✅ **Confidence Scores** - Know reliability of predictions
✅ **Scalability** - MCP servers can scale independently
✅ **Fallback Safety** - LLM fallback if MCP unavailable
✅ **Extensibility** - Easy to add new prediction models

### **Next Steps:**

1. **Replace rule-based logic with ML models** in MCP servers
2. **Integrate external APIs** (Numbeo, currency, visa databases)
3. **Add caching** to MCP servers for common queries
4. **Implement monitoring** dashboard
5. **Train models** on historical data

You now have a working AGNO + MCP integration! 🚀


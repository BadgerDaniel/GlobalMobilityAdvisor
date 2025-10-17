"""
MCP Server for Policy Analysis
Handles visa requirements, compliance checks, eligibility
"""

import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI application
app = FastAPI(title="Policy Analyzer MCP Server")

# Request model
class PolicyRequest(BaseModel):
    origin_country: str
    destination_country: str
    assignment_type: str
    duration: str = "12 months"
    job_title: str = "Manager"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "policy_analyzer"}


@app.post("/analyze")
async def analyze_policy_endpoint(request: PolicyRequest) -> Dict[str, Any]:
    """
    API endpoint for policy analysis
    """
    return await analyze_policy(
        origin_country=request.origin_country,
        destination_country=request.destination_country,
        assignment_type=request.assignment_type,
        duration=request.duration,
        job_title=request.job_title
    )


async def analyze_policy(
    origin_country: str,
    destination_country: str,
    assignment_type: str,
    duration: str = "12 months",
    job_title: str = "Manager"
) -> Dict[str, Any]:
    """
    Analyzes policy requirements for international assignment using OpenAI.

    Args:
        origin_country: Origin country
        destination_country: Destination country
        assignment_type: Type of assignment (Short-term, Long-term, Permanent)
        duration: Duration of assignment
        job_title: Job title

    Returns:
        Structured policy analysis with requirements and recommendations
    """
    logger.info(f"Analyzing policy: {origin_country} -> {destination_country}")

    try:
        # Use OpenAI for policy analysis
        prompt = f"""You are a Global Mobility Policy Expert. Analyze the policy requirements for an international employee assignment.

Input Data:
- Origin Country: {origin_country}
- Destination Country: {destination_country}
- Assignment Type: {assignment_type}
- Duration: {duration}
- Job Title: {job_title}

Provide a comprehensive policy analysis including:
1. Visa requirements (type, processing time, cost, requirements list)
2. Eligibility criteria and any concerns
3. Compliance considerations for both countries
4. Timeline estimate (visa application, approval, relocation phases)
5. Required documentation list
6. Policy recommendations

Return your response in this EXACT JSON format:
{{
  "analysis": {{
    "visa_requirements": {{
      "visa_type": "<visa type>",
      "processing_time": "<time>",
      "cost": "<cost with currency>",
      "requirements": ["<req1>", "<req2>", "<req3>"]
    }},
    "eligibility": {{
      "meets_requirements": true/false,
      "concerns": ["<concern1>", "<concern2>"],
      "recommendations": ["<rec1>", "<rec2>"]
    }},
    "compliance": {{
      "origin_requirements": ["<req1>", "<req2>"],
      "destination_requirements": ["<req1>", "<req2>"],
      "key_considerations": ["<consideration1>", "<consideration2>"]
    }},
    "timeline": {{
      "visa_application": "<phase description>",
      "visa_approval": "<phase description>",
      "relocation_prep": "<phase description>",
      "start_date": "<phase description>"
    }},
    "documentation": ["<doc1>", "<doc2>", "<doc3>", "<doc4>"]
  }},
  "recommendations": ["<recommendation1>", "<recommendation2>", "<recommendation3>"],
  "confidence": 0.85
}}

IMPORTANT: Respond ONLY with valid JSON, no other text."""

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # Parse OpenAI response
        result_text = response.choices[0].message.content

        # Extract JSON from response
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        json_str = result_text[start_idx:end_idx]

        result = json.loads(json_str)

        # Add metadata
        result["status"] = "success"
        result["metadata"] = {
            "policy_version": "2024.Q4",
            "last_updated": "2024-10-16",
            "data_sources": ["OpenAI GPT-4", "General knowledge"],
            "model_type": "openai_gpt4o"
        }

        logger.info("Policy analysis successful via OpenAI")
        return result
        
    except Exception as e:
        logger.error(f"Policy analysis failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to analyze policy requirements"
        }


def get_visa_requirements(origin: str, destination: str) -> Dict:
    """Get visa requirements"""
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


def check_eligibility(assignment_type: str, duration: str) -> Dict:
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


def check_compliance(origin: str, destination: str) -> Dict:
    """Check compliance requirements"""
    return {
        "tax_implications": f"Tax resident in {destination} after 183 days",
        "social_security": "Check totalization agreement status",
        "work_permits": "Required for employment",
        "reporting": "Monthly assignment reports required"
    }


def estimate_timeline(destination: str, assignment_type: str) -> Dict:
    """Estimate timeline for assignment setup"""
    return {
        "visa_application": "Week 1-3",
        "visa_approval": "Week 4-6",
        "relocation_prep": "Week 7-8",
        "start_date": "Week 9-10"
    }


def required_documents(destination: str) -> list:
    """List required documents"""
    return [
        "Passport (valid 6+ months)",
        "Employment contract",
        "Educational certificates",
        "Background check",
        "Medical examination results",
        "Tax clearance certificate"
    ]


def policy_recommendations(
    origin: str, destination: str, 
    assignment_type: str, duration: str
) -> list:
    """Generate policy recommendations"""
    return [
        "Start visa process 4 months before planned start date",
        "Engage immigration counsel for complex cases",
        "Review tax implications with international tax team",
        "Ensure compliance with both home and host country regulations"
    ]


if __name__ == "__main__":
    # Run the FastAPI server
    import uvicorn
    logger.info("Starting Policy Analysis MCP Server on port 8082")
    uvicorn.run(app, host="0.0.0.0", port=8082)



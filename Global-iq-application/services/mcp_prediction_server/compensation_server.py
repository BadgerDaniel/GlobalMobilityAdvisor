"""
MCP Server for Compensation Predictions
Receives structured input from AGNO agent and returns predictions
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
app = FastAPI(title="Compensation Predictor MCP Server")

# Request model
class CompensationRequest(BaseModel):
    origin_location: str
    destination_location: str
    current_salary: float
    currency: str = "USD"
    assignment_duration: str = "12 months"
    job_level: str = "Manager"
    family_size: int = 1
    housing_preference: str = "Company-provided"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "compensation_predictor"}


@app.post("/predict")
async def predict_compensation_endpoint(request: CompensationRequest) -> Dict[str, Any]:
    """
    API endpoint for compensation prediction
    """
    return await predict_compensation(
        origin_location=request.origin_location,
        destination_location=request.destination_location,
        current_salary=request.current_salary,
        currency=request.currency,
        assignment_duration=request.assignment_duration,
        job_level=request.job_level,
        family_size=request.family_size,
        housing_preference=request.housing_preference
    )


async def predict_compensation(
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
    Predicts compensation package for international relocation using OpenAI.

    Args:
        origin_location: Current location (City, Country)
        destination_location: Destination location (City, Country)
        current_salary: Current annual salary
        currency: Currency code (USD, EUR, GBP, etc.)
        assignment_duration: Duration of assignment
        job_level: Job level/title
        family_size: Number of family members
        housing_preference: Housing preference

    Returns:
        Structured compensation prediction with breakdowns and recommendations
    """
    logger.info(f"Predicting compensation for: {origin_location} -> {destination_location}")

    try:
        # Use OpenAI to calculate compensation
        prompt = f"""You are a Global Mobility Compensation Expert. Calculate a comprehensive compensation package for an international employee relocation.

Input Data:
- Origin Location: {origin_location}
- Destination Location: {destination_location}
- Current Salary: {current_salary:,.2f} {currency}
- Assignment Duration: {assignment_duration}
- Job Level: {job_level}
- Family Size: {family_size}
- Housing Preference: {housing_preference}

Provide a detailed compensation calculation including:
1. COLA (Cost of Living Adjustment) ratio - compare living costs between cities
2. Adjusted base salary after COLA
3. Housing allowance based on destination city and family size
4. Hardship pay if applicable (based on destination difficulty)
5. Total compensation package

Also provide:
- Breakdown of each component
- Key recommendations
- Confidence level for calculations (as decimal 0-1)

Return your response in this EXACT JSON format:
{{
  "predictions": {{
    "base_salary": {current_salary},
    "cola_ratio": <decimal like 1.15>,
    "adjusted_salary": <number>,
    "housing_allowance": <number>,
    "hardship_pay": <number>,
    "total_package": <number>,
    "currency": "{currency}"
  }},
  "breakdown": {{
    "base_salary": {current_salary},
    "cola_adjustment": <adjusted_salary - base_salary>,
    "housing": <housing_allowance>,
    "hardship": <hardship_pay>
  }},
  "confidence_scores": {{
    "cola": <0-1>,
    "housing": <0-1>,
    "overall": <0-1>
  }},
  "recommendations": [
    "<recommendation 1>",
    "<recommendation 2>",
    "<recommendation 3>"
  ]
}}

IMPORTANT: Respond ONLY with valid JSON, no other text."""

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # Parse OpenAI response
        result_text = response.choices[0].message.content

        # Extract JSON from response (in case there's any wrapper text)
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        json_str = result_text[start_idx:end_idx]

        result = json.loads(json_str)

        # Add metadata
        result["status"] = "success"
        result["methodology"] = {
            "model_type": "openai_gpt4o",
            "data_sources": ["OpenAI GPT-4", "General knowledge"],
            "version": "2.0.0"
        }

        logger.info(f"Prediction successful via OpenAI")
        return result
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate compensation prediction"
        }


def calculate_cola(origin: str, destination: str) -> float:
    """Calculate Cost of Living Adjustment ratio"""
    cola_map = {
        ("New York", "London"): 1.15,
        ("New York", "Tokyo"): 1.25,
        ("New York", "Singapore"): 1.10,
        ("San Francisco", "London"): 1.20,
        ("Chicago", "London"): 1.30,
        ("London", "New York"): 0.87,
        ("default", "default"): 1.05
    }
    
    origin_city = origin.split(",")[0].strip()
    dest_city = destination.split(",")[0].strip()
    
    key = (origin_city, dest_city)
    return cola_map.get(key, cola_map[("default", "default")])


def calculate_housing(destination: str, family_size: int, preference: str) -> float:
    """Calculate housing allowance"""
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
    
    family_multiplier = 1 + (family_size - 1) * 0.2
    pref_multiplier = 1.0 if "company" in preference.lower() else 0.8
    
    monthly_allowance = base * family_multiplier * pref_multiplier
    return monthly_allowance * 12


def calculate_hardship(destination: str, duration: str) -> float:
    """Calculate hardship pay based on destination difficulty"""
    hardship_locations = {
        "Lagos": 0.15,
        "Riyadh": 0.10,
        "Mumbai": 0.08,
        "default": 0.0
    }
    
    dest_city = destination.split(",")[0].strip()
    hardship_rate = hardship_locations.get(dest_city, hardship_locations["default"])
    
    if "month" in duration.lower():
        months = int(''.join(filter(str.isdigit, duration)))
        if months < 6:
            hardship_rate = 0
    
    return hardship_rate


def generate_recommendations(
    base_salary: float, total_package: float, 
    destination: str, duration: str
) -> list:
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


if __name__ == "__main__":
    # Run the FastAPI server
    import uvicorn
    logger.info("Starting Compensation Prediction MCP Server on port 8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)



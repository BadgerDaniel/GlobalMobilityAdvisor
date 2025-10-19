# app/conversational_collector.py

"""
Conversational Input Collector
Uses LLM to intelligently extract information from natural conversation
and only asks for missing required fields
"""

from openai import AsyncOpenAI
import json
from typing import Dict, List, Tuple, Optional


class ConversationalCollector:
    """Intelligent conversational data collector using LLM"""

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

        # Define required fields for each route
        self.required_fields = {
            "compensation": {
                "Origin Location": "Employee's current city and country",
                "Destination Location": "Where the employee will relocate to",
                "Current Compensation": "Annual salary with currency",
                "Assignment Duration": "How long the assignment will last",
                "Job Level/Title": "Employee's position or seniority level",
                "Family Size": "Number of family members relocating (including employee)",
                "Housing Preference": "Preferred housing arrangement"
            },
            "policy": {
                "Origin Country": "Employee's current country",
                "Destination Country": "Country they're relocating to",
                "Assignment Type": "Type of assignment (Short-term, Long-term, Permanent, etc.)",
                "Assignment Duration": "Duration of the assignment",
                "Job Title": "Employee's job title or position"
            }
        }

    async def start_conversation(self, route: str) -> str:
        """
        Start the conversational intake

        Args:
            route: The route name (compensation or policy)

        Returns:
            Initial prompt asking user to describe their situation
        """
        if route == "compensation":
            return """💰 **Let's figure out your compensation package!**

Tell me about your relocation situation. Include any details you know, such as:
- Where you're moving from and to
- Your current salary
- How long you'll be there
- If family is coming with you
- Your role/position

**Just describe your situation in your own words - I'll ask follow-up questions for anything I need to know!**"""

        elif route == "policy":
            return """📋 **Let's analyze the policy requirements!**

Tell me about your international assignment. Include details like:
- Which countries are involved
- What type of assignment (short-term, long-term, permanent)
- How long it will be
- Your role/position

**Describe your situation naturally - I'll ask for any missing details!**"""

        else:
            return "Tell me about your situation and I'll help gather the information we need!"

    async def extract_information(
        self,
        route: str,
        user_message: str,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Extract structured information from user's natural language description

        Args:
            route: compensation or policy
            user_message: User's description
            conversation_history: Previous messages for context

        Returns:
            Dictionary with extracted fields and what's still missing
        """
        required = self.required_fields.get(route, {})

        # Build extraction prompt
        fields_list = "\n".join([f"- **{field}**: {desc}" for field, desc in required.items()])

        context = ""
        if conversation_history:
            context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                context += f"{msg['role']}: {msg['content']}\n"

        extraction_prompt = f"""You are an intelligent data extraction assistant for an HR global mobility system.

The user is an HR professional describing an employee relocation scenario. Extract information from their message to fill in these required fields:

{fields_list}

User's message: "{user_message}"{context}

Analyze the message and extract any information that matches these fields. Be intelligent about inference:
- If they mention a city, infer the country if obvious (e.g., "Chicago" = "Chicago, USA")
- Parse salary formats (100k, $100,000, etc.)
- Understand duration (2 years, 24 months, etc.)
- Infer assignment type from context
- Recognize third-person descriptions (e.g., "moving someone from Chicago" means Chicago is the origin)
- Family size should include the employee (e.g., "1 kid" = family of 2)

Return a JSON object with this EXACT structure:
{{
    "extracted_fields": {{
        "Field Name": "extracted value or null if not found"
    }},
    "confidence": {{
        "Field Name": 0.0-1.0 confidence score
    }},
    "missing_fields": ["Field Name 1", "Field Name 2"],
    "clarifications_needed": [
        {{
            "field": "Field Name",
            "question": "Natural follow-up question to ask user",
            "reason": "Why we need this information"
        }}
    ]
}}

IMPORTANT: Return ONLY valid JSON, no other text."""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.3
        )

        result_text = response.choices[0].message.content

        # Parse JSON response
        try:
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            json_str = result_text[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        except Exception as e:
            print(f"Error parsing extraction result: {e}")
            return {
                "extracted_fields": {},
                "confidence": {},
                "missing_fields": list(required.keys()),
                "clarifications_needed": []
            }

    async def generate_follow_up(
        self,
        route: str,
        extracted_data: Dict,
        missing_fields: List[str]
    ) -> str:
        """
        Generate a natural follow-up message

        Args:
            route: The route name
            extracted_data: Data already extracted
            missing_fields: Fields still needed

        Returns:
            Natural language follow-up message
        """
        if not missing_fields:
            # All data collected!
            return await self._generate_confirmation_message(route, extracted_data)

        # Generate smart follow-up
        required = self.required_fields.get(route, {})

        # Show what we captured
        captured = []
        for field, value in extracted_data.items():
            if value:
                captured.append(f"✓ **{field}**: {value}")

        captured_text = "\n".join(captured) if captured else ""

        # Ask for missing fields naturally
        missing_descriptions = [f"- {required[field]}" for field in missing_fields if field in required]

        prompt = f"""Generate a BRIEF, conversational follow-up message for an HR global mobility assistant chatbot.

The HR professional has provided this information about the employee relocation:
{captured_text}

We still need:
{chr(10).join(missing_descriptions)}

Generate a SHORT, friendly chat message (2-4 sentences MAX) that:
1. Briefly acknowledges what we've received (if anything)
2. Asks for the missing information naturally in a bulleted list
3. Uses professional third-person language (e.g., "What is the employee's role?" not "What's your role?")
4. Sounds like a helpful chatbot, NOT a formal business email

Example style: "Thanks! I've captured the origin and destination. To continue, I'll need a few more details: • What is the employee's current salary? • How long will the assignment be? • ..."

Return ONLY the message text, no JSON, no subject line, no signature."""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    async def _generate_confirmation_message(self, route: str, collected_data: Dict) -> str:
        """Generate confirmation message with all collected data"""

        summary = "**Here's what I've gathered:**\n\n"
        for field, value in collected_data.items():
            if value:
                summary += f"• **{field}**: {value}\n"

        summary += "\n**Is this information correct?** (Reply 'yes' to proceed or tell me what to change)"

        return summary

    def is_complete(self, extracted_data: Dict, route: str) -> bool:
        """Check if all required fields are collected"""
        required = self.required_fields.get(route, {})

        for field in required.keys():
            if field not in extracted_data or not extracted_data[field]:
                return False

        return True

    def format_for_mcp(self, route: str, collected_data: Dict) -> Dict:
        """
        Format collected data for MCP server

        Args:
            route: compensation or policy
            collected_data: Collected field data

        Returns:
            Dictionary formatted for MCP client
        """
        # The collected_data keys should already match what MCP expects
        return collected_data

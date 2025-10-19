#!/usr/bin/env python
# test_conversational_collector.py
"""
Test script for conversational collector
"""

import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from openai import AsyncOpenAI
from dotenv import load_dotenv
from conversational_collector import ConversationalCollector

load_dotenv()

async def test_extraction():
    """Test the conversational extraction"""

    # Initialize
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    collector = ConversationalCollector(openai_client=client)

    # Test queries
    test_cases = [
        {
            "query": "moving someone from chicago to mumbai",
            "expected_extracted": ["Origin Location", "Destination Location"],
            "expected_missing": ["Current Compensation", "Assignment Duration", "Job Level/Title", "Family Size", "Housing Preference"]
        },
        {
            "query": "moving someone from chicago to mumbai making 100k for 2 years",
            "expected_extracted": ["Origin Location", "Destination Location", "Current Compensation", "Assignment Duration"],
            "expected_missing": ["Job Level/Title", "Family Size", "Housing Preference"]
        },
        {
            "query": "Senior Engineer making $120k in Chicago moving to Mumbai for 2 years with family of 3, prefer company housing",
            "expected_extracted": ["Origin Location", "Destination Location", "Current Compensation", "Assignment Duration", "Job Level/Title", "Family Size", "Housing Preference"],
            "expected_missing": []
        }
    ]

    print("=" * 80)
    print("TESTING CONVERSATIONAL COLLECTOR")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}")
        print(f"{'='*80}")
        print(f"Query: {test_case['query']}")
        print()

        # Extract information
        extraction = await collector.extract_information(
            route="compensation",
            user_message=test_case['query'],
            conversation_history=[]
        )

        print("EXTRACTION RESULTS:")
        print("-" * 80)
        print(f"Extracted fields:")
        for field, value in extraction["extracted_fields"].items():
            if value:
                confidence = extraction["confidence"].get(field, 0)
                print(f"  [+] {field}: {value} (confidence: {confidence:.2f})")

        print(f"\nMissing fields:")
        for field in extraction["missing_fields"]:
            print(f"  [-] {field}")

        # Check if complete
        is_complete = collector.is_complete(extraction["extracted_fields"], "compensation")
        print(f"\nComplete: {'YES' if is_complete else 'NO'}")

        # Generate follow-up if not complete
        if not is_complete:
            print("\n" + "-" * 80)
            print("FOLLOW-UP MESSAGE:")
            print("-" * 80)
            follow_up = await collector.generate_follow_up(
                route="compensation",
                extracted_data=extraction["extracted_fields"],
                missing_fields=extraction["missing_fields"]
            )
            print(follow_up)
        else:
            print("\n" + "-" * 80)
            print("CONFIRMATION MESSAGE:")
            print("-" * 80)
            confirmation = await collector._generate_confirmation_message(
                route="compensation",
                collected_data=extraction["extracted_fields"]
            )
            print(confirmation)

        print()

    print("=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_extraction())

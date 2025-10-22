#!/usr/bin/env python
# test_full_flow.py
"""
Comprehensive test of the conversational intake system
Tests various scenarios and edge cases
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from openai import AsyncOpenAI
from dotenv import load_dotenv
from conversational_collector import ConversationalCollector

load_dotenv()

async def test_scenario(collector, scenario_name, query, expected_fields=None):
    """Test a single scenario"""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*80}")
    print(f"Query: \"{query}\"")
    print()

    # Extract information
    extraction = await collector.extract_information(
        route="compensation",
        user_message=query,
        conversation_history=[]
    )

    print("EXTRACTED FIELDS:")
    print("-" * 80)
    for field, value in extraction["extracted_fields"].items():
        if value:
            confidence = extraction["confidence"].get(field, 0)
            status = "[+]" if confidence > 0.7 else "[?]"
            print(f"  {status} {field}: {value} (confidence: {confidence:.2f})")

    print(f"\nMISSING FIELDS: {len(extraction['missing_fields'])}")
    for field in extraction["missing_fields"]:
        print(f"  [-] {field}")

    # Check completeness
    is_complete = collector.is_complete(extraction["extracted_fields"], "compensation")

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
        print("\n[COMPLETE] ALL FIELDS EXTRACTED")

    # Validation
    if expected_fields:
        print("\n" + "-" * 80)
        print("VALIDATION:")
        print("-" * 80)
        for field, expected_value in expected_fields.items():
            actual_value = extraction["extracted_fields"].get(field)
            if actual_value and expected_value.lower() in actual_value.lower():
                print(f"  [OK] {field}: PASS")
            else:
                print(f"  [FAIL] {field}: FAIL (expected '{expected_value}', got '{actual_value}')")

    return extraction

async def test_multi_turn_conversation(collector):
    """Test a multi-turn conversation"""
    print(f"\n{'='*80}")
    print(f"MULTI-TURN CONVERSATION TEST")
    print(f"{'='*80}")

    conversation_history = []
    collected_data = {}

    # Turn 1
    print("\nTURN 1:")
    print("User: 'relocating from NYC to London'")

    extraction = await collector.extract_information(
        route="compensation",
        user_message="relocating from NYC to London",
        conversation_history=conversation_history
    )

    for field, value in extraction["extracted_fields"].items():
        if value:
            collected_data[field] = value

    conversation_history.append({"role": "user", "content": "relocating from NYC to London"})

    follow_up = await collector.generate_follow_up(
        route="compensation",
        extracted_data=collected_data,
        missing_fields=extraction["missing_fields"]
    )

    conversation_history.append({"role": "assistant", "content": follow_up})
    print(f"Bot: {follow_up}")

    # Turn 2
    print("\nTURN 2:")
    print("User: 'salary is 150k, going for 3 years'")

    extraction = await collector.extract_information(
        route="compensation",
        user_message="salary is 150k, going for 3 years",
        conversation_history=conversation_history
    )

    for field, value in extraction["extracted_fields"].items():
        if value:
            collected_data[field] = value

    conversation_history.append({"role": "user", "content": "salary is 150k, going for 3 years"})

    if not collector.is_complete(collected_data, "compensation"):
        follow_up = await collector.generate_follow_up(
            route="compensation",
            extracted_data=collected_data,
            missing_fields=[f for f in collector.required_fields["compensation"].keys() if f not in collected_data or not collected_data[f]]
        )
        conversation_history.append({"role": "assistant", "content": follow_up})
        print(f"Bot: {follow_up}")

    # Turn 3
    print("\nTURN 3:")
    print("User: 'Director level, solo, prefer serviced apartment'")

    extraction = await collector.extract_information(
        route="compensation",
        user_message="Director level, solo, prefer serviced apartment",
        conversation_history=conversation_history
    )

    for field, value in extraction["extracted_fields"].items():
        if value:
            collected_data[field] = value

    print("\nFINAL COLLECTED DATA:")
    print("-" * 80)
    for field, value in collected_data.items():
        if value:
            print(f"  • {field}: {value}")

    is_complete = collector.is_complete(collected_data, "compensation")
    print(f"\nComplete: {'YES' if is_complete else 'NO'}")

async def main():
    """Run all tests"""
    print("="*80)
    print("CONVERSATIONAL INTAKE COMPREHENSIVE TESTING")
    print("="*80)

    # Initialize
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    collector = ConversationalCollector(openai_client=client)

    # Test scenarios
    scenarios = [
        {
            "name": "Minimal Info",
            "query": "moving someone from chicago to mumbai",
            "expected": {
                "Origin Location": "Chicago",
                "Destination Location": "Mumbai"
            }
        },
        {
            "name": "Moderate Info",
            "query": "moving someone from chicago to mumbai making 100k for 2 years",
            "expected": {
                "Origin Location": "Chicago",
                "Destination Location": "Mumbai",
                "Current Compensation": "100",
                "Assignment Duration": "2 years"
            }
        },
        {
            "name": "Complete Info",
            "query": "Senior Engineer making $120k in Chicago moving to Mumbai for 2 years with family of 3, prefer company housing",
            "expected": {
                "Origin Location": "Chicago",
                "Destination Location": "Mumbai",
                "Current Compensation": "120",
                "Assignment Duration": "2 years",
                "Job Level/Title": "Senior Engineer",
                "Family Size": "3",
                "Housing Preference": "company"
            }
        },
        {
            "name": "Informal Language",
            "query": "we got someone going from SF to Tokyo, they make like 180k, gonna be there 18 months",
            "expected": {
                "Origin Location": "SF",
                "Destination Location": "Tokyo",
                "Current Compensation": "180",
                "Assignment Duration": "18 months"
            }
        },
        {
            "name": "Currency Variations",
            "query": "Employee in London (£80k) relocating to New York for 1 year",
            "expected": {
                "Origin Location": "London",
                "Destination Location": "New York",
                "Current Compensation": "80",
                "Assignment Duration": "1 year"
            }
        },
        {
            "name": "Family Details",
            "query": "moving manager from Berlin to Singapore, 2 kids, spouse coming along",
            "expected": {
                "Origin Location": "Berlin",
                "Destination Location": "Singapore",
                "Family Size": "4"  # employee + spouse + 2 kids
            }
        },
        {
            "name": "Abbreviations",
            "query": "SVP making 250k USD relocating CHI to LON 24mo",
            "expected": {
                "Job Level/Title": "SVP",
                "Current Compensation": "250",
                "Origin Location": "CHI",
                "Destination Location": "LON",
                "Assignment Duration": "24"
            }
        },
        {
            "name": "Missing Critical Info",
            "query": "need to relocate someone",
            "expected": {}
        },
        {
            "name": "Ambiguous Family Size",
            "query": "moving from Paris to Dubai with wife and 2 children",
            "expected": {
                "Origin Location": "Paris",
                "Destination Location": "Dubai",
                "Family Size": "4"
            }
        }
    ]

    # Run single-turn scenarios
    for scenario in scenarios:
        await test_scenario(
            collector,
            scenario["name"],
            scenario["query"],
            scenario.get("expected")
        )
        await asyncio.sleep(1)  # Rate limiting

    # Test multi-turn conversation
    await test_multi_turn_conversation(collector)

    # Test edge cases
    print(f"\n{'='*80}")
    print("EDGE CASES")
    print(f"{'='*80}")

    edge_cases = [
        "What's the cheapest place to send someone?",  # Question instead of statement
        "We need help with relocation",  # Vague request
        "100k chicago mumbai 2yr fam3 eng corp",  # Ultra compressed
        "",  # Empty string
    ]

    for i, edge_case in enumerate(edge_cases, 1):
        print(f"\nEDGE CASE {i}: \"{edge_case}\"")
        try:
            extraction = await collector.extract_information(
                route="compensation",
                user_message=edge_case,
                conversation_history=[]
            )
            extracted_count = sum(1 for v in extraction["extracted_fields"].values() if v)
            print(f"  Extracted {extracted_count} fields")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())

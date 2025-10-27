"""
Quick test script to verify MCP integration is working
Run this before starting the full Chainlit app
"""

import sys
sys.path.insert(0, 'app')

import asyncio
from service_manager import MCPServiceManager
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_integration():
    print("=" * 60)
    print("MCP Integration Test")
    print("=" * 60)

    # Initialize client
    print("\n1. Initializing OpenAI client...")
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("   [OK] OpenAI client initialized")

    # Initialize service manager
    print("\n2. Initializing MCP Service Manager...")
    try:
        service_manager = MCPServiceManager(
            openai_client=client,
            compensation_server_url=os.getenv("COMPENSATION_SERVER_URL", "http://localhost:8081"),
            policy_server_url=os.getenv("POLICY_SERVER_URL", "http://localhost:8082"),
            enable_mcp=os.getenv("ENABLE_MCP", "true").lower() == "true"
        )
        print(f"   [OK] Service manager initialized (MCP enabled: {service_manager.enable_mcp})")
    except Exception as e:
        print(f"   [X] Failed to initialize service manager: {e}")
        return False

    # Check health
    print("\n3. Checking MCP server health...")
    health_status = await service_manager.get_health_status()

    if health_status.get('mcp_enabled'):
        servers = health_status.get('servers', {})
        print(f"   MCP Enabled: {health_status['mcp_enabled']}")
        print(f"   Compensation Server: {'[OK] Healthy' if servers.get('compensation_server') else '[X] Down'}")
        print(f"   Policy Server: {'[OK] Healthy' if servers.get('policy_server') else '[X] Down'}")

        all_healthy = all(servers.values())
        if all_healthy:
            print("\n   [OK] All servers are healthy - MCP integration will be used")
        else:
            print("\n   [!] Some servers are down - Will use GPT-4 fallback")
    else:
        print(f"   MCP Disabled: {health_status.get('reason', 'Unknown')}")
        print("   [i] All requests will use GPT-4 fallback")

    # Test compensation prediction
    print("\n4. Testing compensation prediction...")
    test_data = {
        "Origin Location": "New York, USA",
        "Destination Location": "London, UK",
        "Current Compensation": "$100,000 USD",
        "Assignment Duration": "24 months",
        "Job Level/Title": "Senior Engineer",
        "Family Size": "1",
        "Housing Preference": "Company-provided"
    }

    try:
        result = await service_manager.predict_compensation(
            collected_data=test_data,
            extracted_texts=[]
        )
        print("   [OK] Compensation prediction successful")
        print(f"   Response length: {len(result)} characters")

        # Check if MCP or fallback was used
        if "(via MCP)" in result:
            print("   [OK] Used MCP server")
        elif "(via Fallback GPT-4)" in result:
            print("   [OK] Used GPT-4 fallback")

    except Exception as e:
        print(f"   [X] Compensation prediction failed: {e}")

    # Get statistics
    print("\n5. Usage Statistics:")
    stats = service_manager.get_statistics()
    print(f"   MCP Calls: {stats['mcp_calls']}")
    print(f"   Fallback Calls: {stats['fallback_calls']}")
    print(f"   Errors: {stats['errors']}")

    print("\n" + "=" * 60)
    print("Integration test complete!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    print("\nTesting MCP Integration...\n")

    # Check if MCP servers should be running
    enable_mcp = os.getenv("ENABLE_MCP", "true").lower() == "true"
    if enable_mcp:
        print("Note: ENABLE_MCP=true in .env")
        print("      Make sure MCP servers are running:")
        print("      Terminal 1: python services/mcp_prediction_server/compensation_server.py")
        print("      Terminal 2: python services/mcp_prediction_server/policy_server.py")
        print()
    else:
        print("Note: ENABLE_MCP=false in .env - will test fallback only\n")

    try:
        success = asyncio.run(test_integration())
        if success:
            print("\n[OK] Ready to start Chainlit app: chainlit run app/main.py")
        else:
            print("\n[X] Fix issues before starting app")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n[X] Test failed with error: {e}")
        import traceback
        traceback.print_exc()

"""Quick test to verify MCP servers and environment setup"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_basic():
    print("=" * 60)
    print("Testing Global IQ Setup")
    print("=" * 60)
    print()

    all_passed = True

    # Check environment variables
    print("1. Checking environment variables...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        print("   ❌ Please set your OPENAI_API_KEY in .env file")
        all_passed = False
    else:
        # Mask the key for security
        masked_key = api_key[:7] + "..." + api_key[-4:]
        print(f"   ✅ OpenAI API key found: {masked_key}")

    comp_url = os.getenv("COMPENSATION_SERVER_URL", "http://localhost:8081")
    policy_url = os.getenv("POLICY_SERVER_URL", "http://localhost:8082")
    print(f"   ✅ Compensation server URL: {comp_url}")
    print(f"   ✅ Policy server URL: {policy_url}")
    print()

    # Test MCP server connection
    print("2. Testing MCP server connections...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            # Test compensation server
            try:
                response = await client.get(f"{comp_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print(f"   ✅ Compensation server is running ({comp_url})")
                else:
                    print(f"   ❌ Compensation server error: {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ Cannot connect to compensation server: {e}")
                print(f"      Make sure it's running: python services/mcp_prediction_server/compensation_server.py")
                all_passed = False

            # Test policy server
            try:
                response = await client.get(f"{policy_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print(f"   ✅ Policy server is running ({policy_url})")
                else:
                    print(f"   ❌ Policy server error: {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ Cannot connect to policy server: {e}")
                print(f"      Make sure it's running: python services/mcp_prediction_server/policy_server.py")
                all_passed = False
    except ImportError:
        print("   ❌ httpx not installed. Run: pip install httpx")
        all_passed = False
    print()

    # Test package imports
    print("3. Testing package imports...")
    try:
        import chainlit
        print("   ✅ Chainlit imported")
    except ImportError:
        print("   ❌ Chainlit not installed")
        all_passed = False

    try:
        from openai import AsyncOpenAI
        print("   ✅ OpenAI imported")
    except ImportError:
        print("   ❌ OpenAI not installed")
        all_passed = False

    try:
        from agno.agent import Agent
        print("   ✅ AGNO imported")
    except ImportError:
        print("   ❌ AGNO not installed")
        all_passed = False

    try:
        from mcp import StdioServerParameters
        print("   ✅ MCP imported")
    except ImportError:
        print("   ❌ MCP not installed")
        all_passed = False
    print()

    # Summary
    print("=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED! You're ready to go!")
        print()
        print("Next steps:")
        print("1. Start the Chainlit app:")
        print("   chainlit run app/main.py")
        print()
        print("2. Open browser: http://localhost:8000")
        print("3. Login with: demo / demo")
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Please fix the errors above before proceeding.")
        print("See GETTING_STARTED.md for detailed instructions.")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    result = asyncio.run(test_basic())
    exit(0 if result else 1)

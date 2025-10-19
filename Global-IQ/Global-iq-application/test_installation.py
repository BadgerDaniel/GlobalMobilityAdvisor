"""
Test script to verify AGNO and MCP installation
Run this after installing packages to ensure everything is set up correctly
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...\n")
    
    tests = []
    
    # Test AGNO
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.tools.mcp import MCPTools
        print("[SUCCESS] AGNO installed successfully")
        tests.append(True)
    except ImportError as e:
        print(f"[ERROR] AGNO import failed: {e}")
        tests.append(False)
    
    # Test MCP
    try:
        from mcp import StdioServerParameters
        from mcp.server.fastmcp import FastMCP
        print("[SUCCESS] MCP installed successfully")
        tests.append(True)
    except ImportError as e:
        print(f"[ERROR] MCP import failed: {e}")
        tests.append(False)
    
    # Test FastAPI
    try:
        from fastapi import FastAPI
        print("[SUCCESS] FastAPI installed successfully")
        tests.append(True)
    except ImportError as e:
        print(f"[ERROR] FastAPI import failed: {e}")
        tests.append(False)
    
    # Test Uvicorn
    try:
        import uvicorn
        print("[SUCCESS] Uvicorn installed successfully")
        tests.append(True)
    except ImportError as e:
        print(f"[ERROR] Uvicorn import failed: {e}")
        tests.append(False)
    
    # Test existing packages
    try:
        import chainlit
        print("[SUCCESS] Chainlit installed successfully")
        tests.append(True)
    except ImportError as e:
        print(f"[ERROR] Chainlit import failed: {e}")
        tests.append(False)
    
    try:
        from openai import AsyncOpenAI
        print("[SUCCESS] OpenAI installed successfully")
        tests.append(True)
    except ImportError as e:
        print(f"[ERROR] OpenAI import failed: {e}")
        tests.append(False)
    
    print(f"\n{'='*50}")
    if all(tests):
        print("[SUCCESS] All packages installed correctly!")
        print("\nYou're ready to proceed with AGNO + MCP integration.")
        print("\nNext steps:")
        print("1. Start MCP servers:")
        print("   python services/mcp_prediction_server/compensation_server.py")
        print("   python services/mcp_prediction_server/policy_server.py")
        print("2. Test the integration with your Chainlit app")
        return 0
    else:
        print(f"[WARNING] {sum(not t for t in tests)} package(s) failed to import")
        print("\nPlease install missing packages:")
        print("pip install agno mcp fastapi uvicorn")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())


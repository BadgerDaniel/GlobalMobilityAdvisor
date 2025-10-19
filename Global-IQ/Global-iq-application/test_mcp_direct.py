"""
Direct test of MCP servers without AGNO
Use this to verify MCP servers are working before testing AGNO integration
"""

import requests
import json

def test_compensation_server():
    """Test compensation MCP server directly"""
    print("\n" + "="*60)
    print("Testing Compensation MCP Server (port 8081)")
    print("="*60)
    
    url = "http://localhost:8081/predict_compensation"
    
    payload = {
        "origin_location": "New York, USA",
        "destination_location": "London, UK",
        "current_salary": 100000,
        "currency": "USD",
        "assignment_duration": "12 months",
        "job_level": "Senior Engineer",
        "family_size": 2,
        "housing_preference": "Company-provided"
    }
    
    try:
        print(f"\n[INFO] Sending request to {url}")
        print(f"[INFO] Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] Compensation server responded!")
            print(f"\nTotal Package: ${result['predictions']['total_package']:,.2f}")
            print(f"COLA Ratio: {result['predictions']['cola_ratio']}")
            print(f"Housing Allowance: ${result['predictions']['housing_allowance']:,.2f}")
            print(f"Overall Confidence: {result['confidence_scores']['overall']*100:.1f}%")
            print(f"\nRecommendations:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
            return True
        else:
            print(f"\n[ERROR] Server returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to compensation server")
        print("Make sure the server is running:")
        print("  python services/mcp_prediction_server/compensation_server.py")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False


def test_policy_server():
    """Test policy MCP server directly"""
    print("\n" + "="*60)
    print("Testing Policy MCP Server (port 8082)")
    print("="*60)
    
    url = "http://localhost:8082/analyze_policy"
    
    payload = {
        "origin_country": "USA",
        "destination_country": "UK",
        "assignment_type": "Long-term",
        "duration": "24 months",
        "job_title": "Software Engineer"
    }
    
    try:
        print(f"\n[INFO] Sending request to {url}")
        print(f"[INFO] Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] Policy server responded!")
            
            visa = result['analysis']['visa_requirements']
            print(f"\nVisa Type: {visa['visa_type']}")
            print(f"Processing Time: {visa['processing_time']}")
            print(f"Cost: {visa['cost']}")
            
            eligibility = result['analysis']['eligibility']
            print(f"\nMeets Requirements: {eligibility['meets_requirements']}")
            
            print(f"\nRecommendations:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
            return True
        else:
            print(f"\n[ERROR] Server returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to policy server")
        print("Make sure the server is running:")
        print("  python services/mcp_prediction_server/policy_server.py")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MCP Server Direct Test")
    print("="*60)
    print("\nThis script tests MCP servers directly (without AGNO)")
    print("Make sure both servers are running before running this test")
    print("\nTo start servers:")
    print("  1. Run START_MCP_SERVERS.bat")
    print("  OR")
    print("  2. Manually start in separate terminals:")
    print("     python services/mcp_prediction_server/compensation_server.py")
    print("     python services/mcp_prediction_server/policy_server.py")
    
    input("\nPress Enter to start tests...")
    
    # Run tests
    comp_result = test_compensation_server()
    policy_result = test_policy_server()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Compensation Server: {'[SUCCESS]' if comp_result else '[FAILED]'}")
    print(f"Policy Server: {'[SUCCESS]' if policy_result else '[FAILED]'}")
    
    if comp_result and policy_result:
        print("\n[SUCCESS] All MCP servers are working correctly!")
        print("\nNext steps:")
        print("1. Test AGNO integration with: python test_agno.py")
        print("2. Modify main.py to use AGNO client")
        print("3. Run full Chainlit app: chainlit run app/main.py")
    else:
        print("\n[WARNING] Some servers failed. Check the errors above.")
        print("Make sure servers are running and try again.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()








#!/bin/bash

# Test Examples for MCP Servers
# Run this to verify your implementation matches the contract

echo "======================================"
echo "MCP Server Testing Suite"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local data=$3

    echo "Testing: $name"

    if [ -z "$data" ]; then
        # GET request
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        # POST request
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓${NC} Success (HTTP $http_code)"
        echo "Response: $(echo $body | jq -C '.' 2>/dev/null || echo $body)"
    else
        echo -e "${RED}✗${NC} Failed (HTTP $http_code)"
        echo "Response: $body"
    fi
    echo ""
}

# Test Compensation Server
echo "======================================"
echo "1. Compensation Server (Port 8081)"
echo "======================================"
echo ""

test_endpoint \
    "Health Check" \
    "http://localhost:8081/health"

test_endpoint \
    "Predict Compensation" \
    "http://localhost:8081/predict" \
    '{
        "origin_location": "New York, USA",
        "destination_location": "London, UK",
        "current_salary": 100000,
        "currency": "USD",
        "assignment_duration": "24 months",
        "job_level": "Senior Engineer",
        "family_size": 3,
        "housing_preference": "Company-provided"
    }'

# Test Policy Server
echo "======================================"
echo "2. Policy Server (Port 8082)"
echo "======================================"
echo ""

test_endpoint \
    "Health Check" \
    "http://localhost:8082/health"

test_endpoint \
    "Analyze Policy" \
    "http://localhost:8082/analyze" \
    '{
        "origin_country": "United States",
        "destination_country": "United Kingdom",
        "assignment_type": "Long-term",
        "duration": "24 months",
        "job_title": "Senior Engineer"
    }'

# Summary
echo "======================================"
echo "Testing Complete"
echo "======================================"
echo ""
echo "Next Steps:"
echo "1. Verify all tests passed (✓)"
echo "2. Check response formats match MCP_CONTRACT.md"
echo "3. Test with interactive docs:"
echo "   - Compensation: http://localhost:8081/docs"
echo "   - Policy: http://localhost:8082/docs"
echo ""

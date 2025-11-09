@echo off
REM Test Examples for MCP Servers (Windows)
REM Run this to verify your implementation matches the contract

echo ======================================
echo MCP Server Testing Suite
echo ======================================
echo.

echo ======================================
echo 1. Compensation Server (Port 8081)
echo ======================================
echo.

echo Testing: Health Check
curl -s http://localhost:8081/health
echo.
echo.

echo Testing: Predict Compensation
curl -s -X POST http://localhost:8081/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"origin_location\":\"New York, USA\",\"destination_location\":\"London, UK\",\"current_salary\":100000,\"currency\":\"USD\",\"assignment_duration\":\"24 months\",\"job_level\":\"Senior Engineer\",\"family_size\":3,\"housing_preference\":\"Company-provided\"}"
echo.
echo.

echo ======================================
echo 2. Policy Server (Port 8082)
echo ======================================
echo.

echo Testing: Health Check
curl -s http://localhost:8082/health
echo.
echo.

echo Testing: Analyze Policy
curl -s -X POST http://localhost:8082/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"origin_country\":\"United States\",\"destination_country\":\"United Kingdom\",\"assignment_type\":\"Long-term\",\"duration\":\"24 months\",\"job_title\":\"Senior Engineer\"}"
echo.
echo.

echo ======================================
echo Testing Complete
echo ======================================
echo.
echo Next Steps:
echo 1. Verify all responses returned successfully
echo 2. Check response formats match MCP_CONTRACT.md
echo 3. Test with interactive docs:
echo    - Compensation: http://localhost:8081/docs
echo    - Policy: http://localhost:8082/docs
echo.

pause

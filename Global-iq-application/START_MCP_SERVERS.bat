@echo off
echo ================================================
echo Starting Global IQ MCP Servers
echo ================================================
echo.

echo Starting Compensation Server (Port 8081)...
start "Compensation Server" cmd /k "cd /d %~dp0 && python services\mcp_prediction_server\compensation_server.py"

timeout /t 2 /nobreak >nul

echo Starting Policy Server (Port 8082)...
start "Policy Server" cmd /k "cd /d %~dp0 && python services\mcp_prediction_server\policy_server.py"

timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo Both MCP servers started!
echo ================================================
echo.
echo Compensation Server: http://localhost:8081/docs
echo Policy Server:       http://localhost:8082/docs
echo.
echo Press any key to test servers...
pause >nul

echo.
echo Testing servers...
curl -s http://localhost:8081/health
echo.
curl -s http://localhost:8082/health
echo.
echo.
echo ================================================
echo Setup complete! Servers are running.
echo ================================================
echo.
echo To stop servers, close the server windows.
echo.
pause


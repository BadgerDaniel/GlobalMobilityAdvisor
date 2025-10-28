@echo off
REM Script to run tests for Global IQ application (Windows)

echo ========================================
echo Global IQ Test Runner
echo ========================================
echo.

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pytest not found. Installing test dependencies...
    pip install -r requirements-test.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
)

echo [INFO] Running tests...
echo.

REM Run tests based on argument
if "%1"=="" (
    REM No argument - run all tests with coverage
    python -m pytest --cov=app --cov-report=term-missing --cov-report=html -v
) else if "%1"=="quick" (
    REM Quick run - no coverage
    python -m pytest -v
) else if "%1"=="coverage" (
    REM Coverage only
    python -m pytest --cov=app --cov-report=term-missing --cov-report=html
) else if "%1"=="html" (
    REM Generate HTML coverage and open
    python -m pytest --cov=app --cov-report=html
    start htmlcov\index.html
) else if "%1"=="failed" (
    REM Run only failed tests
    python -m pytest --lf -v
) else if "%1"=="parallel" (
    REM Run tests in parallel
    python -m pytest -n auto -v
) else if "%1"=="router" (
    REM Run only router tests
    python -m pytest tests/test_enhanced_agent_router.py -v
) else if "%1"=="collector" (
    REM Run only collector tests
    python -m pytest tests/test_conversational_collector.py tests/test_input_collector.py -v
) else if "%1"=="auth" (
    REM Run only authentication tests
    python -m pytest tests/test_authentication.py -v
) else if "%1"=="files" (
    REM Run only file processing tests
    python -m pytest tests/test_file_processing.py -v
) else (
    REM Run specific test file
    python -m pytest %* -v
)

echo.
echo ========================================
echo Tests complete!
echo ========================================
echo.

if "%1"=="coverage" (
    echo Coverage report saved to htmlcov\index.html
    echo Open with: start htmlcov\index.html
)

if "%1"=="html" (
    echo Coverage report opened in browser
)

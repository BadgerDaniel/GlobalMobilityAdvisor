#!/bin/bash
# Script to run tests for Global IQ application (Linux/macOS)

echo "========================================"
echo "Global IQ Test Runner"
echo "========================================"
echo ""

# Check if pytest is installed
if ! python -m pytest --version &> /dev/null; then
    echo "[ERROR] pytest not found. Installing test dependencies..."
    pip install -r requirements-test.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
fi

echo "[INFO] Running tests..."
echo ""

# Run tests based on argument
case "$1" in
    "")
        # No argument - run all tests with coverage
        python -m pytest --cov=app --cov-report=term-missing --cov-report=html -v
        ;;
    "quick")
        # Quick run - no coverage
        python -m pytest -v
        ;;
    "coverage")
        # Coverage only
        python -m pytest --cov=app --cov-report=term-missing --cov-report=html
        ;;
    "html")
        # Generate HTML coverage and open
        python -m pytest --cov=app --cov-report=html
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open htmlcov/index.html
        else
            xdg-open htmlcov/index.html 2>/dev/null || echo "Please open htmlcov/index.html manually"
        fi
        ;;
    "failed")
        # Run only failed tests
        python -m pytest --lf -v
        ;;
    "parallel")
        # Run tests in parallel
        python -m pytest -n auto -v
        ;;
    "router")
        # Run only router tests
        python -m pytest tests/test_enhanced_agent_router.py -v
        ;;
    "collector")
        # Run only collector tests
        python -m pytest tests/test_conversational_collector.py tests/test_input_collector.py -v
        ;;
    "auth")
        # Run only authentication tests
        python -m pytest tests/test_authentication.py -v
        ;;
    "files")
        # Run only file processing tests
        python -m pytest tests/test_file_processing.py -v
        ;;
    *)
        # Run specific test file or pattern
        python -m pytest "$@" -v
        ;;
esac

echo ""
echo "========================================"
echo "Tests complete!"
echo "========================================"
echo ""

if [ "$1" == "coverage" ]; then
    echo "Coverage report saved to htmlcov/index.html"
    echo "Open with: open htmlcov/index.html (macOS) or xdg-open htmlcov/index.html (Linux)"
fi

if [ "$1" == "html" ]; then
    echo "Coverage report opened in browser"
fi

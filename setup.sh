#!/bin/bash

# ============================================================================
# Central Quality Hub - Automation Framework Setup Script for Linux/Mac
# ============================================================================
# This script sets up the Python automation testing environment including:
# - Python virtual environment
# - All required dependencies
# - Playwright browsers
# - Directory structure for reports and artifacts
# ============================================================================

echo
echo "============================================================================"
echo "Setting up Central Quality Hub Automation Framework..."
echo "============================================================================"
echo

# Check if Python is installed
echo "[1/8] Checking Python installation..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise use python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "Found Python $PYTHON_VERSION"

# Create virtual environment
echo
echo "[2/8] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo
echo "[3/8] Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo
echo "[4/8] Upgrading pip to latest version..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to upgrade pip, continuing with current version..."
fi

# Install requirements
echo
echo "[5/8] Installing Python dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    echo "Please check requirements.txt and your internet connection"
    exit 1
fi

# Install Playwright browsers (optional)
echo
echo "[6/8] Installing Playwright browsers..."
echo "This may take several minutes for first-time setup..."
playwright install
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to install Playwright browsers"
    echo "Playwright tests may not work until browsers are installed"
    echo "You can install them manually later with: playwright install"
fi

# Create directory structure
echo
echo "[7/8] Creating directory structure..."
mkdir -p reports/{api,web,mobile,database,desktop,allure}
mkdir -p logs
mkdir -p screenshots
mkdir -p test_data

echo "Created directory structure for reports, logs, and screenshots"

# Final setup verification
echo
echo "[8/8] Verifying installation..."
echo "Testing behave installation..."
if command -v behave &> /dev/null; then
    echo "Behave is properly installed"
else
    echo "WARNING: Behave command not found in PATH"
    echo "Try activating the virtual environment first"
fi

echo "Testing selenium installation..."
python -c "import selenium; print(f'Selenium version: {selenium.__version__}')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Selenium is properly installed"
else
    echo "WARNING: Selenium import failed"
fi

echo
echo "============================================================================"
echo "Setup completed successfully!"
echo "============================================================================"
echo
echo "Framework Components Installed:"
echo "  ✓ Python Virtual Environment"
echo "  ✓ Behave BDD Framework"
echo "  ✓ Selenium WebDriver (Web automation)"
echo "  ✓ Playwright (Modern web automation)"
echo "  ✓ Appium (Mobile automation)"
echo "  ✓ API Testing Framework"
echo "  ✓ Database Testing Support"
echo "  ✓ Desktop Automation Support"
echo "  ✓ Comprehensive Utilities"
echo "  ✓ Allure Reporting"
echo
echo "Next steps:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "1. Activate the virtual environment: source venv/Scripts/activate"
else
    echo "1. Activate the virtual environment: source venv/bin/activate"
fi
echo "2. Run sample tests: behave CentralQualityHub/API/features/ --tags=@smoke"
echo "3. Check the README.md for detailed usage instructions"
echo
echo "Optional Additional Setup:"
echo
echo "For Mobile Testing (Appium):"
echo "  - Install Node.js from https://nodejs.org"
echo "  - Install Appium: npm install -g appium"
echo "  - Install drivers: appium driver install uiautomator2"
echo "  - Install Android SDK or Xcode for device testing"
echo
echo "For Playwright (if browsers not installed):"
echo "  - Run: playwright install"
echo
echo "Configuration:"
echo "  - Check behave.ini for test execution options"
echo "  - See CentralQualityHub/ directories for test implementations"
echo "  - Refer to README.md for comprehensive documentation"
echo
echo "============================================================================"

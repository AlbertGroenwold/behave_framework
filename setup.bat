@echo off
REM ============================================================================
REM Central Quality Hub - Automation Framework Setup Script for Windows
REM ============================================================================
REM This script sets up the Python automation testing environment including:
REM - Python virtual environment
REM - All required dependencies
REM - Playwright browsers
REM - Directory structure for reports and artifacts
REM ============================================================================

echo.
echo ============================================================================
echo Setting up Central Quality Hub Automation Framework...
echo ============================================================================
echo.

REM Check if Python is installed
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Create virtual environment
echo.
echo [2/8] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, removing old one...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo.
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo [4/8] Upgrading pip to latest version...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing with current version...
)

REM Install requirements
echo.
echo [5/8] Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    echo Please check requirements.txt and your internet connection
    pause
    exit /b 1
)

REM Install Playwright browsers (optional)
echo.
echo [6/8] Installing Playwright browsers...
echo This may take several minutes for first-time setup...
playwright install
if errorlevel 1 (
    echo WARNING: Failed to install Playwright browsers
    echo Playwright tests may not work until browsers are installed
    echo You can install them manually later with: playwright install
)

REM Create directory structure
echo.
echo [7/8] Creating directory structure...
if not exist "reports" mkdir reports
if not exist "reports\api" mkdir reports\api
if not exist "reports\web" mkdir reports\web
if not exist "reports\mobile" mkdir reports\mobile
if not exist "reports\database" mkdir reports\database
if not exist "reports\desktop" mkdir reports\desktop
if not exist "reports\allure" mkdir reports\allure

REM Create logs directory
if not exist "logs" mkdir logs

REM Create screenshots directory
if not exist "screenshots" mkdir screenshots

REM Create test data directory (if needed)
if not exist "test_data" mkdir test_data

echo Created directory structure for reports, logs, and screenshots

REM Final setup verification
echo.
echo [8/8] Verifying installation...
echo Testing behave installation...
behave --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Behave command not found in PATH
    echo Try running: venv\Scripts\activate.bat
) else (
    echo Behave is properly installed
)

echo Testing selenium installation...
python -c "import selenium; print(f'Selenium version: {selenium.__version__}')" 2>nul
if errorlevel 1 (
    echo WARNING: Selenium import failed
) else (
    echo Selenium is properly installed
)

echo.
echo ============================================================================
echo Setup completed successfully!
echo ============================================================================
echo.
echo Framework Components Installed:
echo   ✓ Python Virtual Environment
echo   ✓ Behave BDD Framework
echo   ✓ Selenium WebDriver (Web automation)
echo   ✓ Playwright (Modern web automation)
echo   ✓ Appium (Mobile automation)
echo   ✓ API Testing Framework
echo   ✓ Database Testing Support
echo   ✓ Desktop Automation Support
echo   ✓ Comprehensive Utilities
echo   ✓ Allure Reporting
echo.
echo Next steps:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run sample tests: behave CentralQualityHub\API\features\ --tags=@smoke
echo 3. Check the README.md for detailed usage instructions
echo.
echo Optional Additional Setup:
echo.
echo For Mobile Testing (Appium):
echo   - Install Node.js from https://nodejs.org
echo   - Install Appium: npm install -g appium
echo   - Install drivers: appium driver install uiautomator2
echo   - Install Android SDK or Xcode for device testing
echo.
echo For Playwright (if browsers not installed):
echo   - Run: playwright install
echo.
echo Configuration:
echo   - Check behave.ini for test execution options
echo   - See CentralQualityHub/ directories for test implementations
echo   - Refer to README.md for comprehensive documentation
echo.
echo ============================================================================

REM Keep window open to show results
pause

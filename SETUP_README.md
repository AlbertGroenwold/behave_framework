# 🚀 Setup Guide - Central Quality Hub Automation Framework

## 📋 Table of Contents
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Detailed Installation](#-detailed-installation)
- [Environment Configuration](#-environment-configuration)
- [Framework Verification](#-framework-verification)
- [IDE Setup](#-ide-setup)
- [Troubleshooting](#-troubleshooting)
- [Advanced Configuration](#-advanced-configuration)

## 🔧 Prerequisites

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Ubuntu 20.04+
- **Python**: 3.9+ (Recommended: Python 3.11 or later)
- **RAM**: 8GB minimum (16GB recommended for parallel execution)
- **Storage**: 5GB free space (10GB recommended with browsers)
- **Network**: Internet connection for package downloads and browser installations

#### Software Dependencies
- **Git**: For version control and repository management
- **Node.js**: 18+ (Required for Appium and Playwright)
- **Java JDK**: 11+ (Required for Appium Android testing)

### Platform-Specific Prerequisites

#### Windows
```powershell
# Check if prerequisites are installed
python --version          # Should be 3.9+
git --version             # Should be 2.0+
node --version            # Should be 18+
java -version             # Should be 11+

# Install missing prerequisites using Chocolatey (recommended)
# Install Chocolatey first: https://chocolatey.org/install
choco install python git nodejs openjdk
```

#### macOS
```bash
# Check if prerequisites are installed
python3 --version        # Should be 3.9+
git --version           # Should be 2.0+
node --version          # Should be 18+
java -version           # Should be 11+

# Install missing prerequisites using Homebrew
# Install Homebrew first: https://brew.sh/
brew install python git node openjdk@11

# For iOS testing (optional)
xcode-select --install   # Install Xcode Command Line Tools
```

#### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt update

# Check if prerequisites are installed
python3 --version        # Should be 3.9+
git --version           # Should be 2.0+
node --version          # Should be 18+
java -version           # Should be 11+

# Install missing prerequisites
sudo apt install python3 python3-pip python3-venv git curl

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install Java 11+
sudo apt install openjdk-11-jdk

# Additional dependencies for desktop automation
sudo apt install xvfb x11-utils libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libfontconfig1 libfreetype6 libgl1 libxss1 libasound2
```

## ⚡ Quick Start

### 1. Clone Repository
```bash
# Clone the repository
git clone https://github.com/AlbertGroenwold/cqh_behave_framework.git
cd cqh_behave_framework/automation_framework/behave_automation

# Or if you already have the repository
cd path/to/central_quality_hub/automation_framework/behave_automation
```

### 2. Automated Setup (Recommended)

#### Windows
```powershell
# Run the automated setup script
.\setup.bat

# If execution policy prevents running scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.bat
```

#### macOS/Linux
```bash
# Make the setup script executable and run it
chmod +x setup.sh
./setup.sh
```

### 3. Manual Setup (If automated setup fails)

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install framework dependencies
pip install -r requirements.txt

# Install Playwright browsers (for web testing)
playwright install

# Install Appium dependencies (for mobile testing)
npm install -g appium
appium driver install uiautomator2  # For Android
appium driver install xcuitest      # For iOS (macOS only)
```

### 4. Verify Installation
```bash
# Quick verification test
python -c "import behave, selenium, playwright, requests; print('✅ All core dependencies installed successfully')"

# Run smoke tests
behave --tags=@smoke --format=pretty
```

## 📦 Detailed Installation

### Python Environment Setup

#### 1. Python Installation
Download and install Python 3.9+ from [python.org](https://python.org/downloads/).

**Important**: During installation, ensure you check "Add Python to PATH".

#### 2. Virtual Environment Creation
```bash
# Navigate to project directory
cd path/to/behave_automation

# Create virtual environment with specific Python version
python3.11 -m venv venv_automation  # Use specific Python version
# OR
python -m venv venv_automation       # Use default Python

# Activate virtual environment
# Windows PowerShell
venv_automation\Scripts\Activate.ps1
# Windows Command Prompt
venv_automation\Scripts\activate.bat
# macOS/Linux
source venv_automation/bin/activate

# Verify activation (should show virtual environment path)
which python
```

#### 3. Dependency Installation
```bash
# Ensure latest pip
python -m pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt  # If this file exists

# Install specific optional dependencies
pip install allure-behave          # For enhanced reporting
pip install pytest-html            # For HTML reports
pip install python-dotenv          # For environment variable management
```

### Browser Setup

#### Selenium WebDriver Setup
```bash
# Install webdriver-manager (handles driver downloads automatically)
pip install webdriver-manager

# Or manually download drivers:
# Chrome: https://chromedriver.chromium.org/
# Firefox: https://github.com/mozilla/geckodriver/releases
# Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

#### Playwright Browser Setup
```bash
# Install Playwright browsers
playwright install

# Install specific browsers only
playwright install chromium
playwright install firefox
playwright install webkit

# Install browsers with system dependencies (Linux)
playwright install-deps
```

### Mobile Testing Setup

#### Android Setup
```bash
# Install Android SDK (via Android Studio or command line tools)
# Download from: https://developer.android.com/studio

# Set environment variables (add to your shell profile)
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Install Appium
npm install -g appium
appium driver install uiautomator2

# Verify setup
appium driver list
adb version
```

#### iOS Setup (macOS only)
```bash
# Install Xcode from App Store
# Install Xcode Command Line Tools
xcode-select --install

# Install iOS WebDriverAgent dependencies
npm install -g ios-deploy
brew install carthage
brew install libimobiledevice --HEAD
brew install ideviceinstaller

# Install iOS driver for Appium
appium driver install xcuitest

# Verify setup
xcrun simctl list devices
```

### Database Setup (Optional)

#### PostgreSQL
```bash
# Install PostgreSQL
# Windows: Download from https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt install postgresql postgresql-contrib

# Install Python adapter
pip install psycopg2-binary

# Create test database
createdb test_automation_db
```

#### MySQL
```bash
# Install MySQL
# Windows: Download from https://dev.mysql.com/downloads/mysql/
# macOS: brew install mysql
# Linux: sudo apt install mysql-server

# Install Python adapter
pip install PyMySQL

# Create test database
mysql -u root -p -e "CREATE DATABASE test_automation_db;"
```

#### MongoDB
```bash
# Install MongoDB
# Windows: Download from https://www.mongodb.com/try/download/community
# macOS: brew install mongodb-community
# Linux: Follow instructions at https://docs.mongodb.com/manual/installation/

# Install Python adapter
pip install pymongo

# Start MongoDB service
# Windows: net start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

#### Redis
```bash
# Install Redis
# Windows: Download from https://github.com/tporadowski/redis/releases
# macOS: brew install redis
# Linux: sudo apt install redis-server

# Install Python adapter
pip install redis

# Start Redis service
# Windows: redis-server
# macOS: brew services start redis
# Linux: sudo systemctl start redis
```

## ⚙️ Environment Configuration

### Environment Variables

#### Create Environment File
```bash
# Create .env file in project root
touch .env

# Add the following variables (customize as needed):
```

#### Sample .env Configuration
```bash
# ===========================================
# GENERAL FRAMEWORK CONFIGURATION
# ===========================================
TEST_ENVIRONMENT=dev
LOG_LEVEL=INFO
PARALLEL_WORKERS=4
GLOBAL_TIMEOUT=60
RETRY_ATTEMPTS=3

# ===========================================
# API TESTING CONFIGURATION
# ===========================================
API_BASE_URL=https://api.example.com
API_VERSION=v1
API_KEY=your-api-key-here
API_SECRET=your-api-secret
API_TIMEOUT=30
MAX_RETRIES=3

# Authentication
AUTH_TYPE=bearer
TOKEN_ENDPOINT=https://auth.example.com/token
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

# ===========================================
# WEB TESTING CONFIGURATION
# ===========================================
WEB_BASE_URL=https://app.example.com
LOGIN_URL=https://app.example.com/login
BROWSER=chrome
BROWSER_VERSION=latest
HEADLESS=false
WINDOW_SIZE=1920x1080
DEFAULT_TIMEOUT=10
PAGE_LOAD_TIMEOUT=30

# Selenium Grid (optional)
SELENIUM_HUB_URL=http://selenium-hub:4444/wd/hub
SELENIUM_REMOTE=false

# Playwright specific
PLAYWRIGHT_TIMEOUT=30000

# ===========================================
# MOBILE TESTING CONFIGURATION
# ===========================================
PLATFORM_NAME=Android
PLATFORM_VERSION=12.0
DEVICE_NAME=emulator-5554
DEVICE_UDID=auto
APP_PATH=/path/to/app.apk
APP_PACKAGE=com.example.app
APP_ACTIVITY=com.example.MainActivity
BUNDLE_ID=com.example.app
APPIUM_SERVER=http://localhost:4723
APPIUM_TIMEOUT=60

# Cloud testing (optional)
CLOUD_PROVIDER=browserstack
CLOUD_USERNAME=your-username
CLOUD_ACCESS_KEY=your-access-key

# ===========================================
# DATABASE CONFIGURATION
# ===========================================
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_automation_db
DB_USER=test_user
DB_PASSWORD=test_password
DB_SCHEMA=public
DB_POOL_SIZE=10
DB_MAX_CONNECTIONS=20

# MongoDB
MONGO_URI=mongodb://user:pass@localhost:27017/testdb
MONGO_AUTH_SOURCE=admin

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis-password

# ===========================================
# SECURITY CONFIGURATION
# ===========================================
SECURITY_MASTER_PASSWORD=your_secure_master_password
SECURITY_MAX_AUDIT_EVENTS=10000
SECURITY_ROTATION_INTERVAL=86400

# HashiCorp Vault
HASHICORP_VAULT_URL=http://localhost:8200
HASHICORP_VAULT_TOKEN=your_vault_token

# AWS Secrets Manager
AWS_SECRETS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Azure Key Vault
AZURE_VAULT_URL=https://your-vault.vault.azure.net/
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

# ===========================================
# REPORTING AND MONITORING
# ===========================================
REPORT_FORMAT=allure
SCREENSHOT_ON_FAILURE=true
VIDEO_RECORDING=false
PERFORMANCE_MONITORING=true

# CI/CD specific
CI=false
BUILD_NUMBER=local
BUILD_URL=http://localhost
GIT_COMMIT=local
GIT_BRANCH=main
```

### Configuration Validation
```bash
# Validate configuration
python -c "
import os
from base.utilities.security_config import SecurityConfig

# Load and validate configuration
config = SecurityConfig.load_config()
issues = SecurityConfig.validate_config(config)

if issues:
    print('❌ Configuration issues found:')
    for issue in issues:
        print(f'  - {issue}')
else:
    print('✅ Configuration validation passed')
"
```

### Framework Configuration Files

#### behave.ini Configuration
```ini
[behave]
# Output formatting
default_format = pretty
show_skipped = true
show_timings = true
show_multiline = true
color = true

# Logging configuration
capture = false
logging_level = INFO
logging_format = %(levelname)-8s %(name)s: %(message)s
logging_clear_handlers = true
logging_filter = -requests.packages.urllib3

# Path configuration
paths = SystemName (Example)/
step_registry = steps

# Tag configuration
default_tags = ~@skip ~@wip ~@manual

# Reporting
junit = true
junit_directory = reports/junit

# Performance
stop_on_first_failure = false
dry_run = false

# Custom formatters
format = allure_behave.formatter:AllureFormatter
outdir = reports/allure

[behave.formatters]
html = behave_html_formatter:HTMLFormatter

[behave.userdata]
# Default values that can be overridden via -D
browser = chrome
headless = false
timeout = 10
retry_count = 3
environment = dev
parallel = false
workers = 1
```

## ✅ Framework Verification

### Basic Verification
```bash
# 1. Verify Python and virtual environment
python --version
which python

# 2. Verify core dependencies
python -c "
try:
    import behave
    import selenium
    import playwright
    import requests
    import pymongo
    import redis
    import psycopg2
    print('✅ All core dependencies installed successfully')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
"

# 3. Verify framework imports
python -c "
try:
    from base.api.api_client import APIClient
    from base.web_selenium.webdriver_manager import WebDriverManager
    from base.web_playwright.playwright_manager import PlaywrightManager
    from base.utilities.security_utils import get_security_manager
    print('✅ Framework imports successful')
except ImportError as e:
    print(f'❌ Framework import error: {e}')
"
```

### Browser Verification
```bash
# Verify Selenium browsers
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.quit()
    print('✅ Selenium Chrome setup successful')
except Exception as e:
    print(f'❌ Selenium Chrome setup failed: {e}')
"

# Verify Playwright browsers
python -c "
from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        browser.close()
    print('✅ Playwright setup successful')
except Exception as e:
    print(f'❌ Playwright setup failed: {e}')
"
```

### Mobile Testing Verification
```bash
# Verify Appium setup
appium driver list

# Test Android connection (if emulator/device is running)
adb devices

# Verify Appium server connectivity
python -c "
from appium import webdriver
import requests

try:
    response = requests.get('http://localhost:4723/wd/hub/status', timeout=5)
    if response.status_code == 200:
        print('✅ Appium server is running')
    else:
        print('❌ Appium server not responding correctly')
except Exception as e:
    print(f'❌ Cannot connect to Appium server: {e}')
"
```

### Database Verification
```bash
# Test database connections
python -c "
from base.database.database_managers import DatabaseManagerFactory

# Test PostgreSQL
try:
    db_manager = DatabaseManagerFactory.create_manager('postgresql', {
        'host': 'localhost',
        'port': 5432,
        'database': 'postgres',
        'username': 'postgres',
        'password': 'your_password'
    })
    db_manager.connect()
    db_manager.disconnect()
    print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
"
```

### Run Smoke Tests
```bash
# Run basic smoke tests
behave --tags=@smoke --format=pretty --no-capture

# Run specific test types
behave "SystemName (Example)/API/features/" --tags=@smoke
behave "SystemName (Example)/Web (Playwright)/features/" --tags=@smoke

# Run with different browsers
behave -D browser=chrome --tags=@web --format=pretty
behave -D browser=firefox --tags=@web --format=pretty
```

## 💻 IDE Setup

### Visual Studio Code (Recommended)

#### Essential Extensions
```bash
# Install via VS Code Extensions marketplace or command line:
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.pylint
code --install-extension alexkrechik.cucumberautocomplete
code --install-extension stevejpurves.cucumber
code --install-extension ms-vscode.test-adapter-converter
```

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": false,
    "python.testing.unittestEnabled": false,
    "files.associations": {
        "*.feature": "cucumber"
    },
    "cucumberautocomplete.steps": [
        "SystemName (Example)/**/steps/*.py"
    ],
    "cucumberautocomplete.syncfeatures": "SystemName (Example)/**/features/*.feature",
    "cucumberautocomplete.strictGherkinCompletion": true,
    "editor.formatOnSave": true,
    "editor.rulers": [88, 120],
    "python.analysis.typeCheckingMode": "basic"
}
```

#### Launch Configuration
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Behave Smoke Tests",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/venv/bin/behave",
            "args": [
                "--tags=@smoke",
                "--format=pretty",
                "--no-capture"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Run Specific Feature",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/venv/bin/behave",
            "args": [
                "${file}",
                "--format=pretty",
                "--no-capture"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### PyCharm Setup

#### Project Configuration
1. Open PyCharm and create new project from existing sources
2. Set Python interpreter to virtual environment: `Settings → Project → Python Interpreter → Add → Existing Environment → Select venv/bin/python`
3. Mark `base` folder as Sources Root: `Right-click base folder → Mark Directory as → Sources Root`

#### Run Configurations
1. Go to `Run → Edit Configurations`
2. Add new configuration:
   - **Type**: Python
   - **Script path**: Path to behave executable in venv
   - **Parameters**: `--tags=@smoke --format=pretty`
   - **Working directory**: Project root

### IntelliJ IDEA with Python Plugin

#### Setup Steps
1. Install Python plugin: `Settings → Plugins → Install Python Plugin`
2. Configure Python SDK: `Settings → Project Structure → SDKs → Add Python SDK`
3. Set project interpreter: `Settings → Python Interpreter`

## 🐛 Troubleshooting

### Common Installation Issues

#### 1. Python PATH Issues
**Problem**: `python` command not found
**Solution**:
```bash
# Windows - Add Python to PATH
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"

# macOS/Linux - Add to shell profile
echo 'export PATH="/usr/local/bin/python3:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. Virtual Environment Issues
**Problem**: Virtual environment not activating
**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv

# Windows activation issues
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# macOS/Linux permission issues
chmod +x venv/bin/activate
```

#### 3. Dependency Installation Failures
**Problem**: Pip install fails with compilation errors
**Solution**:
```bash
# Update build tools
python -m pip install --upgrade pip setuptools wheel

# Windows - Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# macOS - Install Xcode Command Line Tools
xcode-select --install

# Linux - Install build essentials
sudo apt install build-essential python3-dev
```

#### 4. Playwright Browser Installation Issues
**Problem**: Browser download fails
**Solution**:
```bash
# Clear Playwright cache
npx playwright uninstall --all

# Reinstall with system dependencies
playwright install --with-deps

# For corporate networks with proxy
export HTTPS_PROXY=http://proxy.company.com:8080
playwright install
```

#### 5. Appium Installation Issues
**Problem**: Appium driver installation fails
**Solution**:
```bash
# Update Node.js and npm
npm install -g npm@latest

# Clear npm cache
npm cache clean --force

# Reinstall Appium
npm uninstall -g appium
npm install -g appium

# Install drivers individually
appium driver install uiautomator2
appium driver install xcuitest
```

### Framework-Specific Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'base'`
**Solution**:
```bash
# Ensure you're in the correct directory
pwd  # Should end with /behave_automation

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd path/to/behave_automation
behave "SystemName (Example)/API/features/"
```

#### 2. WebDriver Issues
**Problem**: WebDriver executable not found
**Solution**:
```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager

# Clear webdriver cache
rm -rf ~/.wdm

# Force download specific version
python -c "
from webdriver_manager.chrome import ChromeDriverManager
ChromeDriverManager().install()
"
```

#### 3. Database Connection Issues
**Problem**: Database connection timeout
**Solution**:
```bash
# Check database service status
# PostgreSQL
sudo systemctl status postgresql

# MySQL
sudo systemctl status mysql

# MongoDB
sudo systemctl status mongod

# Test connection manually
python -c "
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    database='testdb',
    user='testuser',
    password='testpass'
)
print('Database connection successful')
conn.close()
"
```

#### 4. Permission Issues
**Problem**: Permission denied errors
**Solution**:
```bash
# Fix file permissions
find . -name "*.py" -exec chmod +x {} \;
find . -name "*.sh" -exec chmod +x {} \;

# Fix directory permissions
chmod -R 755 base/
chmod -R 755 "SystemName (Example)/"
```

### Performance Issues

#### 1. Slow Test Execution
**Solutions**:
```bash
# Enable parallel execution
behave --processes 4 --tags=@regression

# Use headless browsers
behave -D headless=true --tags=@web

# Optimize imports
python base/utilities/import_optimizer.py

# Clear cache
rm -rf __pycache__/
find . -name "*.pyc" -delete
```

#### 2. Memory Issues
**Solutions**:
```bash
# Monitor memory usage
python -c "
from base.utilities.memory_profiler import MemoryProfiler
profiler = MemoryProfiler()
profiler.start_monitoring('test')
# ... run your tests ...
metrics = profiler.stop_monitoring('test')
print(f'Memory usage: {metrics}')
"

# Increase virtual memory (Linux)
sudo sysctl vm.swappiness=10
```

### Getting Help

#### 1. Framework Logs
```bash
# Enable debug logging
export BEHAVE_DEBUG=1
behave --logging-level=DEBUG --tags=@smoke

# Check framework logs
tail -f logs/framework.log
```

#### 2. System Information
```bash
# Collect system information for support
python -c "
import sys, platform, os
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')
print(f'Working Directory: {os.getcwd()}')
print(f'Python Path: {sys.path}')
"
```

#### 3. Dependency Versions
```bash
# List installed packages
pip list

# Check specific versions
pip show behave selenium playwright requests
```

## 🔧 Advanced Configuration

### Security Configuration

#### Vault Setup (Optional)
```bash
# HashiCorp Vault
vault --version
vault server -dev

# AWS CLI for Secrets Manager
aws configure
pip install boto3

# Azure CLI for Key Vault
az login
pip install azure-keyvault-secrets
```

#### SSL Certificate Setup
```bash
# Generate self-signed certificates for testing
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure SSL in environment
export SSL_CERT_PATH=./cert.pem
export SSL_KEY_PATH=./key.pem
```

### Performance Tuning

#### Parallel Execution Setup
```bash
# Install parallel execution support
pip install behave-parallel

# Configure parallel execution
export PARALLEL_WORKERS=4
export LOAD_BALANCER=true
```

#### Caching Configuration
```bash
# Redis for distributed caching
redis-server --daemonize yes

# Configure cache settings
export CACHE_ENABLED=true
export CACHE_TTL=3600
export REDIS_URL=redis://localhost:6379/0
```

### CI/CD Integration

#### Jenkins Setup
```bash
# Install Jenkins plugins
# - Python Plugin
# - Allure Plugin
# - HTML Publisher Plugin

# Create Jenkinsfile (provided in framework)
# Configure webhook for automatic builds
```

#### GitHub Actions Setup
```yaml
# .github/workflows/ci.yml is provided
# Configure secrets in repository settings:
# - API_KEY
# - DB_PASSWORD
# - CLOUD_ACCESS_KEY
```

#### Docker Configuration
```bash
# Build Docker image
docker build -t automation-framework .

# Run tests in container
docker run --rm -v $(pwd)/reports:/app/reports automation-framework
```

---

## 🎉 Setup Complete!

Your Central Quality Hub Automation Framework is now ready to use!

### Next Steps:
1. **Explore Examples**: Review test examples in `SystemName (Example)/` folders
2. **Read Documentation**: Check individual README files in `readme/` folder
3. **Run Sample Tests**: Execute smoke tests to verify everything works
4. **Create Your Tests**: Follow the framework patterns to create your own tests
5. **Configure CI/CD**: Set up automated testing in your deployment pipeline

### Quick Commands:
```bash
# Run all smoke tests
behave --tags=@smoke --format=pretty

# Run API tests only
behave "SystemName (Example)/API/features/" --format=pretty

# Run with Allure reporting
behave --format=allure_behave.formatter:AllureFormatter -o reports/allure
allure serve reports/allure

# Run in parallel
behave --processes 4 --tags=@regression
```

### Support:
- **Documentation**: Check README files in each module
- **Examples**: Working examples in all test implementation folders  
- **Issues**: Create issues in the repository for bugs or feature requests
- **Community**: Join discussions for questions and best practices

**Happy Testing! 🚀**

# Central Quality Hub - Comprehensive Python Automation Framework

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.15.2-green)
![Playwright](https://img.shields.io/badge/Playwright-1.40.0-orange)
![Behave](https://img.shields.io/badge/Behave-1.2.6-yellow)

## 🎯 Overview

The Central Quality Hub is a comprehensive Python automation testing framework built with **Behave BDD** that supports multiple testing approaches across different platforms and technologies. The framework follows the **Page Object Model** pattern and provides a clean, maintainable architecture for enterprise-level test automation.

## 🏗️ Framework Architecture

The framework is organized into two main sections:
- **`base/`** - Contains reusable base classes and utilities
- **`CentralQualityHub/`** - Contains actual test implementations organized by automation type

```
python_behave/
├── 📁 base/                        # Base classes and reusable components
│   ├── 📁 api/                    # API testing base classes
│   ├── 📁 database/               # Database testing base classes  
│   ├── 📁 desktop/                # Desktop automation base classes
│   ├── 📁 mobile/                 # Mobile testing base classes
│   ├── 📁 utilities/              # Common utilities (Excel, JSON, etc.)
│   ├── 📁 web_playwright/         # Playwright web automation base classes
│   └── 📁 web_selenium/           # Selenium web automation base classes
│
├── 📁 SystemName (Example)/       # Test implementations by automation type
│   ├── 📁 API/                    # API testing implementation
│   │   ├── 📁 features/           # API feature files
│   │   ├── 📁 pageobjects/        # API page objects (endpoints as page objects)
│   │   └── 📁 steps/              # API step definitions
│   ├── 📁 DB/                     # Database testing implementation
│   │   ├── 📁 features/           # Database feature files
│   │   ├── 📁 pageobjects/        # Database page objects
│   │   └── 📁 steps/              # Database step definitions
│   ├── 📁 Desktop/                # Desktop application testing
│   │   ├── 📁 features/           # Desktop feature files
│   │   ├── 📁 pageobjects/        # Desktop page objects
│   │   └── 📁 steps/              # Desktop step definitions
│   ├── 📁 Mobile/                 # Mobile testing implementation
│   │   ├── 📁 features/           # Mobile feature files
│   │   ├── 📁 pageobjects/        # Mobile page objects
│   │   └── 📁 steps/              # Mobile step definitions
│   ├── 📁 Web (Playwright)/       # Modern web testing with Playwright
│   │   ├── 📁 features/           # Playwright feature files
│   │   ├── 📁 pageobjects/        # Playwright page objects
│   │   └── 📁 steps/              # Playwright step definitions
│   └── 📁 Web (Selenium)/         # Traditional web testing with Selenium
│       ├── 📁 features/           # Selenium feature files
│       ├── 📁 pageobjects/        # Selenium page objects
│       └── 📁 steps/              # Selenium step definitions
│
├── behave.ini                     # Behave configuration
├── requirements.txt               # Python dependencies
├── setup.bat/setup.sh            # Setup scripts
├── run_tests.bat                  # Test execution script
└── README.md                      # This file
```

## 🚀 Supported Testing Types

### 🌐 Web Automation (Dual Framework Support)

#### **Playwright** (Recommended for new projects)
- **Modern Browser Support**: Chromium, Firefox, WebKit
- **Advanced Features**: Auto-wait, fast execution, mobile emulation
- **Built-in Capabilities**: Performance metrics, accessibility testing, network interception
- **Cross-Platform**: Windows, macOS, Linux with native browser automation

#### **Selenium** (Mature, widely adopted)
- **Cross-Browser Support**: Chrome, Firefox, Edge, Safari
- **Enterprise Features**: Selenium Grid, Docker support, cloud platform integration
- **Mature Ecosystem**: Extensive community, plugins, and third-party tools
- **Testing Capabilities**: Headless mode, responsive testing, screenshot capture

### 📱 Mobile Automation  
- **Framework**: Appium with native driver support
- **Platforms**: iOS (real devices & simulators), Android (real devices & emulators)
- **App Types**: Native apps, hybrid apps, mobile web applications
- **Advanced Features**: Touch gestures, device rotation, app installation/uninstallation

### 🔗 API Testing
- **Protocol Support**: REST APIs with full HTTP method support (GET, POST, PUT, DELETE, PATCH)
- **Authentication**: Bearer tokens, API keys, Basic Auth, OAuth 2.0
- **Validation**: JSON schema validation, response time monitoring, status code verification
- **Page Object Model**: Each API endpoint treated as page object for better maintainability

### 🗄️ Database Testing
- **Multi-Database Support**: PostgreSQL, MySQL, SQLite, MongoDB, Redis
- **Operations**: CRUD operations, data validation, migration testing
- **Performance**: Connection pooling, query performance monitoring
- **Data Management**: Test data generation, cleanup, and state management

### 🖥️ Desktop Automation
- **Platform Support**: Windows, macOS, Linux desktop applications
- **Technologies**: Native applications, Electron apps, Java Swing, WPF
- **Capabilities**: UI element interaction, process management, file system operations
- **Testing Types**: Functional testing, performance monitoring, accessibility validation

### 🛠️ Utilities
- **Excel Processing** - Read/write Excel files with pandas and openpyxl
- **Data Processing** - JSON, XML, YAML, CSV utilities
- **File Operations** - Comprehensive file handling utilities

## 📋 Prerequisites

- **Python 3.8+** (Recommended: Python 3.9 or higher)
- **Git** for version control
- **Node.js** (for Appium mobile testing)
- **Java JDK** (for Appium Android testing)

### Platform-Specific Requirements

#### Windows
- **Visual Studio Code** or your preferred IDE
- **Windows Terminal** (recommended)

#### Linux/Mac
- **Terminal** access
- **Xcode** (Mac only, for iOS testing)

## ⚡ Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd automation_framework/python_behave

# Windows Setup
setup.bat

# Linux/Mac Setup
chmod +x setup.sh
./setup.sh
```

### 2. Install Browser Dependencies
```bash
# For Playwright (optional - only if using Playwright)
playwright install

# For Appium (optional - only if using mobile testing)
npm install -g appium
appium driver install uiautomator2  # For Android
appium driver install xcuitest      # For iOS
```

### 3. Run Sample Tests
```bash
# Run API tests (recommended for first test)
behave "SystemName (Example)/API/features/" --tags=@smoke

# Run Web tests (Playwright)
behave "SystemName (Example)/Web (Playwright)/features/" --tags=@smoke

# Run Web tests (Selenium)
behave "SystemName (Example)/Web (Selenium)/features/" --tags=@smoke

# Run all smoke tests across all frameworks
behave --tags=@smoke
```

## 🎯 Running Tests

### By Test Type
```bash
# API Testing
behave "SystemName (Example)/API/features/"

# Web Testing (Playwright) - Recommended
behave "SystemName (Example)/Web (Playwright)/features/"

# Web Testing (Selenium) - Traditional
behave "SystemName (Example)/Web (Selenium)/features/"

# Mobile Testing
behave "SystemName (Example)/Mobile/features/"

# Database Testing
behave "SystemName (Example)/DB/features/"

# Desktop Testing
behave "SystemName (Example)/Desktop/features/"
```

### By Tags
```bash
# Smoke tests only
behave --tags=@smoke

# Regression tests
behave --tags=@regression

# Specific feature tags
behave --tags=@api
behave --tags=@crud
behave --tags=@login
behave --tags=@users

# Exclude certain tags
behave --tags=~@skip
behave --tags=~@slow
```

### Advanced Execution
```bash
# Run with specific format
behave --format=allure_behave.formatter:AllureFormatter

# Run with parallel execution (if configured)
behave --processes 4

# Run specific feature file
behave "SystemName (Example)/API/features/api_users.feature"

# Run with custom configuration
behave -D browser=chrome
behave -D environment=staging
```

## 🏗️ Framework Features

### 📊 Page Object Model Pattern
- **API Page Objects**: Each API endpoint is treated as a page object
- **Web Page Objects**: Traditional page object pattern for web elements
- **Mobile Page Objects**: Mobile-specific page objects with touch gestures
- **Database Page Objects**: Database entities as page objects

### 🔧 Base Class Architecture
- **Single Responsibility**: Each base class handles one automation type
- **Inheritance**: Common functionality in base classes
- **Modularity**: Mix and match different automation types
- **Extensibility**: Easy to add new automation types

### �️ Comprehensive Utilities
- **Excel Processing**: Read/write Excel files with advanced features
- **JSON Utilities**: JSON parsing, querying, and validation
- **File Operations**: File handling, CSV processing
- **String Utilities**: Text processing and manipulation
- **Date/Time Utilities**: Date formatting and calculations
- **Encoding Utilities**: Hashing, encoding, and security functions

### � Reporting and Logging
- **Allure Reports**: Comprehensive test reporting
- **Request/Response Logging**: Detailed API call logging
- **Screenshot Capture**: Automatic screenshots on failures
- **Performance Metrics**: Response time tracking
- **Detailed Error Messages**: Clear failure descriptions

## 📝 Writing Tests

### 1. Feature Files (Gherkin)
Create `.feature` files using Gherkin syntax:

```gherkin
@api @users @smoke
Feature: User Management API
  As an API consumer
  I want to manage users via REST API
  So that I can perform CRUD operations

  Background:
    Given the API is available and accessible

  @crud
  Scenario: Create a new user
    Given I have valid user data:
      | field      | value              |
      | username   | test_user          |
      | email      | test@example.com   |
    When I send a POST request to "/users" with the user data
    Then the response status should be 201
    And the user should be created with the provided data
```

### 2. Page Objects
Create page object classes that inherit from appropriate base classes:

```python
# API Page Object Example
from base.api.base_api_page import BaseAPIPage

class UsersAPIPage(BaseAPIPage):
    def __init__(self, api_client):
        super().__init__(api_client, '/users')
        
    def create_user(self, user_data):
        return self.create(user_data)
        
    def validate_resource_structure(self, resource_data):
        # Implement user-specific validation
        required_fields = ['username', 'email']
        for field in required_fields:
            if field not in resource_data:
                raise AssertionError(f"Missing field: {field}")
```

### 3. Step Definitions
Implement step definitions that use page objects:

```python
from behave import given, when, then
from pageobjects.users_api_page import UsersAPIPage

@when('I send a POST request to "/users" with the user data')
def step_create_user(context):
    if not hasattr(context, 'users_api'):
        context.users_api = UsersAPIPage(context.api_client)
    context.users_api.create_user(context.user_data)

@then('the user should be created with the provided data')
def step_verify_user_created(context):
    context.users_api.validate_user_created(context.user_data)
```

## 🎨 Framework Design Principles

### 1. **Separation of Concerns**
- Base classes contain reusable functionality
- Page objects contain business logic
- Step definitions are thin and delegate to page objects
- Feature files contain only business-readable scenarios

### 2. **Single Class Per File**
- Each file contains exactly one class
- Improves maintainability and readability
- Easier to navigate and find specific functionality
- Better for version control and collaboration

### 3. **Page Object Model for APIs**
- Each API endpoint group is a page object
- Business operations as methods
- Validation logic encapsulated
- Consistent pattern across all automation types

### 4. **Comprehensive Error Handling**
- Meaningful error messages
- Proper exception handling
- Detailed logging for debugging
- Fallback mechanisms where appropriate

## 📁 Project Structure Details

### Base Package (`base/`)
Contains reusable base classes and utilities that provide core functionality for all automation types.

#### API Testing (`base/api/`)
- `api_client.py` - HTTP client with authentication support
- `base_api_page.py` - Abstract base class for API page objects

#### Database Testing (`base/database/`)
- `base_database_manager.py` - Base database connection manager
- `database_managers.py` - Specific database implementations

#### Desktop Testing (`base/desktop/`)
- `base_desktop_page.py` - Base class for desktop page objects
- `desktop_app_manager.py` - Desktop application management

#### Mobile Testing (`base/mobile/`)
- `base_mobile_page.py` - Base class for mobile page objects
- `mobile_driver_manager.py` - Mobile driver management

#### Web Testing (`base/web_selenium/` & `base/web_playwright/`)
- `base_page.py` - Base page classes for web automation
- `webdriver_manager.py` / `playwright_manager.py` - Driver management
- `helpers.py` - Web-specific utility functions

#### Utilities (`base/utilities/`)
- `excel_reader.py` / `excel_writer.py` - Excel file processing
- `json_utils.py` - JSON parsing and querying
- `file_operations.py` - File handling utilities
- `string_utils.py` - String processing functions
- `datetime_utils.py` - Date and time utilities
- And more specialized utilities...

### Test Implementation (`SystemName (Example)/`)
Contains actual test implementations organized by automation type.

Each automation type follows the same structure:
- `features/` - Gherkin feature files
- `pageobjects/` - Page object implementations  
- `steps/` - Step definition implementations

#### Available Test Examples:
- **API/**: REST API testing examples with Page Object Model
- **DB/**: Database testing with multiple database support
- **Desktop/**: Desktop application automation examples
- **Mobile/**: Mobile app testing for iOS and Android
- **Web (Playwright)/**: Modern web testing with Playwright
- **Web (Selenium)/**: Traditional web testing with Selenium

## 🔧 Configuration

### Behave Configuration (`behave.ini`)
```ini
[behave]
default_format = pretty
show_skipped = true
show_timings = true
capture = false
logging_level = INFO
```

### Environment Variables
Set these environment variables for different configurations:
```bash
# API Testing
export API_BASE_URL="https://api.example.com"
export API_KEY="your-api-key"

# Web Testing  
export WEB_BASE_URL="https://app.example.com"
export BROWSER="chrome"  # chrome, firefox, edge

# Mobile Testing
export PLATFORM_NAME="Android"  # Android, iOS
export DEVICE_NAME="emulator-5554"

# Database Testing
export DB_HOST="localhost"
export DB_NAME="test_db"
export DB_USER="test_user"
export DB_PASSWORD="test_password"
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'base'`
**Solution**: Ensure you're running tests from the project root directory

#### 2. WebDriver Issues
**Problem**: WebDriver not found or browser crashes
**Solution**: 
```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager

# For specific browser issues
pip install --upgrade selenium
```

#### 3. Mobile Testing Issues
**Problem**: Appium server connection failed
**Solution**:
```bash
# Check Appium installation
appium --version

# Restart Appium server
appium --allow-insecure chromedriver_autodownload
```

#### 4. API Authentication Issues
**Problem**: 401 Unauthorized errors
**Solution**: Check API credentials and base URL configuration

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export BEHAVE_DEBUG=1
behave --logging-level=DEBUG
```

## 📊 Reports and Artifacts

### Allure Reports
Generate comprehensive HTML reports:
```bash
# Install Allure (one-time setup)
pip install allure-behave

# Run tests with Allure
behave -f allure_behave.formatter:AllureFormatter -o reports/allure

# Generate and serve report
allure serve reports/allure
```

### Screenshots and Logs
- Screenshots saved to `screenshots/` directory on test failures
- Detailed logs available in `logs/` directory
- API request/response logs for debugging

## 🤝 Contributing

### Code Style Guidelines
1. **Follow PEP 8** for Python code formatting
2. **Use meaningful names** for classes, methods, and variables
3. **Add docstrings** to all classes and methods
4. **Keep methods small** and focused on single responsibilities
5. **Use type hints** where appropriate

### Adding New Tests

#### 1. Create Feature File
```gherkin
@new_feature @smoke
Feature: New Feature Description
  As a user
  I want to perform some action
  So that I can achieve some goal

  Scenario: Test scenario description
    Given some precondition
    When I perform some action
    Then I should see expected result
```

#### 2. Create Page Object
```python
class NewFeaturePage(BaseAPIPage):  # or appropriate base class
    def __init__(self, client):
        super().__init__(client, '/new-endpoint')
    
    def perform_action(self, data):
        """Perform the main action for this feature"""
        return self.create(data)
```

#### 3. Implement Step Definitions
```python
@when('I perform some action')
def step_perform_action(context):
    """Step implementation using page object"""
    context.page.perform_action(context.test_data)
```

## 📞 Support

### Documentation
- Framework documentation in each module's README
- API documentation available at `SystemName (Example)/API/README.md`
- Web (Playwright) documentation at `SystemName (Example)/Web (Playwright)/README.md`
- Web (Selenium) documentation at `SystemName (Example)/Web (Selenium)/README.md`
- Database documentation at `SystemName (Example)/DB/README.md`
- Mobile documentation at `SystemName (Example)/Mobile/README.md`  
- Desktop documentation at `SystemName (Example)/Desktop/README.md`
- Code examples in feature files and step definitions

### Best Practices
1. **Use appropriate tags** (@smoke, @regression, @api, etc.)
2. **Write descriptive scenario names** that explain business value
3. **Keep step definitions simple** - delegate complexity to page objects
4. **Use data tables** for multiple test data sets
5. **Implement proper cleanup** in hooks and teardown methods

### Performance Tips
1. **Use parallel execution** for independent tests
2. **Implement smart waits** instead of hard sleeps
3. **Cache authentication tokens** to avoid repeated login
4. **Use appropriate test data** (minimize large datasets)
5. **Clean up test data** after test execution

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏷️ Version

**Current Version**: 2.0.0
**Last Updated**: July 2025
**Python Compatibility**: 3.8+

---

**Happy Testing! 🎉**

For questions, issues, or contributions, please refer to the project documentation or create an issue in the repository.

# Comprehensive Python Automation Framework

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.25.0-green)
![Playwright](https://img.shields.io/badge/Playwright-1.47.0-orange)
![Behave](https://img.shields.io/badge/Behave-1.2.7-yellow)
![Requests](https://img.shields.io/badge/Requests-2.31.0-red)
![Appium](https://img.shields.io/badge/Appium-4.1.0-purple)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 🎯 Overview

A comprehensive, enterprise-grade Python automation testing framework built with **Behave BDD** that supports multiple testing approaches across different platforms and technologies. The framework follows industry best practices including the **Page Object Model** pattern, **SOLID principles**, and provides a clean, maintainable, and scalable architecture for enterprise-level test automation.

### Key Highlights
- 🚀 **Multi-Platform Support**: Web, Mobile, API, Database, and Desktop automation
- 🔧 **Dual Web Framework**: Both Selenium and Playwright support
- 📊 **BDD Approach**: Gherkin-based test scenarios for business readability
- 🏗️ **Modular Architecture**: Reusable base classes and utilities
- 📈 **Comprehensive Reporting**: Allure reports with screenshots and detailed logs
- 🔄 **CI/CD Ready**: Jenkins, GitHub Actions, and Azure DevOps integration
- 🎯 **Enterprise Features**: Parallel execution, environment management, data-driven testing

## 🏗️ Framework Architecture

The framework is organized into two main sections:
- **`base/`** - Contains reusable base classes and utilities
- **`SystemName (Example)/`** - Contains actual test implementations organized by automation type

### Framework Benefits
- ✅ **Reduced Maintenance**: Centralized base classes minimize code duplication
- ✅ **Faster Development**: Pre-built utilities and helpers accelerate test creation
- ✅ **Consistent Patterns**: Standardized approach across all automation types
- ✅ **Easy Scalability**: Add new test types without affecting existing code
- ✅ **Cross-Team Collaboration**: Clear structure enables multiple teams to work simultaneously

```
behave_automation/
├── 📁 base/                        # Base classes and reusable components
│   ├── 📁 api/                    # API testing base classes
│   │   ├── api_client.py         # HTTP client with authentication
│   │   ├── api_response_validator.py  # Response validation utilities
│   │   ├── api_test_helpers.py   # API testing helper methods
│   │   ├── base_api_client.py    # Base API client implementation
│   │   └── base_api_page.py      # Abstract base class for API page objects
│   ├── 📁 database/               # Database testing base classes
│   │   ├── base_database_manager.py      # Base database connection manager
│   │   ├── database_managers.py          # Database-specific implementations
│   │   ├── database_performance_monitor.py  # Performance monitoring
│   │   ├── database_test_data_generator.py  # Test data generation
│   │   ├── database_test_validator.py     # Database validation utilities
│   │   ├── mongodb_manager.py            # MongoDB specific operations
│   │   ├── mysql_manager.py              # MySQL specific operations
│   │   ├── postgresql_manager.py         # PostgreSQL specific operations
│   │   ├── redis_manager.py              # Redis specific operations
│   │   └── sqlite_manager.py             # SQLite specific operations
│   ├── 📁 desktop/                # Desktop automation base classes
│   │   ├── base_desktop_page.py          # Base class for desktop page objects
│   │   ├── desktop_app_manager_core.py   # Core desktop app management
│   │   ├── desktop_app_manager.py        # Desktop application manager
│   │   └── desktop_test_helpers.py       # Desktop testing utilities
│   ├── 📁 mobile/                 # Mobile testing base classes
│   │   ├── base_mobile_page.py           # Base class for mobile page objects
│   │   └── mobile_driver_manager.py      # Mobile driver management
│   ├── 📁 utilities/              # Common utilities (Excel, JSON, etc.)
│   │   ├── csv_utils.py                  # CSV file processing
│   │   ├── datetime_utils.py             # Date and time utilities
│   │   ├── encoding_utils.py             # Encoding and hashing utilities
│   │   ├── excel_reader.py               # Excel file reading
│   │   ├── excel_writer.py               # Excel file writing
│   │   ├── file_operations.py            # File handling utilities
│   │   ├── json_utils.py                 # JSON parsing and manipulation
│   │   ├── string_utils.py               # String processing functions
│   │   ├── url_utils.py                  # URL manipulation utilities
│   │   ├── xml_utils.py                  # XML processing utilities
│   │   └── yaml_utils.py                 # YAML processing utilities
│   ├── 📁 web_playwright/         # Playwright web automation base classes
│   │   ├── base_page.py                  # Base Playwright page class
│   │   ├── helpers.py                    # Playwright-specific helpers
│   │   └── playwright_manager.py         # Playwright driver management
│   └── 📁 web_selenium/           # Selenium web automation base classes
│       ├── base_page.py                  # Base Selenium page class
│       ├── helpers.py                    # Selenium-specific helpers
│       ├── web_element_helpers.py        # Web element interaction utilities
│       ├── web_test_helpers.py           # Web testing utilities
│       ├── web_wait_helpers.py           # Smart wait implementations
│       └── webdriver_manager.py          # WebDriver management
│
├── 📁 SystemName (Example)/       # Test implementations by automation type
│   ├── 📁 API/                    # API testing implementation
│   │   ├── 📁 features/           # API feature files (.feature)
│   │   │   ├── api_products.feature       # Product API scenarios
│   │   │   ├── api_users.feature          # User API scenarios
│   │   │   └── environment.py             # API test environment setup
│   │   ├── 📁 pageobjects/        # API page objects (endpoints as page objects)
│   │   │   ├── products_api_page.py       # Product API operations
│   │   │   └── users_api_page.py          # User API operations
│   │   └── 📁 steps/              # API step definitions
│   │       ├── api_steps.py               # Common API steps
│   │       └── products_steps.py          # Product-specific steps
│   ├── 📁 DB/                     # Database testing implementation
│   │   ├── 📁 features/           # Database feature files
│   │   │   ├── database_crud.feature      # CRUD operation scenarios
│   │   │   └── environment.py             # Database test environment
│   │   ├── 📁 pageobjects/        # Database page objects
│   │   └── 📁 steps/              # Database step definitions
│   │       └── database_steps.py          # Database operation steps
│   ├── 📁 Desktop/                # Desktop application testing
│   │   ├── 📁 features/           # Desktop feature files
│   │   │   ├── desktop_application_testing.feature  # Desktop app scenarios
│   │   │   └── environment.py             # Desktop test environment
│   │   ├── 📁 pageobjects/        # Desktop page objects
│   │   │   ├── calculator_page.py         # Calculator app page object
│   │   │   └── notepad_page.py            # Notepad app page object
│   │   └── 📁 steps/              # Desktop step definitions
│   │       └── desktop_steps.py           # Desktop interaction steps
│   ├── 📁 Mobile/                 # Mobile testing implementation
│   │   ├── 📁 features/           # Mobile feature files
│   │   │   ├── environment.py             # Mobile test environment
│   │   │   └── mobile_login.feature       # Mobile login scenarios
│   │   ├── 📁 pageobjects/        # Mobile page objects
│   │   │   ├── mobile_home_page.py        # Mobile home page
│   │   │   └── mobile_login_page.py       # Mobile login page
│   │   └── 📁 steps/              # Mobile step definitions
│   │       └── mobile_steps.py            # Mobile interaction steps
│   ├── 📁 Web (Playwright)/       # Modern web testing with Playwright
│   │   ├── 📁 features/           # Playwright feature files
│   │   ├── 📁 pageobjects/        # Playwright page objects
│   │   └── 📁 steps/              # Playwright step definitions
│   └── 📁 Web (Selenium)/         # Traditional web testing with Selenium
│       ├── 📁 features/           # Selenium feature files
│       ├── 📁 pageobjects/        # Selenium page objects
│       └── 📁 steps/              # Selenium step definitions
│
├── 📄 behave.ini                  # Behave configuration file
├── 📄 README.md                   # This comprehensive documentation
├── 📄 requirements.txt            # Python dependencies list
├── 🚀 run_tests.bat               # Windows test execution script
├── ⚙️ setup.bat                   # Windows environment setup script
└── ⚙️ setup.sh                    # Unix/Linux environment setup script
```

### Additional Framework Components
- **Environment Management**: Support for multiple environments (dev, staging, prod)
- **Test Data Management**: External test data files (JSON, Excel, CSV)
- **Configuration Management**: Environment-specific configuration files
- **Logging**: Comprehensive logging with different log levels
- **Reporting**: Multiple reporting formats (HTML, JSON, Allure)
- **CI/CD Integration**: Ready-to-use pipeline configurations

## 🚀 Supported Testing Types

### 🌐 Web Automation (Dual Framework Support)

#### **Playwright** (Recommended for new projects)
- **Modern Browser Support**: Chromium, Firefox, WebKit (Safari)
- **Advanced Features**: Auto-wait, fast execution, mobile emulation, network interception
- **Built-in Capabilities**: Performance metrics, accessibility testing, screenshot comparison
- **Cross-Platform**: Windows, macOS, Linux with native browser automation
- **Modern Testing**: Visual testing, API mocking, trace viewer for debugging
- **Performance**: Faster execution compared to Selenium, parallel browser contexts

#### **Selenium** (Mature, widely adopted)
- **Cross-Browser Support**: Chrome, Firefox, Edge, Safari, Internet Explorer
- **Enterprise Features**: Selenium Grid, Docker support, cloud platform integration (BrowserStack, Sauce Labs)
- **Mature Ecosystem**: Extensive community, plugins, and third-party tools
- **Testing Capabilities**: Headless mode, responsive testing, screenshot capture
- **Flexibility**: Custom browser profiles, proxy support, certificate handling
- **Legacy Support**: Works with older browser versions and legacy applications

### 📱 Mobile Automation  
- **Framework**: Appium 4.x with native driver support and WebDriverIO integration
- **Platforms**: iOS (real devices & simulators), Android (real devices & emulators)
- **App Types**: Native apps, hybrid apps, mobile web applications, React Native, Flutter
- **Advanced Features**: Touch gestures, device rotation, app installation/uninstallation, biometric testing
- **Device Management**: Cloud device farms (AWS Device Farm, Firebase Test Lab), local device management
- **Performance Testing**: Memory usage monitoring, battery consumption, network simulation

### 🔗 API Testing
- **Protocol Support**: REST APIs, GraphQL, SOAP, WebSocket APIs
- **HTTP Methods**: Full support for GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- **Authentication**: Bearer tokens, API keys, Basic Auth, OAuth 2.0, JWT tokens, certificate-based auth
- **Validation**: JSON schema validation, XML validation, response time monitoring, status code verification
- **Page Object Model**: Each API endpoint treated as page object for better maintainability
- **Advanced Features**: Request/response logging, data-driven testing, contract testing, mock server integration

### 🗄️ Database Testing
- **Multi-Database Support**: PostgreSQL, MySQL, SQLite, MongoDB, Redis, Cassandra, Oracle
- **Operations**: CRUD operations, data validation, migration testing, stored procedure testing
- **Performance**: Connection pooling, query performance monitoring, load testing
- **Data Management**: Test data generation, cleanup, state management, data seeding
- **Advanced Features**: Transaction testing, concurrent access testing, backup/restore validation
- **NoSQL Support**: Document databases, key-value stores, graph databases

### 🖥️ Desktop Automation
- **Platform Support**: Windows (Win32, WPF, UWP), macOS (Cocoa), Linux (GTK, Qt)
- **Technologies**: Native applications, Electron apps, Java Swing, WPF, Qt applications
- **Capabilities**: UI element interaction, process management, file system operations, registry testing
- **Testing Types**: Functional testing, performance monitoring, accessibility validation, installation testing
- **Advanced Features**: Image recognition, OCR capabilities, multi-monitor support, virtual desktop testing

### 🛠️ Utilities
- **Excel Processing** - Read/write Excel files with pandas, openpyxl, and xlsxwriter
- **Data Processing** - JSON, XML, YAML, CSV utilities with validation and transformation
- **File Operations** - Comprehensive file handling, compression, encryption utilities
- **Date/Time Utilities** - Timezone handling, date arithmetic, format conversion
- **Encoding Utilities** - Base64, URL encoding, hashing (MD5, SHA256), encryption
- **String Processing** - Regular expressions, text manipulation, template processing

## 📋 Prerequisites

### Core Requirements
- **Python 3.9+** (Recommended: Python 3.11 or higher for better performance)
- **Git** for version control and repository management
- **Node.js 18+** (for Appium mobile testing and Playwright browser management)
- **Java JDK 11+** (for Appium Android testing and some desktop applications)

### Development Environment
- **IDE**: Visual Studio Code (recommended), PyCharm, or your preferred Python IDE
- **Extensions**: Python, Behave, Gherkin syntax highlighting
- **Terminal**: Command prompt, PowerShell, or integrated terminal

### Platform-Specific Requirements

#### Windows
- **Windows 10/11** (64-bit recommended)
- **Visual Studio Build Tools** (for Python package compilation)
- **Windows Terminal** (recommended for better command-line experience)
- **PowerShell 5.1+** or PowerShell Core 7+

#### macOS
- **macOS 10.15+** (Catalina or later)
- **Xcode Command Line Tools** (for iOS testing and Python package compilation)
- **Homebrew** (recommended for package management)
- **Xcode** (full version required for iOS simulator testing)

#### Linux
- **Ubuntu 20.04+**, **CentOS 8+**, or equivalent distributions
- **Build essentials** (gcc, make, etc.)
- **X11** or **Wayland** for desktop automation
- **Docker** (optional, for containerized testing)

## ⚡ Quick Start

### Getting started
Refer to the setup_readme.md file.

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
behave --tags=@smoke --format=pretty

# Regression tests
behave --tags=@regression --format=progress

# Specific feature tags
behave --tags=@api --format=json -o reports/api_results.json
behave --tags=@crud --format=pretty
behave --tags=@login --format=pretty
behave --tags=@users --format=pretty

# Exclude certain tags
behave --tags=~@skip --format=pretty
behave --tags=~@slow --format=pretty
behave --tags=~@wip --format=pretty  # Work in progress

# Combined tags (AND operation)
behave --tags=@api and @smoke --format=pretty

# Multiple tag options (OR operation)  
behave --tags=@smoke,@regression --format=pretty
```

### Advanced Execution
```bash
# Run with specific output format
behave --format=allure_behave.formatter:AllureFormatter -o reports/allure
behave --format=json -o reports/results.json
behave --format=junit -o reports/junit_results.xml

# Run with parallel execution (requires behave-parallel)
behave --processes 4 --tags=@regression
behave --processes auto --tags=@api  # Auto-detect CPU cores

# Run specific feature file
behave "SystemName (Example)/API/features/api_users.feature" --format=pretty

# Run specific scenario by line number
behave "SystemName (Example)/API/features/api_users.feature:15" --format=pretty

# Run with custom configuration and environment variables
behave -D browser=chrome -D headless=true --tags=@web
behave -D environment=staging -D api_timeout=30 --tags=@api
behave -D parallel=true -D workers=3 --tags=@regression

# Run with verbose output and logging
behave --verbose --logging-level=DEBUG --tags=@smoke

# Run with dry run (syntax check only)
behave --dry-run "SystemName (Example)/API/features/"

# Run with custom behave.ini configuration
behave -c custom_behave.ini --tags=@smoke
```

### Environment-Specific Execution
```bash
# Development environment
behave -D env=dev --tags=@smoke

# Staging environment  
behave -D env=staging --tags=@regression

# Production smoke tests
behave -D env=prod --tags=@prod_smoke

# Local database tests
behave -D db_host=localhost --tags=@db

# Cloud testing
behave -D cloud=true -D browser_version=latest --tags=@web
```

## 🏗️ Framework Features

### 📊 Page Object Model Pattern
- **API Page Objects**: Each API endpoint is treated as a page object
- **Web Page Objects**: Traditional page object pattern for web elements
- **Mobile Page Objects**: Mobile-specific page objects with touch gestures
- **Database Page Objects**: Database entities as page objects

### 🔧 Base Class Architecture
- **Single Responsibility**: Each base class handles one automation type with clear separation of concerns
- **Inheritance**: Common functionality in base classes, specialized behavior in derived classes
- **Modularity**: Mix and match different automation types within the same test suite
- **Extensibility**: Easy to add new automation types without affecting existing code
- **Interface Consistency**: Uniform method signatures across all automation types

### 🛠️ Comprehensive Utilities
- **Excel Processing**: Read/write Excel files with advanced features (formulas, formatting, charts)
- **JSON Utilities**: JSON parsing, querying with JSONPath, schema validation, pretty printing
- **File Operations**: File handling, CSV processing, archive operations, file watching
- **String Utilities**: Text processing, template engines, regular expressions, encoding
- **Date/Time Utilities**: Date formatting, timezone conversion, business day calculations
- **Encoding Utilities**: Hashing (MD5, SHA1, SHA256), Base64 encoding, URL encoding, encryption
- **Database Utilities**: Connection pooling, query builders, migration helpers, data validation

### 📊 Reporting and Logging
- **Allure Reports**: Comprehensive test reporting with screenshots, videos, and attachments
- **Request/Response Logging**: Detailed API call logging with request/response bodies and headers
- **Screenshot Capture**: Automatic screenshots on failures, manual screenshot capture
- **Performance Metrics**: Response time tracking, memory usage monitoring, CPU utilization
- **Detailed Error Messages**: Clear failure descriptions with stack traces and context
- **Custom Logging**: Configurable log levels, custom log formatters, log rotation
- **Video Recording**: Test execution video recording for debugging (Playwright)

### 🔄 CI/CD Integration
- **Jenkins**: Ready-to-use Jenkinsfile with pipeline stages
- **GitHub Actions**: Workflow files for automated testing
- **Azure DevOps**: Pipeline templates for Azure Pipelines
- **GitLab CI**: Configuration files for GitLab CI/CD
- **Docker Support**: Containerized test execution with Docker Compose
- **Parallel Execution**: Distributed test execution across multiple nodes

### 🎯 Advanced Features
- **Data-Driven Testing**: External data sources (Excel, JSON, CSV, databases)
- **Environment Management**: Multiple environment configurations with easy switching
- **Test Retry Logic**: Automatic retry for flaky tests with configurable retry policies
- **Conditional Execution**: Skip tests based on environment conditions
- **Test Dependencies**: Manage test execution order and dependencies
- **Custom Assertions**: Extended assertion library with descriptive error messages
- **Mock Integration**: Built-in support for API mocking and service virtualization

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

#### Base Package (`base/`)
Contains reusable base classes and utilities that provide core functionality for all automation types.

##### API Testing (`base/api/`)
- `api_client.py` - Comprehensive HTTP client with authentication, retry logic, and request/response logging
- `api_response_validator.py` - JSON schema validation, response time validation, status code checking
- `api_test_helpers.py` - Common API testing utilities and helper methods
- `base_api_client.py` - Abstract base class for API clients with connection management
- `base_api_page.py` - Abstract base class for API page objects with CRUD operations

##### Database Testing (`base/database/`)
- `base_database_manager.py` - Abstract base class for database connections and operations
- `database_managers.py` - Factory pattern for creating database-specific managers
- `database_performance_monitor.py` - Query performance monitoring and optimization suggestions
- `database_test_data_generator.py` - Automated test data generation with realistic data
- `database_test_validator.py` - Data integrity validation and constraint checking
- `mongodb_manager.py` - MongoDB-specific operations, aggregation pipelines, and indexing
- `mysql_manager.py` - MySQL-specific features, stored procedures, and optimization
- `postgresql_manager.py` - PostgreSQL advanced features, JSON operations, and extensions
- `redis_manager.py` - Redis operations, pub/sub, caching strategies, and data structures
- `sqlite_manager.py` - SQLite operations, file-based testing, and migration support

##### Desktop Testing (`base/desktop/`)
- `base_desktop_page.py` - Base class for desktop page objects with common UI interactions
- `desktop_app_manager_core.py` - Core desktop application lifecycle management
- `desktop_app_manager.py` - High-level desktop application management and orchestration
- `desktop_test_helpers.py` - Desktop-specific utilities for window management and process control

##### Mobile Testing (`base/mobile/`)
- `base_mobile_page.py` - Base class for mobile page objects with touch gestures and mobile-specific actions
- `mobile_driver_manager.py` - Appium driver management, device capabilities, and session handling

##### Web Testing (`base/web_selenium/` & `base/web_playwright/`)
- `base_page.py` - Base page classes for web automation with common page operations
- `webdriver_manager.py` / `playwright_manager.py` - Browser driver lifecycle management
- `helpers.py` - Framework-specific utility functions and common operations
- `web_element_helpers.py` (Selenium) - Advanced element interaction and manipulation utilities
- `web_test_helpers.py` (Selenium) - Web testing utilities for form handling and navigation
- `web_wait_helpers.py` (Selenium) - Smart wait implementations and custom wait conditions

##### Utilities (`base/utilities/`)
- `csv_utils.py` - CSV file reading, writing, and data manipulation
- `datetime_utils.py` - Date/time parsing, formatting, timezone handling, and business day calculations
- `encoding_utils.py` - Encoding, decoding, hashing (MD5, SHA256), and encryption utilities
- `excel_reader.py` - Excel file reading with support for multiple sheets and data types
- `excel_writer.py` - Excel file creation with formatting, formulas, and charts
- `file_operations.py` - File system operations, compression, and file monitoring
- `json_utils.py` - JSON parsing, validation, JSONPath querying, and schema validation
- `string_utils.py` - String manipulation, regular expressions, and text processing
- `url_utils.py` - URL parsing, validation, and manipulation utilities
- `xml_utils.py` - XML parsing, validation, XPath querying, and transformation
- `yaml_utils.py` - YAML file processing, validation, and configuration management

#### Test Implementation (`SystemName (Example)/`)
Contains actual test implementations organized by automation type. Each test implementation serves as both working examples and templates for new projects.

Each automation type follows the same standardized structure:
- `features/` - Gherkin feature files with business-readable scenarios
- `pageobjects/` - Page object implementations following the Page Object Model pattern
- `steps/` - Step definition implementations that bridge Gherkin scenarios to page objects
- `environment.py` - Environment setup and teardown hooks specific to each automation type

##### Available Test Examples and Templates:

**API Testing (`API/`)**
- REST API testing examples with comprehensive CRUD operations
- Authentication patterns (Bearer tokens, API keys, OAuth 2.0)
- JSON schema validation and response verification
- Error handling and edge case testing
- Performance testing and load simulation
- Contract testing and API versioning

**Database Testing (`DB/`)**
- Multi-database support with connection management
- CRUD operations with transaction handling
- Data migration and schema validation testing
- Performance monitoring and query optimization
- Data integrity and constraint validation
- Backup and restore operation testing

**Desktop Application Testing (`Desktop/`)**
- Native application automation examples
- Cross-platform desktop testing (Windows, macOS, Linux)
- UI element interaction and validation
- File system operations and registry testing
- Process management and application lifecycle
- Accessibility testing and screen reader compatibility

**Mobile Testing (`Mobile/`)**
- Native and hybrid mobile app testing
- Cross-platform mobile testing (iOS and Android)
- Touch gestures, device rotation, and sensor simulation
- App installation, upgrade, and uninstallation testing
- Performance testing and battery usage monitoring
- Real device and emulator/simulator testing

**Modern Web Testing (`Web (Playwright)/`)**
- Modern browser automation with Playwright
- Fast, reliable, and parallel test execution
- Advanced features like network interception and mobile emulation
- Visual testing and screenshot comparison
- Performance metrics and accessibility testing
- Cross-browser testing with WebKit support

**Traditional Web Testing (`Web (Selenium)/`)**
- Mature web automation with Selenium WebDriver
- Cross-browser compatibility testing
- Selenium Grid integration for distributed testing
- Legacy browser support and enterprise features
- Custom wait strategies and element handling
- Integration with cloud testing platforms

## 🔧 Configuration

### Behave Configuration (`behave.ini`)
```ini
[behave]
# Output formatting
default_format = pretty
show_skipped = true
show_timings = true
show_multiline = true

# Logging configuration
capture = false
logging_level = INFO
logging_format = %(levelname)-8s %(name)s: %(message)s

# Path configuration
paths = SystemName (Example)/
step_registry = steps

# Tag configuration
default_tags = ~@skip ~@wip

# Reporting
junit = true
junit_directory = reports/junit

# Custom formatters
format = allure_behave.formatter:AllureFormatter
outdir = reports/allure

# Feature file execution
stop_on_first_failure = false
```

### Advanced Configuration Options
```ini
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

### Environment Variables
Set these environment variables for different configurations:

#### API Testing Configuration
```bash
# Base configuration
export API_BASE_URL="https://api.example.com"
export API_VERSION="v1"
export API_KEY="your-api-key-here"
export API_SECRET="your-api-secret"

# Authentication
export AUTH_TYPE="bearer"  # bearer, basic, api_key, oauth2
export TOKEN_ENDPOINT="https://auth.example.com/token"
export CLIENT_ID="your-client-id"
export CLIENT_SECRET="your-client-secret"

# Request configuration
export API_TIMEOUT="30"
export MAX_RETRIES="3"
export RETRY_DELAY="1"
```

#### Web Testing Configuration  
```bash
# Browser configuration
export BROWSER="chrome"  # chrome, firefox, edge, safari
export BROWSER_VERSION="latest"
export HEADLESS="false"
export WINDOW_SIZE="1920x1080"

# Application configuration
export WEB_BASE_URL="https://app.example.com"
export LOGIN_URL="https://app.example.com/login"
export DEFAULT_TIMEOUT="10"
export PAGE_LOAD_TIMEOUT="30"

# Selenium Grid (optional)
export SELENIUM_HUB_URL="http://selenium-hub:4444/wd/hub"
export SELENIUM_REMOTE="false"

# Playwright specific
export PLAYWRIGHT_BROWSERS_PATH="/path/to/browsers"
export PLAYWRIGHT_TIMEOUT="30000"
```

#### Mobile Testing Configuration
```bash
# Platform configuration
export PLATFORM_NAME="Android"  # Android, iOS
export PLATFORM_VERSION="12.0"
export DEVICE_NAME="emulator-5554"
export DEVICE_UDID="auto"

# App configuration
export APP_PATH="/path/to/app.apk"  # or .ipa for iOS
export APP_PACKAGE="com.example.app"
export APP_ACTIVITY="com.example.MainActivity"
export BUNDLE_ID="com.example.app"  # iOS

# Appium server
export APPIUM_SERVER="http://localhost:4723"
export APPIUM_TIMEOUT="60"
export IMPLICIT_WAIT="10"

# Cloud testing (optional)
export CLOUD_PROVIDER="browserstack"  # browserstack, saucelabs, aws
export CLOUD_USERNAME="your-username"
export CLOUD_ACCESS_KEY="your-access-key"
```

#### Database Testing Configuration
```bash
# Primary database
export DB_TYPE="postgresql"  # postgresql, mysql, sqlite, mongodb, redis
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="test_database"
export DB_USER="test_user"
export DB_PASSWORD="test_password"
export DB_SCHEMA="public"

# Connection pool settings
export DB_POOL_SIZE="10"
export DB_MAX_CONNECTIONS="20"
export DB_CONNECTION_TIMEOUT="30"

# Multiple database support
export DB_READ_HOST="read-replica.example.com"
export DB_WRITE_HOST="master.example.com"

# MongoDB specific
export MONGO_URI="mongodb://user:pass@localhost:27017/testdb"
export MONGO_AUTH_SOURCE="admin"

# Redis specific
export REDIS_URL="redis://localhost:6379/0"
export REDIS_PASSWORD="redis-password"
```

#### Desktop Testing Configuration
```bash
# Application configuration
export DESKTOP_APP_PATH="/path/to/application.exe"
export DESKTOP_APP_ARGS="--test-mode --debug"
export DESKTOP_WORKING_DIR="/path/to/working/directory"

# Windows specific
export WINDOWS_APP_ID="Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"
export WINDOWS_DRIVER_URL="http://localhost:9999"

# macOS specific
export MACOS_BUNDLE_ID="com.apple.calculator"
export MACOS_APP_PATH="/Applications/Calculator.app"

# Linux specific
export LINUX_DISPLAY=":0"
export LINUX_WM="gnome"  # gnome, kde, xfce
```

#### General Configuration
```bash
# Environment selection
export TEST_ENVIRONMENT="staging"  # dev, staging, prod
export REGION="us-east-1"
export LOCALE="en_US"

# Reporting and logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
export REPORT_FORMAT="allure"  # allure, html, json, junit
export SCREENSHOT_ON_FAILURE="true"
export VIDEO_RECORDING="false"

# Performance and timeouts
export GLOBAL_TIMEOUT="60"
export RETRY_ATTEMPTS="3"
export PARALLEL_WORKERS="4"

# CI/CD specific
export CI="true"
export BUILD_NUMBER="123"
export BUILD_URL="https://ci.example.com/build/123"
export GIT_COMMIT="abc123def456"
export GIT_BRANCH="main"
```

### Configuration Files
```bash
# Environment-specific configuration files
config/
├── dev.yaml          # Development environment
├── staging.yaml      # Staging environment  
├── prod.yaml         # Production environment
└── local.yaml        # Local development overrides

# Example dev.yaml
api:
  base_url: "https://dev-api.example.com"
  timeout: 30
  retry_count: 3

web:
  base_url: "https://dev-app.example.com"
  browser: "chrome"
  headless: false

database:
  host: "dev-db.example.com"
  port: 5432
  name: "dev_database"
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

### Allure Reports (Recommended)
Generate comprehensive, interactive HTML reports with rich visualizations:

```bash
# Install Allure (one-time setup)
pip install allure-behave

# Run tests with Allure reporting
behave -f allure_behave.formatter:AllureFormatter -o reports/allure --tags=@smoke

# Generate and serve interactive report
allure serve reports/allure

# Generate static HTML report
allure generate reports/allure -o reports/allure-html --clean

# Open generated report
# Windows
start reports/allure-html/index.html
# macOS
open reports/allure-html/index.html
# Linux
xdg-open reports/allure-html/index.html
```

### Built-in Reporting Formats
```bash
# HTML Report (simple)
behave --format=html --outfile=reports/report.html

# JSON Report (for CI/CD integration)
behave --format=json --outfile=reports/results.json

# JUnit XML (for Jenkins integration)
behave --format=junit --outfile=reports/junit_results.xml

# Progress format (lightweight)
behave --format=progress

# Pretty format (detailed console output)
behave --format=pretty --no-capture

# Multiple formats simultaneously
behave --format=pretty --format=json --outfile=reports/results.json
```

### Screenshots and Artifacts
- **Screenshots**: Automatically captured on test failures and saved to `screenshots/` directory
- **Video Recordings**: Test execution videos for Playwright tests (configurable)
- **Network Logs**: API request/response logs saved to `logs/api/` directory
- **Performance Metrics**: Response times, memory usage, and CPU utilization logs
- **Database Snapshots**: Before/after database state captures for debugging
- **Browser Logs**: Console logs and JavaScript errors captured during web testing

### Report Features
- **Test Execution Timeline**: Visual timeline of test execution with duration
- **Environment Information**: Browser version, OS, Python version, framework versions
- **Test Categories**: Organized by test type (API, Web, Mobile, DB, Desktop)
- **Failure Analysis**: Detailed failure reasons with stack traces and screenshots
- **Trend Analysis**: Historical test execution trends and performance metrics
- **Parallel Execution**: Support for parallel test execution with combined reporting

### Custom Reporting
```python
# Custom report generation in environment.py
def after_all(context):
    """Generate custom reports after all tests complete"""
    generate_performance_report(context)
    generate_coverage_report(context)
    send_slack_notification(context.test_results)
    
def after_scenario(context, scenario):
    """Capture artifacts after each scenario"""
    if scenario.status == "failed":
        capture_screenshot(context, scenario.name)
        capture_browser_logs(context)
        capture_network_logs(context)
```

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

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Automated Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        test-type: [api, web-playwright, web-selenium, db, mobile]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        playwright install
    
    - name: Run tests
      run: |
        behave "SystemName (Example)/${{ matrix.test-type }}/features/" --tags=@smoke
    
    - name: Generate Allure Report
      if: always()
      run: |
        allure generate reports/allure -o reports/allure-html --clean
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.test-type }}-${{ matrix.python-version }}
        path: reports/
```

### Jenkins Pipeline
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    parameters {
        choice(name: 'TEST_ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Test Environment')
        choice(name: 'TEST_TYPE', choices: ['all', 'smoke', 'regression'], description: 'Test Type')
        booleanParam(name: 'PARALLEL_EXECUTION', defaultValue: true, description: 'Run tests in parallel')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
                sh '. venv/bin/activate && playwright install'
            }
        }
        
        stage('Test Execution') {
            parallel {
                stage('API Tests') {
                    steps {
                        sh """
                            . venv/bin/activate
                            behave "SystemName (Example)/API/features/" --tags=@${params.TEST_TYPE} \
                            -D environment=${params.TEST_ENVIRONMENT} \
                            -f allure_behave.formatter:AllureFormatter -o reports/allure-api
                        """
                    }
                }
                stage('Web Tests') {
                    steps {
                        sh """
                            . venv/bin/activate
                            behave "SystemName (Example)/Web (Playwright)/features/" --tags=@${params.TEST_TYPE} \
                            -D environment=${params.TEST_ENVIRONMENT} \
                            -f allure_behave.formatter:AllureFormatter -o reports/allure-web
                        """
                    }
                }
            }
        }
        
        stage('Report Generation') {
            steps {
                sh 'allure generate reports/allure-* -o reports/allure-combined --clean'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports/allure-combined',
                    reportFiles: 'index.html',
                    reportName: 'Allure Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*', fingerprint: true
            cleanWs()
        }
    }
}
```

### Docker Support
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Playwright
RUN wget -qO- https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Copy test framework
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Default command
CMD ["behave", "--tags=@smoke", "--format=pretty"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  test-runner:
    build: .
    volumes:
      - ./reports:/app/reports
      - ./screenshots:/app/screenshots
    environment:
      - TEST_ENVIRONMENT=staging
      - PARALLEL_WORKERS=4
    depends_on:
      - selenium-hub
      - test-db
      
  selenium-hub:
    image: selenium/hub:4.15.0
    ports:
      - "4444:4444"
      
  chrome:
    image: selenium/node-chrome:4.15.0
    depends_on:
      - selenium-hub
    environment:
      - HUB_HOST=selenium-hub
      
  test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
    ports:
      - "5432:5432"
```

## 🔧 Advanced Configuration

### Custom Environment Setup
```python
# custom_environment.py
import os
from behave import fixture

@fixture
def custom_api_client(context):
    """Custom API client with enhanced features"""
    from base.api.api_client import APIClient
    
    client = APIClient(
        base_url=os.getenv('API_BASE_URL'),
        timeout=int(os.getenv('API_TIMEOUT', 30)),
        retry_count=int(os.getenv('RETRY_COUNT', 3))
    )
    
    # Add custom headers
    client.add_header('X-Test-Suite', 'behave-automation')
    client.add_header('X-Environment', os.getenv('TEST_ENVIRONMENT', 'dev'))
    
    return client

def before_all(context):
    """Global setup before all tests"""
    context.config.setup_logging()
    context.custom_api = custom_api_client(context)
    
def after_all(context):
    """Global cleanup after all tests"""
    generate_test_summary(context)
    cleanup_test_data(context)
```

### Performance Monitoring
```python
# performance_monitor.py
import time
import psutil
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        
    def start_monitoring(self, test_name: str):
        """Start performance monitoring for a test"""
        self.metrics[test_name] = {
            'start_time': time.time(),
            'start_memory': psutil.virtual_memory().used,
            'start_cpu': psutil.cpu_percent()
        }
        
    def stop_monitoring(self, test_name: str) -> Dict[str, Any]:
        """Stop monitoring and return metrics"""
        if test_name not in self.metrics:
            return {}
            
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        end_cpu = psutil.cpu_percent()
        
        return {
            'execution_time': end_time - self.metrics[test_name]['start_time'],
            'memory_usage': end_memory - self.metrics[test_name]['start_memory'],
            'avg_cpu_usage': (self.metrics[test_name]['start_cpu'] + end_cpu) / 2
        }
```

## 🏷️ Version Information

**Current Version**: 3.0.0
**Last Updated**: September 2025
**Python Compatibility**: 3.9+
**Framework Dependencies**:
- Behave: 1.2.7+
- Selenium: 4.25.0+
- Playwright: 1.47.0+
- Requests: 2.31.0+
- Appium-Python-Client: 4.1.0+

### Version History
- **v3.0.0** (September 2025): Major update with enhanced CI/CD integration, performance monitoring, and advanced reporting
- **v2.5.0** (August 2025): Added Docker support, improved database managers, and cloud testing integration
- **v2.0.0** (July 2025): Complete framework restructure with modular architecture and comprehensive utilities
- **v1.5.0** (June 2025): Added Playwright support and mobile testing capabilities
- **v1.0.0** (May 2025): Initial release with basic web and API testing support

---

**Happy Testing! 🚀**

*For questions, issues, or contributions, please refer to the project documentation, create an issue in the repository, or join our community discussions.*

---

**Repository**: [Behave Framework](https://github.com/AlbertGroenwold/cqh_behave_framework)  
**Maintainer**: Albert Groenwold  
**Created**: 2025  
**Framework Type**: Behavior-Driven Development (BDD) Test Automation

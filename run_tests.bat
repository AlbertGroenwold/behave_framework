@echo off
REM ============================================================================
REM Central Quality Hub - Test Execution Script for Windows
REM ============================================================================
REM This script provides convenient commands to run different types of tests
REM in the automation framework with proper environment setup.
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo Central Quality Hub - Test Runner
echo ============================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if "%1"=="" (
    echo Usage: run_tests.bat [command] [options]
    echo.
    echo Available commands:
    echo   all              - Run all tests from all frameworks
    echo   api              - Run API tests
    echo   web              - Run Web tests (Selenium)
    echo   mobile           - Run Mobile tests (Appium)
    echo   database         - Run Database tests
    echo   desktop          - Run Desktop tests
    echo   smoke            - Run smoke tests from all frameworks
    echo   regression       - Run regression tests from all frameworks
    echo   report           - Generate and open Allure report
    echo   clean            - Clean reports and artifacts
    echo   help             - Show detailed help
    echo.
    echo Quick Examples:
    echo   run_tests.bat api             - Run all API tests
    echo   run_tests.bat smoke           - Run all smoke tests
    echo   run_tests.bat api --tags=@users  - Run API user tests only
    echo.
    echo For detailed help: run_tests.bat help
    echo.
    goto :end
)

if "%1"=="help" (
    echo.
    echo ============================================================================
    echo Detailed Usage Guide
    echo ============================================================================
    echo.
    echo Test Type Commands:
    echo   run_tests.bat api              - Run all API tests
    echo   run_tests.bat web              - Run all Web tests
    echo   run_tests.bat mobile           - Run all Mobile tests  
    echo   run_tests.bat database         - Run all Database tests
    echo   run_tests.bat desktop          - Run all Desktop tests
    echo.
    echo Tag-based Commands:
    echo   run_tests.bat smoke            - Run smoke tests across all frameworks
    echo   run_tests.bat regression       - Run regression tests
    echo   run_tests.bat crud             - Run CRUD operation tests
    echo   run_tests.bat login            - Run login functionality tests
    echo.
    echo Advanced Options:
    echo   run_tests.bat api --tags=@users       - Run only user-related API tests
    echo   run_tests.bat web --tags=@smoke       - Run only web smoke tests
    echo   run_tests.bat all --tags=~@skip       - Run all tests except skipped ones
    echo.
    echo Reporting Commands:
    echo   run_tests.bat report           - Generate and open Allure report
    echo   run_tests.bat clean            - Clean reports and artifacts
    echo.
    echo Environment Options:
    echo   You can set environment variables before running:
    echo   set BROWSER=chrome ^&^& run_tests.bat web
    echo   set API_BASE_URL=https://staging.api.com ^&^& run_tests.bat api
    echo.
    echo Examples:
    echo   run_tests.bat api --tags=@smoke --format=allure
    echo   run_tests.bat web --tags="@login and @chrome"
    echo   run_tests.bat all --tags=@regression --processes=4
    echo.
    goto :end
)

REM Create reports directory if it doesn't exist
if not exist "reports" mkdir reports
if not exist "logs" mkdir logs
if not exist "screenshots" mkdir screenshots

REM Set timestamp for this test run
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

echo Test execution started at: %timestamp%
echo.

REM Process the command
if "%1"=="all" (
    echo ============================================================================
    echo Running ALL Tests
    echo ============================================================================
    echo Running API tests...
    behave CentralQualityHub\API\features\ %2 %3 %4 %5
    echo.
    echo Running Web tests...
    behave CentralQualityHub\Web\features\ %2 %3 %4 %5
    echo.
    echo Running Mobile tests...
    behave CentralQualityHub\Mobile\features\ %2 %3 %4 %5
    echo.
    echo Running Database tests...
    behave CentralQualityHub\DB\features\ %2 %3 %4 %5
    echo.
    echo Running Desktop tests...
    behave CentralQualityHub\Desktop\features\ %2 %3 %4 %5
    echo.
    goto :end
)

if "%1"=="api" (
    echo ============================================================================
    echo Running API Tests
    echo ============================================================================
    behave CentralQualityHub\API\features\ %2 %3 %4 %5
    goto :end
)

if "%1"=="web" (
    echo ============================================================================
    echo Running Web Tests (Selenium)
    echo ============================================================================
    behave CentralQualityHub\Web\features\ %2 %3 %4 %5
    goto :end
)

if "%1"=="mobile" (
    echo ============================================================================
    echo Running Mobile Tests (Appium)
    echo ============================================================================
    behave CentralQualityHub\Mobile\features\ %2 %3 %4 %5
    goto :end
)

if "%1"=="database" (
    echo ============================================================================
    echo Running Database Tests
    echo ============================================================================
    behave CentralQualityHub\DB\features\ %2 %3 %4 %5
    goto :end
)

if "%1"=="desktop" (
    echo ============================================================================
    echo Running Desktop Tests
    echo ============================================================================
    behave CentralQualityHub\Desktop\features\ %2 %3 %4 %5
    goto :end
)

if "%1"=="smoke" (
    echo ============================================================================
    echo Running SMOKE Tests (All Frameworks)
    echo ============================================================================
    behave --tags=@smoke %2 %3 %4 %5
    goto :end
)

if "%1"=="regression" (
    echo ============================================================================
    echo Running REGRESSION Tests (All Frameworks)
    echo ============================================================================
    behave --tags=@regression %2 %3 %4 %5
    goto :end
)

if "%1"=="crud" (
    echo ============================================================================
    echo Running CRUD Tests (All Frameworks)
    echo ============================================================================
    behave --tags=@crud %2 %3 %4 %5
    goto :end
)

if "%1"=="login" (
    echo ============================================================================
    echo Running LOGIN Tests (All Frameworks)
    echo ============================================================================
    behave --tags=@login %2 %3 %4 %5
    goto :end
)

if "%1"=="clean" (
    echo ============================================================================
    echo Cleaning Reports and Artifacts
    echo ============================================================================
    if exist "reports" rmdir /s /q reports
    if exist "logs" rmdir /s /q logs
    if exist "screenshots" rmdir /s /q screenshots
    if exist "allure-results" rmdir /s /q allure-results
    
    REM Recreate directories
    mkdir reports\api
    mkdir reports\web
    mkdir reports\mobile
    mkdir reports\database
    mkdir reports\desktop
    mkdir reports\allure
    mkdir logs
    mkdir screenshots
    
    echo Cleanup completed successfully!
    goto :end
)

if "%1"=="report" (
    echo ============================================================================
    echo Generating Allure Report
    echo ============================================================================
    if not exist "reports\allure" mkdir reports\allure
    
    REM Check if allure is installed
    allure --version >nul 2>&1
    if errorlevel 1 (
        echo Allure is not installed or not in PATH
        echo Please install Allure from: https://docs.qameta.io/allure/#_installing_a_commandline
        echo Or use: pip install allure-behave
    ) else (
        allure generate reports\allure --clean -o reports\allure-report
        if exist "reports\allure-report\index.html" (
            echo Opening Allure report in browser...
            start reports\allure-report\index.html
        ) else (
            echo No test results found for report generation
            echo Run some tests first with allure formatter:
            echo behave -f allure_behave.formatter:AllureFormatter -o reports\allure
        )
    )
    goto :end
)

REM If we get here, the command was not recognized
echo ERROR: Unknown command '%1'
echo.
echo Available commands: all, api, web, mobile, database, desktop, smoke, regression, crud, login, clean, report, help
echo For detailed help: run_tests.bat help
echo.

:end
echo.
echo ============================================================================
echo Test execution completed
echo ============================================================================
echo.
pause

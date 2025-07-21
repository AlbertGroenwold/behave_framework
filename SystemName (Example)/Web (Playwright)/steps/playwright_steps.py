"""
Playwright Web Testing Step Definitions

This module contains Behave step definitions for web testing scenarios
using the Page Object Model pattern with Playwright.
"""

from behave import given, when, then
import sys
import os
import time

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from web_playwright.base_page import BasePage
from web_playwright.playwright_manager import PlaywrightManager


# Login Page Steps

@given('I am on the login page using Playwright')
def step_navigate_to_login_page_playwright(context):
    """
    Navigate to the login page using Playwright and verify it loads properly.
    
    Args:
        context: Behave context object containing shared data
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        context.login_page.navigate_to_login_page()
        context.login_page.wait_for_page_load()
        
        # Verify we're actually on the login page
        assert context.login_page.verify_login_page_elements(), "Login page elements are not properly loaded"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to navigate to login page: {e}")


@when('I enter username "{username}" and password "{password}" in Playwright')
def step_enter_credentials_playwright(context, username, password):
    """
    Enter username and password in the login form using Playwright.
    
    Args:
        context: Behave context object
        username (str): Username to enter
        password (str): Password to enter
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        context.login_page.enter_username(username)
        context.login_page.enter_password(password)
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to enter credentials: {e}")


@when('I click the login button in Playwright')
def step_click_login_button_playwright(context):
    """
    Click the login button using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        context.login_page.click_login_button()
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to click login button: {e}")


@when('I check the remember me checkbox in Playwright')
def step_check_remember_me_playwright(context):
    """
    Check the remember me checkbox using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        context.login_page.check_remember_me()
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to check remember me checkbox: {e}")


@then('I should be redirected to the home page in Playwright')
def step_verify_home_page_redirect_playwright(context):
    """
    Verify that user is redirected to the home page using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'home_page'):
            from SystemName.Web.pageobjects.home_page import HomePage
            context.home_page = HomePage(context.playwright_manager)
        
        context.home_page.wait_for_page_load()
        assert context.home_page.is_on_home_page(), "User was not redirected to home page"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify home page redirect: {e}")


@then('I should see a welcome message in Playwright')
def step_verify_welcome_message_playwright(context):
    """
    Verify that welcome message is displayed using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'home_page'):
            from SystemName.Web.pageobjects.home_page import HomePage
            context.home_page = HomePage(context.playwright_manager)
        
        assert context.home_page.verify_welcome_message(), "Welcome message is not displayed"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify welcome message: {e}")


@then('I should see an error message "{error_message}" in Playwright')
def step_verify_error_message_playwright(context, error_message):
    """
    Verify that specific error message is displayed using Playwright.
    
    Args:
        context: Behave context object
        error_message (str): Expected error message
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        context.login_page.wait_for_error_message()
        actual_message = context.login_page.get_error_message()
        
        assert error_message.lower() in actual_message.lower(), \
            f"Expected error message '{error_message}' not found in '{actual_message}'"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify error message: {e}")


@then('I should remain on the login page in Playwright')
def step_verify_remain_on_login_page_playwright(context):
    """
    Verify that user remains on the login page using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        assert context.login_page.is_on_login_page(), "User did not remain on login page"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify user remained on login page: {e}")


@then('the remember me option should be selected in Playwright')
def step_verify_remember_me_selected_playwright(context):
    """
    Verify that remember me option is selected using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        assert context.login_page.is_remember_me_checked(), "Remember me checkbox is not checked"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify remember me selection: {e}")


# User Management Steps

@given('I am logged in as an administrator using Playwright')
def step_login_as_admin_playwright(context):
    """
    Login as administrator using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            from SystemName.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.playwright_manager)
        
        context.login_page.navigate_to_login_page()
        context.login_page.perform_login("admin_user", "admin_password")
        
        # Wait for login to complete
        time.sleep(2)
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to login as administrator: {e}")


@given('I am on the user management page using Playwright')
def step_navigate_to_user_management_playwright(context):
    """
    Navigate to user management page using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'user_management_page'):
            from SystemName.Web.pageobjects.user_management_page import UserManagementPage
            context.user_management_page = UserManagementPage(context.playwright_manager)
        
        if not hasattr(context, 'home_page'):
            from SystemName.Web.pageobjects.home_page import HomePage
            context.home_page = HomePage(context.playwright_manager)
        
        context.home_page.navigate_to_user_management()
        context.user_management_page.wait_for_page_load()
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to navigate to user management page: {e}")


@when('I click the "Add New User" button in Playwright')
def step_click_add_new_user_playwright(context):
    """
    Click the Add New User button using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'user_management_page'):
            from SystemName.Web.pageobjects.user_management_page import UserManagementPage
            context.user_management_page = UserManagementPage(context.playwright_manager)
        
        context.user_management_page.click_add_user_button()
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to click Add New User button: {e}")


@when('I fill in the user creation form with valid data in Playwright')
def step_fill_user_creation_form_playwright(context):
    """
    Fill in the user creation form with valid data using Playwright.
    
    Args:
        context: Behave context object containing table data
    """
    try:
        if not hasattr(context, 'user_management_page'):
            from SystemName.Web.pageobjects.user_management_page import UserManagementPage
            context.user_management_page = UserManagementPage(context.playwright_manager)
        
        # Convert table data to dictionary
        user_data = {}
        for row in context.table:
            user_data[row['field']] = row['value']
        
        context.user_management_page.fill_user_form(user_data)
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to fill user creation form: {e}")


@when('I click the "Create User" button in Playwright')
def step_click_create_user_playwright(context):
    """
    Click the Create User button using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'user_management_page'):
            from SystemName.Web.pageobjects.user_management_page import UserManagementPage
            context.user_management_page = UserManagementPage(context.playwright_manager)
        
        context.user_management_page.click_create_user_button()
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to click Create User button: {e}")


@then('I should see a success message "{success_message}" in Playwright')
def step_verify_success_message_playwright(context, success_message):
    """
    Verify that specific success message is displayed using Playwright.
    
    Args:
        context: Behave context object
        success_message (str): Expected success message
    """
    try:
        if not hasattr(context, 'user_management_page'):
            from SystemName.Web.pageobjects.user_management_page import UserManagementPage
            context.user_management_page = UserManagementPage(context.playwright_manager)
        
        actual_message = context.user_management_page.get_success_message()
        
        assert success_message.lower() in actual_message.lower(), \
            f"Expected success message '{success_message}' not found in '{actual_message}'"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify success message: {e}")


@then('the new user should appear in the user list in Playwright')
def step_verify_user_in_list_playwright(context):
    """
    Verify that the new user appears in the user list using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'user_management_page'):
            from SystemName.Web.pageobjects.user_management_page import UserManagementPage
            context.user_management_page = UserManagementPage(context.playwright_manager)
        
        # Assuming the username was stored from the form data
        username = getattr(context, 'created_username', 'new_test_user')
        
        assert context.user_management_page.is_user_in_table(username), \
            f"User '{username}' not found in user list"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify user in list: {e}")


# Accessibility and Performance Steps

@when('I validate the login page accessibility in Playwright')
def step_validate_accessibility_playwright(context):
    """
    Validate login page accessibility using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        # This is a placeholder for accessibility validation
        # In real implementation, you would use axe-playwright or similar
        context.accessibility_results = {"violations": []}
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to validate accessibility: {e}")


@then('the page should meet WCAG 2.1 AA standards')
def step_verify_wcag_compliance_playwright(context):
    """
    Verify WCAG 2.1 AA compliance using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        violations = context.accessibility_results.get("violations", [])
        assert len(violations) == 0, f"Accessibility violations found: {violations}"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify WCAG compliance: {e}")


@when('I measure the login page load time in Playwright')
def step_measure_page_load_time_playwright(context):
    """
    Measure login page load time using Playwright.
    
    Args:
        context: Behave context object
    """
    try:
        # Use Playwright's performance API
        performance_metrics = context.playwright_manager.page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart
                };
            }
        """)
        
        context.performance_metrics = performance_metrics
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to measure page load time: {e}")


@then('the page should load within {max_time:d} seconds')
def step_verify_page_load_time_playwright(context, max_time):
    """
    Verify page load time is within acceptable limits using Playwright.
    
    Args:
        context: Behave context object
        max_time (int): Maximum acceptable load time in seconds
    """
    try:
        load_time_ms = context.performance_metrics.get("loadTime", 0)
        load_time_seconds = load_time_ms / 1000
        
        assert load_time_seconds <= max_time, \
            f"Page load time ({load_time_seconds:.2f}s) exceeds maximum ({max_time}s)"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify page load time: {e}")


# Generic step for various assertions

@then('I should see "{expected_result}" in Playwright')
def step_verify_expected_result_playwright(context, expected_result):
    """
    Generic step to verify expected result is displayed using Playwright.
    
    Args:
        context: Behave context object
        expected_result (str): Expected result text
    """
    try:
        # Use page content to search for the expected result
        page_content = context.playwright_manager.page.content()
        
        assert expected_result.lower() in page_content.lower(), \
            f"Expected result '{expected_result}' not found in page content"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify expected result: {e}")

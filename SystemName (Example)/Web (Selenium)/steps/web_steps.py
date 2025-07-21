"""
Web Testing Step Definitions

This module contains Behave step definitions for web testing scenarios
using the Page Object Model pattern with Selenium WebDriver.
"""

from behave import given, when, then
import sys
import os
import time

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from web_selenium.base_page import BasePage
from web_selenium.webdriver_manager import WebDriverManager


# Login Page Steps

@given('I am on the login page')
def step_navigate_to_login_page(context):
    """
    Navigate to the login page and verify it loads properly.
    
    Args:
        context: Behave context object containing shared data
    """
    try:
        if not hasattr(context, 'login_page'):
            from CentralQualityHub.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.driver)
        
        context.login_page.navigate_to_login_page()
        context.login_page.wait_for_page_load()
        
        # Verify we're actually on the login page
        assert context.login_page.verify_login_page_elements(), "Login page elements are not properly loaded"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to navigate to login page: {e}")


@when('I enter username "{username}" and password "{password}"')
def step_enter_credentials(context, username, password):
    """
    Enter username and password in the login form.
    
    Args:
        context: Behave context object
        username (str): Username to enter
        password (str): Password to enter
    """
    try:
        if not hasattr(context, 'login_page'):
            raise RuntimeError("Login page not initialized. Make sure you've navigated to the login page first.")
        
        # Clear any existing values and enter new credentials
        context.login_page.enter_username(username)
        context.login_page.enter_password(password)
        
        # Store credentials for verification if needed
        context.entered_username = username
        context.entered_password = password
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to enter credentials: {e}")


@when('I enter username "{username}"')
def step_enter_username_only(context, username):
    """
    Enter only username in the login form.
    
    Args:
        context: Behave context object
        username (str): Username to enter
    """
    try:
        if not hasattr(context, 'login_page'):
            raise RuntimeError("Login page not initialized. Make sure you've navigated to the login page first.")
        
        context.login_page.enter_username(username)
        context.entered_username = username
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to enter username: {e}")


@when('I enter password "{password}"')
def step_enter_password_only(context, password):
    """
    Enter only password in the login form.
    
    Args:
        context: Behave context object
        password (str): Password to enter
    """
    try:
        if not hasattr(context, 'login_page'):
            raise RuntimeError("Login page not initialized. Make sure you've navigated to the login page first.")
        
        context.login_page.enter_password(password)
        context.entered_password = password
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to enter password: {e}")


@when('I click the login button')
def step_click_login_button(context):
    """
    Click the login button to submit the form.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            raise RuntimeError("Login page not initialized. Make sure you've navigated to the login page first.")
        
        # Verify login button is enabled before clicking
        assert context.login_page.is_login_button_enabled(), "Login button is not enabled"
        
        context.login_page.click_login_button()
        
        # Wait a moment for page transition
        time.sleep(1)
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to click login button: {e}")


@when('I check the remember me checkbox')
def step_check_remember_me(context):
    """
    Check the remember me checkbox.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            raise RuntimeError("Login page not initialized. Make sure you've navigated to the login page first.")
        
        context.login_page.check_remember_me()
        
        # Verify checkbox is actually checked
        assert context.login_page.is_remember_me_checked(), "Remember me checkbox was not successfully checked"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to check remember me checkbox: {e}")


@when('I perform login with username "{username}" and password "{password}"')
def step_perform_complete_login(context, username, password):
    """
    Perform complete login operation with username and password.
    
    Args:
        context: Behave context object
        username (str): Username to use for login
        password (str): Password to use for login
    """
    try:
        if not hasattr(context, 'login_page'):
            from CentralQualityHub.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.driver)
        
        context.login_page.login(username, password)
        
        # Store credentials for later verification
        context.entered_username = username
        context.entered_password = password
        
        # Wait for page transition
        time.sleep(2)
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to perform login: {e}")


# Home Page Steps

@then('I should be redirected to the home page')
def step_verify_home_page_redirect(context):
    """
    Verify user is redirected to the home page after successful login.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'home_page'):
            from CentralQualityHub.Web.pageobjects.home_page import HomePage
            context.home_page = HomePage(context.driver)
        
        # Wait for page to load
        context.home_page.wait_for_home_page_to_load()
        
        # Verify we're actually on the home page
        current_url = context.home_page.get_current_url()
        assert "home" in current_url.lower() or "dashboard" in current_url.lower(), \
            f"Expected to be on home page, but current URL is: {current_url}"
        
        # Verify home page elements are present
        assert context.home_page.verify_home_page_elements(), \
            "Home page elements are not properly loaded"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify home page redirect: {e}")


@then('I should see a welcome message')
def step_verify_welcome_message(context):
    """
    Verify that a welcome message is displayed on the home page.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'home_page'):
            from CentralQualityHub.Web.pageobjects.home_page import HomePage
            context.home_page = HomePage(context.driver)
        
        assert context.home_page.is_welcome_message_displayed(), \
            "Welcome message is not displayed on the home page"
        
        welcome_text = context.home_page.get_welcome_message_text()
        assert welcome_text.strip(), "Welcome message text is empty"
        
        # Store welcome message for later verification if needed
        context.welcome_message = welcome_text
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify welcome message: {e}")


# Error Handling Steps

@then('I should see an error message')
def step_verify_error_message_displayed(context):
    """
    Verify that an error message is displayed.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            raise RuntimeError("Login page not initialized")
        
        # Wait a moment for error message to appear
        time.sleep(1)
        
        assert context.login_page.is_error_message_displayed(), \
            "Error message is not displayed when it should be"
        
        error_text = context.login_page.get_error_message_text()
        assert error_text.strip(), "Error message text is empty"
        
        # Store error message for later verification if needed
        context.error_message = error_text
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify error message: {e}")


@then('I should see an error message containing "{expected_text}"')
def step_verify_specific_error_message(context, expected_text):
    """
    Verify that an error message containing specific text is displayed.
    
    Args:
        context: Behave context object
        expected_text (str): Text that should be contained in the error message
    """
    try:
        if not hasattr(context, 'login_page'):
            raise RuntimeError("Login page not initialized")
        
        # Wait a moment for error message to appear
        time.sleep(1)
        
        assert context.login_page.is_error_message_displayed(), \
            "Error message is not displayed when it should be"
        
        error_text = context.login_page.get_error_message_text()
        assert expected_text.lower() in error_text.lower(), \
            f"Expected error message to contain '{expected_text}', but got: '{error_text}'"
        
        context.error_message = error_text
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify specific error message: {e}")


# Logout Steps

@when('I click the logout button')
def step_click_logout_button(context):
    """
    Click the logout button to sign out from the application.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'home_page'):
            from CentralQualityHub.Web.pageobjects.home_page import HomePage
            context.home_page = HomePage(context.driver)
        
        # Verify logout button is available
        assert context.home_page.is_logout_button_displayed(), \
            "Logout button is not displayed or accessible"
        
        context.home_page.click_logout_button()
        
        # Wait for logout process
        time.sleep(2)
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to click logout button: {e}")


@then('I should be redirected to the login page')
def step_verify_login_page_redirect(context):
    """
    Verify user is redirected back to the login page after logout.
    
    Args:
        context: Behave context object
    """
    try:
        if not hasattr(context, 'login_page'):
            from CentralQualityHub.Web.pageobjects.login_page import LoginPage
            context.login_page = LoginPage(context.driver)
        
        # Wait for page to load
        context.login_page.wait_for_page_load()
        
        # Verify we're back on the login page
        current_url = context.login_page.get_current_url()
        assert "login" in current_url.lower(), \
            f"Expected to be on login page after logout, but current URL is: {current_url}"
        
        # Verify login page elements are present
        assert context.login_page.verify_login_page_elements(), \
            "Login page elements are not properly loaded after logout"
        
    except Exception as e:
        context.test_failed = True
        raise AssertionError(f"Failed to verify login page redirect after logout: {e}")


@then('I should see a welcome message')
def step_verify_welcome_message(context):
    """Verify welcome message is displayed"""
    if not hasattr(context, 'home_page'):
        from CentralQualityHub.Web.pageobjects.home_page import HomePage
        context.home_page = HomePage(context.driver)
    assert context.home_page.is_welcome_message_displayed(), "Welcome message is not displayed"


@then('I should see an error message "{expected_message}"')
def step_verify_error_message(context, expected_message):
    """Verify error message is displayed with expected text"""
    assert context.login_page.is_error_message_displayed(), "Error message is not displayed"
    actual_message = context.login_page.get_error_message_text()
    assert expected_message in actual_message, f"Expected '{expected_message}' but got '{actual_message}'"


@then('I should remain on the login page')
def step_verify_remain_on_login_page(context):
    """Verify user remains on login page"""
    current_url = context.login_page.get_current_url()
    assert "login" in current_url, f"Expected to remain on login page, but current URL is: {current_url}"


@then('the remember me option should be selected')
def step_verify_remember_me_selected(context):
    """Verify remember me checkbox is selected"""
    assert context.login_page.is_remember_me_checked(), "Remember me checkbox is not selected"


@then('I should see "{expected_result}"')
def step_verify_expected_result(context, expected_result):
    """Verify expected result is displayed"""
    if not hasattr(context, 'home_page'):
        from CentralQualityHub.Web.pageobjects.home_page import HomePage
        context.home_page = HomePage(context.driver)
    
    page_text = context.home_page.get_page_text()
    assert expected_result in page_text, f"Expected '{expected_result}' not found in page text"


# User Management Steps
@given('I am logged in as an admin user')
def step_login_as_admin(context):
    """Login as admin user"""
    if not hasattr(context, 'login_page'):
        from CentralQualityHub.Web.pageobjects.login_page import LoginPage
        context.login_page = LoginPage(context.driver)
    
    context.login_page.navigate_to_login_page()
    context.login_page.enter_username("admin_user")
    context.login_page.enter_password("admin_password")
    context.login_page.click_login_button()


@given('I am on the user management page')
def step_navigate_to_user_management(context):
    """Navigate to user management page"""
    if not hasattr(context, 'user_management_page'):
        from CentralQualityHub.Web.pageobjects.user_management_page import UserManagementPage
        context.user_management_page = UserManagementPage(context.driver)
    context.user_management_page.navigate_to_user_management()


@when('I click on "{button_text}" button')
def step_click_button(context, button_text):
    """Click on specified button"""
    context.user_management_page.click_button(button_text)


@when('I fill in the user details')
def step_fill_user_details(context):
    """Fill in user details from table"""
    for row in context.table:
        field = row['Field']
        value = row['Value']
        context.user_management_page.fill_field(field, value)


@when('I click "{button_text}" button')
def step_click_specific_button(context, button_text):
    """Click specific button"""
    context.user_management_page.click_button(button_text)


@then('the user should be created successfully')
def step_verify_user_created(context):
    """Verify user was created successfully"""
    assert context.user_management_page.is_success_message_displayed(), "Success message not displayed"


@then('I should see the user in the user list')
def step_verify_user_in_list(context):
    """Verify user appears in user list"""
    assert context.user_management_page.is_user_in_list("newuser123"), "User not found in list"


@given('there is an existing user "{username}"')
def step_create_existing_user(context, username):
    """Ensure existing user exists (test data setup)"""
    context.user_management_page.ensure_user_exists(username)


@when('I click on the edit button for user "{username}"')
def step_click_edit_user(context, username):
    """Click edit button for specific user"""
    context.user_management_page.click_edit_user(username)


@when('I update the email to "{new_email}"')
def step_update_email(context, new_email):
    """Update user email"""
    context.user_management_page.update_user_email(new_email)


@when('I click "Save Changes" button')
def step_save_changes(context):
    """Click save changes button"""
    context.user_management_page.click_save_changes()


@then('the user details should be updated')
def step_verify_user_updated(context):
    """Verify user details were updated"""
    assert context.user_management_page.is_update_success_displayed(), "Update success message not displayed"


@then('I should see the updated email in the user list')
def step_verify_updated_email(context):
    """Verify updated email appears in user list"""
    assert context.user_management_page.is_email_updated("updated@test.com"), "Updated email not found"

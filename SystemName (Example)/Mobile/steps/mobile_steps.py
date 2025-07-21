from behave import given, when, then
import sys
import os

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from mobile.base_mobile_page import BaseMobilePage
from mobile.mobile_driver_manager import MobileDriverManager


@given('I have the mobile app installed and running')
def step_mobile_app_running(context):
    """Ensure mobile app is installed and running"""
    if not hasattr(context, 'mobile_login_page'):
        from CentralQualityHub.Mobile.pageobjects.mobile_login_page import MobileLoginPage
        context.mobile_login_page = MobileLoginPage(context.driver)
    
    # Verify app is running
    assert context.mobile_login_page.is_app_launched(), "Mobile app is not running"


@when('I enter mobile username "{username}" and password "{password}"')
def step_enter_mobile_credentials(context, username, password):
    """Enter username and password in mobile app"""
    context.mobile_login_page.enter_username(username)
    context.mobile_login_page.enter_password(password)


@when('I tap the login button')
def step_tap_login_button(context):
    """Tap the login button"""
    context.mobile_login_page.tap_login_button()


@then('I should be logged into the mobile app')
def step_verify_mobile_login_success(context):
    """Verify successful login to mobile app"""
    if not hasattr(context, 'mobile_home_page'):
        from CentralQualityHub.Mobile.pageobjects.mobile_home_page import MobileHomePage
        context.mobile_home_page = MobileHomePage(context.driver)
    
    assert context.mobile_home_page.is_logged_in(), "User is not logged into mobile app"


@then('I should see the mobile home screen')
def step_verify_mobile_home_screen(context):
    """Verify mobile home screen is displayed"""
    if not hasattr(context, 'mobile_home_page'):
        from CentralQualityHub.Mobile.pageobjects.mobile_home_page import MobileHomePage
        context.mobile_home_page = MobileHomePage(context.driver)
    
    assert context.mobile_home_page.is_home_screen_displayed(), "Mobile home screen is not displayed"


@then('I should see a mobile error message')
def step_verify_mobile_error_message(context):
    """Verify mobile error message is displayed"""
    assert context.mobile_login_page.is_error_message_displayed(), "Mobile error message is not displayed"


@then('I should remain on the mobile login screen')
def step_verify_remain_on_mobile_login(context):
    """Verify user remains on mobile login screen"""
    assert context.mobile_login_page.is_login_screen_displayed(), "Not on mobile login screen"


@given('biometric authentication is enabled')
def step_biometric_enabled(context):
    """Ensure biometric authentication is enabled"""
    context.mobile_login_page.ensure_biometric_enabled()


@when('I tap the biometric login button')
def step_tap_biometric_login(context):
    """Tap biometric login button"""
    context.mobile_login_page.tap_biometric_login_button()


@when('I provide valid biometric authentication')
def step_provide_biometric_auth(context):
    """Provide valid biometric authentication"""
    context.mobile_login_page.provide_biometric_authentication()


@when('I swipe to reveal the login form')
def step_swipe_to_login_form(context):
    """Swipe to reveal login form"""
    context.mobile_login_page.swipe_to_reveal_login_form()


@given('I rotate the device to landscape mode')
def step_rotate_to_landscape(context):
    """Rotate device to landscape mode"""
    context.mobile_login_page.rotate_to_landscape()


@then('the mobile home screen should be displayed in landscape mode')
def step_verify_landscape_home_screen(context):
    """Verify home screen is displayed in landscape mode"""
    if not hasattr(context, 'mobile_home_page'):
        from CentralQualityHub.Mobile.pageobjects.mobile_home_page import MobileHomePage
        context.mobile_home_page = MobileHomePage(context.driver)
    
    assert context.mobile_home_page.is_in_landscape_mode(), "Home screen not in landscape mode"

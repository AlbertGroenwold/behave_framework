"""
Mobile Login Page Object for Mobile Testing

This module contains the MobileLoginPage class which provides methods to interact
with mobile login functionality following the Page Object Model pattern.
"""

import sys
import os
from typing import Optional

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from mobile.base_mobile_page import BaseMobilePage


class MobileLoginPage(BaseMobilePage):
    """
    Mobile login page object following Page Object Model pattern.
    
    This class provides methods to interact with mobile login functionality
    across Android and iOS platforms using platform-specific locators.
    
    Attributes:
        Platform-specific locators for login elements on both Android and iOS
    """
    
    # Android Locators - using standard Android resource IDs
    ANDROID_USERNAME_FIELD = (AppiumBy.ID, "com.example.app:id/username")
    ANDROID_PASSWORD_FIELD = (AppiumBy.ID, "com.example.app:id/password")
    ANDROID_LOGIN_BUTTON = (AppiumBy.ID, "com.example.app:id/login_button")
    ANDROID_ERROR_MESSAGE = (AppiumBy.ID, "com.example.app:id/error_message")
    ANDROID_BIOMETRIC_BUTTON = (AppiumBy.ID, "com.example.app:id/biometric_login")
    ANDROID_FORGOT_PASSWORD = (AppiumBy.ID, "com.example.app:id/forgot_password")
    ANDROID_REMEMBER_ME = (AppiumBy.ID, "com.example.app:id/remember_me")
    ANDROID_LOADING_INDICATOR = (AppiumBy.ID, "com.example.app:id/loading")
    
    # Alternative Android locators for different app versions
    ANDROID_USERNAME_ALT = (AppiumBy.XPATH, "//android.widget.EditText[@hint='Username' or @hint='Email']")
    ANDROID_PASSWORD_ALT = (AppiumBy.XPATH, "//android.widget.EditText[@hint='Password']")
    ANDROID_LOGIN_ALT = (AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'Login') or contains(@text, 'Sign In')]")
    
    # iOS Locators - using accessibility identifiers
    IOS_USERNAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "username_field")
    IOS_PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "password_field")
    IOS_LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "login_button")
    IOS_ERROR_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, "error_message")
    IOS_BIOMETRIC_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "biometric_login")
    IOS_FORGOT_PASSWORD = (AppiumBy.ACCESSIBILITY_ID, "forgot_password")
    IOS_REMEMBER_ME = (AppiumBy.ACCESSIBILITY_ID, "remember_me")
    IOS_LOADING_INDICATOR = (AppiumBy.ACCESSIBILITY_ID, "loading")
    
    # Alternative iOS locators
    IOS_USERNAME_ALT = (AppiumBy.XPATH, "//XCUIElementTypeTextField[@placeholder='Username' or @placeholder='Email']")
    IOS_PASSWORD_ALT = (AppiumBy.XPATH, "//XCUIElementTypeSecureTextField[@placeholder='Password']")
    IOS_LOGIN_ALT = (AppiumBy.XPATH, "//XCUIElementTypeButton[@label='Login' or @label='Sign In']")
    
    def __init__(self, driver):
        """
        Initialize the MobileLoginPage with platform-specific locators.
        
        Args:
            driver: Appium WebDriver instance
        """
        super().__init__(driver)
        
        # Set platform-specific locators based on detected platform
        if self.is_android():
            self.username_field = self.ANDROID_USERNAME_FIELD
            self.password_field = self.ANDROID_PASSWORD_FIELD
            self.login_button = self.ANDROID_LOGIN_BUTTON
            self.error_message = self.ANDROID_ERROR_MESSAGE
            self.biometric_button = self.ANDROID_BIOMETRIC_BUTTON
            self.forgot_password = self.ANDROID_FORGOT_PASSWORD
            self.remember_me = self.ANDROID_REMEMBER_ME
            self.loading_indicator = self.ANDROID_LOADING_INDICATOR
            
            # Alternative locators
            self.username_field_alt = self.ANDROID_USERNAME_ALT
            self.password_field_alt = self.ANDROID_PASSWORD_ALT
            self.login_button_alt = self.ANDROID_LOGIN_ALT
            
        else:  # iOS
            self.username_field = self.IOS_USERNAME_FIELD
            self.password_field = self.IOS_PASSWORD_FIELD
            self.login_button = self.IOS_LOGIN_BUTTON
            self.error_message = self.IOS_ERROR_MESSAGE
            self.biometric_button = self.IOS_BIOMETRIC_BUTTON
            self.forgot_password = self.IOS_FORGOT_PASSWORD
            self.remember_me = self.IOS_REMEMBER_ME
            self.loading_indicator = self.IOS_LOADING_INDICATOR
            
            # Alternative locators
            self.username_field_alt = self.IOS_USERNAME_ALT
            self.password_field_alt = self.IOS_PASSWORD_ALT
            self.login_button_alt = self.IOS_LOGIN_ALT
        
        self.logger.info(f"MobileLoginPage initialized for {self.get_platform_name()} platform")
    
    def is_app_launched(self) -> bool:
        """
        Check if mobile app is launched and login screen is visible.
        
        Returns:
            bool: True if app is launched and login screen is visible, False otherwise
        """
        try:
            self.logger.info("Checking if mobile app is launched")
            
            # Try primary locators first
            if self.wait_for_element_to_be_visible(self.username_field, timeout=10):
                self.logger.info("App launched successfully - primary locators found")
                return True
            
            # Try alternative locators
            if self.wait_for_element_to_be_visible(self.username_field_alt, timeout=5):
                self.logger.info("App launched successfully - alternative locators found")
                return True
            
            self.logger.warning("App does not appear to be launched - login elements not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if app is launched: {e}")
            return False
    
    def wait_for_login_screen(self, timeout: int = 15) -> None:
        """
        Wait for the login screen to fully load.
        
        Args:
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 15.
            
        Raises:
            TimeoutException: If login screen doesn't load within timeout
        """
        self.logger.info(f"Waiting for login screen to load (timeout: {timeout}s)")
        
        try:
            # Wait for essential login elements
            self.wait_for_element_to_be_visible(self.username_field, timeout)
            self.wait_for_element_to_be_visible(self.password_field, timeout)
            
            # Wait for loading to complete if loading indicator is present
            try:
                self.wait_for_element_invisible(self.loading_indicator, timeout=5)
            except Exception:
                pass  # Loading indicator may not be present
            
            self.logger.info("Login screen loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Login screen failed to load: {e}")
            raise
            return True
        except:
            return False
    
    def enter_username(self, username):
        """
        Enter username in the username field
        
        Args:
            username (str): Username to enter
        """
        self.wait_for_element_to_be_visible(self.username_field)
        element = self.find_element(self.username_field)
        element.clear()
        element.send_keys(username)
        self.logger.info(f"Entered username: {username}")
    
    def enter_password(self, password):
        """
        Enter password in the password field
        
        Args:
            password (str): Password to enter
        """
        self.wait_for_element_to_be_visible(self.password_field)
        element = self.find_element(self.password_field)
        element.clear()
        element.send_keys(password)
        self.logger.info("Entered password")
    
    def tap_login_button(self):
        """Tap the login button"""
        self.wait_for_element_to_be_clickable(self.login_button)
        self.tap_element(self.login_button)
        self.logger.info("Tapped login button")
    
    def is_error_message_displayed(self):
        """
        Check if error message is displayed
        
        Returns:
            bool: True if error message is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.error_message)
        except:
            return False
    
    def get_error_message_text(self):
        """
        Get the text of the error message
        
        Returns:
            str: Error message text
        """
        if self.is_error_message_displayed():
            return self.get_element_text(self.error_message)
        return ""
    
    def is_login_screen_displayed(self):
        """Check if login screen is displayed"""
        return self.is_element_displayed(self.username_field) and self.is_element_displayed(self.password_field)
    
    def tap_biometric_login_button(self):
        """Tap biometric login button"""
        self.wait_for_element_to_be_clickable(self.biometric_button)
        self.tap_element(self.biometric_button)
        self.logger.info("Tapped biometric login button")
    
    def ensure_biometric_enabled(self):
        """Ensure biometric authentication is enabled"""
        # This would typically check device settings or app settings
        if self.is_element_displayed(self.biometric_button):
            self.logger.info("Biometric authentication is available")
        else:
            self.logger.warning("Biometric authentication is not available")
    
    def provide_biometric_authentication(self):
        """Provide biometric authentication (simulated)"""
        # In real scenario, this would interact with device biometric
        # For testing, we might simulate or use test-specific methods
        import time
        time.sleep(2)  # Simulate biometric authentication time
        self.logger.info("Biometric authentication provided")
    
    def swipe_to_reveal_login_form(self):
        """Swipe to reveal login form"""
        screen_size = self.get_screen_size()
        start_x = screen_size['width'] // 2
        start_y = screen_size['height'] * 0.8
        end_x = start_x
        end_y = screen_size['height'] * 0.2
        
        self.swipe(start_x, start_y, end_x, end_y)
        self.logger.info("Swiped to reveal login form")
    
    def rotate_to_landscape(self):
        """Rotate device to landscape mode"""
        self.set_orientation('LANDSCAPE')
        self.logger.info("Rotated device to landscape mode")
    
    def mobile_login(self, username, password):
        """
        Perform mobile login with username and password
        
        Args:
            username (str): Username to enter
            password (str): Password to enter
        """
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login_button()
        self.logger.info(f"Performed mobile login for user: {username}")
    
    def wait_for_login_screen_to_load(self, timeout=15):
        """
        Wait for login screen to fully load
        
        Args:
            timeout (int): Maximum time to wait in seconds
        """
        self.wait_for_element_to_be_visible(self.username_field, timeout)
        self.wait_for_element_to_be_visible(self.password_field, timeout)
        self.wait_for_element_to_be_clickable(self.login_button, timeout)
        self.logger.info("Login screen loaded successfully")

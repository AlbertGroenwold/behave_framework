"""
Login Page Object for Web Testing

This module contains the LoginPage class which provides methods to interact
with the login page elements following the Page Object Model pattern.
"""

import sys
import os
from typing import Optional

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from web_selenium.base_page import BasePage


class LoginPage(BasePage):
    """
    Login page object following Page Object Model pattern.
    
    This class provides methods to interact with the login page elements
    and perform login-related operations.
    
    Attributes:
        USERNAME_FIELD: Locator for username input field
        PASSWORD_FIELD: Locator for password input field  
        LOGIN_BUTTON: Locator for login submit button
        ERROR_MESSAGE: Locator for error message display
        FORGOT_PASSWORD_LINK: Locator for forgot password link
        REMEMBER_ME_CHECKBOX: Locator for remember me checkbox
    """
    
    # Page locators - using explicit locator strategy for maintainability
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot Password?")
    REMEMBER_ME_CHECKBOX = (By.ID, "remember-me")
    
    # Alternative locators for different login page implementations
    LOGIN_BUTTON_ALT = (By.XPATH, "//button[@type='submit']")
    ERROR_MESSAGE_ALT = (By.CSS_SELECTOR, ".alert-danger, .error")
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the LoginPage with a WebDriver instance.
        
        Args:
            driver (WebDriver): Selenium WebDriver instance
        """
        super().__init__(driver)
        self.page_url = f"{self.get_base_url()}/login"
        self.page_title = "Login"
    
    def navigate_to_login_page(self) -> None:
        """
        Navigate to the login page and verify it loaded correctly.
        
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        self.logger.info(f"Navigating to login page: {self.page_url}")
        self.navigate_to(self.page_url)
        self.wait_for_page_load()
    
    def wait_for_page_load(self) -> None:
        """Wait for the login page to fully load by checking for key elements."""
        self.wait_for_element_visible(self.USERNAME_FIELD)
        self.wait_for_element_visible(self.PASSWORD_FIELD)
        self.logger.info("Login page loaded successfully")
    
    def enter_username(self, username: str) -> None:
        """
        Enter username in the username field.
        
        Args:
            username (str): Username to enter
            
        Raises:
            TimeoutException: If username field is not found
        """
        self.logger.info(f"Entering username: {username}")
        self.clear_and_type(self.USERNAME_FIELD, username)
    
    def enter_password(self, password: str) -> None:
        """
        Enter password in the password field.
        
        Args:
            password (str): Password to enter
            
        Raises:
            TimeoutException: If password field is not found
        """
        self.logger.info("Entering password")
        self.clear_and_type(self.PASSWORD_FIELD, password)
    
    def click_login_button(self) -> None:
        """
        Click the login button to submit the form.
        
        Raises:
            TimeoutException: If login button is not found or clickable
        """
        self.logger.info("Clicking login button")
        self.click_element(self.LOGIN_BUTTON)
    
    def check_remember_me(self) -> None:
        """
        Check the remember me checkbox if it's not already checked.
        
        Raises:
            TimeoutException: If remember me checkbox is not found
        """
        self.logger.info("Checking remember me checkbox")
        checkbox = self.find_element(self.REMEMBER_ME_CHECKBOX)
        if not checkbox.is_selected():
            self.click_element(self.REMEMBER_ME_CHECKBOX)
    
    def uncheck_remember_me(self) -> None:
        """
        Uncheck the remember me checkbox if it's currently checked.
        
        Raises:
            TimeoutException: If remember me checkbox is not found
        """
        self.logger.info("Unchecking remember me checkbox")
        checkbox = self.find_element(self.REMEMBER_ME_CHECKBOX)
        if checkbox.is_selected():
            self.click_element(self.REMEMBER_ME_CHECKBOX)
    
    def is_remember_me_checked(self) -> bool:
        """
        Check if remember me checkbox is selected.
        
        Returns:
            bool: True if checkbox is selected, False otherwise
            
        Raises:
            TimeoutException: If remember me checkbox is not found
        """
        checkbox = self.find_element(self.REMEMBER_ME_CHECKBOX)
        return checkbox.is_selected()
    
    def login(self, username: str, password: str, remember_me: bool = False) -> None:
        """
        Perform complete login operation with username and password.
        
        Args:
            username (str): Username to enter
            password (str): Password to enter
            remember_me (bool, optional): Whether to check remember me checkbox. Defaults to False.
            
        Raises:
            TimeoutException: If any login elements are not found
        """
        self.logger.info(f"Performing login for user: {username}")
        
        # Clear any existing values first
        self.clear_username_field()
        self.clear_password_field()
        
        # Enter credentials
        self.enter_username(username)
        self.enter_password(password)
        
        # Handle remember me option
        if remember_me:
            self.check_remember_me()
        else:
            self.uncheck_remember_me()
        
        # Submit the form
        self.click_login_button()
        self.logger.info("Login form submitted")
    
    def is_error_message_displayed(self) -> bool:
        """
        Check if error message is displayed on the page.
        
        Returns:
            bool: True if error message is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.ERROR_MESSAGE) or \
                   self.is_element_displayed(self.ERROR_MESSAGE_ALT)
        except Exception:
            return False
    
    def get_error_message_text(self) -> str:
        """
        Get the text of the error message if displayed.
        
        Returns:
            str: Error message text or empty string if no error
        """
        try:
            if self.is_element_displayed(self.ERROR_MESSAGE):
                return self.get_element_text(self.ERROR_MESSAGE)
            elif self.is_element_displayed(self.ERROR_MESSAGE_ALT):
                return self.get_element_text(self.ERROR_MESSAGE_ALT)
        except Exception as e:
            self.logger.warning(f"Could not get error message text: {e}")
        return ""
        return ""
    
    def click_forgot_password_link(self) -> None:
        """
        Click the forgot password link to navigate to password reset page.
        
        Raises:
            TimeoutException: If forgot password link is not found
        """
        self.logger.info("Clicking forgot password link")
        self.click_element(self.FORGOT_PASSWORD_LINK)
    
    def is_login_button_enabled(self) -> bool:
        """
        Check if login button is enabled and clickable.
        
        Returns:
            bool: True if login button is enabled, False otherwise
            
        Raises:
            TimeoutException: If login button is not found
        """
        button = self.find_element(self.LOGIN_BUTTON)
        return button.is_enabled()
    
    def clear_username_field(self) -> None:
        """
        Clear the username field of any existing text.
        
        Raises:
            TimeoutException: If username field is not found
        """
        self.logger.debug("Clearing username field")
        self.clear_text(self.USERNAME_FIELD)
    
    def clear_password_field(self) -> None:
        """
        Clear the password field of any existing text.
        
        Raises:
            TimeoutException: If password field is not found
        """
        self.logger.debug("Clearing password field")
        self.clear_text(self.PASSWORD_FIELD)
    
    def get_username_field_value(self) -> str:
        """
        Get the current value of username field.
        
        Returns:
            str: Current username field value
            
        Raises:
            TimeoutException: If username field is not found
        """
        element = self.find_element(self.USERNAME_FIELD)
        return element.get_attribute('value') or ""
    
    def get_password_field_value(self) -> str:
        """
        Get the current value of password field.
        
        Returns:
            str: Current password field value (Note: may be masked for security)
            
        Raises:
            TimeoutException: If password field is not found
        """
        element = self.find_element(self.PASSWORD_FIELD)
        return element.get_attribute('value') or ""
    
    def is_username_field_displayed(self) -> bool:
        """
        Check if username field is displayed and visible.
        
        Returns:
            bool: True if username field is displayed, False otherwise
        """
        try:
            return self.is_element_displayed(self.USERNAME_FIELD)
        except Exception:
            return False
    
    def is_password_field_displayed(self) -> bool:
        """
        Check if password field is displayed and visible.
        
        Returns:
            bool: True if password field is displayed, False otherwise
        """
        try:
            return self.is_element_displayed(self.PASSWORD_FIELD)
        except Exception:
            return False
    
    def is_login_button_displayed(self) -> bool:
        """
        Check if login button is displayed and visible.
        
        Returns:
            bool: True if login button is displayed, False otherwise
        """
        try:
            return self.is_element_displayed(self.LOGIN_BUTTON) or \
                   self.is_element_displayed(self.LOGIN_BUTTON_ALT)
        except Exception:
            return False
    
    def wait_for_login_page_to_load(self, timeout: int = 10) -> None:
        """
        Wait for login page to fully load with all required elements.
        
        Args:
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 10.
            
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        self.logger.info(f"Waiting for login page to load (timeout: {timeout}s)")
        self.wait_for_element_to_be_visible(self.USERNAME_FIELD, timeout)
        self.wait_for_element_to_be_visible(self.PASSWORD_FIELD, timeout)
        self.wait_for_element_to_be_clickable(self.LOGIN_BUTTON, timeout)
        self.logger.info("Login page loaded successfully with all elements")
    
    def verify_login_page_elements(self) -> bool:
        """
        Verify all essential login page elements are present.
        
        Returns:
            bool: True if all essential elements are present, False otherwise
        """
        try:
            elements_present = (
                self.is_username_field_displayed() and
                self.is_password_field_displayed() and
                self.is_login_button_displayed()
            )
            
            if elements_present:
                self.logger.info("All essential login page elements are present")
            else:
                self.logger.warning("Some essential login page elements are missing")
                
            return elements_present
            
        except Exception as e:
            self.logger.error(f"Error verifying login page elements: {e}")
            return False
    
    def perform_quick_login(self, username: str, password: str) -> None:
        """
        Perform a quick login without additional options.
        
        Args:
            username (str): Username to enter
            password (str): Password to enter
            
        Raises:
            TimeoutException: If any login elements are not found
        """
        self.logger.info(f"Performing quick login for user: {username}")
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

    def get_page_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            str: Current page title
        """
        return self.driver.title
    
    def is_on_login_page(self) -> bool:
        """
        Verify if currently on the login page by checking URL and elements.
        
        Returns:
            bool: True if on login page, False otherwise
        """
        try:
            current_url = self.driver.current_url
            is_login_url = "login" in current_url.lower()
            has_login_elements = self.verify_login_page_elements()
            
            return is_login_url and has_login_elements
        except Exception as e:
            self.logger.error(f"Error checking if on login page: {e}")
            return False

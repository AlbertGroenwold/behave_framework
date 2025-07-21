"""
Login Page Object for Playwright Web Testing

This module contains the LoginPage class which provides methods to interact
with the login page elements using Playwright automation.
"""

import sys
import os
from typing import Optional
import time

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from playwright.sync_api import Page, Locator, expect
from web_playwright.base_page import BasePage
from web_playwright.playwright_manager import PlaywrightManager


class LoginPage(BasePage):
    """
    Login page object for Playwright automation following Page Object Model pattern.
    
    This class provides methods to interact with the login page elements
    and perform login-related operations using Playwright.
    
    Attributes:
        Various selectors for login page elements
    """
    
    # Page selectors - using CSS selectors optimized for Playwright
    USERNAME_FIELD = "#username"
    PASSWORD_FIELD = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = ".error-message"
    FORGOT_PASSWORD_LINK = "a[href*='forgot-password']"
    REMEMBER_ME_CHECKBOX = "#remember-me"
    
    # Alternative selectors for different implementations
    LOGIN_BUTTON_ALT = "button[type='submit']"
    ERROR_MESSAGE_ALT = ".alert-danger, .error, [role='alert']"
    
    # Page title and URL patterns
    PAGE_TITLE = "Login"
    PAGE_URL_PATTERN = "/login"
    
    def __init__(self, playwright_manager: PlaywrightManager):
        """
        Initialize the LoginPage with Playwright manager.
        
        Args:
            playwright_manager (PlaywrightManager): Playwright manager instance
        """
        super().__init__(playwright_manager)
        self.page_url = "https://example.com/login"  # Default URL, can be overridden
    
    def navigate_to_login_page(self, url: Optional[str] = None):
        """
        Navigate to the login page.
        
        Args:
            url (Optional[str]): Custom URL to navigate to. If None, uses default.
        """
        try:
            target_url = url or self.page_url
            self.navigate_to(target_url)
            self.wait_for_page_load()
            self.logger.info(f"Navigated to login page: {target_url}")
        except Exception as e:
            self.logger.error(f"Failed to navigate to login page: {e}")
            raise
    
    def enter_username(self, username: str):
        """
        Enter username in the username field.
        
        Args:
            username (str): Username to enter
        """
        try:
            self.type_text(self.USERNAME_FIELD, username)
            self.logger.info(f"Entered username: {username}")
        except Exception as e:
            self.logger.error(f"Failed to enter username: {e}")
            raise
    
    def enter_password(self, password: str):
        """
        Enter password in the password field.
        
        Args:
            password (str): Password to enter
        """
        try:
            self.type_text(self.PASSWORD_FIELD, password)
            self.logger.info("Entered password")
        except Exception as e:
            self.logger.error(f"Failed to enter password: {e}")
            raise
    
    def click_login_button(self):
        """Click the login button."""
        try:
            self.click_element(self.LOGIN_BUTTON)
            self.logger.info("Clicked login button")
        except Exception as e:
            self.logger.error(f"Failed to click login button: {e}")
            raise
    
    def check_remember_me(self):
        """Check the remember me checkbox."""
        try:
            self.check_checkbox(self.REMEMBER_ME_CHECKBOX)
            self.logger.info("Checked remember me checkbox")
        except Exception as e:
            self.logger.error(f"Failed to check remember me checkbox: {e}")
            raise
    
    def uncheck_remember_me(self):
        """Uncheck the remember me checkbox."""
        try:
            self.uncheck_checkbox(self.REMEMBER_ME_CHECKBOX)
            self.logger.info("Unchecked remember me checkbox")
        except Exception as e:
            self.logger.error(f"Failed to uncheck remember me checkbox: {e}")
            raise
    
    def is_remember_me_checked(self) -> bool:
        """
        Check if remember me checkbox is checked.
        
        Returns:
            bool: True if checked, False otherwise
        """
        try:
            return self.is_checked(self.REMEMBER_ME_CHECKBOX)
        except Exception as e:
            self.logger.error(f"Failed to check remember me status: {e}")
            return False
    
    def click_forgot_password_link(self):
        """Click the forgot password link."""
        try:
            self.click_element(self.FORGOT_PASSWORD_LINK)
            self.logger.info("Clicked forgot password link")
        except Exception as e:
            self.logger.error(f"Failed to click forgot password link: {e}")
            raise
    
    def get_error_message(self) -> str:
        """
        Get the error message text.
        
        Returns:
            str: Error message text
        """
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except Exception as e:
            self.logger.error(f"Failed to get error message: {e}")
            return ""
    
    def is_error_message_displayed(self) -> bool:
        """
        Check if error message is displayed.
        
        Returns:
            bool: True if error message is visible, False otherwise
        """
        try:
            return self.is_visible(self.ERROR_MESSAGE)
        except Exception as e:
            self.logger.error(f"Failed to check error message visibility: {e}")
            return False
    
    def wait_for_error_message(self, timeout: int = 10000) -> bool:
        """
        Wait for error message to appear.
        
        Args:
            timeout (int): Timeout in milliseconds
            
        Returns:
            bool: True if error message appeared, False otherwise
        """
        try:
            self.wait_for_element(self.ERROR_MESSAGE, timeout=timeout)
            return True
        except Exception as e:
            self.logger.warning(f"Error message did not appear within timeout: {e}")
            return False
    
    def perform_login(self, username: str, password: str, remember_me: bool = False):
        """
        Perform complete login operation.
        
        Args:
            username (str): Username
            password (str): Password
            remember_me (bool): Whether to check remember me checkbox
        """
        try:
            self.enter_username(username)
            self.enter_password(password)
            
            if remember_me:
                self.check_remember_me()
                
            self.click_login_button()
            self.logger.info(f"Performed login for user: {username}")
        except Exception as e:
            self.logger.error(f"Failed to perform login: {e}")
            raise
    
    def verify_login_page_elements(self) -> bool:
        """
        Verify that all expected login page elements are present.
        
        Returns:
            bool: True if all elements are present, False otherwise
        """
        try:
            elements_to_check = [
                self.USERNAME_FIELD,
                self.PASSWORD_FIELD,
                self.LOGIN_BUTTON
            ]
            
            for element in elements_to_check:
                if not self.is_visible(element):
                    self.logger.error(f"Element not visible: {element}")
                    return False
            
            self.logger.info("All login page elements are present")
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify login page elements: {e}")
            return False
    
    def wait_for_page_load(self, timeout: int = 30000):
        """
        Wait for the login page to fully load.
        
        Args:
            timeout (int): Timeout in milliseconds
        """
        try:
            # Wait for the login button to be visible as an indicator of page load
            self.wait_for_element(self.LOGIN_BUTTON, timeout=timeout)
            self.logger.info("Login page loaded successfully")
        except Exception as e:
            self.logger.error(f"Login page failed to load: {e}")
            raise
    
    def clear_form(self):
        """Clear all form fields."""
        try:
            self.clear_field(self.USERNAME_FIELD)
            self.clear_field(self.PASSWORD_FIELD)
            
            if self.is_remember_me_checked():
                self.uncheck_remember_me()
                
            self.logger.info("Cleared login form")
        except Exception as e:
            self.logger.error(f"Failed to clear login form: {e}")
            raise
    
    def get_page_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            str: Page title
        """
        try:
            return self.page.title()
        except Exception as e:
            self.logger.error(f"Failed to get page title: {e}")
            return ""
    
    def is_on_login_page(self) -> bool:
        """
        Check if currently on the login page.
        
        Returns:
            bool: True if on login page, False otherwise
        """
        try:
            current_url = self.get_current_url()
            title = self.get_page_title()
            
            url_check = self.PAGE_URL_PATTERN in current_url
            title_check = self.PAGE_TITLE.lower() in title.lower()
            elements_check = self.verify_login_page_elements()
            
            return url_check or title_check or elements_check
        except Exception as e:
            self.logger.error(f"Failed to verify login page: {e}")
            return False

"""
Home Page Object for Web Testing

This module contains the HomePage class which provides methods to interact
with the home page elements following the Page Object Model pattern.
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


class HomePage(BasePage):
    """
    Home page object following Page Object Model pattern.
    
    This class provides methods to interact with the home page elements
    and perform home page-related operations after successful login.
    
    Attributes:
        WELCOME_MESSAGE: Locator for welcome message display
        USER_PROFILE: Locator for user profile section
        LOGOUT_BUTTON: Locator for logout button
        NAVIGATION_MENU: Locator for main navigation menu
        DASHBOARD_HEADER: Locator for dashboard header
        USER_DROPDOWN: Locator for user dropdown menu
        SETTINGS_LINK: Locator for settings navigation
    """
    
    # Page locators - using explicit locator strategy for maintainability
    WELCOME_MESSAGE = (By.CLASS_NAME, "welcome-message")
    USER_PROFILE = (By.ID, "user-profile")
    LOGOUT_BUTTON = (By.ID, "logout-button")
    NAVIGATION_MENU = (By.CLASS_NAME, "navigation-menu")
    DASHBOARD_HEADER = (By.TAG_NAME, "h1")
    
    # Additional common locators
    USER_DROPDOWN = (By.CLASS_NAME, "user-dropdown")
    SETTINGS_LINK = (By.LINK_TEXT, "Settings")
    PROFILE_LINK = (By.LINK_TEXT, "Profile")
    
    # Alternative locators for different implementations
    LOGOUT_BUTTON_ALT = (By.XPATH, "//button[contains(text(), 'Logout')]")
    WELCOME_MESSAGE_ALT = (By.CSS_SELECTOR, ".welcome, .greeting")
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the HomePage with a WebDriver instance.
        
        Args:
            driver (WebDriver): Selenium WebDriver instance
        """
        super().__init__(driver)
        self.page_url = f"{self.get_base_url()}/home"
        self.page_title = "Home - Dashboard"
    
    def navigate_to_home_page(self) -> None:
        """
        Navigate to the home page and verify it loaded correctly.
        
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        self.logger.info(f"Navigating to home page: {self.page_url}")
        self.navigate_to(self.page_url)
        self.wait_for_page_load()
    
    def wait_for_page_load(self) -> None:
        """Wait for the home page to fully load by checking for key elements."""
        try:
            self.wait_for_element_visible(self.DASHBOARD_HEADER)
            self.logger.info("Home page loaded successfully")
        except Exception as e:
            self.logger.warning(f"Home page load verification failed: {e}")
    
    def is_welcome_message_displayed(self) -> bool:
        """
        Check if welcome message is displayed on the page.
        
        Returns:
            bool: True if welcome message is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.WELCOME_MESSAGE) or \
                   self.is_element_displayed(self.WELCOME_MESSAGE_ALT)
        except Exception:
            return False
    
    def get_welcome_message_text(self) -> str:
        """
        Get the text of the welcome message if displayed.
        
        Returns:
            str: Welcome message text or empty string if not found
        """
        try:
            if self.is_element_displayed(self.WELCOME_MESSAGE):
                return self.get_element_text(self.WELCOME_MESSAGE)
            elif self.is_element_displayed(self.WELCOME_MESSAGE_ALT):
                return self.get_element_text(self.WELCOME_MESSAGE_ALT)
        except Exception as e:
            self.logger.warning(f"Could not get welcome message text: {e}")
        return ""
    
    def click_logout_button(self) -> None:
        """
        Click the logout button to sign out from the application.
        
        Raises:
            TimeoutException: If logout button is not found or clickable
        """
        self.logger.info("Clicking logout button")
        try:
            if self.is_element_displayed(self.LOGOUT_BUTTON):
                self.click_element(self.LOGOUT_BUTTON)
            elif self.is_element_displayed(self.LOGOUT_BUTTON_ALT):
                self.click_element(self.LOGOUT_BUTTON_ALT)
            else:
                raise Exception("Logout button not found")
        except Exception as e:
            self.logger.error(f"Failed to click logout button: {e}")
            raise
    
    def is_logout_button_displayed(self) -> bool:
        """
        Check if logout button is displayed and accessible.
        
        Returns:
            bool: True if logout button is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.LOGOUT_BUTTON) or \
                   self.is_element_displayed(self.LOGOUT_BUTTON_ALT)
        except Exception:
            return False
    
    def is_user_profile_displayed(self) -> bool:
        """
        Check if user profile section is displayed.
        
        Returns:
            bool: True if user profile is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.USER_PROFILE)
        except Exception:
            return False
    
    def click_user_profile(self) -> None:
        """
        Click on the user profile section.
        
        Raises:
            TimeoutException: If user profile is not found or clickable
        """
        self.logger.info("Clicking user profile")
        self.click_element(self.USER_PROFILE)
    
    def is_navigation_menu_displayed(self) -> bool:
        """
        Check if navigation menu is displayed.
        
        Returns:
            bool: True if navigation menu is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.NAVIGATION_MENU)
        except Exception:
            return False
    
    def get_dashboard_header_text(self) -> str:
        """
        Get the text of the dashboard header.
        
        Returns:
            str: Dashboard header text or empty string if not found
        """
        try:
            return self.get_element_text(self.DASHBOARD_HEADER)
        except Exception as e:
            self.logger.warning(f"Could not get dashboard header text: {e}")
            return ""
    
    def get_page_text(self) -> str:
        """
        Get all text content from the page body.
        
        Returns:
            str: All visible text content from the page
        """
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception as e:
            self.logger.warning(f"Could not get page text: {e}")
            return ""
    
    def wait_for_home_page_to_load(self, timeout: int = 10) -> None:
        """
        Wait for home page to fully load with all key elements.
        
        Args:
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 10.
            
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        self.logger.info(f"Waiting for home page to load (timeout: {timeout}s)")
        try:
            # Wait for essential elements to be visible
            self.wait_for_element_to_be_visible(self.DASHBOARD_HEADER, timeout)
            
            # Optionally wait for welcome message if it exists
            if self.is_welcome_message_displayed():
                self.wait_for_element_to_be_visible(self.WELCOME_MESSAGE, timeout)
                
            self.logger.info("Home page loaded successfully")
        except Exception as e:
            self.logger.error(f"Home page failed to load: {e}")
            raise
    
    def verify_home_page_elements(self) -> bool:
        """
        Verify all essential home page elements are present.
        
        Returns:
            bool: True if all essential elements are present, False otherwise
        """
        try:
            # Check for essential elements
            has_header = bool(self.get_dashboard_header_text())
            has_logout = self.is_logout_button_displayed()
            
            elements_present = has_header and has_logout
            
            if elements_present:
                self.logger.info("All essential home page elements are present")
            else:
                self.logger.warning("Some essential home page elements are missing")
                
            return elements_present
            
        except Exception as e:
            self.logger.error(f"Error verifying home page elements: {e}")
            return False
    
    def is_on_home_page(self) -> bool:
        """
        Verify if currently on the home page by checking URL and elements.
        
        Returns:
            bool: True if on home page, False otherwise
        """
        try:
            current_url = self.driver.current_url
            is_home_url = "home" in current_url.lower() or "dashboard" in current_url.lower()
            has_home_elements = self.verify_home_page_elements()
            
            return is_home_url and has_home_elements
        except Exception as e:
            self.logger.error(f"Error checking if on home page: {e}")
            return False
    
    def navigate_to_settings(self) -> None:
        """
        Navigate to settings page if the link is available.
        
        Raises:
            TimeoutException: If settings link is not found
        """
        self.logger.info("Navigating to settings")
        self.click_element(self.SETTINGS_LINK)
    
    def navigate_to_profile(self) -> None:
        """
        Navigate to profile page if the link is available.
        
        Raises:
            TimeoutException: If profile link is not found
        """
        self.logger.info("Navigating to profile")
        self.click_element(self.PROFILE_LINK)



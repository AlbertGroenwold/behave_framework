"""
Home Page Object for Playwright Web Testing

This module contains the HomePage class which provides methods to interact
with the home page elements using Playwright automation.
"""

import sys
import os
from typing import Optional, List

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from playwright.sync_api import Page, Locator, expect
from web_playwright.base_page import BasePage
from web_playwright.playwright_manager import PlaywrightManager


class HomePage(BasePage):
    """
    Home page object for Playwright automation following Page Object Model pattern.
    
    This class provides methods to interact with the home page elements
    and perform home page-related operations using Playwright.
    """
    
    # Page selectors
    WELCOME_MESSAGE = ".welcome-message, #welcome-message"
    USER_PROFILE_DROPDOWN = ".user-profile-dropdown, #user-profile"
    LOGOUT_BUTTON = "a[href*='logout'], button:has-text('Logout')"
    NAVIGATION_MENU = ".navigation-menu, #nav-menu"
    MAIN_CONTENT = ".main-content, #main-content"
    
    # Navigation links
    USER_MANAGEMENT_LINK = "a[href*='user-management'], a:has-text('User Management')"
    DASHBOARD_LINK = "a[href*='dashboard'], a:has-text('Dashboard')"
    SETTINGS_LINK = "a[href*='settings'], a:has-text('Settings')"
    
    # Page indicators
    PAGE_TITLE = "Home"
    PAGE_URL_PATTERN = "/home"
    
    def __init__(self, playwright_manager: PlaywrightManager):
        """
        Initialize the HomePage with Playwright manager.
        
        Args:
            playwright_manager (PlaywrightManager): Playwright manager instance
        """
        super().__init__(playwright_manager)
        self.page_url = "https://example.com/home"  # Default URL, can be overridden
    
    def verify_welcome_message(self) -> bool:
        """
        Verify that the welcome message is displayed.
        
        Returns:
            bool: True if welcome message is visible, False otherwise
        """
        try:
            return self.is_visible(self.WELCOME_MESSAGE)
        except Exception as e:
            self.logger.error(f"Failed to verify welcome message: {e}")
            return False
    
    def get_welcome_message_text(self) -> str:
        """
        Get the welcome message text.
        
        Returns:
            str: Welcome message text
        """
        try:
            return self.get_text(self.WELCOME_MESSAGE)
        except Exception as e:
            self.logger.error(f"Failed to get welcome message text: {e}")
            return ""
    
    def click_user_profile_dropdown(self):
        """Click the user profile dropdown."""
        try:
            self.click_element(self.USER_PROFILE_DROPDOWN)
            self.logger.info("Clicked user profile dropdown")
        except Exception as e:
            self.logger.error(f"Failed to click user profile dropdown: {e}")
            raise
    
    def click_logout_button(self):
        """Click the logout button."""
        try:
            self.click_element(self.LOGOUT_BUTTON)
            self.logger.info("Clicked logout button")
        except Exception as e:
            self.logger.error(f"Failed to click logout button: {e}")
            raise
    
    def logout(self):
        """Perform complete logout operation."""
        try:
            self.click_user_profile_dropdown()
            self.wait_for_element(self.LOGOUT_BUTTON)
            self.click_logout_button()
            self.logger.info("Performed logout")
        except Exception as e:
            self.logger.error(f"Failed to perform logout: {e}")
            raise
    
    def navigate_to_user_management(self):
        """Navigate to user management page."""
        try:
            self.click_element(self.USER_MANAGEMENT_LINK)
            self.logger.info("Navigated to user management")
        except Exception as e:
            self.logger.error(f"Failed to navigate to user management: {e}")
            raise
    
    def navigate_to_dashboard(self):
        """Navigate to dashboard page."""
        try:
            self.click_element(self.DASHBOARD_LINK)
            self.logger.info("Navigated to dashboard")
        except Exception as e:
            self.logger.error(f"Failed to navigate to dashboard: {e}")
            raise
    
    def navigate_to_settings(self):
        """Navigate to settings page."""
        try:
            self.click_element(self.SETTINGS_LINK)
            self.logger.info("Navigated to settings")
        except Exception as e:
            self.logger.error(f"Failed to navigate to settings: {e}")
            raise
    
    def verify_home_page_elements(self) -> bool:
        """
        Verify that all expected home page elements are present.
        
        Returns:
            bool: True if all elements are present, False otherwise
        """
        try:
            elements_to_check = [
                self.NAVIGATION_MENU,
                self.MAIN_CONTENT
            ]
            
            for element in elements_to_check:
                if not self.is_visible(element):
                    self.logger.error(f"Element not visible: {element}")
                    return False
            
            self.logger.info("All home page elements are present")
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify home page elements: {e}")
            return False
    
    def wait_for_page_load(self, timeout: int = 30000):
        """
        Wait for the home page to fully load.
        
        Args:
            timeout (int): Timeout in milliseconds
        """
        try:
            # Wait for the main content to be visible as an indicator of page load
            self.wait_for_element(self.MAIN_CONTENT, timeout=timeout)
            self.logger.info("Home page loaded successfully")
        except Exception as e:
            self.logger.error(f"Home page failed to load: {e}")
            raise
    
    def is_on_home_page(self) -> bool:
        """
        Check if currently on the home page.
        
        Returns:
            bool: True if on home page, False otherwise
        """
        try:
            current_url = self.get_current_url()
            title = self.page.title()
            
            url_check = self.PAGE_URL_PATTERN in current_url
            title_check = self.PAGE_TITLE.lower() in title.lower()
            elements_check = self.verify_home_page_elements()
            
            return url_check or title_check or elements_check
        except Exception as e:
            self.logger.error(f"Failed to verify home page: {e}")
            return False
    
    def get_navigation_links(self) -> List[str]:
        """
        Get all navigation links on the page.
        
        Returns:
            List[str]: List of navigation link texts
        """
        try:
            nav_links = self.page.locator(f"{self.NAVIGATION_MENU} a")
            return [link.text_content() for link in nav_links.all()]
        except Exception as e:
            self.logger.error(f"Failed to get navigation links: {e}")
            return []
    
    def verify_user_access_level(self, expected_links: List[str]) -> bool:
        """
        Verify user access level based on available navigation links.
        
        Args:
            expected_links (List[str]): Expected navigation links for user role
            
        Returns:
            bool: True if user has expected access level, False otherwise
        """
        try:
            available_links = self.get_navigation_links()
            
            for expected_link in expected_links:
                if expected_link not in available_links:
                    self.logger.error(f"Expected link not found: {expected_link}")
                    return False
            
            self.logger.info("User access level verified successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify user access level: {e}")
            return False

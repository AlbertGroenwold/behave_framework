"""
User Management Page Object for Playwright Web Testing

This module contains the UserManagementPage class which provides methods to interact
with the user management page elements using Playwright automation.
"""

import sys
import os
from typing import Optional, List, Dict, Any

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from playwright.sync_api import Page, Locator, expect
from web_playwright.base_page import BasePage
from web_playwright.playwright_manager import PlaywrightManager


class UserManagementPage(BasePage):
    """
    User Management page object for Playwright automation following Page Object Model pattern.
    
    This class provides methods to interact with the user management page elements
    and perform user management operations using Playwright.
    """
    
    # Page selectors
    ADD_USER_BUTTON = "button:has-text('Add New User'), #add-user-btn"
    USER_TABLE = ".user-table, #user-table"
    SEARCH_FIELD = "#search-users, .search-field"
    SEARCH_BUTTON = "button:has-text('Search'), .search-btn"
    ROLE_FILTER_DROPDOWN = "#role-filter, .role-filter"
    
    # User form selectors
    USER_FORM = ".user-form, #user-form"
    USERNAME_INPUT = "#username, input[name='username']"
    EMAIL_INPUT = "#email, input[name='email']"
    FIRST_NAME_INPUT = "#first_name, input[name='first_name']"
    LAST_NAME_INPUT = "#last_name, input[name='last_name']"
    ROLE_SELECT = "#role, select[name='role']"
    CREATE_USER_BUTTON = "button:has-text('Create User'), #create-user-btn"
    SAVE_CHANGES_BUTTON = "button:has-text('Save Changes'), #save-changes-btn"
    CANCEL_BUTTON = "button:has-text('Cancel'), .cancel-btn"
    
    # User table selectors
    USER_ROW = ".user-row, tbody tr"
    EDIT_BUTTON = "button:has-text('Edit'), .edit-btn"
    DELETE_BUTTON = "button:has-text('Delete'), .delete-btn"
    
    # Pagination selectors
    PAGINATION_CONTAINER = ".pagination, #pagination"
    NEXT_PAGE_BUTTON = "button:has-text('Next'), .next-page"
    PREVIOUS_PAGE_BUTTON = "button:has-text('Previous'), .previous-page"
    PAGE_NUMBER = ".page-number, .current-page"
    
    # Modal/Dialog selectors
    CONFIRMATION_DIALOG = ".confirmation-dialog, #confirmation-modal"
    CONFIRM_DELETE_BUTTON = "button:has-text('Confirm'), .confirm-delete"
    CANCEL_DELETE_BUTTON = "button:has-text('Cancel'), .cancel-delete"
    
    # Message selectors
    SUCCESS_MESSAGE = ".success-message, .alert-success"
    ERROR_MESSAGE = ".error-message, .alert-error"
    
    # Page indicators
    PAGE_TITLE = "User Management"
    PAGE_URL_PATTERN = "/user-management"
    
    def __init__(self, playwright_manager: PlaywrightManager):
        """
        Initialize the UserManagementPage with Playwright manager.
        
        Args:
            playwright_manager (PlaywrightManager): Playwright manager instance
        """
        super().__init__(playwright_manager)
        self.page_url = "https://example.com/user-management"  # Default URL
    
    def click_add_user_button(self):
        """Click the add new user button."""
        try:
            self.click_element(self.ADD_USER_BUTTON)
            self.logger.info("Clicked add user button")
        except Exception as e:
            self.logger.error(f"Failed to click add user button: {e}")
            raise
    
    def fill_user_form(self, user_data: Dict[str, str]):
        """
        Fill the user creation/edit form with provided data.
        
        Args:
            user_data (Dict[str, str]): Dictionary containing user data
        """
        try:
            if 'username' in user_data:
                self.type_text(self.USERNAME_INPUT, user_data['username'])
            
            if 'email' in user_data:
                self.type_text(self.EMAIL_INPUT, user_data['email'])
            
            if 'first_name' in user_data:
                self.type_text(self.FIRST_NAME_INPUT, user_data['first_name'])
            
            if 'last_name' in user_data:
                self.type_text(self.LAST_NAME_INPUT, user_data['last_name'])
            
            if 'role' in user_data:
                self.select_option(self.ROLE_SELECT, user_data['role'])
            
            self.logger.info("Filled user form with provided data")
        except Exception as e:
            self.logger.error(f"Failed to fill user form: {e}")
            raise
    
    def click_create_user_button(self):
        """Click the create user button."""
        try:
            self.click_element(self.CREATE_USER_BUTTON)
            self.logger.info("Clicked create user button")
        except Exception as e:
            self.logger.error(f"Failed to click create user button: {e}")
            raise
    
    def click_save_changes_button(self):
        """Click the save changes button."""
        try:
            self.click_element(self.SAVE_CHANGES_BUTTON)
            self.logger.info("Clicked save changes button")
        except Exception as e:
            self.logger.error(f"Failed to click save changes button: {e}")
            raise
    
    def search_user(self, search_term: str):
        """
        Search for users using the search functionality.
        
        Args:
            search_term (str): Term to search for
        """
        try:
            self.type_text(self.SEARCH_FIELD, search_term)
            self.click_element(self.SEARCH_BUTTON)
            self.logger.info(f"Searched for user: {search_term}")
        except Exception as e:
            self.logger.error(f"Failed to search for user: {e}")
            raise
    
    def filter_by_role(self, role: str):
        """
        Filter users by role.
        
        Args:
            role (str): Role to filter by
        """
        try:
            self.select_option(self.ROLE_FILTER_DROPDOWN, role)
            self.logger.info(f"Filtered users by role: {role}")
        except Exception as e:
            self.logger.error(f"Failed to filter by role: {e}")
            raise
    
    def get_user_row_by_username(self, username: str) -> Locator:
        """
        Get user row by username.
        
        Args:
            username (str): Username to search for
            
        Returns:
            Locator: User row locator
        """
        try:
            return self.page.locator(f"{self.USER_ROW}:has-text('{username}')")
        except Exception as e:
            self.logger.error(f"Failed to get user row for username {username}: {e}")
            raise
    
    def click_edit_button_for_user(self, username: str):
        """
        Click edit button for specific user.
        
        Args:
            username (str): Username of user to edit
        """
        try:
            user_row = self.get_user_row_by_username(username)
            edit_button = user_row.locator(self.EDIT_BUTTON)
            edit_button.click()
            self.logger.info(f"Clicked edit button for user: {username}")
        except Exception as e:
            self.logger.error(f"Failed to click edit button for user {username}: {e}")
            raise
    
    def click_delete_button_for_user(self, username: str):
        """
        Click delete button for specific user.
        
        Args:
            username (str): Username of user to delete
        """
        try:
            user_row = self.get_user_row_by_username(username)
            delete_button = user_row.locator(self.DELETE_BUTTON)
            delete_button.click()
            self.logger.info(f"Clicked delete button for user: {username}")
        except Exception as e:
            self.logger.error(f"Failed to click delete button for user {username}: {e}")
            raise
    
    def confirm_deletion(self):
        """Confirm deletion in the confirmation dialog."""
        try:
            self.wait_for_element(self.CONFIRMATION_DIALOG)
            self.click_element(self.CONFIRM_DELETE_BUTTON)
            self.logger.info("Confirmed deletion")
        except Exception as e:
            self.logger.error(f"Failed to confirm deletion: {e}")
            raise
    
    def cancel_deletion(self):
        """Cancel deletion in the confirmation dialog."""
        try:
            self.wait_for_element(self.CONFIRMATION_DIALOG)
            self.click_element(self.CANCEL_DELETE_BUTTON)
            self.logger.info("Cancelled deletion")
        except Exception as e:
            self.logger.error(f"Failed to cancel deletion: {e}")
            raise
    
    def get_success_message(self) -> str:
        """
        Get success message text.
        
        Returns:
            str: Success message text
        """
        try:
            return self.get_text(self.SUCCESS_MESSAGE)
        except Exception as e:
            self.logger.error(f"Failed to get success message: {e}")
            return ""
    
    def get_error_message(self) -> str:
        """
        Get error message text.
        
        Returns:
            str: Error message text
        """
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except Exception as e:
            self.logger.error(f"Failed to get error message: {e}")
            return ""
    
    def is_user_in_table(self, username: str) -> bool:
        """
        Check if user exists in the user table.
        
        Args:
            username (str): Username to check for
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            user_row = self.get_user_row_by_username(username)
            return user_row.count() > 0
        except Exception as e:
            self.logger.error(f"Failed to check if user {username} exists in table: {e}")
            return False
    
    def get_user_count(self) -> int:
        """
        Get total number of users in the table.
        
        Returns:
            int: Number of users
        """
        try:
            return self.page.locator(self.USER_ROW).count()
        except Exception as e:
            self.logger.error(f"Failed to get user count: {e}")
            return 0
    
    def click_next_page(self):
        """Click next page button in pagination."""
        try:
            self.click_element(self.NEXT_PAGE_BUTTON)
            self.logger.info("Clicked next page button")
        except Exception as e:
            self.logger.error(f"Failed to click next page button: {e}")
            raise
    
    def click_previous_page(self):
        """Click previous page button in pagination."""
        try:
            self.click_element(self.PREVIOUS_PAGE_BUTTON)
            self.logger.info("Clicked previous page button")
        except Exception as e:
            self.logger.error(f"Failed to click previous page button: {e}")
            raise
    
    def get_current_page_number(self) -> str:
        """
        Get current page number.
        
        Returns:
            str: Current page number
        """
        try:
            return self.get_text(self.PAGE_NUMBER)
        except Exception as e:
            self.logger.error(f"Failed to get current page number: {e}")
            return ""
    
    def verify_user_management_page_elements(self) -> bool:
        """
        Verify that all expected user management page elements are present.
        
        Returns:
            bool: True if all elements are present, False otherwise
        """
        try:
            elements_to_check = [
                self.ADD_USER_BUTTON,
                self.USER_TABLE,
                self.SEARCH_FIELD
            ]
            
            for element in elements_to_check:
                if not self.is_visible(element):
                    self.logger.error(f"Element not visible: {element}")
                    return False
            
            self.logger.info("All user management page elements are present")
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify user management page elements: {e}")
            return False
    
    def wait_for_page_load(self, timeout: int = 30000):
        """
        Wait for the user management page to fully load.
        
        Args:
            timeout (int): Timeout in milliseconds
        """
        try:
            # Wait for the user table to be visible as an indicator of page load
            self.wait_for_element(self.USER_TABLE, timeout=timeout)
            self.logger.info("User management page loaded successfully")
        except Exception as e:
            self.logger.error(f"User management page failed to load: {e}")
            raise
    
    def is_on_user_management_page(self) -> bool:
        """
        Check if currently on the user management page.
        
        Returns:
            bool: True if on user management page, False otherwise
        """
        try:
            current_url = self.get_current_url()
            title = self.page.title()
            
            url_check = self.PAGE_URL_PATTERN in current_url
            title_check = self.PAGE_TITLE.lower() in title.lower()
            elements_check = self.verify_user_management_page_elements()
            
            return url_check or title_check or elements_check
        except Exception as e:
            self.logger.error(f"Failed to verify user management page: {e}")
            return False

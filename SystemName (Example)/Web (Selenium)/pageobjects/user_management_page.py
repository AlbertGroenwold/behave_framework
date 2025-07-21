"""
User Management Page Object for Web Testing

This module contains the UserManagementPage class which provides methods to interact
with user management functionality following the Page Object Model pattern.
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


class UserManagementPage(BasePage):
    """
    User Management page object following Page Object Model pattern.
    
    This class provides methods to interact with user management functionality
    including adding, editing, and managing users in the system.
    
    Attributes:
        ADD_USER_BUTTON: Locator for add user button
        USER_LIST: Locator for user list container
        SUCCESS_MESSAGE: Locator for success message display
        USER_FORM: Locator for user form
        SAVE_BUTTON: Locator for save button
        SAVE_CHANGES_BUTTON: Locator for save changes button
        DELETE_BUTTON: Locator for delete button
        SEARCH_FIELD: Locator for user search field
    """
    
    # Page locators
    ADD_USER_BUTTON = (By.ID, "add-user-button")
    USER_LIST = (By.CLASS_NAME, "user-list")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")
    USER_FORM = (By.ID, "user-form")
    SAVE_BUTTON = (By.ID, "save-button")
    SAVE_CHANGES_BUTTON = (By.ID, "save-changes-button")
    DELETE_BUTTON = (By.CLASS_NAME, "delete-button")
    SEARCH_FIELD = (By.ID, "user-search")
    
    # Form field locators
    USERNAME_FIELD = (By.NAME, "username")
    EMAIL_FIELD = (By.NAME, "email")
    FIRST_NAME_FIELD = (By.NAME, "first_name")
    LAST_NAME_FIELD = (By.NAME, "last_name")
    ROLE_DROPDOWN = (By.NAME, "role")
    PASSWORD_FIELD = (By.NAME, "password")
    CONFIRM_PASSWORD_FIELD = (By.NAME, "confirm_password")
    
    # Alternative locators
    SUCCESS_MESSAGE_ALT = (By.CSS_SELECTOR, ".alert-success, .notification-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger, .error-message")
    LOADING_INDICATOR = (By.CLASS_NAME, "loading")
    
    # Table and list locators
    USER_TABLE = (By.ID, "users-table")
    USER_ROWS = (By.CSS_SELECTOR, "#users-table tbody tr")
    PAGINATION = (By.CLASS_NAME, "pagination")
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the UserManagementPage with a WebDriver instance.
        
        Args:
            driver (WebDriver): Selenium WebDriver instance
        """
        super().__init__(driver)
        self.page_url = f"{self.get_base_url()}/admin/users"
        self.page_title = "User Management"
    
    def navigate_to_user_management(self) -> None:
        """
        Navigate to the user management page and verify it loaded.
        
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        self.logger.info(f"Navigating to user management page: {self.page_url}")
        self.navigate_to(self.page_url)
        self.wait_for_page_load()
    
    def wait_for_page_load(self) -> None:
        """Wait for the user management page to fully load."""
        try:
            self.wait_for_element_visible(self.ADD_USER_BUTTON)
            self.wait_for_element_visible(self.USER_LIST)
            self.logger.info("User management page loaded successfully")
        except Exception as e:
            self.logger.warning(f"User management page load verification failed: {e}")
    
    def click_add_user_button(self) -> None:
        """
        Click the add user button to open user creation form.
        
        Raises:
            TimeoutException: If add user button is not found
        """
        self.logger.info("Clicking add user button")
        self.click_element(self.ADD_USER_BUTTON)
    
    def click_button(self, button_text: str) -> None:
        """
        Click button by its text content.
        
        Args:
            button_text (str): Text content of the button to click
            
        Raises:
            TimeoutException: If button with specified text is not found
        """
        self.logger.info(f"Clicking button with text: {button_text}")
        button_locator = (By.XPATH, f"//button[text()='{button_text}']")
        self.click_element(button_locator)
    
    def fill_field(self, field_name: str, value: str) -> None:
        """
        Fill form field by field name.
        
        Args:
            field_name (str): Name of the field to fill
            value (str): Value to enter in the field
            
        Raises:
            TimeoutException: If field is not found
        """
        self.logger.info(f"Filling field '{field_name}' with value: {value}")
        field_locator = (By.NAME, field_name.lower().replace(' ', '_'))
        self.clear_and_type(field_locator, value)
    
    def is_success_message_displayed(self) -> bool:
        """
        Check if success message is displayed.
        
        Returns:
            bool: True if success message is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.SUCCESS_MESSAGE) or \
                   self.is_element_displayed(self.SUCCESS_MESSAGE_ALT)
        except Exception:
            return False
    
    def get_success_message_text(self) -> str:
        """
        Get the text of the success message.
        
        Returns:
            str: Success message text or empty string if not found
        """
        try:
            if self.is_element_displayed(self.SUCCESS_MESSAGE):
                return self.get_element_text(self.SUCCESS_MESSAGE)
            elif self.is_element_displayed(self.SUCCESS_MESSAGE_ALT):
                return self.get_element_text(self.SUCCESS_MESSAGE_ALT)
        except Exception as e:
            self.logger.warning(f"Could not get success message text: {e}")
        return ""
    
    def is_error_message_displayed(self) -> bool:
        """
        Check if error message is displayed.
        
        Returns:
            bool: True if error message is visible, False otherwise
        """
        try:
            return self.is_element_displayed(self.ERROR_MESSAGE)
        except Exception:
            return False
    
    def get_error_message_text(self) -> str:
        """
        Get the text of the error message.
        
        Returns:
            str: Error message text or empty string if not found
        """
        try:
            if self.is_element_displayed(self.ERROR_MESSAGE):
                return self.get_element_text(self.ERROR_MESSAGE)
        except Exception as e:
            self.logger.warning(f"Could not get error message text: {e}")
        return ""
    
    def is_user_in_list(self, username: str) -> bool:
        """
        Check if user appears in the user list.
        
        Args:
            username (str): Username to search for
            
        Returns:
            bool: True if user is found in list, False otherwise
        """
        self.logger.info(f"Checking if user '{username}' is in list")
        user_locator = (By.XPATH, f"//td[text()='{username}']")
        try:
            return self.is_element_displayed(user_locator)
        except Exception:
            return False
    
    def search_user(self, username: str) -> None:
        """
        Search for a user using the search field.
        
        Args:
            username (str): Username to search for
            
        Raises:
            TimeoutException: If search field is not found
        """
        self.logger.info(f"Searching for user: {username}")
        self.clear_and_type(self.SEARCH_FIELD, username)
    
    def click_edit_user(self, username: str) -> None:
        """
        Click edit button for a specific user.
        
        Args:
            username (str): Username of the user to edit
            
        Raises:
            TimeoutException: If edit button for user is not found
        """
        self.logger.info(f"Clicking edit button for user: {username}")
        edit_button_locator = (By.XPATH, f"//tr[td[text()='{username}']]//button[contains(@class, 'edit') or contains(text(), 'Edit')]")
        self.click_element(edit_button_locator)
    
    def update_user_email(self, new_email: str) -> None:
        """
        Update user email field in the edit form.
        
        Args:
            new_email (str): New email address to set
            
        Raises:
            TimeoutException: If email field is not found
        """
        self.logger.info(f"Updating user email to: {new_email}")
        self.clear_and_type(self.EMAIL_FIELD, new_email)
    
    def click_save_changes(self) -> None:
        """
        Click save changes button to save user modifications.
        
        Raises:
            TimeoutException: If save changes button is not found
        """
        self.logger.info("Clicking save changes button")
        self.click_element(self.SAVE_CHANGES_BUTTON)
    
    def is_update_success_displayed(self) -> bool:
        """
        Check if update success message is displayed.
        
        Returns:
            bool: True if update success message is visible, False otherwise
        """
        return self.is_success_message_displayed()
    
    def is_email_updated(self, email: str) -> bool:
        """
        Check if email appears updated in the user list.
        
        Args:
            email (str): Email to verify in the list
            
        Returns:
            bool: True if email is found in list, False otherwise
        """
        self.logger.info(f"Checking if email '{email}' is updated in list")
        email_locator = (By.XPATH, f"//td[text()='{email}']")
        try:
            return self.is_element_displayed(email_locator)
        except Exception:
            return False
    
    def delete_user(self, username: str) -> None:
        """
        Delete a user from the system.
        
        Args:
            username (str): Username of the user to delete
            
        Raises:
            TimeoutException: If delete button for user is not found
        """
        self.logger.info(f"Deleting user: {username}")
        delete_button_locator = (By.XPATH, f"//tr[td[text()='{username}']]//button[contains(@class, 'delete') or contains(text(), 'Delete')]")
        self.click_element(delete_button_locator)
        
        # Handle confirmation dialog if present
        try:
            confirm_button = (By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes')]")
            if self.is_element_displayed(confirm_button):
                self.click_element(confirm_button)
                self.logger.info("Confirmed user deletion")
        except Exception:
            pass  # No confirmation dialog present
    
    def create_user(self, username: str, email: str, first_name: str = "", last_name: str = "", 
                   role: str = "user", password: str = "defaultPassword123") -> None:
        """
        Create a new user with the provided information.
        
        Args:
            username (str): Username for the new user
            email (str): Email address for the new user
            first_name (str, optional): First name. Defaults to "".
            last_name (str, optional): Last name. Defaults to "".
            role (str, optional): User role. Defaults to "user".
            password (str, optional): User password. Defaults to "defaultPassword123".
            
        Raises:
            TimeoutException: If any form elements are not found
        """
        self.logger.info(f"Creating new user: {username}")
        
        self.click_add_user_button()
        
        # Wait for form to be visible
        self.wait_for_element_visible(self.USER_FORM)
        
        # Fill required fields
        self.clear_and_type(self.USERNAME_FIELD, username)
        self.clear_and_type(self.EMAIL_FIELD, email)
        
        # Fill password fields if present
        try:
            if self.is_element_displayed(self.PASSWORD_FIELD):
                self.clear_and_type(self.PASSWORD_FIELD, password)
            if self.is_element_displayed(self.CONFIRM_PASSWORD_FIELD):
                self.clear_and_type(self.CONFIRM_PASSWORD_FIELD, password)
        except Exception:
            pass  # Password fields may not be required
        
        # Fill optional fields if provided
        if first_name:
            try:
                self.clear_and_type(self.FIRST_NAME_FIELD, first_name)
            except Exception:
                pass  # Field may not exist
        
        if last_name:
            try:
                self.clear_and_type(self.LAST_NAME_FIELD, last_name)
            except Exception:
                pass  # Field may not exist
        
        if role:
            try:
                self.select_from_dropdown(self.ROLE_DROPDOWN, role)
            except Exception:
                pass  # Dropdown may not exist
        
        # Save the user
        self.click_element(self.SAVE_BUTTON)
        self.logger.info(f"User '{username}' creation submitted")
    
    def get_user_count(self) -> int:
        """
        Get the total number of users displayed in the list.
        
        Returns:
            int: Number of users in the list
        """
        try:
            user_rows = self.find_elements(self.USER_ROWS)
            count = len(user_rows)
            self.logger.info(f"Found {count} users in the list")
            return count
        except Exception as e:
            self.logger.warning(f"Could not get user count: {e}")
            return 0
    
    def wait_for_loading_to_complete(self, timeout: int = 10) -> None:
        """
        Wait for loading indicator to disappear.
        
        Args:
            timeout (int, optional): Maximum time to wait. Defaults to 10.
        """
        try:
            self.wait_for_element_invisible(self.LOADING_INDICATOR, timeout)
            self.logger.info("Loading completed")
        except Exception:
            pass  # Loading indicator may not be present
    
    def verify_user_management_page_elements(self) -> bool:
        """
        Verify all essential user management page elements are present.
        
        Returns:
            bool: True if all essential elements are present, False otherwise
        """
        try:
            elements_present = (
                self.is_element_displayed(self.ADD_USER_BUTTON) and
                self.is_element_displayed(self.USER_LIST)
            )
            
            if elements_present:
                self.logger.info("All essential user management page elements are present")
            else:
                self.logger.warning("Some essential user management page elements are missing")
                
            return elements_present
            
        except Exception as e:
            self.logger.error(f"Error verifying user management page elements: {e}")
            return False
    
    def refresh_user_list(self) -> None:
        """Refresh the user list by reloading the page."""
        self.logger.info("Refreshing user list")
        self.driver.refresh()
        self.wait_for_page_load()

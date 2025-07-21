"""
Users API Page Object for API Testing

This module contains the UsersAPIPage class which provides methods to interact
with user-related API endpoints following the Page Object Model pattern.
"""

import sys
import os
from typing import Dict, Any, List, Optional
import re

# Add the base directory to Python path for importing base classes
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from api.base_api_page import BaseAPIPage
from api.api_client import BaseAPIClient


class UsersAPIPage(BaseAPIPage):
    """
    Page Object for Users API endpoints following the Page Object Model pattern.
    
    This class handles all user-related API operations and validations including
    CRUD operations, data validation, and response verification.
    
    Attributes:
        required_fields: List of required fields for user creation
        optional_fields: List of optional fields that may be present
        valid_roles: List of valid user roles
        email_pattern: Regex pattern for email validation
    """
    
    def __init__(self, api_client: BaseAPIClient):
        """
        Initialize Users API page object.
        
        Args:
            api_client (BaseAPIClient): API client instance for making requests
        """
        super().__init__(api_client, '/users')
        
        # Define field validation rules
        self.required_fields = ['username', 'email', 'first_name', 'last_name']
        self.optional_fields = ['id', 'created_at', 'updated_at', 'is_active', 'role', 'phone', 'address']
        self.valid_roles = ['admin', 'user', 'moderator', 'viewer']
        
        # Validation patterns
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.username_pattern = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
        
        self.logger.info("UsersAPIPage initialized")
    
    def validate_resource_structure(self, resource_data: Dict[str, Any], strict: bool = True) -> None:
        """
        Validate that a user resource has the expected structure and field types.
        
        Args:
            resource_data (Dict[str, Any]): User data to validate
            strict (bool, optional): Whether to enforce strict validation. Defaults to True.
            
        Raises:
            AssertionError: If validation fails
        """
        self.logger.info("Validating user resource structure")
        
        if not isinstance(resource_data, dict):
            raise AssertionError("User data must be a dictionary")
        
        # Check required fields
        missing_fields = []
        for field in self.required_fields:
            if field not in resource_data:
                missing_fields.append(field)
        
        if missing_fields:
            raise AssertionError(f"Required fields missing: {', '.join(missing_fields)}")
        
        # Validate specific field types and formats
        self._validate_email(resource_data.get('email'))
        self._validate_username(resource_data.get('username'))
        self._validate_role(resource_data.get('role'))
        
        if strict:
            self._validate_field_types(resource_data)
        
        self.logger.info("User resource structure validation passed")
    
    def _validate_email(self, email: Any) -> None:
        """
        Validate email field format.
        
        Args:
            email: Email value to validate
            
        Raises:
            AssertionError: If email format is invalid
        """
        if email is not None:
            if not isinstance(email, str):
                raise AssertionError(f"Email must be a string, got {type(email)}")
            
            if not self.email_pattern.match(email):
                raise AssertionError(f"Invalid email format: {email}")
    
    def _validate_username(self, username: Any) -> None:
        """
        Validate username field format.
        
        Args:
            username: Username value to validate
            
        Raises:
            AssertionError: If username format is invalid
        """
        if username is not None:
            if not isinstance(username, str):
                raise AssertionError(f"Username must be a string, got {type(username)}")
            
            if not self.username_pattern.match(username):
                raise AssertionError(f"Invalid username format: {username}. Must be 3-20 characters, alphanumeric and underscore only")
    
    def _validate_role(self, role: Any) -> None:
        """
        Validate user role field.
        
        Args:
            role: Role value to validate
            
        Raises:
            AssertionError: If role is invalid
        """
        if role is not None:
            if not isinstance(role, str):
                raise AssertionError(f"Role must be a string, got {type(role)}")
            
            if role not in self.valid_roles:
                raise AssertionError(f"Invalid role: {role}. Valid roles are: {', '.join(self.valid_roles)}")
    
    def _validate_field_types(self, resource_data: Dict[str, Any]) -> None:
        """
        Validate field types for user data.
        
        Args:
            resource_data (Dict[str, Any]): User data to validate
            
        Raises:
            AssertionError: If field types are invalid
        """
        # String field validations
        string_fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address', 'role']
        for field in string_fields:
            if field in resource_data and resource_data[field] is not None:
                if not isinstance(resource_data[field], str):
                    raise AssertionError(f"Field '{field}' must be a string, got {type(resource_data[field])}")
        
        # Boolean field validations
        if 'is_active' in resource_data and resource_data['is_active'] is not None:
            if not isinstance(resource_data['is_active'], bool):
                raise AssertionError(f"Field 'is_active' must be a boolean, got {type(resource_data['is_active'])}")
        
        # Integer field validations (if ID is present)
        if 'id' in resource_data and resource_data['id'] is not None:
            if not isinstance(resource_data['id'], int):
                raise AssertionError(f"Field 'id' must be an integer, got {type(resource_data['id'])}")
    
    def get_resource_id(self, resource_data: Dict[str, Any]) -> str:
        """
        Extract the user ID from user data.
        
        Args:
            resource_data (Dict[str, Any]): User data containing ID
            
        Returns:
            str: User ID as string
            
        Raises:
            AssertionError: If ID is not found or invalid
        """
        if 'id' not in resource_data:
            raise AssertionError("User data does not contain 'id' field")
        
        user_id = resource_data['id']
        if user_id is None:
            raise AssertionError("User ID cannot be None")
        
        return str(user_id)
    
    # Specific user operations with enhanced error handling and logging
    
    def get_all_users(self, page: Optional[int] = None, limit: Optional[int] = None, 
                     filter_active: Optional[bool] = None) -> Any:
        """
        Get all users with optional pagination and filtering.
        
        Args:
            page (int, optional): Page number for pagination
            limit (int, optional): Number of users per page
            filter_active (bool, optional): Filter by active status
            
        Returns:
            Response object containing user list
        """
        self.logger.info(f"Getting all users (page={page}, limit={limit}, active={filter_active})")
        
        params = {}
        if page is not None:
            params['page'] = page
        if limit is not None:
            params['limit'] = limit
        if filter_active is not None:
            params['active'] = filter_active
        
        response = self.get_all(params=params if params else None)
        self.logger.info(f"Retrieved users list with status: {response.status_code}")
        return response
    
    def get_user_by_id(self, user_id: str) -> Any:
        """
        Get user by ID with validation.
        
        Args:
            user_id (str): User ID to retrieve
            
        Returns:
            Response object containing user data
        """
        self.logger.info(f"Getting user by ID: {user_id}")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        response = self.get_by_id(str(user_id))
        self.logger.info(f"Retrieved user {user_id} with status: {response.status_code}")
        return response
    
    def create_user(self, user_data: Dict[str, Any]) -> Any:
        """
        Create a new user with validation.
        
        Args:
            user_data (Dict[str, Any]): User data dictionary
            
        Returns:
            Response object containing created user data
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        self.logger.info(f"Creating new user: {user_data.get('username', 'unknown')}")
        
        # Validate required fields before sending request
        missing_fields = []
        for field in self.required_fields:
            if field not in user_data or not user_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Required fields missing or empty: {', '.join(missing_fields)}")
        
        # Validate field formats
        self._validate_email(user_data.get('email'))
        self._validate_username(user_data.get('username'))
        if 'role' in user_data:
            self._validate_role(user_data.get('role'))
        
        response = self.create(user_data)
        self.logger.info(f"User creation request sent with status: {response.status_code}")
        return response
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Any:
        """
        Update existing user (full update) with validation.
        
        Args:
            user_id (str): User ID to update
            user_data (Dict[str, Any]): Complete user data dictionary
            
        Returns:
            Response object containing updated user data
        """
        self.logger.info(f"Updating user {user_id} with full data")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        # Validate field formats if present
        if 'email' in user_data:
            self._validate_email(user_data.get('email'))
        if 'username' in user_data:
            self._validate_username(user_data.get('username'))
        if 'role' in user_data:
            self._validate_role(user_data.get('role'))
        
        response = self.update(str(user_id), user_data)
        self.logger.info(f"User {user_id} update request sent with status: {response.status_code}")
        return response
    
    def update_user_partial(self, user_id: str, user_data: Dict[str, Any]) -> Any:
        """
        Partially update existing user with validation.
        
        Args:
            user_id (str): User ID to update
            user_data (Dict[str, Any]): Partial user data dictionary
            
        Returns:
            Response object containing updated user data
        """
        self.logger.info(f"Partially updating user {user_id}")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        if not user_data:
            raise ValueError("Update data cannot be empty")
        
        # Validate field formats if present
        if 'email' in user_data:
            self._validate_email(user_data.get('email'))
        if 'username' in user_data:
            self._validate_username(user_data.get('username'))
        if 'role' in user_data:
            self._validate_role(user_data.get('role'))
        
        response = self.partial_update(str(user_id), user_data)
        self.logger.info(f"User {user_id} partial update request sent with status: {response.status_code}")
        return response
    
    def delete_user(self, user_id: str) -> Any:
        """
        Delete user by ID with validation.
        
        Args:
            user_id (str): User ID to delete
            
        Returns:
            Response object
        """
        self.logger.info(f"Deleting user: {user_id}")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        response = self.delete(str(user_id))
        self.logger.info(f"User {user_id} deletion request sent with status: {response.status_code}")
        return response
    
    def search_users(self, search_criteria: Dict[str, Any]) -> Any:
        """
        Search users by criteria with validation.
        
        Args:
            search_criteria (Dict[str, Any]): Search parameters (e.g., name, email, role)
            
        Returns:
            Response object containing search results
        """
        self.logger.info(f"Searching users with criteria: {search_criteria}")
        
        if not search_criteria:
            raise ValueError("Search criteria cannot be empty")
        
        response = self._make_request('GET', '/search', params=search_criteria)
        self.logger.info(f"User search request sent with status: {response.status_code}")
        return response
    
    def get_user_by_username(self, username: str) -> Any:
        """
        Get user by username with validation.
        
        Args:
            username (str): Username to search for
            
        Returns:
            Response object containing user data
        """
        self.logger.info(f"Getting user by username: {username}")
        
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        
        self._validate_username(username)
        
        response = self._make_request('GET', f'/username/{username}')
        self.logger.info(f"User lookup by username request sent with status: {response.status_code}")
        return response
    
    def get_user_by_email(self, email: str) -> Any:
        """
        Get user by email with validation.
        
        Args:
            email (str): Email to search for
            
        Returns:
            Response object containing user data
        """
        self.logger.info(f"Getting user by email: {email}")
        
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        
        self._validate_email(email)
        
        response = self._make_request('GET', f'/email/{email}')
        self.logger.info(f"User lookup by email request sent with status: {response.status_code}")
        return response
    
    def activate_user(self, user_id: str) -> Any:
        """
        Activate user account with validation.
        
        Args:
            user_id (str): User ID to activate
            
        Returns:
            Response object
        """
        self.logger.info(f"Activating user: {user_id}")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        response = self._make_request('POST', f'/{user_id}/activate')
        self.logger.info(f"User {user_id} activation request sent with status: {response.status_code}")
        return response
    
    def deactivate_user(self, user_id: str) -> Any:
        """
        Deactivate user account with validation.
        
        Args:
            user_id (str): User ID to deactivate
            
        Returns:
            Response object
        """
        self.logger.info(f"Deactivating user: {user_id}")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        response = self._make_request('POST', f'/{user_id}/deactivate')
        self.logger.info(f"User {user_id} deactivation request sent with status: {response.status_code}")
        return response
    
    def change_user_password(self, user_id: str, password_data: Dict[str, str]) -> Any:
        """
        Change user password with validation.
        
        Args:
            user_id (str): User ID
            password_data (Dict[str, str]): Dictionary with 'old_password' and 'new_password'
            
        Returns:
            Response object
            
        Raises:
            ValueError: If required password fields are missing or invalid
        """
        self.logger.info(f"Changing password for user: {user_id}")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        required_fields = ['old_password', 'new_password']
        missing_fields = []
        
        for field in required_fields:
            if field not in password_data or not password_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Required password fields missing or empty: {', '.join(missing_fields)}")
        
        # Basic password validation
        new_password = password_data['new_password']
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long")
        
        response = self._make_request('POST', f'/{user_id}/change-password', json=password_data)
        self.logger.info(f"Password change request for user {user_id} sent with status: {response.status_code}")
        return response
    
    def reset_user_password(self, user_id: str, new_password: str) -> Any:
        """
        Reset user password (admin function) with validation.
        
        Args:
            user_id (str): User ID
            new_password (str): New password to set
            
        Returns:
            Response object
        """
        self.logger.info(f"Resetting password for user: {user_id}")
        
        if not user_id or not str(user_id).strip():
            raise ValueError("User ID cannot be empty")
        
        if not new_password or len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long")
        
        password_data = {'new_password': new_password}
        response = self._make_request('POST', f'/{user_id}/reset-password', json=password_data)
        self.logger.info(f"Password reset request for user {user_id} sent with status: {response.status_code}")
        return response
    
    # Enhanced validation methods specific to users
    
    def validate_user_list_response(self) -> None:
        """
        Validate that response contains a properly formatted list of users.
        
        Raises:
            AssertionError: If validation fails
        """
        self.logger.info("Validating user list response")
        self.validate_response_is_list()
        
        # Validate each user in the list
        response_data = self.get_response_data()
        for index, user in enumerate(response_data):
            try:
                self.validate_resource_structure(user, strict=False)
            except AssertionError as e:
                raise AssertionError(f"User at index {index} failed validation: {e}")
        
        self.logger.info(f"User list validation passed for {len(response_data)} users")
    
    def validate_user_details_response(self) -> None:
        """
        Validate that response contains properly formatted user details.
        
        Raises:
            AssertionError: If validation fails
        """
        self.logger.info("Validating user details response")
        response_data = self.get_response_data()
        self.validate_resource_structure(response_data)
        self.logger.info("User details validation passed")
    
    def validate_user_created(self, expected_data: Dict[str, Any]) -> None:
        """
        Validate that user was created with expected data.
        
        Args:
            expected_data (Dict[str, Any]): Expected user data to verify
            
        Raises:
            AssertionError: If validation fails
        """
        self.logger.info("Validating user creation response")
        response_data = self.get_response_data()
        self.validate_resource_structure(response_data)
        
        # Check that expected fields match
        mismatches = []
        for field, expected_value in expected_data.items():
            if field in response_data:
                actual_value = response_data[field]
                if actual_value != expected_value:
                    mismatches.append(f"Field '{field}': expected '{expected_value}', got '{actual_value}'")
        
        if mismatches:
            raise AssertionError(f"User creation validation failed: {'; '.join(mismatches)}")
        
        self.logger.info("User creation validation passed")
    
    def validate_user_updated(self, expected_data: Dict[str, Any]) -> None:
        """
        Validate that user was updated with expected data.
        
        Args:
            expected_data (Dict[str, Any]): Expected updated user data to verify
        """
        self.logger.info("Validating user update response")
        self.validate_user_created(expected_data)  # Same validation logic
        self.logger.info("User update validation passed")
    
    def validate_user_id_matches(self, expected_user_id: str) -> None:
        """
        Validate that the response user ID matches expected ID.
        
        Args:
            expected_user_id (str): Expected user ID
            
        Raises:
            AssertionError: If user ID doesn't match
        """
        response_data = self.get_response_data()
        actual_user_id = self.get_resource_id(response_data)
        
        if actual_user_id != str(expected_user_id):
            raise AssertionError(f"User ID mismatch: expected '{expected_user_id}', got '{actual_user_id}'")
        
        self.logger.info(f"User ID validation passed: {actual_user_id}")
    
    def get_created_user_id(self) -> str:
        """
        Get the ID of the user from the last response.
        
        Returns:
            str: User ID as string
            
        Raises:
            AssertionError: If user ID cannot be extracted
        """
        response_data = self.get_response_data()
        user_id = self.get_resource_id(response_data)
        self.logger.info(f"Extracted user ID: {user_id}")
        return user_id
    
    def get_all_user_ids(self) -> List[str]:
        """
        Get all user IDs from a list response.
        
        Returns:
            List[str]: List of user IDs as strings
            
        Raises:
            AssertionError: If response is not a proper user list
        """
        response_data = self.get_response_data()
        if not isinstance(response_data, list):
            raise AssertionError("Response is not a list of users")
        
        user_ids = []
        for user in response_data:
            try:
                user_id = self.get_resource_id(user)
                user_ids.append(user_id)
            except AssertionError as e:
                self.logger.warning(f"Could not extract ID from user: {e}")
        
        self.logger.info(f"Extracted {len(user_ids)} user IDs")
        return user_ids
    
    def get_user_count_from_response(self) -> int:
        """
        Get the count of users from the response.
        
        Returns:
            int: Number of users in the response
        """
        response_data = self.get_response_data()
        
        if isinstance(response_data, list):
            count = len(response_data)
        elif isinstance(response_data, dict) and 'count' in response_data:
            count = response_data['count']
        else:
            count = 1 if response_data else 0
        
        self.logger.info(f"User count from response: {count}")
        return count

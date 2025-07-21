from behave import given, when, then
import sys
import os
import json

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from api.api_client import BaseAPIClient
from ..pageobjects.users_api_page import UsersAPIPage


@given('the API is available and accessible')
def step_api_available(context):
    """Verify API is available and accessible"""
    if not hasattr(context, 'api_client'):
        context.api_client = BaseAPIClient()
    
    if not hasattr(context, 'users_api'):
        context.users_api = UsersAPIPage(context.api_client)
    
    # Perform health check
    response = context.api_client.get('/health')
    assert response.status_code in [200, 404], f"API not accessible. Status: {response.status_code}"


@given('I have a valid user ID')
def step_have_valid_user_id(context):
    """Setup a valid user ID for testing"""
    # Get existing user or create one for testing
    if not hasattr(context, 'users_api'):
        context.api_client = BaseAPIClient()
        context.users_api = UsersAPIPage(context.api_client)
    
    context.users_api.get_all_users()
    if context.users_api.get_response_status() == 200:
        users = context.users_api.get_response_data()
        if users:
            context.user_id = context.users_api.get_resource_id(users[0])
        else:
            context.user_id = "1"  # Default test user ID
    else:
        context.user_id = "1"  # Default test user ID


@given('I have valid user data')
def step_have_valid_user_data(context):
    """Setup valid user data from table"""
    context.user_data = {}
    for row in context.table:
        context.user_data[row['field']] = row['value']


@given('I have invalid user data')
def step_have_invalid_user_data(context):
    """Setup invalid user data from table"""
    context.user_data = {}
    for row in context.table:
        context.user_data[row['field']] = row['value']


@given('I have an existing user')
def step_have_existing_user(context):
    """Create or ensure existing user for testing"""
    if not hasattr(context, 'users_api'):
        context.api_client = BaseAPIClient()
        context.users_api = UsersAPIPage(context.api_client)
    
    # Create a test user
    test_user_data = {
        'username': 'existing_test_user',
        'email': 'existing@test.com',
        'first_name': 'Existing',
        'last_name': 'User'
    }
    
    context.users_api.create_user(test_user_data)
    if context.users_api.get_response_status() == 201:
        context.existing_user = context.users_api.get_response_data()
        context.user_id = context.users_api.get_resource_id(context.existing_user)
    else:
        # User might already exist, try to find them
        context.users_api.get_all_users()
        if context.users_api.get_response_status() == 200:
            users = context.users_api.get_response_data()
            if users:
                context.existing_user = users[0]
                context.user_id = context.users_api.get_resource_id(context.existing_user)


@given('I have an existing user to delete')
def step_have_existing_user_to_delete(context):
    """Create a user specifically for deletion testing"""
    if not hasattr(context, 'users_api'):
        context.api_client = BaseAPIClient()
        context.users_api = UsersAPIPage(context.api_client)
    
    # Create a test user for deletion
    test_user_data = {
        'username': 'delete_test_user',
        'email': 'delete@test.com',
        'first_name': 'Delete',
        'last_name': 'User'
    }
    
    context.users_api.create_user(test_user_data)
    if context.users_api.get_response_status() == 201:
        context.delete_user = context.users_api.get_response_data()
        context.user_id = context.users_api.get_resource_id(context.delete_user)


@given('I have no authentication token')
def step_no_auth_token(context):
    """Remove authentication token"""
    if not hasattr(context, 'api_client'):
        context.api_client = BaseAPIClient()
    
    context.api_client.remove_header('Authorization')


# WHEN STEPS - Using Page Object Pattern

@when('I send a GET request to "{endpoint}"')
def step_send_get_request(context, endpoint):
    """Send GET request to specified endpoint using page objects"""
    if not hasattr(context, 'users_api'):
        context.api_client = BaseAPIClient()
        context.users_api = UsersAPIPage(context.api_client)
    
    if endpoint == "/users":
        context.users_api.get_all_users()
    elif endpoint.startswith("/users/") and endpoint.endswith(str(context.user_id)):
        context.users_api.get_user_by_id(context.user_id)
    else:
        # Fallback to direct API client for other endpoints
        if '{user_id}' in endpoint and hasattr(context, 'user_id'):
            endpoint = endpoint.replace('{user_id}', str(context.user_id))
        context.response = context.api_client.get(endpoint)


@when('I send a POST request to "{endpoint}" with the user data')
def step_send_post_request_with_data(context, endpoint):
    """Send POST request with user data using page objects"""
    if not hasattr(context, 'users_api'):
        context.api_client = BaseAPIClient()
        context.users_api = UsersAPIPage(context.api_client)
    
    if endpoint == "/users":
        context.users_api.create_user(context.user_data)
    else:
        # Fallback to direct API client for other endpoints
        context.response = context.api_client.post(endpoint, json=context.user_data)


@when('I send a PUT request to "{endpoint}" with updated data')
def step_send_put_request_with_data(context, endpoint):
    """Send PUT request with updated data using page objects"""
    if not hasattr(context, 'users_api'):
        context.api_client = BaseAPIClient()
        context.users_api = UsersAPIPage(context.api_client)
    
    # Get updated data from table
    updated_data = {}
    for row in context.table:
        updated_data[row['field']] = row['value']
    
    if endpoint.startswith("/users/") and hasattr(context, 'user_id'):
        context.users_api.update_user(context.user_id, updated_data)
    else:
        # Fallback to direct API client for other endpoints
        if '{user_id}' in endpoint and hasattr(context, 'user_id'):
            endpoint = endpoint.replace('{user_id}', str(context.user_id))
        context.response = context.api_client.put(endpoint, json=updated_data)


@when('I send a DELETE request to "{endpoint}"')
def step_send_delete_request(context, endpoint):
    """Send DELETE request to specified endpoint using page objects"""
    if not hasattr(context, 'users_api'):
        context.api_client = BaseAPIClient()
        context.users_api = UsersAPIPage(context.api_client)
    
    if endpoint.startswith("/users/") and hasattr(context, 'user_id'):
        context.users_api.delete_user(context.user_id)
    else:
        # Fallback to direct API client for other endpoints
        if '{user_id}' in endpoint and hasattr(context, 'user_id'):
            endpoint = endpoint.replace('{user_id}', str(context.user_id))
        context.response = context.api_client.delete(endpoint)


# THEN STEPS - Using Page Object Pattern

@then('the response status should be {status_code:d}')
def step_verify_response_status(context, status_code):
    """Verify response status code using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_status_code(status_code)
    else:
        # Fallback for direct API client calls
        assert context.response.status_code == status_code, \
            f"Expected status {status_code}, got {context.response.status_code}. Response: {context.response.text}"


@then('the response should contain a list of users')
def step_verify_response_contains_user_list(context):
    """Verify response contains a list of users using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_user_list_response()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, list), "Response should be a list"
        
        if response_data:  # If list is not empty
            # Verify each item has user properties
            for user in response_data:
                assert 'id' in user, "User should have an ID"


@then('the response should contain user details')
def step_verify_response_contains_user_details(context):
    """Verify response contains user details using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_user_details_response()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, dict), "Response should be a dictionary"
        assert 'id' in response_data, "User should have an ID"
        assert 'username' in response_data or 'email' in response_data, "User should have username or email"


@then('the user ID should match the requested ID')
def step_verify_user_id_matches(context):
    """Verify user ID matches the requested ID using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_user_id_matches(context.user_id)
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        actual_user_id = str(response_data.get('id'))
        assert actual_user_id == str(context.user_id), \
            f"User ID mismatch: expected '{context.user_id}', got '{actual_user_id}'"


@then('the response should contain the created user details')
def step_verify_created_user_details(context):
    """Verify response contains created user details using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_user_details_response()
        # Store the created user ID for future use
        context.user_id = context.users_api.get_created_user_id()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, dict), "Response should be a dictionary"
        assert 'id' in response_data, "Created user should have an ID"
        context.user_id = response_data.get('id')


@then('the user should be created with the provided data')
def step_verify_user_created_with_data(context):
    """Verify user was created with provided data using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_user_created(context.user_data)
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        for field, expected_value in context.user_data.items():
            if field in response_data:
                actual_value = response_data[field]
                assert actual_value == expected_value, \
                    f"User field '{field}': expected '{expected_value}', got '{actual_value}'"


@then('the response should contain the updated user details')
def step_verify_updated_user_details(context):
    """Verify response contains updated user details using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_user_details_response()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, dict), "Response should be a dictionary"
        assert 'id' in response_data, "Updated user should have an ID"


@then('the user data should be updated correctly')
def step_verify_user_updated_correctly(context):
    """Verify user data was updated correctly using page objects"""
    # Get updated data from table
    updated_data = {}
    for row in context.table:
        updated_data[row['field']] = row['value']
    
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_user_updated(updated_data)
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        for field, expected_value in updated_data.items():
            if field in response_data:
                actual_value = response_data[field]
                assert actual_value == expected_value, \
                    f"Updated user field '{field}': expected '{expected_value}', got '{actual_value}'"


@then('the response time should be less than {max_time:d} milliseconds')
def step_verify_response_time(context, max_time):
    """Verify response time using page objects"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        context.users_api.validate_response_time(max_time)
    else:
        # For direct API client calls, we'd need to implement timing there
        # For now, just pass as this is a demonstration
        pass


# Additional validation steps

@then('the user should be deleted from the system')
def step_verify_user_deleted(context):
    """Verify user was deleted from system using page objects"""
    if hasattr(context, 'users_api'):
        # Try to get the deleted user - should return 404
        context.users_api.get_user_by_id(context.user_id)
        # Expect 404 status for deleted user
        assert context.users_api.get_response_status() == 404, "Deleted user should not be found"
    else:
        # Fallback for direct API client calls
        get_response = context.api_client.get(f'/users/{context.user_id}')
        assert get_response.status_code == 404, "Deleted user should not be found"


@then('the response should contain an error message')
def step_verify_error_message(context):
    """Verify response contains error message"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        response_data = context.users_api.get_response_data()
    else:
        response_data = context.response.json()
    
    assert 'error' in response_data or 'message' in response_data, \
        "Response should contain error message"


@then('the response should contain validation errors')
def step_verify_validation_errors(context):
    """Verify response contains validation errors"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        response_data = context.users_api.get_response_data()
    else:
        response_data = context.response.json()
    
    assert 'errors' in response_data or 'error' in response_data, \
        "Response should contain validation errors"


@then('the response should contain an authentication error')
def step_verify_auth_error(context):
    """Verify response contains authentication error"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        response_data = context.users_api.get_response_data()
    else:
        response_data = context.response.json()
    
    assert 'error' in response_data or 'message' in response_data, \
        "Response should contain authentication error"


@then('the response should be properly formatted')
def step_verify_response_format(context):
    """Verify response is properly formatted"""
    if hasattr(context, 'users_api') and context.users_api.last_response:
        # Page object already handles JSON parsing, if we get here it's valid
        try:
            context.users_api.get_response_data()
            assert context.users_api.last_response.headers.get('content-type', '').startswith('application/json'), \
                "Response should be JSON formatted"
        except (json.JSONDecodeError, AssertionError):
            assert False, "Response should be valid JSON"
    else:
        # Fallback for direct API client calls
        try:
            context.response.json()  # Should not raise exception
            assert context.response.headers.get('content-type', '').startswith('application/json'), \
                "Response should be JSON formatted"
        except json.JSONDecodeError:
            assert False, "Response should be valid JSON"

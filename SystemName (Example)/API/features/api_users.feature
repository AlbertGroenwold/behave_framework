@api @users @crud
Feature: User Management API
  As an API consumer
  I want to manage user accounts via REST API
  So that I can perform CRUD operations on user data

  Background:
    Given the API is available and accessible

  @smoke @api
  Scenario: Get all users
    When I send a GET request to "/users"
    Then the response status should be 200
    And the response should contain a list of users
    And the response time should be less than 2000 milliseconds

  @smoke @api
  Scenario: Get user by ID
    Given I have a valid user ID
    When I send a GET request to "/users/{user_id}"
    Then the response status should be 200
    And the response should contain user details
    And the user ID should match the requested ID

  @crud @api
  Scenario: Create a new user
    Given I have valid user data:
      | field      | value              |
      | username   | api_test_user      |
      | email      | apitest@email.com  |
      | first_name | API                |
      | last_name  | Test               |
    When I send a POST request to "/users" with the user data
    Then the response status should be 201
    And the response should contain the created user details
    And the user should be created with the provided data

  @crud @api
  Scenario: Update an existing user
    Given I have an existing user
    When I send a PUT request to "/users/{user_id}" with updated data:
      | field      | value                    |
      | email      | updated_api@email.com    |
      | first_name | Updated API              |
    Then the response status should be 200
    And the response should contain the updated user details
    And the user data should be updated correctly

  @crud @api
  Scenario: Delete a user
    Given I have an existing user to delete
    When I send a DELETE request to "/users/{user_id}"
    Then the response status should be 204
    And the user should be deleted from the system

  @negative @api
  Scenario: Get non-existent user
    When I send a GET request to "/users/99999"
    Then the response status should be 404
    And the response should contain an error message

  @negative @api
  Scenario: Create user with invalid data
    Given I have invalid user data:
      | field      | value              |
      | username   |                    |
      | email      | invalid-email      |
    When I send a POST request to "/users" with the user data
    Then the response status should be 400
    And the response should contain validation errors

  @security @api
  Scenario: Unauthorized access to users endpoint
    Given I have no authentication token
    When I send a GET request to "/users"
    Then the response status should be 401
    And the response should contain an authentication error

  @performance @api
  Scenario: API response time validation
    When I send a GET request to "/users"
    Then the response time should be less than 1000 milliseconds
    And the response should be properly formatted

@user_management @web @playwright
Feature: User Management with Playwright
  As an administrator
  I want to manage users in the system using Playwright
  So that I can maintain user accounts efficiently with modern browser automation

  Background:
    Given I am logged in as an administrator using Playwright
    And I am on the user management page using Playwright

  @positive @create
  Scenario: Create a new user
    When I click the "Add New User" button in Playwright
    And I fill in the user creation form with valid data in Playwright:
      | field         | value              |
      | username      | new_test_user      |
      | email         | test@example.com   |
      | first_name    | Test               |
      | last_name     | User               |
      | role          | Standard User      |
    And I click the "Create User" button in Playwright
    Then I should see a success message "User created successfully" in Playwright
    And the new user should appear in the user list in Playwright

  @positive @edit
  Scenario: Edit an existing user
    Given there is an existing user "edit_test_user" in the system
    When I click the edit button for user "edit_test_user" in Playwright
    And I update the user information in Playwright:
      | field      | value                    |
      | email      | updated@example.com      |
      | first_name | Updated                  |
      | role       | Administrator            |
    And I click the "Save Changes" button in Playwright
    Then I should see a success message "User updated successfully" in Playwright
    And the user details should be updated in the user list in Playwright

  @positive @delete
  Scenario: Delete a user
    Given there is an existing user "delete_test_user" in the system
    When I click the delete button for user "delete_test_user" in Playwright
    And I confirm the deletion in the confirmation dialog in Playwright
    Then I should see a success message "User deleted successfully" in Playwright
    And the user should no longer appear in the user list in Playwright

  @positive @search
  Scenario: Search for users
    Given there are multiple users in the system
    When I enter "john" in the search field in Playwright
    And I click the search button in Playwright
    Then I should see only users with "john" in their name or email in Playwright
    And the search results should be highlighted in Playwright

  @positive @filter
  Scenario: Filter users by role
    Given there are users with different roles in the system
    When I select "Administrator" from the role filter dropdown in Playwright
    Then I should see only users with the "Administrator" role in Playwright
    And the filter should show the active selection in Playwright

  @positive @pagination
  Scenario: Navigate through user pages
    Given there are more than 10 users in the system
    When I am on the user management page in Playwright
    Then I should see pagination controls in Playwright
    When I click the "Next" page button in Playwright
    Then I should see the next set of users in Playwright
    And the page number should update accordingly in Playwright

  @negative @validation
  Scenario: Create user with invalid email
    When I click the "Add New User" button in Playwright
    And I fill in the user creation form with invalid email in Playwright:
      | field         | value              |
      | username      | invalid_email_user |
      | email         | invalid-email      |
      | first_name    | Test               |
      | last_name     | User               |
    And I click the "Create User" button in Playwright
    Then I should see an error message "Please enter a valid email address" in Playwright
    And the user should not be created in Playwright

  @negative @duplicate
  Scenario: Create user with duplicate username
    Given there is an existing user "duplicate_user" in the system
    When I click the "Add New User" button in Playwright
    And I fill in the user creation form with duplicate username in Playwright:
      | field      | value              |
      | username   | duplicate_user     |
      | email      | new@example.com    |
      | first_name | Duplicate          |
      | last_name  | User               |
    And I click the "Create User" button in Playwright
    Then I should see an error message "Username already exists" in Playwright
    And the user should not be created in Playwright

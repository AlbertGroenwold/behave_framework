@admin @user_management @web
Feature: User Management
  As an admin user
  I want to manage user accounts
  So that I can control access to the system

  Background:
    Given I am logged in as an admin user
    And I am on the user management page

  @admin @user_management
  Scenario: Create a new user account
    When I click on "Add New User" button
    And I fill in the user details:
      | Field      | Value             |
      | Username   | newuser123        |
      | Email      | newuser@test.com  |
      | First Name | New               |
      | Last Name  | User              |
      | Role       | Standard User     |
    And I click "Save User" button
    Then the user should be created successfully
    And I should see the user in the user list

  @admin @user_management
  Scenario: Edit existing user
    Given there is an existing user "testuser"
    When I click on the edit button for user "testuser"
    And I update the email to "updated@test.com"
    And I click "Save Changes" button
    Then the user details should be updated
    And I should see the updated email in the user list

  @admin @user_management
  Scenario: Delete user account
    Given there is an existing user "userToDelete"
    When I click on the delete button for user "userToDelete"
    And I confirm the deletion
    Then the user should be removed from the system
    And I should not see the user in the user list

  @admin @user_management
  Scenario: Search for user
    Given there are multiple users in the system
    When I enter "john" in the search box
    And I click the search button
    Then I should see only users matching "john"
    And the search results should be highlighted

  @admin @user_management
  Scenario: Activate/Deactivate user account
    Given there is an existing user "activeuser" with status "Active"
    When I click on the status toggle for user "activeuser"
    Then the user status should change to "Inactive"
    And the user should not be able to login

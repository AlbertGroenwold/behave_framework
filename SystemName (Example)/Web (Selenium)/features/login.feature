@login @smoke @web
Feature: User Login
  As a user
  I want to be able to login to the application
  So that I can access my account

  Background:
    Given I am on the login page

  @positive
  Scenario: Successful login with valid credentials
    When I enter username "valid_user" and password "valid_password"
    And I click the login button
    Then I should be redirected to the home page
    And I should see a welcome message

  @negative
  Scenario: Login with invalid credentials
    When I enter username "invalid_user" and password "wrong_password"
    And I click the login button
    Then I should see an error message "Invalid username or password"
    And I should remain on the login page

  @negative
  Scenario: Login with empty username
    When I enter username "" and password "valid_password"
    And I click the login button
    Then I should see an error message "Username is required"

  @negative
  Scenario: Login with empty password
    When I enter username "valid_user" and password ""
    And I click the login button
    Then I should see an error message "Password is required"

  @positive
  Scenario: Remember me functionality
    When I enter username "valid_user" and password "valid_password"
    And I check the remember me checkbox
    And I click the login button
    Then I should be redirected to the home page
    And the remember me option should be selected

  Scenario Outline: Login with different user types
    When I enter username "<username>" and password "<password>"
    And I click the login button
    Then I should see "<expected_result>"

    Examples:
      | username    | password        | expected_result           |
      | admin_user  | admin_password  | Admin Dashboard           |
      | regular_user| user_password   | User Dashboard            |
      | guest_user  | guest_password  | Limited Access Dashboard  |

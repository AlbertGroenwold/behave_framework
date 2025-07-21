@login @smoke @web @playwright
Feature: User Login with Playwright
  As a user
  I want to be able to login to the application using Playwright
  So that I can access my account with modern browser automation

  Background:
    Given I am on the login page using Playwright

  @positive
  Scenario: Successful login with valid credentials
    When I enter username "valid_user" and password "valid_password" in Playwright
    And I click the login button in Playwright
    Then I should be redirected to the home page in Playwright
    And I should see a welcome message in Playwright

  @negative
  Scenario: Login with invalid credentials
    When I enter username "invalid_user" and password "wrong_password" in Playwright
    And I click the login button in Playwright
    Then I should see an error message "Invalid username or password" in Playwright
    And I should remain on the login page in Playwright

  @negative
  Scenario: Login with empty username
    When I enter username "" and password "valid_password" in Playwright
    And I click the login button in Playwright
    Then I should see an error message "Username is required" in Playwright

  @negative
  Scenario: Login with empty password
    When I enter username "valid_user" and password "" in Playwright
    And I click the login button in Playwright
    Then I should see an error message "Password is required" in Playwright

  @positive
  Scenario: Remember me functionality
    When I enter username "valid_user" and password "valid_password" in Playwright
    And I check the remember me checkbox in Playwright
    And I click the login button in Playwright
    Then I should be redirected to the home page in Playwright
    And the remember me option should be selected in Playwright

  @positive @accessibility
  Scenario: Login page accessibility validation
    When I validate the login page accessibility in Playwright
    Then the page should meet WCAG 2.1 AA standards
    And all interactive elements should be keyboard accessible

  @positive @performance
  Scenario: Login page performance validation
    When I measure the login page load time in Playwright
    Then the page should load within 3 seconds
    And the largest contentful paint should be under 2.5 seconds

  Scenario Outline: Login with different user types using Playwright
    When I enter username "<username>" and password "<password>" in Playwright
    And I click the login button in Playwright
    Then I should see "<expected_result>" in Playwright

    Examples:
      | username    | password        | expected_result           |
      | admin_user  | admin_password  | Admin Dashboard           |
      | regular_user| user_password   | User Dashboard            |
      | guest_user  | guest_password  | Limited Access Dashboard  |
      | invalid_user| wrong_password  | Invalid username or password |

@mobile @login @android @ios
Feature: Mobile Application Login
  As a mobile user
  I want to login to the mobile application
  So that I can access my account on my mobile device

  Background:
    Given I have the mobile app installed and running

  @smoke @android
  Scenario: Successful login on Android device
    When I enter mobile username "mobile_user" and password "mobile_pass"
    And I tap the login button
    Then I should be logged into the mobile app
    And I should see the mobile home screen

  @negative @android
  Scenario: Failed login with invalid credentials on Android
    When I enter mobile username "invalid_user" and password "wrong_pass"
    And I tap the login button
    Then I should see a mobile error message
    And I should remain on the mobile login screen

  @smoke @ios
  Scenario: Successful login on iOS device
    When I enter mobile username "mobile_user" and password "mobile_pass"
    And I tap the login button
    Then I should be logged into the mobile app
    And I should see the mobile home screen

  @negative @ios
  Scenario: Failed login with invalid credentials on iOS
    When I enter mobile username "invalid_user" and password "wrong_pass"
    And I tap the login button
    Then I should see a mobile error message
    And I should remain on the mobile login screen

  @smoke @biometric
  Scenario: Login with biometric authentication
    Given biometric authentication is enabled
    When I tap the biometric login button
    And I provide valid biometric authentication
    Then I should be logged into the mobile app
    And I should see the mobile home screen

  @mobile @gestures
  Scenario: Login with gesture navigation
    When I swipe to reveal the login form
    And I enter mobile username "mobile_user" and password "mobile_pass"
    And I tap the login button
    Then I should be logged into the mobile app

  @mobile @orientation
  Scenario: Login in landscape mode
    Given I rotate the device to landscape mode
    When I enter mobile username "mobile_user" and password "mobile_pass"
    And I tap the login button
    Then I should be logged into the mobile app
    And the mobile home screen should be displayed in landscape mode

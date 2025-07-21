@desktop @calculator @notepad @windows
Feature: Desktop Application Testing
  As a QA engineer
  I want to test desktop applications
  So that I can ensure they function correctly on Windows

  Background:
    Given I have desktop applications available

  @calculator @basic_operations
  Scenario: Calculator - Basic arithmetic operations
    Given I launch the calculator application
    When I perform the calculation "5 + 3"
    Then the result should be "8"
    
    When I clear the calculator
    And I perform the calculation "10 - 4"
    Then the result should be "6"
    
    When I clear the calculator
    And I perform the calculation "7 * 6"
    Then the result should be "42"
    
    When I clear the calculator
    And I perform the calculation "15 / 3"
    Then the result should be "5"

  @calculator @decimal_operations
  Scenario: Calculator - Decimal calculations
    Given I launch the calculator application
    When I perform the calculation "2.5 + 3.7"
    Then the result should be "6.2"
    
    When I clear the calculator
    And I perform the calculation "10.5 / 2.1"
    Then the result should be "5"

  @calculator @complex_operations
  Scenario: Calculator - Complex calculations
    Given I launch the calculator application
    When I perform the calculation "2 + 3 * 4"
    Then the result should be "14"
    
    When I clear the calculator
    And I enter the numbers and operations:
      | operation | value |
      | number    | 100   |
      | subtract  | 25    |
      | multiply  | 2     |
      | add       | 10    |
      | equals    |       |
    Then the result should be "160"

  @notepad @text_operations
  Scenario: Notepad - Basic text operations
    Given I launch the notepad application
    When I type the text "Hello, World!"
    Then the text should be displayed in the notepad
    
    When I select all text
    And I copy the text
    And I paste the text
    Then the notepad should contain "Hello, World!Hello, World!"

  @notepad @file_operations
  Scenario: Notepad - File save and open operations
    Given I launch the notepad application
    When I type the text "This is a test file content."
    And I save the file as "test_file.txt"
    Then the file should be saved successfully
    
    When I open the file "test_file.txt"
    Then the file content should be "This is a test file content."

  @window_management
  Scenario: Window management operations
    Given I launch the calculator application
    When I maximize the window
    Then the calculator window should be maximized
    
    When I minimize the window
    Then the calculator window should be minimized
    
    When I restore the window
    Then the calculator window should be restored
    
    When I move the window to position "100, 100"
    Then the calculator window should be at position "100, 100"

  @screenshot_testing
  Scenario: Screenshot and image validation
    Given I launch the calculator application
    When I take a screenshot of the calculator
    Then the screenshot should be saved successfully
    
    When I click on the number "5" button
    And I take a screenshot of the display
    Then the display should show "5"

  @keyboard_shortcuts
  Scenario: Keyboard shortcuts testing
    Given I launch the notepad application
    When I type the text "Test content for shortcuts"
    And I press "Ctrl+A" to select all
    And I press "Ctrl+C" to copy
    And I press "Ctrl+V" to paste
    Then the notepad should contain the duplicated text

  @multi_application
  Scenario: Multi-application interaction
    Given I launch the calculator application
    And I launch the notepad application
    When I switch between applications
    And I perform operations in each application
    Then both applications should maintain their state
    And I should be able to interact with both

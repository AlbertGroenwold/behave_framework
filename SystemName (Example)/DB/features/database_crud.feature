@database @crud @postgresql @mysql @sqlite @mongodb
Feature: Database User Management
  As a database administrator
  I want to test database operations
  So that I can ensure data integrity and performance

  Background:
    Given the database is connected and accessible

  @smoke @database
  Scenario: Create and retrieve user record
    Given I have valid user data:
      | field      | value              |
      | username   | db_test_user       |
      | email      | dbtest@email.com   |
      | first_name | Database           |
      | last_name  | Test               |
      | age        | 25                 |
    When I insert the user data into the users table
    Then the user should be successfully created
    And I should be able to retrieve the user by username
    And the retrieved data should match the inserted data

  @crud @database
  Scenario: Update user information
    Given I have an existing user in the database
    When I update the user's email to "updated_db@email.com"
    And I update the user's age to 30
    Then the user record should be updated successfully
    And the updated fields should have new values
    And the unchanged fields should remain the same

  @crud @database
  Scenario: Delete user record
    Given I have an existing user to delete
    When I delete the user from the database
    Then the user should be removed successfully
    And the user should not be found in subsequent queries

  @validation @database
  Scenario: Validate data constraints
    Given I have user data with invalid email format
    When I attempt to insert the invalid data
    Then the database should reject the operation
    And an appropriate error should be returned

  @performance @database
  Scenario: Query performance validation
    Given the users table has at least 1000 records
    When I execute a query to find users by age range
    Then the query should complete within 500 milliseconds
    And the results should be accurate

  @transaction @database
  Scenario: Transaction rollback testing
    Given I start a database transaction
    When I insert multiple user records
    And I encounter an error during insertion
    Then the transaction should be rolled back
    And no partial data should be committed

  @concurrency @database
  Scenario: Concurrent access testing
    Given multiple database connections are established
    When users are inserted simultaneously from different connections
    Then all insertions should complete successfully
    And data integrity should be maintained

  @backup @database
  Scenario: Data backup and restore
    Given I have a database with test data
    When I create a backup of the database
    And I restore the database from backup
    Then all original data should be preserved
    And the database should function normally

@api @products @crud
Feature: Product Management API
  As an API consumer
  I want to manage products via REST API
  So that I can perform CRUD operations on product data

  Background:
    Given the API is available and accessible

  @smoke @api
  Scenario: Get all products
    When I send a GET request to "/products"
    Then the response status should be 200
    And the response should contain a list of products
    And the response time should be less than 2000 milliseconds

  @smoke @api
  Scenario: Get product by ID
    Given I have a valid product ID
    When I send a GET request to "/products/{product_id}"
    Then the response status should be 200
    And the response should contain product details
    And the product ID should match the requested ID

  @crud @api
  Scenario: Create a new product
    Given I have valid product data:
      | field      | value              |
      | name       | Test Product       |
      | price      | 29.99              |
      | category   | Electronics        |
      | sku        | TEST-001           |
    When I send a POST request to "/products" with the product data
    Then the response status should be 201
    And the response should contain the created product details
    And the product should be created with the provided data

  @crud @api
  Scenario: Update an existing product
    Given I have an existing product
    When I send a PUT request to "/products/{product_id}" with updated data:
      | field      | value                    |
      | name       | Updated Test Product     |
      | price      | 39.99                    |
    Then the response status should be 200
    And the response should contain the updated product details
    And the product data should be updated correctly

  @crud @api
  Scenario: Delete a product
    Given I have an existing product to delete
    When I send a DELETE request to "/products/{product_id}"
    Then the response status should be 204
    And the product should be deleted from the system

  @api @filter
  Scenario: Get products by category
    When I send a GET request to "/products?category=Electronics"
    Then the response status should be 200
    And the response should contain a list of products
    And all products should belong to "Electronics" category

  @api @search
  Scenario: Search products by name
    When I send a GET request to "/products/search?name=Test"
    Then the response status should be 200
    And the response should contain a list of products
    And all products should have "Test" in the name

  @api @validation
  Scenario: Create product with invalid data
    Given I have invalid product data:
      | field      | value    |
      | name       |          |
      | price      | -10      |
    When I send a POST request to "/products" with the product data
    Then the response status should be 400
    And the response should contain validation errors

  @api @security
  Scenario: Access products without authentication
    Given I have no authentication token
    When I send a GET request to "/products"
    Then the response status should be 401
    And the response should contain an authentication error

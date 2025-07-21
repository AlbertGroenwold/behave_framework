# API Page Object Model - Implementation Guide

## Overview

This implementation restructures API testing to follow the **Page Object Model (POM)** pattern, where each API endpoint/resource is treated as a "page object". This approach provides better maintainability, reusability, and follows the same proven patterns used in UI automation.

## Architecture

### Base Classes

#### `BaseAPIPage` (`base/api/base_api_page.py`)
- Abstract base class for all API page objects
- Provides common HTTP operations (GET, POST, PUT, DELETE, PATCH)
- Includes validation methods and response handling
- Implements request/response logging
- Handles timing measurements for performance testing

#### `BaseAPIClient` (`base/api/api_client.py`)
- Low-level HTTP client for making API requests
- Handles authentication (Bearer tokens, API keys, Basic auth)
- Session management and connection pooling
- Custom headers and configuration

### API Page Objects Structure

```
SystemName (Example)/API/
├── pageobjects/
│   ├── __init__.py
│   ├── users_api_page.py          # Users endpoint page object
│   ├── products_api_page.py       # Products endpoint page object
│   └── [other_api]_page.py        # Additional API endpoints
├── features/
│   ├── api_users.feature          # Users API scenarios
│   ├── api_products.feature       # Products API scenarios
│   └── [other_api].feature        # Additional API features
└── steps/
    ├── api_steps.py               # Generic API step definitions
    ├── products_steps.py          # Product-specific steps
    └── [other_api]_steps.py       # Additional API-specific steps
```

## How It Works

### 1. Each API Endpoint = One Page Object

Instead of having generic API calls scattered throughout step definitions, each API resource (like Users, Products, Orders) gets its own page object class:

```python
# Traditional approach (NOT Page Object Model)
@when('I create a user')
def step_create_user(context):
    response = context.api_client.post('/users', json=user_data)
    context.response = response

# Page Object Model approach
@when('I create a user')
def step_create_user(context):
    context.users_api.create_user(user_data)
    # All validation and response handling is in the page object
```

### 2. Validation Built Into Page Objects

Each page object contains validation methods specific to that resource:

```python
class UsersAPIPage(BaseAPIPage):
    def validate_user_created(self, expected_data):
        """Validates user creation with specific business rules"""
        response_data = self.get_response_data()
        self.validate_resource_structure(response_data)
        # Check email format, username length, etc.
```

### 3. Resource-Specific Operations

Page objects provide business-meaningful methods:

```python
# Users API
users_api.get_user_by_email("test@example.com")
users_api.activate_user(user_id)
users_api.change_password(user_id, password_data)

# Products API  
products_api.get_products_by_category("Electronics")
products_api.update_product_stock(product_id, quantity)
products_api.search_products(search_criteria)
```

## Implementation Examples

### Creating a New API Page Object

1. **Create the page object class:**

```python
# SystemName (Example)/API/pageobjects/orders_api_page.py
from api.base_api_page import BaseAPIPage

class OrdersAPIPage(BaseAPIPage):
    def __init__(self, api_client):
        super().__init__(api_client, '/orders')
        self.required_fields = ['customer_id', 'items', 'total']
    
    def validate_resource_structure(self, resource_data):
        # Implement order-specific validation
        for field in self.required_fields:
            if field not in resource_data:
                raise AssertionError(f"Missing field: {field}")
    
    def get_resource_id(self, resource_data):
        return str(resource_data['order_id'])
    
    def create_order(self, order_data):
        return self.create(order_data)
    
    def get_orders_by_customer(self, customer_id):
        return self._make_request('GET', f'/customer/{customer_id}')
```

2. **Create feature file:**

```gherkin
# SystemName (Example)/API/features/api_orders.feature
@api @orders
Feature: Order Management API
  
  Scenario: Create a new order
    Given I have valid order data:
      | field       | value     |
      | customer_id | 123       |
      | total       | 99.99     |
    When I create an order with the order data
    Then the response status should be 201
    And the order should be created successfully
```

3. **Create step definitions:**

```python
# SystemName (Example)/API/steps/orders_steps.py
@when('I create an order with the order data')
def step_create_order(context):
    if not hasattr(context, 'orders_api'):
        context.orders_api = OrdersAPIPage(context.api_client)
    context.orders_api.create_order(context.order_data)

@then('the order should be created successfully')
def step_verify_order_created(context):
    context.orders_api.validate_order_details_response()
```

## Benefits of This Approach

### 1. **Better Organization**
- Each API resource has its own dedicated page object
- Related functionality is grouped together
- Clear separation of concerns

### 2. **Improved Maintainability**
- Changes to API structure only require updates in one page object
- Validation logic is centralized per resource type
- Easier to find and fix issues

### 3. **Enhanced Reusability**
- Page objects can be used across multiple test scenarios
- Common operations are standardized
- Business logic is encapsulated

### 4. **Consistent Pattern**
- Same pattern as UI Page Object Model
- Familiar structure for automation engineers
- Easier onboarding for new team members

### 5. **Better Test Data Management**
- Resource-specific validation
- Type conversion handled in page objects
- Business rules enforced consistently

## Key Features

### Request/Response Handling
- Automatic request logging with details
- Response validation and parsing
- Performance timing measurements
- Error handling and debugging information

### Validation Framework
- Resource structure validation
- Business rule enforcement
- Response time validation
- Status code verification

### Authentication Support
- Bearer token authentication
- API key authentication  
- Basic authentication
- Custom header support

### Advanced Operations
- Pagination support
- Filtering and searching
- Partial updates (PATCH)
- Custom endpoint support

## Usage in Test Scenarios

### Setup in Background
```python
@given('the API is available and accessible')
def step_api_available(context):
    context.api_client = BaseAPIClient()
    context.users_api = UsersAPIPage(context.api_client)
    context.products_api = ProductsAPIPage(context.api_client)
```

### Using Multiple APIs in One Scenario
```python
@when('I create a user and a product')
def step_create_user_and_product(context):
    # Create user
    context.users_api.create_user(context.user_data)
    user_id = context.users_api.get_created_user_id()
    
    # Create product with user as owner
    product_data = dict(context.product_data)
    product_data['owner_id'] = user_id
    context.products_api.create_product(product_data)
```

### Cross-Resource Validation
```python
@then('the user should own the product')
def step_verify_user_owns_product(context):
    user_id = context.users_api.get_created_user_id()
    product = context.products_api.get_response_data()
    assert product['owner_id'] == user_id
```

## Best Practices

1. **One page object per API resource/endpoint group**
2. **Include resource-specific validation in each page object**
3. **Use meaningful method names that reflect business operations**
4. **Handle data type conversions in page objects**
5. **Provide both basic CRUD and advanced operations**
6. **Include proper error handling and logging**
7. **Use inheritance to avoid code duplication**
8. **Keep step definitions thin - business logic goes in page objects**

This approach scales well as you add more API endpoints and provides a consistent, maintainable framework for API testing.

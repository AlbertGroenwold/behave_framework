# Database Testing with Page Object Model - Implementation Guide

## 🎯 Overview

This implementation applies the **Page Object Model (POM)** pattern to database testing, where each database entity or table is treated as a "page object". This approach provides better maintainability, reusability, and follows proven patterns used in UI automation, adapted for database operations.

## 🏗️ Architecture

### Base Classes

#### `BaseDatabaseManager` (`base/database/base_database_manager.py`)
- Abstract base class for all database connection managers
- Provides common database operations (CRUD, transaction management)
- Includes connection pooling and error handling
- Implements query logging and performance monitoring

#### Database-Specific Managers (`base/database/`)
- **PostgreSQLManager** - PostgreSQL database operations
- **MySQLManager** - MySQL/MariaDB database operations
- **SQLiteManager** - SQLite database operations (ideal for testing)
- **MongoDBManager** - MongoDB NoSQL operations
- **RedisManager** - Redis key-value store operations

### Database Page Objects Structure

```
SystemName (Example)/DB/
├── pageobjects/
│   ├── __init__.py
│   ├── users_db_page.py           # Users table page object
│   ├── products_db_page.py        # Products table page object
│   ├── orders_db_page.py          # Orders table page object
│   └── [entity]_db_page.py        # Additional entity page objects
├── features/
│   ├── database_crud.feature      # CRUD operations scenarios
│   ├── data_validation.feature    # Data integrity scenarios
│   ├── performance.feature        # Database performance scenarios
│   └── migration.feature          # Database migration scenarios
├── steps/
│   ├── database_steps.py          # Generic database step definitions
│   ├── users_db_steps.py          # User-specific database steps
│   └── [entity]_db_steps.py       # Additional entity-specific steps
└── environment.py                 # Database test setup and teardown
```

## 🔧 How It Works

### 1. Each Database Entity = One Page Object

Instead of having generic database queries scattered throughout step definitions, each database entity (table, collection, or logical grouping) gets its own page object class:

```python
# Traditional approach (NOT Page Object Model)
@when('I create a user in the database')
def step_create_user(context):
    query = "INSERT INTO users (username, email) VALUES (?, ?)"
    context.db_connection.execute(query, (username, email))

# Page Object Model approach
@when('I create a user in the database')
def step_create_user(context):
    context.users_db.create_user(context.user_data)
    # All query construction and validation is in the page object
```

### 2. Data Validation Built Into Page Objects

Each page object contains validation methods specific to that entity:

```python
class UsersDBPage(BaseDatabasePage):
    def validate_user_exists(self, user_id):
        """Validates user exists with specific business rules"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise AssertionError(f"User with ID {user_id} not found")
        self.validate_user_data_integrity(user)
```

### 3. Entity-Specific Operations

Page objects provide business-meaningful methods:

```python
# Users Database Operations
users_db.create_user(user_data)
users_db.get_user_by_email("test@example.com")
users_db.activate_user(user_id)
users_db.soft_delete_user(user_id)

# Products Database Operations  
products_db.create_product(product_data)
products_db.update_stock_quantity(product_id, quantity)
products_db.get_products_by_category("Electronics")
products_db.archive_discontinued_products()

# Orders Database Operations
orders_db.create_order(order_data)
orders_db.get_orders_by_customer(customer_id)
orders_db.update_order_status(order_id, "shipped")
orders_db.calculate_total_revenue_by_date_range(start_date, end_date)
```

## 🚀 Implementation Examples

### Creating a New Database Page Object

1. **Create the page object class:**

```python
# SystemName (Example)/DB/pageobjects/products_db_page.py
from base.database.base_database_manager import BaseDatabaseManager

class ProductsDBPage:
    def __init__(self, db_manager):
        self.db = db_manager
        self.table_name = 'products'
        self.required_fields = ['name', 'price', 'category_id']
    
    def create_product(self, product_data):
        """Create a new product with validation"""
        self._validate_product_data(product_data)
        
        query = """
        INSERT INTO products (name, description, price, category_id, stock_quantity)
        VALUES (%(name)s, %(description)s, %(price)s, %(category_id)s, %(stock_quantity)s)
        RETURNING product_id
        """
        
        result = self.db.execute_query(query, product_data)
        product_id = result[0]['product_id']
        
        # Log the operation
        self.db.log_operation('CREATE', 'products', product_id, product_data)
        return product_id
    
    def get_product_by_id(self, product_id):
        """Retrieve product by ID with error handling"""
        query = "SELECT * FROM products WHERE product_id = %(product_id)s"
        result = self.db.execute_query(query, {'product_id': product_id})
        
        if not result:
            raise AssertionError(f"Product with ID {product_id} not found")
        
        return result[0]
    
    def update_stock_quantity(self, product_id, new_quantity):
        """Update product stock with business logic"""
        if new_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        query = """
        UPDATE products 
        SET stock_quantity = %(quantity)s, 
            updated_at = CURRENT_TIMESTAMP 
        WHERE product_id = %(product_id)s
        """
        
        affected_rows = self.db.execute_update(query, {
            'product_id': product_id,
            'quantity': new_quantity
        })
        
        if affected_rows == 0:
            raise AssertionError(f"No product found with ID {product_id}")
        
        return affected_rows
    
    def get_products_by_category(self, category_name):
        """Get all products in a specific category"""
        query = """
        SELECT p.*, c.category_name 
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE c.category_name = %(category_name)s
        AND p.is_active = true
        ORDER BY p.name
        """
        
        return self.db.execute_query(query, {'category_name': category_name})
    
    def _validate_product_data(self, product_data):
        """Validate product data according to business rules"""
        for field in self.required_fields:
            if field not in product_data:
                raise AssertionError(f"Missing required field: {field}")
        
        if product_data.get('price', 0) <= 0:
            raise ValueError("Product price must be greater than 0")
        
        if len(product_data.get('name', '')) < 3:
            raise ValueError("Product name must be at least 3 characters long")
    
    def validate_product_data_integrity(self, product_data):
        """Validate database-retrieved product data integrity"""
        expected_fields = ['product_id', 'name', 'price', 'category_id', 'created_at']
        for field in expected_fields:
            if field not in product_data:
                raise AssertionError(f"Product data missing field: {field}")
    
    def cleanup_test_products(self, test_prefix="TEST_"):
        """Clean up test data - useful for test teardown"""
        query = "DELETE FROM products WHERE name LIKE %(prefix)s"
        return self.db.execute_update(query, {'prefix': f'{test_prefix}%'})
```

2. **Create feature file:**

```gherkin
# SystemName (Example)/DB/features/products_database.feature
@database @products @crud
Feature: Products Database Management
  As a system administrator
  I want to manage products in the database
  So that the application can handle product information correctly

  Background:
    Given the database is available and accessible
    And I have a clean products test environment

  @smoke
  Scenario: Create a new product
    Given I have valid product data:
      | field        | value                |
      | name         | TEST_Laptop_Pro      |
      | description  | High-performance laptop |
      | price        | 1299.99              |
      | category_id  | 1                    |
      | stock_quantity | 50                 |
    When I create a product in the database
    Then the product should be created successfully
    And the product should have a valid product ID
    And the product data should match the input data

  @validation
  Scenario: Validate product data integrity
    Given I have a product with ID 1 in the database
    When I retrieve the product from the database
    Then the product data should have all required fields
    And the product data should pass integrity validation

  @business_logic
  Scenario: Update product stock quantity
    Given I have a product with ID 1 in the database
    And the product has an initial stock quantity of 100
    When I update the stock quantity to 75
    Then the product stock should be updated successfully
    And the updated_at timestamp should be current

  @error_handling
  Scenario: Handle invalid stock quantity
    Given I have a product with ID 1 in the database
    When I attempt to update the stock quantity to -10
    Then I should receive a validation error
    And the stock quantity should remain unchanged

  @data_cleanup
  Scenario: Clean up test data
    Given I have test products in the database
    When I clean up products with TEST_ prefix
    Then all test products should be removed
    And no non-test products should be affected
```

3. **Create step definitions:**

```python
# SystemName (Example)/DB/steps/products_db_steps.py
from behave import given, when, then
from pageobjects.products_db_page import ProductsDBPage

@given('I have a clean products test environment')
def step_clean_products_environment(context):
    """Ensure clean test environment"""
    if not hasattr(context, 'products_db'):
        context.products_db = ProductsDBPage(context.db_manager)
    
    # Clean up any existing test data
    context.products_db.cleanup_test_products()

@when('I create a product in the database')
def step_create_product(context):
    """Create product using page object"""
    context.created_product_id = context.products_db.create_product(context.product_data)

@then('the product should be created successfully')
def step_verify_product_created(context):
    """Verify product creation"""
    assert context.created_product_id is not None
    assert isinstance(context.created_product_id, int)

@then('the product should have a valid product ID')
def step_verify_product_id(context):
    """Verify product ID is valid"""
    product = context.products_db.get_product_by_id(context.created_product_id)
    assert product['product_id'] == context.created_product_id

@then('the product data should match the input data')
def step_verify_product_data(context):
    """Verify stored data matches input"""
    product = context.products_db.get_product_by_id(context.created_product_id)
    
    for key, value in context.product_data.items():
        if key in product:
            assert product[key] == value, f"Expected {key}={value}, got {product[key]}"

@when('I update the stock quantity to {quantity:d}')
def step_update_stock_quantity(context, quantity):
    """Update product stock quantity"""
    context.products_db.update_stock_quantity(context.product_id, quantity)

@then('the product stock should be updated successfully')
def step_verify_stock_updated(context):
    """Verify stock quantity was updated"""
    product = context.products_db.get_product_by_id(context.product_id)
    # Verification logic will depend on the specific quantity set in the scenario
    assert 'updated_at' in product
    assert product['updated_at'] is not None
```

## 🎁 Benefits of This Approach

### 1. **Better Organization**
- Each database entity has its own dedicated page object
- Related database operations are grouped together
- Clear separation between data access and business logic

### 2. **Improved Maintainability**
- Database schema changes only require updates in one page object
- Query optimization can be done in one place
- Easier to find and fix database-related issues

### 3. **Enhanced Reusability**
- Page objects can be used across multiple test scenarios
- Common database operations are standardized
- Business logic is encapsulated and reusable

### 4. **Consistent Testing Pattern**
- Same pattern as UI Page Object Model
- Familiar structure for automation engineers
- Easier onboarding for new team members

### 5. **Better Data Management**
- Entity-specific validation and business rules
- Centralized data cleanup and management
- Type-safe database operations

## 🔧 Key Features

### Multi-Database Support
```python
# PostgreSQL
postgres_manager = PostgreSQLManager(connection_string)
users_db = UsersDBPage(postgres_manager)

# MySQL
mysql_manager = MySQLManager(host, database, user, password)
products_db = ProductsDBPage(mysql_manager)

# SQLite (ideal for testing)
sqlite_manager = SQLiteManager(database_file)
orders_db = OrdersDBPage(sqlite_manager)

# MongoDB
mongo_manager = MongoDBManager(connection_string)
logs_db = LogsDBPage(mongo_manager)

# Redis
redis_manager = RedisManager(host, port, password)
cache_db = CacheDBPage(redis_manager)
```

### Transaction Management
```python
@when('I perform multiple database operations')
def step_multiple_operations(context):
    """Perform multiple operations in a transaction"""
    with context.db_manager.transaction():
        user_id = context.users_db.create_user(context.user_data)
        context.orders_db.create_order({
            'user_id': user_id,
            'items': context.order_items
        })
        # If any operation fails, all are rolled back
```

### Performance Monitoring
```python
@then('the database operation should complete within {seconds:d} seconds')
def step_verify_performance(context, seconds):
    """Verify database operation performance"""
    last_operation_time = context.db_manager.get_last_operation_time()
    assert last_operation_time <= seconds, f"Operation took {last_operation_time}s, expected <={seconds}s"
```

### Data Validation Framework
```python
class UsersDBPage:
    def validate_user_business_rules(self, user_data):
        """Validate user data against business rules"""
        # Email format validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_data['email']):
            raise ValueError("Invalid email format")
        
        # Username length validation
        if len(user_data['username']) < 3:
            raise ValueError("Username must be at least 3 characters")
        
        # Age validation
        if user_data.get('age', 0) < 18:
            raise ValueError("User must be at least 18 years old")
```

## 🎯 Usage in Test Scenarios

### Setup in Environment
```python
# SystemName (Example)/DB/environment.py
from base.database.sqlite_manager import SQLiteManager
from pageobjects.users_db_page import UsersDBPage
from pageobjects.products_db_page import ProductsDBPage

def before_all(context):
    """Setup database connection and page objects"""
    context.db_manager = SQLiteManager(':memory:')  # In-memory for testing
    context.db_manager.setup_test_schema()
    
    # Initialize page objects
    context.users_db = UsersDBPage(context.db_manager)
    context.products_db = ProductsDBPage(context.db_manager)

def after_all(context):
    """Cleanup database resources"""
    context.db_manager.close_connection()
```

### Cross-Entity Operations
```python
@when('I create a user and their first order')
def step_create_user_and_order(context):
    """Create user and order in sequence"""
    # Create user first
    user_id = context.users_db.create_user(context.user_data)
    
    # Create order for the user
    order_data = dict(context.order_data)
    order_data['user_id'] = user_id
    context.order_id = context.orders_db.create_order(order_data)

@then('the user should have one order')
def step_verify_user_has_order(context):
    """Verify relationship between user and order"""
    user_orders = context.orders_db.get_orders_by_user_id(context.user_id)
    assert len(user_orders) == 1
    assert user_orders[0]['order_id'] == context.order_id
```

### Data Migration Testing
```python
@given('I have legacy data in the old format')
def step_setup_legacy_data(context):
    """Setup legacy data for migration testing"""
    context.legacy_db.insert_legacy_user_data(context.legacy_users)

@when('I run the data migration script')
def step_run_migration(context):
    """Execute data migration"""
    context.migration_result = context.db_manager.run_migration_script('migrate_users_v2.sql')

@then('the data should be migrated to the new format')
def step_verify_migration(context):
    """Verify data migration success"""
    migrated_users = context.users_db.get_all_users()
    for user in migrated_users:
        context.users_db.validate_user_data_integrity(user)
        # Verify new fields exist
        assert 'migrated_at' in user
        assert user['version'] == 2
```

## 📝 Best Practices

1. **One page object per database entity or logical grouping**
2. **Include entity-specific validation in each page object**
3. **Use meaningful method names that reflect business operations**
4. **Handle database connections and transactions properly**
5. **Provide both basic CRUD and advanced query operations**
6. **Include proper error handling and logging**
7. **Use inheritance to avoid code duplication**
8. **Implement proper test data cleanup**
9. **Keep step definitions thin - business logic goes in page objects**
10. **Use transactions for data consistency in tests**

## 🔧 Configuration

### Database Connection Configuration
```python
# Environment-based configuration
import os

DATABASE_CONFIG = {
    'postgresql': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'test_db'),
        'user': os.getenv('DB_USER', 'test_user'),
        'password': os.getenv('DB_PASSWORD', 'test_password'),
        'port': int(os.getenv('DB_PORT', 5432))
    },
    'mysql': {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'database': os.getenv('MYSQL_DB', 'test_db'),
        'user': os.getenv('MYSQL_USER', 'test_user'),
        'password': os.getenv('MYSQL_PASSWORD', 'test_password'),
        'port': int(os.getenv('MYSQL_PORT', 3306))
    },
    'sqlite': {
        'database': os.getenv('SQLITE_DB', ':memory:')
    }
}
```

### Test Data Management
```python
# Test data generation and cleanup
class TestDataManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.created_records = []
    
    def create_test_user(self, **overrides):
        """Create test user with default values"""
        default_data = {
            'username': f'test_user_{int(time.time())}',
            'email': f'test{int(time.time())}@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        default_data.update(overrides)
        
        user_id = self.users_db.create_user(default_data)
        self.created_records.append(('users', user_id))
        return user_id
    
    def cleanup_all_test_data(self):
        """Clean up all created test data"""
        for table, record_id in reversed(self.created_records):
            if table == 'users':
                self.users_db.delete_user(record_id)
            elif table == 'products':
                self.products_db.delete_product(record_id)
        self.created_records.clear()
```

This approach scales well as you add more database entities and provides a consistent, maintainable framework for database testing that follows the same proven patterns used in UI automation.

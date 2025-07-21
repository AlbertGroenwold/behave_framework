from behave import given, when, then
import sys
import os

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from api.api_client import BaseAPIClient
from ..pageobjects.products_api_page import ProductsAPIPage


# GIVEN STEPS for Products

@given('I have a valid product ID')
def step_have_valid_product_id(context):
    """Setup a valid product ID for testing"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    context.products_api.get_all_products()
    if context.products_api.get_response_status() == 200:
        products = context.products_api.get_response_data()
        if products:
            context.product_id = context.products_api.get_resource_id(products[0])
        else:
            context.product_id = "1"  # Default test product ID
    else:
        context.product_id = "1"  # Default test product ID


@given('I have valid product data')
def step_have_valid_product_data(context):
    """Setup valid product data from table"""
    context.product_data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        # Convert price to float if it's the price field
        if field == 'price':
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string if conversion fails
        context.product_data[field] = value


@given('I have invalid product data')
def step_have_invalid_product_data(context):
    """Setup invalid product data from table"""
    context.product_data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        # Convert price to float if it's the price field and not empty
        if field == 'price' and value.strip():
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string if conversion fails
        context.product_data[field] = value


@given('I have an existing product')
def step_have_existing_product(context):
    """Create or ensure existing product for testing"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    # Create a test product
    test_product_data = {
        'name': 'Existing Test Product',
        'price': 25.99,
        'category': 'Test Category',
        'sku': 'EXIST-001'
    }
    
    context.products_api.create_product(test_product_data)
    if context.products_api.get_response_status() == 201:
        context.existing_product = context.products_api.get_response_data()
        context.product_id = context.products_api.get_resource_id(context.existing_product)
    else:
        # Product might already exist, try to find them
        context.products_api.get_all_products()
        if context.products_api.get_response_status() == 200:
            products = context.products_api.get_response_data()
            if products:
                context.existing_product = products[0]
                context.product_id = context.products_api.get_resource_id(context.existing_product)


@given('I have an existing product to delete')
def step_have_existing_product_to_delete(context):
    """Create a product specifically for deletion testing"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    # Create a test product for deletion
    test_product_data = {
        'name': 'Delete Test Product',
        'price': 19.99,
        'category': 'Test Category',
        'sku': 'DELETE-001'
    }
    
    context.products_api.create_product(test_product_data)
    if context.products_api.get_response_status() == 201:
        context.delete_product = context.products_api.get_response_data()
        context.product_id = context.products_api.get_resource_id(context.delete_product)


# WHEN STEPS for Products (extending existing patterns)

@when('I send a GET request to "/products"')
def step_send_get_products_request(context):
    """Send GET request to get all products"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    context.products_api.get_all_products()


@when('I send a GET request to "/products/{product_id}"')
def step_send_get_product_by_id_request(context):
    """Send GET request to get product by ID"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    context.products_api.get_product_by_id(context.product_id)


@when('I send a POST request to "/products" with the product data')
def step_send_post_products_request(context):
    """Send POST request to create product"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    context.products_api.create_product(context.product_data)


@when('I send a PUT request to "/products/{product_id}" with updated data')
def step_send_put_products_request(context):
    """Send PUT request to update product"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    # Get updated data from table
    updated_data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        # Convert price to float if it's the price field
        if field == 'price':
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string if conversion fails
        updated_data[field] = value
    
    context.products_api.update_product(context.product_id, updated_data)


@when('I send a DELETE request to "/products/{product_id}"')
def step_send_delete_products_request(context):
    """Send DELETE request to delete product"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    context.products_api.delete_product(context.product_id)


@when('I send a GET request to "/products?category={category}"')
def step_send_get_products_by_category_request(context, category):
    """Send GET request to get products by category"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    context.products_api.get_products_by_category(category)
    context.expected_category = category


@when('I send a GET request to "/products/search?name={name}"')
def step_send_get_products_search_request(context, name):
    """Send GET request to search products by name"""
    if not hasattr(context, 'products_api'):
        context.api_client = BaseAPIClient()
        context.products_api = ProductsAPIPage(context.api_client)
    
    search_criteria = {'name': name}
    context.products_api.search_products(search_criteria)
    context.expected_name_filter = name


# THEN STEPS for Products

@then('the response should contain a list of products')
def step_verify_response_contains_product_list(context):
    """Verify response contains a list of products"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        context.products_api.validate_product_list_response()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, list), "Response should be a list"
        
        if response_data:  # If list is not empty
            # Verify each item has product properties
            for product in response_data:
                assert 'id' in product, "Product should have an ID"
                assert 'name' in product, "Product should have a name"


@then('the response should contain product details')
def step_verify_response_contains_product_details(context):
    """Verify response contains product details"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        context.products_api.validate_product_details_response()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, dict), "Response should be a dictionary"
        assert 'id' in response_data, "Product should have an ID"
        assert 'name' in response_data, "Product should have a name"
        assert 'price' in response_data, "Product should have a price"


@then('the product ID should match the requested ID')
def step_verify_product_id_matches(context):
    """Verify product ID matches the requested ID"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        context.products_api.validate_product_id_matches(context.product_id)
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        actual_product_id = str(response_data.get('id'))
        assert actual_product_id == str(context.product_id), \
            f"Product ID mismatch: expected '{context.product_id}', got '{actual_product_id}'"


@then('the response should contain the created product details')
def step_verify_created_product_details(context):
    """Verify response contains created product details"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        context.products_api.validate_product_details_response()
        # Store the created product ID for future use
        context.product_id = context.products_api.get_created_product_id()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, dict), "Response should be a dictionary"
        assert 'id' in response_data, "Created product should have an ID"
        context.product_id = response_data.get('id')


@then('the product should be created with the provided data')
def step_verify_product_created_with_data(context):
    """Verify product was created with provided data"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        context.products_api.validate_product_created(context.product_data)
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        for field, expected_value in context.product_data.items():
            if field in response_data:
                actual_value = response_data[field]
                assert actual_value == expected_value, \
                    f"Product field '{field}': expected '{expected_value}', got '{actual_value}'"


@then('the response should contain the updated product details')
def step_verify_updated_product_details(context):
    """Verify response contains updated product details"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        context.products_api.validate_product_details_response()
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        assert isinstance(response_data, dict), "Response should be a dictionary"
        assert 'id' in response_data, "Updated product should have an ID"


@then('the product data should be updated correctly')
def step_verify_product_updated_correctly(context):
    """Verify product data was updated correctly"""
    # Get updated data from table
    updated_data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        # Convert price to float if it's the price field
        if field == 'price':
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string if conversion fails
        updated_data[field] = value
    
    if hasattr(context, 'products_api') and context.products_api.last_response:
        context.products_api.validate_product_updated(updated_data)
    else:
        # Fallback for direct API client calls
        response_data = context.response.json()
        for field, expected_value in updated_data.items():
            if field in response_data:
                actual_value = response_data[field]
                assert actual_value == expected_value, \
                    f"Updated product field '{field}': expected '{expected_value}', got '{actual_value}'"


@then('the product should be deleted from the system')
def step_verify_product_deleted(context):
    """Verify product was deleted from system"""
    if hasattr(context, 'products_api'):
        # Try to get the deleted product - should return 404
        context.products_api.get_product_by_id(context.product_id)
        # Expect 404 status for deleted product
        assert context.products_api.get_response_status() == 404, "Deleted product should not be found"
    else:
        # Fallback for direct API client calls
        get_response = context.api_client.get(f'/products/{context.product_id}')
        assert get_response.status_code == 404, "Deleted product should not be found"


@then('all products should belong to "{category}" category')
def step_verify_all_products_category(context, category):
    """Verify all products in response belong to specified category"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        products = context.products_api.get_response_data()
        for product in products:
            assert product.get('category') == category, \
                f"Product {product.get('id')} has category '{product.get('category')}', expected '{category}'"
    else:
        # Fallback for direct API client calls
        products = context.response.json()
        for product in products:
            assert product.get('category') == category, \
                f"Product {product.get('id')} has category '{product.get('category')}', expected '{category}'"


@then('all products should have "{name_filter}" in the name')
def step_verify_all_products_name_filter(context, name_filter):
    """Verify all products in response have the specified text in their name"""
    if hasattr(context, 'products_api') and context.products_api.last_response:
        products = context.products_api.get_response_data()
        for product in products:
            product_name = product.get('name', '').lower()
            assert name_filter.lower() in product_name, \
                f"Product {product.get('id')} name '{product.get('name')}' does not contain '{name_filter}'"
    else:
        # Fallback for direct API client calls
        products = context.response.json()
        for product in products:
            product_name = product.get('name', '').lower()
            assert name_filter.lower() in product_name, \
                f"Product {product.get('id')} name '{product.get('name')}' does not contain '{name_filter}'"

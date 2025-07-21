import sys
import os
from typing import Dict, Any, List, Optional

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from api.base_api_page import BaseAPIPage
from api.api_client import BaseAPIClient


class ProductsAPIPage(BaseAPIPage):
    """
    Page Object for Products API endpoints following the Page Object Model pattern.
    Handles all product-related API operations and validations.
    """
    
    def __init__(self, api_client: BaseAPIClient):
        """Initialize Products API page object"""
        super().__init__(api_client, '/products')
        self.required_fields = ['name', 'price', 'category']
        self.optional_fields = ['id', 'description', 'sku', 'stock_quantity', 'created_at', 'updated_at', 'is_active']
    
    def validate_resource_structure(self, resource_data: Dict[str, Any]):
        """
        Validate that a product resource has the expected structure/fields
        
        Args:
            resource_data: Product data to validate
            
        Raises:
            AssertionError: If validation fails
        """
        if not isinstance(resource_data, dict):
            raise AssertionError("Product data must be a dictionary")
        
        # Check required fields
        for field in self.required_fields:
            if field not in resource_data:
                raise AssertionError(f"Required field '{field}' is missing from product data")
        
        # Validate specific field types and formats
        if 'price' in resource_data:
            price = resource_data['price']
            if not isinstance(price, (int, float)) or price < 0:
                raise AssertionError(f"Invalid price: {price}. Price must be a positive number")
        
        if 'name' in resource_data:
            name = resource_data['name']
            if not isinstance(name, str) or len(name.strip()) == 0:
                raise AssertionError(f"Product name must be a non-empty string: {name}")
        
        if 'stock_quantity' in resource_data:
            stock = resource_data['stock_quantity']
            if not isinstance(stock, int) or stock < 0:
                raise AssertionError(f"Stock quantity must be a non-negative integer: {stock}")
    
    def get_resource_id(self, resource_data: Dict[str, Any]) -> str:
        """
        Extract the product ID from product data
        
        Args:
            resource_data: Product data
            
        Returns:
            Product ID as string
            
        Raises:
            AssertionError: If ID is not found
        """
        if 'id' not in resource_data:
            raise AssertionError("Product data does not contain 'id' field")
        
        return str(resource_data['id'])
    
    # Specific product operations
    
    def get_all_products(self, category: Optional[str] = None, 
                        page: Optional[int] = None, 
                        limit: Optional[int] = None,
                        sort_by: Optional[str] = None):
        """
        Get all products with optional filtering and pagination
        
        Args:
            category: Filter by category
            page: Page number for pagination
            limit: Number of products per page
            sort_by: Field to sort by (e.g., 'name', 'price', 'created_at')
            
        Returns:
            Response object
        """
        params = {}
        if category:
            params['category'] = category
        if page is not None:
            params['page'] = page
        if limit is not None:
            params['limit'] = limit
        if sort_by:
            params['sort_by'] = sort_by
        
        return self.get_all(params=params if params else None)
    
    def get_product_by_id(self, product_id: str):
        """
        Get product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Response object
        """
        return self.get_by_id(product_id)
    
    def create_product(self, product_data: Dict[str, Any]):
        """
        Create a new product
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Response object
        """
        # Validate required fields before sending request
        for field in self.required_fields:
            if field not in product_data:
                raise ValueError(f"Required field '{field}' is missing from product data")
        
        return self.create(product_data)
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]):
        """
        Update existing product (full update)
        
        Args:
            product_id: Product ID
            product_data: Complete product data dictionary
            
        Returns:
            Response object
        """
        return self.update(product_id, product_data)
    
    def update_product_partial(self, product_id: str, product_data: Dict[str, Any]):
        """
        Partially update existing product
        
        Args:
            product_id: Product ID
            product_data: Partial product data dictionary
            
        Returns:
            Response object
        """
        return self.partial_update(product_id, product_data)
    
    def delete_product(self, product_id: str):
        """
        Delete product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Response object
        """
        return self.delete(product_id)
    
    def search_products(self, search_criteria: Dict[str, Any]):
        """
        Search products by criteria
        
        Args:
            search_criteria: Search parameters (name, category, price_range, etc.)
            
        Returns:
            Response object
        """
        return self._make_request('GET', '/search', params=search_criteria)
    
    def get_products_by_category(self, category: str):
        """
        Get products by category
        
        Args:
            category: Category name
            
        Returns:
            Response object
        """
        return self._make_request('GET', f'/category/{category}')
    
    def get_product_by_sku(self, sku: str):
        """
        Get product by SKU
        
        Args:
            sku: Product SKU
            
        Returns:
            Response object
        """
        return self._make_request('GET', f'/sku/{sku}')
    
    def update_product_stock(self, product_id: str, stock_quantity: int):
        """
        Update product stock quantity
        
        Args:
            product_id: Product ID
            stock_quantity: New stock quantity
            
        Returns:
            Response object
        """
        stock_data = {'stock_quantity': stock_quantity}
        return self._make_request('PATCH', f'/{product_id}/stock', json=stock_data)
    
    def update_product_price(self, product_id: str, new_price: float):
        """
        Update product price
        
        Args:
            product_id: Product ID
            new_price: New price
            
        Returns:
            Response object
        """
        price_data = {'price': new_price}
        return self._make_request('PATCH', f'/{product_id}/price', json=price_data)
    
    def activate_product(self, product_id: str):
        """
        Activate product (make it available for purchase)
        
        Args:
            product_id: Product ID
            
        Returns:
            Response object
        """
        return self._make_request('POST', f'/{product_id}/activate')
    
    def deactivate_product(self, product_id: str):
        """
        Deactivate product (make it unavailable for purchase)
        
        Args:
            product_id: Product ID
            
        Returns:
            Response object
        """
        return self._make_request('POST', f'/{product_id}/deactivate')
    
    # Validation methods specific to products
    
    def validate_product_list_response(self):
        """Validate that response contains a list of products"""
        self.validate_response_is_list()
        
        # Validate each product in the list
        response_data = self.get_response_data()
        for product in response_data:
            self.validate_resource_structure(product)
    
    def validate_product_details_response(self):
        """Validate that response contains product details"""
        response_data = self.get_response_data()
        self.validate_resource_structure(response_data)
    
    def validate_product_created(self, expected_data: Dict[str, Any]):
        """
        Validate that product was created with expected data
        
        Args:
            expected_data: Expected product data
        """
        response_data = self.get_response_data()
        self.validate_resource_structure(response_data)
        
        # Check that expected fields match
        for field, expected_value in expected_data.items():
            if field in response_data:
                actual_value = response_data[field]
                # Handle price comparison with tolerance for float precision
                if field == 'price' and isinstance(expected_value, (int, float)):
                    assert abs(actual_value - expected_value) < 0.01, \
                        f"Product price '{field}': expected '{expected_value}', got '{actual_value}'"
                else:
                    assert actual_value == expected_value, \
                        f"Product field '{field}': expected '{expected_value}', got '{actual_value}'"
    
    def validate_product_updated(self, expected_data: Dict[str, Any]):
        """
        Validate that product was updated with expected data
        
        Args:
            expected_data: Expected updated product data
        """
        self.validate_product_created(expected_data)  # Same validation logic
    
    def validate_product_id_matches(self, expected_product_id: str):
        """
        Validate that the response product ID matches expected ID
        
        Args:
            expected_product_id: Expected product ID
        """
        response_data = self.get_response_data()
        actual_product_id = self.get_resource_id(response_data)
        
        assert actual_product_id == str(expected_product_id), \
            f"Product ID mismatch: expected '{expected_product_id}', got '{actual_product_id}'"
    
    def get_created_product_id(self) -> str:
        """
        Get the ID of the product from the last response
        
        Returns:
            Product ID as string
        """
        response_data = self.get_response_data()
        return self.get_resource_id(response_data)
    
    def get_all_product_ids(self) -> List[str]:
        """
        Get all product IDs from a list response
        
        Returns:
            List of product IDs as strings
        """
        response_data = self.get_response_data()
        if not isinstance(response_data, list):
            raise AssertionError("Response is not a list of products")
        
        return [self.get_resource_id(product) for product in response_data]
    
    def validate_product_category(self, expected_category: str):
        """
        Validate that the product belongs to the expected category
        
        Args:
            expected_category: Expected category name
        """
        response_data = self.get_response_data()
        actual_category = response_data.get('category')
        
        assert actual_category == expected_category, \
            f"Product category mismatch: expected '{expected_category}', got '{actual_category}'"
    
    def validate_product_price_range(self, min_price: float, max_price: float):
        """
        Validate that the product price is within the expected range
        
        Args:
            min_price: Minimum expected price
            max_price: Maximum expected price
        """
        response_data = self.get_response_data()
        actual_price = response_data.get('price')
        
        assert min_price <= actual_price <= max_price, \
            f"Product price {actual_price} is not within range [{min_price}, {max_price}]"

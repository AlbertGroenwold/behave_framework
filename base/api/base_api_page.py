from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import logging
from .api_client import BaseAPIClient


class BaseAPIPage(ABC):
    """
    Base class for API page objects following the Page Object Model pattern.
    Each API endpoint should inherit from this class and implement specific methods.
    """
    
    def __init__(self, api_client: BaseAPIClient, base_endpoint: str):
        """
        Initialize the API page object
        
        Args:
            api_client: Instance of BaseAPIClient
            base_endpoint: Base endpoint path for this API resource (e.g., '/users', '/products')
        """
        self.api_client = api_client
        self.base_endpoint = base_endpoint.rstrip('/')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_response = None
        self.last_request_time = None
    
    def _log_request(self, method: str, endpoint: str, **kwargs):
        """Log the request details"""
        self.logger.info(f"{method.upper()} request to: {endpoint}")
        if 'json' in kwargs:
            self.logger.debug(f"Request payload: {json.dumps(kwargs['json'], indent=2)}")
    
    def _log_response(self, response):
        """Log the response details"""
        self.logger.info(f"Response status: {response.status_code}")
        try:
            if response.content:
                self.logger.debug(f"Response body: {json.dumps(response.json(), indent=2)}")
        except (json.JSONDecodeError, ValueError):
            self.logger.debug(f"Response body (non-JSON): {response.text}")
    
    def _make_request(self, method: str, endpoint: str = "", **kwargs):
        """
        Make HTTP request and store response
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: Additional endpoint path (will be appended to base_endpoint)
            **kwargs: Additional arguments for the request
            
        Returns:
            Response object
        """
        import time
        
        full_endpoint = f"{self.base_endpoint}{endpoint}"
        self._log_request(method, full_endpoint, **kwargs)
        
        start_time = time.time()
        
        if method.upper() == 'GET':
            response = self.api_client.get(full_endpoint, **kwargs)
        elif method.upper() == 'POST':
            response = self.api_client.post(full_endpoint, **kwargs)
        elif method.upper() == 'PUT':
            response = self.api_client.put(full_endpoint, **kwargs)
        elif method.upper() == 'DELETE':
            response = self.api_client.delete(full_endpoint, **kwargs)
        elif method.upper() == 'PATCH':
            response = self.api_client.patch(full_endpoint, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        end_time = time.time()
        self.last_request_time = (end_time - start_time) * 1000  # Convert to milliseconds
        self.last_response = response
        
        self._log_response(response)
        return response
    
    # Common API operations that most endpoints will have
    
    def get_all(self, params: Optional[Dict] = None):
        """Get all resources"""
        return self._make_request('GET', params=params)
    
    def get_by_id(self, resource_id: str):
        """Get resource by ID"""
        return self._make_request('GET', f"/{resource_id}")
    
    def create(self, data: Dict[str, Any]):
        """Create new resource"""
        return self._make_request('POST', json=data)
    
    def update(self, resource_id: str, data: Dict[str, Any]):
        """Update existing resource"""
        return self._make_request('PUT', f"/{resource_id}", json=data)
    
    def partial_update(self, resource_id: str, data: Dict[str, Any]):
        """Partially update existing resource"""
        return self._make_request('PATCH', f"/{resource_id}", json=data)
    
    def delete(self, resource_id: str):
        """Delete resource by ID"""
        return self._make_request('DELETE', f"/{resource_id}")
    
    # Validation methods
    
    def validate_status_code(self, expected_status: int):
        """Validate the last response status code"""
        if self.last_response is None:
            raise AssertionError("No response available for validation")
        
        actual_status = self.last_response.status_code
        assert actual_status == expected_status, \
            f"Expected status code {expected_status}, but got {actual_status}"
    
    def validate_response_time(self, max_time_ms: float):
        """Validate the last response time"""
        if self.last_request_time is None:
            raise AssertionError("No request time available for validation")
        
        assert self.last_request_time < max_time_ms, \
            f"Response time {self.last_request_time}ms exceeded maximum {max_time_ms}ms"
    
    def validate_response_contains_key(self, key: str):
        """Validate that response JSON contains a specific key"""
        if self.last_response is None:
            raise AssertionError("No response available for validation")
        
        try:
            response_data = self.last_response.json()
            assert key in response_data, f"Response does not contain key: {key}"
        except (json.JSONDecodeError, ValueError):
            raise AssertionError("Response is not valid JSON")
    
    def validate_response_is_list(self):
        """Validate that response JSON is a list"""
        if self.last_response is None:
            raise AssertionError("No response available for validation")
        
        try:
            response_data = self.last_response.json()
            assert isinstance(response_data, list), "Response is not a list"
        except (json.JSONDecodeError, ValueError):
            raise AssertionError("Response is not valid JSON")
    
    def validate_response_field_value(self, field: str, expected_value: Any):
        """Validate a specific field value in the response"""
        if self.last_response is None:
            raise AssertionError("No response available for validation")
        
        try:
            response_data = self.last_response.json()
            actual_value = response_data.get(field)
            assert actual_value == expected_value, \
                f"Expected {field}='{expected_value}', but got '{actual_value}'"
        except (json.JSONDecodeError, ValueError):
            raise AssertionError("Response is not valid JSON")
    
    def get_response_data(self):
        """Get the last response as JSON"""
        if self.last_response is None:
            raise AssertionError("No response available")
        
        try:
            return self.last_response.json()
        except (json.JSONDecodeError, ValueError):
            raise AssertionError("Response is not valid JSON")
    
    def get_response_status(self):
        """Get the last response status code"""
        if self.last_response is None:
            raise AssertionError("No response available")
        
        return self.last_response.status_code
    
    def get_response_time(self):
        """Get the last request response time in milliseconds"""
        return self.last_request_time
    
    # Abstract methods that specific API pages should implement
    
    @abstractmethod
    def validate_resource_structure(self, resource_data: Dict[str, Any]):
        """
        Validate that a resource has the expected structure/fields
        Each API page should implement this based on their specific resource schema
        """
        pass
    
    @abstractmethod
    def get_resource_id(self, resource_data: Dict[str, Any]) -> str:
        """
        Extract the resource ID from resource data
        Each API page should implement this based on their ID field name
        """
        pass

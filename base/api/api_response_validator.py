"""API response validator for automation testing"""

import requests
from typing import Dict


class APIResponseValidator:
    """Validator for API responses"""
    
    @staticmethod
    def validate_status_code(response: requests.Response, expected_code: int) -> bool:
        """Validate response status code"""
        return response.status_code == expected_code
    
    @staticmethod
    def validate_status_codes(response: requests.Response, expected_codes: list) -> bool:
        """Validate response status code is in list of expected codes"""
        return response.status_code in expected_codes
    
    @staticmethod
    def validate_content_type(response: requests.Response, expected_type: str) -> bool:
        """Validate response content type"""
        content_type = response.headers.get('content-type', '')
        return expected_type in content_type
    
    @staticmethod
    def validate_json_structure(response: requests.Response, required_keys: list) -> bool:
        """Validate JSON response has required keys"""
        try:
            json_data = response.json()
            return all(key in json_data for key in required_keys)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_json_schema(response: requests.Response, schema: Dict) -> bool:
        """Validate JSON response against schema"""
        try:
            import jsonschema
            json_data = response.json()
            jsonschema.validate(json_data, schema)
            return True
        except (ValueError, TypeError, jsonschema.ValidationError):
            return False
    
    @staticmethod
    def validate_response_time(response: requests.Response, max_time: float) -> bool:
        """Validate response time is within limit"""
        return response.elapsed.total_seconds() <= max_time
    
    @staticmethod
    def validate_header_present(response: requests.Response, header_name: str) -> bool:
        """Validate specific header is present"""
        return header_name in response.headers
    
    @staticmethod
    def validate_header_value(response: requests.Response, header_name: str, expected_value: str) -> bool:
        """Validate header has expected value"""
        return response.headers.get(header_name) == expected_value

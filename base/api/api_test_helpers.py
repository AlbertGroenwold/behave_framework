"""API test helpers for automation testing"""

import requests
import time
from typing import Dict, Any
from .base_api_client import BaseAPIClient


class APITestHelpers:
    """Helper utilities for API testing"""
    
    @staticmethod
    def wait_for_api_ready(client: BaseAPIClient, endpoint: str, 
                          timeout: int = 60, poll_interval: int = 5) -> bool:
        """Wait for API to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = client.get(endpoint)
                if response.status_code < 500:  # API is responding
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(poll_interval)
        
        return False
    
    @staticmethod
    def extract_json_value(response: requests.Response, json_path: str) -> Any:
        """Extract value from JSON response using dot notation"""
        try:
            json_data = response.json()
            keys = json_path.split('.')
            
            value = json_data
            for key in keys:
                if isinstance(value, dict):
                    value = value[key]
                elif isinstance(value, list) and key.isdigit():
                    value = value[int(key)]
                else:
                    return None
            
            return value
        except (ValueError, KeyError, IndexError, TypeError):
            return None
    
    @staticmethod
    def compare_json_responses(response1: requests.Response, 
                             response2: requests.Response) -> Dict[str, Any]:
        """Compare two JSON responses"""
        try:
            json1 = response1.json()
            json2 = response2.json()
            
            return {
                'equal': json1 == json2,
                'differences': APITestHelpers._find_json_differences(json1, json2)
            }
        except ValueError:
            return {'equal': False, 'error': 'Invalid JSON in response(s)'}
    
    @staticmethod
    def _find_json_differences(obj1: Any, obj2: Any, path: str = '') -> list:
        """Find differences between two JSON objects"""
        differences = []
        
        if type(obj1) != type(obj2):
            differences.append(f"{path}: type mismatch ({type(obj1)} vs {type(obj2)})")
            return differences
        
        if isinstance(obj1, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                
                if key not in obj1:
                    differences.append(f"{new_path}: missing in first object")
                elif key not in obj2:
                    differences.append(f"{new_path}: missing in second object")
                else:
                    differences.extend(
                        APITestHelpers._find_json_differences(obj1[key], obj2[key], new_path)
                    )
        
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                differences.append(f"{path}: length mismatch ({len(obj1)} vs {len(obj2)})")
            
            for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                differences.extend(
                    APITestHelpers._find_json_differences(item1, item2, new_path)
                )
        
        elif obj1 != obj2:
            differences.append(f"{path}: value mismatch ({obj1} vs {obj2})")
        
        return differences
    
    @staticmethod
    def generate_test_data(data_type: str) -> Dict[str, Any]:
        """Generate test data for API requests"""
        import random
        import string
        from datetime import datetime
        
        generators = {
            'user': lambda: {
                'username': ''.join(random.choices(string.ascii_lowercase, k=8)),
                'email': f"test_{random.randint(1000, 9999)}@example.com",
                'first_name': 'Test',
                'last_name': 'User',
                'age': random.randint(18, 80)
            },
            'product': lambda: {
                'name': f"Test Product {random.randint(1, 1000)}",
                'price': round(random.uniform(10, 1000), 2),
                'category': random.choice(['electronics', 'clothing', 'books']),
                'in_stock': random.choice([True, False])
            },
            'order': lambda: {
                'order_id': f"ORD-{random.randint(10000, 99999)}",
                'total_amount': round(random.uniform(50, 500), 2),
                'status': random.choice(['pending', 'processing', 'shipped', 'delivered']),
                'order_date': datetime.now().isoformat()
            }
        }
        
        if data_type not in generators:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        return generators[data_type]()

"""Database test validator for automation testing"""

from typing import Dict, List


class DatabaseTestValidator:
    """Base validator for database testing"""
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """Validate phone number format"""
        import re
        pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> List[str]:
        """Validate required fields are present"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        return missing_fields
    
    @staticmethod
    def validate_data_types(data: Dict, field_types: Dict[str, type]) -> List[str]:
        """Validate data types"""
        type_errors = []
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                type_errors.append(f"{field}: expected {expected_type.__name__}, got {type(data[field]).__name__}")
        return type_errors
    
    @staticmethod
    def validate_string_length(data: Dict, length_constraints: Dict[str, Dict]) -> List[str]:
        """Validate string lengths"""
        length_errors = []
        for field, constraints in length_constraints.items():
            if field in data and isinstance(data[field], str):
                value_length = len(data[field])
                
                if 'min_length' in constraints and value_length < constraints['min_length']:
                    length_errors.append(f"{field}: length {value_length} below minimum {constraints['min_length']}")
                
                if 'max_length' in constraints and value_length > constraints['max_length']:
                    length_errors.append(f"{field}: length {value_length} above maximum {constraints['max_length']}")
        
        return length_errors
    
    @staticmethod
    def validate_numeric_range(data: Dict, range_constraints: Dict[str, Dict]) -> List[str]:
        """Validate numeric ranges"""
        range_errors = []
        for field, constraints in range_constraints.items():
            if field in data and isinstance(data[field], (int, float)):
                value = data[field]
                
                if 'min_value' in constraints and value < constraints['min_value']:
                    range_errors.append(f"{field}: value {value} below minimum {constraints['min_value']}")
                
                if 'max_value' in constraints and value > constraints['max_value']:
                    range_errors.append(f"{field}: value {value} above maximum {constraints['max_value']}")
        
        return range_errors

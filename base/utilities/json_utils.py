import json
import jsonpath_ng
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class JsonUtils:
    """Utility class for working with JSON data"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read JSON data from file
        
        Args:
            file_path (str): Path to JSON file
        
        Returns:
            Dict[str, Any]: JSON data as dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            self.logger.info(f"Successfully read JSON file: {file_path}")
            return data
        
        except Exception as e:
            self.logger.error(f"Error reading JSON file {file_path}: {e}")
            raise
    
    def write_json_file(self, data: Dict[str, Any], file_path: str, indent: int = 4) -> bool:
        """
        Write JSON data to file
        
        Args:
            data (Dict[str, Any]): Data to write
            file_path (str): Path to JSON file
            indent (int): JSON indentation
        
        Returns:
            bool: True if successful
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            
            self.logger.info(f"Successfully wrote JSON file: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing JSON file {file_path}: {e}")
            return False
    
    def parse_json_string(self, json_string: str) -> Dict[str, Any]:
        """
        Parse JSON string to dictionary
        
        Args:
            json_string (str): JSON string
        
        Returns:
            Dict[str, Any]: Parsed JSON data
        """
        try:
            data = json.loads(json_string)
            self.logger.info("Successfully parsed JSON string")
            return data
        
        except Exception as e:
            self.logger.error(f"Error parsing JSON string: {e}")
            raise
    
    def to_json_string(self, data: Dict[str, Any], indent: int = None) -> str:
        """
        Convert dictionary to JSON string
        
        Args:
            data (Dict[str, Any]): Data to convert
            indent (int): JSON indentation
        
        Returns:
            str: JSON string
        """
        try:
            json_string = json.dumps(data, indent=indent, ensure_ascii=False)
            self.logger.info("Successfully converted data to JSON string")
            return json_string
        
        except Exception as e:
            self.logger.error(f"Error converting to JSON string: {e}")
            raise
    
    def query_json(self, data: Dict[str, Any], json_path: str) -> List[Any]:
        """
        Query JSON data using JSONPath
        
        Args:
            data (Dict[str, Any]): JSON data
            json_path (str): JSONPath expression
        
        Returns:
            List[Any]: List of matching values
        """
        try:
            jsonpath_expr = jsonpath_ng.parse(json_path)
            matches = [match.value for match in jsonpath_expr.find(data)]
            
            self.logger.info(f"JSONPath query '{json_path}' returned {len(matches)} matches")
            return matches
        
        except Exception as e:
            self.logger.error(f"Error querying JSON with path '{json_path}': {e}")
            raise
    
    def get_value(self, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Get value from nested JSON using dot notation
        
        Args:
            data (Dict[str, Any]): JSON data
            path (str): Dot-separated path (e.g., 'user.profile.name')
            default (Any): Default value if path not found
        
        Returns:
            Any: Value at the specified path
        """
        try:
            keys = path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                elif isinstance(value, list) and key.isdigit():
                    index = int(key)
                    if 0 <= index < len(value):
                        value = value[index]
                    else:
                        return default
                else:
                    return default
            
            self.logger.info(f"Successfully retrieved value for path '{path}'")
            return value
        
        except Exception as e:
            self.logger.error(f"Error getting value for path '{path}': {e}")
            return default
    
    def set_value(self, data: Dict[str, Any], path: str, value: Any) -> bool:
        """
        Set value in nested JSON using dot notation
        
        Args:
            data (Dict[str, Any]): JSON data
            path (str): Dot-separated path
            value (Any): Value to set
        
        Returns:
            bool: True if successful
        """
        try:
            keys = path.split('.')
            current = data
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the value
            current[keys[-1]] = value
            
            self.logger.info(f"Successfully set value for path '{path}'")
            return True
        
        except Exception as e:
            self.logger.error(f"Error setting value for path '{path}': {e}")
            return False
    
    def merge_json(self, json1: Dict[str, Any], json2: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
        """
        Merge two JSON objects
        
        Args:
            json1 (Dict[str, Any]): First JSON object
            json2 (Dict[str, Any]): Second JSON object
            deep (bool): Whether to perform deep merge
        
        Returns:
            Dict[str, Any]: Merged JSON object
        """
        try:
            if not deep:
                merged = {**json1, **json2}
            else:
                merged = json1.copy()
                for key, value in json2.items():
                    if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key] = self.merge_json(merged[key], value, deep)
                    else:
                        merged[key] = value
            
            self.logger.info("Successfully merged JSON objects")
            return merged
        
        except Exception as e:
            self.logger.error(f"Error merging JSON objects: {e}")
            raise
    
    def validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate JSON data against schema
        
        Args:
            data (Dict[str, Any]): JSON data to validate
            schema (Dict[str, Any]): JSON schema
        
        Returns:
            tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        try:
            import jsonschema
            
            validator = jsonschema.Draft7Validator(schema)
            errors = list(validator.iter_errors(data))
            
            is_valid = len(errors) == 0
            error_messages = [error.message for error in errors]
            
            self.logger.info(f"JSON validation result: {'Valid' if is_valid else 'Invalid'}")
            return is_valid, error_messages
        
        except ImportError:
            self.logger.error("jsonschema library not installed")
            raise ImportError("Please install jsonschema: pip install jsonschema")
        except Exception as e:
            self.logger.error(f"Error validating JSON schema: {e}")
            raise
    
    def flatten_json(self, data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
        """
        Flatten nested JSON object
        
        Args:
            data (Dict[str, Any]): JSON data to flatten
            separator (str): Separator for flattened keys
        
        Returns:
            Dict[str, Any]: Flattened JSON object
        """
        def _flatten(obj, parent_key='', sep='.'):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(_flatten(v, new_key, sep=sep).items())
                    elif isinstance(v, list):
                        for i, item in enumerate(v):
                            items.extend(_flatten(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((new_key, v))
            else:
                return {parent_key: obj}
            return dict(items)
        
        try:
            flattened = _flatten(data, sep=separator)
            self.logger.info("Successfully flattened JSON object")
            return flattened
        
        except Exception as e:
            self.logger.error(f"Error flattening JSON: {e}")
            raise
    
    def compare_json(self, json1: Dict[str, Any], json2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two JSON objects and return differences
        
        Args:
            json1 (Dict[str, Any]): First JSON object
            json2 (Dict[str, Any]): Second JSON object
        
        Returns:
            Dict[str, Any]: Differences between the objects
        """
        try:
            differences = {
                'added': {},
                'removed': {},
                'modified': {},
                'unchanged': {}
            }
            
            all_keys = set(json1.keys()) | set(json2.keys())
            
            for key in all_keys:
                if key in json1 and key in json2:
                    if json1[key] == json2[key]:
                        differences['unchanged'][key] = json1[key]
                    else:
                        differences['modified'][key] = {
                            'old': json1[key],
                            'new': json2[key]
                        }
                elif key in json1:
                    differences['removed'][key] = json1[key]
                else:
                    differences['added'][key] = json2[key]
            
            self.logger.info("Successfully compared JSON objects")
            return differences
        
        except Exception as e:
            self.logger.error(f"Error comparing JSON objects: {e}")
            raise

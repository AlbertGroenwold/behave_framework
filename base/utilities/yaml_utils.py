import logging
from typing import Dict, Any
from pathlib import Path
import yaml


class YamlUtils:
    """Utility class for working with YAML data"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def read_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read YAML data from file
        
        Args:
            file_path (str): Path to YAML file
        
        Returns:
            Dict[str, Any]: YAML data as dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            self.logger.info(f"Successfully read YAML file: {file_path}")
            return data
        
        except Exception as e:
            self.logger.error(f"Error reading YAML file {file_path}: {e}")
            raise
    
    def write_yaml_file(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        Write YAML data to file
        
        Args:
            data (Dict[str, Any]): Data to write
            file_path (str): Path to YAML file
        
        Returns:
            bool: True if successful
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Successfully wrote YAML file: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing YAML file {file_path}: {e}")
            return False

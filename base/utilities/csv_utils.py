import csv
import os
import logging
from pathlib import Path
from typing import List, Dict


class CsvUtils:
    """Utility class for CSV operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def read_csv_file(self, file_path: str, delimiter: str = ',', encoding: str = 'utf-8') -> List[Dict[str, str]]:
        """
        Read CSV file as list of dictionaries
        
        Args:
            file_path (str): CSV file path
            delimiter (str): CSV delimiter
            encoding (str): File encoding
        
        Returns:
            List[Dict[str, str]]: List of row dictionaries
        """
        try:
            data = []
            with open(file_path, 'r', encoding=encoding, newline='') as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                data = list(reader)
            
            self.logger.info(f"Successfully read CSV file: {file_path} ({len(data)} rows)")
            return data
        
        except Exception as e:
            self.logger.error(f"Error reading CSV file {file_path}: {e}")
            return []
    
    def write_csv_file(self, data: List[Dict[str, str]], file_path: str, 
                      delimiter: str = ',', encoding: str = 'utf-8') -> bool:
        """
        Write CSV file from list of dictionaries
        
        Args:
            data (List[Dict[str, str]]): Data to write
            file_path (str): CSV file path
            delimiter (str): CSV delimiter
            encoding (str): File encoding
        
        Returns:
            bool: True if successful
        """
        try:
            if not data:
                self.logger.warning("No data to write")
                return False
            
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            fieldnames = data[0].keys()
            
            with open(file_path, 'w', encoding=encoding, newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"Successfully wrote CSV file: {file_path} ({len(data)} rows)")
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing CSV file {file_path}: {e}")
            return False
    
    def append_csv_file(self, data: List[Dict[str, str]], file_path: str, 
                       delimiter: str = ',', encoding: str = 'utf-8') -> bool:
        """
        Append data to CSV file
        
        Args:
            data (List[Dict[str, str]]): Data to append
            file_path (str): CSV file path
            delimiter (str): CSV delimiter
            encoding (str): File encoding
        
        Returns:
            bool: True if successful
        """
        try:
            if not data:
                self.logger.warning("No data to append")
                return False
            
            file_exists = os.path.exists(file_path)
            
            with open(file_path, 'a', encoding=encoding, newline='') as file:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)
                
                # Write header only if file doesn't exist
                if not file_exists:
                    writer.writeheader()
                
                writer.writerows(data)
            
            self.logger.info(f"Successfully appended to CSV file: {file_path} ({len(data)} rows)")
            return True
        
        except Exception as e:
            self.logger.error(f"Error appending to CSV file {file_path}: {e}")
            return False

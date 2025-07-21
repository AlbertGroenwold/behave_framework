import pandas as pd
import xlsxwriter
import logging
from typing import Dict, List, Any, Union
from pathlib import Path


class ExcelWriter:
    """Utility class for writing Excel files"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def write_dataframe(self, df: pd.DataFrame, sheet_name: str = 'Sheet1', index: bool = False) -> bool:
        """
        Write DataFrame to Excel file
        
        Args:
            df (pd.DataFrame): DataFrame to write
            sheet_name (str): Name of the sheet
            index (bool): Whether to write row indices
        
        Returns:
            bool: True if successful
        """
        try:
            with pd.ExcelWriter(self.file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=index)
            
            self.logger.info(f"Successfully wrote DataFrame to {self.file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing DataFrame: {e}")
            return False
    
    def write_multiple_sheets(self, data_dict: Dict[str, pd.DataFrame], index: bool = False) -> bool:
        """
        Write multiple DataFrames to different sheets
        
        Args:
            data_dict (Dict[str, pd.DataFrame]): Dictionary with sheet names as keys and DataFrames as values
            index (bool): Whether to write row indices
        
        Returns:
            bool: True if successful
        """
        try:
            with pd.ExcelWriter(self.file_path, engine='xlsxwriter') as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=index)
            
            self.logger.info(f"Successfully wrote {len(data_dict)} sheets to {self.file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing multiple sheets: {e}")
            return False
    
    def write_list_data(self, data: List[List[Any]], sheet_name: str = 'Sheet1', 
                       headers: List[str] = None) -> bool:
        """
        Write list data to Excel file
        
        Args:
            data (List[List[Any]]): 2D list of data
            sheet_name (str): Name of the sheet
            headers (List[str]): Column headers
        
        Returns:
            bool: True if successful
        """
        try:
            df = pd.DataFrame(data, columns=headers)
            return self.write_dataframe(df, sheet_name)
        
        except Exception as e:
            self.logger.error(f"Error writing list data: {e}")
            return False
    
    def append_data(self, data: Union[pd.DataFrame, List[List[Any]]], sheet_name: str = 'Sheet1') -> bool:
        """
        Append data to existing Excel file
        
        Args:
            data (Union[pd.DataFrame, List[List[Any]]]): Data to append
            sheet_name (str): Name of the sheet
        
        Returns:
            bool: True if successful
        """
        try:
            if isinstance(data, list):
                new_df = pd.DataFrame(data)
            else:
                new_df = data
            
            if self.file_path.exists():
                existing_df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            return self.write_dataframe(combined_df, sheet_name)
        
        except Exception as e:
            self.logger.error(f"Error appending data: {e}")
            return False

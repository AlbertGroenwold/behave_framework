"""Base database manager and related utilities - backward compatibility imports"""

import configparser
import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod


class BaseDatabaseManager(ABC):
    """Abstract base class for database managers"""
    
    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = None
        self.db_type = None
        
        if config_path:
            self.config.read(config_path)
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to database"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from database"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute database query"""
        pass
    
    @abstractmethod
    def get_row_count(self, table_name: str) -> int:
        """Get row count for table"""
        pass
    
    def is_connected(self) -> bool:
        """Check if connected to database"""
        return self.connection is not None
    
    def log_query(self, query: str, params: Dict = None):
        """Log database query"""
        self.logger.info(f"Executing query: {query}")
        if params:
            self.logger.debug(f"Query parameters: {params}")


# Import and re-export related classes for backward compatibility
from .database_test_validator import DatabaseTestValidator
from .database_performance_monitor import DatabasePerformanceMonitor
from .database_test_data_generator import DatabaseTestDataGenerator

__all__ = [
    'BaseDatabaseManager',
    'DatabaseTestValidator',
    'DatabasePerformanceMonitor',
    'DatabaseTestDataGenerator'
]

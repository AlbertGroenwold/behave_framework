"""Base database manager and related utilities - backward compatibility imports"""

import configparser
import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from ..utilities.recovery_strategies import (
    create_recovery_hook, auto_recovery_manager, 
    register_database_health_checker, recovery_context
)
from ..utilities.error_handler import DatabaseError, ErrorCategory


class BaseDatabaseManager(ABC):
    """Abstract base class for database managers"""
    
    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = None
        self.db_type = None
        
        if config_path:
            self.config.read(config_path)
        
        # Initialize recovery mechanisms
        self.component_name = f"database_{self.__class__.__name__.lower()}"
        self.recovery_hook = create_recovery_hook(self.component_name)
        
        # Set up recovery strategy for database issues
        auto_recovery_manager.register_recovery_strategy(
            self.component_name,
            self._database_recovery_strategy
        )
    
    def _database_recovery_strategy(self, error: Exception) -> bool:
        """Recovery strategy for database-related errors."""
        try:
            self.logger.info(f"Attempting database recovery for {self.component_name}")
            
            # Check if it's a connection-related error
            error_name = type(error).__name__
            if error_name in ['ConnectionError', 'OperationalError', 'TimeoutError', 'DatabaseError']:
                # Try to reconnect
                try:
                    self.disconnect()
                    import time
                    time.sleep(2)
                    
                    if self.connect():
                        self.logger.info("Database recovery successful - reconnected")
                        return True
                except Exception as reconnect_error:
                    self.logger.warning(f"Reconnection failed during recovery: {reconnect_error}")
                
            self.logger.warning("Database recovery failed")
            return False
        except Exception as recovery_error:
            self.logger.error(f"Error during database recovery: {recovery_error}")
            return False
    
    def _register_health_checker(self):
        """Register health checker for this database manager."""
        try:
            register_database_health_checker(
                self.component_name, 
                self
            )
        except Exception as e:
            self.logger.debug(f"Could not register database health checker: {e}")
    
    def connect_with_recovery(self) -> bool:
        """Connect to database with recovery capabilities."""
        def _connect():
            result = self.connect()
            if result:
                self._register_health_checker()
            return result
        
        with recovery_context(self.component_name, auto_recovery_manager, max_recovery_attempts=2):
            return _connect()
    
    def execute_query_with_recovery(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute database query with recovery capabilities."""
        with recovery_context(self.component_name, auto_recovery_manager, max_recovery_attempts=1):
            return self.execute_query(query, params)
    
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

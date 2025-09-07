"""
Database package for the automation framework

This package contains database testing base classes and utilities.
"""

from .base_database_manager import BaseDatabaseManager
from .database_managers import (
    PostgreSQLManager, MySQLManager, SQLiteManager, 
    MongoDBManager, RedisManager
)

__all__ = [
    'BaseDatabaseManager',
    'PostgreSQLManager',
    'MySQLManager', 
    'SQLiteManager',
    'MongoDBManager',
    'RedisManager'
]

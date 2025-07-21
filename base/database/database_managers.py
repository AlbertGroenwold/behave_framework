"""Database managers for automation testing - backward compatibility imports"""

# Import individual database managers
from .postgresql_manager import PostgreSQLManager
from .mysql_manager import MySQLManager
from .sqlite_manager import SQLiteManager
from .mongodb_manager import MongoDBManager
from .redis_manager import RedisManager

# Re-export all managers for backward compatibility
__all__ = [
    'PostgreSQLManager',
    'MySQLManager', 
    'SQLiteManager',
    'MongoDBManager',
    'RedisManager'
]

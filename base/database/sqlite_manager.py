import sqlalchemy
from sqlalchemy import create_engine, text, exc
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Union
from .base_database_manager import BaseDatabaseManager


class SQLiteManager(BaseDatabaseManager):
    """SQLite database manager"""
    
    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        self.db_type = "sqlite"
        self.engine = None
    
    def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            # Get database path from config
            db_path = self.config.get('sqlite', 'database_path', fallback='test.db')
            
            connection_string = f"sqlite:///{db_path}"
            self.engine = create_engine(connection_string)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.connection = self.engine
            self.logger.info(f"Connected to SQLite database: {db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from SQLite"""
        if self.engine:
            self.engine.dispose()
            self.connection = None
            self.logger.info("Disconnected from SQLite")
    
    def execute_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute SQLite query"""
        self.log_query(query, params)
        
        try:
            with self.engine.connect() as conn:
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    # SELECT query
                    result = conn.execute(text(query), params or {})
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    return {
                        'success': True,
                        'data': [dict(zip(columns, row)) for row in rows],
                        'row_count': len(rows)
                    }
                else:
                    # INSERT, UPDATE, DELETE
                    with conn.begin():
                        result = conn.execute(text(query), params or {})
                        return {
                            'success': True,
                            'affected_rows': result.rowcount
                        }
        
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for SQLite table"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        
        if result['success'] and result['data']:
            return result['data'][0]['count']
        return 0

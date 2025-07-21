import sqlalchemy
from sqlalchemy import create_engine, text, exc
import psycopg2
import logging
from typing import Dict, Any, List, Optional, Union
from .base_database_manager import BaseDatabaseManager


class PostgreSQLManager(BaseDatabaseManager):
    """PostgreSQL database manager"""
    
    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        self.db_type = "postgresql"
        self.engine = None
    
    def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            # Get connection details from config
            host = self.config.get('postgresql', 'host', fallback='localhost')
            port = self.config.get('postgresql', 'port', fallback='5432')
            database = self.config.get('postgresql', 'database', fallback='testdb')
            username = self.config.get('postgresql', 'username', fallback='postgres')
            password = self.config.get('postgresql', 'password', fallback='password')
            
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            self.engine = create_engine(connection_string)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.connection = self.engine
            self.logger.info(f"Connected to PostgreSQL database: {database}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from PostgreSQL"""
        if self.engine:
            self.engine.dispose()
            self.connection = None
            self.logger.info("Disconnected from PostgreSQL")
    
    def execute_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute PostgreSQL query"""
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
        """Get row count for PostgreSQL table"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.execute_query(query)
        
        if result['success'] and result['data']:
            return result['data'][0]['count']
        return 0

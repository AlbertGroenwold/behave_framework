import sqlalchemy
from sqlalchemy import create_engine, text, exc
from sqlalchemy.pool import QueuePool
import mysql.connector
import logging
import time
import threading
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
from .base_database_manager import BaseDatabaseManager
from ..utilities.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, create_circuit_breaker,
    CircuitBreakerError, CircuitBreakerState
)
from ..utilities.error_handler import (
    DatabaseError, ConnectionError, ErrorCategory,
    retry_on_error, error_context
)
from ..utilities.recovery_strategies import (
    register_database_health_checker, auto_recovery_manager
)


class MySQLManager(BaseDatabaseManager):
    """Enhanced MySQL database manager with circuit breaker and resilience features"""
    
    def __init__(self, config_path: str = None, enable_circuit_breaker: bool = True,
                 connection_pool_size: int = 5, max_overflow: int = 10):
        super().__init__(config_path)
        self.db_type = "mysql"
        self.engine = None
        self.enable_circuit_breaker = enable_circuit_breaker
        self.connection_pool_size = connection_pool_size
        self.max_overflow = max_overflow
        self._connection_lock = threading.Lock()
        self._active_transactions = {}
        
        # Connection pool recovery tracking
        self.pool_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'pool_recoveries': 0,
            'connection_failures': 0,
            'last_recovery_time': None
        }
        
        # Circuit breaker setup
        if enable_circuit_breaker:
            cb_config = CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                expected_exception=(sqlalchemy.exc.DatabaseError, mysql.connector.Error, DatabaseError),
                timeout=30.0
            )
            self.circuit_breaker = create_circuit_breaker(
                f"mysql_{self.component_name}", 
                cb_config
            )
        else:
            self.circuit_breaker = None
    
    def _create_engine_with_pool(self, connection_string: str):
        """Create SQLAlchemy engine with connection pooling."""
        try:
            engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.connection_pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=3600,   # Recycle connections every hour
                echo=False
            )
            return engine
        except Exception as e:
            self.logger.error(f"Failed to create engine with pool: {e}")
            raise DatabaseError(
                f"Engine creation failed: {str(e)}",
                category=ErrorCategory.PERMANENT,
                original_error=e
            )
    
    def _recover_connection_pool(self) -> bool:
        """Attempt to recover the connection pool."""
        try:
            self.logger.info("Attempting connection pool recovery...")
            
            if self.engine:
                # Dispose of the current engine
                self.engine.dispose()
                time.sleep(2)  # Wait for connections to clean up
            
            # Recreate the engine
            connection_string = self._build_connection_string()
            self.engine = self._create_engine_with_pool(connection_string)
            
            # Test the new connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.connection = self.engine
            self.pool_stats['pool_recoveries'] += 1
            self.pool_stats['last_recovery_time'] = time.time()
            
            self.logger.info("Connection pool recovery successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection pool recovery failed: {e}")
            return False
    
    def _build_connection_string(self) -> str:
        """Build MySQL connection string from config."""
        host = self.config.get('mysql', 'host', fallback='localhost')
        port = self.config.get('mysql', 'port', fallback='3306')
        database = self.config.get('mysql', 'database', fallback='testdb')
        username = self.config.get('mysql', 'username', fallback='root')
        password = self.config.get('mysql', 'password', fallback='password')
        
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    
    @retry_on_error(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
    def connect(self) -> bool:
    @retry_on_error(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
    def connect(self) -> bool:
        """Connect to MySQL database with enhanced resilience"""
        try:
            with self._connection_lock:
                if self.is_connected():
                    return True
                
                connection_string = self._build_connection_string()
                self.engine = self._create_engine_with_pool(connection_string)
                
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                self.connection = self.engine
                self.pool_stats['total_connections'] += 1
                
                # Register health checker
                register_database_health_checker(
                    self.component_name, 
                    self
                )
                
                self.logger.info(f"Connected to MySQL database with connection pool")
                return True
                
        except Exception as e:
            self.pool_stats['connection_failures'] += 1
            self.logger.error(f"Failed to connect to MySQL: {e}")
            raise DatabaseError(
                f"MySQL connection failed: {str(e)}",
                category=ErrorCategory.TRANSIENT,
                original_error=e
            )
    
    def disconnect(self):
        """Disconnect from MySQL with cleanup"""
        with self._connection_lock:
            if self.engine:
                # Clean up any active transactions
                self._rollback_active_transactions()
                
                # Dispose of the engine and connection pool
                self.engine.dispose()
                self.connection = None
                self.logger.info("Disconnected from MySQL")
    
    def _rollback_active_transactions(self):
        """Rollback all active transactions."""
        if self._active_transactions:
            self.logger.warning(f"Rolling back {len(self._active_transactions)} active transactions")
            for tx_id, transaction in list(self._active_transactions.items()):
                try:
                    transaction.rollback()
                    self.logger.info(f"Rolled back transaction {tx_id}")
                except Exception as e:
                    self.logger.error(f"Failed to rollback transaction {tx_id}: {e}")
                finally:
                    self._active_transactions.pop(tx_id, None)
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions with automatic rollback."""
        tx_id = id(threading.current_thread())
        transaction = None
        
        try:
            with self.engine.connect() as conn:
                transaction = conn.begin()
                self._active_transactions[tx_id] = transaction
                
                yield conn
                
                transaction.commit()
                self.logger.debug(f"Transaction {tx_id} committed successfully")
                
        except Exception as e:
            if transaction:
                transaction.rollback()
                self.logger.warning(f"Transaction {tx_id} rolled back due to error: {e}")
            raise
        finally:
            self._active_transactions.pop(tx_id, None)
    
    def _execute_with_circuit_breaker(self, operation_func, *args, **kwargs):
        """Execute database operation with circuit breaker protection."""
        if self.enable_circuit_breaker and self.circuit_breaker:
            try:
                return self.circuit_breaker.call(operation_func, *args, **kwargs)
            except CircuitBreakerError as e:
                self.logger.warning(f"MySQL circuit breaker open: {e}")
                raise DatabaseError(
                    f"Database temporarily unavailable (circuit breaker open): {str(e)}",
                    category=ErrorCategory.TRANSIENT,
                    original_error=e
                )
        else:
            return operation_func(*args, **kwargs)
    
    def execute_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute MySQL query with enhanced error handling and circuit breaker protection"""
        def _execute():
            self.log_query(query, params)
            
            try:
                # Check if we need to recover connection pool
                if not self.is_connected():
                    if not self._recover_connection_pool():
                        raise DatabaseError(
                            "Unable to establish database connection",
                            category=ErrorCategory.TRANSIENT
                        )
                
                with self.engine.connect() as conn:
                    if query.strip().upper().startswith(('SELECT', 'WITH', 'SHOW', 'DESCRIBE')):
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
            
            except (sqlalchemy.exc.DatabaseError, mysql.connector.Error) as e:
                self.logger.error(f"MySQL query execution failed: {e}")
                
                # Determine if this is a connection issue
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['connection', 'lost', 'broken', 'timeout']):
                    category = ErrorCategory.TRANSIENT
                else:
                    category = ErrorCategory.PERMANENT
                
                raise DatabaseError(
                    f"Query execution failed: {str(e)}",
                    query=query,
                    category=category,
                    original_error=e
                )
            except Exception as e:
                self.logger.error(f"Unexpected error during query execution: {e}")
                raise DatabaseError(
                    f"Unexpected query error: {str(e)}",
                    query=query,
                    category=ErrorCategory.UNKNOWN,
                    original_error=e
                )
        
        return self._execute_with_circuit_breaker(_execute)
    
    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        pool_stats = self.pool_stats.copy()
        
        if self.engine and hasattr(self.engine.pool, 'size'):
            pool_stats.update({
                'pool_size': self.engine.pool.size(),
                'checked_out_connections': self.engine.pool.checkedout(),
                'overflow_connections': self.engine.pool.overflow(),
                'checked_in_connections': self.engine.pool.checkedin()
            })
        
        return pool_stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on MySQL connection."""
        try:
            start_time = time.time()
            
            if not self.is_connected():
                return {
                    'healthy': False,
                    'message': 'Not connected to database',
                    'response_time_ms': 0
                }
            
            # Simple health check query
            result = self.execute_query("SELECT 1 as health_check")
            response_time = (time.time() - start_time) * 1000
            
            if result['success']:
                return {
                    'healthy': True,
                    'message': 'Database connection healthy',
                    'response_time_ms': response_time,
                    'pool_stats': self.get_connection_pool_stats()
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Health check query failed',
                    'response_time_ms': response_time
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Health check failed: {str(e)}',
                'response_time_ms': 0
            }
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for MySQL table"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        
        if result['success'] and result['data']:
            return result['data'][0]['count']
        return 0

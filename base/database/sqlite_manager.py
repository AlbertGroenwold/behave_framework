import sqlalchemy
from sqlalchemy import create_engine, text, exc
from sqlalchemy.pool import StaticPool
import sqlite3
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


class SQLiteManager(BaseDatabaseManager):
    """Enhanced SQLite database manager with circuit breaker and resilience features"""
    
    def __init__(self, config_path: str = None, enable_circuit_breaker: bool = True):
        super().__init__(config_path)
        self.db_type = "sqlite"
        self.engine = None
        self.enable_circuit_breaker = enable_circuit_breaker
        self._connection_lock = threading.Lock()
        self._active_transactions = {}
        
        # Connection tracking
        self.connection_stats = {
            'total_connections': 0,
            'connection_failures': 0,
            'last_connection_time': None
        }
        
        # Circuit breaker setup
        if enable_circuit_breaker:
            cb_config = CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                expected_exception=(sqlalchemy.exc.DatabaseError, sqlite3.Error, DatabaseError),
                timeout=30.0
            )
            self.circuit_breaker = create_circuit_breaker(
                f"sqlite_{self.component_name}", 
                cb_config
            )
        else:
            self.circuit_breaker = None
    
    def _create_engine(self, connection_string: str):
        """Create SQLAlchemy engine for SQLite."""
        try:
            # SQLite specific configuration
            engine = create_engine(
                connection_string,
                poolclass=StaticPool,
                connect_args={
                    'check_same_thread': False,  # Allow multi-threading
                    'timeout': 30  # Connection timeout
                },
                echo=False
            )
            return engine
        except Exception as e:
            self.logger.error(f"Failed to create SQLite engine: {e}")
            raise DatabaseError(
                f"SQLite engine creation failed: {str(e)}",
                category=ErrorCategory.PERMANENT,
                original_error=e
            )
    
    def _build_connection_string(self) -> str:
        """Build SQLite connection string from config."""
        db_path = self.config.get('sqlite', 'database_path', fallback='test.db')
        return f"sqlite:///{db_path}"
    
    @retry_on_error(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
    def connect(self) -> bool:
        """Connect to SQLite database with enhanced resilience"""
        try:
            with self._connection_lock:
                if self.is_connected():
                    return True
                
                connection_string = self._build_connection_string()
                self.engine = self._create_engine(connection_string)
                
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                self.connection = self.engine
                self.connection_stats['total_connections'] += 1
                self.connection_stats['last_connection_time'] = time.time()
                
                # Register health checker
                register_database_health_checker(
                    self.component_name, 
                    self
                )
                
                self.logger.info(f"Connected to SQLite database")
                return True
                
        except Exception as e:
            self.connection_stats['connection_failures'] += 1
            self.logger.error(f"Failed to connect to SQLite: {e}")
            raise DatabaseError(
                f"SQLite connection failed: {str(e)}",
                category=ErrorCategory.TRANSIENT,
                original_error=e
            )
    
    def disconnect(self):
        """Disconnect from SQLite with cleanup"""
        with self._connection_lock:
            if self.engine:
                # Clean up any active transactions
                self._rollback_active_transactions()
                
                # Dispose of the engine
                self.engine.dispose()
                self.connection = None
                self.logger.info("Disconnected from SQLite")
    
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
                self.logger.warning(f"SQLite circuit breaker open: {e}")
                raise DatabaseError(
                    f"Database temporarily unavailable (circuit breaker open): {str(e)}",
                    category=ErrorCategory.TRANSIENT,
                    original_error=e
                )
        else:
            return operation_func(*args, **kwargs)
    
    def execute_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute SQLite query with enhanced error handling and circuit breaker protection"""
        def _execute():
            self.log_query(query, params)
            
            try:
                # SQLite doesn't need connection pool recovery like network databases
                if not self.is_connected():
                    raise DatabaseError(
                        "Not connected to SQLite database",
                        category=ErrorCategory.TRANSIENT
                    )
                
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
            
            except (sqlalchemy.exc.DatabaseError, sqlite3.Error) as e:
                self.logger.error(f"SQLite query execution failed: {e}")
                
                # Most SQLite errors are permanent (syntax, constraints, etc.)
                # Only file-related errors might be transient
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['locked', 'busy', 'disk']):
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
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return self.connection_stats.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on SQLite connection."""
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
                    'connection_stats': self.get_connection_stats()
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
        """Get row count for SQLite table"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        
        if result['success'] and result['data']:
            return result['data'][0]['count']
        return 0

"""Redis database manager for automation testing"""

import redis
from typing import Any, Dict
from .base_database_manager import BaseDatabaseManager


class RedisManager(BaseDatabaseManager):
    """Redis database manager"""
    
    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        self.db_type = "redis"
        self.redis_client = None
    
    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            # Get connection details from config
            host = self.config.get('redis', 'host', fallback='localhost')
            port = self.config.get('redis', 'port', fallback='6379')
            db = self.config.get('redis', 'db', fallback='0')
            password = self.config.get('redis', 'password', fallback=None)
            
            self.redis_client = redis.Redis(
                host=host,
                port=int(port),
                db=int(db),
                password=password,
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            
            self.connection = self.redis_client
            self.logger.info(f"Connected to Redis database: {db}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            self.redis_client.close()
            self.connection = None
            self.redis_client = None
            self.logger.info("Disconnected from Redis")
    
    def execute_operation(self, operation: str, key: str, value: Any = None, 
                         field: str = None, **kwargs) -> Dict[str, Any]:
        """Execute Redis operation"""
        self.log_query(f"{operation} on key: {key}", {'value': value, 'field': field})
        
        try:
            if operation == 'set':
                result = self.redis_client.set(key, value, **kwargs)
                return {'success': True, 'result': result}
            
            elif operation == 'get':
                result = self.redis_client.get(key)
                return {'success': True, 'result': result}
            
            elif operation == 'delete':
                result = self.redis_client.delete(key)
                return {'success': True, 'deleted_keys': result}
            
            elif operation == 'exists':
                result = self.redis_client.exists(key)
                return {'success': True, 'exists': bool(result)}
            
            elif operation == 'hset':
                result = self.redis_client.hset(key, field, value)
                return {'success': True, 'fields_set': result}
            
            elif operation == 'hget':
                result = self.redis_client.hget(key, field)
                return {'success': True, 'result': result}
            
            elif operation == 'hgetall':
                result = self.redis_client.hgetall(key)
                return {'success': True, 'result': result}
            
            elif operation == 'keys':
                result = self.redis_client.keys(key)
                return {'success': True, 'keys': result}
            
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        
        except Exception as e:
            self.logger.error(f"Redis operation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_row_count(self, pattern: str = "*") -> int:
        """Get key count for Redis pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            return len(keys)
        except Exception:
            return 0

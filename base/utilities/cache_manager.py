"""Advanced caching mechanism for test automation framework.

This module provides comprehensive caching capabilities including:
- LRU cache for test data
- Cache invalidation strategies
- Cache statistics and monitoring
- Distributed cache support (Redis)
"""

import time
import threading
import json
import pickle
import hashlib
import logging
from typing import Any, Optional, Dict, List, Callable, Union, Set
from collections import OrderedDict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from functools import wraps
from enum import Enum


class CacheStrategy(Enum):
    """Cache invalidation strategies."""
    TTL = "ttl"  # Time to live
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out


class CacheEntry:
    """Represents a cache entry with metadata."""
    
    def __init__(self, key: str, value: Any, ttl: Optional[float] = None):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.ttl = ttl
        self.expires_at = self.created_at + ttl if ttl else None
    
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def touch(self):
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def get_age(self) -> float:
        """Get the age of the cache entry in seconds."""
        return time.time() - self.created_at
    
    def get_time_since_access(self) -> float:
        """Get time since last access in seconds."""
        return time.time() - self.last_accessed


class CacheStats:
    """Track cache usage statistics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.evictions = 0
        self.expired_entries = 0
        self.total_size = 0
        self.start_time = time.time()
        self._lock = threading.Lock()
    
    def record_hit(self):
        """Record a cache hit."""
        with self._lock:
            self.hits += 1
    
    def record_miss(self):
        """Record a cache miss."""
        with self._lock:
            self.misses += 1
    
    def record_set(self):
        """Record a cache set operation."""
        with self._lock:
            self.sets += 1
    
    def record_delete(self):
        """Record a cache delete operation."""
        with self._lock:
            self.deletes += 1
    
    def record_eviction(self):
        """Record a cache eviction."""
        with self._lock:
            self.evictions += 1
    
    def record_expiration(self):
        """Record an expired entry cleanup."""
        with self._lock:
            self.expired_entries += 1
    
    def update_size(self, size: int):
        """Update total cache size."""
        with self._lock:
            self.total_size = size
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            runtime = time.time() - self.start_time
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'sets': self.sets,
                'deletes': self.deletes,
                'evictions': self.evictions,
                'expired_entries': self.expired_entries,
                'total_requests': total_requests,
                'hit_rate_percent': round(hit_rate, 2),
                'total_size': self.total_size,
                'runtime_seconds': round(runtime, 2)
            }
    
    def reset(self):
        """Reset all statistics."""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.sets = 0
            self.deletes = 0
            self.evictions = 0
            self.expired_entries = 0
            self.total_size = 0
            self.start_time = time.time()


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    def get_size(self) -> int:
        """Get number of items in cache."""
        pass
    
    @abstractmethod
    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with configurable eviction strategies."""
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: OrderedDict = OrderedDict()  # For LRU
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background thread for cleanup of expired entries."""
        def cleanup_expired():
            while not self._stop_cleanup.wait(60):  # Check every minute
                self._cleanup_expired_entries()
        
        self._cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_expired_entries(self):
        """Remove expired entries from cache."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._access_order.pop(key, None)
    
    def _evict_if_needed(self):
        """Evict entries if cache is at capacity."""
        if len(self._cache) < self.max_size:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            if self._access_order:
                oldest_key = next(iter(self._access_order))
                del self._cache[oldest_key]
                del self._access_order[oldest_key]
        
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            if self._cache:
                lfu_key = min(self._cache.keys(), 
                            key=lambda k: self._cache[k].access_count)
                del self._cache[lfu_key]
                self._access_order.pop(lfu_key, None)
        
        elif self.strategy == CacheStrategy.FIFO:
            # Remove oldest entry
            if self._cache:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k].created_at)
                del self._cache[oldest_key]
                self._access_order.pop(oldest_key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._access_order.pop(key, None)
                return None
            
            entry.touch()
            
            # Update access order for LRU
            if self.strategy == CacheStrategy.LRU:
                self._access_order.move_to_end(key)
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache."""
        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                del self._cache[key]
                self._access_order.pop(key, None)
            
            # Evict if needed
            self._evict_if_needed()
            
            # Add new entry
            entry = CacheEntry(key, value, ttl)
            self._cache[key] = entry
            
            if self.strategy == CacheStrategy.LRU:
                self._access_order[key] = True
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.pop(key, None)
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            
            if entry.is_expired():
                del self._cache[key]
                self._access_order.pop(key, None)
                return False
            
            return True
    
    def get_size(self) -> int:
        """Get number of items in cache."""
        with self._lock:
            return len(self._cache)
    
    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())
    
    def stop(self):
        """Stop the cleanup thread."""
        self._stop_cleanup.set()
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)


try:
    import redis
    
    class RedisCacheBackend(CacheBackend):
        """Redis-based distributed cache backend."""
        
        def __init__(self, host: str = 'localhost', port: int = 6379, 
                     db: int = 0, password: Optional[str] = None,
                     key_prefix: str = 'test_cache:'):
            self.key_prefix = key_prefix
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, password=password,
                decode_responses=False  # We'll handle encoding ourselves
            )
            
            # Test connection
            self.redis_client.ping()
        
        def _make_key(self, key: str) -> str:
            """Create prefixed key."""
            return f"{self.key_prefix}{key}"
        
        def _serialize(self, value: Any) -> bytes:
            """Serialize value for storage."""
            return pickle.dumps(value)
        
        def _deserialize(self, data: bytes) -> Any:
            """Deserialize value from storage."""
            return pickle.loads(data)
        
        def get(self, key: str) -> Optional[Any]:
            """Get value from cache."""
            try:
                data = self.redis_client.get(self._make_key(key))
                if data is None:
                    return None
                return self._deserialize(data)
            except Exception:
                return None
        
        def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
            """Set value in cache."""
            try:
                serialized = self._serialize(value)
                redis_key = self._make_key(key)
                
                if ttl:
                    return self.redis_client.setex(redis_key, int(ttl), serialized)
                else:
                    return self.redis_client.set(redis_key, serialized)
            except Exception:
                return False
        
        def delete(self, key: str) -> bool:
            """Delete value from cache."""
            try:
                return bool(self.redis_client.delete(self._make_key(key)))
            except Exception:
                return False
        
        def clear(self) -> bool:
            """Clear all cache entries with our prefix."""
            try:
                pattern = f"{self.key_prefix}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    return bool(self.redis_client.delete(*keys))
                return True
            except Exception:
                return False
        
        def exists(self, key: str) -> bool:
            """Check if key exists in cache."""
            try:
                return bool(self.redis_client.exists(self._make_key(key)))
            except Exception:
                return False
        
        def get_size(self) -> int:
            """Get number of items in cache."""
            try:
                pattern = f"{self.key_prefix}*"
                return len(self.redis_client.keys(pattern))
            except Exception:
                return 0
        
        def get_keys(self) -> List[str]:
            """Get all cache keys."""
            try:
                pattern = f"{self.key_prefix}*"
                redis_keys = self.redis_client.keys(pattern)
                # Remove prefix from keys
                return [key.decode('utf-8').replace(self.key_prefix, '') 
                       for key in redis_keys]
            except Exception:
                return []

except ImportError:
    # Redis not available
    class RedisCacheBackend(CacheBackend):
        def __init__(self, *args, **kwargs):
            raise ImportError("Redis not available. Install redis-py to use Redis cache backend.")
        
        def get(self, key: str) -> Optional[Any]: pass
        def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool: pass
        def delete(self, key: str) -> bool: pass
        def clear(self) -> bool: pass
        def exists(self, key: str) -> bool: pass
        def get_size(self) -> int: pass
        def get_keys(self) -> List[str]: pass


class CacheManager:
    """Advanced cache manager with multiple backends and strategies."""
    
    def __init__(self, backend: Optional[CacheBackend] = None, 
                 enable_stats: bool = True):
        self.backend = backend or MemoryCacheBackend()
        self.enable_stats = enable_stats
        self.stats = CacheStats() if enable_stats else None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Cache warming configuration
        self.warming_functions: Dict[str, Callable] = {}
        self.warming_enabled = False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            value = self.backend.get(key)
            if value is not None:
                if self.stats:
                    self.stats.record_hit()
                self.logger.debug(f"Cache hit for key: {key}")
                return value
            
            if self.stats:
                self.stats.record_miss()
            self.logger.debug(f"Cache miss for key: {key}")
            return default
            
        except Exception as e:
            self.logger.error(f"Cache get error for key {key}: {e}")
            if self.stats:
                self.stats.record_miss()
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache."""
        try:
            success = self.backend.set(key, value, ttl)
            if success and self.stats:
                self.stats.record_set()
                self.stats.update_size(self.backend.get_size())
            self.logger.debug(f"Cache set for key: {key}, TTL: {ttl}")
            return success
            
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            success = self.backend.delete(key)
            if success and self.stats:
                self.stats.record_delete()
                self.stats.update_size(self.backend.get_size())
            self.logger.debug(f"Cache delete for key: {key}")
            return success
            
        except Exception as e:
            self.logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            success = self.backend.clear()
            if success and self.stats:
                self.stats.update_size(0)
            self.logger.info("Cache cleared")
            return success
            
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return self.backend.exists(key)
        except Exception as e:
            self.logger.error(f"Cache exists check error for key {key}: {e}")
            return False
    
    def get_size(self) -> int:
        """Get number of items in cache."""
        try:
            return self.backend.get_size()
        except Exception as e:
            self.logger.error(f"Cache size check error: {e}")
            return 0
    
    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        try:
            return self.backend.get_keys()
        except Exception as e:
            self.logger.error(f"Cache keys retrieval error: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.stats:
            return {}
        
        base_stats = self.stats.get_stats()
        base_stats['current_size'] = self.get_size()
        return base_stats
    
    def reset_stats(self):
        """Reset cache statistics."""
        if self.stats:
            self.stats.reset()
    
    def warm_cache(self, keys: Optional[List[str]] = None):
        """Warm up cache with predefined data."""
        if not self.warming_enabled:
            return
        
        if keys is None:
            keys = list(self.warming_functions.keys())
        
        for key in keys:
            if key in self.warming_functions:
                try:
                    value = self.warming_functions[key]()
                    self.set(key, value)
                    self.logger.debug(f"Cache warmed for key: {key}")
                except Exception as e:
                    self.logger.error(f"Cache warming error for key {key}: {e}")
    
    def register_warming_function(self, key: str, func: Callable):
        """Register a function for cache warming."""
        self.warming_functions[key] = func
        self.logger.debug(f"Cache warming function registered for key: {key}")
    
    def enable_warming(self):
        """Enable cache warming."""
        self.warming_enabled = True
        self.logger.info("Cache warming enabled")
    
    def disable_warming(self):
        """Disable cache warming."""
        self.warming_enabled = False
        self.logger.info("Cache warming disabled")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching a pattern."""
        keys_to_delete = []
        for key in self.get_keys():
            if pattern in key:  # Simple pattern matching
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.delete(key)
        
        self.logger.info(f"Invalidated {len(keys_to_delete)} keys matching pattern: {pattern}")
    
    def get_or_set(self, key: str, func: Callable, ttl: Optional[float] = None) -> Any:
        """Get from cache or set if not present."""
        value = self.get(key)
        if value is not None:
            return value
        
        # Generate value and cache it
        try:
            value = func()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            self.logger.error(f"Error generating value for cache key {key}: {e}")
            raise


def cache_result(cache_manager: CacheManager, key_func: Optional[Callable] = None, 
                ttl: Optional[float] = None):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{func.__name__}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            # Try to get from cache
            result = cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def cache_test_data(cache_manager: CacheManager, ttl: float = 3600):
    """Decorator specifically for caching test data."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate key based on function name and test context
            test_context = kwargs.get('test_context', 'default')
            cache_key = f"test_data:{func.__name__}:{test_context}"
            
            return cache_manager.get_or_set(cache_key, lambda: func(*args, **kwargs), ttl)
        
        return wrapper
    return decorator


# Global cache manager instance
_global_cache_manager = None


def get_global_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager


def set_global_cache_backend(backend: CacheBackend):
    """Set the global cache backend."""
    global _global_cache_manager
    _global_cache_manager = CacheManager(backend)


# Convenience functions for global cache
def cache_get(key: str, default: Any = None) -> Any:
    """Get value from global cache."""
    return get_global_cache_manager().get(key, default)


def cache_set(key: str, value: Any, ttl: Optional[float] = None) -> bool:
    """Set value in global cache."""
    return get_global_cache_manager().set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete value from global cache."""
    return get_global_cache_manager().delete(key)


def cache_clear() -> bool:
    """Clear global cache."""
    return get_global_cache_manager().clear()

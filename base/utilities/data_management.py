"""
Memory-Efficient Data Management Module

This module provides memory-efficient data structures and operations including:
- Streaming for large datasets
- Data pagination support  
- Memory-efficient data structures
- Data compression utilities
- Memory usage limits and monitoring
"""

import gzip
import zlib
import pickle
import json
import csv
import sqlite3
import threading
import logging
import weakref
from typing import Iterator, List, Dict, Any, Optional, Union, Callable, Generator
from dataclasses import dataclass
from collections import deque, defaultdict
from contextlib import contextmanager
from io import StringIO, BytesIO
import psutil
import sys
import gc
from abc import ABC, abstractmethod


@dataclass
class MemoryLimit:
    """Memory limit configuration"""
    max_memory_mb: float
    warning_threshold: float = 0.8  # 80% of max
    cleanup_threshold: float = 0.9  # 90% of max
    check_interval: int = 10  # seconds


class MemoryLimitExceeded(Exception):
    """Raised when memory usage exceeds configured limits"""
    pass


class LimitedMemoryMonitor:
    """Monitor and enforce memory limits"""
    
    def __init__(self, memory_limit: MemoryLimit):
        self.memory_limit = memory_limit
        self.logger = logging.getLogger(self.__class__.__name__)
        self.callbacks = []
        self._monitoring = False
        self._monitor_thread = None
    
    def add_cleanup_callback(self, callback: Callable):
        """Add cleanup callback for when memory threshold is reached"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Start memory monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self.logger.info("Memory monitoring stopped")
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage against limits"""
        process = psutil.Process()
        current_mb = process.memory_info().rss / 1024 / 1024
        usage_ratio = current_mb / self.memory_limit.max_memory_mb
        
        status = {
            'current_mb': current_mb,
            'max_mb': self.memory_limit.max_memory_mb,
            'usage_ratio': usage_ratio,
            'status': 'ok'
        }
        
        if usage_ratio >= 1.0:
            status['status'] = 'exceeded'
            raise MemoryLimitExceeded(f"Memory usage {current_mb:.1f}MB exceeds limit {self.memory_limit.max_memory_mb}MB")
        elif usage_ratio >= self.memory_limit.cleanup_threshold:
            status['status'] = 'cleanup_needed'
            self._trigger_cleanup()
        elif usage_ratio >= self.memory_limit.warning_threshold:
            status['status'] = 'warning'
            self.logger.warning(f"Memory usage {current_mb:.1f}MB approaching limit {self.memory_limit.max_memory_mb}MB")
        
        return status
    
    def _monitor_worker(self):
        """Background monitoring worker"""
        import time
        while self._monitoring:
            try:
                self.check_memory_usage()
                time.sleep(self.memory_limit.check_interval)
            except MemoryLimitExceeded:
                self.logger.error("Memory limit exceeded")
                break
            except Exception as e:
                self.logger.error(f"Error in memory monitoring: {e}")
    
    def _trigger_cleanup(self):
        """Trigger cleanup callbacks"""
        self.logger.warning("Memory cleanup threshold reached, triggering cleanup")
        for callback in self.callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in cleanup callback: {e}")
        
        # Force garbage collection
        gc.collect()


class DataStreamProcessor:
    """Process data in streaming fashion to minimize memory usage"""
    
    def __init__(self, chunk_size: int = 1000, memory_monitor: LimitedMemoryMonitor = None):
        self.chunk_size = chunk_size
        self.memory_monitor = memory_monitor
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def stream_from_file(self, filepath: str, file_type: str = 'auto') -> Iterator[Any]:
        """Stream data from file in chunks"""
        if file_type == 'auto':
            file_type = self._detect_file_type(filepath)
        
        if file_type == 'json':
            yield from self._stream_json(filepath)
        elif file_type == 'csv':
            yield from self._stream_csv(filepath)
        elif file_type == 'txt':
            yield from self._stream_text(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _detect_file_type(self, filepath: str) -> str:
        """Detect file type from extension"""
        ext = filepath.lower().split('.')[-1]
        type_map = {
            'json': 'json',
            'csv': 'csv',
            'txt': 'txt',
            'log': 'txt'
        }
        return type_map.get(ext, 'txt')
    
    def _stream_json(self, filepath: str) -> Iterator[Dict[str, Any]]:
        """Stream JSON data line by line"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if self.memory_monitor:
                    self.memory_monitor.check_memory_usage()
                
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON at line {line_num}: {e}")
    
    def _stream_csv(self, filepath: str) -> Iterator[Dict[str, Any]]:
        """Stream CSV data row by row"""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 1):
                if self.memory_monitor:
                    self.memory_monitor.check_memory_usage()
                
                yield dict(row)
    
    def _stream_text(self, filepath: str) -> Iterator[str]:
        """Stream text data line by line"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if self.memory_monitor:
                    self.memory_monitor.check_memory_usage()
                
                yield line.rstrip('\n\r')
    
    def process_in_chunks(self, data_source: Iterator[Any], 
                         processor: Callable[[List[Any]], Any]) -> Iterator[Any]:
        """Process data in chunks to limit memory usage"""
        chunk = []
        
        for item in data_source:
            chunk.append(item)
            
            if len(chunk) >= self.chunk_size:
                if self.memory_monitor:
                    self.memory_monitor.check_memory_usage()
                
                yield processor(chunk)
                chunk = []
        
        # Process remaining items
        if chunk:
            yield processor(chunk)
    
    def aggregate_streaming(self, data_source: Iterator[Dict[str, Any]], 
                          aggregations: Dict[str, Callable]) -> Dict[str, Any]:
        """Perform aggregations on streaming data"""
        results = {key: None for key in aggregations.keys()}
        accumulators = {}
        
        for item in data_source:
            if self.memory_monitor:
                self.memory_monitor.check_memory_usage()
            
            for key, agg_func in aggregations.items():
                if key not in accumulators:
                    accumulators[key] = []
                
                # Extract value for aggregation
                value = item.get(key)
                if value is not None:
                    accumulators[key].append(value)
                    
                    # Apply aggregation periodically to limit memory
                    if len(accumulators[key]) >= self.chunk_size:
                        current_result = agg_func(accumulators[key])
                        accumulators[key] = [current_result] if current_result is not None else []
        
        # Final aggregation
        for key, agg_func in aggregations.items():
            if key in accumulators and accumulators[key]:
                results[key] = agg_func(accumulators[key])
        
        return results


class Paginator:
    """Handle pagination for large datasets"""
    
    def __init__(self, data_source: Union[List, Iterator, Callable], 
                 page_size: int = 100, total_count: int = None):
        self.data_source = data_source
        self.page_size = page_size
        self.total_count = total_count
        self.current_page = 0
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_page(self, page_number: int) -> Dict[str, Any]:
        """Get specific page of data"""
        if isinstance(self.data_source, list):
            return self._get_page_from_list(page_number)
        elif callable(self.data_source):
            return self._get_page_from_callable(page_number)
        else:
            return self._get_page_from_iterator(page_number)
    
    def _get_page_from_list(self, page_number: int) -> Dict[str, Any]:
        """Get page from list data source"""
        start_idx = page_number * self.page_size
        end_idx = start_idx + self.page_size
        
        page_data = self.data_source[start_idx:end_idx]
        
        return {
            'page_number': page_number,
            'page_size': self.page_size,
            'data': page_data,
            'has_next': end_idx < len(self.data_source),
            'has_previous': page_number > 0,
            'total_count': len(self.data_source),
            'total_pages': (len(self.data_source) + self.page_size - 1) // self.page_size
        }
    
    def _get_page_from_callable(self, page_number: int) -> Dict[str, Any]:
        """Get page from callable data source"""
        page_data = self.data_source(page_number, self.page_size)
        
        return {
            'page_number': page_number,
            'page_size': self.page_size,
            'data': page_data,
            'has_next': len(page_data) == self.page_size,
            'has_previous': page_number > 0,
            'total_count': self.total_count,
            'total_pages': (self.total_count + self.page_size - 1) // self.page_size if self.total_count else None
        }
    
    def _get_page_from_iterator(self, page_number: int) -> Dict[str, Any]:
        """Get page from iterator data source"""
        # Skip to the desired page
        skip_count = page_number * self.page_size
        page_data = []
        
        for i, item in enumerate(self.data_source):
            if i < skip_count:
                continue
            
            page_data.append(item)
            
            if len(page_data) >= self.page_size:
                break
        
        return {
            'page_number': page_number,
            'page_size': self.page_size,
            'data': page_data,
            'has_next': len(page_data) == self.page_size,
            'has_previous': page_number > 0,
            'total_count': self.total_count,
            'total_pages': None  # Cannot determine from iterator
        }
    
    def iter_pages(self) -> Iterator[Dict[str, Any]]:
        """Iterate through all pages"""
        page_num = 0
        while True:
            page = self.get_page(page_num)
            if not page['data']:
                break
            
            yield page
            
            if not page['has_next']:
                break
            
            page_num += 1


class MemoryEfficientCache:
    """Memory-efficient cache with automatic cleanup"""
    
    def __init__(self, max_items: int = 1000, max_memory_mb: float = 100):
        self.max_items = max_items
        self.max_memory_mb = max_memory_mb
        self.cache = {}
        self.access_order = deque()
        self.memory_usage = 0
        self.lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get(self, key: str) -> Any:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]['value']
            return None
    
    def put(self, key: str, value: Any):
        """Put item in cache with automatic cleanup"""
        with self.lock:
            # Calculate item size
            item_size = sys.getsizeof(value) / 1024 / 1024  # MB
            
            # Remove existing item if updating
            if key in self.cache:
                old_size = self.cache[key]['size']
                self.memory_usage -= old_size
                self.access_order.remove(key)
            
            # Check if we need to make room
            while (len(self.cache) >= self.max_items or 
                   self.memory_usage + item_size > self.max_memory_mb):
                self._evict_lru()
            
            # Add new item
            self.cache[key] = {
                'value': value,
                'size': item_size
            }
            self.access_order.append(key)
            self.memory_usage += item_size
            
            self.logger.debug(f"Cache: added {key} ({item_size:.2f}MB), total: {self.memory_usage:.2f}MB")
    
    def remove(self, key: str):
        """Remove item from cache"""
        with self.lock:
            if key in self.cache:
                item_size = self.cache[key]['size']
                del self.cache[key]
                self.access_order.remove(key)
                self.memory_usage -= item_size
    
    def clear(self):
        """Clear all cache items"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.memory_usage = 0
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order.popleft()
            item_size = self.cache[lru_key]['size']
            del self.cache[lru_key]
            self.memory_usage -= item_size
            self.logger.debug(f"Cache: evicted LRU item {lru_key} ({item_size:.2f}MB)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'items': len(self.cache),
                'max_items': self.max_items,
                'memory_mb': self.memory_usage,
                'max_memory_mb': self.max_memory_mb,
                'utilization': len(self.cache) / self.max_items,
                'memory_utilization': self.memory_usage / self.max_memory_mb
            }


class CompressedDataStore:
    """Store data with automatic compression to save memory"""
    
    def __init__(self, compression_type: str = 'gzip', compression_level: int = 6):
        self.compression_type = compression_type.lower()
        self.compression_level = compression_level
        self.data_store = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if self.compression_type not in ['gzip', 'zlib', 'none']:
            raise ValueError(f"Unsupported compression type: {compression_type}")
    
    def store(self, key: str, data: Any) -> Dict[str, Any]:
        """Store data with compression"""
        with self.lock:
            # Serialize data
            serialized = pickle.dumps(data)
            original_size = len(serialized)
            
            # Compress if enabled
            if self.compression_type == 'gzip':
                compressed = gzip.compress(serialized, compresslevel=self.compression_level)
            elif self.compression_type == 'zlib':
                compressed = zlib.compress(serialized, level=self.compression_level)
            else:
                compressed = serialized
            
            compressed_size = len(compressed)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            self.data_store[key] = {
                'data': compressed,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio
            }
            
            stats = {
                'key': key,
                'original_size_mb': original_size / 1024 / 1024,
                'compressed_size_mb': compressed_size / 1024 / 1024,
                'compression_ratio': compression_ratio,
                'space_saved_mb': (original_size - compressed_size) / 1024 / 1024
            }
            
            self.logger.debug(f"Stored compressed data: {stats}")
            return stats
    
    def retrieve(self, key: str) -> Any:
        """Retrieve and decompress data"""
        with self.lock:
            if key not in self.data_store:
                return None
            
            compressed_data = self.data_store[key]['data']
            
            # Decompress if needed
            if self.compression_type == 'gzip':
                decompressed = gzip.decompress(compressed_data)
            elif self.compression_type == 'zlib':
                decompressed = zlib.decompress(compressed_data)
            else:
                decompressed = compressed_data
            
            # Deserialize
            return pickle.loads(decompressed)
    
    def remove(self, key: str):
        """Remove stored data"""
        with self.lock:
            if key in self.data_store:
                del self.data_store[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        with self.lock:
            if not self.data_store:
                return {}
            
            total_original = sum(item['original_size'] for item in self.data_store.values())
            total_compressed = sum(item['compressed_size'] for item in self.data_store.values())
            
            return {
                'items': len(self.data_store),
                'total_original_mb': total_original / 1024 / 1024,
                'total_compressed_mb': total_compressed / 1024 / 1024,
                'overall_compression_ratio': total_compressed / total_original if total_original > 0 else 1.0,
                'total_space_saved_mb': (total_original - total_compressed) / 1024 / 1024,
                'compression_type': self.compression_type,
                'compression_level': self.compression_level
            }


class MemoryEfficientDataManager:
    """Main manager for memory-efficient data operations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize memory monitoring
        memory_limit = MemoryLimit(
            max_memory_mb=self.config.get('max_memory_mb', 1000),
            warning_threshold=self.config.get('warning_threshold', 0.8),
            cleanup_threshold=self.config.get('cleanup_threshold', 0.9)
        )
        self.memory_monitor = LimitedMemoryMonitor(memory_limit)
        
        # Initialize components
        self.stream_processor = DataStreamProcessor(
            chunk_size=self.config.get('chunk_size', 1000),
            memory_monitor=self.memory_monitor
        )
        
        self.cache = MemoryEfficientCache(
            max_items=self.config.get('cache_max_items', 1000),
            max_memory_mb=self.config.get('cache_max_memory_mb', 100)
        )
        
        self.compressed_store = CompressedDataStore(
            compression_type=self.config.get('compression_type', 'gzip'),
            compression_level=self.config.get('compression_level', 6)
        )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup cleanup callbacks
        self.memory_monitor.add_cleanup_callback(self._cleanup_callback)
        
        # Start monitoring if enabled
        if self.config.get('enable_monitoring', True):
            self.memory_monitor.start_monitoring()
    
    def _cleanup_callback(self):
        """Cleanup callback for memory pressure"""
        self.logger.warning("Memory cleanup triggered")
        
        # Clear cache
        cache_stats = self.cache.get_stats()
        self.cache.clear()
        self.logger.info(f"Cleared cache: freed {cache_stats['memory_mb']:.2f}MB")
        
        # Force garbage collection
        gc.collect()
    
    def create_paginator(self, data_source: Any, page_size: int = 100, 
                        total_count: int = None) -> Paginator:
        """Create paginator for large datasets"""
        return Paginator(data_source, page_size, total_count)
    
    def stream_file(self, filepath: str, file_type: str = 'auto') -> Iterator[Any]:
        """Stream data from file"""
        return self.stream_processor.stream_from_file(filepath, file_type)
    
    def process_in_chunks(self, data_source: Iterator[Any], 
                         processor: Callable[[List[Any]], Any]) -> Iterator[Any]:
        """Process data in memory-efficient chunks"""
        return self.stream_processor.process_in_chunks(data_source, processor)
    
    def cache_data(self, key: str, data: Any):
        """Cache data with memory management"""
        self.cache.put(key, data)
    
    def get_cached_data(self, key: str) -> Any:
        """Retrieve cached data"""
        return self.cache.get(key)
    
    def store_compressed(self, key: str, data: Any) -> Dict[str, Any]:
        """Store data with compression"""
        return self.compressed_store.store(key, data)
    
    def retrieve_compressed(self, key: str) -> Any:
        """Retrieve compressed data"""
        return self.compressed_store.retrieve(key)
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get comprehensive memory status"""
        return {
            'memory_monitor': self.memory_monitor.check_memory_usage(),
            'cache_stats': self.cache.get_stats(),
            'compression_stats': self.compressed_store.get_stats(),
            'system_memory': {
                'available_mb': psutil.virtual_memory().available / 1024 / 1024,
                'percent_used': psutil.virtual_memory().percent
            }
        }
    
    def cleanup(self):
        """Manual cleanup of resources"""
        self.memory_monitor.stop_monitoring()
        self.cache.clear()
        self.logger.info("Memory-efficient data manager cleanup completed")


# Global instance
_global_data_manager = None


def get_data_manager(config: Dict[str, Any] = None) -> MemoryEfficientDataManager:
    """Get global data manager instance"""
    global _global_data_manager
    if _global_data_manager is None:
        _global_data_manager = MemoryEfficientDataManager(config)
    return _global_data_manager


# Convenience functions
def create_paginator(data_source: Any, page_size: int = 100) -> Paginator:
    """Create paginator for data source"""
    return get_data_manager().create_paginator(data_source, page_size)


def stream_large_file(filepath: str, file_type: str = 'auto') -> Iterator[Any]:
    """Stream large file efficiently"""
    return get_data_manager().stream_file(filepath, file_type)


def cache_with_memory_limit(key: str, data: Any):
    """Cache data with automatic memory management"""
    get_data_manager().cache_data(key, data)


def get_from_cache(key: str) -> Any:
    """Get data from memory-managed cache"""
    return get_data_manager().get_cached_data(key)


def compress_and_store(key: str, data: Any) -> Dict[str, Any]:
    """Compress and store large data"""
    return get_data_manager().store_compressed(key, data)


def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics"""
    return get_data_manager().get_memory_status()

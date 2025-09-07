"""Advanced logging utilities for the test automation framework.

This module provides comprehensive logging capabilities including:
- Structured logging with JSON formatting
- Log correlation IDs for tracing
- Log aggregation support
- Log filtering and routing
- Context injection and management
- Sensitive data masking
"""

import json
import logging
import logging.handlers
import time
import threading
import uuid
import traceback
import inspect
import re
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime
from enum import Enum
from contextlib import contextmanager
from functools import wraps
from pathlib import Path


class LogLevel(Enum):
    """Enhanced log levels."""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class CorrelationContext:
    """Thread-local storage for correlation IDs and context."""
    
    def __init__(self):
        self._local = threading.local()
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current thread."""
        self._local.correlation_id = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Get correlation ID for current thread."""
        return getattr(self._local, 'correlation_id', None)
    
    def set_context(self, key: str, value: Any):
        """Set context value for current thread."""
        if not hasattr(self._local, 'context'):
            self._local.context = {}
        self._local.context[key] = value
    
    def get_context(self, key: str = None) -> Union[Any, Dict[str, Any]]:
        """Get context value(s) for current thread."""
        context = getattr(self._local, 'context', {})
        if key is None:
            return context
        return context.get(key)
    
    def clear_context(self):
        """Clear all context for current thread."""
        if hasattr(self._local, 'context'):
            self._local.context.clear()
    
    def clear_correlation_id(self):
        """Clear correlation ID for current thread."""
        if hasattr(self._local, 'correlation_id'):
            delattr(self._local, 'correlation_id')


# Global correlation context
correlation_context = CorrelationContext()


class SensitiveDataMasker:
    """Mask sensitive data in log messages."""
    
    def __init__(self):
        self.patterns = [
            # Passwords
            (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'\\s]+)', re.IGNORECASE), r'\1***MASKED***'),
            # API Keys
            (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\\s]+)', re.IGNORECASE), r'\1***MASKED***'),
            # Tokens
            (re.compile(r'(token["\']?\s*[:=]\s*["\']?)([^"\'\\s]+)', re.IGNORECASE), r'\1***MASKED***'),
            # Credit card numbers
            (re.compile(r'\b(\d{4}[-\\s]?\d{4}[-\\s]?\d{4}[-\\s]?\d{4})\b'), r'****-****-****-****'),
            # Social Security Numbers
            (re.compile(r'\b(\d{3}[-\\s]?\d{2}[-\\s]?\d{4})\b'), r'***-**-****'),
            # Email addresses (partial masking)
            (re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'), 
             lambda m: f"{m.group(1)[:2]}***@{m.group(2)}"),
        ]
        self.custom_patterns = []
    
    def add_pattern(self, pattern: str, replacement: str):
        """Add custom masking pattern."""
        self.custom_patterns.append((re.compile(pattern, re.IGNORECASE), replacement))
    
    def mask_data(self, text: str) -> str:
        """Mask sensitive data in text."""
        if not isinstance(text, str):
            text = str(text)
        
        # Apply built-in patterns
        for pattern, replacement in self.patterns:
            if callable(replacement):
                text = pattern.sub(replacement, text)
            else:
                text = pattern.sub(replacement, text)
        
        # Apply custom patterns
        for pattern, replacement in self.custom_patterns:
            text = pattern.sub(replacement, text)
        
        return text


class JsonFormatter(logging.Formatter):
    """JSON log formatter with correlation IDs and context."""
    
    def __init__(self, include_context: bool = True, 
                 mask_sensitive_data: bool = True):
        super().__init__()
        self.include_context = include_context
        self.mask_sensitive_data = mask_sensitive_data
        self.masker = SensitiveDataMasker() if mask_sensitive_data else None
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log data
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
        }
        
        # Add correlation ID if available
        correlation_id = correlation_context.get_correlation_id()
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        # Add context if enabled
        if self.include_context:
            context = correlation_context.get_context()
            if context:
                log_data['context'] = context
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                             'pathname', 'filename', 'module', 'lineno', 
                             'funcName', 'created', 'msecs', 'relativeCreated',
                             'thread', 'threadName', 'processName', 'process',
                             'stack_info', 'exc_info', 'exc_text']:
                    log_data['extra'] = log_data.get('extra', {})
                    log_data['extra'][key] = value
        
        # Convert to JSON string
        json_str = json.dumps(log_data, default=str, ensure_ascii=False)
        
        # Mask sensitive data if enabled
        if self.mask_sensitive_data and self.masker:
            json_str = self.masker.mask_data(json_str)
        
        return json_str


class ContextFilter(logging.Filter):
    """Filter to add automatic context to log records."""
    
    def __init__(self, auto_inject_context: bool = True):
        super().__init__()
        self.auto_inject_context = auto_inject_context
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to log record."""
        if self.auto_inject_context:
            # Add correlation ID
            correlation_id = correlation_context.get_correlation_id()
            if correlation_id:
                record.correlation_id = correlation_id
            
            # Add test context if available
            test_context = correlation_context.get_context('test_name')
            if test_context:
                record.test_name = test_context
            
            # Add environment context
            env_context = correlation_context.get_context('environment')
            if env_context:
                record.environment = env_context
            
            # Add performance metrics if available
            perf_context = correlation_context.get_context('performance')
            if perf_context:
                record.performance = perf_context
        
        return True


class LogAggregator:
    """Aggregate logs for analysis and reporting."""
    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.log_entries: List[Dict[str, Any]] = []
        self.stats = {
            'total_logs': 0,
            'by_level': {},
            'by_module': {},
            'errors': [],
            'warnings': []
        }
        self._lock = threading.Lock()
    
    def add_log_entry(self, record: logging.LogRecord):
        """Add log entry to aggregator."""
        with self._lock:
            entry = {
                'timestamp': datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'correlation_id': correlation_context.get_correlation_id()
            }
            
            # Add to entries list
            self.log_entries.append(entry)
            if len(self.log_entries) > self.max_entries:
                self.log_entries.pop(0)
            
            # Update statistics
            self.stats['total_logs'] += 1
            self.stats['by_level'][record.levelname] = \
                self.stats['by_level'].get(record.levelname, 0) + 1
            self.stats['by_module'][record.module] = \
                self.stats['by_module'].get(record.module, 0) + 1
            
            # Track errors and warnings
            if record.levelname == 'ERROR':
                self.stats['errors'].append(entry)
                if len(self.stats['errors']) > 100:  # Keep last 100 errors
                    self.stats['errors'].pop(0)
            elif record.levelname == 'WARNING':
                self.stats['warnings'].append(entry)
                if len(self.stats['warnings']) > 100:  # Keep last 100 warnings
                    self.stats['warnings'].pop(0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated log statistics."""
        with self._lock:
            return {
                'total_logs': self.stats['total_logs'],
                'by_level': dict(self.stats['by_level']),
                'by_module': dict(self.stats['by_module']),
                'recent_errors': len(self.stats['errors']),
                'recent_warnings': len(self.stats['warnings']),
                'current_entries': len(self.log_entries)
            }
    
    def get_recent_logs(self, count: int = 100, level: str = None) -> List[Dict[str, Any]]:
        """Get recent log entries."""
        with self._lock:
            entries = self.log_entries[-count:] if count else self.log_entries
            if level:
                entries = [e for e in entries if e['level'] == level]
            return entries


class AggregatorHandler(logging.Handler):
    """Logging handler that feeds into log aggregator."""
    
    def __init__(self, aggregator: LogAggregator):
        super().__init__()
        self.aggregator = aggregator
    
    def emit(self, record: logging.LogRecord):
        """Emit log record to aggregator."""
        try:
            self.aggregator.add_log_entry(record)
        except Exception:
            self.handleError(record)


class LogRouter:
    """Route logs based on criteria."""
    
    def __init__(self):
        self.routes: List[Dict[str, Any]] = []
    
    def add_route(self, filter_func: Callable[[logging.LogRecord], bool], 
                  handler: logging.Handler):
        """Add routing rule."""
        self.routes.append({
            'filter': filter_func,
            'handler': handler
        })
    
    def route_record(self, record: logging.LogRecord):
        """Route log record to appropriate handlers."""
        for route in self.routes:
            try:
                if route['filter'](record):
                    route['handler'].emit(record)
            except Exception as e:
                # Handle routing errors gracefully
                logging.getLogger(__name__).error(f"Log routing error: {e}")


class StructuredLogger:
    """Main structured logger class."""
    
    def __init__(self, name: str, level: int = logging.INFO,
                 use_json_formatter: bool = True,
                 enable_correlation: bool = True,
                 enable_aggregation: bool = True,
                 log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set up formatters
        if use_json_formatter:
            formatter = JsonFormatter(
                include_context=enable_correlation,
                mask_sensitive_data=True
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        if enable_correlation:
            console_handler.addFilter(ContextFilter())
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            if enable_correlation:
                file_handler.addFilter(ContextFilter())
            self.logger.addHandler(file_handler)
        
        # Aggregation
        if enable_aggregation:
            self.aggregator = LogAggregator()
            aggregator_handler = AggregatorHandler(self.aggregator)
            self.logger.addHandler(aggregator_handler)
        else:
            self.aggregator = None
        
        self.router = LogRouter()
    
    def add_handler(self, handler: logging.Handler):
        """Add custom handler."""
        self.logger.addHandler(handler)
    
    def add_route(self, filter_func: Callable[[logging.LogRecord], bool], 
                  handler: logging.Handler):
        """Add routing rule."""
        self.router.add_route(filter_func, handler)
    
    def trace(self, message: str, **kwargs):
        """Log trace message."""
        self.logger.log(LogLevel.TRACE.value, message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message."""
        if exception:
            kwargs['exception_type'] = type(exception).__name__
            kwargs['exception_message'] = str(exception)
        self.logger.error(message, exc_info=exception is not None, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Get log statistics."""
        return self.aggregator.get_statistics() if self.aggregator else None


# Context managers and decorators

@contextmanager
def log_context(**context_vars):
    """Context manager for adding context to logs."""
    # Store previous context
    previous_context = {}
    for key, value in context_vars.items():
        previous_context[key] = correlation_context.get_context(key)
        correlation_context.set_context(key, value)
    
    try:
        yield
    finally:
        # Restore previous context
        for key, value in previous_context.items():
            if value is None:
                correlation_context.set_context(key, None)
            else:
                correlation_context.set_context(key, value)


@contextmanager
def correlation_id(correlation_id: str = None):
    """Context manager for correlation ID."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    previous_id = correlation_context.get_correlation_id()
    correlation_context.set_correlation_id(correlation_id)
    
    try:
        yield correlation_id
    finally:
        if previous_id:
            correlation_context.set_correlation_id(previous_id)
        else:
            correlation_context.clear_correlation_id()


def log_performance(logger: StructuredLogger):
    """Decorator to log method performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            method_name = f"{func.__module__}.{func.__qualname__}"
            
            logger.debug(f"Starting {method_name}", method=method_name)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Completed {method_name}",
                    method=method_name,
                    execution_time=execution_time,
                    status="success"
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Failed {method_name}",
                    method=method_name,
                    execution_time=execution_time,
                    status="error",
                    exception=e
                )
                raise
        
        return wrapper
    return decorator


def log_method_calls(logger: StructuredLogger, include_args: bool = False):
    """Decorator to log method calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            method_name = f"{func.__module__}.{func.__qualname__}"
            
            log_data = {
                'method': method_name,
                'action': 'call'
            }
            
            if include_args:
                # Be careful with sensitive data
                log_data['args_count'] = len(args)
                log_data['kwargs_keys'] = list(kwargs.keys())
            
            logger.debug(f"Calling {method_name}", **log_data)
            
            try:
                result = func(*args, **kwargs)
                logger.trace(f"Returned from {method_name}", method=method_name, action='return')
                return result
            except Exception as e:
                logger.error(f"Exception in {method_name}", method=method_name, action='exception', exception=e)
                raise
        
        return wrapper
    return decorator


# Global logger factory
_loggers: Dict[str, StructuredLogger] = {}
_default_config = {
    'level': logging.INFO,
    'use_json_formatter': True,
    'enable_correlation': True,
    'enable_aggregation': True,
    'log_file': None
}


def configure_logging(**config):
    """Configure global logging settings."""
    global _default_config
    _default_config.update(config)


def get_logger(name: str, **config) -> StructuredLogger:
    """Get or create structured logger."""
    if name not in _loggers:
        final_config = _default_config.copy()
        final_config.update(config)
        _loggers[name] = StructuredLogger(name, **final_config)
    return _loggers[name]


# Convenience functions
def set_global_correlation_id(correlation_id: str = None):
    """Set global correlation ID."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_context.set_correlation_id(correlation_id)
    return correlation_id


def get_global_correlation_id() -> Optional[str]:
    """Get global correlation ID."""
    return correlation_context.get_correlation_id()


def add_global_context(key: str, value: Any):
    """Add global context."""
    correlation_context.set_context(key, value)


def clear_global_context():
    """Clear global context."""
    correlation_context.clear_context()
    correlation_context.clear_correlation_id()


def get_log_statistics() -> Dict[str, Any]:
    """Get aggregated statistics from all loggers."""
    stats = {}
    for name, logger in _loggers.items():
        logger_stats = logger.get_statistics()
        if logger_stats:
            stats[name] = logger_stats
    return stats

"""
Enhanced Error Handling Module

This module provides centralized error handling, custom exception hierarchy,
retry mechanisms with exponential backoff, error context managers, and
error categorization for the behave automation framework.
"""

import time
import random
import logging
import functools
from contextlib import contextmanager
from typing import Type, Callable, Any, Optional, Dict, List, Union
from enum import Enum


class ErrorCategory(Enum):
    """Categorizes errors as transient or permanent."""
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"


class BaseAutomationError(Exception):
    """Base exception class for all automation framework errors."""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.original_error = original_error
        self.timestamp = time.time()


class TransientError(BaseAutomationError):
    """Exception for transient errors that may succeed on retry."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.TRANSIENT, original_error)


class PermanentError(BaseAutomationError):
    """Exception for permanent errors that should not be retried."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.PERMANENT, original_error)


class ApiError(BaseAutomationError):
    """Exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_body: Optional[str] = None, category: ErrorCategory = ErrorCategory.UNKNOWN,
                 original_error: Optional[Exception] = None):
        super().__init__(message, category, original_error)
        self.status_code = status_code
        self.response_body = response_body


class DatabaseError(BaseAutomationError):
    """Exception for database-related errors."""
    
    def __init__(self, message: str, query: Optional[str] = None, 
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 original_error: Optional[Exception] = None):
        super().__init__(message, category, original_error)
        self.query = query


class WebDriverError(BaseAutomationError):
    """Exception for web driver-related errors."""
    
    def __init__(self, message: str, element_selector: Optional[str] = None,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 original_error: Optional[Exception] = None):
        super().__init__(message, category, original_error)
        self.element_selector = element_selector


class ConfigurationError(PermanentError):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        super().__init__(message, original_error)
        self.config_key = config_key


class ValidationError(PermanentError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None, original_error: Optional[Exception] = None):
        super().__init__(message, original_error)
        self.field = field
        self.value = value


class TimeoutError(TransientError):
    """Exception for timeout-related errors."""
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None,
                 original_error: Optional[Exception] = None):
        super().__init__(message, original_error)
        self.timeout_duration = timeout_duration


class ConnectionError(TransientError):
    """Exception for connection-related errors."""
    
    def __init__(self, message: str, host: Optional[str] = None,
                 port: Optional[int] = None, original_error: Optional[Exception] = None):
        super().__init__(message, original_error)
        self.host = host
        self.port = port


class ErrorCategorizer:
    """Categorizes exceptions into transient or permanent errors."""
    
    # Default categorization rules
    TRANSIENT_EXCEPTIONS = {
        'ConnectionError', 'TimeoutError', 'ConnectionResetError',
        'ConnectionRefusedError', 'ConnectionAbortedError',
        'HTTPError', 'RequestException', 'Timeout',
        'SocketError', 'SocketTimeout', 'DNSError',
        'TemporaryFailure', 'ServiceUnavailable',
        'TooManyRequests', 'InternalServerError',
        'BadGateway', 'ServiceUnavailable', 'GatewayTimeout'
    }
    
    PERMANENT_EXCEPTIONS = {
        'ValueError', 'TypeError', 'AttributeError',
        'ImportError', 'ModuleNotFoundError', 'NameError',
        'SyntaxError', 'IndentationError', 'KeyError',
        'IndexError', 'FileNotFoundError', 'PermissionError',
        'NotImplementedError', 'ValidationError', 'ConfigurationError',
        'Unauthorized', 'Forbidden', 'NotFound', 'MethodNotAllowed',
        'UnprocessableEntity', 'BadRequest'
    }
    
    @classmethod
    def categorize_error(cls, error: Exception) -> ErrorCategory:
        """
        Categorize an exception as transient or permanent.
        
        Args:
            error: The exception to categorize
            
        Returns:
            ErrorCategory: The category of the error
        """
        error_name = type(error).__name__
        
        if error_name in cls.TRANSIENT_EXCEPTIONS:
            return ErrorCategory.TRANSIENT
        elif error_name in cls.PERMANENT_EXCEPTIONS:
            return ErrorCategory.PERMANENT
        else:
            # Check if it's an HTTP status code based error
            if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
                status_code = error.response.status_code
                if status_code in [408, 429, 500, 502, 503, 504]:
                    return ErrorCategory.TRANSIENT
                elif status_code in [400, 401, 403, 404, 405, 422]:
                    return ErrorCategory.PERMANENT
            
            return ErrorCategory.UNKNOWN


class RetryConfig:
    """Configuration for retry mechanism."""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, backoff_factor: float = 2.0,
                 jitter: bool = True, retry_on: Optional[List[Type[Exception]]] = None):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_on = retry_on or [TransientError, ConnectionError, TimeoutError]


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if an error should be retried.
        
        Args:
            error: The exception that occurred
            attempt: Current attempt number (1-based)
            
        Returns:
            bool: True if should retry, False otherwise
        """
        if attempt >= self.config.max_attempts:
            return False
        
        # Check if error type is in retry list
        for retry_type in self.config.retry_on:
            if isinstance(error, retry_type):
                return True
        
        # Check error category if it's a BaseAutomationError
        if isinstance(error, BaseAutomationError):
            return error.category == ErrorCategory.TRANSIENT
        
        # Use categorizer for other exceptions
        category = ErrorCategorizer.categorize_error(error)
        return category == ErrorCategory.TRANSIENT
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt.
        
        Args:
            attempt: Current attempt number (1-based)
            
        Returns:
            float: Delay in seconds
        """
        delay = self.config.base_delay * (self.config.backoff_factor ** (attempt - 1))
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            # Add jitter to avoid thundering herd
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(delay, 0)
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        last_error = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                last_error = error
                
                if not self.should_retry(error, attempt):
                    self.logger.error(f"Permanent error on attempt {attempt}: {error}")
                    raise error
                
                if attempt < self.config.max_attempts:
                    delay = self.calculate_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt} failed: {error}. Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"All {self.config.max_attempts} attempts failed")
        
        if last_error:
            raise last_error


def retry_on_error(max_attempts: int = 3, base_delay: float = 1.0,
                   max_delay: float = 60.0, backoff_factor: float = 2.0,
                   jitter: bool = True, retry_on: Optional[List[Type[Exception]]] = None):
    """
    Decorator for adding retry logic to functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Exponential backoff factor
        jitter: Whether to add jitter to delays
        retry_on: List of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                jitter=jitter,
                retry_on=retry_on
            )
            handler = RetryHandler(config)
            return handler.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator


@contextmanager
def error_context(operation: str, capture_errors: bool = True, 
                  reraise_as: Optional[Type[BaseAutomationError]] = None,
                  additional_context: Optional[Dict[str, Any]] = None):
    """
    Context manager for consistent error handling.
    
    Args:
        operation: Description of the operation being performed
        capture_errors: Whether to capture and log errors
        reraise_as: Exception type to reraise errors as
        additional_context: Additional context to include in error logs
        
    Yields:
        None
        
    Raises:
        Exception: Original or reraised exception
    """
    logger = logging.getLogger(__name__)
    context = additional_context or {}
    
    try:
        logger.debug(f"Starting operation: {operation}")
        if context:
            logger.debug(f"Operation context: {context}")
        yield
        logger.debug(f"Completed operation: {operation}")
    except Exception as error:
        if capture_errors:
            error_info = {
                'operation': operation,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'error_category': ErrorCategorizer.categorize_error(error).value,
                **context
            }
            logger.error(f"Error in operation '{operation}': {error_info}")
        
        if reraise_as:
            # Determine category based on original error
            category = ErrorCategorizer.categorize_error(error)
            if issubclass(reraise_as, BaseAutomationError):
                raise reraise_as(
                    f"Error in {operation}: {str(error)}",
                    category=category,
                    original_error=error
                )
            else:
                raise reraise_as(f"Error in {operation}: {str(error)}")
        else:
            raise


class CentralizedErrorHandler:
    """Centralized error handler for the automation framework."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_stats = {
            'total_errors': 0,
            'transient_errors': 0,
            'permanent_errors': 0,
            'unknown_errors': 0,
            'retried_operations': 0,
            'successful_retries': 0
        }
    
    def handle_error(self, error: Exception, operation: str = "Unknown",
                     context: Optional[Dict[str, Any]] = None) -> None:
        """
        Handle and log an error with appropriate categorization.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            context: Additional context information
        """
        category = ErrorCategorizer.categorize_error(error)
        context = context or {}
        
        error_info = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_category': category.value,
            'timestamp': time.time(),
            **context
        }
        
        # Update statistics
        self.error_stats['total_errors'] += 1
        if category == ErrorCategory.TRANSIENT:
            self.error_stats['transient_errors'] += 1
        elif category == ErrorCategory.PERMANENT:
            self.error_stats['permanent_errors'] += 1
        else:
            self.error_stats['unknown_errors'] += 1
        
        # Log based on category
        if category == ErrorCategory.PERMANENT:
            self.logger.error(f"Permanent error in {operation}: {error_info}")
        elif category == ErrorCategory.TRANSIENT:
            self.logger.warning(f"Transient error in {operation}: {error_info}")
        else:
            self.logger.error(f"Unknown error in {operation}: {error_info}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        return self.error_stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset error handling statistics."""
        for key in self.error_stats:
            self.error_stats[key] = 0


# Global error handler instance
error_handler = CentralizedErrorHandler()


def handle_errors(operation: str = "Unknown", 
                  context: Optional[Dict[str, Any]] = None,
                  reraise_as: Optional[Type[BaseAutomationError]] = None):
    """
    Decorator for centralized error handling.
    
    Args:
        operation: Description of the operation
        context: Additional context information
        reraise_as: Exception type to reraise errors as
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                error_handler.handle_error(error, operation, context)
                
                if reraise_as:
                    category = ErrorCategorizer.categorize_error(error)
                    if issubclass(reraise_as, BaseAutomationError):
                        raise reraise_as(
                            f"Error in {operation}: {str(error)}",
                            category=category,
                            original_error=error
                        )
                    else:
                        raise reraise_as(f"Error in {operation}: {str(error)}")
                else:
                    raise
        return wrapper
    return decorator

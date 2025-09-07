"""
Unit tests for the enhanced error handling module.

These tests verify that the error handling functionality works as expected
and all components integrate properly.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from base.utilities.error_handler import (
    ErrorCategory, BaseAutomationError, TransientError, PermanentError,
    ApiError, DatabaseError, WebDriverError, ConfigurationError,
    ValidationError, TimeoutError, ConnectionError, ErrorCategorizer,
    RetryConfig, RetryHandler, retry_on_error, error_context,
    CentralizedErrorHandler, error_handler, handle_errors
)


class TestErrorHierarchy:
    """Test the custom exception hierarchy."""
    
    def test_base_automation_error(self):
        """Test BaseAutomationError creation and properties."""
        error = BaseAutomationError("Test error", ErrorCategory.TRANSIENT)
        assert error.message == "Test error"
        assert error.category == ErrorCategory.TRANSIENT
        assert error.original_error is None
        assert isinstance(error.timestamp, float)
    
    def test_transient_error(self):
        """Test TransientError categorization."""
        error = TransientError("Connection timeout")
        assert error.category == ErrorCategory.TRANSIENT
        assert error.message == "Connection timeout"
    
    def test_permanent_error(self):
        """Test PermanentError categorization."""
        error = PermanentError("Invalid configuration")
        assert error.category == ErrorCategory.PERMANENT
        assert error.message == "Invalid configuration"
    
    def test_api_error_with_details(self):
        """Test ApiError with additional details."""
        error = ApiError("API call failed", status_code=500, response_body="Internal Error")
        assert error.status_code == 500
        assert error.response_body == "Internal Error"
    
    def test_database_error_with_query(self):
        """Test DatabaseError with query information."""
        error = DatabaseError("Query failed", query="SELECT * FROM users")
        assert error.query == "SELECT * FROM users"
    
    def test_webdriver_error_with_selector(self):
        """Test WebDriverError with element selector."""
        error = WebDriverError("Element not found", element_selector="#submit-button")
        assert error.element_selector == "#submit-button"


class TestErrorCategorizer:
    """Test the error categorization functionality."""
    
    def test_categorize_transient_errors(self):
        """Test categorization of transient errors."""
        transient_errors = [
            Exception("ConnectionError"),
            Exception("TimeoutError"),
            Exception("ServiceUnavailable")
        ]
        
        for error in transient_errors:
            # Mock the error type name
            error.__class__.__name__ = error.args[0]
            category = ErrorCategorizer.categorize_error(error)
            assert category == ErrorCategory.TRANSIENT
    
    def test_categorize_permanent_errors(self):
        """Test categorization of permanent errors."""
        permanent_errors = [
            ValueError("Invalid value"),
            TypeError("Invalid type"),
            KeyError("Missing key")
        ]
        
        for error in permanent_errors:
            category = ErrorCategorizer.categorize_error(error)
            assert category == ErrorCategory.PERMANENT
    
    def test_categorize_unknown_errors(self):
        """Test categorization of unknown errors."""
        unknown_error = Exception("CustomError")
        unknown_error.__class__.__name__ = "CustomError"
        category = ErrorCategorizer.categorize_error(unknown_error)
        assert category == ErrorCategory.UNKNOWN


class TestRetryHandler:
    """Test the retry mechanism."""
    
    def test_retry_config(self):
        """Test RetryConfig creation."""
        config = RetryConfig(max_attempts=5, base_delay=2.0, jitter=False)
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.jitter is False
    
    def test_should_retry_transient_error(self):
        """Test retry decision for transient errors."""
        config = RetryConfig(max_attempts=3)
        handler = RetryHandler(config)
        
        error = TransientError("Connection failed")
        assert handler.should_retry(error, 1) is True
        assert handler.should_retry(error, 2) is True
        assert handler.should_retry(error, 3) is False  # Max attempts reached
    
    def test_should_not_retry_permanent_error(self):
        """Test retry decision for permanent errors."""
        config = RetryConfig(max_attempts=3)
        handler = RetryHandler(config)
        
        error = PermanentError("Invalid configuration")
        assert handler.should_retry(error, 1) is False
    
    def test_calculate_delay(self):
        """Test delay calculation with exponential backoff."""
        config = RetryConfig(base_delay=1.0, backoff_factor=2.0, jitter=False)
        handler = RetryHandler(config)
        
        assert handler.calculate_delay(1) == 1.0
        assert handler.calculate_delay(2) == 2.0
        assert handler.calculate_delay(3) == 4.0
    
    def test_calculate_delay_with_max_limit(self):
        """Test delay calculation respects maximum delay."""
        config = RetryConfig(base_delay=10.0, max_delay=15.0, backoff_factor=2.0, jitter=False)
        handler = RetryHandler(config)
        
        assert handler.calculate_delay(1) == 10.0
        assert handler.calculate_delay(2) == 15.0  # Capped at max_delay
        assert handler.calculate_delay(3) == 15.0  # Still capped
    
    @patch('time.sleep')
    def test_execute_with_retry_success_on_second_attempt(self, mock_sleep):
        """Test successful retry after initial failure."""
        config = RetryConfig(max_attempts=3, base_delay=0.1, jitter=False)
        handler = RetryHandler(config)
        
        mock_func = MagicMock()
        mock_func.side_effect = [TransientError("Temporary failure"), "Success"]
        
        result = handler.execute_with_retry(mock_func)
        
        assert result == "Success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(0.1)
    
    @patch('time.sleep')
    def test_execute_with_retry_failure_after_max_attempts(self, mock_sleep):
        """Test failure after maximum retry attempts."""
        config = RetryConfig(max_attempts=2, base_delay=0.1, jitter=False)
        handler = RetryHandler(config)
        
        mock_func = MagicMock()
        mock_func.side_effect = TransientError("Persistent failure")
        
        with pytest.raises(TransientError):
            handler.execute_with_retry(mock_func)
        
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(0.1)


class TestRetryDecorator:
    """Test the retry decorator functionality."""
    
    @patch('time.sleep')
    def test_retry_decorator_success(self, mock_sleep):
        """Test retry decorator with successful retry."""
        call_count = 0
        
        @retry_on_error(max_attempts=3, base_delay=0.1, jitter=False)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TransientError("First attempt failed")
            return "Success"
        
        result = test_function()
        
        assert result == "Success"
        assert call_count == 2
        mock_sleep.assert_called_once_with(0.1)
    
    def test_retry_decorator_permanent_error(self):
        """Test retry decorator with permanent error."""
        @retry_on_error(max_attempts=3)
        def test_function():
            raise PermanentError("Configuration error")
        
        with pytest.raises(PermanentError):
            test_function()


class TestErrorContext:
    """Test the error context manager."""
    
    def test_error_context_success(self):
        """Test error context manager with successful operation."""
        with error_context("Test operation"):
            result = "success"
        
        assert result == "success"
    
    def test_error_context_with_exception(self):
        """Test error context manager with exception."""
        with pytest.raises(ValueError):
            with error_context("Test operation"):
                raise ValueError("Test error")
    
    def test_error_context_reraise_as(self):
        """Test error context manager with custom exception reraising."""
        with pytest.raises(ApiError):
            with error_context("API call", reraise_as=ApiError):
                raise ValueError("Original error")


class TestCentralizedErrorHandler:
    """Test the centralized error handler."""
    
    def test_handle_error_updates_stats(self):
        """Test that handling errors updates statistics."""
        handler = CentralizedErrorHandler()
        handler.reset_statistics()
        
        # Handle different types of errors
        handler.handle_error(TransientError("Network error"), "Network operation")
        handler.handle_error(PermanentError("Config error"), "Configuration")
        handler.handle_error(ValueError("Value error"), "Validation")
        
        stats = handler.get_error_statistics()
        assert stats['total_errors'] == 3
        assert stats['transient_errors'] == 1
        assert stats['permanent_errors'] == 2  # PermanentError + ValueError
        assert stats['unknown_errors'] == 0
    
    def test_reset_statistics(self):
        """Test resetting error statistics."""
        handler = CentralizedErrorHandler()
        handler.handle_error(ValueError("Test error"), "Test operation")
        
        stats_before = handler.get_error_statistics()
        assert stats_before['total_errors'] > 0
        
        handler.reset_statistics()
        stats_after = handler.get_error_statistics()
        assert stats_after['total_errors'] == 0


class TestHandleErrorsDecorator:
    """Test the handle_errors decorator."""
    
    def test_handle_errors_decorator_success(self):
        """Test handle_errors decorator with successful operation."""
        @handle_errors("Test operation")
        def test_function():
            return "Success"
        
        result = test_function()
        assert result == "Success"
    
    def test_handle_errors_decorator_with_exception(self):
        """Test handle_errors decorator with exception."""
        @handle_errors("Test operation")
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_function()
    
    def test_handle_errors_decorator_reraise_as(self):
        """Test handle_errors decorator with custom exception reraising."""
        @handle_errors("API operation", reraise_as=ApiError)
        def test_function():
            raise ValueError("Original error")
        
        with pytest.raises(ApiError):
            test_function()


if __name__ == "__main__":
    pytest.main([__file__])

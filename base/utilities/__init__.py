"""
Utilities package for the automation framework

This package contains utility classes for common operations:
- excel_reader: Excel file reading operations
- excel_writer: Excel file writing operations
- json_utils: JSON data processing and querying
- yaml_utils: YAML data processing
- xml_utils: XML data processing
- file_operations: File and directory operations
- csv_utils: CSV file operations
- string_utils: String manipulation and validation
- datetime_utils: Date and time operations
- encoding_utils: Encoding/decoding operations
- url_utils: URL parsing and manipulation
- error_handler: Centralized error handling and retry mechanisms
"""

from .excel_reader import ExcelReader
from .excel_writer import ExcelWriter
from .json_utils import JsonUtils
from .yaml_utils import YamlUtils
from .xml_utils import XmlUtils
from .file_operations import FileUtils
from .csv_utils import CsvUtils
from .string_utils import StringUtils
from .datetime_utils import DateTimeUtils
from .encoding_utils import EncodingUtils
from .url_utils import UrlUtils
from .error_handler import (
    ErrorCategory, BaseAutomationError, TransientError, PermanentError,
    ApiError, DatabaseError, WebDriverError, ConfigurationError,
    ValidationError, TimeoutError, ConnectionError, ErrorCategorizer,
    RetryConfig, RetryHandler, retry_on_error, error_context,
    CentralizedErrorHandler, error_handler, handle_errors
)

__all__ = [
    'ExcelReader',
    'ExcelWriter',
    'JsonUtils',
    'YamlUtils', 
    'XmlUtils',
    'FileUtils',
    'CsvUtils',
    'StringUtils',
    'DateTimeUtils',
    'EncodingUtils',
    'UrlUtils',
    # Error handling components
    'ErrorCategory',
    'BaseAutomationError',
    'TransientError',
    'PermanentError',
    'ApiError',
    'DatabaseError',
    'WebDriverError',
    'ConfigurationError',
    'ValidationError',
    'TimeoutError',
    'ConnectionError',
    'ErrorCategorizer',
    'RetryConfig',
    'RetryHandler',
    'retry_on_error',
    'error_context',
    'CentralizedErrorHandler',
    'error_handler',
    'handle_errors'
]

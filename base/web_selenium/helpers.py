"""
Web Selenium Helper Classes

This module provides backward compatibility by importing all helper classes.
Individual helper classes are now split into separate modules for better organization.
"""

# Import all helper classes for backward compatibility
from .web_test_helpers import WebTestHelpers
from .web_element_helpers import WebElementHelpers  
from .web_wait_helpers import WebWaitHelpers

# Re-export for compatibility
__all__ = ['WebTestHelpers', 'WebElementHelpers', 'WebWaitHelpers']

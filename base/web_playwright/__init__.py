"""
Web Playwright package for the automation framework

This package contains Playwright-specific web automation classes:
- playwright_manager: Browser and page management for Playwright
- base_page: Base page class with common web interaction methods
- helpers: Helper methods for advanced Playwright features
"""

from .playwright_manager import PlaywrightManager
from .base_page import BasePage
from .helpers import PlaywrightHelpers

__all__ = [
    'PlaywrightManager',
    'BasePage', 
    'PlaywrightHelpers'
]

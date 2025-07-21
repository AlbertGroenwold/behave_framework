"""
Web Selenium package for the automation framework

This package contains Selenium-specific web automation classes:
- webdriver_manager: WebDriver management for different browsers
- base_page: Base page class with common web interaction methods
- helpers: Helper methods for advanced Selenium features
"""

from .webdriver_manager import WebDriverManager
from .base_page import BasePage
from .helpers import SeleniumHelpers

__all__ = [
    'WebDriverManager',
    'BasePage', 
    'SeleniumHelpers'
]

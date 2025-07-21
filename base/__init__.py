"""
Base package for the automation framework

This package contains base classes and utilities for different automation types:
- api: API testing base classes
- database: Database testing base classes  
- desktop: Desktop application testing base classes
- mobile: Mobile testing base classes
- web_selenium: Selenium-based web testing base classes
- web_playwright: Playwright-based web testing base classes
- utilities: Common utility functions for data processing and file operations
"""

# Import all base modules
from . import api
from . import database
from . import desktop
from . import mobile
from . import web_selenium
from . import web_playwright
from . import utilities

__all__ = [
    'api',
    'database', 
    'desktop',
    'mobile',
    'web_selenium',
    'web_playwright',
    'utilities'
]

"""
Page Objects package for Playwright Web Testing

This package contains all page object classes for the Playwright web automation
following the Page Object Model pattern.
"""

from .login_page import LoginPage
from .home_page import HomePage
from .user_management_page import UserManagementPage

__all__ = [
    'LoginPage',
    'HomePage',
    'UserManagementPage'
]

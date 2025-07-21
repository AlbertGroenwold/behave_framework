"""
Desktop package for the automation framework

This package contains desktop application testing base classes.
"""

from .base_desktop_page import BaseDesktopPage
from .desktop_app_manager import DesktopAppManager

__all__ = [
    'BaseDesktopPage',
    'DesktopAppManager'
]

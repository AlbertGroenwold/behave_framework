"""
Mobile package for the automation framework

This package contains mobile testing base classes and utilities.
"""

from .base_mobile_page import BaseMobilePage
from .mobile_driver_manager import MobileDriverManager

__all__ = [
    'BaseMobilePage',
    'MobileDriverManager'
]

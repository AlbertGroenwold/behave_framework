"""
API Page Objects for the automation framework

This package contains API page objects following the Page Object Model pattern.
Each API endpoint/resource is represented as a page object.
"""

from .users_api_page import UsersAPIPage
from .products_api_page import ProductsAPIPage

__all__ = [
    'UsersAPIPage',
    'ProductsAPIPage'
]

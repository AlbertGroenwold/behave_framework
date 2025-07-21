"""Desktop application manager and test helpers - backward compatibility imports"""

# Import individual desktop classes
from .desktop_app_manager_core import DesktopAppManager
from .desktop_test_helpers import DesktopTestHelpers

# Re-export all classes for backward compatibility
__all__ = [
    'DesktopAppManager',
    'DesktopTestHelpers'
]

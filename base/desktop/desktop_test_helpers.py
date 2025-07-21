"""Desktop test helpers for automation testing"""

import psutil
import os
import logging
from typing import Dict, Any
from pathlib import Path


class DesktopTestHelpers:
    """Helper utilities for desktop testing"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information"""
        import platform
        
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available
        }
    
    @staticmethod
    def get_screen_resolution() -> tuple:
        """Get screen resolution"""
        try:
            import pyautogui
            return pyautogui.size()
        except Exception:
            return (0, 0)
    
    @staticmethod
    def create_test_file(file_path: str, content: str = "Test file content") -> bool:
        """Create test file"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            logging.error(f"Error creating test file: {e}")
            return False
    
    @staticmethod
    def cleanup_test_file(file_path: str) -> bool:
        """Clean up test file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            logging.error(f"Error cleaning up test file: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'exists': True,
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'accessed': stat.st_atime
                }
            else:
                return {'exists': False}
        except Exception as e:
            logging.error(f"Error getting file info: {e}")
            return {'exists': False, 'error': str(e)}

import pyautogui
import pygetwindow as gw
from pyautogui import ImageNotFoundException
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Union
import configparser
from abc import ABC, abstractmethod


class BaseDesktopPage(ABC):
    """Base page class for desktop application testing"""
    
    def __init__(self, app_manager, app_name: str = None):
        self.app_manager = app_manager
        self.app_name = app_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.window = None
        
        # Default settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1
    
    def find_window(self, title_contains: str = None) -> bool:
        """Find application window"""
        try:
            if title_contains:
                windows = gw.getWindowsWithTitle(title_contains)
            elif self.app_name:
                windows = gw.getWindowsWithTitle(self.app_name)
            else:
                self.logger.error("No window title specified")
                return False
            
            if windows:
                self.window = windows[0]
                self.logger.info(f"Found window: {self.window.title}")
                return True
            else:
                self.logger.warning(f"Window not found: {title_contains or self.app_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error finding window: {e}")
            return False
    
    def activate_window(self) -> bool:
        """Activate application window"""
        try:
            if not self.window:
                if not self.find_window():
                    return False
            
            if self.window.isMinimized:
                self.window.restore()
            
            self.window.activate()
            time.sleep(0.5)
            self.logger.info(f"Activated window: {self.window.title}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error activating window: {e}")
            return False
    
    def maximize_window(self) -> bool:
        """Maximize application window"""
        try:
            if not self.window:
                if not self.find_window():
                    return False
            
            self.window.maximize()
            time.sleep(0.5)
            self.logger.info("Window maximized")
            return True
        
        except Exception as e:
            self.logger.error(f"Error maximizing window: {e}")
            return False
    
    def minimize_window(self) -> bool:
        """Minimize application window"""
        try:
            if not self.window:
                if not self.find_window():
                    return False
            
            self.window.minimize()
            time.sleep(0.5)
            self.logger.info("Window minimized")
            return True
        
        except Exception as e:
            self.logger.error(f"Error minimizing window: {e}")
            return False
    
    def close_window(self) -> bool:
        """Close application window"""
        try:
            if not self.window:
                if not self.find_window():
                    return False
            
            self.window.close()
            time.sleep(0.5)
            self.logger.info("Window closed")
            return True
        
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
            return False
    
    def get_window_position(self) -> Tuple[int, int, int, int]:
        """Get window position and size"""
        try:
            if not self.window:
                if not self.find_window():
                    return (0, 0, 0, 0)
            
            return (self.window.left, self.window.top, self.window.width, self.window.height)
        
        except Exception as e:
            self.logger.error(f"Error getting window position: {e}")
            return (0, 0, 0, 0)
    
    def move_window(self, x: int, y: int) -> bool:
        """Move window to position"""
        try:
            if not self.window:
                if not self.find_window():
                    return False
            
            self.window.moveTo(x, y)
            time.sleep(0.5)
            self.logger.info(f"Window moved to: ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Error moving window: {e}")
            return False
    
    def resize_window(self, width: int, height: int) -> bool:
        """Resize window"""
        try:
            if not self.window:
                if not self.find_window():
                    return False
            
            self.window.resizeTo(width, height)
            time.sleep(0.5)
            self.logger.info(f"Window resized to: {width}x{height}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error resizing window: {e}")
            return False
    
    # Mouse actions
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """Click at coordinates"""
        try:
            pyautogui.click(x, y, button=button, clicks=clicks)
            self.logger.info(f"Clicked at ({x}, {y}) with {button} button, {clicks} times")
            return True
        
        except Exception as e:
            self.logger.error(f"Error clicking: {e}")
            return False
    
    def right_click(self, x: int, y: int) -> bool:
        """Right click at coordinates"""
        return self.click(x, y, button='right')
    
    def double_click(self, x: int, y: int) -> bool:
        """Double click at coordinates"""
        return self.click(x, y, clicks=2)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """Drag from start to end coordinates"""
        try:
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            self.logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Error dragging: {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int) -> bool:
        """Scroll at coordinates"""
        try:
            pyautogui.scroll(clicks, x=x, y=y)
            self.logger.info(f"Scrolled {clicks} clicks at ({x}, {y})")
            return True
        
        except Exception as e:
            self.logger.error(f"Error scrolling: {e}")
            return False
    
    # Keyboard actions
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Type text"""
        try:
            pyautogui.typewrite(text, interval=interval)
            self.logger.info(f"Typed text: {text}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a key"""
        try:
            pyautogui.press(key)
            self.logger.info(f"Pressed key: {key}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return False
    
    def press_key_combination(self, keys: List[str]) -> bool:
        """Press key combination"""
        try:
            pyautogui.hotkey(*keys)
            self.logger.info(f"Pressed key combination: {' + '.join(keys)}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error pressing key combination: {e}")
            return False
    
    def hold_key(self, key: str) -> bool:
        """Hold down a key"""
        try:
            pyautogui.keyDown(key)
            self.logger.info(f"Holding key: {key}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error holding key: {e}")
            return False
    
    def release_key(self, key: str) -> bool:
        """Release a held key"""
        try:
            pyautogui.keyUp(key)
            self.logger.info(f"Released key: {key}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error releasing key: {e}")
            return False
    
    # Image recognition
    def find_image(self, image_path: str, confidence: float = 0.8) -> Tuple[int, int]:
        """Find image on screen"""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                self.logger.info(f"Found image at: {center}")
                return center
            else:
                self.logger.warning(f"Image not found: {image_path}")
                return (0, 0)
        
        except ImageNotFoundException:
            self.logger.warning(f"Image not found: {image_path}")
            return (0, 0)
        except Exception as e:
            self.logger.error(f"Error finding image: {e}")
            return (0, 0)
    
    def click_image(self, image_path: str, confidence: float = 0.8, button: str = 'left') -> bool:
        """Click on image if found"""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center, button=button)
                self.logger.info(f"Clicked on image: {image_path}")
                return True
            else:
                self.logger.warning(f"Image not found for clicking: {image_path}")
                return False
        
        except ImageNotFoundException:
            self.logger.warning(f"Image not found for clicking: {image_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error clicking image: {e}")
            return False
    
    def wait_for_image(self, image_path: str, timeout: int = 10, confidence: float = 0.8) -> bool:
        """Wait for image to appear"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    self.logger.info(f"Image appeared: {image_path}")
                    return True
            except ImageNotFoundException:
                pass
            except Exception as e:
                self.logger.error(f"Error waiting for image: {e}")
                return False
            
            time.sleep(0.5)
        
        self.logger.warning(f"Image did not appear within timeout: {image_path}")
        return False
    
    # Screen capture
    def take_screenshot(self, filename: str = None, region: Tuple[int, int, int, int] = None) -> str:
        """Take screenshot"""
        try:
            if filename is None:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
        
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return ""
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size"""
        try:
            size = pyautogui.size()
            self.logger.info(f"Screen size: {size}")
            return size
        
        except Exception as e:
            self.logger.error(f"Error getting screen size: {e}")
            return (0, 0)
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get pixel color at coordinates"""
        try:
            color = pyautogui.pixel(x, y)
            self.logger.info(f"Pixel color at ({x}, {y}): {color}")
            return color
        
        except Exception as e:
            self.logger.error(f"Error getting pixel color: {e}")
            return (0, 0, 0)
    
    # Utility methods
    def wait(self, seconds: float):
        """Wait for specified seconds"""
        time.sleep(seconds)
        self.logger.info(f"Waited {seconds} seconds")
    
    def set_pause(self, seconds: float):
        """Set pause between actions"""
        pyautogui.PAUSE = seconds
        self.logger.info(f"Set pause to {seconds} seconds")
    
    def set_fail_safe(self, enabled: bool):
        """Set fail safe mode"""
        pyautogui.FAILSAFE = enabled
        self.logger.info(f"Fail safe {'enabled' if enabled else 'disabled'}")
    
    # Abstract methods for specific implementations
    @abstractmethod
    def navigate_to_section(self, section: str) -> bool:
        """Navigate to specific section (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    def perform_action(self, action: str, **kwargs) -> bool:
        """Perform specific action (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    def verify_element_exists(self, element_identifier: str) -> bool:
        """Verify element exists (to be implemented by subclasses)"""
        pass

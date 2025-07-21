import sys
import os
import time

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from desktop.base_desktop_page import BaseDesktopPage


class CalculatorPage(BaseDesktopPage):
    """Calculator page object for Windows Calculator application"""
    
    def __init__(self, app_manager, app_name="Calculator"):
        super().__init__(app_manager, app_name)
        self.display_value = ""
    
    def navigate_to_section(self, section: str) -> bool:
        """Navigate to specific calculator section (not applicable for calculator)"""
        return True
    
    def perform_action(self, action: str, **kwargs) -> bool:
        """Perform specific calculator action"""
        if action == "clear":
            return self.clear_calculator()
        elif action == "calculate":
            calculation = kwargs.get('calculation', '')
            return self.perform_calculation(calculation)
        return False
    
    def verify_element_exists(self, element_identifier: str) -> bool:
        """Verify calculator element exists (simplified implementation)"""
        return True
    
    def perform_calculation(self, calculation: str) -> bool:
        """
        Perform calculation by clicking calculator buttons
        
        Args:
            calculation (str): Mathematical expression like "5 + 3"
        
        Returns:
            bool: True if calculation was performed successfully
        """
        try:
            self.activate_window()
            
            # Clear calculator first
            self.clear_calculator()
            
            # Parse and execute calculation
            for char in calculation:
                if char.isdigit():
                    self.click_number(char)
                elif char == '+':
                    self.click_add()
                elif char == '-':
                    self.click_subtract()
                elif char == '*':
                    self.click_multiply()
                elif char == '/':
                    self.click_divide()
                elif char == '.':
                    self.click_decimal()
                elif char == ' ':
                    continue  # Skip spaces
            
            # Click equals to get result
            self.click_equals()
            
            self.logger.info(f"Performed calculation: {calculation}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error performing calculation: {e}")
            return False
    
    def click_number(self, number: str) -> bool:
        """Click number button"""
        try:
            # Use keyboard input for simplicity
            self.activate_window()
            self.press_key(number)
            time.sleep(0.2)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking number {number}: {e}")
            return False
    
    def click_add(self) -> bool:
        """Click add button"""
        try:
            self.press_key('+')
            time.sleep(0.2)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking add button: {e}")
            return False
    
    def click_subtract(self) -> bool:
        """Click subtract button"""
        try:
            self.press_key('-')
            time.sleep(0.2)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking subtract button: {e}")
            return False
    
    def click_multiply(self) -> bool:
        """Click multiply button"""
        try:
            self.press_key('*')
            time.sleep(0.2)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking multiply button: {e}")
            return False
    
    def click_divide(self) -> bool:
        """Click divide button"""
        try:
            self.press_key('/')
            time.sleep(0.2)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking divide button: {e}")
            return False
    
    def click_decimal(self) -> bool:
        """Click decimal button"""
        try:
            self.press_key('.')
            time.sleep(0.2)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking decimal button: {e}")
            return False
    
    def click_equals(self) -> bool:
        """Click equals button"""
        try:
            self.press_key('Return')  # Enter key for equals
            time.sleep(0.5)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking equals button: {e}")
            return False
    
    def clear_calculator(self) -> bool:
        """Clear calculator display"""
        try:
            self.activate_window()
            self.press_key('Escape')  # Clear calculator
            time.sleep(0.3)
            return True
        except Exception as e:
            self.logger.error(f"Error clearing calculator: {e}")
            return False
    
    def enter_number(self, number: str) -> bool:
        """Enter a number (possibly multi-digit)"""
        try:
            for digit in number:
                self.click_number(digit)
            return True
        except Exception as e:
            self.logger.error(f"Error entering number {number}: {e}")
            return False
    
    def get_display_value(self) -> str:
        """
        Get the current display value from calculator
        Note: This is a simplified implementation
        """
        try:
            # In a real implementation, this would read the calculator display
            # For now, we'll use a simple approach with clipboard
            self.activate_window()
            
            # Select all and copy the display value
            self.press_key_combination(['ctrl', 'c'])
            time.sleep(0.2)
            
            # In reality, you'd read from clipboard or use OCR/image recognition
            # For demonstration, we'll return a placeholder
            return "result"  # This would be the actual display value
        
        except Exception as e:
            self.logger.error(f"Error getting display value: {e}")
            return ""
    
    def is_window_maximized(self) -> bool:
        """Check if calculator window is maximized"""
        try:
            if self.window:
                return self.window.isMaximized
            return False
        except Exception as e:
            self.logger.error(f"Error checking if window is maximized: {e}")
            return False
    
    def is_window_minimized(self) -> bool:
        """Check if calculator window is minimized"""
        try:
            if self.window:
                return self.window.isMinimized
            return False
        except Exception as e:
            self.logger.error(f"Error checking if window is minimized: {e}")
            return False
    
    def is_window_restored(self) -> bool:
        """Check if calculator window is restored (not minimized or maximized)"""
        try:
            if self.window:
                return not self.window.isMinimized and not self.window.isMaximized
            return False
        except Exception as e:
            self.logger.error(f"Error checking if window is restored: {e}")
            return False
    
    def wait_for_calculator_to_load(self, timeout: int = 10) -> bool:
        """Wait for calculator to load completely"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.find_window("Calculator"):
                    self.logger.info("Calculator loaded successfully")
                    return True
                time.sleep(0.5)
            
            self.logger.warning("Calculator did not load within timeout")
            return False
        
        except Exception as e:
            self.logger.error(f"Error waiting for calculator to load: {e}")
            return False

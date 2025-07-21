import logging
import os
import time


class WebElementHelpers:
    """Helper methods for web element interactions"""
    
    @staticmethod
    def safe_send_keys(element, text, clear_first=True):
        """Safely send keys to element"""
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            logging.error(f"Failed to send keys: {e}")
            return False
    
    @staticmethod
    def get_element_attribute_safely(element, attribute):
        """Safely get element attribute"""
        try:
            return element.get_attribute(attribute)
        except Exception as e:
            logging.error(f"Failed to get attribute {attribute}: {e}")
            return None
    
    @staticmethod
    def is_element_clickable(driver, locator, timeout=5):
        """Check if element is clickable"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True
        except:
            return False
    
    @staticmethod
    def wait_for_text_to_change(driver, locator, initial_text, timeout=10):
        """Wait for element text to change from initial value"""
        from selenium.webdriver.support.ui import WebDriverWait
        
        def text_changed(driver):
            try:
                element = driver.find_element(*locator)
                return element.text != initial_text
            except:
                return False
        
        WebDriverWait(driver, timeout).until(text_changed)
    
    @staticmethod
    def select_dropdown_option(driver, dropdown_locator, option_text, timeout=10):
        """Select dropdown option by text"""
        from selenium.webdriver.support.ui import Select, WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        dropdown = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(dropdown_locator)
        )
        select = Select(dropdown)
        select.select_by_visible_text(option_text)
        logging.info(f"Selected dropdown option: {option_text}")
    
    @staticmethod
    def upload_file(driver, file_input_locator, file_path, timeout=10):
        """Upload file to file input element"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(file_input_locator)
        )
        file_input.send_keys(file_path)
        logging.info(f"File uploaded: {file_path}")

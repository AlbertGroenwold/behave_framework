import time
import random
import string
import json
import os
from datetime import datetime
import logging


class WebTestHelpers:
    """Base helper utilities for web testing"""
    
    @staticmethod
    def generate_random_string(length=10):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    @staticmethod
    def generate_random_email():
        """Generate random email address"""
        username = WebTestHelpers.generate_random_string(8)
        domain = random.choice(['test.com', 'example.org', 'demo.net'])
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_random_phone():
        """Generate random phone number"""
        return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    @staticmethod
    def wait_with_timeout(condition_func, timeout=30, poll_interval=0.5):
        """Wait for condition with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(poll_interval)
        return False
    
    @staticmethod
    def load_test_data(file_path):
        """Load test data from JSON file"""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Failed to load test data: {e}")
            return {}
    
    @staticmethod
    def save_test_data(data, file_path):
        """Save test data to JSON file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
            logging.info(f"Test data saved: {file_path}")
        except Exception as e:
            logging.error(f"Failed to save test data: {e}")
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp string"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def create_unique_filename(base_name, extension=''):
        """Create unique filename with timestamp"""
        timestamp = WebTestHelpers.get_timestamp()
        return f"{base_name}_{timestamp}{extension}"
    
    @staticmethod
    def validate_email_format(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone_format(phone):
        """Validate phone number format"""
        import re
        # Simple phone validation - adjust pattern as needed
        pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def retry_on_failure(func, max_attempts=3, delay=1):
        """Retry function on failure"""
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(delay)
    
    @staticmethod
    def safe_click(driver, element, max_attempts=3):
        """Safely click element with retry"""
        from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
        
        for attempt in range(max_attempts):
            try:
                element.click()
                return True
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                if attempt == max_attempts - 1:
                    logging.error(f"Failed to click element after {max_attempts} attempts")
                    raise e
                time.sleep(0.5)
        return False
    
    @staticmethod
    def scroll_to_element(driver, element):
        """Scroll element into view"""
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Allow time for scroll
    
    @staticmethod
    def highlight_element(driver, element, duration=2):
        """Highlight element for debugging"""
        original_style = element.get_attribute('style')
        driver.execute_script(
            "arguments[0].style.border='3px solid red';", element
        )
        time.sleep(duration)
        driver.execute_script(
            f"arguments[0].style.border='{original_style}';", element
        )
    
    @staticmethod
    def capture_element_screenshot(driver, element, filepath):
        """Capture screenshot of specific element"""
        element.screenshot(filepath)
        logging.info(f"Element screenshot saved: {filepath}")
    
    @staticmethod
    def get_element_info(element):
        """Get comprehensive element information"""
        return {
            'tag_name': element.tag_name,
            'text': element.text,
            'location': element.location,
            'size': element.size,
            'is_displayed': element.is_displayed(),
            'is_enabled': element.is_enabled(),
            'is_selected': element.is_selected()
        }
    
    @staticmethod
    def wait_for_page_load(driver, timeout=30):
        """Wait for page to fully load"""
        from selenium.webdriver.support.ui import WebDriverWait
        
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    
    @staticmethod
    def switch_to_new_window(driver):
        """Switch to newly opened window"""
        main_window = driver.current_window_handle
        for window_handle in driver.window_handles:
            if window_handle != main_window:
                driver.switch_to.window(window_handle)
                break
    
    @staticmethod
    def close_extra_windows(driver):
        """Close all windows except the main one"""
        main_window = driver.window_handles[0]
        for window_handle in driver.window_handles[1:]:
            driver.switch_to.window(window_handle)
            driver.close()
        driver.switch_to.window(main_window)
    
    @staticmethod
    def clear_browser_data(driver):
        """Clear browser cookies and local storage"""
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        logging.info("Browser data cleared")

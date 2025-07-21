class WebWaitHelpers:
    """Helper methods for various wait conditions"""
    
    @staticmethod
    def wait_for_url_contains(driver, url_part, timeout=10):
        """Wait for URL to contain specific text"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        WebDriverWait(driver, timeout).until(
            EC.url_contains(url_part)
        )
    
    @staticmethod
    def wait_for_title_contains(driver, title_part, timeout=10):
        """Wait for page title to contain specific text"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        WebDriverWait(driver, timeout).until(
            EC.title_contains(title_part)
        )
    
    @staticmethod
    def wait_for_element_count(driver, locator, expected_count, timeout=10):
        """Wait for specific number of elements"""
        from selenium.webdriver.support.ui import WebDriverWait
        
        def element_count_matches(driver):
            elements = driver.find_elements(*locator)
            return len(elements) == expected_count
        
        WebDriverWait(driver, timeout).until(element_count_matches)
    
    @staticmethod
    def wait_for_attribute_value(driver, locator, attribute, expected_value, timeout=10):
        """Wait for element attribute to have specific value"""
        from selenium.webdriver.support.ui import WebDriverWait
        
        def attribute_has_value(driver):
            try:
                element = driver.find_element(*locator)
                return element.get_attribute(attribute) == expected_value
            except:
                return False
        
        WebDriverWait(driver, timeout).until(attribute_has_value)

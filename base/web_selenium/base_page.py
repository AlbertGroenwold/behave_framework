from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging


class BasePage:
    """Base page class that all page objects should inherit from"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def find_element(self, locator, timeout=10):
        """Find a single element"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {locator}")
            raise
    
    def find_elements(self, locator, timeout=10):
        """Find multiple elements"""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except TimeoutException:
            self.logger.error(f"Elements not found: {locator}")
            return []
    
    def click_element(self, locator, timeout=10):
        """Click an element"""
        element = self.wait_for_element_clickable(locator, timeout)
        element.click()
        self.logger.info(f"Clicked element: {locator}")
    
    def type_text(self, locator, text, timeout=10):
        """Type text into an element"""
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        self.logger.info(f"Typed '{text}' into element: {locator}")
    
    def get_text(self, locator, timeout=10):
        """Get text from an element"""
        element = self.find_element(locator, timeout)
        text = element.text
        self.logger.info(f"Got text '{text}' from element: {locator}")
        return text
    
    def get_attribute(self, locator, attribute, timeout=10):
        """Get attribute value from an element"""
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        self.logger.info(f"Got attribute '{attribute}' = '{value}' from element: {locator}")
        return value
    
    def wait_for_element_visible(self, locator, timeout=10):
        """Wait for element to be visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"Element not visible: {locator}")
            raise
    
    def wait_for_element_clickable(self, locator, timeout=10):
        """Wait for element to be clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"Element not clickable: {locator}")
            raise
    
    def wait_for_element_invisible(self, locator, timeout=10):
        """Wait for element to become invisible"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            self.logger.error(f"Element still visible: {locator}")
            return False
    
    def is_element_present(self, locator, timeout=5):
        """Check if element is present"""
        try:
            self.find_element(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator, timeout=5):
        """Check if element is visible"""
        try:
            self.wait_for_element_visible(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def scroll_to_element(self, locator, timeout=10):
        """Scroll to an element"""
        element = self.find_element(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.logger.info(f"Scrolled to element: {locator}")
    
    def switch_to_frame(self, frame_locator):
        """Switch to iframe"""
        frame = self.find_element(frame_locator)
        self.driver.switch_to.frame(frame)
        self.logger.info(f"Switched to frame: {frame_locator}")
    
    def switch_to_default_content(self):
        """Switch back to default content"""
        self.driver.switch_to.default_content()
        self.logger.info("Switched to default content")
    
    def get_page_title(self):
        """Get current page title"""
        title = self.driver.title
        self.logger.info(f"Page title: {title}")
        return title
    
    def get_current_url(self):
        """Get current URL"""
        url = self.driver.current_url
        self.logger.info(f"Current URL: {url}")
        return url
    
    def refresh_page(self):
        """Refresh the current page"""
        self.driver.refresh()
        self.logger.info("Page refreshed")
    
    def go_back(self):
        """Go back to previous page"""
        self.driver.back()
        self.logger.info("Navigated back")
    
    def go_forward(self):
        """Go forward to next page"""
        self.driver.forward()
        self.logger.info("Navigated forward")
    
    def execute_javascript(self, script, *args):
        """Execute JavaScript code"""
        result = self.driver.execute_script(script, *args)
        self.logger.info(f"Executed JavaScript: {script}")
        return result
    
    def take_screenshot(self, filename):
        """Take a screenshot"""
        self.driver.save_screenshot(filename)
        self.logger.info(f"Screenshot saved: {filename}")
    
    def wait_for_page_load(self, timeout=30):
        """Wait for page to fully load"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        self.logger.info("Page fully loaded")
    
    def hover_over_element(self, locator, timeout=10):
        """Hover over an element"""
        from selenium.webdriver.common.action_chains import ActionChains
        element = self.find_element(locator, timeout)
        ActionChains(self.driver).move_to_element(element).perform()
        self.logger.info(f"Hovered over element: {locator}")
    
    def double_click_element(self, locator, timeout=10):
        """Double click an element"""
        from selenium.webdriver.common.action_chains import ActionChains
        element = self.find_element(locator, timeout)
        ActionChains(self.driver).double_click(element).perform()
        self.logger.info(f"Double clicked element: {locator}")
    
    def right_click_element(self, locator, timeout=10):
        """Right click an element"""
        from selenium.webdriver.common.action_chains import ActionChains
        element = self.find_element(locator, timeout)
        ActionChains(self.driver).context_click(element).perform()
        self.logger.info(f"Right clicked element: {locator}")
    
    def drag_and_drop(self, source_locator, target_locator, timeout=10):
        """Drag and drop from source to target"""
        from selenium.webdriver.common.action_chains import ActionChains
        source = self.find_element(source_locator, timeout)
        target = self.find_element(target_locator, timeout)
        ActionChains(self.driver).drag_and_drop(source, target).perform()
        self.logger.info(f"Dragged from {source_locator} to {target_locator}")
    
    def select_dropdown_by_text(self, dropdown_locator, text, timeout=10):
        """Select dropdown option by visible text"""
        from selenium.webdriver.support.ui import Select
        dropdown = self.find_element(dropdown_locator, timeout)
        select = Select(dropdown)
        select.select_by_visible_text(text)
        self.logger.info(f"Selected dropdown option: {text}")
    
    def select_dropdown_by_value(self, dropdown_locator, value, timeout=10):
        """Select dropdown option by value"""
        from selenium.webdriver.support.ui import Select
        dropdown = self.find_element(dropdown_locator, timeout)
        select = Select(dropdown)
        select.select_by_value(value)
        self.logger.info(f"Selected dropdown value: {value}")
    
    def get_dropdown_selected_text(self, dropdown_locator, timeout=10):
        """Get currently selected dropdown text"""
        from selenium.webdriver.support.ui import Select
        dropdown = self.find_element(dropdown_locator, timeout)
        select = Select(dropdown)
        selected_text = select.first_selected_option.text
        self.logger.info(f"Selected dropdown text: {selected_text}")
        return selected_text

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging


class BaseMobilePage:
    """Base page class for mobile automation that all mobile page objects should inherit from"""
    
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
            self.logger.error(f"Mobile element not found: {locator}")
            raise
    
    def find_elements(self, locator, timeout=10):
        """Find multiple elements"""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except TimeoutException:
            self.logger.error(f"Mobile elements not found: {locator}")
            return []
    
    def tap_element(self, locator, timeout=10):
        """Tap an element"""
        element = self.find_element(locator, timeout)
        element.click()
        self.logger.info(f"Tapped element: {locator}")
    
    def type_text(self, locator, text, timeout=10):
        """Type text into an element"""
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        self.logger.info(f"Typed '{text}' into mobile element: {locator}")
    
    def get_text(self, locator, timeout=10):
        """Get text from an element"""
        element = self.find_element(locator, timeout)
        text = element.text
        self.logger.info(f"Got text '{text}' from mobile element: {locator}")
        return text
    
    def get_attribute(self, locator, attribute, timeout=10):
        """Get attribute value from an element"""
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        self.logger.info(f"Got attribute '{attribute}' = '{value}' from mobile element: {locator}")
        return value
    
    def wait_for_element_visible(self, locator, timeout=10):
        """Wait for element to be visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"Mobile element not visible: {locator}")
            raise
    
    def is_element_present(self, locator, timeout=5):
        """Check if element is present"""
        try:
            self.find_element(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def swipe_up(self, duration=1000):
        """Swipe up on screen"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.8
        end_y = size['height'] * 0.2
        
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        self.logger.info("Swiped up")
    
    def swipe_down(self, duration=1000):
        """Swipe down on screen"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = size['height'] * 0.2
        end_y = size['height'] * 0.8
        
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        self.logger.info("Swiped down")
    
    def swipe_left(self, duration=1000):
        """Swipe left on screen"""
        size = self.driver.get_window_size()
        start_x = size['width'] * 0.8
        start_y = size['height'] // 2
        end_x = size['width'] * 0.2
        
        self.driver.swipe(start_x, start_y, end_x, start_y, duration)
        self.logger.info("Swiped left")
    
    def swipe_right(self, duration=1000):
        """Swipe right on screen"""
        size = self.driver.get_window_size()
        start_x = size['width'] * 0.2
        start_y = size['height'] // 2
        end_x = size['width'] * 0.8
        
        self.driver.swipe(start_x, start_y, end_x, start_y, duration)
        self.logger.info("Swiped right")
    
    def scroll_to_element(self, locator, max_scrolls=10):
        """Scroll to find element"""
        for _ in range(max_scrolls):
            if self.is_element_present(locator, timeout=2):
                return self.find_element(locator)
            self.swipe_up()
        
        raise Exception(f"Element not found after {max_scrolls} scrolls: {locator}")
    
    def long_press(self, locator, duration=2000, timeout=10):
        """Long press on element"""
        from selenium.webdriver.common.action_chains import ActionChains
        
        element = self.find_element(locator, timeout)
        actions = ActionChains(self.driver)
        actions.click_and_hold(element).pause(duration/1000).release().perform()
        self.logger.info(f"Long pressed element: {locator}")
    
    def take_screenshot(self, filename):
        """Take a screenshot"""
        self.driver.save_screenshot(filename)
        self.logger.info(f"Mobile screenshot saved: {filename}")
    
    def hide_keyboard(self):
        """Hide mobile keyboard"""
        try:
            self.driver.hide_keyboard()
            self.logger.info("Keyboard hidden")
        except Exception as e:
            self.logger.warning(f"Could not hide keyboard: {e}")
    
    def get_current_activity(self):
        """Get current Android activity"""
        try:
            activity = self.driver.current_activity
            self.logger.info(f"Current activity: {activity}")
            return activity
        except Exception as e:
            self.logger.warning(f"Could not get current activity: {e}")
            return None
    
    def get_current_package(self):
        """Get current Android package"""
        try:
            package = self.driver.current_package
            self.logger.info(f"Current package: {package}")
            return package
        except Exception as e:
            self.logger.warning(f"Could not get current package: {e}")
            return None
    
    def press_back_button(self):
        """Press Android back button"""
        try:
            self.driver.back()
            self.logger.info("Pressed back button")
        except Exception as e:
            self.logger.warning(f"Could not press back button: {e}")
    
    def press_home_button(self):
        """Press home button"""
        try:
            self.driver.press_keycode(3)  # Android home key
            self.logger.info("Pressed home button")
        except Exception as e:
            self.logger.warning(f"Could not press home button: {e}")
    
    def switch_to_context(self, context_name):
        """Switch to specific context (NATIVE_APP or WEBVIEW)"""
        try:
            self.driver.switch_to.context(context_name)
            self.logger.info(f"Switched to context: {context_name}")
        except Exception as e:
            self.logger.error(f"Could not switch to context {context_name}: {e}")
    
    def get_contexts(self):
        """Get available contexts"""
        try:
            contexts = self.driver.contexts
            self.logger.info(f"Available contexts: {contexts}")
            return contexts
        except Exception as e:
            self.logger.error(f"Could not get contexts: {e}")
            return []
    
    def tap_coordinates(self, x, y):
        """Tap at specific coordinates"""
        self.driver.tap([(x, y)])
        self.logger.info(f"Tapped at coordinates: ({x}, {y})")
    
    def pinch_zoom(self, element, scale=2.0):
        """Pinch zoom on element"""
        try:
            self.driver.pinch(element)
            self.logger.info("Performed pinch zoom")
        except Exception as e:
            self.logger.warning(f"Could not perform pinch zoom: {e}")
    
    def zoom(self, element, scale=2.0):
        """Zoom on element"""
        try:
            self.driver.zoom(element)
            self.logger.info("Performed zoom")
        except Exception as e:
            self.logger.warning(f"Could not perform zoom: {e}")

from playwright.sync_api import Page, Locator, expect
import logging
import time
from typing import Optional, List, Dict, Any, Union
import os
from .playwright_manager import PlaywrightManager


class BasePage:
    """Base page class for Playwright automation"""
    
    def __init__(self, playwright_manager: PlaywrightManager):
        self.playwright_manager = playwright_manager
        self.page: Page = playwright_manager.page
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default timeouts
        self.default_timeout = 30000  # 30 seconds
        self.short_timeout = 5000     # 5 seconds
        self.long_timeout = 60000     # 60 seconds
    
    def find_element(self, selector: str, timeout: int = None) -> Locator:
        """
        Find element by selector
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        
        Returns:
            Locator: Element locator
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.wait_for(timeout=timeout)
            self.logger.info(f"Element found: {selector}")
            return element
        except Exception as e:
            self.logger.error(f"Failed to find element {selector}: {e}")
            raise
    
    def find_elements(self, selector: str) -> List[Locator]:
        """
        Find multiple elements by selector
        
        Args:
            selector (str): Element selector
        
        Returns:
            List[Locator]: List of element locators
        """
        try:
            elements = self.page.locator(selector).all()
            self.logger.info(f"Found {len(elements)} elements with selector: {selector}")
            return elements
        except Exception as e:
            self.logger.error(f"Failed to find elements {selector}: {e}")
            raise
    
    def click_element(self, selector: str, timeout: int = None, force: bool = False) -> None:
        """
        Click element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
            force (bool): Whether to force click
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.click(timeout=timeout, force=force)
            self.logger.info(f"Clicked element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to click element {selector}: {e}")
            raise
    
    def double_click_element(self, selector: str, timeout: int = None) -> None:
        """
        Double click element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.dblclick(timeout=timeout)
            self.logger.info(f"Double clicked element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to double click element {selector}: {e}")
            raise
    
    def right_click_element(self, selector: str, timeout: int = None) -> None:
        """
        Right click element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.click(button="right", timeout=timeout)
            self.logger.info(f"Right clicked element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to right click element {selector}: {e}")
            raise
    
    def hover_element(self, selector: str, timeout: int = None) -> None:
        """
        Hover over element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.hover(timeout=timeout)
            self.logger.info(f"Hovered over element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to hover over element {selector}: {e}")
            raise
    
    def type_text(self, selector: str, text: str, clear: bool = True, timeout: int = None) -> None:
        """
        Type text into element
        
        Args:
            selector (str): Element selector
            text (str): Text to type
            clear (bool): Whether to clear field first
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            
            if clear:
                element.clear(timeout=timeout)
            
            element.type(text, timeout=timeout)
            self.logger.info(f"Typed text '{text}' into element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to type text into element {selector}: {e}")
            raise
    
    def fill_text(self, selector: str, text: str, timeout: int = None) -> None:
        """
        Fill text into element (faster than type)
        
        Args:
            selector (str): Element selector
            text (str): Text to fill
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.fill(text, timeout=timeout)
            self.logger.info(f"Filled text '{text}' into element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to fill text into element {selector}: {e}")
            raise
    
    def clear_text(self, selector: str, timeout: int = None) -> None:
        """
        Clear text from element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.clear(timeout=timeout)
            self.logger.info(f"Cleared text from element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to clear text from element {selector}: {e}")
            raise
    
    def get_text(self, selector: str, timeout: int = None) -> str:
        """
        Get text content of element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        
        Returns:
            str: Element text content
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            text = element.text_content(timeout=timeout)
            self.logger.info(f"Got text '{text}' from element: {selector}")
            return text or ""
        except Exception as e:
            self.logger.error(f"Failed to get text from element {selector}: {e}")
            raise
    
    def get_inner_text(self, selector: str, timeout: int = None) -> str:
        """
        Get inner text of element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        
        Returns:
            str: Element inner text
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            text = element.inner_text(timeout=timeout)
            self.logger.info(f"Got inner text '{text}' from element: {selector}")
            return text
        except Exception as e:
            self.logger.error(f"Failed to get inner text from element {selector}: {e}")
            raise
    
    def get_attribute(self, selector: str, attribute: str, timeout: int = None) -> str:
        """
        Get attribute value of element
        
        Args:
            selector (str): Element selector
            attribute (str): Attribute name
            timeout (int): Timeout in milliseconds
        
        Returns:
            str: Attribute value
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            value = element.get_attribute(attribute, timeout=timeout)
            self.logger.info(f"Got attribute '{attribute}' = '{value}' from element: {selector}")
            return value or ""
        except Exception as e:
            self.logger.error(f"Failed to get attribute {attribute} from element {selector}: {e}")
            raise
    
    def is_element_visible(self, selector: str, timeout: int = None) -> bool:
        """
        Check if element is visible
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        
        Returns:
            bool: True if element is visible
        """
        try:
            timeout = timeout or self.short_timeout
            element = self.page.locator(selector)
            is_visible = element.is_visible(timeout=timeout)
            self.logger.info(f"Element visibility check for {selector}: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.error(f"Failed to check visibility of element {selector}: {e}")
            return False
    
    def is_element_enabled(self, selector: str, timeout: int = None) -> bool:
        """
        Check if element is enabled
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        
        Returns:
            bool: True if element is enabled
        """
        try:
            timeout = timeout or self.short_timeout
            element = self.page.locator(selector)
            is_enabled = element.is_enabled(timeout=timeout)
            self.logger.info(f"Element enabled check for {selector}: {is_enabled}")
            return is_enabled
        except Exception as e:
            self.logger.error(f"Failed to check if element {selector} is enabled: {e}")
            return False
    
    def is_element_checked(self, selector: str, timeout: int = None) -> bool:
        """
        Check if checkbox/radio element is checked
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        
        Returns:
            bool: True if element is checked
        """
        try:
            timeout = timeout or self.short_timeout
            element = self.page.locator(selector)
            is_checked = element.is_checked(timeout=timeout)
            self.logger.info(f"Element checked state for {selector}: {is_checked}")
            return is_checked
        except Exception as e:
            self.logger.error(f"Failed to check if element {selector} is checked: {e}")
            return False
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: int = None) -> None:
        """
        Wait for element to reach specified state
        
        Args:
            selector (str): Element selector
            state (str): State to wait for (visible, hidden, attached, detached)
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.wait_for(state=state, timeout=timeout)
            self.logger.info(f"Element {selector} reached state: {state}")
        except Exception as e:
            self.logger.error(f"Failed to wait for element {selector} to reach state {state}: {e}")
            raise
    
    def wait_for_element_to_disappear(self, selector: str, timeout: int = None) -> None:
        """
        Wait for element to disappear
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.wait_for(state="hidden", timeout=timeout)
            self.logger.info(f"Element disappeared: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to wait for element {selector} to disappear: {e}")
            raise
    
    def select_option(self, selector: str, option: Union[str, int, List[str]], timeout: int = None) -> None:
        """
        Select option from dropdown
        
        Args:
            selector (str): Select element selector
            option (Union[str, int, List[str]]): Option to select
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            
            if isinstance(option, int):
                element.select_option(index=option, timeout=timeout)
            elif isinstance(option, list):
                element.select_option(option, timeout=timeout)
            else:
                element.select_option(option, timeout=timeout)
            
            self.logger.info(f"Selected option '{option}' from element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to select option {option} from element {selector}: {e}")
            raise
    
    def check_checkbox(self, selector: str, timeout: int = None) -> None:
        """
        Check checkbox
        
        Args:
            selector (str): Checkbox selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.check(timeout=timeout)
            self.logger.info(f"Checked checkbox: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to check checkbox {selector}: {e}")
            raise
    
    def uncheck_checkbox(self, selector: str, timeout: int = None) -> None:
        """
        Uncheck checkbox
        
        Args:
            selector (str): Checkbox selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.uncheck(timeout=timeout)
            self.logger.info(f"Unchecked checkbox: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to uncheck checkbox {selector}: {e}")
            raise
    
    def upload_file(self, selector: str, file_path: str, timeout: int = None) -> None:
        """
        Upload file to file input
        
        Args:
            selector (str): File input selector
            file_path (str): Path to file to upload
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            element = self.page.locator(selector)
            element.set_input_files(file_path, timeout=timeout)
            self.logger.info(f"Uploaded file '{file_path}' to element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to upload file to element {selector}: {e}")
            raise
    
    def press_key(self, selector: str, key: str, timeout: int = None) -> None:
        """
        Press key on element
        
        Args:
            selector (str): Element selector
            key (str): Key to press
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.press(key, timeout=timeout)
            self.logger.info(f"Pressed key '{key}' on element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to press key {key} on element {selector}: {e}")
            raise
    
    def scroll_to_element(self, selector: str, timeout: int = None) -> None:
        """
        Scroll to element
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            element.scroll_into_view_if_needed(timeout=timeout)
            self.logger.info(f"Scrolled to element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to scroll to element {selector}: {e}")
            raise
    
    def drag_and_drop(self, source_selector: str, target_selector: str, timeout: int = None) -> None:
        """
        Drag and drop element
        
        Args:
            source_selector (str): Source element selector
            target_selector (str): Target element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            source = self.page.locator(source_selector)
            target = self.page.locator(target_selector)
            source.drag_to(target, timeout=timeout)
            self.logger.info(f"Dragged element {source_selector} to {target_selector}")
        except Exception as e:
            self.logger.error(f"Failed to drag element {source_selector} to {target_selector}: {e}")
            raise
    
    def get_page_title(self) -> str:
        """
        Get page title
        
        Returns:
            str: Page title
        """
        try:
            title = self.page.title()
            self.logger.info(f"Page title: {title}")
            return title
        except Exception as e:
            self.logger.error(f"Failed to get page title: {e}")
            raise
    
    def get_current_url(self) -> str:
        """
        Get current URL
        
        Returns:
            str: Current URL
        """
        try:
            url = self.page.url
            self.logger.info(f"Current URL: {url}")
            return url
        except Exception as e:
            self.logger.error(f"Failed to get current URL: {e}")
            raise
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript
        
        Args:
            script (str): JavaScript code to execute
            *args: Arguments to pass to script
        
        Returns:
            Any: Script result
        """
        try:
            result = self.page.evaluate(script, *args)
            self.logger.info("JavaScript executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed to execute JavaScript: {e}")
            raise
    
    def wait_for_page_load(self, timeout: int = None) -> None:
        """
        Wait for page to load completely
        
        Args:
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            self.logger.info("Page loaded completely")
        except Exception as e:
            self.logger.error(f"Failed to wait for page load: {e}")
            raise
    
    def wait(self, seconds: float) -> None:
        """
        Wait for specified seconds
        
        Args:
            seconds (float): Seconds to wait
        """
        try:
            time.sleep(seconds)
            self.logger.info(f"Waited for {seconds} seconds")
        except Exception as e:
            self.logger.error(f"Error during wait: {e}")
            raise
    
    def take_screenshot(self, file_path: str = None, full_page: bool = True) -> str:
        """
        Take screenshot
        
        Args:
            file_path (str): Path to save screenshot
            full_page (bool): Whether to capture full page
        
        Returns:
            str: Screenshot file path
        """
        try:
            return self.playwright_manager.take_screenshot(file_path, full_page)
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            raise
    
    # Assertion methods using Playwright's expect
    def expect_element_to_be_visible(self, selector: str, timeout: int = None) -> None:
        """
        Assert element is visible
        
        Args:
            selector (str): Element selector
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            expect(element).to_be_visible(timeout=timeout)
            self.logger.info(f"Assertion passed: Element {selector} is visible")
        except Exception as e:
            self.logger.error(f"Assertion failed: Element {selector} is not visible: {e}")
            raise
    
    def expect_element_to_have_text(self, selector: str, expected_text: str, timeout: int = None) -> None:
        """
        Assert element has expected text
        
        Args:
            selector (str): Element selector
            expected_text (str): Expected text
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            expect(element).to_have_text(expected_text, timeout=timeout)
            self.logger.info(f"Assertion passed: Element {selector} has text '{expected_text}'")
        except Exception as e:
            self.logger.error(f"Assertion failed: Element {selector} does not have text '{expected_text}': {e}")
            raise
    
    def expect_element_to_contain_text(self, selector: str, expected_text: str, timeout: int = None) -> None:
        """
        Assert element contains expected text
        
        Args:
            selector (str): Element selector
            expected_text (str): Expected text
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            element = self.page.locator(selector)
            expect(element).to_contain_text(expected_text, timeout=timeout)
            self.logger.info(f"Assertion passed: Element {selector} contains text '{expected_text}'")
        except Exception as e:
            self.logger.error(f"Assertion failed: Element {selector} does not contain text '{expected_text}': {e}")
            raise
    
    def expect_page_to_have_title(self, expected_title: str, timeout: int = None) -> None:
        """
        Assert page has expected title
        
        Args:
            expected_title (str): Expected title
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            expect(self.page).to_have_title(expected_title, timeout=timeout)
            self.logger.info(f"Assertion passed: Page has title '{expected_title}'")
        except Exception as e:
            self.logger.error(f"Assertion failed: Page does not have title '{expected_title}': {e}")
            raise
    
    def expect_page_to_have_url(self, expected_url: str, timeout: int = None) -> None:
        """
        Assert page has expected URL
        
        Args:
            expected_url (str): Expected URL
            timeout (int): Timeout in milliseconds
        """
        try:
            timeout = timeout or self.default_timeout
            expect(self.page).to_have_url(expected_url, timeout=timeout)
            self.logger.info(f"Assertion passed: Page has URL '{expected_url}'")
        except Exception as e:
            self.logger.error(f"Assertion failed: Page does not have URL '{expected_url}': {e}")
            raise

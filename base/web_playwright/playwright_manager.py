from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from playwright.sync_api import expect
import logging
import time
from typing import Optional, Dict, Any, List
import os


class PlaywrightManager:
    """Manager class for Playwright browser operations"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default browser settings
        self.default_timeout = 30000  # 30 seconds
        self.default_viewport = {"width": 1920, "height": 1080}
        
    def start_playwright(self):
        """Start Playwright"""
        try:
            self.playwright = sync_playwright().start()
            self.logger.info("Playwright started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Playwright: {e}")
            raise
    
    def launch_browser(self, browser_name: str = "chromium", headless: bool = False, **kwargs):
        """
        Launch browser
        
        Args:
            browser_name (str): Browser name (chromium, firefox, webkit)
            headless (bool): Whether to run in headless mode
            **kwargs: Additional browser launch options
        """
        try:
            if not self.playwright:
                self.start_playwright()
            
            browser_options = {
                "headless": headless,
                "args": kwargs.get("args", []),
                "slow_mo": kwargs.get("slow_mo", 0),
                "devtools": kwargs.get("devtools", False)
            }
            
            if browser_name.lower() == "chromium":
                self.browser = self.playwright.chromium.launch(**browser_options)
            elif browser_name.lower() == "firefox":
                self.browser = self.playwright.firefox.launch(**browser_options)
            elif browser_name.lower() == "webkit":
                self.browser = self.playwright.webkit.launch(**browser_options)
            else:
                raise ValueError(f"Unsupported browser: {browser_name}")
            
            self.logger.info(f"Browser {browser_name} launched successfully")
        except Exception as e:
            self.logger.error(f"Failed to launch browser {browser_name}: {e}")
            raise
    
    def create_context(self, **kwargs) -> BrowserContext:
        """
        Create browser context
        
        Args:
            **kwargs: Context options
        
        Returns:
            BrowserContext: Browser context
        """
        try:
            if not self.browser:
                raise Exception("Browser not launched. Call launch_browser() first.")
            
            context_options = {
                "viewport": kwargs.get("viewport", self.default_viewport),
                "user_agent": kwargs.get("user_agent"),
                "locale": kwargs.get("locale"),
                "timezone_id": kwargs.get("timezone_id"),
                "permissions": kwargs.get("permissions"),
                "geolocation": kwargs.get("geolocation"),
                "extra_http_headers": kwargs.get("extra_http_headers"),
                "http_credentials": kwargs.get("http_credentials"),
                "offline": kwargs.get("offline", False),
                "ignore_https_errors": kwargs.get("ignore_https_errors", False),
                "record_video_dir": kwargs.get("record_video_dir"),
                "record_video_size": kwargs.get("record_video_size"),
                "record_har_path": kwargs.get("record_har_path")
            }
            
            # Remove None values
            context_options = {k: v for k, v in context_options.items() if v is not None}
            
            self.context = self.browser.new_context(**context_options)
            self.context.set_default_timeout(self.default_timeout)
            
            self.logger.info("Browser context created successfully")
            return self.context
        except Exception as e:
            self.logger.error(f"Failed to create browser context: {e}")
            raise
    
    def create_page(self) -> Page:
        """
        Create new page
        
        Returns:
            Page: Browser page
        """
        try:
            if not self.context:
                self.create_context()
            
            self.page = self.context.new_page()
            self.logger.info("New page created successfully")
            return self.page
        except Exception as e:
            self.logger.error(f"Failed to create page: {e}")
            raise
    
    def navigate_to(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to URL
        
        Args:
            url (str): URL to navigate to
            wait_until (str): When to consider navigation successful
        """
        try:
            if not self.page:
                self.create_page()
            
            self.page.goto(url, wait_until=wait_until)
            self.logger.info(f"Navigated to: {url}")
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
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
            if not self.page:
                raise Exception("No page available for screenshot")
            
            if not file_path:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                file_path = f"screenshot_{timestamp}.png"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            self.page.screenshot(path=file_path, full_page=full_page)
            self.logger.info(f"Screenshot saved: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            raise
    
    def close_page(self) -> None:
        """Close current page"""
        try:
            if self.page:
                self.page.close()
                self.page = None
                self.logger.info("Page closed")
        except Exception as e:
            self.logger.error(f"Failed to close page: {e}")
    
    def close_context(self) -> None:
        """Close browser context"""
        try:
            if self.context:
                self.context.close()
                self.context = None
                self.logger.info("Browser context closed")
        except Exception as e:
            self.logger.error(f"Failed to close context: {e}")
    
    def close_browser(self) -> None:
        """Close browser"""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
                self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Failed to close browser: {e}")
    
    def stop_playwright(self) -> None:
        """Stop Playwright"""
        try:
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
                self.logger.info("Playwright stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop Playwright: {e}")
    
    def quit(self) -> None:
        """Clean shutdown of all resources"""
        try:
            self.close_page()
            self.close_context()
            self.close_browser()
            self.stop_playwright()
            self.logger.info("Playwright manager shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_page_title(self) -> str:
        """
        Get current page title
        
        Returns:
            str: Page title
        """
        try:
            if not self.page:
                raise Exception("No page available")
            
            title = self.page.title()
            self.logger.info(f"Page title: {title}")
            return title
        except Exception as e:
            self.logger.error(f"Failed to get page title: {e}")
            raise
    
    def get_current_url(self) -> str:
        """
        Get current page URL
        
        Returns:
            str: Current URL
        """
        try:
            if not self.page:
                raise Exception("No page available")
            
            url = self.page.url
            self.logger.info(f"Current URL: {url}")
            return url
        except Exception as e:
            self.logger.error(f"Failed to get current URL: {e}")
            raise
    
    def wait_for_load_state(self, state: str = "networkidle", timeout: int = None) -> None:
        """
        Wait for page load state
        
        Args:
            state (str): Load state to wait for (load, domcontentloaded, networkidle)
            timeout (int): Timeout in milliseconds
        """
        try:
            if not self.page:
                raise Exception("No page available")
            
            timeout = timeout or self.default_timeout
            self.page.wait_for_load_state(state, timeout=timeout)
            self.logger.info(f"Page load state '{state}' reached")
        except Exception as e:
            self.logger.error(f"Failed to wait for load state '{state}': {e}")
            raise
    
    def reload_page(self, wait_until: str = "networkidle") -> None:
        """
        Reload current page
        
        Args:
            wait_until (str): When to consider reload complete
        """
        try:
            if not self.page:
                raise Exception("No page available")
            
            self.page.reload(wait_until=wait_until)
            self.logger.info("Page reloaded")
        except Exception as e:
            self.logger.error(f"Failed to reload page: {e}")
            raise
    
    def go_back(self, wait_until: str = "networkidle") -> None:
        """
        Navigate back in browser history
        
        Args:
            wait_until (str): When to consider navigation complete
        """
        try:
            if not self.page:
                raise Exception("No page available")
            
            self.page.go_back(wait_until=wait_until)
            self.logger.info("Navigated back")
        except Exception as e:
            self.logger.error(f"Failed to go back: {e}")
            raise
    
    def go_forward(self, wait_until: str = "networkidle") -> None:
        """
        Navigate forward in browser history
        
        Args:
            wait_until (str): When to consider navigation complete
        """
        try:
            if not self.page:
                raise Exception("No page available")
            
            self.page.go_forward(wait_until=wait_until)
            self.logger.info("Navigated forward")
        except Exception as e:
            self.logger.error(f"Failed to go forward: {e}")
            raise

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import configparser
import os
import logging


class WebDriverManager:
    """Base WebDriver manager for handling browser initialization and configuration"""
    
    def __init__(self, config_path=None):
        self.driver = None
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if config_path and os.path.exists(config_path):
            self.config.read(config_path)
        else:
            # Default configuration
            self.config['selenium'] = {
                'browser': 'chrome',
                'headless': 'false',
                'window_size': '1920x1080',
                'timeout': '10'
            }
    
    def get_driver(self, browser=None, headless=None, window_size=None):
        """Get WebDriver instance with specified configuration"""
        browser = browser or self.config.get('selenium', 'browser', fallback='chrome')
        headless = headless or self.config.getboolean('selenium', 'headless', fallback=False)
        window_size = window_size or self.config.get('selenium', 'window_size', fallback='1920x1080')
        
        if browser.lower() == 'chrome':
            self.driver = self._get_chrome_driver(headless, window_size)
        elif browser.lower() == 'firefox':
            self.driver = self._get_firefox_driver(headless, window_size)
        elif browser.lower() == 'edge':
            self.driver = self._get_edge_driver(headless, window_size)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        # Set implicit wait
        timeout = self.config.getint('selenium', 'timeout', fallback=10)
        self.driver.implicitly_wait(timeout)
        
        self.logger.info(f"WebDriver initialized: {browser}")
        return self.driver
    
    def _get_chrome_driver(self, headless, window_size):
        """Initialize Chrome WebDriver"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        options.add_argument(f'--window-size={window_size}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _get_firefox_driver(self, headless, window_size):
        """Initialize Firefox WebDriver"""
        from selenium.webdriver.firefox.options import Options
        
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        width, height = window_size.split('x')
        options.add_argument(f'--width={width}')
        options.add_argument(f'--height={height}')
        
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    def _get_edge_driver(self, headless, window_size):
        """Initialize Edge WebDriver"""
        from selenium.webdriver.edge.options import Options
        
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        options.add_argument(f'--window-size={window_size}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    
    def quit_driver(self):
        """Quit the WebDriver instance"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver quit")
            self.driver = None
    
    def maximize_window(self):
        """Maximize browser window"""
        if self.driver:
            self.driver.maximize_window()
            self.logger.info("Browser window maximized")
    
    def set_window_size(self, width, height):
        """Set browser window size"""
        if self.driver:
            self.driver.set_window_size(width, height)
            self.logger.info(f"Window size set to {width}x{height}")
    
    def navigate_to(self, url):
        """Navigate to specified URL"""
        if self.driver:
            self.driver.get(url)
            self.logger.info(f"Navigated to: {url}")
    
    def get_current_url(self):
        """Get current URL"""
        if self.driver:
            return self.driver.current_url
        return None
    
    def get_page_title(self):
        """Get current page title"""
        if self.driver:
            return self.driver.title
        return None
    
    def take_screenshot(self, filepath):
        """Take screenshot and save to file"""
        if self.driver:
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            return filepath
        return None
    
    def delete_all_cookies(self):
        """Delete all browser cookies"""
        if self.driver:
            self.driver.delete_all_cookies()
            self.logger.info("All cookies deleted")
    
    def add_cookie(self, cookie_dict):
        """Add a cookie"""
        if self.driver:
            self.driver.add_cookie(cookie_dict)
            self.logger.info(f"Cookie added: {cookie_dict}")
    
    def get_cookie(self, name):
        """Get a specific cookie by name"""
        if self.driver:
            cookie = self.driver.get_cookie(name)
            self.logger.info(f"Retrieved cookie: {name}")
            return cookie
        return None
    
    def execute_script(self, script, *args):
        """Execute JavaScript"""
        if self.driver:
            result = self.driver.execute_script(script, *args)
            self.logger.info(f"JavaScript executed: {script}")
            return result
        return None

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
import atexit
import threading
import time
import psutil
import weakref
from typing import Dict, List, Optional, Any
from datetime import datetime


class DriverInstance:
    """Track individual driver instance information"""
    def __init__(self, driver, browser: str, process_id: int = None):
        self.driver = driver
        self.browser = browser
        self.process_id = process_id
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.is_active = True
        self.memory_usage = 0
        self.session_id = getattr(driver, 'session_id', None)
    
    def update_usage(self):
        """Update last used timestamp and memory usage"""
        self.last_used = datetime.now()
        try:
            if self.process_id:
                process = psutil.Process(self.process_id)
                self.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.is_active = False
    
    def cleanup(self):
        """Clean up driver instance"""
        try:
            if self.driver and self.is_active:
                self.driver.quit()
                self.is_active = False
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error during driver cleanup: {e}")


class WebDriverRegistry:
    """Global registry for tracking all WebDriver instances"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not getattr(self, '_initialized', False):
            self.drivers: Dict[str, DriverInstance] = {}
            self.cleanup_lock = threading.Lock()
            self.logger = logging.getLogger(self.__class__.__name__)
            self._setup_cleanup_hooks()
            self._initialized = True
    
    def register_driver(self, driver_id: str, driver, browser: str) -> str:
        """Register a new driver instance"""
        process_id = None
        try:
            # Get browser process ID
            if hasattr(driver, 'service') and hasattr(driver.service, 'process'):
                process_id = driver.service.process.pid
        except Exception:
            pass
        
        instance = DriverInstance(driver, browser, process_id)
        
        with self.cleanup_lock:
            self.drivers[driver_id] = instance
        
        self.logger.info(f"Registered driver {driver_id} (browser: {browser}, PID: {process_id})")
        return driver_id
    
    def unregister_driver(self, driver_id: str):
        """Unregister and cleanup driver instance"""
        with self.cleanup_lock:
            if driver_id in self.drivers:
                instance = self.drivers[driver_id]
                instance.cleanup()
                del self.drivers[driver_id]
                self.logger.info(f"Unregistered driver {driver_id}")
    
    def get_driver_info(self, driver_id: str) -> Optional[DriverInstance]:
        """Get driver instance information"""
        return self.drivers.get(driver_id)
    
    def update_driver_usage(self, driver_id: str):
        """Update driver usage statistics"""
        if driver_id in self.drivers:
            self.drivers[driver_id].update_usage()
    
    def cleanup_all_drivers(self):
        """Cleanup all registered drivers"""
        with self.cleanup_lock:
            driver_ids = list(self.drivers.keys())
            for driver_id in driver_ids:
                self.unregister_driver(driver_id)
        self.logger.info("All drivers cleaned up")
    
    def force_cleanup_stale_drivers(self):
        """Force cleanup of stale/zombie driver processes"""
        with self.cleanup_lock:
            stale_drivers = []
            for driver_id, instance in self.drivers.items():
                try:
                    if instance.process_id:
                        process = psutil.Process(instance.process_id)
                        # Check if process is still running
                        if not process.is_running():
                            stale_drivers.append(driver_id)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    stale_drivers.append(driver_id)
            
            for driver_id in stale_drivers:
                self.logger.warning(f"Force cleaning stale driver: {driver_id}")
                self.unregister_driver(driver_id)
    
    def get_all_driver_stats(self) -> Dict[str, Any]:
        """Get statistics for all drivers"""
        stats = {
            'total_drivers': len(self.drivers),
            'active_drivers': 0,
            'total_memory_mb': 0,
            'drivers': {}
        }
        
        for driver_id, instance in self.drivers.items():
            instance.update_usage()
            if instance.is_active:
                stats['active_drivers'] += 1
                stats['total_memory_mb'] += instance.memory_usage
            
            stats['drivers'][driver_id] = {
                'browser': instance.browser,
                'created_at': instance.created_at.isoformat(),
                'last_used': instance.last_used.isoformat(),
                'memory_mb': instance.memory_usage,
                'is_active': instance.is_active,
                'process_id': instance.process_id
            }
        
        return stats
    
    def _setup_cleanup_hooks(self):
        """Setup cleanup hooks for proper resource management"""
        atexit.register(self.cleanup_all_drivers)


class WebDriverManager:
    """Enhanced WebDriver manager with automatic cleanup and instance tracking"""
    
    def __init__(self, config_path=None):
        self.driver = None
        self.driver_id = None
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.registry = WebDriverRegistry()
        self._cleanup_thread = None
        self._cleanup_interval = 300  # 5 minutes
        
        if config_path and os.path.exists(config_path):
            self.config.read(config_path)
        else:
            # Default configuration
            self.config['selenium'] = {
                'browser': 'chrome',
                'headless': 'false',
                'window_size': '1920x1080',
                'timeout': '10',
                'cleanup_interval': '300',
                'memory_threshold_mb': '500'
            }
        
        # Setup automatic cleanup
        self._setup_automatic_cleanup()
    
    def _setup_automatic_cleanup(self):
        """Setup automatic cleanup thread"""
        self._cleanup_interval = self.config.getint('selenium', 'cleanup_interval', fallback=300)
        
        def cleanup_worker():
            while True:
                time.sleep(self._cleanup_interval)
                try:
                    self.registry.force_cleanup_stale_drivers()
                    self._cleanup_high_memory_drivers()
                except Exception as e:
                    self.logger.error(f"Error in cleanup worker: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        self.logger.info("Automatic cleanup thread started")
    
    def _cleanup_high_memory_drivers(self):
        """Cleanup drivers exceeding memory threshold"""
        memory_threshold = self.config.getint('selenium', 'memory_threshold_mb', fallback=500)
        stats = self.registry.get_all_driver_stats()
        
        for driver_id, driver_stats in stats['drivers'].items():
            if driver_stats['memory_mb'] > memory_threshold:
                self.logger.warning(f"Driver {driver_id} exceeding memory threshold: {driver_stats['memory_mb']}MB")
                # Don't cleanup current driver
                if driver_id != self.driver_id:
                    self.registry.unregister_driver(driver_id)
    
    def get_driver(self, browser=None, headless=None, window_size=None):
        """Get WebDriver instance with enhanced tracking and cleanup"""
        browser = browser or self.config.get('selenium', 'browser', fallback='chrome')
        headless = headless or self.config.getboolean('selenium', 'headless', fallback=False)
        window_size = window_size or self.config.get('selenium', 'window_size', fallback='1920x1080')
        
        # Cleanup previous driver if exists
        if self.driver:
            self.quit_driver()
        
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
        
        # Register driver with tracking
        self.driver_id = f"{browser}_{threading.current_thread().ident}_{int(time.time())}"
        self.registry.register_driver(self.driver_id, self.driver, browser)
        
        self.logger.info(f"WebDriver initialized: {browser} (ID: {self.driver_id})")
        return self.driver
    
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
        """Enhanced quit with proper cleanup and verification"""
        if self.driver and self.driver_id:
            try:
                # Update usage before cleanup
                self.registry.update_driver_usage(self.driver_id)
                
                # Get driver info for verification
                driver_info = self.registry.get_driver_info(self.driver_id)
                if driver_info:
                    process_id = driver_info.process_id
                    
                    # Quit the driver
                    self.driver.quit()
                    
                    # Verify process termination
                    if process_id:
                        self._verify_process_termination(process_id)
                
                # Unregister from tracking
                self.registry.unregister_driver(self.driver_id)
                
                self.logger.info(f"WebDriver quit and verified (ID: {self.driver_id})")
                
            except Exception as e:
                self.logger.error(f"Error during driver quit: {e}")
                # Force cleanup
                self._force_quit_driver()
            finally:
                self.driver = None
                self.driver_id = None
    
    def _verify_process_termination(self, process_id: int, timeout: int = 10):
        """Verify that driver process has terminated"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                process = psutil.Process(process_id)
                if not process.is_running():
                    return True
                time.sleep(0.5)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return True
        
        # Force kill if still running
        try:
            process = psutil.Process(process_id)
            process.kill()
            self.logger.warning(f"Force killed driver process {process_id}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return False
    
    def _force_quit_driver(self):
        """Force quit driver and cleanup resources"""
        if self.driver_id:
            driver_info = self.registry.get_driver_info(self.driver_id)
            if driver_info and driver_info.process_id:
                try:
                    process = psutil.Process(driver_info.process_id)
                    process.terminate()
                    time.sleep(2)
                    if process.is_running():
                        process.kill()
                    self.logger.warning(f"Force terminated driver process {driver_info.process_id}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            self.registry.unregister_driver(self.driver_id)
    
    def get_driver_stats(self) -> Dict[str, Any]:
        """Get current driver statistics"""
        if self.driver_id:
            self.registry.update_driver_usage(self.driver_id)
            driver_info = self.registry.get_driver_info(self.driver_id)
            if driver_info:
                return {
                    'driver_id': self.driver_id,
                    'browser': driver_info.browser,
                    'memory_mb': driver_info.memory_usage,
                    'created_at': driver_info.created_at.isoformat(),
                    'last_used': driver_info.last_used.isoformat(),
                    'is_active': driver_info.is_active,
                    'session_id': driver_info.session_id
                }
        return {}
    
    def cleanup_all_instances(self):
        """Cleanup all driver instances"""
        self.registry.cleanup_all_drivers()
    
    @classmethod
    def get_global_stats(cls) -> Dict[str, Any]:
        """Get global driver statistics"""
        registry = WebDriverRegistry()
        return registry.get_all_driver_stats()
    
    def maximize_window(self):
        """Maximize browser window"""
        if self.driver:
            self.driver.maximize_window()
            self.logger.info("Browser window maximized")
            self._update_driver_usage()
    
    def set_window_size(self, width, height):
        """Set browser window size"""
        if self.driver:
            self.driver.set_window_size(width, height)
            self.logger.info(f"Window size set to {width}x{height}")
            self._update_driver_usage()
    
    def navigate_to(self, url):
        """Navigate to specified URL"""
        if self.driver:
            self.driver.get(url)
            self.logger.info(f"Navigated to: {url}")
            self._update_driver_usage()
    
    def get_current_url(self):
        """Get current URL"""
        if self.driver:
            self._update_driver_usage()
            return self.driver.current_url
        return None
    
    def get_page_title(self):
        """Get current page title"""
        if self.driver:
            self._update_driver_usage()
            return self.driver.title
        return None
    
    def take_screenshot(self, filepath):
        """Take screenshot and save to file"""
        if self.driver:
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            self._update_driver_usage()
            return filepath
        return None
    
    def delete_all_cookies(self):
        """Delete all browser cookies"""
        if self.driver:
            self.driver.delete_all_cookies()
            self.logger.info("All cookies deleted")
            self._update_driver_usage()
    
    def add_cookie(self, cookie_dict):
        """Add a cookie"""
        if self.driver:
            self.driver.add_cookie(cookie_dict)
            self.logger.info(f"Cookie added: {cookie_dict}")
            self._update_driver_usage()
    
    def get_cookie(self, name):
        """Get a specific cookie by name"""
        if self.driver:
            cookie = self.driver.get_cookie(name)
            self.logger.info(f"Retrieved cookie: {name}")
            self._update_driver_usage()
            return cookie
        return None
    
    def execute_script(self, script, *args):
        """Execute JavaScript"""
        if self.driver:
            result = self.driver.execute_script(script, *args)
            self.logger.info(f"JavaScript executed: {script}")
            self._update_driver_usage()
            return result
        return None
    
    def _update_driver_usage(self):
        """Update driver usage statistics"""
        if self.driver_id:
            self.registry.update_driver_usage(self.driver_id)

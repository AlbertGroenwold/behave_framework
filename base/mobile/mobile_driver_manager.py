from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
import configparser
import os
import logging


class MobileDriverManager:
    """Base mobile driver manager for handling Appium driver initialization"""
    
    def __init__(self, config_path=None):
        self.driver = None
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if config_path and os.path.exists(config_path):
            self.config.read(config_path)
        else:
            # Default configuration
            self.config['appium'] = {
                'server_url': 'http://localhost:4723',
                'platform': 'Android',
                'device_name': 'emulator-5554',
                'app_package': '',
                'app_activity': '',
                'automation_name': 'UiAutomator2'
            }
    
    def get_driver(self, platform=None, device_name=None, app_package=None, app_activity=None):
        """Get Appium driver instance with specified configuration"""
        platform = platform or self.config.get('appium', 'platform', fallback='Android')
        
        if platform.lower() == 'android':
            self.driver = self._get_android_driver(device_name, app_package, app_activity)
        elif platform.lower() == 'ios':
            self.driver = self._get_ios_driver(device_name)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        self.logger.info(f"Mobile driver initialized: {platform}")
        return self.driver
    
    def _get_android_driver(self, device_name=None, app_package=None, app_activity=None):
        """Initialize Android driver"""
        options = UiAutomator2Options()
        
        # Basic capabilities
        options.platform_name = "Android"
        options.device_name = device_name or self.config.get('appium', 'device_name', fallback='emulator-5554')
        options.automation_name = self.config.get('appium', 'automation_name', fallback='UiAutomator2')
        
        # App capabilities
        if app_package:
            options.app_package = app_package
        elif self.config.has_option('appium', 'app_package'):
            options.app_package = self.config.get('appium', 'app_package')
        
        if app_activity:
            options.app_activity = app_activity
        elif self.config.has_option('appium', 'app_activity'):
            options.app_activity = self.config.get('appium', 'app_activity')
        
        # Optional capabilities
        if self.config.has_option('appium', 'app_path'):
            options.app = self.config.get('appium', 'app_path')
        
        if self.config.has_option('appium', 'platform_version'):
            options.platform_version = self.config.get('appium', 'platform_version')
        
        # Performance and behavior settings
        options.no_reset = self.config.getboolean('appium', 'no_reset', fallback=False)
        options.full_reset = self.config.getboolean('appium', 'full_reset', fallback=False)
        options.new_command_timeout = self.config.getint('appium', 'new_command_timeout', fallback=60)
        
        # Server URL
        server_url = self.config.get('appium', 'server_url', fallback='http://localhost:4723')
        
        return webdriver.Remote(server_url, options=options)
    
    def _get_ios_driver(self, device_name=None):
        """Initialize iOS driver"""
        options = XCUITestOptions()
        
        # Basic capabilities
        options.platform_name = "iOS"
        options.device_name = device_name or self.config.get('appium', 'device_name', fallback='iPhone Simulator')
        options.automation_name = "XCUITest"
        
        # App capabilities
        if self.config.has_option('appium', 'bundle_id'):
            options.bundle_id = self.config.get('appium', 'bundle_id')
        
        if self.config.has_option('appium', 'app_path'):
            options.app = self.config.get('appium', 'app_path')
        
        if self.config.has_option('appium', 'platform_version'):
            options.platform_version = self.config.get('appium', 'platform_version')
        
        # Performance and behavior settings
        options.no_reset = self.config.getboolean('appium', 'no_reset', fallback=False)
        options.full_reset = self.config.getboolean('appium', 'full_reset', fallback=False)
        options.new_command_timeout = self.config.getint('appium', 'new_command_timeout', fallback=60)
        
        # Server URL
        server_url = self.config.get('appium', 'server_url', fallback='http://localhost:4723')
        
        return webdriver.Remote(server_url, options=options)
    
    def quit_driver(self):
        """Quit the mobile driver instance"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Mobile driver quit")
            self.driver = None
    
    def install_app(self, app_path):
        """Install app on device"""
        if self.driver:
            self.driver.install_app(app_path)
            self.logger.info(f"App installed: {app_path}")
    
    def remove_app(self, app_package):
        """Remove app from device"""
        if self.driver:
            self.driver.remove_app(app_package)
            self.logger.info(f"App removed: {app_package}")
    
    def launch_app(self):
        """Launch the app"""
        if self.driver:
            self.driver.launch_app()
            self.logger.info("App launched")
    
    def close_app(self):
        """Close the app"""
        if self.driver:
            self.driver.close_app()
            self.logger.info("App closed")
    
    def reset_app(self):
        """Reset the app"""
        if self.driver:
            self.driver.reset()
            self.logger.info("App reset")
    
    def background_app(self, seconds=5):
        """Put app in background for specified seconds"""
        if self.driver:
            self.driver.background_app(seconds)
            self.logger.info(f"App backgrounded for {seconds} seconds")
    
    def is_app_installed(self, app_package):
        """Check if app is installed"""
        if self.driver:
            installed = self.driver.is_app_installed(app_package)
            self.logger.info(f"App {app_package} installed: {installed}")
            return installed
        return False
    
    def get_device_time(self):
        """Get device time"""
        if self.driver:
            device_time = self.driver.device_time
            self.logger.info(f"Device time: {device_time}")
            return device_time
        return None
    
    def set_network_connection(self, connection_type):
        """Set network connection type"""
        if self.driver:
            self.driver.set_network_connection(connection_type)
            self.logger.info(f"Network connection set to: {connection_type}")
    
    def get_network_connection(self):
        """Get current network connection"""
        if self.driver:
            connection = self.driver.network_connection
            self.logger.info(f"Current network connection: {connection}")
            return connection
        return None
    
    def toggle_wifi(self):
        """Toggle WiFi on/off"""
        if self.driver:
            self.driver.toggle_wifi()
            self.logger.info("WiFi toggled")
    
    def toggle_mobile_data(self):
        """Toggle mobile data on/off"""
        if self.driver:
            self.driver.toggle_data()
            self.logger.info("Mobile data toggled")
    
    def get_performance_data(self, package_name, data_type):
        """Get performance data for app"""
        if self.driver:
            data = self.driver.get_performance_data(package_name, data_type)
            self.logger.info(f"Performance data retrieved for {package_name}")
            return data
        return None
    
    def start_recording_screen(self, **options):
        """Start screen recording"""
        if self.driver:
            self.driver.start_recording_screen(**options)
            self.logger.info("Screen recording started")
    
    def stop_recording_screen(self):
        """Stop screen recording and return video data"""
        if self.driver:
            video_data = self.driver.stop_recording_screen()
            self.logger.info("Screen recording stopped")
            return video_data
        return None
    
    def take_screenshot(self, filepath):
        """Take screenshot and save to file"""
        if self.driver:
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Mobile screenshot saved: {filepath}")
            return filepath
        return None

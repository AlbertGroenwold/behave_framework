import sys
import os

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from appium.webdriver.common.appiumby import AppiumBy
from mobile.base_mobile_page import BaseMobilePage


class MobileHomePage(BaseMobilePage):
    """Mobile home page object following Page Object Model pattern"""
    
    # Android Locators
    ANDROID_HOME_SCREEN = (AppiumBy.ID, "com.example.app:id/home_screen")
    ANDROID_USER_PROFILE = (AppiumBy.ID, "com.example.app:id/user_profile")
    ANDROID_LOGOUT_BUTTON = (AppiumBy.ID, "com.example.app:id/logout_button")
    ANDROID_MENU_BUTTON = (AppiumBy.ID, "com.example.app:id/menu_button")
    ANDROID_WELCOME_MESSAGE = (AppiumBy.ID, "com.example.app:id/welcome_message")
    
    # iOS Locators
    IOS_HOME_SCREEN = (AppiumBy.ACCESSIBILITY_ID, "home_screen")
    IOS_USER_PROFILE = (AppiumBy.ACCESSIBILITY_ID, "user_profile")
    IOS_LOGOUT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "logout_button")
    IOS_MENU_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "menu_button")
    IOS_WELCOME_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, "welcome_message")
    
    def __init__(self, driver):
        super().__init__(driver)
        
        # Set platform-specific locators
        if self.is_android():
            self.home_screen = self.ANDROID_HOME_SCREEN
            self.user_profile = self.ANDROID_USER_PROFILE
            self.logout_button = self.ANDROID_LOGOUT_BUTTON
            self.menu_button = self.ANDROID_MENU_BUTTON
            self.welcome_message = self.ANDROID_WELCOME_MESSAGE
        else:  # iOS
            self.home_screen = self.IOS_HOME_SCREEN
            self.user_profile = self.IOS_USER_PROFILE
            self.logout_button = self.IOS_LOGOUT_BUTTON
            self.menu_button = self.IOS_MENU_BUTTON
            self.welcome_message = self.IOS_WELCOME_MESSAGE
    
    def is_logged_in(self):
        """Check if user is logged in (home screen is displayed)"""
        try:
            self.wait_for_element_to_be_visible(self.home_screen, timeout=10)
            return True
        except:
            return False
    
    def is_home_screen_displayed(self):
        """Check if home screen is displayed"""
        return self.is_element_displayed(self.home_screen)
    
    def is_welcome_message_displayed(self):
        """Check if welcome message is displayed"""
        return self.is_element_displayed(self.welcome_message)
    
    def get_welcome_message_text(self):
        """Get welcome message text"""
        if self.is_welcome_message_displayed():
            return self.get_element_text(self.welcome_message)
        return ""
    
    def tap_user_profile(self):
        """Tap user profile"""
        self.wait_for_element_to_be_clickable(self.user_profile)
        self.tap_element(self.user_profile)
        self.logger.info("Tapped user profile")
    
    def tap_logout_button(self):
        """Tap logout button"""
        self.wait_for_element_to_be_clickable(self.logout_button)
        self.tap_element(self.logout_button)
        self.logger.info("Tapped logout button")
    
    def tap_menu_button(self):
        """Tap menu button"""
        self.wait_for_element_to_be_clickable(self.menu_button)
        self.tap_element(self.menu_button)
        self.logger.info("Tapped menu button")
    
    def is_in_landscape_mode(self):
        """Check if screen is in landscape mode"""
        orientation = self.get_orientation()
        return orientation == 'LANDSCAPE'
    
    def is_in_portrait_mode(self):
        """Check if screen is in portrait mode"""
        orientation = self.get_orientation()
        return orientation == 'PORTRAIT'
    
    def wait_for_home_screen_to_load(self, timeout=15):
        """
        Wait for home screen to fully load
        
        Args:
            timeout (int): Maximum time to wait in seconds
        """
        self.wait_for_element_to_be_visible(self.home_screen, timeout)
        self.logger.info("Home screen loaded successfully")

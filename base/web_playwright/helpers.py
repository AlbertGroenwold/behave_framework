import logging
import time
from typing import Dict, Any, List, Optional
from playwright.sync_api import Page, BrowserContext
from .playwright_manager import PlaywrightManager


class PlaywrightHelpers:
    """Helper methods for Playwright automation"""
    
    def __init__(self, playwright_manager: PlaywrightManager):
        self.playwright_manager = playwright_manager
        self.page: Page = playwright_manager.page
        self.context: BrowserContext = playwright_manager.context
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def handle_dialog(self, accept: bool = True, prompt_text: str = None) -> None:
        """
        Set up dialog handler
        
        Args:
            accept (bool): Whether to accept or dismiss dialog
            prompt_text (str): Text to enter in prompt dialog
        """
        try:
            def dialog_handler(dialog):
                if dialog.type == "prompt" and prompt_text:
                    dialog.accept(prompt_text)
                elif accept:
                    dialog.accept()
                else:
                    dialog.dismiss()
                self.logger.info(f"Dialog handled: {dialog.type}, accept={accept}")
            
            self.page.on("dialog", dialog_handler)
            self.logger.info("Dialog handler set up")
        except Exception as e:
            self.logger.error(f"Failed to set up dialog handler: {e}")
            raise
    
    def handle_popup(self, popup_handler_func: callable = None) -> None:
        """
        Set up popup handler
        
        Args:
            popup_handler_func (callable): Function to handle popup
        """
        try:
            def default_popup_handler(popup):
                popup.wait_for_load_state()
                self.logger.info(f"Popup opened: {popup.url}")
                return popup
            
            handler = popup_handler_func or default_popup_handler
            self.page.on("popup", handler)
            self.logger.info("Popup handler set up")
        except Exception as e:
            self.logger.error(f"Failed to set up popup handler: {e}")
            raise
    
    def wait_for_download(self, timeout: int = 30000) -> Dict[str, Any]:
        """
        Wait for download to start
        
        Args:
            timeout (int): Timeout in milliseconds
        
        Returns:
            Dict[str, Any]: Download information
        """
        try:
            with self.page.expect_download(timeout=timeout) as download_info:
                download = download_info.value
                
            download_details = {
                "url": download.url,
                "suggested_filename": download.suggested_filename,
                "path": None
            }
            
            # Save the download
            download_path = f"downloads/{download.suggested_filename}"
            download.save_as(download_path)
            download_details["path"] = download_path
            
            self.logger.info(f"Download completed: {download_details}")
            return download_details
        except Exception as e:
            self.logger.error(f"Failed to handle download: {e}")
            raise
    
    def set_geolocation(self, latitude: float, longitude: float) -> None:
        """
        Set geolocation
        
        Args:
            latitude (float): Latitude
            longitude (float): Longitude
        """
        try:
            self.context.set_geolocation({"latitude": latitude, "longitude": longitude})
            self.logger.info(f"Geolocation set: {latitude}, {longitude}")
        except Exception as e:
            self.logger.error(f"Failed to set geolocation: {e}")
            raise
    
    def clear_permissions(self) -> None:
        """Clear all permissions"""
        try:
            self.context.clear_permissions()
            self.logger.info("Permissions cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear permissions: {e}")
            raise
    
    def grant_permissions(self, permissions: List[str], origin: str = None) -> None:
        """
        Grant permissions
        
        Args:
            permissions (List[str]): List of permissions to grant
            origin (str): Origin to grant permissions for
        """
        try:
            if origin:
                self.context.grant_permissions(permissions, origin=origin)
            else:
                self.context.grant_permissions(permissions)
            self.logger.info(f"Permissions granted: {permissions}")
        except Exception as e:
            self.logger.error(f"Failed to grant permissions: {e}")
            raise
    
    def set_offline(self, offline: bool = True) -> None:
        """
        Set network offline mode
        
        Args:
            offline (bool): Whether to go offline
        """
        try:
            self.context.set_offline(offline)
            status = "offline" if offline else "online"
            self.logger.info(f"Network set to: {status}")
        except Exception as e:
            self.logger.error(f"Failed to set offline mode: {e}")
            raise
    
    def add_init_script(self, script: str) -> None:
        """
        Add initialization script to run on every page
        
        Args:
            script (str): JavaScript code to run
        """
        try:
            self.context.add_init_script(script)
            self.logger.info("Initialization script added")
        except Exception as e:
            self.logger.error(f"Failed to add init script: {e}")
            raise
    
    def expose_function(self, name: str, callback: callable) -> None:
        """
        Expose Python function to page's window object
        
        Args:
            name (str): Function name in window object
            callback (callable): Python function to expose
        """
        try:
            self.page.expose_function(name, callback)
            self.logger.info(f"Function '{name}' exposed to page")
        except Exception as e:
            self.logger.error(f"Failed to expose function '{name}': {e}")
            raise
    
    def add_locator_handler(self, locator_selector: str, handler_func: callable) -> None:
        """
        Add locator handler for persistent elements
        
        Args:
            locator_selector (str): Selector for element to handle
            handler_func (callable): Function to handle the element
        """
        try:
            locator = self.page.locator(locator_selector)
            self.page.add_locator_handler(locator, handler_func)
            self.logger.info(f"Locator handler added for: {locator_selector}")
        except Exception as e:
            self.logger.error(f"Failed to add locator handler: {e}")
            raise
    
    def remove_locator_handler(self, locator_selector: str) -> None:
        """
        Remove locator handler
        
        Args:
            locator_selector (str): Selector for element handler to remove
        """
        try:
            locator = self.page.locator(locator_selector)
            self.page.remove_locator_handler(locator)
            self.logger.info(f"Locator handler removed for: {locator_selector}")
        except Exception as e:
            self.logger.error(f"Failed to remove locator handler: {e}")
            raise
    
    def get_network_requests(self) -> List[Dict[str, Any]]:
        """
        Get all network requests made by the page
        
        Returns:
            List[Dict[str, Any]]: List of request details
        """
        try:
            requests = []
            
            def request_handler(request):
                request_info = {
                    "url": request.url,
                    "method": request.method,
                    "headers": request.headers,
                    "resource_type": request.resource_type
                }
                requests.append(request_info)
            
            self.page.on("request", request_handler)
            self.logger.info("Network request monitoring started")
            return requests
        except Exception as e:
            self.logger.error(f"Failed to monitor network requests: {e}")
            raise
    
    def intercept_requests(self, url_pattern: str, handler_func: callable) -> None:
        """
        Intercept and modify network requests
        
        Args:
            url_pattern (str): URL pattern to intercept
            handler_func (callable): Function to handle intercepted requests
        """
        try:
            self.page.route(url_pattern, handler_func)
            self.logger.info(f"Request interception set up for pattern: {url_pattern}")
        except Exception as e:
            self.logger.error(f"Failed to set up request interception: {e}")
            raise
    
    def unroute_requests(self, url_pattern: str, handler_func: callable = None) -> None:
        """
        Remove request interception
        
        Args:
            url_pattern (str): URL pattern to stop intercepting
            handler_func (callable): Specific handler to remove
        """
        try:
            self.page.unroute(url_pattern, handler_func)
            self.logger.info(f"Request interception removed for pattern: {url_pattern}")
        except Exception as e:
            self.logger.error(f"Failed to remove request interception: {e}")
            raise
    
    def mock_api_response(self, url_pattern: str, response_data: Dict[str, Any], 
                         status_code: int = 200) -> None:
        """
        Mock API response
        
        Args:
            url_pattern (str): URL pattern to mock
            response_data (Dict[str, Any]): Response data to return
            status_code (int): HTTP status code
        """
        try:
            def mock_handler(route, request):
                route.fulfill(
                    status=status_code,
                    content_type="application/json",
                    body=str(response_data)
                )
            
            self.page.route(url_pattern, mock_handler)
            self.logger.info(f"API response mocked for pattern: {url_pattern}")
        except Exception as e:
            self.logger.error(f"Failed to mock API response: {e}")
            raise
    
    def set_extra_http_headers(self, headers: Dict[str, str]) -> None:
        """
        Set extra HTTP headers for all requests
        
        Args:
            headers (Dict[str, str]): Headers to set
        """
        try:
            self.context.set_extra_http_headers(headers)
            self.logger.info(f"Extra HTTP headers set: {list(headers.keys())}")
        except Exception as e:
            self.logger.error(f"Failed to set extra HTTP headers: {e}")
            raise
    
    def add_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """
        Add cookies to browser context
        
        Args:
            cookies (List[Dict[str, Any]]): List of cookie dictionaries
        """
        try:
            self.context.add_cookies(cookies)
            self.logger.info(f"Added {len(cookies)} cookies")
        except Exception as e:
            self.logger.error(f"Failed to add cookies: {e}")
            raise
    
    def get_cookies(self, urls: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get cookies from browser context
        
        Args:
            urls (List[str]): URLs to get cookies for
        
        Returns:
            List[Dict[str, Any]]: List of cookies
        """
        try:
            if urls:
                cookies = self.context.cookies(urls)
            else:
                cookies = self.context.cookies()
            
            self.logger.info(f"Retrieved {len(cookies)} cookies")
            return cookies
        except Exception as e:
            self.logger.error(f"Failed to get cookies: {e}")
            raise
    
    def clear_cookies(self) -> None:
        """Clear all cookies"""
        try:
            self.context.clear_cookies()
            self.logger.info("All cookies cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cookies: {e}")
            raise
    
    def start_tracing(self, trace_path: str = "trace.zip") -> None:
        """
        Start tracing for debugging
        
        Args:
            trace_path (str): Path to save trace file
        """
        try:
            self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
            self.logger.info("Tracing started")
        except Exception as e:
            self.logger.error(f"Failed to start tracing: {e}")
            raise
    
    def stop_tracing(self, trace_path: str = "trace.zip") -> None:
        """
        Stop tracing and save trace file
        
        Args:
            trace_path (str): Path to save trace file
        """
        try:
            self.context.tracing.stop(path=trace_path)
            self.logger.info(f"Tracing stopped and saved to: {trace_path}")
        except Exception as e:
            self.logger.error(f"Failed to stop tracing: {e}")
            raise
    
    def emulate_media(self, media_type: str = None, color_scheme: str = None, 
                     reduced_motion: str = None) -> None:
        """
        Emulate media features
        
        Args:
            media_type (str): Media type (screen, print)
            color_scheme (str): Color scheme (light, dark, no-preference)
            reduced_motion (str): Reduced motion (reduce, no-preference)
        """
        try:
            media_options = {}
            if media_type:
                media_options["media"] = media_type
            if color_scheme:
                media_options["color_scheme"] = color_scheme
            if reduced_motion:
                media_options["reduced_motion"] = reduced_motion
            
            self.page.emulate_media(**media_options)
            self.logger.info(f"Media emulation set: {media_options}")
        except Exception as e:
            self.logger.error(f"Failed to emulate media: {e}")
            raise
    
    def set_viewport_size(self, width: int, height: int) -> None:
        """
        Set viewport size
        
        Args:
            width (int): Viewport width
            height (int): Viewport height
        """
        try:
            self.page.set_viewport_size({"width": width, "height": height})
            self.logger.info(f"Viewport size set to: {width}x{height}")
        except Exception as e:
            self.logger.error(f"Failed to set viewport size: {e}")
            raise
    
    def get_console_messages(self) -> List[str]:
        """
        Get console messages from the page
        
        Returns:
            List[str]: List of console messages
        """
        try:
            messages = []
            
            def console_handler(msg):
                messages.append(f"{msg.type}: {msg.text}")
            
            self.page.on("console", console_handler)
            self.logger.info("Console message monitoring started")
            return messages
        except Exception as e:
            self.logger.error(f"Failed to monitor console messages: {e}")
            raise
    
    def get_page_errors(self) -> List[str]:
        """
        Get JavaScript errors from the page
        
        Returns:
            List[str]: List of error messages
        """
        try:
            errors = []
            
            def error_handler(error):
                errors.append(str(error))
            
            self.page.on("pageerror", error_handler)
            self.logger.info("Page error monitoring started")
            return errors
        except Exception as e:
            self.logger.error(f"Failed to monitor page errors: {e}")
            raise

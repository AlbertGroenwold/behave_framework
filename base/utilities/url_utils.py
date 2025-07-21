import logging
from typing import Dict, List
from urllib.parse import urlparse, parse_qs, urlencode


class UrlUtils:
    """Utility class for URL operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse URL into components
        
        Args:
            url (str): URL to parse
        
        Returns:
            Dict[str, str]: URL components
        """
        try:
            parsed = urlparse(url)
            components = {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'params': parsed.params,
                'query': parsed.query,
                'fragment': parsed.fragment
            }
            self.logger.info(f"Parsed URL: {url}")
            return components
        
        except Exception as e:
            self.logger.error(f"Error parsing URL {url}: {e}")
            raise
    
    def get_query_parameters(self, url: str) -> Dict[str, List[str]]:
        """
        Extract query parameters from URL
        
        Args:
            url (str): URL to extract parameters from
        
        Returns:
            Dict[str, List[str]]: Query parameters
        """
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            self.logger.info(f"Extracted query parameters from URL")
            return params
        
        except Exception as e:
            self.logger.error(f"Error extracting query parameters: {e}")
            raise
    
    def build_url_with_params(self, base_url: str, params: Dict[str, str]) -> str:
        """
        Build URL with query parameters
        
        Args:
            base_url (str): Base URL
            params (Dict[str, str]): Query parameters
        
        Returns:
            str: URL with parameters
        """
        try:
            query_string = urlencode(params)
            separator = '&' if '?' in base_url else '?'
            full_url = f"{base_url}{separator}{query_string}"
            self.logger.info(f"Built URL with parameters")
            return full_url
        
        except Exception as e:
            self.logger.error(f"Error building URL with parameters: {e}")
            raise

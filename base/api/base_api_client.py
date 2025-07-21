"""Base API client for automation testing"""

import requests
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin


class BaseAPIClient:
    """Base API client for handling HTTP requests and responses"""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def set_auth_token(self, token: str, auth_type: str = 'Bearer'):
        """Set authentication token"""
        self.session.headers['Authorization'] = f'{auth_type} {token}'
        self.logger.info(f"Authentication token set: {auth_type}")
    
    def set_api_key(self, api_key: str, header_name: str = 'X-API-Key'):
        """Set API key in headers"""
        self.session.headers[header_name] = api_key
        self.logger.info(f"API key set in header: {header_name}")
    
    def set_basic_auth(self, username: str, password: str):
        """Set basic authentication"""
        self.session.auth = (username, password)
        self.logger.info("Basic authentication set")
    
    def add_header(self, key: str, value: str):
        """Add custom header"""
        self.session.headers[key] = value
        self.logger.info(f"Header added: {key}")
    
    def remove_header(self, key: str):
        """Remove header"""
        self.session.headers.pop(key, None)
        self.logger.info(f"Header removed: {key}")
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def _log_request(self, method: str, url: str, **kwargs):
        """Log request details"""
        self.logger.info(f"API Request: {method.upper()} {url}")
        if 'params' in kwargs:
            self.logger.debug(f"Query params: {kwargs['params']}")
        if 'json' in kwargs:
            self.logger.debug(f"JSON payload: {kwargs['json']}")
        elif 'data' in kwargs:
            self.logger.debug(f"Data payload: {kwargs['data']}")
    
    def _log_response(self, response: requests.Response):
        """Log response details"""
        self.logger.info(f"API Response: {response.status_code} {response.reason}")
        self.logger.debug(f"Response headers: {dict(response.headers)}")
        
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                self.logger.debug(f"Response body: {response.json()}")
            else:
                self.logger.debug(f"Response body: {response.text[:500]}...")
        except:
            pass
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Send GET request"""
        url = self._build_url(endpoint)
        self._log_request('GET', url, params=params, **kwargs)
        
        response = self.session.get(
            url, 
            params=params, 
            timeout=self.timeout, 
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def post(self, endpoint: str, json_data: Optional[Dict] = None, 
             data: Optional[Union[Dict, str]] = None, **kwargs) -> requests.Response:
        """Send POST request"""
        url = self._build_url(endpoint)
        self._log_request('POST', url, json=json_data, data=data, **kwargs)
        
        response = self.session.post(
            url, 
            json=json_data, 
            data=data, 
            timeout=self.timeout, 
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def put(self, endpoint: str, json_data: Optional[Dict] = None, 
            data: Optional[Union[Dict, str]] = None, **kwargs) -> requests.Response:
        """Send PUT request"""
        url = self._build_url(endpoint)
        self._log_request('PUT', url, json=json_data, data=data, **kwargs)
        
        response = self.session.put(
            url, 
            json=json_data, 
            data=data, 
            timeout=self.timeout, 
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def patch(self, endpoint: str, json_data: Optional[Dict] = None, 
              data: Optional[Union[Dict, str]] = None, **kwargs) -> requests.Response:
        """Send PATCH request"""
        url = self._build_url(endpoint)
        self._log_request('PATCH', url, json=json_data, data=data, **kwargs)
        
        response = self.session.patch(
            url, 
            json=json_data, 
            data=data, 
            timeout=self.timeout, 
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Send DELETE request"""
        url = self._build_url(endpoint)
        self._log_request('DELETE', url, **kwargs)
        
        response = self.session.delete(
            url, 
            timeout=self.timeout, 
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def head(self, endpoint: str, **kwargs) -> requests.Response:
        """Send HEAD request"""
        url = self._build_url(endpoint)
        self._log_request('HEAD', url, **kwargs)
        
        response = self.session.head(
            url, 
            timeout=self.timeout, 
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def options(self, endpoint: str, **kwargs) -> requests.Response:
        """Send OPTIONS request"""
        url = self._build_url(endpoint)
        self._log_request('OPTIONS', url, **kwargs)
        
        response = self.session.options(
            url, 
            timeout=self.timeout, 
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def upload_file(self, endpoint: str, file_path: str, 
                   file_field: str = 'file', **kwargs) -> requests.Response:
        """Upload file"""
        url = self._build_url(endpoint)
        
        with open(file_path, 'rb') as file:
            files = {file_field: file}
            self._log_request('POST', url, **kwargs)
            
            response = self.session.post(
                url, 
                files=files, 
                timeout=self.timeout, 
                **kwargs
            )
        
        self._log_response(response)
        return response
    
    def download_file(self, endpoint: str, save_path: str, **kwargs) -> bool:
        """Download file"""
        url = self._build_url(endpoint)
        self._log_request('GET', url, **kwargs)
        
        response = self.session.get(
            url, 
            stream=True, 
            timeout=self.timeout, 
            **kwargs
        )
        
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            self.logger.info(f"File downloaded: {save_path}")
            return True
        else:
            self.logger.error(f"Failed to download file: {response.status_code}")
            return False
    
    def close(self):
        """Close the session"""
        self.session.close()
        self.logger.info("API client session closed")

"""Base API client for automation testing"""

import requests
import logging
import time
import random
import threading
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urljoin
from queue import Queue, Empty
from contextlib import contextmanager
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
from ..utilities.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, create_circuit_breaker,
    CircuitBreakerError, CircuitBreakerState
)
from ..utilities.error_handler import (
    ApiError, ConnectionError, TimeoutError, ErrorCategory,
    retry_on_error, error_context
)
from ..utilities.recovery_strategies import (
    HealthChecker, HealthCheckResult, HealthStatus,
    auto_recovery_manager
)


class ConnectionPoolAdapter(HTTPAdapter):
    """Custom HTTP adapter with connection pooling configuration."""
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20, 
                 max_retries: int = 3, pool_block: bool = False, **kwargs):
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.pool_block = pool_block
        super().__init__(max_retries=max_retries, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        """Initialize pool manager with custom settings."""
        kwargs['maxsize'] = self.pool_maxsize
        kwargs['block'] = self.pool_block
        return super().init_poolmanager(*args, **kwargs)


class ConnectionPoolStats:
    """Track connection pool usage statistics."""
    
    def __init__(self):
        self.pool_size = 0
        self.active_connections = 0
        self.total_connections_created = 0
        self.connections_reused = 0
        self.pool_hits = 0
        self.pool_misses = 0
        self.warmup_connections = 0
        self._lock = threading.Lock()
    
    def update_stats(self, reused: bool, pool_hit: bool):
        """Update connection statistics."""
        with self._lock:
            if reused:
                self.connections_reused += 1
            else:
                self.total_connections_created += 1
            
            if pool_hit:
                self.pool_hits += 1
            else:
                self.pool_misses += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current connection pool statistics."""
        with self._lock:
            total_requests = self.pool_hits + self.pool_misses
            hit_rate = (self.pool_hits / total_requests * 100) if total_requests > 0 else 0
            reuse_rate = (self.connections_reused / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'pool_size': self.pool_size,
                'active_connections': self.active_connections,
                'total_connections_created': self.total_connections_created,
                'connections_reused': self.connections_reused,
                'pool_hits': self.pool_hits,
                'pool_misses': self.pool_misses,
                'hit_rate_percent': round(hit_rate, 2),
                'reuse_rate_percent': round(reuse_rate, 2),
                'warmup_connections': self.warmup_connections
            }


class RateLimitQueue:
    """Request queue for rate limiting."""
    
    def __init__(self, max_requests_per_second: float = 10.0):
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0
        self._lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()


class APIHealthChecker(HealthChecker):
    """Health checker specifically for API clients."""
    
    def __init__(self, name: str, api_client: 'BaseAPIClient', health_endpoint: str = "/health"):
        super().__init__(name)
        self.api_client = api_client
        self.health_endpoint = health_endpoint
    
    def check_health(self) -> HealthCheckResult:
        """Check API health."""
        try:
            # Use a simple GET request to health endpoint
            response = self.api_client.session.get(
                self.api_client._build_url(self.health_endpoint),
                timeout=5.0
            )
            
            if response.status_code == 200:
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="API endpoint healthy",
                    details={"status_code": response.status_code}
                )
            elif 500 <= response.status_code < 600:
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"API returning server error: {response.status_code}",
                    details={"status_code": response.status_code}
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    message=f"API returning unexpected status: {response.status_code}",
                    details={"status_code": response.status_code}
                )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"API health check failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )


class BaseAPIClient:
    """Enhanced Base API client with circuit breaker, retry logic, and health monitoring"""
    
    def __init__(self, base_url: str = "", timeout: int = 30, 
                 enable_circuit_breaker: bool = True,
                 circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
                 rate_limit_per_second: float = 10.0,
                 enable_health_monitoring: bool = True,
                 pool_connections: int = 10,
                 pool_maxsize: int = 20,
                 pool_block: bool = False,
                 enable_connection_warmup: bool = True):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Connection pool configuration
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.pool_block = pool_block
        self.enable_connection_warmup = enable_connection_warmup
        
        # Create session with connection pooling
        self.session = requests.Session()
        self._configure_connection_pool()
        
        # Connection pool statistics
        self.pool_stats = ConnectionPoolStats()
        self.pool_stats.pool_size = pool_maxsize
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Circuit breaker setup
        self.enable_circuit_breaker = enable_circuit_breaker
        if enable_circuit_breaker:
            cb_config = circuit_breaker_config or CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                expected_exception=(requests.exceptions.RequestException, ApiError),
                timeout=timeout
            )
            self.circuit_breaker = create_circuit_breaker(
                f"api_client_{base_url.replace('://', '_').replace('/', '_')}", 
                cb_config
            )
        else:
            self.circuit_breaker = None
        
        # Rate limiting
        self.rate_limiter = RateLimitQueue(rate_limit_per_second)
        
        # Health monitoring
        self.enable_health_monitoring = enable_health_monitoring
        if enable_health_monitoring:
            self.health_checker = APIHealthChecker(
                f"api_{base_url.replace('://', '_').replace('/', '_')}", 
                self
            )
            auto_recovery_manager.register_health_checker(
                self.health_checker.name, 
                self.health_checker
            )
        else:
            self.health_checker = None
        
        # Connection statistics
        self.connection_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'circuit_breaker_openings': 0,
            'retry_attempts': 0,
            'average_response_time': 0.0,
            'last_request_time': None
        }
        self._stats_lock = threading.Lock()
        
        # Default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Warm up connections if enabled
        if self.enable_connection_warmup and self.base_url:
            self._warmup_connections()
    
    def _configure_connection_pool(self):
        """Configure connection pool for the session."""
        # Create custom adapter with connection pooling
        adapter = ConnectionPoolAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            pool_block=self.pool_block,
            max_retries=3
        )
        
        # Mount adapter for both HTTP and HTTPS
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.logger.info(f"Connection pool configured: {self.pool_connections} connections, {self.pool_maxsize} max size")
    
    def _warmup_connections(self):
        """Warm up connection pool by making initial requests."""
        if not self.base_url:
            return
        
        warmup_count = min(3, self.pool_connections)  # Warm up a few connections
        
        def warmup_request():
            try:
                # Make a simple HEAD request to warm up connection
                response = self.session.head(self.base_url, timeout=5)
                with self.pool_stats._lock:
                    self.pool_stats.warmup_connections += 1
                self.logger.debug(f"Connection warmed up: {response.status_code}")
            except Exception as e:
                self.logger.debug(f"Connection warmup failed: {e}")
        
        # Warm up connections in parallel
        threads = []
        for _ in range(warmup_count):
            thread = threading.Thread(target=warmup_request)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for warmup to complete (with timeout)
        for thread in threads:
            thread.join(timeout=5)
        
        self.logger.info(f"Connection pool warmup completed: {warmup_count} connections")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return self.pool_stats.get_stats()
    
    def configure_pool_settings(self, pool_connections: int = None, 
                              pool_maxsize: int = None, pool_block: bool = None):
        """Reconfigure connection pool settings."""
        if pool_connections is not None:
            self.pool_connections = pool_connections
        if pool_maxsize is not None:
            self.pool_maxsize = pool_maxsize
            self.pool_stats.pool_size = pool_maxsize
        if pool_block is not None:
            self.pool_block = pool_block
        
        # Reconfigure the connection pool
        self._configure_connection_pool()
        self.logger.info("Connection pool settings updated")
    
    def _update_connection_stats(self, success: bool, response_time: float, retries: int = 0):
        """Update connection statistics."""
        with self._stats_lock:
            self.connection_stats['total_requests'] += 1
            self.connection_stats['last_request_time'] = time.time()
            
            if retries > 0:
                self.connection_stats['retry_attempts'] += retries
            
            if success:
                self.connection_stats['successful_requests'] += 1
            else:
                self.connection_stats['failed_requests'] += 1
            
            # Update average response time (exponential moving average)
            current_avg = self.connection_stats['average_response_time']
            if current_avg == 0.0:
                self.connection_stats['average_response_time'] = response_time
            else:
                # Use alpha = 0.1 for exponential moving average
                self.connection_stats['average_response_time'] = (0.1 * response_time) + (0.9 * current_avg)
    
    def _add_jitter_to_retry(self, base_delay: float) -> float:
        """Add jitter to retry delay to prevent thundering herd."""
        jitter = random.uniform(0.1, 0.5) * base_delay
        return base_delay + jitter
    
    def _handle_timeout_with_custom_exception(self, timeout_duration: float):
        """Handle timeout with custom exception."""
        raise TimeoutError(
            f"Request timed out after {timeout_duration} seconds",
            timeout_duration=timeout_duration
        )
    
    def _categorize_http_error(self, response: requests.Response) -> ErrorCategory:
        """Categorize HTTP errors as transient or permanent."""
        status_code = response.status_code
        
        # Transient errors (should retry)
        if status_code in [408, 429, 500, 502, 503, 504]:
            return ErrorCategory.TRANSIENT
        
        # Permanent errors (should not retry)
        if status_code in [400, 401, 403, 404, 405, 422]:
            return ErrorCategory.PERMANENT
        
        # Other 4xx errors are generally permanent
        if 400 <= status_code < 500:
            return ErrorCategory.PERMANENT
        
        # Other 5xx errors are generally transient
        if 500 <= status_code < 600:
            return ErrorCategory.TRANSIENT
        
        return ErrorCategory.UNKNOWN
    
    @retry_on_error(max_attempts=3, base_delay=1.0, backoff_factor=2.0, jitter=True)
    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic and jitter."""
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        start_time = time.time()
        
        try:
            # Make the actual request
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response_time = time.time() - start_time
            
            # Check for HTTP errors
            if not response.ok:
                error_category = self._categorize_http_error(response)
                api_error = ApiError(
                    f"HTTP {response.status_code}: {response.reason}",
                    status_code=response.status_code,
                    response_body=response.text[:500] if response.text else None,
                    category=error_category
                )
                
                self._update_connection_stats(False, response_time)
                raise api_error
            
            self._update_connection_stats(True, response_time)
            return response
            
        except requests.exceptions.Timeout as e:
            response_time = time.time() - start_time
            self._update_connection_stats(False, response_time)
            self._handle_timeout_with_custom_exception(self.timeout)
            
        except requests.exceptions.ConnectionError as e:
            response_time = time.time() - start_time
            self._update_connection_stats(False, response_time)
            raise ConnectionError(
                f"Connection failed: {str(e)}",
                host=self.base_url
            )
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self._update_connection_stats(False, response_time)
            raise ApiError(
                f"Request failed: {str(e)}",
                category=ErrorCategory.TRANSIENT,
                original_error=e
            )
    
    def _make_request_with_circuit_breaker(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make request with circuit breaker protection."""
        if self.enable_circuit_breaker and self.circuit_breaker:
            try:
                return self.circuit_breaker.call(self._make_request_with_retry, method, url, **kwargs)
            except CircuitBreakerError as e:
                # Circuit breaker is open
                with self._stats_lock:
                    self.connection_stats['circuit_breaker_openings'] += 1
                
                self.logger.warning(f"Circuit breaker open for {self.base_url}: {e}")
                raise ApiError(
                    f"Service temporarily unavailable (circuit breaker open): {str(e)}",
                    category=ErrorCategory.TRANSIENT,
                    original_error=e
                )
        else:
            return self._make_request_with_retry(method, url, **kwargs)
    
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
        """Send GET request with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"GET {url}", additional_context={'endpoint': endpoint, 'params': params}):
            self._log_request('GET', url, params=params, **kwargs)
            response = self._make_request_with_circuit_breaker('GET', url, params=params, **kwargs)
            self._log_response(response)
            return response
    
    def post(self, endpoint: str, json_data: Optional[Dict] = None, 
             data: Optional[Union[Dict, str]] = None, **kwargs) -> requests.Response:
        """Send POST request with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"POST {url}", additional_context={'endpoint': endpoint}):
            self._log_request('POST', url, json=json_data, data=data, **kwargs)
            response = self._make_request_with_circuit_breaker('POST', url, json=json_data, data=data, **kwargs)
            self._log_response(response)
            return response
    
    def put(self, endpoint: str, json_data: Optional[Dict] = None, 
            data: Optional[Union[Dict, str]] = None, **kwargs) -> requests.Response:
        """Send PUT request with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"PUT {url}", additional_context={'endpoint': endpoint}):
            self._log_request('PUT', url, json=json_data, data=data, **kwargs)
            response = self._make_request_with_circuit_breaker('PUT', url, json=json_data, data=data, **kwargs)
            self._log_response(response)
            return response
    
    def patch(self, endpoint: str, json_data: Optional[Dict] = None, 
              data: Optional[Union[Dict, str]] = None, **kwargs) -> requests.Response:
        """Send PATCH request with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"PATCH {url}", additional_context={'endpoint': endpoint}):
            self._log_request('PATCH', url, json=json_data, data=data, **kwargs)
            response = self._make_request_with_circuit_breaker('PATCH', url, json=json_data, data=data, **kwargs)
            self._log_response(response)
            return response
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Send DELETE request with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"DELETE {url}", additional_context={'endpoint': endpoint}):
            self._log_request('DELETE', url, **kwargs)
            response = self._make_request_with_circuit_breaker('DELETE', url, **kwargs)
            self._log_response(response)
            return response
    
    def head(self, endpoint: str, **kwargs) -> requests.Response:
        """Send HEAD request with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"HEAD {url}", additional_context={'endpoint': endpoint}):
            self._log_request('HEAD', url, **kwargs)
            response = self._make_request_with_circuit_breaker('HEAD', url, **kwargs)
            self._log_response(response)
            return response
    
    def options(self, endpoint: str, **kwargs) -> requests.Response:
        """Send OPTIONS request with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"OPTIONS {url}", additional_context={'endpoint': endpoint}):
            self._log_request('OPTIONS', url, **kwargs)
            response = self._make_request_with_circuit_breaker('OPTIONS', url, **kwargs)
            self._log_response(response)
            return response
    
    def upload_file(self, endpoint: str, file_path: str, 
                   file_field: str = 'file', **kwargs) -> requests.Response:
        """Upload file with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"UPLOAD {url}", additional_context={'endpoint': endpoint, 'file_path': file_path}):
            with open(file_path, 'rb') as file:
                files = {file_field: file}
                self._log_request('POST', url, **kwargs)
                
                # Note: For file uploads, we bypass the normal JSON handling
                kwargs_copy = kwargs.copy()
                kwargs_copy.pop('json', None)  # Remove json if present
                response = self._make_request_with_circuit_breaker('POST', url, files=files, **kwargs_copy)
            
            self._log_response(response)
            return response
    
    def download_file(self, endpoint: str, save_path: str, **kwargs) -> bool:
        """Download file with enhanced error handling"""
        url = self._build_url(endpoint)
        
        with error_context(f"DOWNLOAD {url}", additional_context={'endpoint': endpoint, 'save_path': save_path}):
            self._log_request('GET', url, **kwargs)
            
            kwargs_copy = kwargs.copy()
            kwargs_copy['stream'] = True
            response = self._make_request_with_circuit_breaker('GET', url, **kwargs_copy)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                
                self.logger.info(f"File downloaded: {save_path}")
                return True
            else:
                self.logger.error(f"Failed to download file: {response.status_code}")
                return False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        with self._stats_lock:
            stats = self.connection_stats.copy()
        
        # Add circuit breaker stats if available
        if self.circuit_breaker:
            cb_metrics = self.circuit_breaker.get_metrics()
            stats['circuit_breaker'] = cb_metrics
        
        # Add connection pool stats
        stats['connection_pool'] = self.get_pool_stats()
        
        return stats
    
    def get_health_status(self) -> Optional[HealthCheckResult]:
        """Get current health status."""
        if self.health_checker:
            return self.health_checker.check_health()
        return None
    
    def reset_circuit_breaker(self):
        """Reset the circuit breaker to closed state."""
        if self.circuit_breaker:
            self.circuit_breaker.reset()
            self.logger.info("Circuit breaker reset")
    
    def configure_rate_limit(self, requests_per_second: float):
        """Configure rate limiting."""
        self.rate_limiter = RateLimitQueue(requests_per_second)
        self.logger.info(f"Rate limit configured: {requests_per_second} requests/second")
    
    def is_healthy(self) -> bool:
        """Check if the API client is healthy."""
        if self.circuit_breaker:
            cb_state = self.circuit_breaker.get_state()
            if cb_state != CircuitBreakerState.CLOSED:
                return False
        
        if self.health_checker:
            health_result = self.health_checker.check_health()
            return health_result.is_healthy()
        
        return True
    
    def close(self):
        """Close the session"""
        self.session.close()
        self.logger.info("API client session closed")

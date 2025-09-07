"""
Recovery Strategies Module

This module provides automatic recovery mechanisms for common transient failures,
fallback mechanisms for critical operations, recovery hooks for base classes,
health check mechanisms, and graceful degradation patterns.
"""

import time
import threading
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Union, Type
from enum import Enum
from contextlib import contextmanager
from .error_handler import ErrorCategory, ErrorCategorizer, TransientError, PermanentError


class RecoveryStrategy(Enum):
    """Available recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    HEALTH_CHECK = "health_check"


class HealthStatus(Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Result of a health check operation."""
    
    def __init__(self, status: HealthStatus, message: str = "", 
                 details: Optional[Dict[str, Any]] = None, check_time: Optional[float] = None):
        self.status = status
        self.message = message
        self.details = details or {}
        self.check_time = check_time or time.time()
        self.response_time_ms = None
    
    def is_healthy(self) -> bool:
        """Check if the status indicates healthy state."""
        return self.status == HealthStatus.HEALTHY
    
    def is_degraded(self) -> bool:
        """Check if the status indicates degraded state."""
        return self.status == HealthStatus.DEGRADED
    
    def is_unhealthy(self) -> bool:
        """Check if the status indicates unhealthy state."""
        return self.status == HealthStatus.UNHEALTHY


class HealthChecker(ABC):
    """Abstract base class for health checkers."""
    
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
    
    @abstractmethod
    def check_health(self) -> HealthCheckResult:
        """Perform health check and return result."""
        pass
    
    def check_health_with_timeout(self) -> HealthCheckResult:
        """Perform health check with timeout."""
        start_time = time.time()
        try:
            result = self.check_health()
            end_time = time.time()
            result.response_time_ms = (end_time - start_time) * 1000
            return result
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            self.logger.error(f"Health check failed for {self.name}: {e}")
            result = HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )
            result.response_time_ms = response_time
            return result


class DatabaseHealthChecker(HealthChecker):
    """Health checker for database connections."""
    
    def __init__(self, name: str, database_manager, timeout: float = 5.0):
        super().__init__(name, timeout)
        self.database_manager = database_manager
    
    def check_health(self) -> HealthCheckResult:
        """Check database health."""
        try:
            if not self.database_manager.is_connected():
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="Database not connected"
                )
            
            # Try a simple query
            result = self.database_manager.execute_query("SELECT 1")
            if result:
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="Database connection healthy"
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    message="Database query returned no result"
                )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Database health check failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )


class APIHealthChecker(HealthChecker):
    """Health checker for API endpoints."""
    
    def __init__(self, name: str, api_client, health_endpoint: str = "/health", timeout: float = 5.0):
        super().__init__(name, timeout)
        self.api_client = api_client
        self.health_endpoint = health_endpoint
    
    def check_health(self) -> HealthCheckResult:
        """Check API health."""
        try:
            response = self.api_client.get(self.health_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="API endpoint healthy",
                    details={"status_code": response.status_code}
                )
            elif 500 <= response.status_code < 600:
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"API endpoint returning server error: {response.status_code}",
                    details={"status_code": response.status_code}
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    message=f"API endpoint returning unexpected status: {response.status_code}",
                    details={"status_code": response.status_code}
                )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"API health check failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )


class WebDriverHealthChecker(HealthChecker):
    """Health checker for WebDriver instances."""
    
    def __init__(self, name: str, driver, timeout: float = 5.0):
        super().__init__(name, timeout)
        self.driver = driver
    
    def check_health(self) -> HealthCheckResult:
        """Check WebDriver health."""
        try:
            # Try to get current URL to test if driver is responsive
            current_url = self.driver.current_url
            
            # Check if driver is still alive by executing a simple script
            result = self.driver.execute_script("return document.readyState;")
            
            if result:
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="WebDriver responsive",
                    details={"current_url": current_url, "ready_state": result}
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    message="WebDriver partially responsive"
                )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"WebDriver health check failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )


class FallbackMechanism:
    """Implements fallback mechanisms for critical operations."""
    
    def __init__(self, name: str):
        self.name = name
        self.primary_function = None
        self.fallback_functions = []
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
    
    def set_primary(self, func: Callable) -> 'FallbackMechanism':
        """Set the primary function to execute."""
        self.primary_function = func
        return self
    
    def add_fallback(self, func: Callable) -> 'FallbackMechanism':
        """Add a fallback function."""
        self.fallback_functions.append(func)
        return self
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute with fallback logic."""
        if not self.primary_function:
            raise ValueError("No primary function defined")
        
        # Try primary function first
        try:
            self.logger.debug(f"Executing primary function for {self.name}")
            return self.primary_function(*args, **kwargs)
        except Exception as primary_error:
            self.logger.warning(f"Primary function failed for {self.name}: {primary_error}")
            
            # Try fallback functions
            for i, fallback_func in enumerate(self.fallback_functions):
                try:
                    self.logger.info(f"Trying fallback {i+1} for {self.name}")
                    return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    self.logger.warning(f"Fallback {i+1} failed for {self.name}: {fallback_error}")
                    continue
            
            # If all fallbacks failed, raise the original error
            self.logger.error(f"All fallbacks failed for {self.name}")
            raise primary_error


class AutoRecoveryManager:
    """Manages automatic recovery for common transient failures."""
    
    def __init__(self):
        self.recovery_strategies = {}
        self.health_checkers = {}
        self.fallback_mechanisms = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._lock = threading.Lock()
        self.recovery_stats = {
            'total_recoveries': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'recovery_by_type': {}
        }
    
    def register_health_checker(self, name: str, checker: HealthChecker):
        """Register a health checker."""
        with self._lock:
            self.health_checkers[name] = checker
            self.logger.info(f"Registered health checker: {name}")
    
    def register_fallback_mechanism(self, name: str, mechanism: FallbackMechanism):
        """Register a fallback mechanism."""
        with self._lock:
            self.fallback_mechanisms[name] = mechanism
            self.logger.info(f"Registered fallback mechanism: {name}")
    
    def check_component_health(self, component_name: str) -> HealthCheckResult:
        """Check health of a specific component."""
        if component_name not in self.health_checkers:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                message=f"No health checker registered for {component_name}"
            )
        
        checker = self.health_checkers[component_name]
        return checker.check_health_with_timeout()
    
    def check_all_health(self) -> Dict[str, HealthCheckResult]:
        """Check health of all registered components."""
        results = {}
        for name, checker in self.health_checkers.items():
            results[name] = checker.check_health_with_timeout()
        return results
    
    def attempt_recovery(self, component_name: str, error: Exception) -> bool:
        """Attempt to recover from an error."""
        self.recovery_stats['total_recoveries'] += 1
        error_type = type(error).__name__
        
        if error_type not in self.recovery_stats['recovery_by_type']:
            self.recovery_stats['recovery_by_type'][error_type] = 0
        self.recovery_stats['recovery_by_type'][error_type] += 1
        
        self.logger.info(f"Attempting recovery for {component_name} after {error_type}")
        
        try:
            # Check if we have a specific recovery strategy for this component
            if component_name in self.recovery_strategies:
                strategy = self.recovery_strategies[component_name]
                success = strategy(error)
                if success:
                    self.recovery_stats['successful_recoveries'] += 1
                    self.logger.info(f"Recovery successful for {component_name}")
                    return True
            
            # Try generic recovery based on error category
            category = ErrorCategorizer.categorize_error(error)
            if category == ErrorCategory.TRANSIENT:
                success = self._generic_transient_recovery(component_name, error)
                if success:
                    self.recovery_stats['successful_recoveries'] += 1
                    self.logger.info(f"Generic recovery successful for {component_name}")
                    return True
            
            self.recovery_stats['failed_recoveries'] += 1
            self.logger.warning(f"Recovery failed for {component_name}")
            return False
            
        except Exception as recovery_error:
            self.recovery_stats['failed_recoveries'] += 1
            self.logger.error(f"Recovery attempt failed for {component_name}: {recovery_error}")
            return False
    
    def _generic_transient_recovery(self, component_name: str, error: Exception) -> bool:
        """Generic recovery for transient errors."""
        self.logger.debug(f"Attempting generic transient recovery for {component_name}")
        
        # Wait a bit before retrying
        time.sleep(1)
        
        # Check health after waiting
        health_result = self.check_component_health(component_name)
        return health_result.is_healthy()
    
    def register_recovery_strategy(self, component_name: str, strategy: Callable[[Exception], bool]):
        """Register a custom recovery strategy for a component."""
        with self._lock:
            self.recovery_strategies[component_name] = strategy
            self.logger.info(f"Registered recovery strategy for {component_name}")
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        return self.recovery_stats.copy()


class GracefulDegradationManager:
    """Manages graceful degradation patterns."""
    
    def __init__(self):
        self.degradation_modes = {}
        self.current_mode = "normal"
        self.logger = logging.getLogger(self.__class__.__name__)
        self._lock = threading.Lock()
    
    def register_degradation_mode(self, mode_name: str, 
                                  condition_checker: Callable[[], bool],
                                  degraded_behavior: Callable[[], Any]):
        """Register a degradation mode."""
        with self._lock:
            self.degradation_modes[mode_name] = {
                'condition': condition_checker,
                'behavior': degraded_behavior
            }
            self.logger.info(f"Registered degradation mode: {mode_name}")
    
    def check_degradation_conditions(self) -> Optional[str]:
        """Check if any degradation conditions are met."""
        for mode_name, mode_config in self.degradation_modes.items():
            try:
                if mode_config['condition']():
                    return mode_name
            except Exception as e:
                self.logger.warning(f"Error checking degradation condition for {mode_name}: {e}")
        return None
    
    def activate_degradation_mode(self, mode_name: str):
        """Activate a specific degradation mode."""
        if mode_name not in self.degradation_modes:
            raise ValueError(f"Unknown degradation mode: {mode_name}")
        
        with self._lock:
            self.current_mode = mode_name
            self.logger.warning(f"Activated degradation mode: {mode_name}")
    
    def deactivate_degradation_mode(self):
        """Deactivate degradation mode and return to normal."""
        with self._lock:
            if self.current_mode != "normal":
                previous_mode = self.current_mode
                self.current_mode = "normal"
                self.logger.info(f"Deactivated degradation mode: {previous_mode}")
    
    def is_degraded(self) -> bool:
        """Check if currently in degraded mode."""
        return self.current_mode != "normal"
    
    def get_current_mode(self) -> str:
        """Get current degradation mode."""
        return self.current_mode
    
    def execute_with_degradation(self, normal_behavior: Callable[[], Any],
                                 fallback_behavior: Optional[Callable[[], Any]] = None) -> Any:
        """Execute behavior with degradation support."""
        # Check if we should enter degradation mode
        degradation_mode = self.check_degradation_conditions()
        if degradation_mode:
            self.activate_degradation_mode(degradation_mode)
        
        # Execute appropriate behavior
        if self.is_degraded():
            if degradation_mode and degradation_mode in self.degradation_modes:
                self.logger.info(f"Executing degraded behavior for mode: {degradation_mode}")
                return self.degradation_modes[degradation_mode]['behavior']()
            elif fallback_behavior:
                self.logger.info("Executing fallback behavior")
                return fallback_behavior()
            else:
                self.logger.warning("No degraded behavior available, attempting normal execution")
                return normal_behavior()
        else:
            return normal_behavior()


class RecoveryHook:
    """Recovery hook that can be added to base classes."""
    
    def __init__(self, name: str, recovery_manager: AutoRecoveryManager):
        self.name = name
        self.recovery_manager = recovery_manager
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator that adds recovery capabilities to methods."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                self.logger.warning(f"Error in {func.__name__}: {error}")
                
                # Attempt recovery
                recovery_successful = self.recovery_manager.attempt_recovery(self.name, error)
                
                if recovery_successful:
                    self.logger.info(f"Recovery successful, retrying {func.__name__}")
                    # Retry the operation once after recovery
                    try:
                        return func(*args, **kwargs)
                    except Exception as retry_error:
                        self.logger.error(f"Operation failed even after recovery: {retry_error}")
                        raise retry_error
                else:
                    # Recovery failed, re-raise original error
                    raise error
        
        return wrapper


@contextmanager
def recovery_context(component_name: str, recovery_manager: AutoRecoveryManager,
                     max_recovery_attempts: int = 1):
    """Context manager for automatic recovery."""
    attempts = 0
    while attempts <= max_recovery_attempts:
        try:
            yield
            break  # Success, exit the loop
        except Exception as error:
            attempts += 1
            if attempts <= max_recovery_attempts:
                recovery_successful = recovery_manager.attempt_recovery(component_name, error)
                if not recovery_successful:
                    raise error  # Recovery failed, give up
                # Continue the loop to retry
            else:
                raise error  # Max attempts reached


# Global instances
auto_recovery_manager = AutoRecoveryManager()
graceful_degradation_manager = GracefulDegradationManager()


def create_recovery_hook(component_name: str) -> RecoveryHook:
    """Create a recovery hook for a component."""
    return RecoveryHook(component_name, auto_recovery_manager)


def register_database_health_checker(name: str, database_manager, timeout: float = 5.0):
    """Register a database health checker."""
    checker = DatabaseHealthChecker(name, database_manager, timeout)
    auto_recovery_manager.register_health_checker(name, checker)


def register_api_health_checker(name: str, api_client, health_endpoint: str = "/health", timeout: float = 5.0):
    """Register an API health checker."""
    checker = APIHealthChecker(name, api_client, health_endpoint, timeout)
    auto_recovery_manager.register_health_checker(name, checker)


def register_webdriver_health_checker(name: str, driver, timeout: float = 5.0):
    """Register a WebDriver health checker."""
    checker = WebDriverHealthChecker(name, driver, timeout)
    auto_recovery_manager.register_health_checker(name, checker)


def create_fallback_mechanism(name: str) -> FallbackMechanism:
    """Create and register a fallback mechanism."""
    mechanism = FallbackMechanism(name)
    auto_recovery_manager.register_fallback_mechanism(name, mechanism)
    return mechanism

"""
Circuit Breaker Pattern Implementation

This module provides a circuit breaker pattern implementation for preventing
cascade failures and improving system resilience by temporarily failing fast
when a service is detected to be failing.
"""

import time
import threading
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict, Type
from dataclasses import dataclass
from contextlib import contextmanager
import functools


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast, not calling service
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: float = 60.0      # Seconds before attempting recovery
    expected_exception: Type[Exception] = Exception  # Exception types to count as failures
    timeout: float = 30.0               # Operation timeout in seconds
    half_open_max_calls: int = 3        # Max calls allowed in half-open state


class CircuitBreakerMetrics:
    """Metrics tracking for circuit breaker."""
    
    def __init__(self):
        self.failure_count = 0
        self.success_count = 0
        self.total_calls = 0
        self.last_failure_time = None
        self.state_change_count = 0
        self.open_duration = 0.0
        self.half_open_calls = 0
        self._lock = threading.Lock()
    
    def record_success(self):
        """Record a successful call."""
        with self._lock:
            self.success_count += 1
            self.total_calls += 1
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call."""
        with self._lock:
            self.failure_count += 1
            self.total_calls += 1
            self.last_failure_time = time.time()
    
    def record_state_change(self):
        """Record a state change."""
        with self._lock:
            self.state_change_count += 1
    
    def record_half_open_call(self):
        """Record a call in half-open state."""
        with self._lock:
            self.half_open_calls += 1
    
    def reset_half_open_calls(self):
        """Reset half-open call counter."""
        with self._lock:
            self.half_open_calls = 0
    
    def get_failure_rate(self) -> float:
        """Get current failure rate."""
        with self._lock:
            if self.total_calls == 0:
                return 0.0
            return self.failure_count / self.total_calls
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all metrics as dictionary."""
        with self._lock:
            return {
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'total_calls': self.total_calls,
                'failure_rate': self.get_failure_rate(),
                'last_failure_time': self.last_failure_time,
                'state_change_count': self.state_change_count,
                'half_open_calls': self.half_open_calls
            }


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, message: str, circuit_name: str, state: CircuitBreakerState):
        super().__init__(message)
        self.circuit_name = circuit_name
        self.state = state


class CircuitBreaker:
    """Circuit breaker implementation."""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.last_opened_time = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
        
        # Callbacks for state changes
        self._on_state_change_callbacks = []
    
    def add_state_change_callback(self, callback: Callable[[CircuitBreakerState, CircuitBreakerState], None]):
        """Add callback to be called on state changes."""
        self._on_state_change_callbacks.append(callback)
    
    def _notify_state_change(self, old_state: CircuitBreakerState, new_state: CircuitBreakerState):
        """Notify all callbacks of state change."""
        for callback in self._on_state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")
    
    def _change_state(self, new_state: CircuitBreakerState):
        """Change circuit breaker state."""
        old_state = self.state
        self.state = new_state
        self.metrics.record_state_change()
        
        if new_state == CircuitBreakerState.OPEN:
            self.last_opened_time = time.time()
        
        self.logger.info(f"Circuit breaker {self.name} state changed: {old_state.value} -> {new_state.value}")
        self._notify_state_change(old_state, new_state)
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset from OPEN to HALF_OPEN."""
        if self.state != CircuitBreakerState.OPEN:
            return False
        
        if self.last_opened_time is None:
            return False
        
        return time.time() - self.last_opened_time >= self.config.recovery_timeout
    
    def _can_execute(self) -> bool:
        """Check if execution is allowed based on current state."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._change_state(CircuitBreakerState.HALF_OPEN)
                    self.metrics.reset_half_open_calls()
                    return True
                return False
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                return self.metrics.half_open_calls < self.config.half_open_max_calls
            
            return False
    
    def _record_success(self):
        """Record successful execution."""
        with self._lock:
            self.metrics.record_success()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                # If we have enough successful calls in half-open, close the circuit
                if self.metrics.half_open_calls >= self.config.half_open_max_calls - 1:
                    self._change_state(CircuitBreakerState.CLOSED)
    
    def _record_failure(self, exception: Exception):
        """Record failed execution."""
        with self._lock:
            # Only count expected exceptions as failures
            if isinstance(exception, self.config.expected_exception):
                self.metrics.record_failure()
                
                if self.state == CircuitBreakerState.CLOSED:
                    if self.metrics.failure_count >= self.config.failure_threshold:
                        self._change_state(CircuitBreakerState.OPEN)
                
                elif self.state == CircuitBreakerState.HALF_OPEN:
                    # Any failure in half-open immediately opens the circuit
                    self._change_state(CircuitBreakerState.OPEN)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self._can_execute():
            raise CircuitBreakerError(
                f"Circuit breaker {self.name} is {self.state.value}",
                self.name,
                self.state
            )
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.metrics.record_half_open_call()
        
        start_time = time.time()
        try:
            # Apply timeout if configured
            if hasattr(func, '__call__'):
                result = func(*args, **kwargs)
            else:
                result = func
            
            execution_time = time.time() - start_time
            
            # Check if execution took too long (treat as failure)
            if execution_time > self.config.timeout:
                timeout_error = TimeoutError(f"Function execution exceeded {self.config.timeout}s timeout")
                self._record_failure(timeout_error)
                raise timeout_error
            
            self._record_success()
            return result
            
        except Exception as e:
            self._record_failure(e)
            raise
    
    @contextmanager
    def context(self):
        """Context manager for circuit breaker protection."""
        if not self._can_execute():
            raise CircuitBreakerError(
                f"Circuit breaker {self.name} is {self.state.value}",
                self.name,
                self.state
            )
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.metrics.record_half_open_call()
        
        try:
            yield
            self._record_success()
        except Exception as e:
            self._record_failure(e)
            raise
    
    def get_state(self) -> CircuitBreakerState:
        """Get current state."""
        return self.state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            'name': self.name,
            'state': self.state.value,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'timeout': self.config.timeout,
                'half_open_max_calls': self.config.half_open_max_calls
            },
            'metrics': self.metrics.get_stats()
        }
    
    def reset(self):
        """Reset circuit breaker to closed state."""
        with self._lock:
            old_state = self.state
            self._change_state(CircuitBreakerState.CLOSED)
            self.metrics = CircuitBreakerMetrics()
            self.last_opened_time = None
            self.logger.info(f"Circuit breaker {self.name} manually reset")
    
    def force_open(self):
        """Force circuit breaker to open state."""
        with self._lock:
            self._change_state(CircuitBreakerState.OPEN)
            self.logger.warning(f"Circuit breaker {self.name} manually opened")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_or_create(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get existing circuit breaker or create new one."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
                self.logger.info(f"Created new circuit breaker: {name}")
            return self._breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self._breakers.get(name)
    
    def remove(self, name: str) -> bool:
        """Remove circuit breaker."""
        with self._lock:
            if name in self._breakers:
                del self._breakers[name]
                self.logger.info(f"Removed circuit breaker: {name}")
                return True
            return False
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers."""
        return {name: breaker.get_metrics() for name, breaker in self._breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
            self.logger.info("Reset all circuit breakers")
    
    def get_unhealthy_breakers(self) -> Dict[str, CircuitBreaker]:
        """Get all circuit breakers that are not in closed state."""
        return {
            name: breaker for name, breaker in self._breakers.items()
            if breaker.get_state() != CircuitBreakerState.CLOSED
        }


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator for applying circuit breaker pattern to functions."""
    def decorator(func: Callable) -> Callable:
        breaker = circuit_breaker_registry.get_or_create(name, config)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        # Attach the circuit breaker to the function for access
        wrapper._circuit_breaker = breaker
        return wrapper
    
    return decorator


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """Get circuit breaker by name."""
    return circuit_breaker_registry.get(name)


def create_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """Create or get circuit breaker."""
    return circuit_breaker_registry.get_or_create(name, config)


def reset_circuit_breaker(name: str) -> bool:
    """Reset specific circuit breaker."""
    breaker = circuit_breaker_registry.get(name)
    if breaker:
        breaker.reset()
        return True
    return False


def get_all_circuit_breaker_metrics() -> Dict[str, Dict[str, Any]]:
    """Get metrics for all circuit breakers."""
    return circuit_breaker_registry.get_all_metrics()


class CircuitBreakerMonitor:
    """Monitor for circuit breaker health and metrics."""
    
    def __init__(self, registry: CircuitBreakerRegistry):
        self.registry = registry
        self.logger = logging.getLogger(self.__class__.__name__)
        self._monitoring = False
        self._monitor_thread = None
        self.monitor_interval = 60.0  # seconds
    
    def start_monitoring(self, interval: float = 60.0):
        """Start monitoring circuit breakers."""
        self.monitor_interval = interval
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info(f"Started circuit breaker monitoring with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop monitoring circuit breakers."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()
        self.logger.info("Stopped circuit breaker monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                self._check_all_breakers()
                time.sleep(self.monitor_interval)
            except Exception as e:
                self.logger.error(f"Error in circuit breaker monitoring: {e}")
    
    def _check_all_breakers(self):
        """Check health of all circuit breakers."""
        unhealthy = self.registry.get_unhealthy_breakers()
        
        if unhealthy:
            self.logger.warning(f"Found {len(unhealthy)} unhealthy circuit breakers")
            for name, breaker in unhealthy.items():
                metrics = breaker.get_metrics()
                self.logger.warning(
                    f"Circuit breaker '{name}' is {breaker.get_state().value}: "
                    f"failures={metrics['metrics']['failure_count']}, "
                    f"total_calls={metrics['metrics']['total_calls']}"
                )
        
        # Log summary metrics
        all_metrics = self.registry.get_all_metrics()
        total_calls = sum(m['metrics']['total_calls'] for m in all_metrics.values())
        total_failures = sum(m['metrics']['failure_count'] for m in all_metrics.values())
        
        if total_calls > 0:
            overall_failure_rate = total_failures / total_calls
            self.logger.info(
                f"Circuit breaker summary: {len(all_metrics)} breakers, "
                f"{total_calls} total calls, {overall_failure_rate:.2%} failure rate"
            )


# Global monitor instance
circuit_breaker_monitor = CircuitBreakerMonitor(circuit_breaker_registry)

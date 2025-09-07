# Error Handling & Recovery Mechanisms Documentation

## Overview

The Error Handling & Recovery Mechanisms module provides a comprehensive suite of reliability features for the automation framework, including circuit breakers, enhanced error handling, recovery strategies, API client resilience, and database connection resilience.

## Components

### 1. Circuit Breaker Implementation

The circuit breaker pattern prevents cascading failures by temporarily failing fast when a service is detected to be failing.

#### Features
- **Three States**: CLOSED (normal), OPEN (failing fast), HALF_OPEN (testing recovery)
- **Configurable Thresholds**: Customizable failure counts and timeouts
- **Metrics Tracking**: Comprehensive statistics on failures and state changes
- **Registry System**: Global management of multiple circuit breakers
- **Monitoring**: Background health monitoring

#### Usage Examples

```python
from base.utilities.circuit_breaker import circuit_breaker, CircuitBreakerConfig

# Using decorator
@circuit_breaker("database_service")
def connect_to_database():
    # Database connection logic
    pass

# Manual circuit breaker
from base.utilities.circuit_breaker import create_circuit_breaker

cb = create_circuit_breaker("api_service", CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0
))

try:
    result = cb.call(some_function, arg1, arg2)
except CircuitBreakerError:
    print("Service temporarily unavailable")
```

### 2. Enhanced Error Handling

Provides centralized error handling with custom exception hierarchy and intelligent retry mechanisms.

#### Key Features
- **Custom Exception Hierarchy**: Specific exceptions for different error types
- **Error Categorization**: Automatic classification as transient or permanent
- **Retry Mechanisms**: Exponential backoff with jitter
- **Error Context Management**: Consistent error handling across operations
- **Statistics Tracking**: Comprehensive error metrics

#### Exception Types
- `BaseAutomationError`: Base exception for all framework errors
- `TransientError`: Errors that may succeed on retry
- `PermanentError`: Errors that should not be retried
- `ApiError`: API-specific errors with status codes
- `DatabaseError`: Database-specific errors with query context
- `WebDriverError`: WebDriver-specific errors with element context

#### Usage Examples

```python
from base.utilities.error_handler import error_context, retry_on_error

# Error context manager
with error_context("user_registration", additional_context={'user_id': '123'}):
    register_user(user_data)

# Retry decorator
@retry_on_error(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
def unreliable_operation():
    # Operation that might fail transiently
    pass
```

### 3. Recovery Strategies

Automatic recovery mechanisms for common transient failures with fallback support.

#### Components
- **Auto Recovery Manager**: Manages recovery attempts for failed operations
- **Health Checkers**: Monitor component health in real-time
- **Fallback Mechanisms**: Alternative execution paths for critical operations
- **Graceful Degradation**: Automatic switching to degraded operation modes
- **Recovery Hooks**: Seamless integration with base classes

#### Usage Examples

```python
from base.utilities.recovery_strategies import (
    create_fallback_mechanism, 
    auto_recovery_manager,
    graceful_degradation_manager
)

# Fallback mechanism
fallback = create_fallback_mechanism("data_service")
fallback.set_primary(get_data_from_api)
fallback.add_fallback(get_data_from_cache)
fallback.add_fallback(get_default_data)

result = fallback.execute(query_params)

# Graceful degradation
graceful_degradation_manager.register_degradation_mode(
    "offline_mode",
    condition_checker=lambda: not network_available(),
    degraded_behavior=lambda: use_cached_data()
)
```

### 4. API Client Enhancements

Enhanced API client with circuit breaker integration, retry logic, and health monitoring.

#### Key Features
- **Circuit Breaker Integration**: Automatic circuit breaker protection for all requests
- **Connection Retry Logic**: Intelligent retry with jitter and backoff
- **Rate Limiting**: Configurable request queuing to prevent API abuse
- **Timeout Handling**: Custom timeout exceptions with detailed context
- **Health Monitoring**: Real-time API endpoint health checking
- **Connection Statistics**: Comprehensive metrics on API performance

#### Configuration Options

```python
from base.api.base_api_client import BaseAPIClient
from base.utilities.circuit_breaker import CircuitBreakerConfig

# Enhanced API client
api_client = BaseAPIClient(
    base_url="https://api.example.com",
    timeout=30,
    enable_circuit_breaker=True,
    circuit_breaker_config=CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60.0
    ),
    rate_limit_per_second=10.0,
    enable_health_monitoring=True
)

# Get health status
health = api_client.get_health_status()
print(f"API Health: {health.status}")

# Get connection statistics
stats = api_client.get_connection_stats()
print(f"Success rate: {stats['successful_requests'] / stats['total_requests']:.2%}")
```

### 5. Database Connection Resilience

Enhanced database managers with circuit breaker pattern, connection pool recovery, and transaction management.

#### Features
- **Circuit Breaker Protection**: All database operations protected by circuit breakers
- **Connection Pool Recovery**: Automatic recovery of failed connection pools
- **Health Checks**: Real-time database connection monitoring
- **Automatic Reconnection**: Smart reconnection logic for transient failures
- **Transaction Rollback**: Automatic transaction management with rollback strategies
- **Multi-Database Support**: Enhanced MySQL, PostgreSQL, and SQLite managers

#### Usage Examples

```python
from base.database.mysql_manager import MySQLManager

# Enhanced database manager
db_manager = MySQLManager(
    config_path="config.ini",
    enable_circuit_breaker=True,
    connection_pool_size=10,
    max_overflow=20
)

# Connect with automatic retry
if db_manager.connect():
    # Transaction context manager
    with db_manager.transaction() as conn:
        conn.execute(text("INSERT INTO users (name) VALUES ('test')"))
        # Automatic commit or rollback

# Health check
health = db_manager.health_check()
if health['healthy']:
    print(f"Database healthy - response time: {health['response_time_ms']:.2f}ms")

# Connection pool statistics
pool_stats = db_manager.get_connection_pool_stats()
print(f"Active connections: {pool_stats['checked_out_connections']}")
```

## Configuration

### Global Configuration

Error handling and recovery can be configured globally through environment variables or configuration files:

```ini
[error_handling]
default_retry_attempts = 3
default_base_delay = 1.0
default_backoff_factor = 2.0
enable_jitter = true

[circuit_breaker]
default_failure_threshold = 5
default_recovery_timeout = 60.0
enable_monitoring = true

[recovery]
enable_auto_recovery = true
health_check_interval = 30.0
```

### Component-Specific Configuration

Each component can be configured independently:

```python
# API Client Configuration
api_config = {
    'timeout': 30,
    'rate_limit_per_second': 10.0,
    'circuit_breaker': {
        'failure_threshold': 5,
        'recovery_timeout': 60.0
    }
}

# Database Configuration
db_config = {
    'connection_pool_size': 10,
    'max_overflow': 20,
    'circuit_breaker': {
        'failure_threshold': 3,
        'recovery_timeout': 30.0
    }
}
```

## Monitoring and Metrics

### Error Statistics

```python
from base.utilities.error_handler import error_handler

# Get error statistics
stats = error_handler.get_error_statistics()
print(f"Total errors: {stats['total_errors']}")
print(f"Transient errors: {stats['transient_errors']}")
print(f"Permanent errors: {stats['permanent_errors']}")
```

### Circuit Breaker Metrics

```python
from base.utilities.circuit_breaker import get_all_circuit_breaker_metrics

# Get all circuit breaker metrics
metrics = get_all_circuit_breaker_metrics()
for name, data in metrics.items():
    print(f"{name}: {data['state']} - {data['metrics']['failure_count']} failures")
```

### Recovery Statistics

```python
from base.utilities.recovery_strategies import auto_recovery_manager

# Get recovery statistics
recovery_stats = auto_recovery_manager.get_recovery_stats()
print(f"Successful recoveries: {recovery_stats['successful_recoveries']}")
print(f"Failed recoveries: {recovery_stats['failed_recoveries']}")
```

## Best Practices

### 1. Error Categorization

Always categorize errors appropriately:

```python
# Good: Specific error with proper categorization
raise ApiError(
    "Service temporarily unavailable",
    status_code=503,
    category=ErrorCategory.TRANSIENT
)

# Bad: Generic exception without context
raise Exception("Something went wrong")
```

### 2. Circuit Breaker Usage

Use circuit breakers for external dependencies:

```python
# Good: Circuit breaker for external API
@circuit_breaker("payment_service")
def process_payment(payment_data):
    return external_payment_api.process(payment_data)

# Consider: Internal operations may not need circuit breakers
def validate_user_input(data):
    # Pure validation logic
    pass
```

### 3. Retry Strategy

Choose appropriate retry strategies:

```python
# Transient network errors - retry with backoff
@retry_on_error(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
def fetch_user_data(user_id):
    return api_client.get(f"/users/{user_id}")

# Permanent errors - don't retry
def validate_email_format(email):
    if not email_pattern.match(email):
        raise ValidationError("Invalid email format")  # Don't retry
```

### 4. Health Check Implementation

Implement lightweight health checks:

```python
# Good: Simple, fast health check
def api_health_check():
    response = requests.get("/health", timeout=5)
    return response.status_code == 200

# Avoid: Heavy operations in health checks
def avoid_heavy_health_check():
    # Don't do this - too slow and resource intensive
    heavy_computation()
    complex_database_query()
```

### 5. Transaction Management

Use transaction context managers for database operations:

```python
# Good: Automatic transaction management
with db_manager.transaction() as conn:
    conn.execute(text("INSERT INTO orders ..."))
    conn.execute(text("UPDATE inventory ..."))
    # Automatic commit on success, rollback on error

# Avoid: Manual transaction management
conn = db_manager.get_connection()
try:
    conn.begin()
    conn.execute("INSERT INTO orders ...")
    conn.execute("UPDATE inventory ...")
    conn.commit()
except:
    conn.rollback()  # Easy to forget!
```

## Troubleshooting

### Common Issues

#### 1. Circuit Breaker Stuck Open

**Symptoms**: Circuit breaker remains open despite service recovery
**Solution**: Check health checker implementation and recovery timeout

```python
# Check circuit breaker status
cb = get_circuit_breaker("service_name")
print(f"State: {cb.get_state()}")
print(f"Metrics: {cb.get_metrics()}")

# Manual reset if needed
cb.reset()
```

#### 2. Excessive Retry Attempts

**Symptoms**: Too many retry attempts causing delays
**Solution**: Review error categorization and retry configuration

```python
# Check error categorization
try:
    risky_operation()
except Exception as e:
    category = ErrorCategorizer.categorize_error(e)
    print(f"Error category: {category}")
```

#### 3. Database Connection Pool Exhaustion

**Symptoms**: Connection timeouts and pool errors
**Solution**: Monitor pool statistics and adjust configuration

```python
# Monitor pool health
pool_stats = db_manager.get_connection_pool_stats()
print(f"Pool size: {pool_stats['pool_size']}")
print(f"Active: {pool_stats['checked_out_connections']}")
print(f"Available: {pool_stats['checked_in_connections']}")
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging

# Enable debug logging for error handling
logging.getLogger('base.utilities.error_handler').setLevel(logging.DEBUG)
logging.getLogger('base.utilities.circuit_breaker').setLevel(logging.DEBUG)
logging.getLogger('base.utilities.recovery_strategies').setLevel(logging.DEBUG)
```

## Performance Considerations

- **Circuit Breaker Overhead**: Minimal performance impact in normal operation
- **Retry Logic**: Configured delays prevent overwhelming failed services
- **Health Checks**: Lightweight checks performed on-demand
- **Connection Pooling**: Improves database performance and resource usage
- **Memory Usage**: Bounded memory usage with configurable limits

## Integration with Testing Framework

All error handling and recovery mechanisms integrate seamlessly with the test automation framework:

- **Test Isolation**: Each test gets independent error handling context
- **Parallel Execution**: Thread-safe implementation for parallel test runs
- **Reporting**: Error statistics included in test reports
- **Cleanup**: Automatic cleanup of resources and connections
- **Mocking**: Support for mocking external dependencies in tests

This comprehensive error handling and recovery system provides enterprise-grade reliability for automation testing while maintaining high performance and ease of use.

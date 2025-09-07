# Test Data Management System

## Overview

The Test Data Management system provides comprehensive lifecycle management for test data in the Central Quality Hub automation framework. It offers robust capabilities for data creation, isolation, versioning, cleanup, and template-based generation.

## Core Components

### 1. Test Data Manager (`test_data_manager.py`)

The main orchestrator that provides centralized test data lifecycle management with support for:

- **Automatic cleanup registry and tracking**
- **Test data versioning and migration**
- **Data snapshot and restore capabilities**
- **Data isolation for parallel test execution**
- **Data conflict detection and resolution**
- **Data locking mechanisms and templates system**

### 2. Enhanced Database Test Data Generator

Extended functionality for generating realistic test data with:

- **Realistic data generation patterns**
- **Data relationship management**
- **Template-based data creation**
- **Data validation rules**

## Key Features

### Test Data Lifecycle Management

```python
from base.utilities.test_data_manager import TestDataManager

# Initialize manager
data_manager = TestDataManager()

# Create test data with lifecycle tracking
resource_id = data_manager.create_test_data(
    data_type="user",
    data={"username": "testuser", "email": "test@example.com"},
    namespace="test_suite_1",
    cleanup_callback=lambda: print("Cleaning up user data")
)

# Get test data
user_data = data_manager.get_test_data(resource_id, namespace="test_suite_1")

# Cleanup when done
cleanup_results = data_manager.cleanup_test_data(resource_id=resource_id)
```

### Data Isolation for Parallel Execution

```python
# Create isolated namespace for parallel test execution
with data_manager.isolated_data_context("worker_1") as namespace:
    # Create data in isolated environment
    user_id = data_manager.create_test_data(
        data_type="user",
        data={"username": "parallel_user"},
        namespace=namespace
    )
    
    # Data is automatically cleaned up when context exits
```

### Data Versioning and Migration

```python
# Create versioned data
version = data_manager.version_manager.create_version(
    resource_id="user_123",
    data={"name": "John", "version": "1.0"},
    version="1.0.0"
)

# Migrate to new version
migrated_data = data_manager.version_manager.migrate_to_version(
    resource_id="user_123",
    target_version="2.0.0"
)
```

### Data Snapshots and Restore

```python
# Create snapshot of current state
snapshot_id = data_manager.create_snapshot(
    name="baseline_data",
    namespace="test_suite_1",
    metadata={"test_run": "baseline_001"}
)

# Restore from snapshot later
success = data_manager.restore_snapshot(
    snapshot_id=snapshot_id,
    target_namespace="restored_environment"
)
```

### Template-Based Data Generation

```python
from base.database.database_test_data_generator import DatabaseTestDataGenerator

# Initialize generator
generator = DatabaseTestDataGenerator(enable_caching=True)

# Create data template
template_id = generator.create_data_template(
    template_name="standard_user",
    template_data={
        "username": "${username}",
        "email": "${username}@company.com",
        "department": "${department}",
        "role": "employee"
    },
    entity_type="user"
)

# Generate data from template
user_data = generator.generate_from_template(
    template_id=template_id,
    count=5,
    username="john.doe",
    department="engineering"
)
```

### Realistic Data Generation

```python
# Generate realistic user data with patterns
realistic_users = generator.generate_realistic_user_data(
    count=10,
    cache_key="realistic_batch_1"
)

# Generate related data
orders = generator.generate_related_data(
    entity_type="order",
    parent_data=realistic_users,
    count_per_parent=3
)

# Validate generated data
is_valid = generator.validate_generated_data(realistic_users, "user")
```

### Data Locking and Conflict Detection

```python
# Lock resource for exclusive access
lock_acquired = data_manager.isolation_manager.lock_resource(
    namespace="shared_env",
    resource_key="shared_user_1",
    lock_id="test_worker_1"
)

if lock_acquired:
    # Use resource exclusively
    # ...
    
    # Release lock when done
    data_manager.isolation_manager.unlock_resource(
        namespace="shared_env",
        resource_key="shared_user_1",
        lock_id="test_worker_1"
    )
```

## Configuration

### Basic Configuration

```python
# Initialize with custom settings
data_manager = TestDataManager(
    base_path="/custom/test/data/path",
    enable_versioning=True
)

# Configure cleanup registry
data_manager.cleanup_registry._max_retries = 5

# Setup health checks
health_results = data_manager.run_health_checks()
```

### Cache Configuration

```python
# Configure test data generator with caching
generator = DatabaseTestDataGenerator(
    enable_caching=True,
    cache_ttl=7200  # 2 hours
)

# Enable cache warming
generator.enable_cache_warming()

# Get cache performance metrics
metrics = generator.get_cache_performance_metrics()
```

## Advanced Features

### Custom Migration Handlers

```python
from base.utilities.test_data_manager import DataMigrationHandler

class UserDataMigrationHandler(DataMigrationHandler):
    def can_handle(self, from_version: str, to_version: str) -> bool:
        return from_version == "1.0.0" and to_version == "2.0.0"
    
    def migrate(self, data: Any, from_version: str, to_version: str) -> Any:
        # Add new fields for version 2.0.0
        if isinstance(data, dict):
            data["profile_updated_at"] = datetime.now().isoformat()
            data["preferences"] = {"theme": "light", "notifications": True}
        return data

# Register migration handler
data_manager.version_manager.register_migration_handler(UserDataMigrationHandler())
```

### Custom Cleanup Callbacks

```python
def custom_cleanup():
    print("Performing custom cleanup operations")
    # Additional cleanup logic here

# Register custom cleanup callback
data_manager.cleanup_registry.add_cleanup_callback(
    resource_id=resource_id,
    callback=custom_cleanup
)
```

### Health Monitoring

```python
# Run comprehensive health checks
health_status = data_manager.run_health_checks()

# Get detailed status report
status_report = data_manager.get_status_report()

# Monitor cleanup performance
cleanup_report = data_manager.cleanup_registry.get_cleanup_report()
```

## Best Practices

### 1. Use Namespaces for Isolation

Always use appropriate namespaces to isolate test data:

```python
# Good: Use specific namespace
data_manager.create_test_data(
    data_type="user",
    data=user_data,
    namespace=f"test_suite_{test_id}"
)

# Avoid: Using default namespace for everything
```

### 2. Implement Proper Cleanup

Always register cleanup callbacks for resources that need special handling:

```python
def cleanup_database_user(user_id):
    # Database-specific cleanup
    db.delete_user(user_id)

resource_id = data_manager.create_test_data(
    data_type="user",
    data=user_data,
    cleanup_callback=lambda: cleanup_database_user(user_data["id"])
)
```

### 3. Use Templates for Consistency

Create templates for commonly used data patterns:

```python
# Create standard templates
standard_user_template = generator.create_data_template(
    template_name="standard_user",
    template_data={
        "username": "${username}",
        "email": "${username}@company.com",
        "role": "user",
        "is_active": True
    },
    entity_type="user"
)

# Reuse templates across tests
test_users = generator.generate_from_template(
    template_id=standard_user_template,
    count=10
)
```

### 4. Monitor Data Health

Regularly check the health of your test data management:

```python
# Schedule regular health checks
def periodic_health_check():
    health_status = data_manager.run_health_checks()
    if not all(health_status.values()):
        logger.warning(f"Health check failures: {health_status}")

# Run cleanup verification
cleanup_report = data_manager.cleanup_registry.get_cleanup_report()
failed_cleanups = cleanup_report.get('failed_cleanups', [])
if failed_cleanups:
    logger.error(f"Failed cleanups detected: {failed_cleanups}")
```

### 5. Use Versioning for Data Evolution

Implement versioning for test data that evolves over time:

```python
# Create initial version
initial_data = {"name": "John", "email": "john@example.com"}
version_1 = data_manager.version_manager.create_version(
    resource_id="user_profile",
    data=initial_data,
    version="1.0.0"
)

# Evolve data structure
enhanced_data = {
    "name": "John",
    "email": "john@example.com",
    "preferences": {"theme": "dark"}
}
version_2 = data_manager.version_manager.create_version(
    resource_id="user_profile",
    data=enhanced_data,
    version="2.0.0"
)
```

## Integration Examples

### With Behave Steps

```python
# In your step definitions
from base.utilities.test_data_manager import get_test_data_manager

@given('I have test user data for "{test_scenario}"')
def step_create_test_user(context, test_scenario):
    data_manager = get_test_data_manager()
    
    user_data = {
        "username": f"test_user_{test_scenario}",
        "email": f"test_{test_scenario}@example.com"
    }
    
    context.user_id = data_manager.create_test_data(
        data_type="user",
        data=user_data,
        namespace=context.scenario.name.lower().replace(" ", "_")
    )

@then('cleanup test data for this scenario')
def step_cleanup_test_data(context):
    data_manager = get_test_data_manager()
    namespace = context.scenario.name.lower().replace(" ", "_")
    data_manager.cleanup_test_data(namespace=namespace)
```

### With Database Tests

```python
# Database integration
from base.utilities.test_data_manager import TestDataManager
from base.database.database_test_data_generator import DatabaseTestDataGenerator

class DatabaseTestHelper:
    def __init__(self):
        self.data_manager = TestDataManager()
        self.generator = DatabaseTestDataGenerator(enable_caching=True)
    
    def setup_test_data(self, test_name: str):
        # Generate realistic test data
        users = self.generator.generate_realistic_user_data(
            count=5,
            cache_key=f"users_{test_name}"
        )
        
        # Store in database and track for cleanup
        for user in users:
            user_id = self.insert_user_to_db(user)
            self.data_manager.create_test_data(
                data_type="db_user",
                data={"db_id": user_id, "user_data": user},
                namespace=test_name,
                cleanup_callback=lambda uid=user_id: self.delete_user_from_db(uid)
            )
    
    def cleanup_test_data(self, test_name: str):
        return self.data_manager.cleanup_test_data(namespace=test_name)
```

## Performance Considerations

### 1. Cache Optimization

```python
# Configure appropriate cache TTL
generator = DatabaseTestDataGenerator(
    enable_caching=True,
    cache_ttl=3600  # 1 hour for frequently used data
)

# Monitor cache performance
cache_metrics = generator.get_cache_performance_metrics()
cache_hit_rate = cache_metrics.get('hit_rate', 0)
if cache_hit_rate < 0.8:  # 80% hit rate threshold
    logger.warning(f"Low cache hit rate: {cache_hit_rate}")
```

### 2. Cleanup Optimization

```python
# Batch cleanup operations
cleanup_results = data_manager.cleanup_test_data(namespace="large_test_suite")

# Monitor cleanup performance
cleanup_report = data_manager.cleanup_registry.get_cleanup_report()
retry_counts = cleanup_report.get('retry_counts', {})
high_retry_resources = [rid for rid, count in retry_counts.items() if count > 2]
if high_retry_resources:
    logger.warning(f"Resources requiring multiple cleanup attempts: {high_retry_resources}")
```

### 3. Memory Management

```python
# Use snapshots for large datasets
if len(test_data) > 1000:
    snapshot_id = data_manager.create_snapshot(
        name="large_dataset_backup",
        namespace=test_namespace
    )
    
    # Process data in chunks
    # ...
    
    # Restore if needed
    data_manager.restore_snapshot(snapshot_id)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Cleanup Failures

```python
# Check cleanup report for failed resources
cleanup_report = data_manager.cleanup_registry.get_cleanup_report()
failed_cleanups = cleanup_report.get('failed_cleanups', [])

for resource_id in failed_cleanups:
    # Manual cleanup
    try:
        manual_cleanup_resource(resource_id)
        data_manager.cleanup_registry.unregister_resource(resource_id)
    except Exception as e:
        logger.error(f"Manual cleanup failed for {resource_id}: {e}")
```

#### 2. Data Conflicts

```python
# Monitor and resolve conflicts
conflicts = data_manager.isolation_manager.get_conflicts()
for conflict in conflicts:
    logger.warning(f"Data conflict detected: {conflict}")
    # Implement conflict resolution strategy
    resolve_data_conflict(conflict)
```

#### 3. Version Migration Issues

```python
# Handle migration failures
try:
    migrated_data = data_manager.version_manager.migrate_to_version(
        resource_id="problematic_resource",
        target_version="2.0.0"
    )
except Exception as e:
    logger.error(f"Migration failed: {e}")
    # Fallback to manual migration or previous version
    fallback_data = data_manager.version_manager.get_version(
        resource_id="problematic_resource",
        version="1.0.0"
    )
```

## API Reference

### TestDataManager

- `create_test_data(data_type, data, namespace, **kwargs)` - Create managed test data
- `get_test_data(resource_id, namespace, version)` - Retrieve test data
- `cleanup_test_data(**kwargs)` - Clean up test data
- `create_snapshot(name, namespace, metadata)` - Create data snapshot
- `restore_snapshot(snapshot_id, target_namespace)` - Restore from snapshot
- `run_health_checks()` - Run system health checks
- `get_status_report()` - Get comprehensive status report

### DatabaseTestDataGenerator

- `generate_realistic_user_data(count, cache_key, use_cache)` - Generate realistic users
- `generate_related_data(entity_type, parent_data, count_per_parent)` - Generate related data
- `validate_generated_data(data, entity_type)` - Validate generated data
- `create_data_template(template_name, template_data, entity_type)` - Create reusable template
- `generate_from_template(template_id, count, **context)` - Generate from template

For complete API documentation, refer to the source code docstrings.

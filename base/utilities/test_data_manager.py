"""
Test Data Manager - Comprehensive test data lifecycle management system

This module provides centralized test data lifecycle management with support for:
- Automatic cleanup registry and tracking
- Test data versioning and migration
- Data snapshot and restore capabilities
- Data isolation for parallel test execution
- Data conflict detection and resolution
- Data locking mechanisms and templates system
"""

import os
import json
import uuid
import threading
import weakref
import shutil
import sqlite3
import pickle
import hashlib
import logging
from typing import Dict, List, Any, Optional, Callable, Set, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict
import tempfile


@dataclass
class TestDataResource:
    """Represents a test data resource that needs lifecycle management."""
    resource_id: str
    resource_type: str
    namespace: str
    created_at: datetime
    cleanup_callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    is_locked: bool = False
    locked_by: Optional[str] = None
    version: str = "1.0.0"
    size_bytes: int = 0


@dataclass
class DataSnapshot:
    """Represents a data snapshot for backup/restore."""
    snapshot_id: str
    name: str
    namespace: str
    created_at: datetime
    data_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    size_bytes: int = 0
    checksum: str = ""


@dataclass
class DataTemplate:
    """Represents a reusable data template."""
    template_id: str
    name: str
    template_type: str
    template_data: Any
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataMigrationHandler(ABC):
    """Abstract base class for data migration handlers."""
    
    @abstractmethod
    def can_handle(self, from_version: str, to_version: str) -> bool:
        """Check if this handler can migrate between versions."""
        pass
    
    @abstractmethod
    def migrate(self, data: Any, from_version: str, to_version: str) -> Any:
        """Perform the migration."""
        pass


class CleanupRegistry:
    """Registry for tracking resources that need cleanup."""
    
    def __init__(self):
        self._resources: Dict[str, TestDataResource] = {}
        self._namespaces: Dict[str, Set[str]] = defaultdict(set)
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._cleanup_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Cleanup verification tracking
        self._cleanup_results: Dict[str, bool] = {}
        self._cleanup_retry_count: Dict[str, int] = defaultdict(int)
        self._max_retries = 3
    
    def register_resource(self, resource: TestDataResource) -> str:
        """Register a resource for cleanup tracking."""
        with self._lock:
            resource_id = resource.resource_id
            self._resources[resource_id] = resource
            self._namespaces[resource.namespace].add(resource_id)
            
            # Register dependencies
            for dep_id in resource.dependencies:
                self._dependencies[dep_id].add(resource_id)
            
            self.logger.debug(f"Registered resource: {resource_id} in namespace: {resource.namespace}")
            return resource_id
    
    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource from cleanup tracking."""
        with self._lock:
            if resource_id not in self._resources:
                return False
            
            resource = self._resources[resource_id]
            
            # Remove from namespace
            self._namespaces[resource.namespace].discard(resource_id)
            
            # Remove dependencies
            for dep_id in resource.dependencies:
                self._dependencies[dep_id].discard(resource_id)
            
            # Remove the resource
            del self._resources[resource_id]
            
            self.logger.debug(f"Unregistered resource: {resource_id}")
            return True
    
    def cleanup_resource(self, resource_id: str) -> bool:
        """Cleanup a specific resource with retry logic."""
        with self._lock:
            if resource_id not in self._resources:
                self.logger.warning(f"Resource not found for cleanup: {resource_id}")
                return False
            
            resource = self._resources[resource_id]
            
            # Check if resource is locked
            if resource.is_locked:
                self.logger.warning(f"Cannot cleanup locked resource: {resource_id}")
                return False
            
            # Check dependencies
            if resource_id in self._dependencies and self._dependencies[resource_id]:
                dependent_resources = list(self._dependencies[resource_id])
                self.logger.warning(f"Cannot cleanup resource {resource_id} - has dependencies: {dependent_resources}")
                return False
            
            # Perform cleanup with retry
            for attempt in range(self._max_retries):
                try:
                    if resource.cleanup_callback:
                        resource.cleanup_callback()
                    
                    # Execute additional cleanup callbacks
                    for callback in self._cleanup_callbacks.get(resource_id, []):
                        callback()
                    
                    # Verify cleanup
                    if self._verify_cleanup(resource):
                        self._cleanup_results[resource_id] = True
                        self.unregister_resource(resource_id)
                        self.logger.info(f"Successfully cleaned up resource: {resource_id}")
                        return True
                    else:
                        raise Exception("Cleanup verification failed")
                        
                except Exception as e:
                    self._cleanup_retry_count[resource_id] = attempt + 1
                    self.logger.warning(f"Cleanup attempt {attempt + 1} failed for {resource_id}: {e}")
                    
                    if attempt == self._max_retries - 1:
                        self._cleanup_results[resource_id] = False
                        self.logger.error(f"Failed to cleanup resource after {self._max_retries} attempts: {resource_id}")
                        return False
            
            return False
    
    def cleanup_namespace(self, namespace: str) -> Dict[str, bool]:
        """Cleanup all resources in a namespace."""
        with self._lock:
            if namespace not in self._namespaces:
                return {}
            
            resource_ids = list(self._namespaces[namespace])
            results = {}
            
            # Sort by dependencies (cleanup dependents first)
            sorted_resources = self._sort_by_dependencies(resource_ids)
            
            for resource_id in sorted_resources:
                results[resource_id] = self.cleanup_resource(resource_id)
            
            self.logger.info(f"Cleaned up namespace '{namespace}': {sum(results.values())}/{len(results)} successful")
            return results
    
    def cleanup_all(self) -> Dict[str, bool]:
        """Cleanup all registered resources."""
        with self._lock:
            all_resource_ids = list(self._resources.keys())
            results = {}
            
            # Sort by dependencies
            sorted_resources = self._sort_by_dependencies(all_resource_ids)
            
            for resource_id in sorted_resources:
                results[resource_id] = self.cleanup_resource(resource_id)
            
            self.logger.info(f"Global cleanup completed: {sum(results.values())}/{len(results)} successful")
            return results
    
    def add_cleanup_callback(self, resource_id: str, callback: Callable):
        """Add additional cleanup callback for a resource."""
        with self._lock:
            self._cleanup_callbacks[resource_id].append(callback)
    
    def get_cleanup_report(self) -> Dict[str, Any]:
        """Get comprehensive cleanup report."""
        with self._lock:
            return {
                'total_resources': len(self._resources),
                'namespaces': {ns: len(resources) for ns, resources in self._namespaces.items()},
                'cleanup_results': self._cleanup_results.copy(),
                'retry_counts': self._cleanup_retry_count.copy(),
                'failed_cleanups': [rid for rid, success in self._cleanup_results.items() if not success],
                'locked_resources': [rid for rid, res in self._resources.items() if res.is_locked]
            }
    
    def _verify_cleanup(self, resource: TestDataResource) -> bool:
        """Verify that resource cleanup was successful."""
        try:
            # Basic verification - check if resource metadata indicates successful cleanup
            # This can be extended with specific verification logic per resource type
            if resource.metadata.get('verification_callback'):
                return resource.metadata['verification_callback']()
            return True
        except Exception as e:
            self.logger.error(f"Cleanup verification failed for {resource.resource_id}: {e}")
            return False
    
    def _sort_by_dependencies(self, resource_ids: List[str]) -> List[str]:
        """Sort resources by dependencies (dependents first)."""
        sorted_ids = []
        remaining = set(resource_ids)
        
        while remaining:
            # Find resources with no dependents in remaining set
            no_dependents = []
            for rid in remaining:
                has_dependents = any(
                    dep in remaining for dep in self._dependencies.get(rid, set())
                )
                if not has_dependents:
                    no_dependents.append(rid)
            
            if not no_dependents:
                # Circular dependency - just take remaining
                no_dependents = list(remaining)
            
            sorted_ids.extend(no_dependents)
            remaining -= set(no_dependents)
        
        return sorted_ids


class DataVersionManager:
    """Manages test data versioning and migration."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.versions_db_path = self.base_path / "versions.db"
        self._migration_handlers: List[DataMigrationHandler] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize the versions database."""
        with sqlite3.connect(str(self.versions_db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_versions (
                    resource_id TEXT PRIMARY KEY,
                    current_version TEXT NOT NULL,
                    version_history TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def register_migration_handler(self, handler: DataMigrationHandler):
        """Register a migration handler."""
        self._migration_handlers.append(handler)
        self.logger.debug(f"Registered migration handler: {handler.__class__.__name__}")
    
    def create_version(self, resource_id: str, data: Any, version: str = None) -> str:
        """Create a new version of data."""
        if version is None:
            version = self._generate_version(resource_id)
        
        # Store the data
        version_path = self._get_version_path(resource_id, version)
        version_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(version_path, 'wb') as f:
            pickle.dump(data, f)
        
        # Update version database
        with sqlite3.connect(str(self.versions_db_path)) as conn:
            # Get current version history
            cursor = conn.execute(
                "SELECT version_history FROM data_versions WHERE resource_id = ?",
                (resource_id,)
            )
            row = cursor.fetchone()
            
            if row:
                version_history = json.loads(row[0])
                version_history.append({
                    'version': version,
                    'created_at': datetime.now().isoformat(),
                    'size_bytes': version_path.stat().st_size
                })
                
                conn.execute(
                    "UPDATE data_versions SET current_version = ?, version_history = ?, updated_at = CURRENT_TIMESTAMP WHERE resource_id = ?",
                    (version, json.dumps(version_history), resource_id)
                )
            else:
                version_history = [{
                    'version': version,
                    'created_at': datetime.now().isoformat(),
                    'size_bytes': version_path.stat().st_size
                }]
                
                conn.execute(
                    "INSERT INTO data_versions (resource_id, current_version, version_history) VALUES (?, ?, ?)",
                    (resource_id, version, json.dumps(version_history))
                )
            
            conn.commit()
        
        self.logger.info(f"Created version {version} for resource {resource_id}")
        return version
    
    def get_version(self, resource_id: str, version: str = None) -> Any:
        """Get a specific version of data."""
        if version is None:
            version = self.get_current_version(resource_id)
        
        version_path = self._get_version_path(resource_id, version)
        if not version_path.exists():
            raise ValueError(f"Version {version} not found for resource {resource_id}")
        
        with open(version_path, 'rb') as f:
            return pickle.load(f)
    
    def get_current_version(self, resource_id: str) -> str:
        """Get the current version of a resource."""
        with sqlite3.connect(str(self.versions_db_path)) as conn:
            cursor = conn.execute(
                "SELECT current_version FROM data_versions WHERE resource_id = ?",
                (resource_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"No versions found for resource {resource_id}")
            
            return row[0]
    
    def migrate_to_version(self, resource_id: str, target_version: str) -> Any:
        """Migrate data to a target version."""
        current_version = self.get_current_version(resource_id)
        
        if current_version == target_version:
            return self.get_version(resource_id, current_version)
        
        # Find migration path
        migration_handler = None
        for handler in self._migration_handlers:
            if handler.can_handle(current_version, target_version):
                migration_handler = handler
                break
        
        if not migration_handler:
            raise ValueError(f"No migration handler found for {current_version} -> {target_version}")
        
        # Get current data and migrate
        current_data = self.get_version(resource_id, current_version)
        migrated_data = migration_handler.migrate(current_data, current_version, target_version)
        
        # Create new version
        self.create_version(resource_id, migrated_data, target_version)
        
        self.logger.info(f"Migrated resource {resource_id} from {current_version} to {target_version}")
        return migrated_data
    
    def get_version_history(self, resource_id: str) -> List[Dict[str, Any]]:
        """Get version history for a resource."""
        with sqlite3.connect(str(self.versions_db_path)) as conn:
            cursor = conn.execute(
                "SELECT version_history FROM data_versions WHERE resource_id = ?",
                (resource_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return []
            
            return json.loads(row[0])
    
    def cleanup_old_versions(self, resource_id: str, keep_count: int = 5):
        """Cleanup old versions, keeping only the most recent ones."""
        version_history = self.get_version_history(resource_id)
        
        if len(version_history) <= keep_count:
            return
        
        # Sort by creation date and keep only recent ones
        version_history.sort(key=lambda x: x['created_at'], reverse=True)
        versions_to_delete = version_history[keep_count:]
        
        for version_info in versions_to_delete:
            version_path = self._get_version_path(resource_id, version_info['version'])
            if version_path.exists():
                version_path.unlink()
        
        # Update database
        new_history = version_history[:keep_count]
        with sqlite3.connect(str(self.versions_db_path)) as conn:
            conn.execute(
                "UPDATE data_versions SET version_history = ?, updated_at = CURRENT_TIMESTAMP WHERE resource_id = ?",
                (json.dumps(new_history), resource_id)
            )
            conn.commit()
        
        self.logger.info(f"Cleaned up {len(versions_to_delete)} old versions for resource {resource_id}")
    
    def _generate_version(self, resource_id: str) -> str:
        """Generate a new version number."""
        try:
            current_version = self.get_current_version(resource_id)
            # Simple semantic versioning increment
            parts = current_version.split('.')
            patch = int(parts[2]) + 1
            return f"{parts[0]}.{parts[1]}.{patch}"
        except ValueError:
            return "1.0.0"
    
    def _get_version_path(self, resource_id: str, version: str) -> Path:
        """Get the file path for a specific version."""
        return self.base_path / "versions" / resource_id / f"{version}.pkl"


class DataIsolationManager:
    """Manages data isolation for parallel test execution."""
    
    def __init__(self):
        self._namespaces: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, threading.RLock] = defaultdict(threading.RLock)
        self._conflicts: List[Dict[str, Any]] = []
        self._isolation_environments: Dict[str, str] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_namespace(self, namespace: str, worker_id: str = None) -> str:
        """Create an isolated namespace for test data."""
        if worker_id:
            namespace = f"{namespace}_{worker_id}"
        
        if namespace in self._namespaces:
            raise ValueError(f"Namespace {namespace} already exists")
        
        self._namespaces[namespace] = {
            'created_at': datetime.now(),
            'worker_id': worker_id,
            'resources': {},
            'metadata': {}
        }
        
        # Create isolated environment
        env_path = self._create_isolated_environment(namespace)
        self._isolation_environments[namespace] = env_path
        
        self.logger.info(f"Created isolated namespace: {namespace}")
        return namespace
    
    def get_namespace_data(self, namespace: str, key: str, default=None):
        """Get data from a namespace."""
        if namespace not in self._namespaces:
            return default
        
        return self._namespaces[namespace]['resources'].get(key, default)
    
    def set_namespace_data(self, namespace: str, key: str, value: Any):
        """Set data in a namespace."""
        if namespace not in self._namespaces:
            raise ValueError(f"Namespace {namespace} does not exist")
        
        with self._locks[namespace]:
            # Check for conflicts
            conflict = self._detect_conflict(namespace, key, value)
            if conflict:
                self._conflicts.append(conflict)
                raise RuntimeError(f"Data conflict detected: {conflict}")
            
            self._namespaces[namespace]['resources'][key] = value
        
        self.logger.debug(f"Set data in namespace {namespace}: {key}")
    
    def lock_resource(self, namespace: str, resource_key: str, lock_id: str) -> bool:
        """Lock a resource in a namespace."""
        if namespace not in self._namespaces:
            return False
        
        with self._locks[namespace]:
            resources = self._namespaces[namespace]['resources']
            
            if resource_key in resources:
                resource = resources[resource_key]
                if hasattr(resource, 'is_locked') and resource.is_locked:
                    return False
                
                if hasattr(resource, 'is_locked'):
                    resource.is_locked = True
                    resource.locked_by = lock_id
                    self.logger.debug(f"Locked resource {resource_key} in namespace {namespace}")
                    return True
        
        return False
    
    def unlock_resource(self, namespace: str, resource_key: str, lock_id: str) -> bool:
        """Unlock a resource in a namespace."""
        if namespace not in self._namespaces:
            return False
        
        with self._locks[namespace]:
            resources = self._namespaces[namespace]['resources']
            
            if resource_key in resources:
                resource = resources[resource_key]
                if hasattr(resource, 'is_locked') and resource.is_locked and resource.locked_by == lock_id:
                    resource.is_locked = False
                    resource.locked_by = None
                    self.logger.debug(f"Unlocked resource {resource_key} in namespace {namespace}")
                    return True
        
        return False
    
    def cleanup_namespace(self, namespace: str):
        """Cleanup an isolated namespace."""
        if namespace not in self._namespaces:
            return
        
        # Cleanup isolated environment
        env_path = self._isolation_environments.get(namespace)
        if env_path and os.path.exists(env_path):
            shutil.rmtree(env_path)
        
        # Remove namespace
        del self._namespaces[namespace]
        if namespace in self._isolation_environments:
            del self._isolation_environments[namespace]
        
        # Remove locks
        if namespace in self._locks:
            del self._locks[namespace]
        
        self.logger.info(f"Cleaned up namespace: {namespace}")
    
    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Get detected conflicts."""
        return self._conflicts.copy()
    
    def _detect_conflict(self, namespace: str, key: str, value: Any) -> Optional[Dict[str, Any]]:
        """Detect potential data conflicts."""
        # Simple conflict detection - check if key exists with different value
        current_value = self._namespaces[namespace]['resources'].get(key)
        
        if current_value is not None and current_value != value:
            return {
                'namespace': namespace,
                'key': key,
                'current_value': current_value,
                'new_value': value,
                'detected_at': datetime.now().isoformat()
            }
        
        return None
    
    def _create_isolated_environment(self, namespace: str) -> str:
        """Create isolated environment directory."""
        env_path = os.path.join(tempfile.gettempdir(), f"test_env_{namespace}")
        os.makedirs(env_path, exist_ok=True)
        return env_path


class DataTemplateManager:
    """Manages reusable data templates and relationships."""
    
    def __init__(self, templates_path: str = None):
        self.templates_path = Path(templates_path) if templates_path else Path.cwd() / "test_templates"
        self.templates_path.mkdir(parents=True, exist_ok=True)
        self._templates: Dict[str, DataTemplate] = {}
        self._validation_rules: Dict[str, List[Callable]] = defaultdict(list)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._load_templates()
    
    def create_template(self, name: str, template_type: str, template_data: Any,
                       validation_rules: List[Dict] = None, relationships: Dict[str, str] = None) -> str:
        """Create a new data template."""
        template_id = str(uuid.uuid4())
        
        template = DataTemplate(
            template_id=template_id,
            name=name,
            template_type=template_type,
            template_data=template_data,
            validation_rules=validation_rules or [],
            relationships=relationships or {},
            metadata={'created_at': datetime.now().isoformat()}
        )
        
        self._templates[template_id] = template
        self._save_template(template)
        
        self.logger.info(f"Created template: {name} ({template_id})")
        return template_id
    
    def get_template(self, template_id: str) -> Optional[DataTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)
    
    def get_template_by_name(self, name: str) -> Optional[DataTemplate]:
        """Get a template by name."""
        for template in self._templates.values():
            if template.name == name:
                return template
        return None
    
    def apply_template(self, template_id: str, context: Dict[str, Any] = None) -> Any:
        """Apply a template with context variables."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Apply context to template data
        applied_data = self._apply_context(template.template_data, context or {})
        
        # Validate data
        if not self._validate_data(applied_data, template.validation_rules):
            raise ValueError(f"Template data validation failed for {template_id}")
        
        return applied_data
    
    def generate_from_template(self, template_name: str, count: int = 1,
                             context: Dict[str, Any] = None) -> Union[Any, List[Any]]:
        """Generate data from template."""
        template = self.get_template_by_name(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        if count == 1:
            return self.apply_template(template.template_id, context)
        else:
            return [self.apply_template(template.template_id, context) for _ in range(count)]
    
    def add_validation_rule(self, template_id: str, rule: Callable):
        """Add a validation rule for a template."""
        self._validation_rules[template_id].append(rule)
    
    def _apply_context(self, data: Any, context: Dict[str, Any]) -> Any:
        """Apply context variables to template data."""
        if isinstance(data, dict):
            return {k: self._apply_context(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._apply_context(item, context) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            # Simple variable substitution
            var_name = data[2:-1]
            return context.get(var_name, data)
        else:
            return data
    
    def _validate_data(self, data: Any, validation_rules: List[Dict]) -> bool:
        """Validate data against rules."""
        for rule in validation_rules:
            rule_type = rule.get('type')
            field = rule.get('field')
            
            if rule_type == 'required' and field:
                if not self._check_required_field(data, field):
                    return False
            elif rule_type == 'type_check' and field:
                expected_type = rule.get('expected_type')
                if not self._check_field_type(data, field, expected_type):
                    return False
        
        return True
    
    def _check_required_field(self, data: Any, field: str) -> bool:
        """Check if required field is present."""
        if isinstance(data, dict):
            return field in data and data[field] is not None
        return False
    
    def _check_field_type(self, data: Any, field: str, expected_type: str) -> bool:
        """Check if field has expected type."""
        if isinstance(data, dict) and field in data:
            value = data[field]
            if expected_type == 'string':
                return isinstance(value, str)
            elif expected_type == 'integer':
                return isinstance(value, int)
            elif expected_type == 'float':
                return isinstance(value, float)
            elif expected_type == 'boolean':
                return isinstance(value, bool)
        return False
    
    def _save_template(self, template: DataTemplate):
        """Save template to file."""
        template_file = self.templates_path / f"{template.template_id}.json"
        template_data = {
            'template_id': template.template_id,
            'name': template.name,
            'template_type': template.template_type,
            'template_data': template.template_data,
            'validation_rules': template.validation_rules,
            'relationships': template.relationships,
            'metadata': template.metadata
        }
        
        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2, default=str)
    
    def _load_templates(self):
        """Load templates from files."""
        for template_file in self.templates_path.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                
                template = DataTemplate(**template_data)
                self._templates[template.template_id] = template
                
            except Exception as e:
                self.logger.warning(f"Failed to load template {template_file}: {e}")


class TestDataManager:
    """Main test data manager orchestrating all components."""
    
    def __init__(self, base_path: str = None, enable_versioning: bool = True):
        self.base_path = Path(base_path) if base_path else Path.cwd() / "test_data"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.cleanup_registry = CleanupRegistry()
        self.isolation_manager = DataIsolationManager()
        self.template_manager = DataTemplateManager(str(self.base_path / "templates"))
        
        if enable_versioning:
            self.version_manager = DataVersionManager(str(self.base_path / "versions"))
        else:
            self.version_manager = None
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Health check tracking
        self._health_checks: Dict[str, Callable] = {}
        self._last_health_check: Optional[datetime] = None
        
        # Setup cleanup hooks
        self._setup_cleanup_hooks()
    
    def create_test_data(self, data_type: str, data: Any, namespace: str = "default",
                        resource_id: str = None, cleanup_callback: Callable = None,
                        version: str = None) -> str:
        """Create test data with lifecycle management."""
        if resource_id is None:
            resource_id = f"{data_type}_{uuid.uuid4().hex[:8]}"
        
        # Create resource
        resource = TestDataResource(
            resource_id=resource_id,
            resource_type=data_type,
            namespace=namespace,
            created_at=datetime.now(),
            cleanup_callback=cleanup_callback,
            metadata={'data_type': data_type},
            version=version or "1.0.0"
        )
        
        # Register for cleanup
        self.cleanup_registry.register_resource(resource)
        
        # Create version if versioning is enabled
        if self.version_manager:
            self.version_manager.create_version(resource_id, data, version)
        
        # Store in isolation manager
        if namespace != "default":
            if namespace not in self.isolation_manager._namespaces:
                self.isolation_manager.create_namespace(namespace)
            self.isolation_manager.set_namespace_data(namespace, resource_id, data)
        
        self.logger.info(f"Created test data: {resource_id} in namespace: {namespace}")
        return resource_id
    
    def get_test_data(self, resource_id: str, namespace: str = "default", version: str = None) -> Any:
        """Get test data by resource ID."""
        if namespace != "default":
            data = self.isolation_manager.get_namespace_data(namespace, resource_id)
            if data is not None:
                return data
        
        if self.version_manager:
            return self.version_manager.get_version(resource_id, version)
        
        raise ValueError(f"Data not found: {resource_id}")
    
    def cleanup_test_data(self, resource_id: str = None, namespace: str = None) -> Dict[str, bool]:
        """Cleanup test data."""
        if resource_id:
            result = self.cleanup_registry.cleanup_resource(resource_id)
            return {resource_id: result}
        elif namespace:
            return self.cleanup_registry.cleanup_namespace(namespace)
        else:
            return self.cleanup_registry.cleanup_all()
    
    def create_snapshot(self, name: str, namespace: str = "default", 
                       metadata: Dict[str, Any] = None) -> str:
        """Create a data snapshot."""
        snapshot_id = str(uuid.uuid4())
        snapshot_path = self.base_path / "snapshots" / f"{snapshot_id}.pkl"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Collect namespace data
        if namespace in self.isolation_manager._namespaces:
            namespace_data = self.isolation_manager._namespaces[namespace]['resources']
        else:
            namespace_data = {}
        
        # Save snapshot
        with open(snapshot_path, 'wb') as f:
            pickle.dump(namespace_data, f)
        
        # Create snapshot record
        snapshot = DataSnapshot(
            snapshot_id=snapshot_id,
            name=name,
            namespace=namespace,
            created_at=datetime.now(),
            data_path=str(snapshot_path),
            metadata=metadata or {},
            size_bytes=snapshot_path.stat().st_size,
            checksum=self._calculate_checksum(snapshot_path)
        )
        
        # Save snapshot metadata
        metadata_path = self.base_path / "snapshots" / f"{snapshot_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump({
                'snapshot_id': snapshot.snapshot_id,
                'name': snapshot.name,
                'namespace': snapshot.namespace,
                'created_at': snapshot.created_at.isoformat(),
                'data_path': snapshot.data_path,
                'metadata': snapshot.metadata,
                'size_bytes': snapshot.size_bytes,
                'checksum': snapshot.checksum
            }, f, indent=2)
        
        self.logger.info(f"Created snapshot: {name} ({snapshot_id})")
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id: str, target_namespace: str = None) -> bool:
        """Restore from a data snapshot."""
        metadata_path = self.base_path / "snapshots" / f"{snapshot_id}_metadata.json"
        
        if not metadata_path.exists():
            self.logger.error(f"Snapshot metadata not found: {snapshot_id}")
            return False
        
        # Load snapshot metadata
        with open(metadata_path, 'r') as f:
            snapshot_data = json.load(f)
        
        snapshot_path = Path(snapshot_data['data_path'])
        if not snapshot_path.exists():
            self.logger.error(f"Snapshot data not found: {snapshot_path}")
            return False
        
        # Verify checksum
        if self._calculate_checksum(snapshot_path) != snapshot_data['checksum']:
            self.logger.error(f"Snapshot checksum verification failed: {snapshot_id}")
            return False
        
        # Load and restore data
        with open(snapshot_path, 'rb') as f:
            namespace_data = pickle.load(f)
        
        namespace = target_namespace or snapshot_data['namespace']
        
        # Create namespace if it doesn't exist
        if namespace not in self.isolation_manager._namespaces:
            self.isolation_manager.create_namespace(namespace)
        
        # Restore data
        for resource_id, data in namespace_data.items():
            self.isolation_manager.set_namespace_data(namespace, resource_id, data)
        
        self.logger.info(f"Restored snapshot {snapshot_id} to namespace {namespace}")
        return True
    
    def run_health_checks(self) -> Dict[str, bool]:
        """Run health checks on test data management components."""
        results = {}
        
        # Check cleanup registry health
        results['cleanup_registry'] = len(self.cleanup_registry._resources) < 1000  # Arbitrary limit
        
        # Check isolation manager health
        results['isolation_manager'] = len(self.isolation_manager._namespaces) < 100  # Arbitrary limit
        
        # Check version manager health
        if self.version_manager:
            try:
                # Check if version database is accessible
                with sqlite3.connect(str(self.version_manager.versions_db_path)) as conn:
                    conn.execute("SELECT COUNT(*) FROM data_versions")
                results['version_manager'] = True
            except Exception:
                results['version_manager'] = False
        
        # Check template manager health
        results['template_manager'] = self.template_manager.templates_path.exists()
        
        self._last_health_check = datetime.now()
        
        # Log results
        failed_checks = [component for component, status in results.items() if not status]
        if failed_checks:
            self.logger.warning(f"Health check failures: {failed_checks}")
        else:
            self.logger.info("All health checks passed")
        
        return results
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        return {
            'cleanup_registry': self.cleanup_registry.get_cleanup_report(),
            'isolation_manager': {
                'namespaces': list(self.isolation_manager._namespaces.keys()),
                'conflicts': len(self.isolation_manager.get_conflicts())
            },
            'template_manager': {
                'templates_count': len(self.template_manager._templates)
            },
            'version_manager': {
                'enabled': self.version_manager is not None
            },
            'health_checks': {
                'last_run': self._last_health_check.isoformat() if self._last_health_check else None
            }
        }
    
    @contextmanager
    def isolated_data_context(self, namespace: str = None):
        """Context manager for isolated test data."""
        if namespace is None:
            namespace = f"temp_{uuid.uuid4().hex[:8]}"
        
        # Create namespace
        self.isolation_manager.create_namespace(namespace)
        
        try:
            yield namespace
        finally:
            # Cleanup namespace
            self.cleanup_test_data(namespace=namespace)
            self.isolation_manager.cleanup_namespace(namespace)
    
    def _setup_cleanup_hooks(self):
        """Setup cleanup hooks for proper resource management."""
        import atexit
        
        def cleanup_all_resources():
            try:
                self.cleanup_test_data()
                self.logger.info("Cleanup completed on exit")
            except Exception as e:
                self.logger.error(f"Error during exit cleanup: {e}")
        
        atexit.register(cleanup_all_resources)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# Global test data manager instance
_global_test_data_manager = None


def get_test_data_manager() -> TestDataManager:
    """Get global test data manager instance."""
    global _global_test_data_manager
    if _global_test_data_manager is None:
        _global_test_data_manager = TestDataManager()
    return _global_test_data_manager


# Convenience functions
def create_test_data(data_type: str, data: Any, namespace: str = "default", **kwargs) -> str:
    """Create test data using global manager."""
    return get_test_data_manager().create_test_data(data_type, data, namespace, **kwargs)


def get_test_data(resource_id: str, namespace: str = "default", **kwargs) -> Any:
    """Get test data using global manager."""
    return get_test_data_manager().get_test_data(resource_id, namespace, **kwargs)


def cleanup_test_data(**kwargs) -> Dict[str, bool]:
    """Cleanup test data using global manager."""
    return get_test_data_manager().cleanup_test_data(**kwargs)


def create_data_snapshot(name: str, namespace: str = "default", **kwargs) -> str:
    """Create data snapshot using global manager."""
    return get_test_data_manager().create_snapshot(name, namespace, **kwargs)


def restore_data_snapshot(snapshot_id: str, **kwargs) -> bool:
    """Restore data snapshot using global manager."""
    return get_test_data_manager().restore_snapshot(snapshot_id, **kwargs)

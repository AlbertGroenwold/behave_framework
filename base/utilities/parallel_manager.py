"""
Parallel Execution Manager - Test isolation and resource management for parallel test execution

This module provides comprehensive test isolation capabilities for parallel test execution with:
- Resource locking mechanisms to prevent conflicts
- Test dependency management for proper execution order
- Isolated test environments for each worker
- Test quarantine system for flaky tests
"""

import os
import json
import uuid
import threading
import time
import logging
import hashlib
import tempfile
import shutil
from typing import Dict, List, Set, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import weakref
import queue
import statistics
import psutil


@dataclass
class TestResource:
    """Represents a test resource that can be locked."""
    resource_id: str
    resource_type: str
    resource_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    lock_timeout: Optional[float] = None
    is_exclusive: bool = True
    max_concurrent_users: int = 1


@dataclass
class TestDependency:
    """Represents a dependency between tests."""
    dependent_test: str
    dependency_test: str
    dependency_type: str  # 'before', 'after', 'parallel_safe', 'mutex'
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IsolatedEnvironment:
    """Represents an isolated test environment."""
    environment_id: str
    worker_id: str
    base_path: str
    temp_path: str
    resources: Dict[str, Any] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    cleanup_callbacks: List[Callable] = field(default_factory=list)


@dataclass
class QuarantinedTest:
    """Represents a quarantined flaky test."""
    test_id: str
    test_name: str
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    quarantine_reason: str = ""
    quarantine_start: Optional[datetime] = None
    release_criteria: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourcePool:
    """Represents a pool of shared resources."""
    pool_id: str
    resource_type: str
    total_capacity: int
    available_capacity: int
    allocated_resources: Dict[str, str] = field(default_factory=dict)  # resource_id -> worker_id
    waiting_queue: List[Tuple[str, datetime]] = field(default_factory=list)  # (worker_id, request_time)
    health_status: str = "healthy"  # "healthy", "degraded", "unhealthy"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerNode:
    """Represents a worker node in the test distribution system."""
    worker_id: str
    worker_type: str
    capabilities: List[str] = field(default_factory=list)
    current_load: int = 0
    max_capacity: int = 1
    health_score: float = 1.0
    last_heartbeat: Optional[datetime] = None
    assigned_tests: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestGroup:
    """Represents a group of related tests for distribution."""
    group_id: str
    group_name: str
    test_ids: List[str] = field(default_factory=list)
    group_type: str = "functional"  # "functional", "integration", "performance"
    priority: int = 1
    estimated_duration: Optional[float] = None
    required_capabilities: List[str] = field(default_factory=list)
    parallel_safe: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelExecutionMetrics:
    """Metrics for parallel execution monitoring."""
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tests: int = 0
    completed_tests: int = 0
    failed_tests: int = 0
    worker_count: int = 0
    average_test_duration: float = 0.0
    total_execution_time: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    throughput_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class QuarantinedTest:
    """Represents a quarantined flaky test."""
    test_id: str
    test_name: str
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    quarantine_reason: str = ""
    quarantine_start: Optional[datetime] = None
    release_criteria: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResourceLockManager:
    """Manages resource locking for parallel test execution."""
    
    def __init__(self):
        self._locks: Dict[str, threading.RLock] = defaultdict(threading.RLock)
        self._resources: Dict[str, TestResource] = {}
        self._lock_registry: Dict[str, str] = {}  # resource_id -> lock_holder
        self._lock_queue: Dict[str, deque] = defaultdict(deque)
        self._timeout_monitor = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register_resource(self, resource: TestResource) -> str:
        """Register a resource for locking."""
        with self._locks[resource.resource_id]:
            self._resources[resource.resource_id] = resource
            self.logger.debug(f"Registered resource: {resource.resource_id}")
            return resource.resource_id
    
    def acquire_lock(self, resource_id: str, lock_holder: str, 
                    timeout: Optional[float] = None) -> bool:
        """Acquire an exclusive lock on a resource."""
        if resource_id not in self._resources:
            self.logger.error(f"Resource not found: {resource_id}")
            return False
        
        resource = self._resources[resource_id]
        
        with self._locks[resource_id]:
            # Check if already locked
            if resource.locked_by and resource.locked_by != lock_holder:
                # Check if lock has timed out
                if self._is_lock_expired(resource):
                    self._force_release_lock(resource_id)
                else:
                    # Add to queue if configured for queuing
                    if timeout:
                        self._lock_queue[resource_id].append((lock_holder, time.time() + timeout))
                    self.logger.debug(f"Resource {resource_id} is locked by {resource.locked_by}")
                    return False
            
            # Acquire lock
            resource.locked_by = lock_holder
            resource.locked_at = datetime.now()
            resource.lock_timeout = timeout
            self._lock_registry[resource_id] = lock_holder
            
            # Set timeout monitor
            if timeout:
                self._timeout_monitor[resource_id] = time.time() + timeout
            
            self.logger.info(f"Lock acquired on {resource_id} by {lock_holder}")
            return True
    
    def release_lock(self, resource_id: str, lock_holder: str) -> bool:
        """Release a lock on a resource."""
        if resource_id not in self._resources:
            return False
        
        resource = self._resources[resource_id]
        
        with self._locks[resource_id]:
            if resource.locked_by != lock_holder:
                self.logger.warning(f"Lock release attempt by non-owner: {lock_holder} for {resource_id}")
                return False
            
            # Release lock
            resource.locked_by = None
            resource.locked_at = None
            resource.lock_timeout = None
            
            if resource_id in self._lock_registry:
                del self._lock_registry[resource_id]
            
            if resource_id in self._timeout_monitor:
                del self._timeout_monitor[resource_id]
            
            # Process queue
            self._process_lock_queue(resource_id)
            
            self.logger.info(f"Lock released on {resource_id} by {lock_holder}")
            return True
    
    def force_release_lock(self, resource_id: str) -> bool:
        """Force release a lock (admin operation)."""
        return self._force_release_lock(resource_id)
    
    def _force_release_lock(self, resource_id: str) -> bool:
        """Internal method to force release a lock."""
        if resource_id not in self._resources:
            return False
        
        resource = self._resources[resource_id]
        old_holder = resource.locked_by
        
        with self._locks[resource_id]:
            resource.locked_by = None
            resource.locked_at = None
            resource.lock_timeout = None
            
            if resource_id in self._lock_registry:
                del self._lock_registry[resource_id]
            
            if resource_id in self._timeout_monitor:
                del self._timeout_monitor[resource_id]
            
            self._process_lock_queue(resource_id)
            
            self.logger.warning(f"Force released lock on {resource_id} (was held by {old_holder})")
            return True
    
    def is_locked(self, resource_id: str) -> bool:
        """Check if a resource is currently locked."""
        if resource_id not in self._resources:
            return False
        
        resource = self._resources[resource_id]
        
        # Check for expired locks
        if resource.locked_by and self._is_lock_expired(resource):
            self._force_release_lock(resource_id)
            return False
        
        return resource.locked_by is not None
    
    def get_lock_holder(self, resource_id: str) -> Optional[str]:
        """Get the current lock holder for a resource."""
        if resource_id not in self._resources:
            return None
        
        resource = self._resources[resource_id]
        
        if resource.locked_by and self._is_lock_expired(resource):
            self._force_release_lock(resource_id)
            return None
        
        return resource.locked_by
    
    def cleanup_expired_locks(self):
        """Clean up expired locks."""
        expired_resources = []
        
        for resource_id, resource in self._resources.items():
            if resource.locked_by and self._is_lock_expired(resource):
                expired_resources.append(resource_id)
        
        for resource_id in expired_resources:
            self._force_release_lock(resource_id)
        
        if expired_resources:
            self.logger.info(f"Cleaned up {len(expired_resources)} expired locks")
    
    def get_lock_status(self) -> Dict[str, Any]:
        """Get status of all locks."""
        status = {
            'total_resources': len(self._resources),
            'locked_resources': len(self._lock_registry),
            'queued_requests': sum(len(queue) for queue in self._lock_queue.values()),
            'resources': {}
        }
        
        for resource_id, resource in self._resources.items():
            status['resources'][resource_id] = {
                'locked': resource.locked_by is not None,
                'locked_by': resource.locked_by,
                'locked_at': resource.locked_at.isoformat() if resource.locked_at else None,
                'timeout': resource.lock_timeout,
                'queue_length': len(self._lock_queue.get(resource_id, []))
            }
        
        return status
    
    def _is_lock_expired(self, resource: TestResource) -> bool:
        """Check if a lock has expired."""
        if not resource.locked_at or not resource.lock_timeout:
            return False
        
        elapsed = (datetime.now() - resource.locked_at).total_seconds()
        return elapsed > resource.lock_timeout
    
    def _process_lock_queue(self, resource_id: str):
        """Process queued lock requests for a resource."""
        if resource_id not in self._lock_queue or not self._lock_queue[resource_id]:
            return
        
        current_time = time.time()
        queue = self._lock_queue[resource_id]
        
        # Remove expired requests
        while queue and queue[0][1] < current_time:
            expired_holder, _ = queue.popleft()
            self.logger.debug(f"Removed expired lock request from {expired_holder} for {resource_id}")
        
        # Try to grant lock to next in queue
        if queue:
            next_holder, _ = queue.popleft()
            if self.acquire_lock(resource_id, next_holder):
                self.logger.info(f"Granted queued lock to {next_holder} for {resource_id}")


class TestDependencyManager:
    """Manages test dependencies for proper execution order."""
    
    def __init__(self):
        self._dependencies: Dict[str, List[TestDependency]] = defaultdict(list)
        self._reverse_deps: Dict[str, List[TestDependency]] = defaultdict(list)
        self._test_status: Dict[str, str] = {}  # 'pending', 'running', 'completed', 'failed'
        self._completion_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_dependency(self, dependency: TestDependency):
        """Add a test dependency."""
        self._dependencies[dependency.dependent_test].append(dependency)
        self._reverse_deps[dependency.dependency_test].append(dependency)
        
        # Initialize test status if not exists
        if dependency.dependent_test not in self._test_status:
            self._test_status[dependency.dependent_test] = 'pending'
        if dependency.dependency_test not in self._test_status:
            self._test_status[dependency.dependency_test] = 'pending'
        
        self.logger.debug(f"Added dependency: {dependency.dependent_test} depends on {dependency.dependency_test}")
    
    def can_execute_test(self, test_id: str) -> bool:
        """Check if a test can be executed based on its dependencies."""
        if test_id not in self._dependencies:
            return True  # No dependencies
        
        for dependency in self._dependencies[test_id]:
            dep_status = self._test_status.get(dependency.dependency_test, 'pending')
            
            if dependency.dependency_type == 'before':
                if dep_status not in ['completed']:
                    return False
            elif dependency.dependency_type == 'mutex':
                if dep_status == 'running':
                    return False
            # 'parallel_safe' and 'after' don't block execution
        
        return True
    
    def mark_test_started(self, test_id: str):
        """Mark a test as started."""
        self._test_status[test_id] = 'running'
        self.logger.debug(f"Test started: {test_id}")
    
    def mark_test_completed(self, test_id: str, success: bool = True):
        """Mark a test as completed."""
        self._test_status[test_id] = 'completed' if success else 'failed'
        
        # Trigger completion callbacks
        for callback in self._completion_callbacks.get(test_id, []):
            try:
                callback(test_id, success)
            except Exception as e:
                self.logger.error(f"Error in completion callback for {test_id}: {e}")
        
        self.logger.info(f"Test completed: {test_id} ({'success' if success else 'failed'})")
    
    def get_runnable_tests(self, available_tests: List[str]) -> List[str]:
        """Get list of tests that can currently be executed."""
        runnable = []
        
        for test_id in available_tests:
            if (self._test_status.get(test_id, 'pending') == 'pending' and 
                self.can_execute_test(test_id)):
                runnable.append(test_id)
        
        return runnable
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the dependency graph."""
        graph = {}
        
        for test_id, deps in self._dependencies.items():
            graph[test_id] = [dep.dependency_test for dep in deps]
        
        return graph
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies."""
        def dfs(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dep in self._dependencies.get(node, []):
                neighbor = dep.dependency_test
                
                if neighbor not in visited:
                    cycle = dfs(neighbor, visited, rec_stack, path.copy())
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            path.pop()
            return None
        
        visited = set()
        cycles = []
        
        for test_id in self._test_status.keys():
            if test_id not in visited:
                cycle = dfs(test_id, visited, set(), [])
                if cycle:
                    cycles.append(cycle)
        
        return cycles
    
    def add_completion_callback(self, test_id: str, callback: Callable):
        """Add a callback to be called when a test completes."""
        self._completion_callbacks[test_id].append(callback)


class IsolatedEnvironmentManager:
    """Manages isolated test environments for parallel execution."""
    
    def __init__(self, base_temp_dir: str = None):
        self.base_temp_dir = Path(base_temp_dir) if base_temp_dir else Path(tempfile.gettempdir()) / "test_isolation"
        self.base_temp_dir.mkdir(parents=True, exist_ok=True)
        self._environments: Dict[str, IsolatedEnvironment] = {}
        self._worker_environments: Dict[str, str] = {}  # worker_id -> environment_id
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_environment(self, worker_id: str, environment_config: Dict[str, Any] = None) -> str:
        """Create an isolated environment for a worker."""
        environment_id = f"env_{worker_id}_{uuid.uuid4().hex[:8]}"
        
        # Create temporary directory
        temp_path = self.base_temp_dir / environment_id
        temp_path.mkdir(parents=True, exist_ok=True)
        
        # Create base path structure
        base_path = temp_path / "workspace"
        base_path.mkdir(exist_ok=True)
        
        # Setup environment variables
        env_vars = {
            'TEST_WORKER_ID': worker_id,
            'TEST_ENVIRONMENT_ID': environment_id,
            'TEST_TEMP_PATH': str(temp_path),
            'TEST_BASE_PATH': str(base_path),
            'TEST_ISOLATION_MODE': 'true'
        }
        
        if environment_config:
            env_vars.update(environment_config.get('environment_variables', {}))
        
        # Create environment
        environment = IsolatedEnvironment(
            environment_id=environment_id,
            worker_id=worker_id,
            base_path=str(base_path),
            temp_path=str(temp_path),
            environment_variables=env_vars
        )
        
        self._environments[environment_id] = environment
        self._worker_environments[worker_id] = environment_id
        
        # Setup cleanup callback
        def cleanup_env():
            self.cleanup_environment(environment_id)
        
        environment.cleanup_callbacks.append(cleanup_env)
        
        self.logger.info(f"Created isolated environment {environment_id} for worker {worker_id}")
        return environment_id
    
    def get_environment(self, environment_id: str) -> Optional[IsolatedEnvironment]:
        """Get an environment by ID."""
        return self._environments.get(environment_id)
    
    def get_worker_environment(self, worker_id: str) -> Optional[IsolatedEnvironment]:
        """Get the environment for a specific worker."""
        environment_id = self._worker_environments.get(worker_id)
        if environment_id:
            return self._environments.get(environment_id)
        return None
    
    def add_resource_to_environment(self, environment_id: str, resource_name: str, resource_data: Any):
        """Add a resource to an environment."""
        if environment_id in self._environments:
            self._environments[environment_id].resources[resource_name] = resource_data
            self.logger.debug(f"Added resource {resource_name} to environment {environment_id}")
    
    def get_resource_from_environment(self, environment_id: str, resource_name: str) -> Any:
        """Get a resource from an environment."""
        environment = self._environments.get(environment_id)
        if environment:
            return environment.resources.get(resource_name)
        return None
    
    def cleanup_environment(self, environment_id: str):
        """Clean up an isolated environment."""
        if environment_id not in self._environments:
            return
        
        environment = self._environments[environment_id]
        
        # Run cleanup callbacks
        for callback in environment.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in cleanup callback for {environment_id}: {e}")
        
        # Remove temporary directory
        temp_path = Path(environment.temp_path)
        if temp_path.exists():
            shutil.rmtree(str(temp_path), ignore_errors=True)
        
        # Remove from tracking
        del self._environments[environment_id]
        
        # Remove worker mapping
        worker_id = environment.worker_id
        if worker_id in self._worker_environments:
            del self._worker_environments[worker_id]
        
        self.logger.info(f"Cleaned up environment {environment_id}")
    
    def cleanup_all_environments(self):
        """Clean up all environments."""
        environment_ids = list(self._environments.keys())
        for environment_id in environment_ids:
            self.cleanup_environment(environment_id)
        
        self.logger.info(f"Cleaned up {len(environment_ids)} environments")
    
    @contextmanager
    def isolated_environment(self, worker_id: str, config: Dict[str, Any] = None):
        """Context manager for isolated environment."""
        environment_id = self.create_environment(worker_id, config)
        try:
            yield self.get_environment(environment_id)
        finally:
            self.cleanup_environment(environment_id)


class TestQuarantineManager:
    """Manages quarantine for flaky tests."""
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path.cwd() / "test_quarantine.json"
        self._quarantined_tests: Dict[str, QuarantinedTest] = {}
        self._failure_threshold = 3  # Number of failures before quarantine
        self._success_threshold = 5  # Number of successes needed to release
        self._quarantine_duration = timedelta(hours=24)  # Default quarantine duration
        self.logger = logging.getLogger(self.__class__.__name__)
        self._load_quarantine_data()
    
    def record_test_result(self, test_id: str, test_name: str, success: bool, 
                          failure_reason: str = None):
        """Record a test result and check for quarantine conditions."""
        if test_id not in self._quarantined_tests:
            self._quarantined_tests[test_id] = QuarantinedTest(
                test_id=test_id,
                test_name=test_name
            )
        
        quarantined_test = self._quarantined_tests[test_id]
        
        if success:
            quarantined_test.success_count += 1
            # Check if test can be released from quarantine
            if (quarantined_test.quarantine_start and 
                quarantined_test.success_count >= self._success_threshold):
                self._release_from_quarantine(test_id)
        else:
            quarantined_test.failure_count += 1
            quarantined_test.last_failure_time = datetime.now()
            
            # Check if test should be quarantined
            if (not quarantined_test.quarantine_start and 
                quarantined_test.failure_count >= self._failure_threshold):
                self._quarantine_test(test_id, failure_reason or "Excessive failures")
        
        self._save_quarantine_data()
    
    def is_test_quarantined(self, test_id: str) -> bool:
        """Check if a test is currently quarantined."""
        if test_id not in self._quarantined_tests:
            return False
        
        quarantined_test = self._quarantined_tests[test_id]
        
        if not quarantined_test.quarantine_start:
            return False
        
        # Check if quarantine has expired
        if datetime.now() - quarantined_test.quarantine_start > self._quarantine_duration:
            self._release_from_quarantine(test_id)
            return False
        
        return True
    
    def get_quarantined_tests(self) -> List[QuarantinedTest]:
        """Get list of currently quarantined tests."""
        quarantined = []
        
        for test_id, quarantined_test in self._quarantined_tests.items():
            if self.is_test_quarantined(test_id):
                quarantined.append(quarantined_test)
        
        return quarantined
    
    def force_quarantine(self, test_id: str, test_name: str, reason: str):
        """Force quarantine a test."""
        if test_id not in self._quarantined_tests:
            self._quarantined_tests[test_id] = QuarantinedTest(
                test_id=test_id,
                test_name=test_name
            )
        
        self._quarantine_test(test_id, reason)
        self._save_quarantine_data()
    
    def force_release(self, test_id: str):
        """Force release a test from quarantine."""
        if test_id in self._quarantined_tests:
            self._release_from_quarantine(test_id)
            self._save_quarantine_data()
    
    def get_test_stats(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a test."""
        if test_id not in self._quarantined_tests:
            return None
        
        quarantined_test = self._quarantined_tests[test_id]
        total_runs = quarantined_test.success_count + quarantined_test.failure_count
        
        return {
            'test_id': test_id,
            'test_name': quarantined_test.test_name,
            'total_runs': total_runs,
            'success_count': quarantined_test.success_count,
            'failure_count': quarantined_test.failure_count,
            'success_rate': (quarantined_test.success_count / total_runs * 100) if total_runs > 0 else 0,
            'is_quarantined': self.is_test_quarantined(test_id),
            'quarantine_start': quarantined_test.quarantine_start,
            'last_failure_time': quarantined_test.last_failure_time,
            'quarantine_reason': quarantined_test.quarantine_reason
        }
    
    def _quarantine_test(self, test_id: str, reason: str):
        """Internal method to quarantine a test."""
        quarantined_test = self._quarantined_tests[test_id]
        quarantined_test.quarantine_start = datetime.now()
        quarantined_test.quarantine_reason = reason
        quarantined_test.success_count = 0  # Reset success count
        
        self.logger.warning(f"Test quarantined: {test_id} - {reason}")
    
    def _release_from_quarantine(self, test_id: str):
        """Internal method to release a test from quarantine."""
        quarantined_test = self._quarantined_tests[test_id]
        quarantined_test.quarantine_start = None
        quarantined_test.quarantine_reason = ""
        
        self.logger.info(f"Test released from quarantine: {test_id}")
    
    def _load_quarantine_data(self):
        """Load quarantine data from file."""
        if not self.config_path.exists():
            return
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            for test_data in data.get('quarantined_tests', []):
                test_id = test_data['test_id']
                quarantined_test = QuarantinedTest(
                    test_id=test_id,
                    test_name=test_data['test_name'],
                    failure_count=test_data.get('failure_count', 0),
                    success_count=test_data.get('success_count', 0),
                    quarantine_reason=test_data.get('quarantine_reason', ''),
                    metadata=test_data.get('metadata', {})
                )
                
                # Parse datetime fields
                if test_data.get('last_failure_time'):
                    quarantined_test.last_failure_time = datetime.fromisoformat(test_data['last_failure_time'])
                
                if test_data.get('quarantine_start'):
                    quarantined_test.quarantine_start = datetime.fromisoformat(test_data['quarantine_start'])
                
                self._quarantined_tests[test_id] = quarantined_test
            
            self.logger.info(f"Loaded {len(self._quarantined_tests)} quarantine records")
            
        except Exception as e:
            self.logger.error(f"Error loading quarantine data: {e}")
    
    def _save_quarantine_data(self):
        """Save quarantine data to file."""
        try:
            data = {
                'quarantined_tests': [],
                'updated_at': datetime.now().isoformat()
            }
            
            for test_id, quarantined_test in self._quarantined_tests.items():
                test_data = {
                    'test_id': test_id,
                    'test_name': quarantined_test.test_name,
                    'failure_count': quarantined_test.failure_count,
                    'success_count': quarantined_test.success_count,
                    'quarantine_reason': quarantined_test.quarantine_reason,
                    'metadata': quarantined_test.metadata
                }
                
                if quarantined_test.last_failure_time:
                    test_data['last_failure_time'] = quarantined_test.last_failure_time.isoformat()
                
                if quarantined_test.quarantine_start:
                    test_data['quarantine_start'] = quarantined_test.quarantine_start.isoformat()
                
                data['quarantined_tests'].append(test_data)
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving quarantine data: {e}")


class ResourcePoolManager:
    """Manages resource pools for parallel test execution."""
    
    def __init__(self):
        self._pools: Dict[str, ResourcePool] = {}
        self._pool_locks: Dict[str, threading.RLock] = defaultdict(threading.RLock)
        self._health_monitor_interval = 30.0  # seconds
        self._health_monitor_thread = None
        self._stop_monitoring = threading.Event()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_resource_pool(self, pool_id: str, resource_type: str, 
                           total_capacity: int, metadata: Dict[str, Any] = None) -> str:
        """Create a new resource pool."""
        with self._pool_locks[pool_id]:
            if pool_id in self._pools:
                raise ValueError(f"Pool {pool_id} already exists")
            
            pool = ResourcePool(
                pool_id=pool_id,
                resource_type=resource_type,
                total_capacity=total_capacity,
                available_capacity=total_capacity,
                metadata=metadata or {}
            )
            
            self._pools[pool_id] = pool
            self.logger.info(f"Created resource pool: {pool_id} with capacity {total_capacity}")
            return pool_id
    
    def allocate_resource(self, pool_id: str, worker_id: str, timeout: float = None) -> Optional[str]:
        """Allocate a resource from a pool to a worker."""
        if pool_id not in self._pools:
            return None
        
        with self._pool_locks[pool_id]:
            pool = self._pools[pool_id]
            
            if pool.available_capacity > 0:
                # Allocate resource
                resource_id = f"{pool_id}_resource_{len(pool.allocated_resources) + 1}"
                pool.allocated_resources[resource_id] = worker_id
                pool.available_capacity -= 1
                
                self.logger.debug(f"Allocated resource {resource_id} from pool {pool_id} to worker {worker_id}")
                return resource_id
            else:
                # Add to waiting queue if timeout specified
                if timeout:
                    pool.waiting_queue.append((worker_id, datetime.now()))
                    self.logger.debug(f"Added worker {worker_id} to waiting queue for pool {pool_id}")
                
                return None
    
    def release_resource(self, pool_id: str, resource_id: str, worker_id: str) -> bool:
        """Release a resource back to the pool."""
        if pool_id not in self._pools:
            return False
        
        with self._pool_locks[pool_id]:
            pool = self._pools[pool_id]
            
            if (resource_id in pool.allocated_resources and 
                pool.allocated_resources[resource_id] == worker_id):
                
                # Release resource
                del pool.allocated_resources[resource_id]
                pool.available_capacity += 1
                
                # Process waiting queue
                self._process_waiting_queue(pool_id)
                
                self.logger.debug(f"Released resource {resource_id} from pool {pool_id} by worker {worker_id}")
                return True
        
        return False
    
    def get_pool_status(self, pool_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a resource pool."""
        if pool_id not in self._pools:
            return None
        
        pool = self._pools[pool_id]
        return {
            'pool_id': pool_id,
            'resource_type': pool.resource_type,
            'total_capacity': pool.total_capacity,
            'available_capacity': pool.available_capacity,
            'allocated_count': len(pool.allocated_resources),
            'waiting_queue_length': len(pool.waiting_queue),
            'health_status': pool.health_status,
            'utilization_rate': (pool.total_capacity - pool.available_capacity) / pool.total_capacity * 100
        }
    
    def start_health_monitoring(self):
        """Start health monitoring for resource pools."""
        if self._health_monitor_thread and self._health_monitor_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._health_monitor_thread = threading.Thread(target=self._health_monitor_loop)
        self._health_monitor_thread.daemon = True
        self._health_monitor_thread.start()
        self.logger.info("Started resource health monitoring")
    
    def stop_health_monitoring(self):
        """Stop health monitoring."""
        self._stop_monitoring.set()
        if self._health_monitor_thread and self._health_monitor_thread.is_alive():
            self._health_monitor_thread.join(timeout=5)
        self.logger.info("Stopped resource health monitoring")
    
    def _process_waiting_queue(self, pool_id: str):
        """Process waiting queue for a pool."""
        pool = self._pools[pool_id]
        
        while pool.waiting_queue and pool.available_capacity > 0:
            worker_id, request_time = pool.waiting_queue.pop(0)
            
            # Check if request hasn't timed out (implement timeout logic if needed)
            resource_id = f"{pool_id}_resource_{len(pool.allocated_resources) + 1}"
            pool.allocated_resources[resource_id] = worker_id
            pool.available_capacity -= 1
            
            self.logger.debug(f"Processed waiting queue: allocated {resource_id} to {worker_id}")
    
    def _health_monitor_loop(self):
        """Health monitoring loop."""
        while not self._stop_monitoring.wait(self._health_monitor_interval):
            try:
                self._check_pool_health()
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
    
    def _check_pool_health(self):
        """Check health of all pools."""
        for pool_id, pool in self._pools.items():
            try:
                # Simple health check based on utilization and queue length
                utilization = (pool.total_capacity - pool.available_capacity) / pool.total_capacity
                queue_pressure = len(pool.waiting_queue) / max(pool.total_capacity, 1)
                
                if utilization > 0.9 or queue_pressure > 0.5:
                    pool.health_status = "degraded"
                elif utilization > 0.95 or queue_pressure > 1.0:
                    pool.health_status = "unhealthy"
                else:
                    pool.health_status = "healthy"
                
            except Exception as e:
                self.logger.error(f"Error checking health for pool {pool_id}: {e}")
                pool.health_status = "unknown"


class TestDistributionManager:
    """Manages intelligent test distribution across workers."""
    
    def __init__(self):
        self._workers: Dict[str, WorkerNode] = {}
        self._test_groups: Dict[str, TestGroup] = {}
        self._distribution_strategies: Dict[str, Callable] = {}
        self._assignment_queue = queue.PriorityQueue()
        self._execution_history: Dict[str, List[float]] = defaultdict(list)  # test_id -> durations
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Register default distribution strategies
        self._register_default_strategies()
    
    def register_worker(self, worker_id: str, worker_type: str, capabilities: List[str] = None,
                       max_capacity: int = 1, metadata: Dict[str, Any] = None) -> str:
        """Register a worker node."""
        worker = WorkerNode(
            worker_id=worker_id,
            worker_type=worker_type,
            capabilities=capabilities or [],
            max_capacity=max_capacity,
            last_heartbeat=datetime.now(),
            metadata=metadata or {}
        )
        
        self._workers[worker_id] = worker
        self.logger.info(f"Registered worker: {worker_id} with capabilities {capabilities}")
        return worker_id
    
    def create_test_group(self, group_id: str, group_name: str, test_ids: List[str],
                         group_type: str = "functional", priority: int = 1,
                         estimated_duration: float = None, required_capabilities: List[str] = None) -> str:
        """Create a test group for distribution."""
        group = TestGroup(
            group_id=group_id,
            group_name=group_name,
            test_ids=test_ids,
            group_type=group_type,
            priority=priority,
            estimated_duration=estimated_duration,
            required_capabilities=required_capabilities or []
        )
        
        self._test_groups[group_id] = group
        self.logger.info(f"Created test group: {group_name} with {len(test_ids)} tests")
        return group_id
    
    def distribute_tests(self, strategy: str = "load_balanced") -> Dict[str, List[str]]:
        """Distribute tests to workers using specified strategy."""
        if strategy not in self._distribution_strategies:
            raise ValueError(f"Unknown distribution strategy: {strategy}")
        
        distribution_func = self._distribution_strategies[strategy]
        distribution = distribution_func()
        
        # Update worker assignments
        for worker_id, test_ids in distribution.items():
            if worker_id in self._workers:
                self._workers[worker_id].assigned_tests = test_ids
                self._workers[worker_id].current_load = len(test_ids)
        
        self.logger.info(f"Distributed tests using {strategy} strategy")
        return distribution
    
    def update_worker_heartbeat(self, worker_id: str, performance_metrics: Dict[str, float] = None):
        """Update worker heartbeat and performance metrics."""
        if worker_id in self._workers:
            worker = self._workers[worker_id]
            worker.last_heartbeat = datetime.now()
            
            if performance_metrics:
                worker.performance_metrics.update(performance_metrics)
                # Update health score based on performance
                worker.health_score = self._calculate_health_score(worker)
    
    def get_optimal_worker(self, test_id: str, required_capabilities: List[str] = None) -> Optional[str]:
        """Get the optimal worker for a specific test."""
        available_workers = []
        
        for worker_id, worker in self._workers.items():
            # Check if worker is healthy and has capacity
            if (worker.health_score > 0.5 and 
                worker.current_load < worker.max_capacity):
                
                # Check capabilities
                if required_capabilities:
                    if not all(cap in worker.capabilities for cap in required_capabilities):
                        continue
                
                available_workers.append((worker_id, worker))
        
        if not available_workers:
            return None
        
        # Select worker with lowest load and highest health score
        best_worker = min(available_workers, 
                         key=lambda x: (x[1].current_load, -x[1].health_score))
        
        return best_worker[0]
    
    def record_test_completion(self, test_id: str, worker_id: str, duration: float, success: bool):
        """Record test completion for optimization."""
        self._execution_history[test_id].append(duration)
        
        # Keep only last 10 executions
        if len(self._execution_history[test_id]) > 10:
            self._execution_history[test_id] = self._execution_history[test_id][-10:]
        
        # Update worker metrics
        if worker_id in self._workers:
            worker = self._workers[worker_id]
            worker.current_load = max(0, worker.current_load - 1)
            
            # Update performance metrics
            if 'average_duration' not in worker.performance_metrics:
                worker.performance_metrics['average_duration'] = duration
            else:
                # Running average
                current_avg = worker.performance_metrics['average_duration']
                worker.performance_metrics['average_duration'] = (current_avg + duration) / 2
            
            if 'success_rate' not in worker.performance_metrics:
                worker.performance_metrics['success_rate'] = 1.0 if success else 0.0
            else:
                # Simple running average (could be improved with proper tracking)
                current_rate = worker.performance_metrics['success_rate']
                new_rate = 1.0 if success else 0.0
                worker.performance_metrics['success_rate'] = (current_rate + new_rate) / 2
    
    def get_estimated_duration(self, test_id: str) -> float:
        """Get estimated duration for a test."""
        if test_id in self._execution_history and self._execution_history[test_id]:
            return statistics.mean(self._execution_history[test_id])
        return 60.0  # Default 1 minute
    
    def _register_default_strategies(self):
        """Register default distribution strategies."""
        self._distribution_strategies['round_robin'] = self._round_robin_distribution
        self._distribution_strategies['load_balanced'] = self._load_balanced_distribution
        self._distribution_strategies['capability_based'] = self._capability_based_distribution
        self._distribution_strategies['duration_optimized'] = self._duration_optimized_distribution
    
    def _round_robin_distribution(self) -> Dict[str, List[str]]:
        """Round-robin distribution strategy."""
        distribution = {worker_id: [] for worker_id in self._workers.keys()}
        
        all_tests = []
        for group in self._test_groups.values():
            all_tests.extend(group.test_ids)
        
        worker_ids = list(self._workers.keys())
        for i, test_id in enumerate(all_tests):
            worker_id = worker_ids[i % len(worker_ids)]
            distribution[worker_id].append(test_id)
        
        return distribution
    
    def _load_balanced_distribution(self) -> Dict[str, List[str]]:
        """Load-balanced distribution strategy."""
        distribution = {worker_id: [] for worker_id in self._workers.keys()}
        
        # Get all tests sorted by estimated duration (longest first)
        all_tests = []
        for group in self._test_groups.values():
            for test_id in group.test_ids:
                duration = self.get_estimated_duration(test_id)
                all_tests.append((test_id, duration))
        
        all_tests.sort(key=lambda x: x[1], reverse=True)
        
        # Assign tests to workers with least current load
        worker_loads = {worker_id: 0 for worker_id in self._workers.keys()}
        
        for test_id, duration in all_tests:
            # Find worker with minimum load
            min_worker = min(worker_loads.keys(), key=lambda w: worker_loads[w])
            distribution[min_worker].append(test_id)
            worker_loads[min_worker] += duration
        
        return distribution
    
    def _capability_based_distribution(self) -> Dict[str, List[str]]:
        """Capability-based distribution strategy."""
        distribution = {worker_id: [] for worker_id in self._workers.keys()}
        
        for group in self._test_groups.values():
            suitable_workers = []
            
            for worker_id, worker in self._workers.items():
                if all(cap in worker.capabilities for cap in group.required_capabilities):
                    suitable_workers.append(worker_id)
            
            if suitable_workers:
                # Distribute among suitable workers using round-robin
                for i, test_id in enumerate(group.test_ids):
                    worker_id = suitable_workers[i % len(suitable_workers)]
                    distribution[worker_id].append(test_id)
            else:
                # Fall back to any available worker
                worker_ids = list(self._workers.keys())
                for i, test_id in enumerate(group.test_ids):
                    worker_id = worker_ids[i % len(worker_ids)]
                    distribution[worker_id].append(test_id)
        
        return distribution
    
    def _duration_optimized_distribution(self) -> Dict[str, List[str]]:
        """Duration-optimized distribution strategy."""
        # This is a simplified version of bin packing algorithm
        return self._load_balanced_distribution()  # Reuse load balanced for now
    
    def _calculate_health_score(self, worker: WorkerNode) -> float:
        """Calculate health score for a worker."""
        score = 1.0
        
        # Penalize for high load
        if worker.current_load > worker.max_capacity * 0.8:
            score *= 0.8
        
        # Consider success rate
        if 'success_rate' in worker.performance_metrics:
            score *= worker.performance_metrics['success_rate']
        
        # Consider response time
        if 'average_duration' in worker.performance_metrics:
            # Normalize duration (assuming 60s is baseline)
            duration_factor = min(60.0 / worker.performance_metrics['average_duration'], 1.0)
            score *= duration_factor
        
        # Check last heartbeat
        if worker.last_heartbeat:
            time_since_heartbeat = (datetime.now() - worker.last_heartbeat).total_seconds()
            if time_since_heartbeat > 60:  # 1 minute
                score *= 0.5
        
        return max(0.0, min(1.0, score))


class ParallelReportingManager:
    """Manages thread-safe reporting and metrics for parallel execution."""
    
    def __init__(self):
        self._execution_metrics: Dict[str, ParallelExecutionMetrics] = {}
        self._real_time_data = defaultdict(dict)
        self._report_queue = queue.Queue()
        self._aggregated_reports: Dict[str, Dict[str, Any]] = {}
        self._metrics_lock = threading.RLock()
        self._report_callbacks: List[Callable] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Start background processing
        self._processing_thread = threading.Thread(target=self._process_reports)
        self._processing_thread.daemon = True
        self._processing_thread.start()
    
    def start_execution_tracking(self, execution_id: str, total_tests: int, worker_count: int) -> str:
        """Start tracking a parallel execution."""
        with self._metrics_lock:
            metrics = ParallelExecutionMetrics(
                execution_id=execution_id,
                start_time=datetime.now(),
                total_tests=total_tests,
                worker_count=worker_count
            )
            
            self._execution_metrics[execution_id] = metrics
            self.logger.info(f"Started execution tracking: {execution_id}")
            return execution_id
    
    def report_test_completion(self, execution_id: str, test_id: str, worker_id: str,
                             success: bool, duration: float, metadata: Dict[str, Any] = None):
        """Report completion of a test (thread-safe)."""
        report_data = {
            'type': 'test_completion',
            'execution_id': execution_id,
            'test_id': test_id,
            'worker_id': worker_id,
            'success': success,
            'duration': duration,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        self._report_queue.put(report_data)
    
    def report_worker_status(self, execution_id: str, worker_id: str, status: str,
                           current_test: str = None, metadata: Dict[str, Any] = None):
        """Report worker status (thread-safe)."""
        report_data = {
            'type': 'worker_status',
            'execution_id': execution_id,
            'worker_id': worker_id,
            'status': status,
            'current_test': current_test,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        self._report_queue.put(report_data)
    
    def get_real_time_metrics(self, execution_id: str) -> Dict[str, Any]:
        """Get real-time execution metrics."""
        with self._metrics_lock:
            if execution_id not in self._execution_metrics:
                return {}
            
            metrics = self._execution_metrics[execution_id]
            real_time_data = self._real_time_data[execution_id]
            
            current_time = datetime.now()
            elapsed_time = (current_time - metrics.start_time).total_seconds()
            
            # Calculate throughput
            tests_per_second = metrics.completed_tests / max(elapsed_time, 1)
            
            # Calculate ETA
            remaining_tests = metrics.total_tests - metrics.completed_tests
            eta_seconds = remaining_tests / max(tests_per_second, 0.01)
            
            return {
                'execution_id': execution_id,
                'start_time': metrics.start_time.isoformat(),
                'elapsed_time': elapsed_time,
                'total_tests': metrics.total_tests,
                'completed_tests': metrics.completed_tests,
                'failed_tests': metrics.failed_tests,
                'success_rate': (metrics.completed_tests - metrics.failed_tests) / max(metrics.completed_tests, 1) * 100,
                'progress_percentage': metrics.completed_tests / metrics.total_tests * 100,
                'tests_per_second': tests_per_second,
                'eta_seconds': eta_seconds,
                'worker_count': metrics.worker_count,
                'average_test_duration': metrics.average_test_duration,
                'worker_status': real_time_data.get('worker_status', {}),
                'resource_utilization': metrics.resource_utilization
            }
    
    def generate_consolidated_report(self, execution_id: str) -> Dict[str, Any]:
        """Generate consolidated report for a parallel execution."""
        with self._metrics_lock:
            if execution_id not in self._execution_metrics:
                return {}
            
            metrics = self._execution_metrics[execution_id]
            
            if not metrics.end_time:
                metrics.end_time = datetime.now()
                metrics.total_execution_time = (metrics.end_time - metrics.start_time).total_seconds()
            
            # Calculate detailed metrics
            success_rate = ((metrics.completed_tests - metrics.failed_tests) / 
                          max(metrics.completed_tests, 1) * 100)
            
            parallel_efficiency = (metrics.total_tests * metrics.average_test_duration) / \
                                (metrics.total_execution_time * metrics.worker_count) * 100
            
            report = {
                'execution_summary': {
                    'execution_id': execution_id,
                    'start_time': metrics.start_time.isoformat(),
                    'end_time': metrics.end_time.isoformat(),
                    'total_execution_time': metrics.total_execution_time,
                    'total_tests': metrics.total_tests,
                    'completed_tests': metrics.completed_tests,
                    'failed_tests': metrics.failed_tests,
                    'success_rate': success_rate,
                    'worker_count': metrics.worker_count
                },
                'performance_metrics': {
                    'average_test_duration': metrics.average_test_duration,
                    'tests_per_second': metrics.completed_tests / max(metrics.total_execution_time, 1),
                    'parallel_efficiency': parallel_efficiency,
                    'resource_utilization': metrics.resource_utilization,
                    'throughput_metrics': metrics.throughput_metrics
                },
                'worker_details': self._real_time_data[execution_id].get('worker_details', {}),
                'test_results': self._real_time_data[execution_id].get('test_results', []),
                'generation_time': datetime.now().isoformat()
            }
            
            self._aggregated_reports[execution_id] = report
            return report
    
    def add_report_callback(self, callback: Callable):
        """Add callback for real-time report updates."""
        self._report_callbacks.append(callback)
    
    def _process_reports(self):
        """Background thread to process reports."""
        while True:
            try:
                report_data = self._report_queue.get(timeout=1)
                self._handle_report(report_data)
                self._report_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing report: {e}")
    
    def _handle_report(self, report_data: Dict[str, Any]):
        """Handle individual report data."""
        report_type = report_data['type']
        execution_id = report_data['execution_id']
        
        with self._metrics_lock:
            if execution_id not in self._execution_metrics:
                return
            
            metrics = self._execution_metrics[execution_id]
            real_time_data = self._real_time_data[execution_id]
            
            if report_type == 'test_completion':
                metrics.completed_tests += 1
                
                if not report_data['success']:
                    metrics.failed_tests += 1
                
                # Update average duration
                duration = report_data['duration']
                if metrics.average_test_duration == 0:
                    metrics.average_test_duration = duration
                else:
                    # Running average
                    metrics.average_test_duration = (
                        (metrics.average_test_duration * (metrics.completed_tests - 1) + duration) /
                        metrics.completed_tests
                    )
                
                # Store test result
                if 'test_results' not in real_time_data:
                    real_time_data['test_results'] = []
                
                real_time_data['test_results'].append({
                    'test_id': report_data['test_id'],
                    'worker_id': report_data['worker_id'],
                    'success': report_data['success'],
                    'duration': duration,
                    'timestamp': report_data['timestamp'].isoformat()
                })
            
            elif report_type == 'worker_status':
                if 'worker_status' not in real_time_data:
                    real_time_data['worker_status'] = {}
                
                real_time_data['worker_status'][report_data['worker_id']] = {
                    'status': report_data['status'],
                    'current_test': report_data.get('current_test'),
                    'last_update': report_data['timestamp'].isoformat()
                }
        
        # Notify callbacks
        for callback in self._report_callbacks:
            try:
                callback(report_data)
            except Exception as e:
                self.logger.error(f"Error in report callback: {e}")


class ParallelTestManager:
    """Main parallel test manager orchestrating all isolation components."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize components
        self.lock_manager = ResourceLockManager()
        self.dependency_manager = TestDependencyManager()
        self.environment_manager = IsolatedEnvironmentManager(
            base_temp_dir=self.config.get('temp_dir')
        )
        self.quarantine_manager = TestQuarantineManager(
            config_path=self.config.get('quarantine_config')
        )
        
        # Initialize new components for Resource Management, Test Distribution, and Parallel Reporting
        self.resource_pool_manager = ResourcePoolManager()
        self.distribution_manager = TestDistributionManager()
        self.reporting_manager = ParallelReportingManager()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup cleanup and monitoring
        self._setup_cleanup_hooks()
        self.resource_pool_manager.start_health_monitoring()
    
    def register_test_resource(self, resource_id: str, resource_type: str, 
                              resource_path: str = None, exclusive: bool = True) -> str:
        """Register a test resource for locking."""
        resource = TestResource(
            resource_id=resource_id,
            resource_type=resource_type,
            resource_path=resource_path,
            is_exclusive=exclusive
        )
        
        return self.lock_manager.register_resource(resource)
    
    def add_test_dependency(self, dependent_test: str, dependency_test: str, 
                           dependency_type: str = 'before', timeout: float = None):
        """Add a test dependency."""
        dependency = TestDependency(
            dependent_test=dependent_test,
            dependency_test=dependency_test,
            dependency_type=dependency_type,
            timeout=timeout
        )
        
        self.dependency_manager.add_dependency(dependency)
    
    def create_worker_environment(self, worker_id: str, config: Dict[str, Any] = None) -> str:
        """Create an isolated environment for a worker."""
        return self.environment_manager.create_environment(worker_id, config)
    
    def can_execute_test(self, test_id: str, worker_id: str, required_resources: List[str] = None) -> bool:
        """Check if a test can be executed by a worker."""
        # Check quarantine status
        if self.quarantine_manager.is_test_quarantined(test_id):
            self.logger.debug(f"Test {test_id} is quarantined")
            return False
        
        # Check dependencies
        if not self.dependency_manager.can_execute_test(test_id):
            self.logger.debug(f"Test {test_id} has unmet dependencies")
            return False
        
        # Check resource availability
        if required_resources:
            for resource_id in required_resources:
                if self.lock_manager.is_locked(resource_id):
                    current_holder = self.lock_manager.get_lock_holder(resource_id)
                    if current_holder != worker_id:
                        self.logger.debug(f"Resource {resource_id} is locked by {current_holder}")
                        return False
        
        return True
    
    def execute_test_with_isolation(self, test_id: str, worker_id: str, 
                                  test_function: Callable, required_resources: List[str] = None,
                                  timeout: float = None) -> bool:
        """Execute a test with full isolation."""
        if not self.can_execute_test(test_id, worker_id, required_resources):
            return False
        
        # Acquire resources
        acquired_resources = []
        if required_resources:
            for resource_id in required_resources:
                if self.lock_manager.acquire_lock(resource_id, worker_id, timeout):
                    acquired_resources.append(resource_id)
                else:
                    # Release already acquired resources
                    for acquired_resource in acquired_resources:
                        self.lock_manager.release_lock(acquired_resource, worker_id)
                    return False
        
        # Mark test as started
        self.dependency_manager.mark_test_started(test_id)
        
        # Get worker environment
        environment = self.environment_manager.get_worker_environment(worker_id)
        
        success = False
        failure_reason = None
        
        try:
            # Execute test
            if environment:
                # Set environment variables
                old_env = {}
                for key, value in environment.environment_variables.items():
                    old_env[key] = os.environ.get(key)
                    os.environ[key] = value
                
                try:
                    success = test_function()
                finally:
                    # Restore environment variables
                    for key, value in old_env.items():
                        if value is None:
                            os.environ.pop(key, None)
                        else:
                            os.environ[key] = value
            else:
                success = test_function()
                
        except Exception as e:
            failure_reason = str(e)
            self.logger.error(f"Test {test_id} failed: {e}")
        
        finally:
            # Release resources
            for resource_id in acquired_resources:
                self.lock_manager.release_lock(resource_id, worker_id)
            
            # Mark test as completed
            self.dependency_manager.mark_test_completed(test_id, success)
            
            # Record test result for quarantine tracking
            self.quarantine_manager.record_test_result(
                test_id, test_id, success, failure_reason
            )
        
        return success
    
    def get_runnable_tests(self, available_tests: List[str]) -> List[str]:
        """Get tests that can currently be executed."""
        # Filter out quarantined tests
        non_quarantined = [
            test_id for test_id in available_tests 
            if not self.quarantine_manager.is_test_quarantined(test_id)
        ]
        
        # Get tests with satisfied dependencies
        return self.dependency_manager.get_runnable_tests(non_quarantined)
    
    def cleanup_worker(self, worker_id: str):
        """Clean up resources for a worker."""
        # Release any locks held by the worker
        lock_status = self.lock_manager.get_lock_status()
        for resource_id, status in lock_status['resources'].items():
            if status['locked_by'] == worker_id:
                self.lock_manager.release_lock(resource_id, worker_id)
        
        # Clean up worker environment
        environment = self.environment_manager.get_worker_environment(worker_id)
        if environment:
            self.environment_manager.cleanup_environment(environment.environment_id)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        return {
            'lock_manager': self.lock_manager.get_lock_status(),
            'dependency_manager': {
                'dependency_graph': self.dependency_manager.get_dependency_graph(),
                'circular_dependencies': self.dependency_manager.detect_circular_dependencies()
            },
            'environment_manager': {
                'active_environments': len(self.environment_manager._environments),
                'worker_mappings': len(self.environment_manager._worker_environments)
            },
            'quarantine_manager': {
                'quarantined_tests': len(self.quarantine_manager.get_quarantined_tests()),
                'total_tracked_tests': len(self.quarantine_manager._quarantined_tests)
            }
        }
    
    @contextmanager
    def isolated_test_execution(self, test_id: str, worker_id: str, 
                               required_resources: List[str] = None):
        """Context manager for isolated test execution."""
        # Acquire resources and setup
        acquired_resources = []
        if required_resources:
            for resource_id in required_resources:
                if self.lock_manager.acquire_lock(resource_id, worker_id):
                    acquired_resources.append(resource_id)
                else:
                    # Release already acquired resources
                    for acquired_resource in acquired_resources:
                        self.lock_manager.release_lock(acquired_resource, worker_id)
                    raise RuntimeError(f"Could not acquire required resources for {test_id}")
        
        self.dependency_manager.mark_test_started(test_id)
        
        try:
            yield
        finally:
            # Release resources
            for resource_id in acquired_resources:
                self.lock_manager.release_lock(resource_id, worker_id)
            
            # Mark as completed (caller should handle success/failure)
            self.dependency_manager.mark_test_completed(test_id, True)
    
    def execute_parallel_tests(self, tests: List[TestCase], parallel_config: Dict[str, Any] = None) -> ParallelExecutionMetrics:
        """Execute tests in parallel with full optimization."""
        config = parallel_config or {}
        max_workers = config.get('max_workers', min(4, len(tests)))
        
        self.logger.info(f"Starting parallel execution of {len(tests)} tests with {max_workers} workers")
        
        # Initialize resource pools
        self.resource_pool_manager.add_pool('selenium_drivers', max_workers * 2)
        self.resource_pool_manager.add_pool('test_data', max_workers * 3)
        self.resource_pool_manager.add_pool('temp_files', max_workers * 5)
        
        # Create worker nodes
        worker_nodes = []
        for i in range(max_workers):
            node = WorkerNode(id=f"worker_{i}", capacity=10, current_load=0)
            worker_nodes.append(node)
            self.resource_pool_manager.register_worker(node)
        
        # Distribute tests
        test_groups = self.distribution_manager.distribute_tests(tests, worker_nodes)
        
        start_time = time.time()
        execution_results = []
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit test groups to workers
                future_to_group = {}
                for group in test_groups:
                    future = executor.submit(self._execute_test_group, group)
                    future_to_group[future] = group
                
                # Collect results
                for future in as_completed(future_to_group):
                    group = future_to_group[future]
                    try:
                        result = future.result()
                        execution_results.extend(result)
                        self.reporting_manager.update_progress(group.worker_id, len(result))
                    except Exception as e:
                        self.logger.error(f"Worker {group.worker_id} failed: {e}")
                        # Mark tests as failed
                        failed_results = [{'test': test, 'status': 'failed', 'error': str(e)} for test in group.tests]
                        execution_results.extend(failed_results)
        
        finally:
            # Cleanup resources
            self.resource_pool_manager.cleanup_all_pools()
            end_time = time.time()
        
        # Generate execution metrics
        metrics = ParallelExecutionMetrics(
            total_tests=len(tests),
            passed_tests=len([r for r in execution_results if r.get('status') == 'passed']),
            failed_tests=len([r for r in execution_results if r.get('status') == 'failed']),
            execution_time=end_time - start_time,
            worker_count=max_workers,
            resource_efficiency=self.resource_pool_manager.calculate_efficiency(),
            load_balance_score=self.distribution_manager.calculate_balance_score(test_groups)
        )
        
        # Generate final report
        self.reporting_manager.generate_final_report(metrics, execution_results)
        
        self.logger.info(f"Parallel execution completed in {metrics.execution_time:.2f}s")
        return metrics
    
    def _execute_test_group(self, group: TestGroup) -> List[Dict[str, Any]]:
        """Execute a group of tests on a specific worker."""
        results = []
        worker_id = group.worker_id
        
        # Acquire resources for this worker
        driver_resource = self.resource_pool_manager.acquire_resource('selenium_drivers', worker_id)
        data_resource = self.resource_pool_manager.acquire_resource('test_data', worker_id)
        
        try:
            for test in group.tests:
                start_time = time.time()
                
                # Check quarantine status
                if self.quarantine_manager.is_test_quarantined(test.name):
                    results.append({
                        'test': test,
                        'status': 'quarantined',
                        'execution_time': 0,
                        'worker_id': worker_id
                    })
                    continue
                
                # Create isolated environment
                env_id = self.environment_manager.create_environment(worker_id)
                
                try:
                    # Check dependencies
                    if hasattr(test, 'dependencies'):
                        dep_status = self.dependency_manager.check_dependencies(test.dependencies)
                        if not dep_status.all_satisfied:
                            results.append({
                                'test': test,
                                'status': 'dependency_failed',
                                'error': f"Unsatisfied dependencies: {dep_status.unsatisfied}",
                                'execution_time': 0,
                                'worker_id': worker_id
                            })
                            continue
                    
                    # Acquire necessary locks
                    locks = []
                    if hasattr(test, 'required_resources'):
                        for resource in test.required_resources:
                            if self.lock_manager.acquire_lock(resource, worker_id):
                                locks.append(resource)
                    
                    try:
                        # Execute the test
                        test_result = self._run_single_test(test, worker_id)
                        execution_time = time.time() - start_time
                        
                        result = {
                            'test': test,
                            'status': 'passed' if test_result['success'] else 'failed',
                            'execution_time': execution_time,
                            'worker_id': worker_id,
                            'details': test_result
                        }
                        
                        # Check for quarantine conditions
                        if not test_result['success'] and test_result.get('should_quarantine'):
                            self.quarantine_manager.record_test_result(
                                test.name, test.name, False, test_result.get('failure_reason', 'Unknown failure')
                            )
                        
                        results.append(result)
                        
                    finally:
                        # Release locks
                        for resource in locks:
                            self.lock_manager.release_lock(resource, worker_id)
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    results.append({
                        'test': test,
                        'status': 'error',
                        'error': str(e),
                        'execution_time': execution_time,
                        'worker_id': worker_id
                    })
                    self.logger.error(f"Test {test.name} failed with error: {e}")
                
                finally:
                    # Cleanup environment
                    self.environment_manager.cleanup_environment(env_id)
        
        finally:
            # Release resources
            if driver_resource:
                self.resource_pool_manager.release_resource('selenium_drivers', driver_resource, worker_id)
            if data_resource:
                self.resource_pool_manager.release_resource('test_data', data_resource, worker_id)
        
        return results
    
    def _run_single_test(self, test: TestCase, worker_id: str) -> Dict[str, Any]:
        """Run a single test case."""
        try:
            # This would be implemented based on your specific test framework
            # For now, returning a mock result
            result = {
                'success': True,
                'output': f"Test {test.name} executed successfully on worker {worker_id}",
                'worker_id': worker_id
            }
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'should_quarantine': True,
                'failure_reason': str(e)
            }
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """Get current execution metrics from all managers."""
        return {
            'resource_pools': self.resource_pool_manager.get_pool_status(),
            'test_distribution': self.distribution_manager.get_distribution_metrics(),
            'parallel_reporting': self.reporting_manager.get_reporting_status(),
            'isolation_status': self.get_status_report()
        }

    def _setup_cleanup_hooks(self):
        """Setup cleanup hooks for proper resource management."""
        import atexit
        
        def cleanup_all():
            try:
                self.environment_manager.cleanup_all_environments()
                self.logger.info("Parallel test manager cleanup completed")
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
        
        atexit.register(cleanup_all)


# Global parallel test manager instance
_global_parallel_manager = None


def get_parallel_manager(config: Dict[str, Any] = None) -> ParallelTestManager:
    """Get global parallel test manager instance."""
    global _global_parallel_manager
    if _global_parallel_manager is None:
        _global_parallel_manager = ParallelTestManager(config)
    return _global_parallel_manager


# Convenience functions
def register_test_resource(resource_id: str, resource_type: str, **kwargs) -> str:
    """Register a test resource using global manager."""
    return get_parallel_manager().register_test_resource(resource_id, resource_type, **kwargs)


def add_test_dependency(dependent_test: str, dependency_test: str, **kwargs):
    """Add test dependency using global manager."""
    return get_parallel_manager().add_test_dependency(dependent_test, dependency_test, **kwargs)


def execute_test_isolated(test_id: str, worker_id: str, test_function: Callable, **kwargs) -> bool:
    """Execute test with isolation using global manager."""
    return get_parallel_manager().execute_test_with_isolation(test_id, worker_id, test_function, **kwargs)


def cleanup_worker(worker_id: str):
    """Cleanup worker using global manager."""
    return get_parallel_manager().cleanup_worker(worker_id)

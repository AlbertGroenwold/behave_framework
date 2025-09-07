"""
Resource Cleanup Module for Central Quality Hub Framework

This module provides comprehensive resource cleanup capabilities including:
- Automatic resource cleanup
- Cleanup verification
- Resource leak detection
- Cleanup scheduling
- Cleanup monitoring
"""

import threading
import logging
import time
import weakref
import gc
import os
import psutil
import atexit
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from abc import ABC, abstractmethod
from enum import Enum
import traceback


class ResourceType(Enum):
    """Types of resources that can be managed"""
    FILE_HANDLE = "file_handle"
    NETWORK_CONNECTION = "network_connection"
    DATABASE_CONNECTION = "database_connection"
    WEBDRIVER = "webdriver"
    THREAD = "thread"
    MEMORY_BUFFER = "memory_buffer"
    TEMP_FILE = "temp_file"
    TEMP_DIRECTORY = "temp_directory"
    CUSTOM = "custom"


@dataclass
class ResourceInfo:
    """Information about a managed resource"""
    resource_id: str
    resource_type: ResourceType
    resource_ref: Any  # Weak reference or actual resource
    created_at: datetime
    last_accessed: datetime
    cleanup_function: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_critical: bool = False
    max_lifetime: Optional[float] = None  # seconds
    cleanup_attempts: int = 0
    max_cleanup_attempts: int = 3


@dataclass
class CleanupResult:
    """Result of cleanup operation"""
    resource_id: str
    success: bool
    error: Optional[str] = None
    cleanup_time: float = 0.0
    attempts: int = 1


class ResourceLeakDetector:
    """Detect potential resource leaks"""
    
    def __init__(self, check_interval: int = 300):  # 5 minutes
        self.check_interval = check_interval
        self.baseline_metrics = {}
        self.current_metrics = {}
        self.detected_leaks = []
        self.monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_monitoring(self):
        """Start leak detection monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self._take_baseline_metrics()
        
        self.monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Resource leak monitoring started")
    
    def stop_monitoring(self):
        """Stop leak detection monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("Resource leak monitoring stopped")
    
    def _take_baseline_metrics(self):
        """Take baseline resource metrics"""
        self.baseline_metrics = self._get_system_metrics()
        self.logger.debug(f"Baseline metrics: {self.baseline_metrics}")
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics"""
        process = psutil.Process()
        
        metrics = {
            'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0,
            'connections': len(process.connections()) if hasattr(process, 'connections') else 0,
            'threads': process.num_threads(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'timestamp': datetime.now()
        }
        
        # Add file descriptor count for Unix systems
        try:
            if hasattr(os, 'listdir') and os.path.exists(f'/proc/{process.pid}/fd'):
                metrics['file_descriptors'] = len(os.listdir(f'/proc/{process.pid}/fd'))
        except (OSError, PermissionError):
            pass
        
        return metrics
    
    def _monitor_worker(self):
        """Background worker for leak detection"""
        while self.monitoring:
            try:
                self._check_for_leaks()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in leak detection: {e}")
    
    def _check_for_leaks(self):
        """Check for potential resource leaks"""
        self.current_metrics = self._get_system_metrics()
        
        # Compare with baseline
        leaks_detected = []
        
        for metric, current_value in self.current_metrics.items():
            if metric == 'timestamp':
                continue
                
            baseline_value = self.baseline_metrics.get(metric, 0)
            
            # Check for significant increases
            if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                if baseline_value > 0:
                    increase_ratio = (current_value - baseline_value) / baseline_value
                    if increase_ratio > 0.5:  # 50% increase
                        leaks_detected.append({
                            'metric': metric,
                            'baseline': baseline_value,
                            'current': current_value,
                            'increase_ratio': increase_ratio,
                            'detected_at': datetime.now()
                        })
        
        if leaks_detected:
            self.detected_leaks.extend(leaks_detected)
            self.logger.warning(f"Potential resource leaks detected: {leaks_detected}")
    
    def get_leak_report(self) -> Dict[str, Any]:
        """Get comprehensive leak detection report"""
        return {
            'monitoring_active': self.monitoring,
            'check_interval': self.check_interval,
            'baseline_metrics': self.baseline_metrics,
            'current_metrics': self.current_metrics,
            'detected_leaks': self.detected_leaks,
            'leak_count': len(self.detected_leaks)
        }


class ResourceCleanupScheduler:
    """Schedule and manage resource cleanup operations"""
    
    def __init__(self):
        self.scheduled_tasks = {}
        self.recurring_tasks = {}
        self.scheduler_thread = None
        self.running = False
        self.lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start(self):
        """Start the cleanup scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Resource cleanup scheduler started")
    
    def stop(self):
        """Stop the cleanup scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        
        self.logger.info("Resource cleanup scheduler stopped")
    
    def schedule_cleanup(self, task_id: str, cleanup_function: Callable, 
                        delay_seconds: float, description: str = ""):
        """Schedule a one-time cleanup task"""
        execute_at = datetime.now() + timedelta(seconds=delay_seconds)
        
        with self.lock:
            self.scheduled_tasks[task_id] = {
                'function': cleanup_function,
                'execute_at': execute_at,
                'description': description,
                'scheduled_at': datetime.now()
            }
        
        self.logger.info(f"Scheduled cleanup task {task_id} for {execute_at}")
    
    def schedule_recurring_cleanup(self, task_id: str, cleanup_function: Callable,
                                 interval_seconds: float, description: str = ""):
        """Schedule a recurring cleanup task"""
        next_execution = datetime.now() + timedelta(seconds=interval_seconds)
        
        with self.lock:
            self.recurring_tasks[task_id] = {
                'function': cleanup_function,
                'interval_seconds': interval_seconds,
                'next_execution': next_execution,
                'description': description,
                'execution_count': 0,
                'last_execution': None
            }
        
        self.logger.info(f"Scheduled recurring cleanup task {task_id} with {interval_seconds}s interval")
    
    def cancel_task(self, task_id: str):
        """Cancel a scheduled task"""
        with self.lock:
            removed = False
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]
                removed = True
            if task_id in self.recurring_tasks:
                del self.recurring_tasks[task_id]
                removed = True
        
        if removed:
            self.logger.info(f"Cancelled cleanup task {task_id}")
    
    def _scheduler_worker(self):
        """Background worker for executing scheduled tasks"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Execute one-time tasks
                with self.lock:
                    tasks_to_remove = []
                    for task_id, task_info in self.scheduled_tasks.items():
                        if current_time >= task_info['execute_at']:
                            try:
                                task_info['function']()
                                self.logger.info(f"Executed scheduled task {task_id}")
                            except Exception as e:
                                self.logger.error(f"Error executing task {task_id}: {e}")
                            tasks_to_remove.append(task_id)
                    
                    for task_id in tasks_to_remove:
                        del self.scheduled_tasks[task_id]
                
                # Execute recurring tasks
                with self.lock:
                    for task_id, task_info in self.recurring_tasks.items():
                        if current_time >= task_info['next_execution']:
                            try:
                                task_info['function']()
                                task_info['execution_count'] += 1
                                task_info['last_execution'] = current_time
                                task_info['next_execution'] = current_time + timedelta(
                                    seconds=task_info['interval_seconds']
                                )
                                self.logger.debug(f"Executed recurring task {task_id}")
                            except Exception as e:
                                self.logger.error(f"Error executing recurring task {task_id}: {e}")
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in scheduler worker: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        with self.lock:
            return {
                'running': self.running,
                'scheduled_tasks': len(self.scheduled_tasks),
                'recurring_tasks': len(self.recurring_tasks),
                'task_details': {
                    'scheduled': {
                        task_id: {
                            'execute_at': info['execute_at'].isoformat(),
                            'description': info['description']
                        } for task_id, info in self.scheduled_tasks.items()
                    },
                    'recurring': {
                        task_id: {
                            'interval_seconds': info['interval_seconds'],
                            'next_execution': info['next_execution'].isoformat(),
                            'execution_count': info['execution_count'],
                            'description': info['description']
                        } for task_id, info in self.recurring_tasks.items()
                    }
                }
            }


class ResourceCleanupManager:
    """Main resource cleanup manager"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.resources: Dict[str, ResourceInfo] = {}
        self.cleanup_history: List[CleanupResult] = []
        self.lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.leak_detector = ResourceLeakDetector(
            check_interval=self.config.get('leak_check_interval', 300)
        )
        self.scheduler = ResourceCleanupScheduler()
        
        # Configuration
        self.auto_cleanup_enabled = self.config.get('auto_cleanup', True)
        self.cleanup_interval = self.config.get('cleanup_interval', 60)
        self.max_resource_lifetime = self.config.get('max_resource_lifetime', 3600)
        
        # Setup automatic cleanup
        self._setup_automatic_cleanup()
    
    def _setup_automatic_cleanup(self):
        """Setup automatic cleanup processes"""
        if self.auto_cleanup_enabled:
            self.scheduler.start()
            
            # Schedule periodic cleanup
            self.scheduler.schedule_recurring_cleanup(
                'periodic_cleanup',
                self._periodic_cleanup,
                self.cleanup_interval,
                'Periodic resource cleanup'
            )
            
            # Schedule leak detection
            if self.config.get('enable_leak_detection', True):
                self.leak_detector.start_monitoring()
        
        # Setup exit cleanup
        atexit.register(self._exit_cleanup)
    
    def register_resource(self, resource_id: str, resource: Any, 
                         resource_type: ResourceType, cleanup_function: Callable = None,
                         is_critical: bool = False, max_lifetime: float = None,
                         metadata: Dict[str, Any] = None) -> str:
        """Register a resource for automatic cleanup"""
        
        # Create weak reference for non-critical resources
        if not is_critical and hasattr(resource, '__weakref__'):
            resource_ref = weakref.ref(resource)
        else:
            resource_ref = resource
        
        resource_info = ResourceInfo(
            resource_id=resource_id,
            resource_type=resource_type,
            resource_ref=resource_ref,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            cleanup_function=cleanup_function,
            metadata=metadata or {},
            is_critical=is_critical,
            max_lifetime=max_lifetime or self.max_resource_lifetime
        )
        
        with self.lock:
            self.resources[resource_id] = resource_info
        
        self.logger.debug(f"Registered resource {resource_id} ({resource_type.value})")
        return resource_id
    
    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource"""
        with self.lock:
            if resource_id in self.resources:
                del self.resources[resource_id]
                self.logger.debug(f"Unregistered resource {resource_id}")
                return True
        return False
    
    def cleanup_resource(self, resource_id: str, force: bool = False) -> CleanupResult:
        """Cleanup a specific resource"""
        start_time = time.time()
        
        with self.lock:
            if resource_id not in self.resources:
                return CleanupResult(resource_id, False, "Resource not found")
            
            resource_info = self.resources[resource_id]
            resource_info.cleanup_attempts += 1
            
            try:
                # Get actual resource
                if isinstance(resource_info.resource_ref, weakref.ref):
                    resource = resource_info.resource_ref()
                    if resource is None and not force:
                        # Resource already garbage collected
                        del self.resources[resource_id]
                        return CleanupResult(resource_id, True, None, time.time() - start_time)
                else:
                    resource = resource_info.resource_ref
                
                # Call cleanup function
                if resource_info.cleanup_function:
                    resource_info.cleanup_function(resource)
                else:
                    # Default cleanup based on resource type
                    self._default_cleanup(resource, resource_info.resource_type)
                
                # Remove from registry
                del self.resources[resource_id]
                
                cleanup_time = time.time() - start_time
                result = CleanupResult(resource_id, True, None, cleanup_time, resource_info.cleanup_attempts)
                self.cleanup_history.append(result)
                
                self.logger.info(f"Successfully cleaned up resource {resource_id}")
                return result
                
            except Exception as e:
                error_msg = str(e)
                cleanup_time = time.time() - start_time
                result = CleanupResult(resource_id, False, error_msg, cleanup_time, resource_info.cleanup_attempts)
                self.cleanup_history.append(result)
                
                self.logger.error(f"Failed to cleanup resource {resource_id}: {error_msg}")
                
                # Remove if max attempts reached
                if resource_info.cleanup_attempts >= resource_info.max_cleanup_attempts:
                    self.logger.warning(f"Removing resource {resource_id} after {resource_info.cleanup_attempts} failed attempts")
                    del self.resources[resource_id]
                
                return result
    
    def _default_cleanup(self, resource: Any, resource_type: ResourceType):
        """Default cleanup methods for different resource types"""
        if resource_type == ResourceType.FILE_HANDLE:
            if hasattr(resource, 'close'):
                resource.close()
        elif resource_type == ResourceType.WEBDRIVER:
            if hasattr(resource, 'quit'):
                resource.quit()
        elif resource_type == ResourceType.DATABASE_CONNECTION:
            if hasattr(resource, 'close'):
                resource.close()
        elif resource_type == ResourceType.NETWORK_CONNECTION:
            if hasattr(resource, 'close'):
                resource.close()
        elif resource_type == ResourceType.THREAD:
            if hasattr(resource, 'join') and resource.is_alive():
                resource.join(timeout=5)
        elif resource_type == ResourceType.TEMP_FILE:
            if isinstance(resource, str) and os.path.exists(resource):
                os.remove(resource)
        elif resource_type == ResourceType.TEMP_DIRECTORY:
            if isinstance(resource, str) and os.path.exists(resource):
                import shutil
                shutil.rmtree(resource)
    
    def cleanup_all_resources(self, resource_type: ResourceType = None) -> Dict[str, CleanupResult]:
        """Cleanup all resources or resources of specific type"""
        results = {}
        
        with self.lock:
            resource_ids = list(self.resources.keys())
        
        for resource_id in resource_ids:
            resource_info = self.resources.get(resource_id)
            if resource_info and (resource_type is None or resource_info.resource_type == resource_type):
                results[resource_id] = self.cleanup_resource(resource_id)
        
        return results
    
    def _periodic_cleanup(self):
        """Periodic cleanup of expired resources"""
        current_time = datetime.now()
        expired_resources = []
        
        with self.lock:
            for resource_id, resource_info in self.resources.items():
                # Check if resource has expired
                age = (current_time - resource_info.created_at).total_seconds()
                if age > resource_info.max_lifetime:
                    expired_resources.append(resource_id)
                
                # Check if weak reference is dead
                if isinstance(resource_info.resource_ref, weakref.ref) and resource_info.resource_ref() is None:
                    expired_resources.append(resource_id)
        
        # Cleanup expired resources
        for resource_id in expired_resources:
            self.cleanup_resource(resource_id)
        
        if expired_resources:
            self.logger.info(f"Cleaned up {len(expired_resources)} expired resources")
    
    def _exit_cleanup(self):
        """Cleanup all resources on exit"""
        self.logger.info("Performing exit cleanup")
        
        # Stop scheduler and leak detector
        self.scheduler.stop()
        self.leak_detector.stop_monitoring()
        
        # Cleanup all remaining resources
        results = self.cleanup_all_resources()
        success_count = sum(1 for result in results.values() if result.success)
        
        self.logger.info(f"Exit cleanup completed: {success_count}/{len(results)} resources cleaned up successfully")
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get status of all registered resources"""
        with self.lock:
            status = {
                'total_resources': len(self.resources),
                'resources_by_type': {},
                'cleanup_history_count': len(self.cleanup_history),
                'recent_cleanups': self.cleanup_history[-10:] if self.cleanup_history else []
            }
            
            # Count by type
            for resource_info in self.resources.values():
                resource_type = resource_info.resource_type.value
                status['resources_by_type'][resource_type] = status['resources_by_type'].get(resource_type, 0) + 1
            
            return status
    
    def verify_cleanup(self, resource_id: str) -> Dict[str, Any]:
        """Verify that a resource has been properly cleaned up"""
        verification = {
            'resource_id': resource_id,
            'still_registered': resource_id in self.resources,
            'cleanup_history': [],
            'verification_time': datetime.now().isoformat()
        }
        
        # Check cleanup history
        for result in self.cleanup_history:
            if result.resource_id == resource_id:
                verification['cleanup_history'].append({
                    'success': result.success,
                    'error': result.error,
                    'cleanup_time': result.cleanup_time,
                    'attempts': result.attempts
                })
        
        return verification
    
    @contextmanager
    def managed_resource(self, resource: Any, resource_type: ResourceType,
                        cleanup_function: Callable = None, **kwargs):
        """Context manager for automatic resource management"""
        resource_id = f"{resource_type.value}_{id(resource)}_{int(time.time())}"
        
        try:
            self.register_resource(resource_id, resource, resource_type, cleanup_function, **kwargs)
            yield resource
        finally:
            self.cleanup_resource(resource_id)


# Global instance
_global_cleanup_manager = None


def get_cleanup_manager(config: Dict[str, Any] = None) -> ResourceCleanupManager:
    """Get global cleanup manager instance"""
    global _global_cleanup_manager
    if _global_cleanup_manager is None:
        _global_cleanup_manager = ResourceCleanupManager(config)
    return _global_cleanup_manager


# Convenience functions
def register_for_cleanup(resource: Any, resource_type: ResourceType, 
                        cleanup_function: Callable = None, **kwargs) -> str:
    """Register resource for automatic cleanup"""
    resource_id = f"{resource_type.value}_{id(resource)}_{int(time.time())}"
    get_cleanup_manager().register_resource(resource_id, resource, resource_type, cleanup_function, **kwargs)
    return resource_id


def cleanup_resource_by_id(resource_id: str) -> CleanupResult:
    """Cleanup specific resource by ID"""
    return get_cleanup_manager().cleanup_resource(resource_id)


def cleanup_all_of_type(resource_type: ResourceType) -> Dict[str, CleanupResult]:
    """Cleanup all resources of specific type"""
    return get_cleanup_manager().cleanup_all_resources(resource_type)


@contextmanager
def auto_cleanup_resource(resource: Any, resource_type: ResourceType, 
                         cleanup_function: Callable = None):
    """Context manager for automatic resource cleanup"""
    with get_cleanup_manager().managed_resource(resource, resource_type, cleanup_function):
        yield resource


def get_resource_status() -> Dict[str, Any]:
    """Get status of all managed resources"""
    return get_cleanup_manager().get_resource_status()


def start_leak_detection():
    """Start resource leak detection"""
    get_cleanup_manager().leak_detector.start_monitoring()


def get_leak_report() -> Dict[str, Any]:
    """Get resource leak detection report"""
    return get_cleanup_manager().leak_detector.get_leak_report()

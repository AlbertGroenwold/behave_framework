"""
Memory Profiler Module for Central Quality Hub Framework

This module provides comprehensive memory profiling capabilities including:
- Memory usage tracking
- Memory leak detection  
- Memory usage reports
- Memory optimization suggestions
- Real-time memory monitoring
"""

import psutil
import gc
import threading
import time
import logging
import json
import tracemalloc
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps
import weakref
import sys
import os


@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a point in time"""
    timestamp: datetime
    process_memory_mb: float
    system_memory_mb: float
    memory_percent: float
    gc_objects: int
    tracemalloc_current: int
    tracemalloc_peak: int
    thread_count: int
    file_descriptors: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass 
class MemoryLeak:
    """Detected memory leak information"""
    object_type: str
    count_increase: int
    memory_increase_mb: float
    detection_time: datetime
    stack_trace: List[str]
    severity: str  # 'low', 'medium', 'high', 'critical'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['detection_time'] = self.detection_time.isoformat()
        return data


@dataclass
class MemoryOptimization:
    """Memory optimization suggestion"""
    category: str
    description: str
    potential_savings_mb: float
    priority: str  # 'low', 'medium', 'high'
    action_items: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


class MemoryTracker:
    """Track memory usage for specific objects or code blocks"""
    
    def __init__(self, name: str):
        self.name = name
        self.snapshots: List[MemorySnapshot] = []
        self.start_memory = None
        self.peak_memory = 0
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_tracking(self):
        """Start memory tracking"""
        self.start_memory = self._get_current_memory()
        self.snapshots.append(self._create_snapshot())
        self.logger.debug(f"Started memory tracking for: {self.name}")
    
    def stop_tracking(self) -> Dict[str, Any]:
        """Stop tracking and return summary"""
        if not self.start_memory:
            return {}
        
        end_memory = self._get_current_memory()
        end_snapshot = self._create_snapshot()
        self.snapshots.append(end_snapshot)
        
        summary = {
            'name': self.name,
            'start_memory_mb': self.start_memory,
            'end_memory_mb': end_memory,
            'memory_change_mb': end_memory - self.start_memory,
            'peak_memory_mb': self.peak_memory,
            'duration_seconds': (end_snapshot.timestamp - self.snapshots[0].timestamp).total_seconds(),
            'snapshots_count': len(self.snapshots)
        }
        
        self.logger.info(f"Memory tracking completed for {self.name}: {summary}")
        return summary
    
    def take_snapshot(self):
        """Take a memory snapshot"""
        snapshot = self._create_snapshot()
        self.snapshots.append(snapshot)
        
        # Update peak memory
        if snapshot.process_memory_mb > self.peak_memory:
            self.peak_memory = snapshot.process_memory_mb
    
    def _get_current_memory(self) -> float:
        """Get current process memory in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def _create_snapshot(self) -> MemorySnapshot:
        """Create a memory snapshot"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Get system memory
        system_memory = psutil.virtual_memory()
        
        # Get tracemalloc info if available
        tracemalloc_current = 0
        tracemalloc_peak = 0
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc_current = current
            tracemalloc_peak = peak
        
        return MemorySnapshot(
            timestamp=datetime.now(),
            process_memory_mb=memory_info.rss / 1024 / 1024,
            system_memory_mb=system_memory.used / 1024 / 1024,
            memory_percent=process.memory_percent(),
            gc_objects=len(gc.get_objects()),
            tracemalloc_current=tracemalloc_current,
            tracemalloc_peak=tracemalloc_peak,
            thread_count=threading.active_count(),
            file_descriptors=len(process.open_files()) if hasattr(process, 'open_files') else 0
        )


class MemoryLeakDetector:
    """Detect memory leaks in the application"""
    
    def __init__(self, check_interval: int = 60, leak_threshold: float = 50.0):
        self.check_interval = check_interval
        self.leak_threshold = leak_threshold  # MB increase threshold
        self.baseline_snapshots: List[MemorySnapshot] = []
        self.detected_leaks: List[MemoryLeak] = []
        self.monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.object_counts = {}
    
    def start_monitoring(self):
        """Start memory leak monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        # Start tracemalloc for detailed tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        # Take baseline snapshot
        self._take_baseline_snapshot()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Memory leak monitoring started")
    
    def stop_monitoring(self):
        """Stop memory leak monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Memory leak monitoring stopped")
    
    def _take_baseline_snapshot(self):
        """Take baseline memory snapshot"""
        tracker = MemoryTracker("baseline")
        tracker.take_snapshot()
        self.baseline_snapshots.append(tracker.snapshots[0])
        
        # Record object counts
        self._record_object_counts()
    
    def _record_object_counts(self):
        """Record current object counts by type"""
        objects = gc.get_objects()
        counts = {}
        
        for obj in objects:
            obj_type = type(obj).__name__
            counts[obj_type] = counts.get(obj_type, 0) + 1
        
        self.object_counts[datetime.now()] = counts
    
    def _monitor_worker(self):
        """Background worker for memory monitoring"""
        while self.monitoring:
            try:
                self._check_for_leaks()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in memory monitoring: {e}")
    
    def _check_for_leaks(self):
        """Check for potential memory leaks"""
        if not self.baseline_snapshots:
            return
        
        # Take current snapshot
        tracker = MemoryTracker("leak_check")
        tracker.take_snapshot()
        current_snapshot = tracker.snapshots[0]
        
        # Compare with baseline
        baseline = self.baseline_snapshots[-1]
        memory_increase = current_snapshot.process_memory_mb - baseline.process_memory_mb
        
        if memory_increase > self.leak_threshold:
            # Record object counts
            self._record_object_counts()
            
            # Analyze object growth
            leak = self._analyze_object_growth(memory_increase)
            if leak:
                self.detected_leaks.append(leak)
                self.logger.warning(f"Memory leak detected: {leak.object_type}")
        
        # Update baseline (rolling window)
        if len(self.baseline_snapshots) > 10:
            self.baseline_snapshots.pop(0)
        self.baseline_snapshots.append(current_snapshot)
    
    def _analyze_object_growth(self, memory_increase: float) -> Optional[MemoryLeak]:
        """Analyze object count growth to identify leak source"""
        if len(self.object_counts) < 2:
            return None
        
        timestamps = sorted(self.object_counts.keys())
        latest = timestamps[-1]
        baseline = timestamps[0]
        
        latest_counts = self.object_counts[latest]
        baseline_counts = self.object_counts[baseline]
        
        # Find objects with significant growth
        max_growth = 0
        leak_type = "unknown"
        
        for obj_type in latest_counts:
            current_count = latest_counts[obj_type]
            baseline_count = baseline_counts.get(obj_type, 0)
            growth = current_count - baseline_count
            
            if growth > max_growth and growth > 100:  # Significant growth
                max_growth = growth
                leak_type = obj_type
        
        if max_growth > 0:
            # Get stack trace
            stack_trace = traceback.format_stack()
            
            # Determine severity
            if memory_increase > 200:
                severity = "critical"
            elif memory_increase > 100:
                severity = "high"
            elif memory_increase > 50:
                severity = "medium"
            else:
                severity = "low"
            
            return MemoryLeak(
                object_type=leak_type,
                count_increase=max_growth,
                memory_increase_mb=memory_increase,
                detection_time=datetime.now(),
                stack_trace=stack_trace,
                severity=severity
            )
        
        return None
    
    def get_leak_report(self) -> Dict[str, Any]:
        """Get comprehensive leak detection report"""
        return {
            'monitoring_active': self.monitoring,
            'check_interval': self.check_interval,
            'leak_threshold_mb': self.leak_threshold,
            'detected_leaks': [leak.to_dict() for leak in self.detected_leaks],
            'baseline_snapshots': len(self.baseline_snapshots),
            'total_memory_checks': len(self.object_counts)
        }


class MemoryOptimizer:
    """Provide memory optimization suggestions"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_memory_usage(self, snapshots: List[MemorySnapshot]) -> List[MemoryOptimization]:
        """Analyze memory usage and provide optimization suggestions"""
        optimizations = []
        
        if not snapshots:
            return optimizations
        
        # Analyze garbage collection
        optimizations.extend(self._analyze_gc_efficiency(snapshots))
        
        # Analyze memory growth patterns
        optimizations.extend(self._analyze_memory_growth(snapshots))
        
        # Analyze system resource usage
        optimizations.extend(self._analyze_system_resources(snapshots))
        
        # Sort by priority and potential savings
        optimizations.sort(key=lambda x: (x.priority, x.potential_savings_mb), reverse=True)
        
        return optimizations
    
    def _analyze_gc_efficiency(self, snapshots: List[MemorySnapshot]) -> List[MemoryOptimization]:
        """Analyze garbage collection efficiency"""
        optimizations = []
        
        if len(snapshots) < 2:
            return optimizations
        
        # Check object count growth
        object_growth = []
        for i in range(1, len(snapshots)):
            growth = snapshots[i].gc_objects - snapshots[i-1].gc_objects
            object_growth.append(growth)
        
        avg_growth = sum(object_growth) / len(object_growth)
        
        if avg_growth > 1000:  # High object creation rate
            optimizations.append(MemoryOptimization(
                category="Garbage Collection",
                description="High object creation rate detected. Consider object pooling or reducing object creation.",
                potential_savings_mb=avg_growth * 0.001,  # Estimate
                priority="medium",
                action_items=[
                    "Implement object pooling for frequently created objects",
                    "Review code for unnecessary object creation",
                    "Consider using generators instead of lists where appropriate",
                    "Explicitly call gc.collect() in memory-intensive operations"
                ]
            ))
        
        return optimizations
    
    def _analyze_memory_growth(self, snapshots: List[MemorySnapshot]) -> List[MemoryOptimization]:
        """Analyze memory growth patterns"""
        optimizations = []
        
        if len(snapshots) < 3:
            return optimizations
        
        # Calculate memory growth trend
        memory_values = [s.process_memory_mb for s in snapshots]
        growth_rate = (memory_values[-1] - memory_values[0]) / len(snapshots)
        
        if growth_rate > 5:  # 5MB per snapshot growth
            optimizations.append(MemoryOptimization(
                category="Memory Growth",
                description=f"Consistent memory growth detected ({growth_rate:.2f}MB per measurement). Potential memory leak.",
                potential_savings_mb=growth_rate * 10,  # Estimate
                priority="high",
                action_items=[
                    "Enable memory leak monitoring",
                    "Review code for circular references",
                    "Check for unclosed file handles or network connections",
                    "Implement proper cleanup in destructors",
                    "Use weak references where appropriate"
                ]
            ))
        
        # Check for memory spikes
        max_memory = max(memory_values)
        avg_memory = sum(memory_values) / len(memory_values)
        
        if max_memory > avg_memory * 1.5:  # 50% spike
            optimizations.append(MemoryOptimization(
                category="Memory Spikes",
                description=f"Memory spikes detected (peak: {max_memory:.2f}MB, avg: {avg_memory:.2f}MB)",
                potential_savings_mb=max_memory - avg_memory,
                priority="medium",
                action_items=[
                    "Implement streaming for large data processing",
                    "Use pagination for large datasets",
                    "Consider lazy loading for large objects",
                    "Implement data compression where appropriate"
                ]
            ))
        
        return optimizations
    
    def _analyze_system_resources(self, snapshots: List[MemorySnapshot]) -> List[MemoryOptimization]:
        """Analyze system resource usage"""
        optimizations = []
        
        if not snapshots:
            return optimizations
        
        latest = snapshots[-1]
        
        # Check high memory percentage usage
        if latest.memory_percent > 80:
            optimizations.append(MemoryOptimization(
                category="System Resources",
                description=f"High system memory usage: {latest.memory_percent:.1f}%",
                potential_savings_mb=latest.process_memory_mb * 0.3,
                priority="high",
                action_items=[
                    "Reduce memory footprint of the application",
                    "Implement memory limits and monitoring",
                    "Consider horizontal scaling",
                    "Optimize data structures and algorithms"
                ]
            ))
        
        # Check thread count
        if latest.thread_count > 50:
            optimizations.append(MemoryOptimization(
                category="Thread Management",
                description=f"High thread count: {latest.thread_count}",
                potential_savings_mb=latest.thread_count * 0.1,  # Rough estimate
                priority="medium",
                action_items=[
                    "Use thread pools instead of creating individual threads",
                    "Implement asynchronous programming patterns",
                    "Review thread lifecycle management",
                    "Consider using multiprocessing for CPU-bound tasks"
                ]
            ))
        
        return optimizations


class MemoryProfiler:
    """Main memory profiler class orchestrating all memory monitoring capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.trackers: Dict[str, MemoryTracker] = {}
        self.leak_detector = MemoryLeakDetector(
            check_interval=self.config.get('leak_check_interval', 60),
            leak_threshold=self.config.get('leak_threshold_mb', 50.0)
        )
        self.optimizer = MemoryOptimizer()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.global_snapshots: List[MemorySnapshot] = []
        self._monitoring = False
        self._monitor_thread = None
        
        # Setup automatic cleanup
        self._setup_cleanup_hooks()
    
    def start_profiling(self, enable_leak_detection: bool = True):
        """Start comprehensive memory profiling"""
        self.logger.info("Starting memory profiling")
        
        # Start global monitoring
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._global_monitor_worker, daemon=True)
        self._monitor_thread.start()
        
        # Start leak detection if enabled
        if enable_leak_detection:
            self.leak_detector.start_monitoring()
        
        self.logger.info("Memory profiling started")
    
    def stop_profiling(self) -> Dict[str, Any]:
        """Stop profiling and generate final report"""
        self.logger.info("Stopping memory profiling")
        
        # Stop global monitoring
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        # Stop leak detection
        self.leak_detector.stop_monitoring()
        
        # Generate final report
        report = self.generate_comprehensive_report()
        
        self.logger.info("Memory profiling stopped")
        return report
    
    def create_tracker(self, name: str) -> MemoryTracker:
        """Create a new memory tracker"""
        tracker = MemoryTracker(name)
        self.trackers[name] = tracker
        return tracker
    
    def remove_tracker(self, name: str):
        """Remove a memory tracker"""
        if name in self.trackers:
            del self.trackers[name]
    
    @contextmanager
    def track_memory(self, name: str):
        """Context manager for tracking memory usage"""
        tracker = self.create_tracker(name)
        tracker.start_tracking()
        try:
            yield tracker
        finally:
            summary = tracker.stop_tracking()
            self.logger.info(f"Memory tracking summary for {name}: {summary}")
            self.remove_tracker(name)
    
    def profile_function(self, func: Callable) -> Callable:
        """Decorator for profiling function memory usage"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            with self.track_memory(func_name) as tracker:
                # Take snapshots during execution
                result = func(*args, **kwargs)
                tracker.take_snapshot()
                return result
        return wrapper
    
    def _global_monitor_worker(self):
        """Background worker for global memory monitoring"""
        while self._monitoring:
            try:
                tracker = MemoryTracker("global")
                tracker.take_snapshot()
                self.global_snapshots.append(tracker.snapshots[0])
                
                # Keep only last 1000 snapshots
                if len(self.global_snapshots) > 1000:
                    self.global_snapshots.pop(0)
                
                time.sleep(10)  # Take snapshot every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in global memory monitoring: {e}")
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory profiling report"""
        # Get optimization suggestions
        optimizations = self.optimizer.analyze_memory_usage(self.global_snapshots)
        
        # Get leak detection report
        leak_report = self.leak_detector.get_leak_report()
        
        # Calculate summary statistics
        summary = self._calculate_summary_stats()
        
        report = {
            'profiling_summary': summary,
            'memory_optimizations': [opt.to_dict() for opt in optimizations],
            'leak_detection': leak_report,
            'global_snapshots_count': len(self.global_snapshots),
            'active_trackers': list(self.trackers.keys()),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics from global snapshots"""
        if not self.global_snapshots:
            return {}
        
        memory_values = [s.process_memory_mb for s in self.global_snapshots]
        
        return {
            'total_snapshots': len(self.global_snapshots),
            'memory_stats': {
                'min_mb': min(memory_values),
                'max_mb': max(memory_values),
                'avg_mb': sum(memory_values) / len(memory_values),
                'current_mb': memory_values[-1] if memory_values else 0
            },
            'profiling_duration_seconds': (
                self.global_snapshots[-1].timestamp - self.global_snapshots[0].timestamp
            ).total_seconds() if len(self.global_snapshots) > 1 else 0
        }
    
    def export_report(self, filepath: str, format: str = 'json'):
        """Export memory profiling report to file"""
        report = self.generate_comprehensive_report()
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Memory profiling report exported to: {filepath}")
    
    def get_current_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        
        return {
            'process_memory_mb': memory_info.rss / 1024 / 1024,
            'process_memory_percent': process.memory_percent(),
            'system_memory_total_mb': system_memory.total / 1024 / 1024,
            'system_memory_available_mb': system_memory.available / 1024 / 1024,
            'system_memory_percent': system_memory.percent,
            'gc_objects': len(gc.get_objects()),
            'thread_count': threading.active_count()
        }
    
    def _setup_cleanup_hooks(self):
        """Setup cleanup hooks for proper resource management"""
        import atexit
        
        def cleanup():
            try:
                if self._monitoring:
                    self.stop_profiling()
                self.logger.info("Memory profiler cleanup completed")
            except Exception as e:
                self.logger.error(f"Error during memory profiler cleanup: {e}")
        
        atexit.register(cleanup)


# Global memory profiler instance
_global_memory_profiler = None


def get_memory_profiler(config: Dict[str, Any] = None) -> MemoryProfiler:
    """Get global memory profiler instance"""
    global _global_memory_profiler
    if _global_memory_profiler is None:
        _global_memory_profiler = MemoryProfiler(config)
    return _global_memory_profiler


# Convenience decorators and functions
def profile_memory(func: Callable) -> Callable:
    """Decorator for profiling function memory usage"""
    return get_memory_profiler().profile_function(func)


@contextmanager
def track_memory_usage(name: str):
    """Context manager for tracking memory usage"""
    with get_memory_profiler().track_memory(name) as tracker:
        yield tracker


def start_memory_monitoring(config: Dict[str, Any] = None):
    """Start global memory monitoring"""
    profiler = get_memory_profiler(config)
    profiler.start_profiling()


def stop_memory_monitoring() -> Dict[str, Any]:
    """Stop global memory monitoring and get report"""
    return get_memory_profiler().stop_profiling()


def get_current_memory_stats() -> Dict[str, Any]:
    """Get current memory statistics"""
    return get_memory_profiler().get_current_memory_usage()


def detect_memory_leaks(threshold_mb: float = 50.0, check_interval: int = 60):
    """Start memory leak detection"""
    profiler = get_memory_profiler()
    profiler.leak_detector.leak_threshold = threshold_mb
    profiler.leak_detector.check_interval = check_interval
    profiler.leak_detector.start_monitoring()


def generate_memory_report(filepath: str = None) -> Dict[str, Any]:
    """Generate comprehensive memory report"""
    report = get_memory_profiler().generate_comprehensive_report()
    
    if filepath:
        get_memory_profiler().export_report(filepath)
    
    return report

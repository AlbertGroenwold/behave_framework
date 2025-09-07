"""Performance profiler for the test automation framework.

This module provides comprehensive performance monitoring including:
- Method-level performance tracking
- Memory usage profiling
- Performance baseline comparisons
- Performance regression detection
"""

import time
import threading
import functools
import logging
import psutil
import tracemalloc
import gc
from typing import Dict, Any, Optional, List, Callable, Union
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import contextmanager
from abc import ABC, abstractmethod
import json
import os


@dataclass
class PerformanceMetric:
    """Represents a single performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MethodProfile:
    """Profile data for a method execution."""
    method_name: str
    execution_time: float
    memory_usage: Optional[float] = None
    memory_peak: Optional[float] = None
    call_count: int = 1
    total_time: float = 0
    min_time: float = 0
    max_time: float = 0
    avg_time: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.total_time == 0:
            self.total_time = self.execution_time
        if self.min_time == 0:
            self.min_time = self.execution_time
        if self.max_time == 0:
            self.max_time = self.execution_time
        if self.avg_time == 0:
            self.avg_time = self.execution_time
    
    def update(self, execution_time: float, memory_usage: Optional[float] = None):
        """Update profile with new execution data."""
        self.call_count += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.avg_time = self.total_time / self.call_count
        self.timestamp = datetime.now()
        
        if memory_usage is not None:
            if self.memory_usage is None:
                self.memory_usage = memory_usage
                self.memory_peak = memory_usage
            else:
                self.memory_peak = max(self.memory_peak or 0, memory_usage)


class MemoryProfiler:
    """Memory usage profiler."""
    
    def __init__(self):
        self.tracking_enabled = False
        self.snapshots: List[Dict[str, Any]] = []
        self.baseline_memory = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_tracking(self):
        """Start memory tracking."""
        if not self.tracking_enabled:
            tracemalloc.start()
            self.tracking_enabled = True
            self.baseline_memory = self.get_current_memory()
            self.logger.info("Memory tracking started")
    
    def stop_tracking(self):
        """Stop memory tracking."""
        if self.tracking_enabled:
            tracemalloc.stop()
            self.tracking_enabled = False
            self.logger.info("Memory tracking stopped")
    
    def get_current_memory(self) -> Dict[str, float]:
        """Get current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        result = {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Physical memory
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual memory
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
        
        if self.tracking_enabled:
            current, peak = tracemalloc.get_traced_memory()
            result.update({
                'traced_current_mb': current / 1024 / 1024,
                'traced_peak_mb': peak / 1024 / 1024
            })
        
        return result
    
    def take_snapshot(self, label: str = ""):
        """Take a memory snapshot."""
        if not self.tracking_enabled:
            return
        
        snapshot_data = {
            'label': label,
            'timestamp': datetime.now(),
            'memory': self.get_current_memory()
        }
        
        if self.tracking_enabled:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('filename')[:10]
            
            snapshot_data['top_allocations'] = [
                {
                    'filename': stat.traceback.format()[0],
                    'size_mb': stat.size / 1024 / 1024,
                    'count': stat.count
                }
                for stat in top_stats
            ]
        
        self.snapshots.append(snapshot_data)
        self.logger.debug(f"Memory snapshot taken: {label}")
    
    def get_memory_usage_report(self) -> Dict[str, Any]:
        """Get comprehensive memory usage report."""
        if not self.snapshots:
            return {'error': 'No snapshots available'}
        
        current_memory = self.get_current_memory()
        
        # Calculate memory growth
        memory_growth = {}
        if self.baseline_memory:
            for key in current_memory:
                if key in self.baseline_memory:
                    growth = current_memory[key] - self.baseline_memory[key]
                    memory_growth[f"{key}_growth"] = growth
        
        # Find peak memory usage across snapshots
        peak_memory = {}
        for snapshot in self.snapshots:
            for key, value in snapshot['memory'].items():
                if key not in peak_memory or value > peak_memory[key]:
                    peak_memory[key] = value
        
        return {
            'current_memory': current_memory,
            'baseline_memory': self.baseline_memory,
            'memory_growth': memory_growth,
            'peak_memory': peak_memory,
            'snapshot_count': len(self.snapshots),
            'snapshots': self.snapshots[-5:] if len(self.snapshots) > 5 else self.snapshots  # Last 5
        }
    
    def detect_memory_leaks(self, threshold_mb: float = 50.0) -> List[Dict[str, Any]]:
        """Detect potential memory leaks."""
        leaks = []
        
        if len(self.snapshots) < 2:
            return leaks
        
        # Compare first and last snapshots
        first_snapshot = self.snapshots[0]
        last_snapshot = self.snapshots[-1]
        
        for key in ['rss_mb', 'traced_current_mb']:
            if key in first_snapshot['memory'] and key in last_snapshot['memory']:
                growth = last_snapshot['memory'][key] - first_snapshot['memory'][key]
                if growth > threshold_mb:
                    leaks.append({
                        'metric': key,
                        'growth_mb': growth,
                        'threshold_mb': threshold_mb,
                        'first_value': first_snapshot['memory'][key],
                        'last_value': last_snapshot['memory'][key],
                        'timespan': last_snapshot['timestamp'] - first_snapshot['timestamp']
                    })
        
        return leaks


class PerformanceBaseline:
    """Manages performance baselines for regression detection."""
    
    def __init__(self, baseline_file: str = "performance_baseline.json"):
        self.baseline_file = baseline_file
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.load_baselines()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_baselines(self):
        """Load baselines from file."""
        try:
            if os.path.exists(self.baseline_file):
                with open(self.baseline_file, 'r') as f:
                    self.baselines = json.load(f)
                self.logger.info(f"Loaded {len(self.baselines)} performance baselines")
        except Exception as e:
            self.logger.error(f"Error loading baselines: {e}")
            self.baselines = {}
    
    def save_baselines(self):
        """Save baselines to file."""
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(self.baselines, f, indent=2, default=str)
            self.logger.info(f"Saved {len(self.baselines)} performance baselines")
        except Exception as e:
            self.logger.error(f"Error saving baselines: {e}")
    
    def set_baseline(self, method_name: str, metrics: Dict[str, float]):
        """Set baseline for a method."""
        self.baselines[method_name] = metrics
        self.save_baselines()
        self.logger.debug(f"Baseline set for {method_name}")
    
    def get_baseline(self, method_name: str) -> Optional[Dict[str, float]]:
        """Get baseline for a method."""
        return self.baselines.get(method_name)
    
    def compare_to_baseline(self, method_name: str, current_metrics: Dict[str, float], 
                           threshold_percent: float = 20.0) -> Dict[str, Any]:
        """Compare current metrics to baseline."""
        baseline = self.get_baseline(method_name)
        if not baseline:
            return {'status': 'no_baseline', 'message': 'No baseline available'}
        
        comparisons = {}
        regressions = []
        improvements = []
        
        for metric, current_value in current_metrics.items():
            if metric in baseline:
                baseline_value = baseline[metric]
                if baseline_value > 0:
                    change_percent = ((current_value - baseline_value) / baseline_value) * 100
                    
                    comparisons[metric] = {
                        'current': current_value,
                        'baseline': baseline_value,
                        'change_percent': change_percent,
                        'change_absolute': current_value - baseline_value
                    }
                    
                    if change_percent > threshold_percent:
                        regressions.append({
                            'metric': metric,
                            'change_percent': change_percent,
                            'current': current_value,
                            'baseline': baseline_value
                        })
                    elif change_percent < -threshold_percent:
                        improvements.append({
                            'metric': metric,
                            'change_percent': change_percent,
                            'current': current_value,
                            'baseline': baseline_value
                        })
        
        return {
            'status': 'compared',
            'comparisons': comparisons,
            'regressions': regressions,
            'improvements': improvements,
            'has_regressions': len(regressions) > 0
        }


class PerformanceProfiler:
    """Main performance profiler class."""
    
    def __init__(self, enable_memory_profiling: bool = True, 
                 baseline_file: str = "performance_baseline.json"):
        self.method_profiles: Dict[str, MethodProfile] = {}
        self.memory_profiler = MemoryProfiler() if enable_memory_profiling else None
        self.baseline_manager = PerformanceBaseline(baseline_file)
        self.profiling_enabled = False
        self.start_time = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance metrics collection
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.regression_alerts: List[Dict[str, Any]] = []
    
    def start_profiling(self):
        """Start performance profiling."""
        if self.profiling_enabled:
            return
        
        self.profiling_enabled = True
        self.start_time = datetime.now()
        
        if self.memory_profiler:
            self.memory_profiler.start_tracking()
            self.memory_profiler.take_snapshot("profiling_start")
        
        self.logger.info("Performance profiling started")
    
    def stop_profiling(self):
        """Stop performance profiling."""
        if not self.profiling_enabled:
            return
        
        self.profiling_enabled = False
        
        if self.memory_profiler:
            self.memory_profiler.take_snapshot("profiling_end")
            self.memory_profiler.stop_tracking()
        
        self.logger.info("Performance profiling stopped")
    
    def profile_method(self, method_name: str = None):
        """Decorator to profile method performance."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.profiling_enabled:
                    return func(*args, **kwargs)
                
                name = method_name or f"{func.__module__}.{func.__name__}"
                
                # Memory snapshot before
                memory_before = None
                if self.memory_profiler:
                    memory_before = self.memory_profiler.get_current_memory()
                
                # Execute method with timing
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    
                    # Memory snapshot after
                    memory_after = None
                    memory_usage = None
                    if self.memory_profiler and memory_before:
                        memory_after = self.memory_profiler.get_current_memory()
                        memory_usage = memory_after.get('rss_mb', 0) - memory_before.get('rss_mb', 0)
                    
                    # Update profile
                    self._update_method_profile(name, execution_time, memory_usage)
            
            return wrapper
        return decorator
    
    def _update_method_profile(self, method_name: str, execution_time: float, 
                              memory_usage: Optional[float] = None):
        """Update method profile with new execution data."""
        with self._lock:
            if method_name in self.method_profiles:
                self.method_profiles[method_name].update(execution_time, memory_usage)
            else:
                self.method_profiles[method_name] = MethodProfile(
                    method_name=method_name,
                    execution_time=execution_time,
                    memory_usage=memory_usage
                )
            
            # Add to metrics history
            self.metrics_history[f"{method_name}_time"].append({
                'value': execution_time,
                'timestamp': datetime.now()
            })
            
            if memory_usage is not None:
                self.metrics_history[f"{method_name}_memory"].append({
                    'value': memory_usage,
                    'timestamp': datetime.now()
                })
    
    def get_performance_report(self, top_n: int = 20) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        with self._lock:
            # Sort methods by total time
            sorted_profiles = sorted(
                self.method_profiles.values(),
                key=lambda p: p.total_time,
                reverse=True
            )
            
            # Create summary
            total_profiled_time = sum(p.total_time for p in sorted_profiles)
            total_calls = sum(p.call_count for p in sorted_profiles)
            
            report = {
                'summary': {
                    'total_methods': len(self.method_profiles),
                    'total_profiled_time': round(total_profiled_time, 4),
                    'total_calls': total_calls,
                    'profiling_duration': str(datetime.now() - self.start_time) if self.start_time else "N/A"
                },
                'top_methods_by_total_time': [
                    {
                        'method': p.method_name,
                        'total_time': round(p.total_time, 4),
                        'call_count': p.call_count,
                        'avg_time': round(p.avg_time, 4),
                        'min_time': round(p.min_time, 4),
                        'max_time': round(p.max_time, 4),
                        'memory_peak_mb': round(p.memory_peak, 4) if p.memory_peak else None
                    }
                    for p in sorted_profiles[:top_n]
                ],
                'slowest_single_calls': [
                    {
                        'method': p.method_name,
                        'max_time': round(p.max_time, 4),
                        'avg_time': round(p.avg_time, 4)
                    }
                    for p in sorted(sorted_profiles, key=lambda p: p.max_time, reverse=True)[:top_n]
                ]
            }
            
            # Add memory report if available
            if self.memory_profiler:
                report['memory_report'] = self.memory_profiler.get_memory_usage_report()
                report['memory_leaks'] = self.memory_profiler.detect_memory_leaks()
            
            # Add regression analysis
            report['regression_analysis'] = self._analyze_regressions()
            
            return report
    
    def _analyze_regressions(self) -> Dict[str, Any]:
        """Analyze performance regressions."""
        regressions = []
        
        for method_name, profile in self.method_profiles.items():
            current_metrics = {
                'avg_time': profile.avg_time,
                'max_time': profile.max_time,
                'total_time': profile.total_time
            }
            
            if profile.memory_peak:
                current_metrics['memory_peak'] = profile.memory_peak
            
            comparison = self.baseline_manager.compare_to_baseline(
                method_name, current_metrics
            )
            
            if comparison.get('has_regressions'):
                regressions.extend(comparison['regressions'])
        
        return {
            'total_regressions': len(regressions),
            'regressions': regressions
        }
    
    def set_performance_baseline(self, method_name: Optional[str] = None):
        """Set performance baseline for methods."""
        if method_name:
            # Set baseline for specific method
            if method_name in self.method_profiles:
                profile = self.method_profiles[method_name]
                metrics = {
                    'avg_time': profile.avg_time,
                    'max_time': profile.max_time,
                    'total_time': profile.total_time
                }
                if profile.memory_peak:
                    metrics['memory_peak'] = profile.memory_peak
                
                self.baseline_manager.set_baseline(method_name, metrics)
        else:
            # Set baseline for all profiled methods
            for method_name, profile in self.method_profiles.items():
                metrics = {
                    'avg_time': profile.avg_time,
                    'max_time': profile.max_time,
                    'total_time': profile.total_time
                }
                if profile.memory_peak:
                    metrics['memory_peak'] = profile.memory_peak
                
                self.baseline_manager.set_baseline(method_name, metrics)
        
        self.logger.info(f"Performance baseline set for {method_name or 'all methods'}")
    
    def detect_performance_regressions(self, threshold_percent: float = 20.0) -> List[Dict[str, Any]]:
        """Detect performance regressions."""
        regressions = []
        
        for method_name, profile in self.method_profiles.items():
            current_metrics = {
                'avg_time': profile.avg_time,
                'max_time': profile.max_time
            }
            
            comparison = self.baseline_manager.compare_to_baseline(
                method_name, current_metrics, threshold_percent
            )
            
            if comparison.get('has_regressions'):
                for regression in comparison['regressions']:
                    regression['method'] = method_name
                    regressions.append(regression)
        
        return regressions
    
    def get_method_trend(self, method_name: str, metric: str = 'time') -> List[Dict[str, Any]]:
        """Get performance trend for a method."""
        key = f"{method_name}_{metric}"
        return list(self.metrics_history.get(key, []))
    
    def reset_profiles(self):
        """Reset all performance profiles."""
        with self._lock:
            self.method_profiles.clear()
            self.metrics_history.clear()
            self.regression_alerts.clear()
        
        if self.memory_profiler:
            self.memory_profiler.snapshots.clear()
        
        self.logger.info("Performance profiles reset")


# Context manager for profiling code blocks
@contextmanager
def profile_block(profiler: PerformanceProfiler, block_name: str):
    """Context manager to profile a code block."""
    if not profiler.profiling_enabled:
        yield
        return
    
    # Memory snapshot before
    memory_before = None
    if profiler.memory_profiler:
        memory_before = profiler.memory_profiler.get_current_memory()
    
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        
        # Memory snapshot after
        memory_usage = None
        if profiler.memory_profiler and memory_before:
            memory_after = profiler.memory_profiler.get_current_memory()
            memory_usage = memory_after.get('rss_mb', 0) - memory_before.get('rss_mb', 0)
        
        profiler._update_method_profile(block_name, execution_time, memory_usage)


# Global profiler instance
_global_profiler = None


def get_global_profiler() -> PerformanceProfiler:
    """Get global performance profiler."""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler


def profile_method(method_name: str = None):
    """Decorator using global profiler."""
    return get_global_profiler().profile_method(method_name)


def start_global_profiling():
    """Start global performance profiling."""
    get_global_profiler().start_profiling()


def stop_global_profiling():
    """Stop global performance profiling."""
    get_global_profiler().stop_profiling()


def get_global_performance_report() -> Dict[str, Any]:
    """Get global performance report."""
    return get_global_profiler().get_performance_report()

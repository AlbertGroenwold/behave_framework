"""Import optimization utilities for the test automation framework.

This module provides:
- Import profiler to identify bottlenecks
- Lazy loading for heavy modules
- Import caching mechanisms
- Module initialization optimization
"""

import sys
import time
import importlib
import importlib.util
import threading
import logging
from typing import Dict, Any, Optional, List, Callable, Set
from collections import defaultdict, OrderedDict
from functools import wraps
from contextlib import contextmanager


class ImportProfiler:
    """Profile import times to identify bottlenecks."""
    
    def __init__(self):
        self.import_times: Dict[str, float] = {}
        self.import_order: List[str] = []
        self.import_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.profiling_enabled = False
        self._original_import = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_profiling(self):
        """Start profiling imports."""
        if self.profiling_enabled:
            return
        
        self._original_import = __builtins__.__import__
        __builtins__.__import__ = self._profiled_import
        self.profiling_enabled = True
        self.logger.info("Import profiling started")
    
    def stop_profiling(self):
        """Stop profiling imports."""
        if not self.profiling_enabled:
            return
        
        __builtins__.__import__ = self._original_import
        self.profiling_enabled = False
        self.logger.info("Import profiling stopped")
    
    def _profiled_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Wrapper for __import__ that profiles import times."""
        start_time = time.time()
        
        try:
            # Call original import
            module = self._original_import(name, globals, locals, fromlist, level)
            
            # Record timing
            import_time = time.time() - start_time
            
            with self._lock:
                if name not in self.import_times:
                    self.import_times[name] = import_time
                    self.import_order.append(name)
                else:
                    # Update with cumulative time for repeated imports
                    self.import_times[name] += import_time
                
                # Track dependencies if we can determine the caller
                if globals and '__name__' in globals:
                    caller = globals['__name__']
                    self.import_dependencies[caller].add(name)
            
            return module
            
        except Exception as e:
            # Record failed import
            import_time = time.time() - start_time
            with self._lock:
                self.import_times[f"{name} (FAILED)"] = import_time
            raise
    
    def get_import_report(self, top_n: int = 20) -> Dict[str, Any]:
        """Get import profiling report."""
        with self._lock:
            # Sort by import time
            sorted_imports = sorted(
                self.import_times.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            total_time = sum(self.import_times.values())
            
            report = {
                'total_imports': len(self.import_times),
                'total_import_time': round(total_time, 4),
                'top_slowest_imports': [
                    {
                        'module': name,
                        'time_seconds': round(time_val, 4),
                        'percentage': round((time_val / total_time) * 100, 2) if total_time > 0 else 0
                    }
                    for name, time_val in sorted_imports[:top_n]
                ],
                'import_order': self.import_order.copy(),
                'dependencies': {
                    module: list(deps) 
                    for module, deps in self.import_dependencies.items()
                }
            }
            
            return report
    
    def identify_redundant_imports(self) -> List[str]:
        """Identify potentially redundant imports."""
        redundant = []
        
        # Look for modules imported multiple times
        import_counts = defaultdict(int)
        for module in self.import_order:
            import_counts[module] += 1
        
        for module, count in import_counts.items():
            if count > 1:
                redundant.append(f"{module} (imported {count} times)")
        
        return redundant
    
    def get_heavy_modules(self, threshold: float = 0.1) -> List[str]:
        """Get modules that take more than threshold seconds to import."""
        return [
            name for name, time_val in self.import_times.items()
            if time_val > threshold
        ]
    
    def reset(self):
        """Reset profiling data."""
        with self._lock:
            self.import_times.clear()
            self.import_order.clear()
            self.import_dependencies.clear()


class LazyLoader:
    """Lazy loader for heavy modules."""
    
    def __init__(self, module_name: str, package: Optional[str] = None):
        self.module_name = module_name
        self.package = package
        self._module = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def __getattr__(self, name):
        """Load module on first attribute access."""
        if self._module is None:
            with self._lock:
                if self._module is None:  # Double-check locking
                    self._load_module()
        
        return getattr(self._module, name)
    
    def _load_module(self):
        """Actually load the module."""
        start_time = time.time()
        try:
            self._module = importlib.import_module(self.module_name, self.package)
            load_time = time.time() - start_time
            self.logger.debug(f"Lazy loaded {self.module_name} in {load_time:.4f}s")
        except ImportError as e:
            self.logger.error(f"Failed to lazy load {self.module_name}: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if module is loaded."""
        return self._module is not None
    
    def force_load(self):
        """Force load the module."""
        if self._module is None:
            self._load_module()


class ModuleCache:
    """Cache for imported modules to avoid redundant imports."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get(self, module_name: str) -> Optional[Any]:
        """Get cached module."""
        with self._lock:
            if module_name in self._cache:
                # Move to end (LRU)
                module = self._cache.pop(module_name)
                self._cache[module_name] = module
                return module
            return None
    
    def set(self, module_name: str, module: Any):
        """Cache module."""
        with self._lock:
            if module_name in self._cache:
                # Update existing
                self._cache.pop(module_name)
            elif len(self._cache) >= self.max_size:
                # Remove oldest
                self._cache.popitem(last=False)
            
            self._cache[module_name] = module
    
    def clear(self):
        """Clear cache."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'cached_modules': list(self._cache.keys())
            }


class ImportOptimizer:
    """Main class for import optimization."""
    
    def __init__(self):
        self.profiler = ImportProfiler()
        self.module_cache = ModuleCache()
        self.lazy_loaders: Dict[str, LazyLoader] = {}
        self.optimization_enabled = False
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def enable_optimization(self):
        """Enable import optimization."""
        self.optimization_enabled = True
        self.profiler.start_profiling()
        self.logger.info("Import optimization enabled")
    
    def disable_optimization(self):
        """Disable import optimization."""
        self.optimization_enabled = False
        self.profiler.stop_profiling()
        self.logger.info("Import optimization disabled")
    
    def create_lazy_loader(self, module_name: str, package: Optional[str] = None) -> LazyLoader:
        """Create lazy loader for a module."""
        loader = LazyLoader(module_name, package)
        self.lazy_loaders[module_name] = loader
        return loader
    
    def cached_import(self, module_name: str, package: Optional[str] = None):
        """Import module with caching."""
        # Check cache first
        cached_module = self.module_cache.get(module_name)
        if cached_module is not None:
            return cached_module
        
        # Import and cache
        module = importlib.import_module(module_name, package)
        self.module_cache.set(module_name, module)
        return module
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        import_report = self.profiler.get_import_report()
        cache_stats = self.module_cache.get_stats()
        
        lazy_loader_info = {
            name: {
                'loaded': loader.is_loaded(),
                'module_name': loader.module_name
            }
            for name, loader in self.lazy_loaders.items()
        }
        
        redundant_imports = self.profiler.identify_redundant_imports()
        heavy_modules = self.profiler.get_heavy_modules()
        
        return {
            'import_profiling': import_report,
            'module_cache': cache_stats,
            'lazy_loaders': lazy_loader_info,
            'redundant_imports': redundant_imports,
            'heavy_modules': heavy_modules,
            'recommendations': self._generate_recommendations(
                redundant_imports, heavy_modules, import_report
            )
        }
    
    def _generate_recommendations(self, redundant_imports: List[str], 
                                heavy_modules: List[str], 
                                import_report: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if redundant_imports:
            recommendations.append(
                f"Consider consolidating {len(redundant_imports)} redundant imports"
            )
        
        if heavy_modules:
            recommendations.append(
                f"Consider lazy loading for {len(heavy_modules)} slow modules"
            )
        
        total_time = import_report.get('total_import_time', 0)
        if total_time > 5.0:
            recommendations.append(
                "Total import time is high - consider import optimization"
            )
        
        top_imports = import_report.get('top_slowest_imports', [])
        if top_imports and top_imports[0]['percentage'] > 30:
            slowest = top_imports[0]['module']
            recommendations.append(
                f"Module '{slowest}' dominates import time - consider lazy loading"
            )
        
        return recommendations
    
    def audit_step_definitions(self, step_dir: str) -> Dict[str, Any]:
        """Audit step definition files for import optimization."""
        import os
        import ast
        
        audit_results = {
            'files_analyzed': 0,
            'total_imports': 0,
            'redundant_imports': [],
            'heavy_imports': [],
            'optimization_opportunities': []
        }
        
        for root, dirs, files in os.walk(step_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        tree = ast.parse(content)
                        file_imports = self._extract_imports(tree)
                        
                        audit_results['files_analyzed'] += 1
                        audit_results['total_imports'] += len(file_imports)
                        
                        # Check for optimization opportunities
                        self._analyze_file_imports(file_path, file_imports, audit_results)
                        
                    except Exception as e:
                        self.logger.error(f"Error analyzing {file_path}: {e}")
        
        return audit_results
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    
    def _analyze_file_imports(self, file_path: str, imports: List[str], 
                            audit_results: Dict[str, Any]):
        """Analyze imports in a single file."""
        # Check for commonly heavy imports
        heavy_modules = [
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'tensorflow', 
            'torch', 'selenium', 'requests', 'pytest'
        ]
        
        for imp in imports:
            for heavy in heavy_modules:
                if heavy in imp:
                    audit_results['heavy_imports'].append({
                        'file': file_path,
                        'import': imp,
                        'recommendation': f"Consider lazy loading for {heavy}"
                    })
                    break
        
        # Check for redundant imports (basic check)
        seen_imports = set()
        for imp in imports:
            if imp in seen_imports:
                audit_results['redundant_imports'].append({
                    'file': file_path,
                    'import': imp
                })
            seen_imports.add(imp)


# Decorators for import optimization

def lazy_import(module_name: str, package: Optional[str] = None):
    """Decorator to create lazy import for a module."""
    def decorator(func):
        loader = LazyLoader(module_name, package)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Ensure module is loaded before function execution
            if not loader.is_loaded():
                loader.force_load()
            return func(*args, **kwargs)
        
        # Store loader reference on function
        wrapper._lazy_loader = loader
        return wrapper
    
    return decorator


def profile_imports(func):
    """Decorator to profile imports during function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = ImportProfiler()
        profiler.start_profiling()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.stop_profiling()
            report = profiler.get_import_report(top_n=10)
            logging.getLogger('import_profiler').info(
                f"Import profile for {func.__name__}: {report['total_import_time']:.4f}s total"
            )
    
    return wrapper


# Global optimizer instance
_global_optimizer = ImportOptimizer()


def get_global_optimizer() -> ImportOptimizer:
    """Get global import optimizer."""
    return _global_optimizer


def enable_global_optimization():
    """Enable global import optimization."""
    _global_optimizer.enable_optimization()


def disable_global_optimization():
    """Disable global import optimization."""
    _global_optimizer.disable_optimization()


# Context manager for temporary optimization
@contextmanager
def import_optimization():
    """Context manager for temporary import optimization."""
    optimizer = ImportOptimizer()
    optimizer.enable_optimization()
    try:
        yield optimizer
    finally:
        optimizer.disable_optimization()

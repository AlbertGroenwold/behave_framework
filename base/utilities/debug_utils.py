"""Debug utilities for the test automation framework.

This module provides comprehensive debugging capabilities including:
- Debug mode with verbose output
- Step-through debugging support
- Debug data dumps on failure
- Interactive debugging hooks
"""

import os
import sys
import json
import traceback
import inspect
import time
import threading
import pdb
import logging
from typing import Dict, Any, Optional, List, Callable, Union, TextIO
from datetime import datetime
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from functools import wraps
from pathlib import Path
import io


class DebugMode:
    """Global debug mode management."""
    
    def __init__(self):
        self._enabled = False
        self._verbose = False
        self._debug_level = 0
        self._output_file = None
        self._hooks: List[Callable] = []
        self._lock = threading.Lock()
        
        # Check environment variables
        self._enabled = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self._verbose = os.getenv('DEBUG_VERBOSE', 'false').lower() == 'true'
        debug_level = os.getenv('DEBUG_LEVEL', '0')
        try:
            self._debug_level = int(debug_level)
        except ValueError:
            self._debug_level = 0
    
    def enable(self, verbose: bool = False, level: int = 1):
        """Enable debug mode."""
        with self._lock:
            self._enabled = True
            self._verbose = verbose
            self._debug_level = level
    
    def disable(self):
        """Disable debug mode."""
        with self._lock:
            self._enabled = False
            self._verbose = False
            self._debug_level = 0
    
    def is_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self._enabled
    
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        return self._verbose and self._enabled
    
    def get_level(self) -> int:
        """Get debug level."""
        return self._debug_level if self._enabled else 0
    
    def set_output_file(self, file_path: str):
        """Set debug output file."""
        with self._lock:
            self._output_file = file_path
    
    def get_output_file(self) -> Optional[str]:
        """Get debug output file."""
        return self._output_file
    
    def add_hook(self, hook: Callable):
        """Add debug hook."""
        with self._lock:
            self._hooks.append(hook)
    
    def remove_hook(self, hook: Callable):
        """Remove debug hook."""
        with self._lock:
            if hook in self._hooks:
                self._hooks.remove(hook)
    
    def call_hooks(self, context: Dict[str, Any]):
        """Call all registered hooks."""
        with self._lock:
            hooks = self._hooks.copy()
        
        for hook in hooks:
            try:
                hook(context)
            except Exception as e:
                print(f"Debug hook error: {e}")


# Global debug mode instance
debug_mode = DebugMode()


class DebugDataDumper:
    """Dump debug data on failures or request."""
    
    def __init__(self, dump_dir: str = "debug_dumps"):
        self.dump_dir = Path(dump_dir)
        self.dump_dir.mkdir(exist_ok=True)
        self.auto_dump_on_error = True
        self.max_dumps = 100  # Keep only last 100 dumps
        
    def dump_data(self, data: Dict[str, Any], 
                  dump_name: str = None, 
                  include_stack: bool = True) -> str:
        """Dump debug data to file."""
        if dump_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            dump_name = f"debug_dump_{timestamp}"
        
        dump_file = self.dump_dir / f"{dump_name}.json"
        
        # Prepare dump data
        dump_data = {
            'timestamp': datetime.now().isoformat(),
            'dump_name': dump_name,
            'data': data
        }
        
        # Add stack trace if requested
        if include_stack:
            dump_data['stack_trace'] = traceback.format_stack()
        
        # Add system information
        dump_data['system_info'] = {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'process_id': os.getpid(),
            'thread_id': threading.get_ident()
        }
        
        # Write to file
        try:
            with open(dump_file, 'w', encoding='utf-8') as f:
                json.dump(dump_data, f, indent=2, default=str)
            
            # Clean up old dumps
            self._cleanup_old_dumps()
            
            if debug_mode.is_verbose():
                print(f"Debug data dumped to: {dump_file}")
            
            return str(dump_file)
            
        except Exception as e:
            print(f"Failed to dump debug data: {e}")
            return ""
    
    def dump_variables(self, frame_depth: int = 1, 
                      dump_name: str = None) -> str:
        """Dump local and global variables from calling frame."""
        frame = inspect.currentframe()
        try:
            # Go up the specified number of frames
            for _ in range(frame_depth):
                frame = frame.f_back
                if frame is None:
                    break
            
            if frame is None:
                return ""
            
            # Collect variable data
            var_data = {
                'locals': self._serialize_variables(frame.f_locals),
                'globals': self._serialize_variables(frame.f_globals),
                'frame_info': {
                    'filename': frame.f_code.co_filename,
                    'function': frame.f_code.co_name,
                    'line_number': frame.f_lineno
                }
            }
            
            return self.dump_data(var_data, dump_name)
            
        finally:
            del frame
    
    def _serialize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize variables for JSON dump."""
        serialized = {}
        for name, value in variables.items():
            if name.startswith('_'):
                continue  # Skip private variables
            
            try:
                # Try to serialize the value
                json.dumps(value, default=str)
                serialized[name] = value
            except (TypeError, ValueError):
                # If can't serialize, store type and string representation
                serialized[name] = {
                    'type': type(value).__name__,
                    'repr': repr(value)[:500],  # Limit size
                    'serializable': False
                }
        
        return serialized
    
    def _cleanup_old_dumps(self):
        """Clean up old debug dumps."""
        try:
            dump_files = list(self.dump_dir.glob("debug_dump_*.json"))
            if len(dump_files) > self.max_dumps:
                # Sort by creation time and remove oldest
                dump_files.sort(key=lambda f: f.stat().st_ctime)
                for old_file in dump_files[:-self.max_dumps]:
                    old_file.unlink()
        except Exception:
            pass  # Ignore cleanup errors


class StepThroughDebugger:
    """Step-through debugging support."""
    
    def __init__(self):
        self.breakpoints: List[str] = []
        self.step_mode = False
        self.current_step = 0
        self.step_history: List[Dict[str, Any]] = []
        
    def add_breakpoint(self, location: str):
        """Add breakpoint (function name or file:line)."""
        self.breakpoints.append(location)
        if debug_mode.is_verbose():
            print(f"Breakpoint added: {location}")
    
    def remove_breakpoint(self, location: str):
        """Remove breakpoint."""
        if location in self.breakpoints:
            self.breakpoints.remove(location)
            if debug_mode.is_verbose():
                print(f"Breakpoint removed: {location}")
    
    def enable_step_mode(self):
        """Enable step-through mode."""
        self.step_mode = True
        if debug_mode.is_verbose():
            print("Step-through mode enabled")
    
    def disable_step_mode(self):
        """Disable step-through mode."""
        self.step_mode = False
        if debug_mode.is_verbose():
            print("Step-through mode disabled")
    
    def check_breakpoint(self, location: str = None):
        """Check if execution should break here."""
        if not debug_mode.is_enabled():
            return False
        
        # Auto-determine location if not provided
        if location is None:
            frame = inspect.currentframe().f_back
            filename = frame.f_code.co_filename
            line_number = frame.f_lineno
            function_name = frame.f_code.co_name
            location = f"{filename}:{line_number}"
        
        # Check breakpoints
        should_break = False
        for bp in self.breakpoints:
            if bp in location or location.endswith(bp):
                should_break = True
                break
        
        # Check step mode
        if self.step_mode:
            should_break = True
        
        if should_break:
            self._enter_debug_session(location)
            return True
        
        return False
    
    def _enter_debug_session(self, location: str):
        """Enter interactive debug session."""
        self.current_step += 1
        
        print(f"\n=== DEBUG BREAK AT STEP {self.current_step} ===")
        print(f"Location: {location}")
        print("Commands: (c)ontinue, (s)tep, (v)ariables, (d)ump, (q)uit, (h)elp")
        
        while True:
            try:
                command = input("debug> ").strip().lower()
                
                if command in ['c', 'continue']:
                    break
                elif command in ['s', 'step']:
                    break
                elif command in ['v', 'variables']:
                    self._print_variables()
                elif command in ['d', 'dump']:
                    dumper = DebugDataDumper()
                    dump_file = dumper.dump_variables(frame_depth=2)
                    print(f"Variables dumped to: {dump_file}")
                elif command in ['q', 'quit']:
                    sys.exit(0)
                elif command in ['h', 'help']:
                    self._print_help()
                else:
                    print(f"Unknown command: {command}")
                    
            except (EOFError, KeyboardInterrupt):
                break
    
    def _print_variables(self):
        """Print current variables."""
        frame = inspect.currentframe()
        try:
            # Go up to the caller's frame
            frame = frame.f_back.f_back
            
            print("\n--- Local Variables ---")
            for name, value in frame.f_locals.items():
                if not name.startswith('_'):
                    try:
                        print(f"{name}: {repr(value)[:100]}")
                    except:
                        print(f"{name}: <unable to display>")
        finally:
            del frame
    
    def _print_help(self):
        """Print debug help."""
        print("""
Debug Commands:
  c, continue - Continue execution
  s, step     - Step to next breakpoint
  v, variables - Display local variables  
  d, dump     - Dump variables to file
  q, quit     - Quit program
  h, help     - Show this help
        """)


class InteractiveDebugger:
    """Interactive debugging hooks."""
    
    def __init__(self):
        self.pdb_enabled = False
        self.custom_debugger = None
        
    def enable_pdb_on_error(self):
        """Enable automatic PDB on exceptions."""
        self.pdb_enabled = True
        if debug_mode.is_verbose():
            print("PDB on error enabled")
    
    def disable_pdb_on_error(self):
        """Disable automatic PDB on exceptions."""
        self.pdb_enabled = False
        if debug_mode.is_verbose():
            print("PDB on error disabled")
    
    def set_custom_debugger(self, debugger_func: Callable):
        """Set custom debugger function."""
        self.custom_debugger = debugger_func
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle exception with debugging."""
        if not debug_mode.is_enabled():
            return
        
        print(f"\n=== EXCEPTION OCCURRED ===")
        print(f"Type: {exc_type.__name__}")
        print(f"Message: {exc_value}")
        
        # Dump debug data
        dumper = DebugDataDumper()
        debug_data = {
            'exception': {
                'type': exc_type.__name__,
                'message': str(exc_value),
                'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback)
            }
        }
        dump_file = dumper.dump_data(debug_data, "exception_dump")
        print(f"Exception data dumped to: {dump_file}")
        
        # Enter debugger if enabled
        if self.pdb_enabled:
            print("Entering PDB debugger...")
            pdb.post_mortem(exc_traceback)
        elif self.custom_debugger:
            self.custom_debugger(exc_type, exc_value, exc_traceback)


class VerboseOutput:
    """Manage verbose debug output."""
    
    def __init__(self):
        self.output_stream = sys.stdout
        self.log_file = None
        self.buffer = io.StringIO()
        
    def set_output_file(self, file_path: str):
        """Set output file for verbose logging."""
        self.log_file = open(file_path, 'a', encoding='utf-8')
    
    def print_verbose(self, message: str, level: int = 1):
        """Print verbose message if debug level is sufficient."""
        if debug_mode.get_level() >= level:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            formatted_message = f"[{timestamp}] DEBUG(L{level}): {message}"
            
            print(formatted_message, file=self.output_stream)
            
            if self.log_file:
                print(formatted_message, file=self.log_file)
                self.log_file.flush()
    
    def capture_output(self):
        """Context manager to capture output."""
        return CapturedOutput(self.buffer)
    
    def close(self):
        """Close output file."""
        if self.log_file:
            self.log_file.close()
            self.log_file = None


class CapturedOutput:
    """Capture stdout/stderr for debugging."""
    
    def __init__(self, buffer: io.StringIO):
        self.buffer = buffer
        self.original_stdout = None
        self.original_stderr = None
    
    def __enter__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self.buffer
        sys.stderr = self.buffer
        return self.buffer
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr


# Global instances
step_debugger = StepThroughDebugger()
interactive_debugger = InteractiveDebugger()
verbose_output = VerboseOutput()
data_dumper = DebugDataDumper()


# Decorators and context managers

def debug_on_error(dump_data: bool = True, enter_debugger: bool = False):
    """Decorator to handle errors with debugging."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if debug_mode.is_enabled():
                    print(f"\nError in {func.__name__}: {e}")
                    
                    if dump_data:
                        debug_data = {
                            'function': func.__name__,
                            'args': [repr(arg)[:100] for arg in args],
                            'kwargs': {k: repr(v)[:100] for k, v in kwargs.items()},
                            'error': str(e)
                        }
                        data_dumper.dump_data(debug_data, f"error_{func.__name__}")
                    
                    if enter_debugger:
                        interactive_debugger.handle_exception(type(e), e, e.__traceback__)
                
                raise
        return wrapper
    return decorator


def debug_step(location: str = None):
    """Decorator to add debug step checkpoint."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            checkpoint_location = location or func.__name__
            
            if debug_mode.is_enabled():
                verbose_output.print_verbose(f"Entering {checkpoint_location}")
                step_debugger.check_breakpoint(checkpoint_location)
            
            try:
                result = func(*args, **kwargs)
                
                if debug_mode.is_enabled():
                    verbose_output.print_verbose(f"Completed {checkpoint_location}")
                
                return result
            except Exception as e:
                if debug_mode.is_enabled():
                    verbose_output.print_verbose(f"Error in {checkpoint_location}: {e}")
                raise
        
        return wrapper
    return decorator


def debug_trace(include_args: bool = False, include_result: bool = False):
    """Decorator to trace function calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not debug_mode.is_enabled():
                return func(*args, **kwargs)
            
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Entry trace
            trace_msg = f"→ {func_name}"
            if include_args and debug_mode.get_level() >= 2:
                trace_msg += f" args={len(args)}, kwargs={list(kwargs.keys())}"
            verbose_output.print_verbose(trace_msg, level=2)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Exit trace
                trace_msg = f"← {func_name} ({execution_time:.4f}s)"
                if include_result and debug_mode.get_level() >= 3:
                    trace_msg += f" result={type(result).__name__}"
                verbose_output.print_verbose(trace_msg, level=2)
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                verbose_output.print_verbose(
                    f"✗ {func_name} ({execution_time:.4f}s) ERROR: {e}", 
                    level=1
                )
                raise
        
        return wrapper
    return decorator


@contextmanager
def debug_context(context_name: str, **context_data):
    """Context manager for debug information."""
    if debug_mode.is_enabled():
        verbose_output.print_verbose(f"Entering context: {context_name}")
        
        if context_data and debug_mode.get_level() >= 2:
            for key, value in context_data.items():
                verbose_output.print_verbose(f"  {key}: {value}")
    
    try:
        yield
    except Exception as e:
        if debug_mode.is_enabled():
            verbose_output.print_verbose(f"Exception in context {context_name}: {e}")
            data_dumper.dump_data({
                'context': context_name,
                'context_data': context_data,
                'error': str(e)
            }, f"context_error_{context_name}")
        raise
    finally:
        if debug_mode.is_enabled():
            verbose_output.print_verbose(f"Exiting context: {context_name}")


# Utility functions

def debug_print(message: str, level: int = 1):
    """Print debug message if debug mode is enabled."""
    if debug_mode.is_enabled():
        verbose_output.print_verbose(message, level)


def debug_dump_vars(**variables):
    """Dump variables for debugging."""
    if debug_mode.is_enabled():
        data_dumper.dump_data(variables, "variable_dump")


def debug_breakpoint(name: str = None):
    """Set a debug breakpoint."""
    if debug_mode.is_enabled():
        location = name or f"breakpoint_{inspect.currentframe().f_back.f_lineno}"
        step_debugger.check_breakpoint(location)


def set_debug_mode(enabled: bool = True, verbose: bool = False, level: int = 1):
    """Configure debug mode."""
    if enabled:
        debug_mode.enable(verbose, level)
    else:
        debug_mode.disable()


def enable_debug_on_exception():
    """Enable automatic debugging on exceptions."""
    interactive_debugger.enable_pdb_on_error()
    
    # Install exception hook
    original_excepthook = sys.excepthook
    
    def debug_excepthook(exc_type, exc_value, exc_traceback):
        interactive_debugger.handle_exception(exc_type, exc_value, exc_traceback)
        return original_excepthook(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = debug_excepthook


def get_debug_statistics() -> Dict[str, Any]:
    """Get debug statistics."""
    return {
        'debug_mode_enabled': debug_mode.is_enabled(),
        'debug_level': debug_mode.get_level(),
        'verbose_mode': debug_mode.is_verbose(),
        'breakpoints_count': len(step_debugger.breakpoints),
        'step_mode_enabled': step_debugger.step_mode,
        'current_step': step_debugger.current_step,
        'pdb_on_error': interactive_debugger.pdb_enabled,
        'dump_directory': str(data_dumper.dump_dir),
        'max_dumps': data_dumper.max_dumps
    }

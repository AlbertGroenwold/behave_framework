"""Desktop application manager for automation testing"""

import subprocess
import psutil
import time
import logging
import os
from typing import Dict, Any, List, Optional, Union
import configparser
from pathlib import Path


class DesktopAppManager:
    """Manager for desktop application lifecycle"""
    
    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running_processes = {}
        
        if config_path:
            self.config.read(config_path)
    
    def launch_application(self, app_path: str, app_name: str = None, args: List[str] = None, 
                          wait_time: int = 3) -> Dict[str, Any]:
        """Launch desktop application"""
        try:
            if not os.path.exists(app_path):
                self.logger.error(f"Application not found: {app_path}")
                return {'success': False, 'error': f'Application not found: {app_path}'}
            
            command = [app_path]
            if args:
                command.extend(args)
            
            self.logger.info(f"Launching application: {' '.join(command)}")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for application to start
            time.sleep(wait_time)
            
            if process.poll() is None:  # Process is still running
                app_key = app_name or os.path.basename(app_path)
                self.running_processes[app_key] = {
                    'process': process,
                    'pid': process.pid,
                    'path': app_path,
                    'start_time': time.time()
                }
                
                self.logger.info(f"Application launched successfully: {app_key} (PID: {process.pid})")
                return {
                    'success': True,
                    'pid': process.pid,
                    'app_name': app_key,
                    'process': process
                }
            else:
                # Process terminated
                stdout, stderr = process.communicate()
                self.logger.error(f"Application failed to start: {stderr.decode()}")
                return {
                    'success': False,
                    'error': f'Application failed to start: {stderr.decode()}'
                }
        
        except Exception as e:
            self.logger.error(f"Error launching application: {e}")
            return {'success': False, 'error': str(e)}
    
    def close_application(self, app_name: str = None, pid: int = None, force: bool = False) -> bool:
        """Close desktop application"""
        try:
            if app_name and app_name in self.running_processes:
                process_info = self.running_processes[app_name]
                process = process_info['process']
                
                if force:
                    process.kill()
                    self.logger.info(f"Force killed application: {app_name}")
                else:
                    process.terminate()
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        self.logger.info(f"Application terminated gracefully: {app_name}")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        self.logger.warning(f"Application killed after timeout: {app_name}")
                
                del self.running_processes[app_name]
                return True
            
            elif pid:
                try:
                    if force:
                        os.kill(pid, 9)  # SIGKILL
                        self.logger.info(f"Force killed process: {pid}")
                    else:
                        os.kill(pid, 15)  # SIGTERM
                        self.logger.info(f"Terminated process: {pid}")
                    return True
                except ProcessLookupError:
                    self.logger.warning(f"Process not found: {pid}")
                    return False
            
            else:
                self.logger.error("No application name or PID provided")
                return False
        
        except Exception as e:
            self.logger.error(f"Error closing application: {e}")
            return False
    
    def is_application_running(self, app_name: str = None, pid: int = None, 
                              process_name: str = None) -> bool:
        """Check if application is running"""
        try:
            if app_name and app_name in self.running_processes:
                process = self.running_processes[app_name]['process']
                return process.poll() is None
            
            elif pid:
                return psutil.pid_exists(pid)
            
            elif process_name:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower() == process_name.lower():
                        return True
                return False
            
            else:
                self.logger.error("No application identifier provided")
                return False
        
        except Exception as e:
            self.logger.error(f"Error checking application status: {e}")
            return False
    
    def get_application_info(self, app_name: str = None, pid: int = None) -> Dict[str, Any]:
        """Get application information"""
        try:
            if app_name and app_name in self.running_processes:
                process_info = self.running_processes[app_name]
                process = process_info['process']
                
                if process.poll() is None:
                    psutil_process = psutil.Process(process.pid)
                    return {
                        'pid': process.pid,
                        'name': app_name,
                        'path': process_info['path'],
                        'start_time': process_info['start_time'],
                        'memory_usage': psutil_process.memory_info().rss,
                        'cpu_percent': psutil_process.cpu_percent(),
                        'status': psutil_process.status(),
                        'is_running': True
                    }
                else:
                    return {
                        'name': app_name,
                        'is_running': False
                    }
            
            elif pid:
                if psutil.pid_exists(pid):
                    psutil_process = psutil.Process(pid)
                    return {
                        'pid': pid,
                        'name': psutil_process.name(),
                        'memory_usage': psutil_process.memory_info().rss,
                        'cpu_percent': psutil_process.cpu_percent(),
                        'status': psutil_process.status(),
                        'is_running': True
                    }
                else:
                    return {
                        'pid': pid,
                        'is_running': False
                    }
            
            else:
                self.logger.error("No application identifier provided")
                return {}
        
        except Exception as e:
            self.logger.error(f"Error getting application info: {e}")
            return {}
    
    def get_running_applications(self) -> List[Dict[str, Any]]:
        """Get list of all managed running applications"""
        running_apps = []
        
        for app_name, process_info in self.running_processes.items():
            app_info = self.get_application_info(app_name=app_name)
            if app_info.get('is_running'):
                running_apps.append(app_info)
            else:
                # Clean up terminated processes
                del self.running_processes[app_name]
        
        return running_apps
    
    def wait_for_application_start(self, process_name: str, timeout: int = 30) -> bool:
        """Wait for application to start"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_application_running(process_name=process_name):
                self.logger.info(f"Application started: {process_name}")
                return True
            time.sleep(1)
        
        self.logger.warning(f"Application did not start within timeout: {process_name}")
        return False
    
    def wait_for_application_close(self, app_name: str = None, pid: int = None, 
                                  timeout: int = 30) -> bool:
        """Wait for application to close"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.is_application_running(app_name=app_name, pid=pid):
                self.logger.info(f"Application closed: {app_name or pid}")
                return True
            time.sleep(1)
        
        self.logger.warning(f"Application did not close within timeout: {app_name or pid}")
        return False
    
    def restart_application(self, app_name: str, app_path: str = None, 
                           args: List[str] = None, wait_time: int = 3) -> Dict[str, Any]:
        """Restart application"""
        if app_name in self.running_processes:
            app_path = app_path or self.running_processes[app_name]['path']
            
            # Close application
            if self.close_application(app_name):
                # Wait for application to close
                if self.wait_for_application_close(app_name=app_name):
                    # Launch application again
                    return self.launch_application(app_path, app_name, args, wait_time)
                else:
                    return {'success': False, 'error': 'Application did not close properly'}
            else:
                return {'success': False, 'error': 'Failed to close application'}
        else:
            if app_path:
                return self.launch_application(app_path, app_name, args, wait_time)
            else:
                return {'success': False, 'error': 'Application not running and no path provided'}
    
    def get_application_path_from_config(self, app_name: str) -> str:
        """Get application path from configuration"""
        try:
            return self.config.get('applications', app_name, fallback='')
        except Exception:
            return ''
    
    def find_application_by_name(self, app_name: str) -> List[Dict[str, Any]]:
        """Find application processes by name"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                if app_name.lower() in proc.info['name'].lower():
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': proc.info['exe'],
                        'create_time': proc.info['create_time']
                    })
        except Exception as e:
            self.logger.error(f"Error finding application: {e}")
        
        return processes
    
    def kill_all_by_name(self, process_name: str) -> int:
        """Kill all processes with given name"""
        killed_count = 0
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    try:
                        proc.kill()
                        killed_count += 1
                        self.logger.info(f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})")
                    except Exception as e:
                        self.logger.error(f"Failed to kill process {proc.info['pid']}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error killing processes: {e}")
        
        return killed_count
    
    def cleanup_all_managed_applications(self):
        """Clean up all managed applications"""
        for app_name in list(self.running_processes.keys()):
            self.close_application(app_name)
        
        self.running_processes.clear()
        self.logger.info("Cleaned up all managed applications")

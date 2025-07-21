"""Database performance monitor for automation testing"""

import logging
from typing import Dict, Any
from .base_database_manager import BaseDatabaseManager


class DatabasePerformanceMonitor:
    """Base performance monitor for database testing"""
    
    def __init__(self, database_manager: BaseDatabaseManager):
        self.database_manager = database_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.performance_data = []
    
    def execute_timed_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute query and measure performance"""
        import time
        
        start_time = time.time()
        
        try:
            result = self.database_manager.execute_query(query, params)
            execution_time = time.time() - start_time
            
            performance_data = {
                'query': query,
                'execution_time': execution_time,
                'success': True,
                'timestamp': time.time()
            }
            
            if isinstance(result, dict) and 'affected_rows' in result:
                performance_data['affected_rows'] = result['affected_rows']
            elif isinstance(result, list):
                performance_data['result_count'] = len(result)
            
            self.performance_data.append(performance_data)
            self.logger.info(f"Query executed in {execution_time:.3f} seconds")
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            performance_data = {
                'query': query,
                'execution_time': execution_time,
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
            
            self.performance_data.append(performance_data)
            self.logger.error(f"Query failed after {execution_time:.3f} seconds: {e}")
            
            raise
    
    def validate_performance_threshold(self, max_time: float) -> bool:
        """Validate query performance meets threshold"""
        if not self.performance_data:
            return False
        
        latest_execution = self.performance_data[-1]
        execution_time = latest_execution['execution_time']
        
        meets_threshold = execution_time <= max_time
        
        if meets_threshold:
            self.logger.info(f"Performance threshold met: {execution_time:.3f}s <= {max_time}s")
        else:
            self.logger.warning(f"Performance threshold exceeded: {execution_time:.3f}s > {max_time}s")
        
        return meets_threshold
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.performance_data:
            return {}
        
        successful_queries = [data for data in self.performance_data if data['success']]
        
        if not successful_queries:
            return {'total_queries': len(self.performance_data), 'successful_queries': 0}
        
        execution_times = [data['execution_time'] for data in successful_queries]
        
        return {
            'total_queries': len(self.performance_data),
            'successful_queries': len(successful_queries),
            'failed_queries': len(self.performance_data) - len(successful_queries),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'total_execution_time': sum(execution_times)
        }
    
    def reset_performance_data(self):
        """Reset collected performance data"""
        self.performance_data.clear()
        self.logger.info("Performance data reset")

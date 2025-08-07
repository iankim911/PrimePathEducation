"""
Monitoring and Logging Service - Phase 7
Provides centralized monitoring, metrics, and logging
"""
import time
import logging
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List, Callable
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
import traceback
import sys

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores application metrics."""
    
    # Metrics storage
    _metrics = {
        'requests': {},
        'database': {},
        'cache': {},
        'errors': [],
        'performance': {},
    }
    
    @classmethod
    def record_request(cls, path: str, method: str, status_code: int, 
                      response_time: float):
        """Record HTTP request metrics."""
        key = f"{method}:{path}"
        
        if key not in cls._metrics['requests']:
            cls._metrics['requests'][key] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'status_codes': {},
            }
        
        metrics = cls._metrics['requests'][key]
        metrics['count'] += 1
        metrics['total_time'] += response_time
        metrics['avg_time'] = metrics['total_time'] / metrics['count']
        metrics['min_time'] = min(metrics['min_time'], response_time)
        metrics['max_time'] = max(metrics['max_time'], response_time)
        
        status_key = str(status_code)
        metrics['status_codes'][status_key] = metrics['status_codes'].get(status_key, 0) + 1
    
    @classmethod
    def record_database_query(cls, query: str, execution_time: float):
        """Record database query metrics."""
        # Simplify query for grouping
        query_type = query.split()[0].upper() if query else 'UNKNOWN'
        
        if query_type not in cls._metrics['database']:
            cls._metrics['database'][query_type] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
            }
        
        metrics = cls._metrics['database'][query_type]
        metrics['count'] += 1
        metrics['total_time'] += execution_time
        metrics['avg_time'] = metrics['total_time'] / metrics['count']
    
    @classmethod
    def record_cache_operation(cls, operation: str, hit: bool):
        """Record cache operation metrics."""
        if operation not in cls._metrics['cache']:
            cls._metrics['cache'][operation] = {
                'hits': 0,
                'misses': 0,
                'hit_rate': 0,
            }
        
        metrics = cls._metrics['cache'][operation]
        if hit:
            metrics['hits'] += 1
        else:
            metrics['misses'] += 1
        
        total = metrics['hits'] + metrics['misses']
        metrics['hit_rate'] = (metrics['hits'] / total * 100) if total > 0 else 0
    
    @classmethod
    def record_error(cls, error_type: str, message: str, traceback_str: str = None):
        """Record application errors."""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'traceback': traceback_str,
        }
        
        cls._metrics['errors'].append(error_entry)
        
        # Keep only last 100 errors
        if len(cls._metrics['errors']) > 100:
            cls._metrics['errors'] = cls._metrics['errors'][-100:]
    
    @classmethod
    def record_performance(cls, operation: str, duration: float):
        """Record performance metrics for specific operations."""
        if operation not in cls._metrics['performance']:
            cls._metrics['performance'][operation] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
            }
        
        metrics = cls._metrics['performance'][operation]
        metrics['count'] += 1
        metrics['total_time'] += duration
        metrics['avg_time'] = metrics['total_time'] / metrics['count']
        metrics['min_time'] = min(metrics['min_time'], duration)
        metrics['max_time'] = max(metrics['max_time'], duration)
    
    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Get all collected metrics."""
        return cls._metrics.copy()
    
    @classmethod
    def reset_metrics(cls):
        """Reset all metrics."""
        cls._metrics = {
            'requests': {},
            'database': {},
            'cache': {},
            'errors': [],
            'performance': {},
        }


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    @staticmethod
    def measure_time(func: Callable) -> Callable:
        """Decorator to measure function execution time."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                
                MetricsCollector.record_performance(
                    f"{func.__module__}.{func.__name__}",
                    execution_time
                )
                
                if execution_time > 1000:  # Log slow operations (> 1 second)
                    logger.warning(
                        f"Slow operation: {func.__name__} took {execution_time:.2f}ms"
                    )
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(
                    f"Error in {func.__name__} after {execution_time:.2f}ms: {e}"
                )
                raise
        
        return wrapper
    
    @staticmethod
    def monitor_database_queries(func: Callable) -> Callable:
        """Decorator to monitor database queries in a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            initial_queries = len(connection.queries)
            
            result = func(*args, **kwargs)
            
            query_count = len(connection.queries) - initial_queries
            
            if query_count > 10:  # Warn about potential N+1 queries
                logger.warning(
                    f"High query count in {func.__name__}: {query_count} queries"
                )
                
                if settings.DEBUG:
                    # Log query details in debug mode
                    queries = connection.queries[initial_queries:]
                    for query in queries[-5:]:  # Show last 5 queries
                        logger.debug(f"Query: {query['sql'][:100]}...")
            
            return result
        
        return wrapper


class HealthCheckService:
    """Service for system health checks."""
    
    @classmethod
    def check_database(cls) -> Dict[str, Any]:
        """Check database health."""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return {
                'status': 'healthy',
                'message': 'Database connection OK',
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database error: {str(e)}',
            }
    
    @classmethod
    def check_cache(cls) -> Dict[str, Any]:
        """Check cache health."""
        try:
            test_key = '_health_check_test'
            cache.set(test_key, 'test', 10)
            value = cache.get(test_key)
            cache.delete(test_key)
            
            if value == 'test':
                return {
                    'status': 'healthy',
                    'message': 'Cache connection OK',
                }
            else:
                return {
                    'status': 'degraded',
                    'message': 'Cache read/write mismatch',
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Cache error: {str(e)}',
            }
    
    @classmethod
    def check_disk_space(cls) -> Dict[str, Any]:
        """Check available disk space."""
        try:
            import shutil
            stats = shutil.disk_usage(settings.BASE_DIR)
            free_gb = stats.free / (1024 ** 3)
            total_gb = stats.total / (1024 ** 3)
            used_percent = (stats.used / stats.total) * 100
            
            if free_gb < 1:  # Less than 1GB free
                status = 'critical'
                message = f'Low disk space: {free_gb:.2f}GB free'
            elif used_percent > 90:
                status = 'warning'
                message = f'High disk usage: {used_percent:.1f}%'
            else:
                status = 'healthy'
                message = f'Disk space OK: {free_gb:.2f}GB free of {total_gb:.2f}GB'
            
            return {
                'status': status,
                'message': message,
                'free_gb': free_gb,
                'total_gb': total_gb,
                'used_percent': used_percent,
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'message': f'Could not check disk space: {str(e)}',
            }
    
    @classmethod
    def check_memory(cls) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = 'critical'
                message = f'Critical memory usage: {memory.percent}%'
            elif memory.percent > 75:
                status = 'warning'
                message = f'High memory usage: {memory.percent}%'
            else:
                status = 'healthy'
                message = f'Memory usage OK: {memory.percent}%'
            
            return {
                'status': status,
                'message': message,
                'used_percent': memory.percent,
                'available_mb': memory.available / (1024 ** 2),
                'total_mb': memory.total / (1024 ** 2),
            }
        except ImportError:
            return {
                'status': 'unknown',
                'message': 'psutil not installed',
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'message': f'Could not check memory: {str(e)}',
            }
    
    @classmethod
    def get_system_health(cls) -> Dict[str, Any]:
        """Get overall system health status."""
        checks = {
            'database': cls.check_database(),
            'cache': cls.check_cache(),
            'disk': cls.check_disk_space(),
            'memory': cls.check_memory(),
        }
        
        # Determine overall status
        statuses = [check['status'] for check in checks.values()]
        
        if 'critical' in statuses or 'unhealthy' in statuses:
            overall_status = 'unhealthy'
        elif 'warning' in statuses or 'degraded' in statuses:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'checks': checks,
        }


class ActivityLogger:
    """Log user and system activities."""
    
    @classmethod
    def log_user_action(cls, user_id: Optional[str], action: str, 
                       details: Dict[str, Any] = None):
        """
        Log a user action.
        
        Args:
            user_id: User identifier
            action: Action performed
            details: Additional details
        """
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details or {},
        }
        
        logger.info(f"User action: {json.dumps(log_entry)}")
        
        # Store in cache for recent activity tracking
        cache_key = f"activity:user:{user_id or 'anonymous'}"
        recent_activities = cache.get(cache_key, [])
        recent_activities.append(log_entry)
        
        # Keep only last 50 activities
        if len(recent_activities) > 50:
            recent_activities = recent_activities[-50:]
        
        cache.set(cache_key, recent_activities, 3600)  # 1 hour
    
    @classmethod
    def log_system_event(cls, event_type: str, message: str, 
                        severity: str = 'info', details: Dict[str, Any] = None):
        """
        Log a system event.
        
        Args:
            event_type: Type of event
            message: Event message
            severity: Event severity (info, warning, error, critical)
            details: Additional details
        """
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'message': message,
            'severity': severity,
            'details': details or {},
        }
        
        # Use appropriate logger level
        log_func = getattr(logger, severity, logger.info)
        log_func(f"System event: {json.dumps(log_entry)}")
        
        # Store critical events
        if severity in ['error', 'critical']:
            MetricsCollector.record_error(event_type, message)
    
    @classmethod
    def get_recent_activities(cls, user_id: Optional[str] = None, 
                            limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent activities.
        
        Args:
            user_id: Optional user filter
            limit: Maximum number of activities
            
        Returns:
            List of recent activities
        """
        if user_id:
            cache_key = f"activity:user:{user_id}"
            activities = cache.get(cache_key, [])
        else:
            # Get all recent activities from cache
            activities = []
            # This would need a more sophisticated implementation
            # for production (e.g., using Redis SCAN)
        
        return activities[-limit:] if activities else []


def log_execution(level: str = 'info', include_args: bool = False):
    """
    Decorator to log function execution.
    
    Args:
        level: Log level
        include_args: Whether to include function arguments
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            if include_args:
                logger.log(
                    getattr(logging, level.upper()),
                    f"Executing {func_name} with args={args}, kwargs={kwargs}"
                )
            else:
                logger.log(
                    getattr(logging, level.upper()),
                    f"Executing {func_name}"
                )
            
            try:
                result = func(*args, **kwargs)
                logger.log(
                    getattr(logging, level.upper()),
                    f"Completed {func_name}"
                )
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}: {e}", exc_info=True)
                raise
        
        return wrapper
    return decorator
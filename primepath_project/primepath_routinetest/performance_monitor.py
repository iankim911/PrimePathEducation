"""
Performance monitoring and health checks for the placement test system.
Tracks metrics to identify issues before they become critical.
"""
import time
import logging
from functools import wraps
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from datetime import timedelta
import json

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor system performance and health metrics."""
    
    @staticmethod
    def track_execution_time(operation_name):
        """
        Decorator to track execution time of functions.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    # Log if execution time is high
                    if execution_time > 1000:  # More than 1 second
                        logger.warning(
                            f"Slow operation: {operation_name} took {execution_time:.2f}ms"
                        )
                    
                    # Track in cache for aggregation
                    PerformanceMonitor.record_metric(operation_name, execution_time)
                    
                    return result
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    logger.error(
                        f"Operation {operation_name} failed after {execution_time:.2f}ms: {e}"
                    )
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def record_metric(metric_name, value):
        """
        Record a performance metric.
        """
        cache_key = f'metrics:{metric_name}:{timezone.now().strftime("%Y%m%d%H")}'
        
        # Get existing metrics
        metrics = cache.get(cache_key, {
            'count': 0,
            'total': 0,
            'min': float('inf'),
            'max': 0,
            'values': []
        })
        
        # Update metrics
        metrics['count'] += 1
        metrics['total'] += value
        metrics['min'] = min(metrics['min'], value)
        metrics['max'] = max(metrics['max'], value)
        
        # Keep last 100 values for percentile calculations
        if len(metrics['values']) < 100:
            metrics['values'].append(value)
        
        # Save back to cache (expires after 24 hours)
        cache.set(cache_key, metrics, 86400)
    
    @staticmethod
    def get_database_stats():
        """
        Get database performance statistics.
        """
        from primepath_routinetest.models import StudentSession, StudentAnswer, Exam
        
        # Use Django ORM for cross-database compatibility
        try:
            stats = {
                'total_sessions': StudentSession.objects.count(),
                'total_answers': StudentAnswer.objects.count(),
                'active_exams': Exam.objects.filter(is_active=True).count(),
                'database_size_mb': 0  # Size calculation is database-specific
            }
            
            # Try to get database size for SQLite
            if connection.vendor == 'sqlite':
                import os
                from django.conf import settings
                db_path = settings.DATABASES['default']['NAME']
                if os.path.exists(db_path):
                    stats['database_size_mb'] = os.path.getsize(db_path) / 1048576
            
            return stats
        except Exception as e:
            logger.warning(f"Could not get database stats: {e}")
            return {
                'database_size_mb': 0,
                'total_sessions': 0,
                'total_answers': 0,
                'active_exams': 0
            }
    
    @staticmethod
    def get_cache_stats():
        """
        Get cache performance statistics.
        """
        # This is Django cache specific - adjust based on your cache backend
        cache_stats = {
            'backend': cache._cache.__class__.__name__,
            'entries': 0,  # Would need cache backend specific implementation
            'hit_rate': 0  # Would need to track hits/misses
        }
        
        # Try to get Redis stats if using Redis
        try:
            if hasattr(cache._cache, '_cache'):
                client = cache._cache._cache
                info = client.info('stats')
                cache_stats.update({
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                    'memory_used_mb': info.get('used_memory', 0) / 1048576
                })
                
                total = cache_stats['hits'] + cache_stats['misses']
                if total > 0:
                    cache_stats['hit_rate'] = (cache_stats['hits'] / total) * 100
        except:
            pass
        
        return cache_stats
    
    @staticmethod
    def check_system_health():
        """
        Perform comprehensive health checks.
        """
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Check database connectivity
        try:
            from primepath_routinetest.models import Exam
            Exam.objects.exists()
            health_status['checks']['database'] = 'ok'
        except Exception as e:
            health_status['checks']['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check cache connectivity
        try:
            cache.set('health_check', 'ok', 1)
            if cache.get('health_check') == 'ok':
                health_status['checks']['cache'] = 'ok'
            else:
                health_status['checks']['cache'] = 'error: cannot read from cache'
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['checks']['cache'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'
        
        # Check response times
        recent_metrics = PerformanceMonitor.get_recent_metrics()
        avg_response_time = recent_metrics.get('average_response_time', 0)
        
        if avg_response_time > 1000:  # Over 1 second
            health_status['checks']['performance'] = f'slow: {avg_response_time:.0f}ms'
            health_status['status'] = 'degraded'
        else:
            health_status['checks']['performance'] = f'ok: {avg_response_time:.0f}ms'
        
        # Check error rates
        error_rate = recent_metrics.get('error_rate', 0)
        if error_rate > 5:  # More than 5% errors
            health_status['checks']['errors'] = f'high: {error_rate:.1f}%'
            health_status['status'] = 'degraded'
        else:
            health_status['checks']['errors'] = f'ok: {error_rate:.1f}%'
        
        # Check memory usage (if available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                health_status['checks']['memory'] = f'critical: {memory.percent:.1f}%'
                health_status['status'] = 'unhealthy'
            elif memory.percent > 80:
                health_status['checks']['memory'] = f'high: {memory.percent:.1f}%'
                health_status['status'] = 'degraded'
            else:
                health_status['checks']['memory'] = f'ok: {memory.percent:.1f}%'
        except ImportError:
            health_status['checks']['memory'] = 'unknown: psutil not installed'
        
        return health_status
    
    @staticmethod
    def get_recent_metrics(hours=1):
        """
        Get aggregated metrics for the recent period.
        """
        metrics_summary = {
            'average_response_time': 0,
            'max_response_time': 0,
            'total_requests': 0,
            'error_rate': 0,
            'slow_requests': 0
        }
        
        # Aggregate metrics from cache
        current_hour = timezone.now().strftime("%Y%m%d%H")
        
        operations = [
            'submit_answer', 'complete_test', 'save_exam',
            'load_test', 'grade_session'
        ]
        
        total_time = 0
        total_count = 0
        max_time = 0
        slow_count = 0
        
        for operation in operations:
            cache_key = f'metrics:{operation}:{current_hour}'
            metrics = cache.get(cache_key)
            
            if metrics:
                total_count += metrics['count']
                total_time += metrics['total']
                max_time = max(max_time, metrics['max'])
                
                # Count slow requests (> 1 second)
                slow_count += sum(1 for v in metrics.get('values', []) if v > 1000)
        
        if total_count > 0:
            metrics_summary['average_response_time'] = total_time / total_count
            metrics_summary['max_response_time'] = max_time
            metrics_summary['total_requests'] = total_count
            metrics_summary['slow_requests'] = slow_count
            metrics_summary['error_rate'] = 0  # Would need error tracking
        
        return metrics_summary
    
    @staticmethod
    def cleanup_old_sessions():
        """
        Clean up old incomplete sessions to prevent database bloat.
        """
        from primepath_routinetest.models import StudentSession
        
        # Delete incomplete sessions older than 24 hours
        cutoff = timezone.now() - timedelta(hours=24)
        
        deleted = StudentSession.objects.filter(
            completed_at__isnull=True,  # Use completed_at field instead of is_completed
            started_at__lt=cutoff
        ).delete()
        
        logger.info(f"Cleaned up {deleted[0]} old incomplete sessions")
        return deleted[0]
    
    @staticmethod
    def get_performance_report():
        """
        Generate a comprehensive performance report.
        """
        report = {
            'timestamp': timezone.now().isoformat(),
            'health': PerformanceMonitor.check_system_health(),
            'metrics': PerformanceMonitor.get_recent_metrics(),
            'database': PerformanceMonitor.get_database_stats(),
            'cache': PerformanceMonitor.get_cache_stats()
        }
        
        # Add recommendations
        recommendations = []
        
        if report['metrics']['average_response_time'] > 500:
            recommendations.append("Consider adding database indexes or caching")
        
        if report['metrics']['error_rate'] > 1:
            recommendations.append("Investigate error sources and add retry logic")
        
        if report['database']['total_sessions'] > 10000:
            recommendations.append("Consider archiving old sessions")
        
        if report['cache']['hit_rate'] < 50:
            recommendations.append("Review caching strategy")
        
        report['recommendations'] = recommendations
        
        return report


# Middleware to track all requests
class PerformanceMiddleware:
    """
    Middleware to track performance of all requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Track request start time
        request._start_time = time.time()
        
        # Get response
        response = self.get_response(request)
        
        # Calculate execution time
        if hasattr(request, '_start_time'):
            execution_time = (time.time() - request._start_time) * 1000
            
            # Track metric
            operation = f"{request.method}:{request.path}"
            PerformanceMonitor.record_metric(operation, execution_time)
            
            # Add header with execution time
            response['X-Execution-Time'] = f"{execution_time:.2f}ms"
            
            # Log slow requests
            if execution_time > 1000:
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {execution_time:.2f}ms"
                )
        
        return response
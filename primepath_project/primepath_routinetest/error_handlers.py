"""
Enhanced Error Handlers for RoutineTest Module
Comprehensive error handling and logging infrastructure with performance monitoring
Version 2.0 - Updated August 17, 2025
"""
import logging
import traceback
import json
from datetime import datetime
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.db import IntegrityError, DatabaseError, transaction
from django.utils import timezone
from django.core.cache import cache

# Configure enhanced logger
logger = logging.getLogger('primepath_routinetest')

class RoutineTestError(Exception):
    """Base exception for routine test app"""
    pass

class SessionError(RoutineTestError):
    """Exception for session-related errors"""
    pass

class ExamError(RoutineTestError):
    """Exception for exam-related errors"""
    pass

class GradingError(RoutineTestError):
    """Exception for grading-related errors"""
    pass

class MatrixError(RoutineTestError):
    """Exception for matrix operation errors"""
    pass

class PerformanceError(RoutineTestError):
    """Exception for performance-related issues"""
    pass


class RoutineTestErrorHandler:
    """Centralized error handling for RoutineTest module with enhanced capabilities"""
    
    @staticmethod
    def log_error(error, context=None, user=None, request=None, performance_metrics=None):
        """Comprehensive error logging with context and performance data"""
        error_details = {
            "module": "primepath_routinetest",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": timezone.now().isoformat(),
            "context": context or {},
            "user": user.username if user else "Anonymous",
            "is_superuser": user.is_superuser if user else False,
            "request_path": request.path if request else None,
            "request_method": request.method if request else None,
            "user_agent": request.META.get('HTTP_USER_AGENT', 'Unknown') if request else None,
            "performance_metrics": performance_metrics or {},
            "stack_trace": traceback.format_exc()
        }
        
        # Enhanced console logging for real-time debugging
        print(f"\n{'='*100}")
        print(f"🚨 [ROUTINETEST_ERROR] {error_details['error_type']}: {error_details['error_message']}")
        print(f"👤 User: {error_details['user']} {'(Admin)' if error_details['is_superuser'] else '(Regular)'}")
        print(f"🌐 Path: {error_details['request_method']} {error_details['request_path']}")
        print(f"⏰ Time: {error_details['timestamp']}")
        
        if context:
            print(f"📋 Context: {json.dumps(context, default=str, indent=2)}")
        
        if performance_metrics:
            print(f"📊 Performance: {json.dumps(performance_metrics, default=str)}")
            
        print(f"{'='*100}\n")
        
        # Structured logging for persistent storage
        logger.error(f"[ROUTINETEST_ERROR] {json.dumps(error_details, default=str)}", exc_info=True)
        
        return error_details
    
    @staticmethod
    def handle_database_error(error, context=None, user=None, request=None, performance_metrics=None):
        """Enhanced database error handling with pattern recognition"""
        error_details = RoutineTestErrorHandler.log_error(error, context, user, request, performance_metrics)
        
        error_str = str(error).lower()
        
        # Pattern matching for common database issues
        if "unique constraint failed" in error_str:
            return {
                'error': True,
                'error_type': 'DUPLICATE_ENTRY',
                'message': 'This item already exists. Please check for duplicates and try again.',
                'user_friendly': True,
                'action_suggestions': ['Check existing records', 'Modify unique values', 'Contact support'],
                'details': error_details if user and user.is_superuser else None
            }
        elif "not null constraint failed" in error_str:
            return {
                'error': True,
                'error_type': 'MISSING_REQUIRED_FIELD',
                'message': 'Required information is missing. Please fill in all required fields.',
                'user_friendly': True,
                'action_suggestions': ['Check required fields', 'Validate input data'],
                'details': error_details if user and user.is_superuser else None
            }
        elif "foreign key constraint failed" in error_str:
            return {
                'error': True,
                'error_type': 'INVALID_REFERENCE',
                'message': 'The referenced item does not exist. Please check your selection.',
                'user_friendly': True,
                'action_suggestions': ['Verify referenced items exist', 'Refresh the page'],
                'details': error_details if user and user.is_superuser else None
            }
        elif "database is locked" in error_str:
            return {
                'error': True,
                'error_type': 'DATABASE_LOCKED',
                'message': 'The database is temporarily busy. Please try again in a moment.',
                'user_friendly': True,
                'action_suggestions': ['Wait a moment', 'Try again', 'Contact support if persists'],
                'retry_suggested': True,
                'details': error_details if user and user.is_superuser else None
            }
        else:
            return {
                'error': True,
                'error_type': 'DATABASE_ERROR',
                'message': 'Database operation failed. Please try again or contact support.',
                'user_friendly': True,
                'action_suggestions': ['Try again', 'Contact support'],
                'details': error_details if user and user.is_superuser else None
            }
    
    @staticmethod
    def handle_performance_error(error, context=None, user=None, request=None, performance_metrics=None):
        """Handle performance-related errors"""
        error_details = RoutineTestErrorHandler.log_error(error, context, user, request, performance_metrics)
        
        return {
            'error': True,
            'error_type': 'PERFORMANCE_ERROR',
            'message': 'The operation is taking longer than expected. Please try again.',
            'user_friendly': True,
            'action_suggestions': ['Try again', 'Check your connection', 'Contact support'],
            'performance_issue': True,
            'details': error_details if user and user.is_superuser else None
        }


class ConsoleLogger:
    """Enhanced console logging with performance monitoring and structured output"""
    
    @staticmethod
    def log_view_start(view_name, user, request_data=None, cache_info=None):
        """Log view start with comprehensive context"""
        start_data = {
            "event": "VIEW_START",
            "view": view_name,
            "user": user.username if user else "Anonymous",
            "is_authenticated": user.is_authenticated if user else False,
            "is_superuser": user.is_superuser if user else False,
            "timestamp": timezone.now().isoformat(),
            "request_data_count": len(request_data) if request_data else 0,
            "cache_info": cache_info or {}
        }
        
        print(f"\n{'='*100}")
        print(f"🚀 [VIEW_START] {view_name}")
        print(f"👤 User: {start_data['user']} {'👑(Admin)' if start_data['is_superuser'] else '👥(User)'}")
        print(f"⏰ Start Time: {start_data['timestamp']}")
        
        if request_data:
            print(f"📊 Request Data: {len(request_data)} items")
            if len(request_data) <= 5:  # Show details for small datasets
                print(f"📋 Data: {json.dumps(request_data, default=str, indent=2)}")
        
        if cache_info:
            print(f"💾 Cache Info: {json.dumps(cache_info, default=str)}")
            
        print(f"{'='*100}\n")
        
        logger.info(f"[VIEW_START] {json.dumps(start_data, default=str)}")
        
        return start_data
    
    @staticmethod
    def log_view_end(view_name, user, duration, result_summary=None, performance_warnings=None):
        """Log view completion with performance analysis"""
        end_data = {
            "event": "VIEW_END",
            "view": view_name,
            "user": user.username if user else "Anonymous",
            "duration_seconds": duration,
            "timestamp": timezone.now().isoformat(),
            "result": result_summary or {},
            "performance_warnings": performance_warnings or []
        }
        
        # Performance assessment
        if duration > 5.0:
            performance_status = "🐌 SLOW"
        elif duration > 2.0:
            performance_status = "⚠️ MODERATE"
        else:
            performance_status = "⚡ FAST"
        
        print(f"\n✅ [VIEW_END] {view_name} completed in {duration:.2f}s {performance_status}")
        print(f"👤 User: {end_data['user']}")
        
        if result_summary:
            print(f"📈 Results: {json.dumps(result_summary, default=str)}")
        
        if performance_warnings:
            print(f"⚠️ Performance Warnings:")
            for warning in performance_warnings:
                print(f"   • {warning}")
                
        print(f"{'='*100}\n")
        
        logger.info(f"[VIEW_END] {json.dumps(end_data, default=str)}")
        
        return end_data
    
    @staticmethod
    def log_database_operation(operation, model, count=None, filters=None, user=None, duration=None):
        """Log database operations with performance monitoring"""
        db_data = {
            "event": "DB_OPERATION",
            "operation": operation,
            "model": model,
            "count": count,
            "filters": filters,
            "user": user.username if user else "System",
            "duration_ms": duration * 1000 if duration else None,
            "timestamp": timezone.now().isoformat()
        }
        
        # Performance status for DB operations
        if duration:
            if duration > 1.0:
                perf_status = "🐌"
            elif duration > 0.5:
                perf_status = "⚠️"
            else:
                perf_status = "⚡"
        else:
            perf_status = "📊"
        
        print(f"🗄️ [DB_OP] {perf_status} {operation} on {model} | Count: {count} | "
              f"Duration: {duration:.3f}s | User: {db_data['user']}" if duration else 
              f"🗄️ [DB_OP] {operation} on {model} | Count: {count} | User: {db_data['user']}")
        
        logger.debug(f"[DB_OPERATION] {json.dumps(db_data, default=str)}")
        
        return db_data
    
    @staticmethod
    def log_cache_operation(operation, key, hit=None, ttl=None, size=None):
        """Log cache operations for performance monitoring"""
        cache_data = {
            "event": "CACHE_OPERATION",
            "operation": operation,
            "key": key,
            "cache_hit": hit,
            "ttl_seconds": ttl,
            "size_bytes": size,
            "timestamp": timezone.now().isoformat()
        }
        
        hit_status = "💾✅" if hit else "💾❌" if hit is False else "💾"
        
        print(f"{hit_status} [CACHE] {operation} | Key: {key[:50]}... | "
              f"TTL: {ttl}s" if ttl else f"{hit_status} [CACHE] {operation} | Key: {key[:50]}...")
        
        logger.debug(f"[CACHE_OPERATION] {json.dumps(cache_data, default=str)}")
        
        return cache_data

def enhanced_view_handler(view_name=None, template_name=None, cache_enabled=True):
    """
    Enhanced decorator for robust error handling in RoutineTest views with performance monitoring
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            start_time = datetime.now()
            actual_view_name = view_name or view_func.__name__
            performance_warnings = []
            
            # Enhanced logging with performance monitoring
            ConsoleLogger.log_view_start(
                actual_view_name, 
                request.user, 
                dict(request.GET) if request.GET else None,
                {'cache_enabled': cache_enabled}
            )
            
            context = {
                'view_name': actual_view_name,
                'args': args,
                'kwargs': kwargs,
                'cache_enabled': cache_enabled
            }
            
            try:
                # Execute the view function with performance monitoring
                result = view_func(request, *args, **kwargs)
                
                # Calculate performance metrics
                duration = (datetime.now() - start_time).total_seconds()
                
                # Performance analysis
                if duration > 5.0:
                    performance_warnings.append(f"View took {duration:.2f}s (>5s threshold)")
                if duration > 2.0:
                    performance_warnings.append("Consider caching or optimization")
                
                # Log successful completion
                result_summary = {
                    'status': 'success',
                    'response_type': type(result).__name__,
                    'cache_used': cache_enabled
                }
                
                ConsoleLogger.log_view_end(
                    actual_view_name, 
                    request.user, 
                    duration, 
                    result_summary, 
                    performance_warnings
                )
                
                return result
                
            except ObjectDoesNotExist as e:
                duration = (datetime.now() - start_time).total_seconds()
                performance_metrics = {'duration_seconds': duration, 'failed_at': 'data_lookup'}
                
                error_response = RoutineTestErrorHandler.log_error(e, context, request.user, request, performance_metrics)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Resource not found',
                        'error_type': 'NOT_FOUND',
                        'details': error_response if request.user.is_superuser else None
                    }, status=404)
                
                error_context = {
                    'error': True,
                    'error_message': 'The requested resource was not found.',
                    'error_type': 'NOT_FOUND',
                    'user': request.user,
                    'tab_name': actual_view_name,
                    'error_timestamp': timezone.now().isoformat(),
                    'debug_info': error_response if request.user.is_superuser else None
                }
                return render(request, template_name or 'primepath_routinetest/error.html', error_context, status=404)
            
            except ValidationError as e:
                duration = (datetime.now() - start_time).total_seconds()
                performance_metrics = {'duration_seconds': duration, 'failed_at': 'validation'}
                
                error_response = RoutineTestErrorHandler.handle_validation_error(e, context, request.user, request)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(error_response, status=400)
                
                error_context = {
                    'error': True,
                    'error_message': error_response['message'],
                    'error_type': error_response['error_type'],
                    'field_errors': error_response.get('field_errors', {}),
                    'user': request.user,
                    'tab_name': actual_view_name,
                    'error_timestamp': timezone.now().isoformat(),
                    'debug_info': error_response.get('details') if request.user.is_superuser else None
                }
                return render(request, template_name or 'primepath_routinetest/error.html', error_context, status=400)
            
            except (IntegrityError, DatabaseError) as e:
                duration = (datetime.now() - start_time).total_seconds()
                performance_metrics = {'duration_seconds': duration, 'failed_at': 'database_operation'}
                
                error_response = RoutineTestErrorHandler.handle_database_error(e, context, request.user, request, performance_metrics)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(error_response, status=500)
                
                error_context = {
                    'error': True,
                    'error_message': error_response['message'],
                    'error_type': error_response['error_type'],
                    'action_suggestions': error_response.get('action_suggestions', []),
                    'retry_suggested': error_response.get('retry_suggested', False),
                    'user': request.user,
                    'tab_name': actual_view_name,
                    'error_timestamp': timezone.now().isoformat(),
                    'debug_info': error_response.get('details') if request.user.is_superuser else None
                }
                return render(request, template_name or 'primepath_routinetest/error.html', error_context, status=500)
            
            except PermissionDenied as e:
                duration = (datetime.now() - start_time).total_seconds()
                performance_metrics = {'duration_seconds': duration, 'failed_at': 'permission_check'}
                
                error_response = RoutineTestErrorHandler.log_error(e, context, request.user, request, performance_metrics)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Permission denied',
                        'error_type': 'PERMISSION_DENIED'
                    }, status=403)
                
                error_context = {
                    'error': True,
                    'error_message': 'You do not have permission to perform this action.',
                    'error_type': 'PERMISSION_DENIED',
                    'user': request.user,
                    'tab_name': actual_view_name,
                    'error_timestamp': timezone.now().isoformat(),
                    'debug_info': error_response if request.user.is_superuser else None
                }
                return render(request, template_name or 'primepath_routinetest/error.html', error_context, status=403)
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                performance_metrics = {'duration_seconds': duration, 'failed_at': 'unexpected_error'}
                
                error_response = RoutineTestErrorHandler.log_error(e, context, request.user, request, performance_metrics)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'An unexpected error occurred',
                        'error_type': 'SYSTEM_ERROR',
                        'details': error_response if request.user.is_superuser else None
                    }, status=500)
                
                error_context = {
                    'error': True,
                    'error_message': 'An unexpected error occurred. Please try again or contact support.',
                    'error_type': 'SYSTEM_ERROR',
                    'user': request.user,
                    'tab_name': actual_view_name,
                    'error_timestamp': timezone.now().isoformat(),
                    'debug_info': error_response if request.user.is_superuser else None
                }
                return render(request, template_name or 'primepath_routinetest/error.html', error_context, status=500)
        
        return wrapped_view
    return decorator


# Matrix-specific decorator with enhanced capabilities
def matrix_operation_handler(operation_name=None, require_permissions=True):
    """Enhanced decorator for matrix operations with comprehensive error handling and performance monitoring"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            operation = operation_name or view_func.__name__
            start_time = datetime.now()
            
            # Enhanced logging for matrix operations
            ConsoleLogger.log_view_start(f"MATRIX_{operation.upper()}", request.user)
            
            context = {
                "operation": operation,
                "require_permissions": require_permissions,
                "args": str(args),
                "kwargs": {k: str(v) for k, v in kwargs.items()}
            }
            
            try:
                # Execute with atomic transaction for data integrity
                with transaction.atomic():
                    result = view_func(request, *args, **kwargs)
                
                # Log successful completion with performance metrics
                duration = (datetime.now() - start_time).total_seconds()
                result_summary = {
                    'operation': operation,
                    'status': 'SUCCESS',
                    'duration_seconds': duration
                }
                
                ConsoleLogger.log_view_end(f"MATRIX_{operation.upper()}", request.user, duration, result_summary)
                
                return result
                
            except (DatabaseError, IntegrityError) as e:
                duration = (datetime.now() - start_time).total_seconds()
                performance_metrics = {'operation': operation, 'duration_seconds': duration}
                
                error_response = RoutineTestErrorHandler.handle_database_error(
                    e, context, request.user, request, performance_metrics
                )
                
                print(f"[MATRIX_OP_ERROR] {operation} failed after {duration:.2f}s")
                
                if request.headers.get('content-type') == 'application/json' or 'ajax' in request.path.lower():
                    return JsonResponse(error_response, status=500)
                else:
                    error_context = {
                        'error': True,
                        'error_message': f"Matrix operation '{operation}' failed: {error_response['message']}",
                        'error_type': error_response['error_type'],
                        'user': request.user,
                        'tab_name': 'Schedule Matrix',
                        'operation_name': operation,
                        'error_timestamp': timezone.now().isoformat(),
                        'debug_info': error_response.get('details') if request.user.is_superuser else None
                    }
                    return render(request, 'primepath_routinetest/error.html', error_context)
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                performance_metrics = {'operation': operation, 'duration_seconds': duration}
                
                error_response = RoutineTestErrorHandler.log_error(
                    e, context, request.user, request, performance_metrics
                )
                
                print(f"[MATRIX_OP_ERROR] {operation} failed after {duration:.2f}s")
                
                if request.headers.get('content-type') == 'application/json' or 'ajax' in request.path.lower():
                    return JsonResponse(error_response, status=500)
                else:
                    error_context = {
                        'error': True,
                        'error_message': f"Matrix operation '{operation}' failed: {error_response.get('message', str(e))}",
                        'error_type': error_response.get('error_type', 'SYSTEM_ERROR'),
                        'user': request.user,
                        'tab_name': 'Schedule Matrix',
                        'operation_name': operation,
                        'error_timestamp': timezone.now().isoformat(),
                        'debug_info': error_response.get('details') if request.user.is_superuser else None
                    }
                    return render(request, 'primepath_routinetest/error.html', error_context)
        
        return wrapper
    return decorator


# Keep original decorators for backward compatibility but mark as deprecated
def handle_view_errors(view_func):
    """
    DEPRECATED: Use enhanced_view_handler instead
    Original decorator for backward compatibility
    """
    return enhanced_view_handler()(view_func)


def handle_api_errors(api_func):
    """
    Enhanced API error handler with comprehensive logging
    """
    @wraps(api_func)
    def wrapped_api(request, *args, **kwargs):
        start_time = datetime.now()
        
        ConsoleLogger.log_view_start(f"API_{api_func.__name__}", request.user)
        
        try:
            result = api_func(request, *args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            ConsoleLogger.log_view_end(f"API_{api_func.__name__}", request.user, duration, {'status': 'success'})
            
            return result
            
        except ObjectDoesNotExist as e:
            duration = (datetime.now() - start_time).total_seconds()
            context = {'api_function': api_func.__name__, 'duration_seconds': duration}
            
            RoutineTestErrorHandler.log_error(e, context, request.user, request)
            
            return JsonResponse({
                'success': False,
                'error': 'Resource not found',
                'error_code': 'NOT_FOUND'
            }, status=404)
            
        except ValidationError as e:
            duration = (datetime.now() - start_time).total_seconds()
            context = {'api_function': api_func.__name__, 'duration_seconds': duration}
            
            RoutineTestErrorHandler.log_error(e, context, request.user, request)
            
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'error_code': 'VALIDATION_ERROR',
                'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
            }, status=400)
            
        except (IntegrityError, DatabaseError) as e:
            duration = (datetime.now() - start_time).total_seconds()
            context = {'api_function': api_func.__name__, 'duration_seconds': duration}
            
            error_response = RoutineTestErrorHandler.handle_database_error(e, context, request.user, request)
            
            return JsonResponse({
                'success': False,
                'error': error_response['message'],
                'error_code': error_response['error_type']
            }, status=500)
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            context = {'api_function': api_func.__name__, 'duration_seconds': duration}
            
            RoutineTestErrorHandler.log_error(e, context, request.user, request)
            
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'error_code': 'INTERNAL_ERROR',
                'details': str(e) if request.user.is_superuser else None
            }, status=500)
    
    return wrapped_api


# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor and log performance metrics for RoutineTest operations"""
    
    @staticmethod
    def monitor_database_queries(func):
        """Decorator to monitor database query performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            from django.db import connection
            
            initial_queries = len(connection.queries)
            start_time = datetime.now()
            
            result = func(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            query_count = len(connection.queries) - initial_queries
            
            # Log performance metrics
            if query_count > 10:
                print(f"⚠️ [PERF_WARNING] {func.__name__} executed {query_count} queries in {duration:.2f}s")
            elif duration > 1.0:
                print(f"⚠️ [PERF_WARNING] {func.__name__} took {duration:.2f}s")
            else:
                print(f"✅ [PERF_OK] {func.__name__}: {query_count} queries in {duration:.2f}s")
            
            return result
        
        return wrapper


# Export enhanced functions
__all__ = [
    'enhanced_view_handler',
    'matrix_operation_handler', 
    'handle_api_errors',
    'RoutineTestErrorHandler',
    'ConsoleLogger',
    'PerformanceMonitor',
    # Legacy exports for backward compatibility
    'handle_view_errors',
    'safe_get_or_404',
    'safe_bulk_create',
    'log_activity',
    'validate_session_access', 
    'validate_exam_access'
]


# Enhanced utility functions 
def handle_validation_error(error, context=None, user=None, request=None):
    """Handle validation errors with enhanced context"""
    error_details = RoutineTestErrorHandler.log_error(error, context, user, request)
    
    return {
        'error': True,
        'error_type': 'VALIDATION_ERROR',
        'message': str(error) if hasattr(error, 'message') else 'Invalid data provided.',
        'user_friendly': True,
        'field_errors': error.message_dict if hasattr(error, 'message_dict') else {},
        'details': error_details if user and user.is_superuser else None
    }


# Legacy utility functions (preserved for backward compatibility)
def safe_get_or_404(model, **kwargs):
    """Safely get an object or raise a proper 404 error"""
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise ObjectDoesNotExist(f"{model.__name__} not found with criteria: {kwargs}")
    except Exception as e:
        logger.error(f"Error retrieving {model.__name__}: {str(e)}")
        raise DatabaseError(f"Failed to retrieve {model.__name__}")

def safe_bulk_create(model, objects, **kwargs):
    """Safely bulk create objects with error handling"""
    try:
        return model.objects.bulk_create(objects, **kwargs)
    except IntegrityError as e:
        logger.error(f"Integrity error during bulk create for {model.__name__}: {str(e)}")
        raise IntegrityError(f"Failed to create {model.__name__} objects: Data integrity violation")
    except Exception as e:
        logger.error(f"Error during bulk create for {model.__name__}: {str(e)}")
        raise DatabaseError(f"Failed to create {model.__name__} objects")

def log_activity(user, action, details=None):
    """Log user activity for audit purposes"""
    try:
        logger.info(f"USER_ACTIVITY: User={user.username if user else 'Anonymous'}, "
                   f"Action={action}, Details={details}")
    except Exception as e:
        logger.error(f"Failed to log activity: {str(e)}")

def validate_session_access(session, user):
    """Validate that a user has access to a session"""
    if not session:
        raise SessionError("Session not found")
    
    # Add your access control logic here
    if hasattr(session, 'student') and session.student != user:
        if not user.is_staff and not user.groups.filter(name='Teachers').exists():
            raise SessionError("You don't have permission to access this session")
    
    return True

def validate_exam_access(exam, user):
    """Validate that a user has access to an exam"""
    if not exam:
        raise ExamError("Exam not found")
    
    # Add your access control logic here
    if not exam.is_active and not user.is_staff:
        raise ExamError("This exam is not currently available")
    
    return True

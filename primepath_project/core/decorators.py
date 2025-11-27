"""
Decorators for consistent error handling and logging across the application.
"""
import functools
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .exceptions import PrimePathException

logger = logging.getLogger(__name__)


def handle_errors(view_func=None, *, template_name=None, ajax_only=False):
    """
    Decorator for consistent error handling in views.
    
    Args:
        template_name: Template to render for non-AJAX requests on error
        ajax_only: If True, always return JSON responses
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                return func(request, *args, **kwargs)
            except PrimePathException as e:
                # Log the custom exception with details
                logger.warning(
                    f"PrimePath exception in {func.__name__}: {e.message}",
                    extra={
                        'code': e.code,
                        'details': e.details,
                        'user': getattr(request.user, 'username', 'anonymous'),
                        'path': request.path
                    }
                )
                
                if ajax_only or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }, status=400)
                else:
                    if template_name:
                        return render(request, template_name, {
                            'error': e.message,
                            'error_code': e.code
                        }, status=400)
                    raise
                    
            except Exception as e:
                # Log unexpected exceptions
                logger.error(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    exc_info=True,
                    extra={
                        'user': getattr(request.user, 'username', 'anonymous'),
                        'path': request.path
                    }
                )
                
                if ajax_only or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'An unexpected error occurred. Please try again.'
                    }, status=500)
                else:
                    if template_name:
                        return render(request, template_name, {
                            'error': 'An unexpected error occurred.'
                        }, status=500)
                    raise
                    
        return wrapper
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)


def validate_request_data(required_fields=None, method='POST'):
    """
    Decorator to validate request data before processing.
    
    Args:
        required_fields: List of required field names
        method: HTTP method to validate (POST, GET, etc.)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method != method:
                return JsonResponse({
                    'success': False,
                    'error': f'Method {request.method} not allowed'
                }, status=405)
                
            if required_fields:
                data = request.POST if method == 'POST' else request.GET
                missing_fields = [field for field in required_fields if not data.get(field)]
                
                if missing_fields:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required fields: {", ".join(missing_fields)}'
                    }, status=400)
                    
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def teacher_required(view_func):
    """
    Decorator to ensure only teachers can access certain views.
    For now, just requires login. Can be extended to check user roles.
    """
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # For now, just check if user is authenticated
        # In the future, you can add role checking here:
        # if not hasattr(request.user, 'is_teacher') or not request.user.is_teacher:
        #     return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
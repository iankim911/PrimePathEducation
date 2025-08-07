"""
Common mixins for views across the application.
"""
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import ContextMixin
import json
import logging

logger = logging.getLogger(__name__)


class AjaxResponseMixin:
    """Standardize AJAX/JSON responses across the application."""
    
    def json_response(self, data=None, message="Success", status=200):
        """
        Return a standardized JSON success response.
        
        Args:
            data: Data to include in response
            message: Success message
            status: HTTP status code
            
        Returns:
            JsonResponse
        """
        response_data = {
            'status': 'success',
            'message': message
        }
        if data is not None:
            response_data['data'] = data
        return JsonResponse(response_data, status=status)
    
    def error_response(self, message="An error occurred", errors=None, status=400):
        """
        Return a standardized JSON error response.
        
        Args:
            message: Error message
            errors: Dictionary of field errors
            status: HTTP status code
            
        Returns:
            JsonResponse
        """
        response_data = {
            'status': 'error',
            'message': message
        }
        if errors:
            response_data['errors'] = errors
        return JsonResponse(response_data, status=status)
    
    def is_ajax(self, request):
        """
        Check if request is AJAX.
        
        Args:
            request: HttpRequest
            
        Returns:
            Boolean
        """
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


class TeacherRequiredMixin(LoginRequiredMixin):
    """Ensure user is authenticated and is a teacher."""
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user is a teacher before proceeding."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Check if user has teacher profile
        try:
            from core.models import Teacher
            teacher = Teacher.objects.get(user=request.user)
            if not teacher.is_active:
                logger.warning(f"Inactive teacher attempted access: {request.user.username}")
                return self.handle_no_permission()
        except Teacher.DoesNotExist:
            logger.warning(f"Non-teacher user attempted teacher-only access: {request.user.username}")
            return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)


class RequestValidationMixin:
    """Validate request data consistently."""
    
    def validate_required_fields(self, data, required_fields):
        """
        Validate that required fields are present in data.
        
        Args:
            data: Dictionary of data to validate
            required_fields: List of required field names
            
        Returns:
            Tuple (is_valid, missing_fields)
        """
        missing_fields = [field for field in required_fields if not data.get(field)]
        return len(missing_fields) == 0, missing_fields
    
    def get_json_data(self, request):
        """
        Safely parse JSON data from request body.
        
        Args:
            request: HttpRequest
            
        Returns:
            Dictionary or None if parsing fails
        """
        try:
            return json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to parse JSON data: {e}")
            return None
    
    def validate_uuid(self, uuid_string):
        """
        Validate UUID string format.
        
        Args:
            uuid_string: String to validate
            
        Returns:
            Boolean
        """
        import uuid
        try:
            uuid.UUID(str(uuid_string))
            return True
        except (ValueError, AttributeError):
            return False


class PaginationMixin(ContextMixin):
    """Add pagination support to views."""
    
    paginate_by = 20
    
    def get_paginate_by(self, queryset=None):
        """
        Get the number of items to paginate by.
        
        Returns:
            Integer
        """
        return self.paginate_by
    
    def get_pagination_context(self, page_obj):
        """
        Get pagination context for templates.
        
        Args:
            page_obj: Page object from paginator
            
        Returns:
            Dictionary with pagination context
        """
        return {
            'paginator': page_obj.paginator,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'page_range': page_obj.paginator.get_elided_page_range(
                page_obj.number, 
                on_each_side=2, 
                on_ends=1
            )
        }


class CacheMixin:
    """Add caching support to views."""
    
    cache_timeout = 300  # 5 minutes default
    cache_key_prefix = None
    
    def get_cache_key(self, *args):
        """
        Generate cache key.
        
        Args:
            *args: Arguments to include in cache key
            
        Returns:
            String cache key
        """
        prefix = self.cache_key_prefix or self.__class__.__name__.lower()
        key_parts = [prefix] + [str(arg) for arg in args]
        return ':'.join(key_parts)
    
    def get_from_cache(self, cache_key):
        """
        Get data from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None
        """
        from django.core.cache import cache
        return cache.get(cache_key)
    
    def set_cache(self, cache_key, data, timeout=None):
        """
        Set data in cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            timeout: Cache timeout in seconds
        """
        from django.core.cache import cache
        timeout = timeout or self.cache_timeout
        cache.set(cache_key, data, timeout)
    
    def delete_cache(self, cache_key):
        """
        Delete data from cache.
        
        Args:
            cache_key: Cache key
        """
        from django.core.cache import cache
        cache.delete(cache_key)


class LoggingMixin:
    """Add structured logging to views."""
    
    def log_action(self, action, user=None, data=None, level='info'):
        """
        Log an action with context.
        
        Args:
            action: Action being performed
            user: User performing action
            data: Additional data to log
            level: Log level (info, warning, error)
        """
        log_data = {
            'action': action,
            'view': self.__class__.__name__,
            'user': str(user) if user else 'anonymous',
        }
        if data:
            log_data.update(data)
        
        log_method = getattr(logger, level, logger.info)
        log_method(f"Action: {action}", extra=log_data)
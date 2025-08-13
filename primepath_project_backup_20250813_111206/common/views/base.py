"""
Base view classes that combine common functionality.
"""
from django.views import View
from django.views.generic import TemplateView, FormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from ..mixins import (
    AjaxResponseMixin, 
    RequestValidationMixin, 
    LoggingMixin,
    TeacherRequiredMixin
)
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_protect, name='dispatch')
class BaseAPIView(View, AjaxResponseMixin, RequestValidationMixin, LoggingMixin):
    """
    Base class for API views with JSON responses.
    
    Provides:
    - Standardized JSON responses
    - Request validation helpers
    - Structured logging
    - CSRF protection
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Add logging to dispatch."""
        self.log_action(
            f"{request.method} request",
            user=request.user,
            data={'path': request.path}
        )
        return super().dispatch(request, *args, **kwargs)
    
    def handle_exception(self, exception):
        """
        Handle exceptions consistently.
        
        Args:
            exception: Exception that occurred
            
        Returns:
            JsonResponse with error
        """
        logger.exception(f"Exception in {self.__class__.__name__}: {str(exception)}")
        
        # Map exception types to appropriate responses
        from core.exceptions import ValidationException, PlacementRuleException
        
        if isinstance(exception, ValidationException):
            return self.error_response(
                message=str(exception),
                status=400
            )
        elif isinstance(exception, PlacementRuleException):
            return self.error_response(
                message=str(exception),
                status=400
            )
        else:
            # Generic error response for unexpected exceptions
            return self.error_response(
                message="An unexpected error occurred. Please try again.",
                status=500
            )


class BaseTemplateView(TemplateView, TeacherRequiredMixin, LoggingMixin):
    """
    Base class for template views with teacher authentication.
    
    Provides:
    - Teacher authentication requirement
    - Structured logging
    - Common context data
    """
    
    def get_context_data(self, **kwargs):
        """Add common context data."""
        context = super().get_context_data(**kwargs)
        
        # Add user and teacher info to context
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
            try:
                from core.models import Teacher
                context['teacher'] = Teacher.objects.get(user=self.request.user)
            except Teacher.DoesNotExist:
                context['teacher'] = None
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Add logging to dispatch."""
        self.log_action(
            f"Page view: {self.__class__.__name__}",
            user=request.user,
            data={'path': request.path}
        )
        return super().dispatch(request, *args, **kwargs)


class BaseFormView(FormView, TeacherRequiredMixin, AjaxResponseMixin, LoggingMixin):
    """
    Base class for form views with AJAX support.
    
    Provides:
    - Teacher authentication requirement
    - AJAX response handling
    - Form validation
    - Structured logging
    """
    
    def form_valid(self, form):
        """Handle valid form submission."""
        self.log_action(
            f"Form valid: {self.__class__.__name__}",
            user=self.request.user,
            data={'form_data': form.cleaned_data}
        )
        
        # Check if this is an AJAX request
        if self.is_ajax(self.request):
            return self.json_response(
                data={'form': 'valid'},
                message="Form submitted successfully"
            )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        self.log_action(
            f"Form invalid: {self.__class__.__name__}",
            user=self.request.user,
            data={'errors': form.errors},
            level='warning'
        )
        
        # Check if this is an AJAX request
        if self.is_ajax(self.request):
            return self.error_response(
                message="Form validation failed",
                errors=form.errors,
                status=400
            )
        return super().form_invalid(form)
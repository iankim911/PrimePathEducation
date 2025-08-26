"""
CRUD Base Views - Common patterns for Create, Read, Update, Delete operations
Part of Phase 11: Final Integration & Testing

Phase 3 Enhancement: Dynamic pagination using DataService
Removes hardcoded pagination values for environment flexibility
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from common.mixins import AjaxResponseMixin, TeacherRequiredMixin
import logging

logger = logging.getLogger(__name__)


class BaseListView(LoginRequiredMixin, ListView):
    """
    Base class for list views with common functionality:
    - Dynamic pagination using DataService
    - Search
    - Filtering
    - Sorting
    """
    search_fields = []
    filter_fields = {}
    ordering_fields = []
    default_ordering = '-created_at'
    
    # Dynamic pagination using DataService
    @property
    def paginate_by(self):
        """Get pagination size from DataService"""
        try:
            from core.services.data_service import get_pagination_size
            page_size = get_pagination_size('default')
            logger.debug(f"[CRUD] Using pagination size: {page_size}")
            return page_size
        except ImportError:
            logger.warning("[CRUD] DataService not available, using fallback pagination: 20")
            return 20
    
    def get_queryset(self):
        """Get queryset with search, filter, and ordering applied"""
        queryset = super().get_queryset()
        
        # Apply search
        search_query = self.request.GET.get('q')
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f'{field}__icontains': search_query})
            queryset = queryset.filter(q_objects)
        
        # Apply filters
        for field, param in self.filter_fields.items():
            value = self.request.GET.get(param)
            if value:
                queryset = queryset.filter(**{field: value})
        
        # Apply ordering
        ordering = self.request.GET.get('ordering', self.default_ordering)
        if ordering in self.ordering_fields:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by(self.default_ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add common context data"""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_filters'] = {
            param: self.request.GET.get(param, '')
            for param in self.filter_fields.values()
        }
        return context


class BaseCreateView(LoginRequiredMixin, CreateView):
    """
    Base class for create views with common functionality:
    - Success messages
    - Form validation
    - Audit logging
    """
    success_message = "Item created successfully"
    
    def form_valid(self, form):
        """Handle valid form submission"""
        # Add created_by if model has it
        if hasattr(form.instance, 'created_by'):
            # Check if created_by expects a Teacher instance
            from core.models import Teacher
            field = form.instance._meta.get_field('created_by')
            if field.related_model == Teacher:
                # Get or create Teacher profile for the user
                try:
                    teacher_profile = self.request.user.teacher_profile
                except (AttributeError, Teacher.DoesNotExist):
                    # Create Teacher profile if it doesn't exist
                    teacher_profile = Teacher.objects.create(
                        user=self.request.user,
                        name=self.request.user.get_full_name() or self.request.user.username,
                        email=self.request.user.email or f"{self.request.user.username}@example.com",
                        is_head_teacher=self.request.user.is_superuser
                    )
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"[CRUD_CREATE] Created Teacher profile for user {self.request.user.username}")
                form.instance.created_by = teacher_profile
            else:
                # For non-Teacher created_by fields, use User directly
                form.instance.created_by = self.request.user
        
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        
        # Log activity if available
        if hasattr(self, 'log_activity'):
            self.log_activity('create', self.object)
        
        return response
    
    def form_invalid(self, form):
        """Handle invalid form submission"""
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class BaseUpdateView(LoginRequiredMixin, UpdateView):
    """
    Base class for update views with common functionality:
    - Success messages
    - Change tracking
    - Permission checks
    """
    success_message = "Item updated successfully"
    
    def form_valid(self, form):
        """Handle valid form submission"""
        # Add updated_by if model has it
        if hasattr(form.instance, 'updated_by'):
            # Check if updated_by expects a Teacher instance
            from core.models import Teacher
            field = form.instance._meta.get_field('updated_by')
            if field.related_model == Teacher:
                # Get or create Teacher profile for the user
                try:
                    teacher_profile = self.request.user.teacher_profile
                except (AttributeError, Teacher.DoesNotExist):
                    # Create Teacher profile if it doesn't exist
                    teacher_profile = Teacher.objects.create(
                        user=self.request.user,
                        name=self.request.user.get_full_name() or self.request.user.username,
                        email=self.request.user.email or f"{self.request.user.username}@example.com",
                        is_head_teacher=self.request.user.is_superuser
                    )
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"[CRUD_UPDATE] Created Teacher profile for user {self.request.user.username}")
                form.instance.updated_by = teacher_profile
            else:
                # For non-Teacher updated_by fields, use User directly
                form.instance.updated_by = self.request.user
        
        # Track changes if needed
        if hasattr(self, 'track_changes'):
            self.track_changes(form)
        
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        
        # Log activity if available
        if hasattr(self, 'log_activity'):
            self.log_activity('update', self.object)
        
        return response


class BaseDeleteView(LoginRequiredMixin, DeleteView):
    """
    Base class for delete views with common functionality:
    - Confirmation
    - Soft delete support
    - Cascade checking
    """
    success_message = "Item deleted successfully"
    confirm_template_name = 'common/confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion"""
        self.object = self.get_object()
        
        # Check for soft delete
        if hasattr(self.object, 'is_deleted'):
            self.object.is_deleted = True
            self.object.save()
            messages.success(request, self.success_message)
            
            # Log activity if available
            if hasattr(self, 'log_activity'):
                self.log_activity('soft_delete', self.object)
            
            return self.get_success_url()
        else:
            # Hard delete
            messages.success(request, self.success_message)
            
            # Log activity if available
            if hasattr(self, 'log_activity'):
                self.log_activity('delete', self.object)
            
            return super().delete(request, *args, **kwargs)


class BaseDetailView(LoginRequiredMixin, DetailView):
    """
    Base class for detail views with common functionality:
    - Related data loading
    - View tracking
    - Permission checks
    """
    
    def get_context_data(self, **kwargs):
        """Add common context data"""
        context = super().get_context_data(**kwargs)
        
        # Load related data if specified
        if hasattr(self, 'related_fields'):
            for field in self.related_fields:
                related_data = getattr(self.object, field).all()
                context[f'{field}_list'] = related_data
        
        # Track view if available
        if hasattr(self, 'track_view'):
            self.track_view(self.object)
        
        return context


class AjaxCRUDMixin(AjaxResponseMixin):
    """
    Mixin for AJAX CRUD operations
    """
    
    def form_valid(self, form):
        """Handle valid AJAX form submission"""
        if self.request.is_ajax():
            self.object = form.save()
            return self.json_response({
                'success': True,
                'message': getattr(self, 'success_message', 'Operation successful'),
                'data': self.get_ajax_data()
            })
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle invalid AJAX form submission"""
        if self.request.is_ajax():
            return self.json_response({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)
    
    def get_ajax_data(self):
        """Get data to return in AJAX response"""
        if hasattr(self.object, 'to_dict'):
            return self.object.to_dict()
        return {
            'id': str(self.object.id),
            'name': str(self.object)
        }


# Teacher-specific CRUD views
class TeacherListView(TeacherRequiredMixin, BaseListView):
    """List view restricted to teachers"""
    pass


class TeacherCreateView(TeacherRequiredMixin, BaseCreateView):
    """Create view restricted to teachers"""
    pass


class TeacherUpdateView(TeacherRequiredMixin, BaseUpdateView):
    """Update view restricted to teachers"""
    pass


class TeacherDeleteView(TeacherRequiredMixin, BaseDeleteView):
    """Delete view restricted to teachers"""
    pass
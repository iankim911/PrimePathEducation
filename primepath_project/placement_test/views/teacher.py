"""
Teacher Dashboard Views - Comprehensive Authentication & Management System

This module provides view classes for teacher dashboard functionality including:
- Teacher authentication with Django User integration
- Dashboard statistics and overview
- Session monitoring and management
- Exam oversight and administration
- Teacher settings and preferences

All views require proper teacher authentication and include comprehensive
error handling, logging, and security measures.
"""
import json
import logging
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone

# Import models
from ..models import Exam, StudentSession, Question, AudioFile
from core.models import Teacher
from common.mixins import AjaxResponseMixin, TeacherRequiredMixin

# Initialize logger
logger = logging.getLogger(__name__)


class TeacherRequiredMixin(LoginRequiredMixin):
    """
    Mixin to ensure only authenticated teachers can access views.
    Checks for both Django User authentication and Teacher profile.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # First check Django authentication
        if not request.user.is_authenticated:
            console_log = {
                "event": "TEACHER_ACCESS_DENIED",
                "reason": "user_not_authenticated",
                "path": request.path,
                "timestamp": str(timezone.now())
            }
            print(f"[TEACHER_AUTH] {json.dumps(console_log)}")
            logger.warning(f"Unauthenticated access attempt to {request.path}")
            return redirect('PlacementTest:teacher_login')
        
        # Check if user has teacher profile
        try:
            teacher = request.user.teacher_profile
            if not teacher.is_active:
                console_log = {
                    "event": "TEACHER_ACCESS_DENIED",
                    "reason": "teacher_inactive",
                    "user_id": request.user.id,
                    "teacher_id": teacher.id,
                    "path": request.path
                }
                print(f"[TEACHER_AUTH] {json.dumps(console_log)}")
                logger.warning(f"Inactive teacher access attempt: {teacher.name}")
                messages.error(request, "Your teacher account is not active.")
                return redirect('PlacementTest:teacher_login')
            
            # Add teacher to request for easy access
            request.teacher = teacher
            
        except Teacher.DoesNotExist:
            console_log = {
                "event": "TEACHER_ACCESS_DENIED",
                "reason": "no_teacher_profile",
                "user_id": request.user.id,
                "username": request.user.username,
                "path": request.path
            }
            print(f"[TEACHER_AUTH] {json.dumps(console_log)}")
            logger.warning(f"User {request.user.username} has no teacher profile")
            messages.error(request, "You do not have teacher access privileges.")
            return redirect('PlacementTest:teacher_login')
        
        return super().dispatch(request, *args, **kwargs)


class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    """
    Main teacher dashboard showing overview statistics and recent activity.
    Provides comprehensive dashboard with exam stats, session monitoring, and quick actions.
    """
    template_name = 'core/teacher_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get dashboard statistics
            total_sessions = StudentSession.objects.count()
            active_exams = Exam.objects.filter(is_active=True).count()
            
            # Get recent sessions (last 10)
            recent_sessions = StudentSession.objects.select_related('exam').order_by('-started_at')[:10]
            
            # Calculate completion rate
            completed_sessions = StudentSession.objects.filter(completed_at__isnull=False).count()
            completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Get sessions from last 7 days
            last_week = timezone.now() - timedelta(days=7)
            weekly_sessions = StudentSession.objects.filter(started_at__gte=last_week).count()
            
            context.update({
                'total_sessions': total_sessions,
                'active_exams': active_exams,
                'recent_sessions': recent_sessions,
                'completion_rate': round(completion_rate, 1),
                'weekly_sessions': weekly_sessions,
                'teacher': self.request.teacher,
                'current_timestamp': int(datetime.now().timestamp())
            })
            
            # Console logging for dashboard access
            dashboard_log = {
                "event": "TEACHER_DASHBOARD_ACCESS",
                "teacher_id": self.request.teacher.id,
                "teacher_name": self.request.teacher.name,
                "stats": {
                    "total_sessions": total_sessions,
                    "active_exams": active_exams,
                    "completion_rate": completion_rate,
                    "weekly_sessions": weekly_sessions
                },
                "timestamp": str(timezone.now())
            }
            print(f"[TEACHER_DASHBOARD] {json.dumps(dashboard_log, indent=2)}")
            logger.info(f"Teacher dashboard accessed by {self.request.teacher.name}")
            
        except Exception as e:
            error_log = {
                "event": "TEACHER_DASHBOARD_ERROR",
                "error": str(e),
                "teacher_id": getattr(self.request, 'teacher', {}).get('id', 'unknown'),
                "timestamp": str(timezone.now())
            }
            print(f"[TEACHER_ERROR] {json.dumps(error_log)}")
            logger.error(f"Teacher dashboard error: {e}")
            
            # Provide fallback data
            context.update({
                'total_sessions': 0,
                'active_exams': 0,
                'recent_sessions': [],
                'completion_rate': 0,
                'weekly_sessions': 0,
                'error_message': 'Unable to load dashboard statistics.'
            })
        
        return context


class TeacherLoginView(View):
    """
    Teacher authentication view with Django User integration.
    Provides secure login with comprehensive error handling and logging.
    """
    template_name = 'core/teacher_login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            try:
                teacher = request.user.teacher_profile
                console_log = {
                    "event": "TEACHER_ALREADY_AUTHENTICATED",
                    "teacher_id": teacher.id,
                    "redirect": "dashboard"
                }
                print(f"[TEACHER_LOGIN] {json.dumps(console_log)}")
                return redirect('PlacementTest:teacher_dashboard')
            except Teacher.DoesNotExist:
                pass
        
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, self.template_name)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                teacher = user.teacher_profile
                if not teacher.is_active:
                    messages.error(request, 'Your teacher account is not active.')
                    logger.warning(f"Login attempt by inactive teacher: {teacher.name}")
                    return render(request, self.template_name)
                
                # Successful login
                login(request, user)
                
                login_log = {
                    "event": "TEACHER_LOGIN_SUCCESS",
                    "teacher_id": teacher.id,
                    "teacher_name": teacher.name,
                    "username": username,
                    "timestamp": str(timezone.now())
                }
                print(f"[TEACHER_LOGIN] {json.dumps(login_log)}")
                logger.info(f"Teacher login successful: {teacher.name}")
                
                messages.success(request, f'Welcome back, {teacher.get_display_name()}!')
                return redirect('PlacementTest:teacher_dashboard')
                
            except Teacher.DoesNotExist:
                messages.error(request, 'This account does not have teacher privileges.')
                logger.warning(f"Login attempt by user without teacher profile: {username}")
                return render(request, self.template_name)
        else:
            messages.error(request, 'Invalid username or password.')
            failed_login_log = {
                "event": "TEACHER_LOGIN_FAILED",
                "username": username,
                "timestamp": str(timezone.now())
            }
            print(f"[TEACHER_LOGIN] {json.dumps(failed_login_log)}")
            logger.warning(f"Failed teacher login attempt: {username}")
            return render(request, self.template_name)


class TeacherLogoutView(View):
    """
    Teacher logout view with comprehensive logging.
    """
    def get(self, request):
        if request.user.is_authenticated:
            try:
                teacher = request.user.teacher_profile
                logout_log = {
                    "event": "TEACHER_LOGOUT",
                    "teacher_id": teacher.id,
                    "teacher_name": teacher.name,
                    "timestamp": str(timezone.now())
                }
                print(f"[TEACHER_LOGOUT] {json.dumps(logout_log)}")
                logger.info(f"Teacher logout: {teacher.name}")
            except Teacher.DoesNotExist:
                pass
        
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('PlacementTest:teacher_login')


class TeacherSessionListView(TeacherRequiredMixin, ListView):
    """
    View for managing and monitoring student test sessions.
    Provides comprehensive session oversight with filtering and statistics.
    """
    template_name = 'core/teacher_sessions.html'
    context_object_name = 'sessions'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = StudentSession.objects.select_related('exam').order_by('-started_at')
        
        # Apply filters from GET parameters
        status_filter = self.request.GET.get('status')
        if status_filter == 'completed':
            queryset = queryset.filter(completed_at__isnull=False)
        elif status_filter == 'in_progress':
            queryset = queryset.filter(completed_at__isnull=True)
        
        date_filter = self.request.GET.get('date')
        if date_filter == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(started_at__date=today)
        elif date_filter == 'week':
            last_week = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(started_at__gte=last_week)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter context
        context.update({
            'current_status_filter': self.request.GET.get('status', ''),
            'current_date_filter': self.request.GET.get('date', ''),
            'teacher': self.request.teacher
        })
        
        return context


class TeacherExamOverviewView(TeacherRequiredMixin, TemplateView):
    """
    View for exam management and oversight.
    Provides comprehensive exam statistics and management tools.
    """
    template_name = 'core/teacher_exams.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get exam statistics
        exams = Exam.objects.annotate(
            session_count=Count('studentsession')
        ).order_by('-created_at')
        
        context.update({
            'exams': exams,
            'total_exams': exams.count(),
            'active_exams': exams.filter(is_active=True).count(),
            'teacher': self.request.teacher
        })
        
        return context


class TeacherSettingsView(TeacherRequiredMixin, TemplateView):
    """
    Teacher settings and preferences view.
    Allows teachers to manage their profile and system preferences.
    """
    template_name = 'core/teacher_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = self.request.teacher
        return context
    
    def post(self, request):
        # Handle settings updates
        teacher = request.teacher
        
        # Update teacher profile fields
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        if name:
            teacher.name = name
        if email:
            teacher.email = email
        if phone:
            teacher.phone = phone
        
        teacher.save()
        
        settings_log = {
            "event": "TEACHER_SETTINGS_UPDATE",
            "teacher_id": teacher.id,
            "fields_updated": [f for f in ['name', 'email', 'phone'] if request.POST.get(f)],
            "timestamp": str(timezone.now())
        }
        print(f"[TEACHER_SETTINGS] {json.dumps(settings_log)}")
        logger.info(f"Teacher settings updated: {teacher.name}")
        
        messages.success(request, 'Settings updated successfully.')
        return redirect('PlacementTest:teacher_settings')
"""
Comprehensive Authentication Utilities for PrimePath Project
Centralizes all authentication logic with robust logging and debugging

This module provides:
1. Backend-specific login functions
2. Comprehensive authentication logging
3. User type detection and routing
4. Authentication debugging utilities
5. OAuth integration support

Author: Claude Assistant
Date: August 25, 2025
Purpose: Fix "multiple authentication backends" error comprehensively
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, Union
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.utils import timezone

# Configure authentication logger
auth_logger = logging.getLogger('primepath.authentication')

# Authentication backend constants
DJANGO_MODEL_BACKEND = 'django.contrib.auth.backends.ModelBackend'
ALLAUTH_BACKEND = 'allauth.account.auth_backends.AuthenticationBackend'


class AuthenticationLogger:
    """Comprehensive authentication event logging"""
    
    @staticmethod
    def log_event(event_type: str, user: Optional[User] = None, 
                  request: Optional[HttpRequest] = None, **kwargs):
        """Log authentication events with comprehensive context"""
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user.id if user else None,
            'username': user.username if user else None,
            'session_key': request.session.session_key if request and hasattr(request, 'session') else None,
            'ip_address': get_client_ip(request) if request else None,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255] if request else None,
            **kwargs
        }
        
        # Console logging with color coding
        if event_type.startswith('SUCCESS'):
            print(f"\033[92m[AUTH_SUCCESS]\033[0m {json.dumps(log_data, indent=2)}")
        elif event_type.startswith('ERROR') or event_type.startswith('FAILURE'):
            print(f"\033[91m[AUTH_ERROR]\033[0m {json.dumps(log_data, indent=2)}")
        elif event_type.startswith('WARNING'):
            print(f"\033[93m[AUTH_WARNING]\033[0m {json.dumps(log_data, indent=2)}")
        else:
            print(f"\033[96m[AUTH_INFO]\033[0m {json.dumps(log_data, indent=2)}")
        
        # Standard logging
        auth_logger.info(json.dumps(log_data))


class UserTypeDetector:
    """Detect user types and appropriate authentication backends"""
    
    @staticmethod
    def detect_user_type(user: User) -> Dict[str, Any]:
        """Detect user type and return authentication context"""
        
        context = {
            'user_id': user.id,
            'username': user.username,
            'user_type': 'UNKNOWN',
            'backend': DJANGO_MODEL_BACKEND,  # Default
            'profile_type': None,
            'has_teacher_profile': False,
            'has_student_profile': False,
            'has_user_profile': False,
            'is_social_auth': False,
            'detection_method': 'PROFILE_ANALYSIS'
        }
        
        try:
            # Check for Teacher profile
            if hasattr(user, 'teacher_profile') and user.teacher_profile:
                context.update({
                    'user_type': 'TEACHER',
                    'profile_type': 'Teacher',
                    'has_teacher_profile': True,
                    'backend': DJANGO_MODEL_BACKEND,
                    'teacher_id': user.teacher_profile.id,
                    'is_head_teacher': user.teacher_profile.is_head_teacher,
                })
                AuthenticationLogger.log_event('INFO_USER_TYPE_DETECTED', user=user, **context)
                return context
                
        except AttributeError:
            pass
        
        try:
            # Check for StudentProfile
            if hasattr(user, 'primepath_student_profile') and user.primepath_student_profile:
                context.update({
                    'user_type': 'STUDENT',
                    'profile_type': 'StudentProfile',
                    'has_student_profile': True,
                    'backend': DJANGO_MODEL_BACKEND,
                    'student_id': user.primepath_student_profile.student_id,
                    'student_profile_id': user.primepath_student_profile.id,
                })
                AuthenticationLogger.log_event('INFO_USER_TYPE_DETECTED', user=user, **context)
                return context
                
        except AttributeError:
            pass
        
        try:
            # Check for UserProfile (OAuth users)
            if hasattr(user, 'profile') and user.profile:
                context.update({
                    'user_type': 'OAUTH_USER',
                    'profile_type': 'UserProfile',
                    'has_user_profile': True,
                    'backend': ALLAUTH_BACKEND,
                    'is_social_auth': True,
                    'account_type': user.profile.account_type if hasattr(user.profile, 'account_type') else 'UNKNOWN',
                })
                AuthenticationLogger.log_event('INFO_USER_TYPE_DETECTED', user=user, **context)
                return context
                
        except AttributeError:
            pass
        
        # Check if user came from social authentication
        try:
            from allauth.socialaccount.models import SocialAccount
            if SocialAccount.objects.filter(user=user).exists():
                context.update({
                    'user_type': 'SOCIAL_USER',
                    'profile_type': 'SocialAccount',
                    'backend': ALLAUTH_BACKEND,
                    'is_social_auth': True,
                    'detection_method': 'SOCIAL_ACCOUNT_LOOKUP'
                })
                AuthenticationLogger.log_event('INFO_USER_TYPE_DETECTED', user=user, **context)
                return context
        except ImportError:
            pass
        
        # Default case - standard Django user
        context.update({
            'user_type': 'DJANGO_USER',
            'profile_type': 'User',
            'backend': DJANGO_MODEL_BACKEND,
            'detection_method': 'DEFAULT_FALLBACK'
        })
        
        AuthenticationLogger.log_event('WARNING_USER_TYPE_FALLBACK', user=user, **context)
        return context


def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def safe_login(request: HttpRequest, user: User, source: str = 'UNKNOWN', **kwargs) -> bool:
    """
    Comprehensive login function with automatic backend detection and logging
    
    Args:
        request: Django HTTP request object
        user: User instance to login
        source: Source of the login attempt (for debugging)
        **kwargs: Additional context for logging
    
    Returns:
        bool: True if login successful, False otherwise
    """
    
    start_time = timezone.now()
    
    # Detect user type and backend
    user_context = UserTypeDetector.detect_user_type(user)
    backend = user_context['backend']
    
    # Log login attempt
    AuthenticationLogger.log_event(
        'INFO_LOGIN_ATTEMPT_START',
        user=user,
        request=request,
        source=source,
        backend=backend,
        user_type=user_context['user_type'],
        **user_context,
        **kwargs
    )
    
    try:
        # Set the backend attribute on the user
        user.backend = backend
        
        # Perform login with specified backend
        django_login(request, user, backend=backend)
        
        # Calculate login duration
        end_time = timezone.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log successful login
        AuthenticationLogger.log_event(
            'SUCCESS_LOGIN_COMPLETE',
            user=user,
            request=request,
            source=source,
            backend=backend,
            duration_ms=duration_ms,
            session_key=request.session.session_key,
            **user_context,
            **kwargs
        )
        
        return True
        
    except Exception as e:
        # Calculate attempt duration
        end_time = timezone.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log login failure
        AuthenticationLogger.log_event(
            'ERROR_LOGIN_FAILED',
            user=user,
            request=request,
            source=source,
            backend=backend,
            error_type=type(e).__name__,
            error_message=str(e),
            duration_ms=duration_ms,
            **user_context,
            **kwargs
        )
        
        return False


def debug_authentication_state(request: HttpRequest, user: Optional[User] = None) -> Dict[str, Any]:
    """
    Comprehensive authentication debugging information
    
    Args:
        request: Django HTTP request object
        user: Optional user instance
    
    Returns:
        dict: Complete authentication debugging context
    """
    
    debug_info = {
        'timestamp': timezone.now().isoformat(),
        'request_info': {
            'method': request.method,
            'path': request.path,
            'user_authenticated': request.user.is_authenticated,
            'session_key': request.session.session_key,
            'session_data': dict(request.session) if hasattr(request, 'session') else {},
        },
        'user_info': {},
        'backend_info': {},
        'profile_info': {},
    }
    
    # User information
    if user:
        debug_info['user_info'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
        
        # Detect user type
        user_context = UserTypeDetector.detect_user_type(user)
        debug_info['profile_info'] = user_context
        
    elif request.user.is_authenticated:
        user = request.user
        debug_info['user_info'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        user_context = UserTypeDetector.detect_user_type(user)
        debug_info['profile_info'] = user_context
    
    # Backend information
    from django.conf import settings
    debug_info['backend_info'] = {
        'configured_backends': getattr(settings, 'AUTHENTICATION_BACKENDS', []),
        'total_backends': len(getattr(settings, 'AUTHENTICATION_BACKENDS', [])),
        'supports_multiple_backends': len(getattr(settings, 'AUTHENTICATION_BACKENDS', [])) > 1,
    }
    
    AuthenticationLogger.log_event(
        'INFO_DEBUG_STATE_CAPTURED',
        user=user,
        request=request,
        debug_context=debug_info
    )
    
    return debug_info


def validate_authentication_setup() -> Dict[str, Any]:
    """
    Validate authentication configuration and return status report
    
    Returns:
        dict: Validation results and recommendations
    """
    
    from django.conf import settings
    
    validation_report = {
        'timestamp': timezone.now().isoformat(),
        'status': 'CHECKING',
        'backends_configured': 0,
        'issues_found': [],
        'recommendations': [],
        'configuration': {}
    }
    
    # Check authentication backends
    backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
    validation_report['backends_configured'] = len(backends)
    validation_report['configuration']['AUTHENTICATION_BACKENDS'] = backends
    
    if len(backends) == 0:
        validation_report['issues_found'].append('No authentication backends configured')
        validation_report['recommendations'].append('Add at least ModelBackend to AUTHENTICATION_BACKENDS')
    elif len(backends) == 1:
        validation_report['status'] = 'SIMPLE_BACKEND'
    else:
        validation_report['status'] = 'MULTIPLE_BACKENDS'
        validation_report['recommendations'].append('Using safe_login() function for all login operations')
    
    # Check for allauth configuration
    if 'allauth.account.auth_backends.AuthenticationBackend' in backends:
        validation_report['configuration']['allauth_enabled'] = True
        if 'allauth' not in settings.INSTALLED_APPS:
            validation_report['issues_found'].append('Allauth backend configured but allauth not in INSTALLED_APPS')
    else:
        validation_report['configuration']['allauth_enabled'] = False
    
    # Check LOGIN_URL and related settings
    validation_report['configuration']['LOGIN_URL'] = getattr(settings, 'LOGIN_URL', '/accounts/login/')
    validation_report['configuration']['LOGIN_REDIRECT_URL'] = getattr(settings, 'LOGIN_REDIRECT_URL', '/')
    validation_report['configuration']['LOGOUT_REDIRECT_URL'] = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
    
    if not validation_report['issues_found']:
        validation_report['status'] = 'HEALTHY'
    
    AuthenticationLogger.log_event(
        'INFO_AUTHENTICATION_VALIDATION_COMPLETE',
        validation_results=validation_report
    )
    
    return validation_report


# Convenience functions for different authentication flows

def teacher_login(request: HttpRequest, user: User, **kwargs) -> bool:
    """Login function specifically for teacher users"""
    return safe_login(request, user, source='TEACHER_LOGIN', **kwargs)


def student_login(request: HttpRequest, user: User, **kwargs) -> bool:
    """Login function specifically for student users"""
    return safe_login(request, user, source='STUDENT_LOGIN', **kwargs)


def oauth_login(request: HttpRequest, user: User, **kwargs) -> bool:
    """Login function specifically for OAuth/social authentication"""
    return safe_login(request, user, source='OAUTH_LOGIN', **kwargs)


def admin_login(request: HttpRequest, user: User, **kwargs) -> bool:
    """Login function specifically for admin users"""
    return safe_login(request, user, source='ADMIN_LOGIN', **kwargs)


# Export main functions
__all__ = [
    'safe_login',
    'teacher_login',
    'student_login',
    'oauth_login', 
    'admin_login',
    'debug_authentication_state',
    'validate_authentication_setup',
    'AuthenticationLogger',
    'UserTypeDetector',
]
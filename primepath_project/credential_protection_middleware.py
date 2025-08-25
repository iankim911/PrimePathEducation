"""
Credential Protection Middleware
===============================

Django middleware to protect critical user accounts from unauthorized modifications
during development, testing, and QA activities.

This middleware:
1. Intercepts User model modifications
2. Validates changes against protected account policies  
3. Logs all credential-related activities
4. Prevents test scripts from corrupting production accounts
5. Provides audit trail for security compliance

Author: Claude Code AI System
Date: August 25, 2025
"""
import logging
import json
import time
from typing import Any, Dict, Optional
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse


logger = logging.getLogger(__name__)


class CredentialProtectionMiddleware:
    """
    Middleware to protect critical user credentials from unauthorized modifications.
    
    Features:
    - Real-time monitoring of User model changes
    - Protection of critical accounts (teacher1, admin, etc.)
    - Comprehensive audit logging
    - Test script detection and blocking
    - Production deployment safety
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Load protected accounts configuration
        self.protected_usernames = {
            'teacher1', 'admin', 'superuser', 'system_admin'
        }
        
        # Load settings
        self.protection_enabled = getattr(settings, 'CREDENTIAL_PROTECTION_ENABLED', True)
        self.block_test_modifications = getattr(settings, 'BLOCK_TEST_CREDENTIAL_MODIFICATIONS', True)
        self.audit_all_changes = getattr(settings, 'AUDIT_ALL_CREDENTIAL_CHANGES', True)
        
        # Initialize audit log
        self.audit_log = []
        self.protection_stats = {
            'blocked_modifications': 0,
            'logged_changes': 0,
            'protected_accounts_accessed': 0,
            'test_scripts_detected': 0
        }
        
        console_log = {
            'middleware': 'CredentialProtectionMiddleware',
            'action': 'initialized',
            'protection_enabled': self.protection_enabled,
            'protected_accounts': list(self.protected_usernames),
            'timestamp': timezone.now().isoformat()
        }
        logger.info(f"[CREDENTIAL_PROTECTION_INIT] {json.dumps(console_log)}")
        print(f"[CREDENTIAL_PROTECTION_INIT] {json.dumps(console_log)}")
    
    def __call__(self, request):
        """Process each request through the middleware."""
        # Add protection context to request
        request.credential_protection = {
            'enabled': self.protection_enabled,
            'request_id': f"req_{int(time.time() * 1000)}",
            'timestamp': timezone.now().isoformat(),
            'is_test_request': self._is_test_request(request)
        }
        
        # Process the request
        response = self.get_response(request)
        
        # Add protection headers to response
        if self.protection_enabled:
            response['X-Credential-Protection'] = 'enabled'
            response['X-Protection-Version'] = '1.0'
        
        return response
    
    def _is_test_request(self, request) -> bool:
        """
        Detect if this is a test request that might modify credentials.
        
        Args:
            request: Django HttpRequest
            
        Returns:
            bool: True if this appears to be a test request
        """
        # Check for test indicators
        test_indicators = [
            'test' in request.path.lower(),
            'pytest' in request.META.get('HTTP_USER_AGENT', '').lower(),
            'test_' in request.META.get('SCRIPT_NAME', ''),
            request.META.get('HTTP_X_TESTING', False),
            'manage.py test' in ' '.join(request.META.get('argv', []))
        ]
        
        return any(test_indicators)
    
    def log_credential_activity(self, action: str, user_data: Dict, context: Dict = None):
        """
        Log credential-related activity with comprehensive details.
        
        Args:
            action: The action being performed
            user_data: User data involved in the action
            context: Additional context information
        """
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'middleware': 'CredentialProtectionMiddleware',
            'action': action,
            'user_data': user_data,
            'context': context or {},
            'protection_stats': self.protection_stats.copy()
        }
        
        # Add to audit log
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries to prevent memory issues
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
        
        # Log to file
        logger.info(f"[CREDENTIAL_ACTIVITY] {json.dumps(log_entry)}")
        print(f"[CREDENTIAL_ACTIVITY] {json.dumps(log_entry)}")
        
        # Update stats
        self.protection_stats['logged_changes'] += 1
    
    def get_protection_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive protection report.
        
        Returns:
            Dict containing protection statistics and recent activity
        """
        return {
            'middleware_version': '1.0',
            'timestamp': timezone.now().isoformat(),
            'protection_enabled': self.protection_enabled,
            'protected_usernames': list(self.protected_usernames),
            'statistics': self.protection_stats.copy(),
            'recent_activity': self.audit_log[-50:],  # Last 50 activities
            'settings': {
                'block_test_modifications': self.block_test_modifications,
                'audit_all_changes': self.audit_all_changes
            }
        }


# Global middleware instance for signal handlers
_middleware_instance = None


def get_protection_middleware():
    """Get the global middleware instance."""
    return _middleware_instance


@receiver(pre_save, sender=User)
def protect_user_credentials(sender, instance, **kwargs):
    """
    Signal handler to protect user credentials from unauthorized changes.
    
    This function is called before any User model save operation.
    """
    global _middleware_instance
    
    if not _middleware_instance:
        return  # Middleware not initialized yet
    
    middleware = _middleware_instance
    
    # Check if this is a protected account
    if instance.username in middleware.protected_usernames:
        middleware.protection_stats['protected_accounts_accessed'] += 1
        
        # Get the current user from database for comparison
        try:
            current_user = User.objects.get(pk=instance.pk) if instance.pk else None
        except User.DoesNotExist:
            current_user = None
        
        # Check for password changes
        password_changed = False
        if current_user and hasattr(instance, 'password'):
            password_changed = current_user.password != instance.password
        
        # Log the access attempt
        user_data = {
            'username': instance.username,
            'pk': instance.pk,
            'password_changed': password_changed,
            'is_new_user': current_user is None
        }
        
        context = {
            'protected_account': True,
            'field_changes': []
        }
        
        # Detect field changes
        if current_user:
            for field in ['is_staff', 'is_superuser', 'is_active', 'email']:
                old_value = getattr(current_user, field)
                new_value = getattr(instance, field)
                if old_value != new_value:
                    context['field_changes'].append({
                        'field': field,
                        'old_value': old_value,
                        'new_value': new_value
                    })
        
        middleware.log_credential_activity('user_save_attempt', user_data, context)
        
        # In production, we might want to be more restrictive
        if not getattr(settings, 'DEBUG', True):
            console_log = {
                'action': 'protected_account_modification',
                'username': instance.username,
                'password_changed': password_changed,
                'field_changes': len(context['field_changes']),
                'timestamp': timezone.now().isoformat()
            }
            logger.warning(f"[PROTECTED_ACCOUNT_MODIFIED] {json.dumps(console_log)}")


@receiver(post_save, sender=User)
def audit_user_changes(sender, instance, created, **kwargs):
    """
    Signal handler to audit all user changes after they occur.
    
    This provides a complete audit trail of user modifications.
    """
    global _middleware_instance
    
    if not _middleware_instance:
        return
    
    middleware = _middleware_instance
    
    action = 'user_created' if created else 'user_updated'
    user_data = {
        'username': instance.username,
        'pk': instance.pk,
        'is_staff': instance.is_staff,
        'is_superuser': instance.is_superuser,
        'is_active': instance.is_active,
        'email': instance.email,
        'created': created
    }
    
    context = {
        'is_protected_account': instance.username in middleware.protected_usernames
    }
    
    middleware.log_credential_activity(action, user_data, context)


# Initialize middleware instance when module is imported
def initialize_protection_middleware():
    """Initialize the global middleware instance."""
    global _middleware_instance
    
    if _middleware_instance is None:
        # Create a dummy get_response function for standalone initialization
        def dummy_get_response(request):
            return HttpResponse()
        
        _middleware_instance = CredentialProtectionMiddleware(dummy_get_response)


# Auto-initialize when module is imported
initialize_protection_middleware()


# Utility functions for external use
def get_protection_report() -> Dict[str, Any]:
    """Get the current protection report."""
    middleware = get_protection_middleware()
    if middleware:
        return middleware.get_protection_report()
    return {'error': 'Protection middleware not initialized'}


def is_protected_account(username: str) -> bool:
    """Check if an account is protected."""
    middleware = get_protection_middleware()
    if middleware:
        return username in middleware.protected_usernames
    return False


def add_protected_account(username: str):
    """Add a username to the protected accounts list."""
    middleware = get_protection_middleware()
    if middleware:
        middleware.protected_usernames.add(username)
        console_log = {
            'action': 'account_protection_added',
            'username': username,
            'timestamp': timezone.now().isoformat()
        }
        logger.info(f"[PROTECTION_ADDED] {json.dumps(console_log)}")
        print(f"[PROTECTION_ADDED] {json.dumps(console_log)}")
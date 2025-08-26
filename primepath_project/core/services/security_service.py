"""
Security Service Layer
Centralized security configuration and credential management
Created: August 26, 2025

This service provides:
- Secure credential management
- Dynamic authentication settings
- Security validation and monitoring
- Secure defaults enforcement
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.management.utils import get_random_secret_key
import logging

logger = logging.getLogger(__name__)


class SecurityService:
    """
    Central security service for credential and authentication management
    Prevents hardcoded credentials and enforces security best practices
    """
    
    # Security constants
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_COMPLEXITY_SCORE = 3  # Minimum complexity score
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Cache keys
    CACHE_PREFIX = 'security:'
    LOGIN_ATTEMPTS_KEY = f'{CACHE_PREFIX}login_attempts:'
    SECURITY_EVENTS_KEY = f'{CACHE_PREFIX}events:'
    
    @classmethod
    def generate_secure_secret_key(cls):
        """Generate a cryptographically secure secret key"""
        return get_random_secret_key()
    
    @classmethod
    def get_secure_secret_key(cls, app_name='django'):
        """
        Get or generate a secure secret key for the application
        Follows security best practices for key management
        """
        # Check environment variable first
        env_key = f'{app_name.upper()}_SECRET_KEY'
        secret_key = os.environ.get(env_key) or os.environ.get('SECRET_KEY')
        
        if secret_key and cls.validate_secret_key(secret_key):
            cls.log_security_event('secret_key_loaded', 'environment', success=True)
            return secret_key
        
        # Check if we're in development
        if settings.DEBUG:
            # Try to load from secure file
            secret_file = settings.BASE_DIR / '.env.secret'
            if secret_file.exists():
                try:
                    with open(secret_file, 'r') as f:
                        file_secret = f.read().strip()
                        if cls.validate_secret_key(file_secret):
                            cls.log_security_event('secret_key_loaded', 'file', success=True)
                            return file_secret
                except Exception as e:
                    logger.error(f"[SECURITY] Error reading secret file: {e}")
            
            # Generate new key for development
            new_secret = cls.generate_secure_secret_key()
            try:
                with open(secret_file, 'w') as f:
                    f.write(new_secret)
                logger.info(f"[SECURITY] Generated new secret key for development")
                cls.log_security_event('secret_key_generated', 'development', success=True)
            except Exception as e:
                logger.error(f"[SECURITY] Could not save secret key: {e}")
            
            return new_secret
        else:
            # Production: Require explicit configuration
            cls.log_security_event('secret_key_missing', 'production', success=False)
            raise ValueError(
                f"SECRET_KEY must be set in production! "
                f"Set {env_key} or SECRET_KEY environment variable with a secure random string."
            )
    
    @classmethod
    def validate_secret_key(cls, secret_key):
        """
        Validate that a secret key meets security requirements
        """
        if not secret_key:
            return False
        
        # Must be at least 50 characters
        if len(secret_key) < 50:
            return False
        
        # Must not be a known insecure default
        insecure_patterns = [
            'django-insecure-',
            'your-secret-key',
            'change-me',
            'insecure',
            '123456',
            'password',
        ]
        
        for pattern in insecure_patterns:
            if pattern.lower() in secret_key.lower():
                return False
        
        return True
    
    @classmethod
    def get_oauth_credentials(cls, provider):
        """
        Get OAuth credentials securely for a specific provider
        Returns None if not properly configured to prevent accidental exposure
        """
        provider = provider.upper()
        
        # Define credential mapping
        credential_mapping = {
            'GOOGLE': {
                'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
                'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI'),
            },
            'KAKAO': {
                'client_id': os.environ.get('KAKAO_REST_API_KEY'),
                'client_secret': os.environ.get('KAKAO_CLIENT_SECRET'),
                'redirect_uri': os.environ.get('KAKAO_REDIRECT_URI'),
            }
        }
        
        if provider not in credential_mapping:
            cls.log_security_event('oauth_provider_unknown', provider, success=False)
            return None
        
        credentials = credential_mapping[provider]
        
        # Validate all credentials are present and secure
        for key, value in credentials.items():
            if not value or cls._is_placeholder_credential(value):
                logger.warning(f"[SECURITY] {provider} OAuth {key} not configured properly")
                cls.log_security_event('oauth_credential_missing', f"{provider}_{key}", success=False)
                return None
        
        cls.log_security_event('oauth_credentials_loaded', provider, success=True)
        return credentials
    
    @classmethod
    def _is_placeholder_credential(cls, credential):
        """Check if a credential is a placeholder/example value"""
        placeholder_patterns = [
            'your-',
            'example',
            'test-',
            'demo-',
            'placeholder',
            'change-me',
            'replace-me',
            'xxx',
            '123456',
        ]
        
        credential_lower = credential.lower()
        return any(pattern in credential_lower for pattern in placeholder_patterns)
    
    @classmethod
    def validate_password_strength(cls, password):
        """
        Validate password strength and return score and feedback
        """
        if not password:
            return 0, ["Password is required"]
        
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= cls.MIN_PASSWORD_LENGTH:
            score += 1
        else:
            feedback.append(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters")
        
        # Complexity checks
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Password must contain uppercase letters")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Password must contain lowercase letters")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Password must contain numbers")
        
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 1
        else:
            feedback.append("Password must contain special characters")
        
        # Length bonus
        if len(password) >= 12:
            score += 1
        
        return score, feedback
    
    @classmethod
    def generate_secure_password(cls, length=12):
        """Generate a cryptographically secure password"""
        import string
        
        # Ensure we have characters from each category
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice('!@#$%^&*()_+-=[]{}|;:,.<>?'),
        ]
        
        # Fill the rest randomly
        all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    @classmethod
    def track_login_attempt(cls, username, ip_address, success=True):
        """
        Track login attempts and implement rate limiting
        """
        cache_key = f"{cls.LOGIN_ATTEMPTS_KEY}{username}:{ip_address}"
        
        if success:
            # Clear failed attempts on successful login
            cache.delete(cache_key)
            cls.log_security_event('login_success', username, ip_address=ip_address)
        else:
            # Track failed attempt
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, timeout=cls.LOCKOUT_DURATION_MINUTES * 60)
            
            cls.log_security_event(
                'login_failure', 
                username, 
                ip_address=ip_address, 
                attempts=attempts,
                success=False
            )
            
            if attempts >= cls.MAX_LOGIN_ATTEMPTS:
                cls.log_security_event(
                    'account_lockout', 
                    username, 
                    ip_address=ip_address,
                    success=False
                )
    
    @classmethod
    def is_account_locked(cls, username, ip_address):
        """
        Check if an account/IP combination is locked due to too many failed attempts
        """
        cache_key = f"{cls.LOGIN_ATTEMPTS_KEY}{username}:{ip_address}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= cls.MAX_LOGIN_ATTEMPTS:
            cls.log_security_event('login_blocked', username, ip_address=ip_address)
            return True
        
        return False
    
    @classmethod
    def log_security_event(cls, event_type, subject, ip_address=None, success=True, **kwargs):
        """
        Log security events for monitoring and auditing
        """
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'subject': subject,
            'ip_address': ip_address,
            'success': success,
            'environment': os.environ.get('ENVIRONMENT', 'development'),
            'additional_data': kwargs
        }
        
        # Log to Django logger
        log_level = logging.INFO if success else logging.WARNING
        logger.log(
            log_level,
            f"[SECURITY_EVENT] {event_type}: {subject} "
            f"{'SUCCESS' if success else 'FAILURE'}"
            f"{f' from {ip_address}' if ip_address else ''}"
        )
        
        # Store in cache for recent events monitoring
        cache_key = f"{cls.SECURITY_EVENTS_KEY}{event_type}"
        recent_events = cache.get(cache_key, [])
        recent_events.append(event_data)
        
        # Keep only last 100 events of each type
        recent_events = recent_events[-100:]
        cache.set(cache_key, recent_events, timeout=3600)  # 1 hour
    
    @classmethod
    def get_security_status(cls):
        """
        Get overall security status and recent events
        """
        status = {
            'secret_key_configured': bool(os.environ.get('SECRET_KEY')),
            'oauth_providers': {},
            'recent_events': {},
            'environment': os.environ.get('ENVIRONMENT', 'development'),
            'debug_mode': settings.DEBUG,
        }
        
        # Check OAuth providers
        for provider in ['GOOGLE', 'KAKAO']:
            credentials = cls.get_oauth_credentials(provider)
            status['oauth_providers'][provider] = {
                'configured': credentials is not None,
                'has_client_id': bool(credentials and credentials.get('client_id')),
                'has_client_secret': bool(credentials and credentials.get('client_secret')),
                'has_redirect_uri': bool(credentials and credentials.get('redirect_uri')),
            }
        
        # Get recent security events
        event_types = ['login_success', 'login_failure', 'account_lockout', 'oauth_credentials_loaded']
        for event_type in event_types:
            cache_key = f"{cls.SECURITY_EVENTS_KEY}{event_type}"
            status['recent_events'][event_type] = cache.get(cache_key, [])
        
        return status
    
    @classmethod
    def create_secure_user(cls, username, email, password=None, **kwargs):
        """
        Create a user account with secure defaults
        """
        if not password:
            password = cls.generate_secure_password()
        
        # Validate password strength
        score, feedback = cls.validate_password_strength(password)
        if score < cls.PASSWORD_COMPLEXITY_SCORE:
            raise ValueError(f"Password not secure enough: {', '.join(feedback)}")
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                **kwargs
            )
            
            cls.log_security_event('user_created', username, success=True)
            logger.info(f"[SECURITY] Secure user created: {username}")
            
            return user, password if not kwargs.get('password') else None
            
        except Exception as e:
            cls.log_security_event('user_creation_failed', username, success=False, error=str(e))
            raise
    
    @classmethod
    def get_client_ip(cls, request):
        """
        Get the real client IP address from request
        Handles proxies and load balancers
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def secure_authenticate(cls, request, username, password):
        """
        Secure authentication with rate limiting and logging
        """
        ip_address = cls.get_client_ip(request)
        
        # Check if account is locked
        if cls.is_account_locked(username, ip_address):
            return None
        
        # Attempt authentication
        user = authenticate(request, username=username, password=password)
        
        # Track the attempt
        cls.track_login_attempt(username, ip_address, success=bool(user))
        
        return user


# Utility functions for easy access
def get_oauth_credentials(provider):
    """Shorthand for getting OAuth credentials"""
    return SecurityService.get_oauth_credentials(provider)

def validate_password_strength(password):
    """Shorthand for password validation"""
    return SecurityService.validate_password_strength(password)

def create_secure_user(username, email, password=None, **kwargs):
    """Shorthand for secure user creation"""
    return SecurityService.create_secure_user(username, email, password, **kwargs)

def log_security_event(event_type, subject, **kwargs):
    """Shorthand for security event logging"""
    return SecurityService.log_security_event(event_type, subject, **kwargs)
"""
Authentication views for teacher login/logout
Handles user authentication with comprehensive logging
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from core.utils.authentication import safe_login, debug_authentication_state
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .models import Teacher
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle teacher login with comprehensive logging
    GET: Display login form
    POST: Process login credentials
    """
    # Log request
    console_log = {
        "view": "login_view",
        "method": request.method,
        "user": str(request.user) if request.user.is_authenticated else "anonymous",
        "path": request.path,
        "next": request.GET.get('next', '')
    }
    logger.info(f"[AUTH_LOGIN] {json.dumps(console_log)}")
    print(f"[AUTH_LOGIN] {json.dumps(console_log)}")
    
    # If already logged in, redirect to application chooser
    if request.user.is_authenticated:
        console_log = {
            "view": "login_view",
            "action": "already_authenticated",
            "user": request.user.username,
            "original_next": request.GET.get('next', ''),
            "redirect": "app_chooser"
        }
        logger.info(f"[AUTH_REDIRECT] {json.dumps(console_log)}")
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Log login attempt
        console_log = {
            "view": "login_view",
            "action": "login_attempt",
            "username": username,
            "remember_me": bool(remember_me)
        }
        logger.info(f"[AUTH_ATTEMPT] {json.dumps(console_log)}")
        print(f"[AUTH_ATTEMPT] {json.dumps(console_log)}")
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Login successful with comprehensive authentication handling
                login_successful = safe_login(
                    request, 
                    user, 
                    source='CORE_AUTH_VIEW',
                    remember_me=remember_me,
                    username_provided=username
                )
                
                if login_successful:
                    # Set session expiry based on remember me
                    if not remember_me:
                        request.session.set_expiry(0)  # Browser close
                    else:
                        request.session.set_expiry(1209600)  # 2 weeks
                
                # Check for Teacher profile
                try:
                    teacher = user.teacher_profile
                    teacher_info = {
                        "id": teacher.id,
                        "name": teacher.name,
                        "is_head": teacher.is_head_teacher
                    }
                except Teacher.DoesNotExist:
                    teacher_info = None
                
                # Log successful login
                console_log = {
                    "view": "login_view",
                    "action": "login_success",
                    "user_id": user.id,
                    "username": user.username,
                    "teacher": teacher_info,
                    "session_expiry": "2_weeks" if remember_me else "browser_close"
                }
                logger.info(f"[AUTH_SUCCESS] {json.dumps(console_log)}")
                print(f"[AUTH_SUCCESS] {json.dumps(console_log)}")
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Always redirect to application chooser page after login
                # This ensures consistent behavior and prevents unwanted redirects
                # to system-specific URLs like /exam-mapping/ or /PlacementTest/
                console_log = {
                    "view": "login_view",
                    "action": "redirect_to_app_chooser",
                    "user": user.username,
                    "original_next": request.POST.get('next', request.GET.get('next', '')),
                    "final_redirect": "/"
                }
                logger.info(f"[AUTH_REDIRECT_FIXED] {json.dumps(console_log)}")
                print(f"[AUTH_REDIRECT_FIXED] {json.dumps(console_log)}")
                return redirect('/')
            else:
                # Account inactive
                console_log = {
                    "view": "login_view",
                    "action": "login_failed",
                    "reason": "account_inactive",
                    "username": username
                }
                logger.warning(f"[AUTH_FAILED] {json.dumps(console_log)}")
                messages.error(request, 'Your account has been disabled. Please contact an administrator.')
        else:
            # Invalid credentials
            console_log = {
                "view": "login_view",
                "action": "login_failed",
                "reason": "invalid_credentials",
                "username": username
            }
            logger.warning(f"[AUTH_FAILED] {json.dumps(console_log)}")
            print(f"[AUTH_FAILED] {json.dumps(console_log)}")
            messages.error(request, 'Invalid username or password. Please try again.')
    
    # Render login template with enhanced context
    next_url = request.GET.get('next', '')
    context = {
        'next': next_url,
        'page_title': 'Teacher Login - PrimePath',
        'template_base': 'core/base_clean.html',  # Explicitly set for template validation
        'is_auth_page': True,  # Flag for authentication pages
        'hide_navigation': True,  # Ensure no navigation is shown
    }
    
    # Enhanced template rendering log
    console_log = {
        "view": "login_view",
        "action": "render_template",
        "template": "core/auth/login.html",
        "base_template": "core/base_clean.html",
        "next_url": next_url,
        "referred_from": request.META.get('HTTP_REFERER', 'direct'),
        "user_agent": request.META.get('HTTP_USER_AGENT', 'unknown')[:100],
        "session_exists": bool(request.session.session_key),
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"[AUTH_RENDER] {json.dumps(console_log)}")
    print(f"[AUTH_RENDER] {json.dumps(console_log)}")
    
    return render(request, 'core/auth/login.html', context)


@login_required
def logout_view(request):
    """
    Handle teacher logout - immediate logout on GET request (industry standard)
    Simplified to avoid CSRF issues and match common UX patterns
    """
    # Get user info before logout
    username = request.user.username
    user_id = request.user.id
    full_name = request.user.get_full_name()
    
    # Enhanced logging with more details
    console_log = {
        "view": "logout_view",
        "method": request.method,
        "action": "logout_initiated",
        "user_id": user_id,
        "username": username,
        "full_name": full_name,
        "session_key": request.session.session_key[:8] if request.session.session_key else None,
        "ip_address": request.META.get('REMOTE_ADDR', 'unknown'),
        "user_agent": request.META.get('HTTP_USER_AGENT', 'unknown')[:100],
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"[AUTH_LOGOUT_INITIATED] {json.dumps(console_log)}")
    print(f"[AUTH_LOGOUT_INITIATED] {json.dumps(console_log)}")
    
    # Perform logout immediately (GET request friendly)
    logout(request)
    
    # Log successful logout
    console_log = {
        "view": "logout_view",
        "action": "logout_completed",
        "user_id": user_id,
        "username": username,
        "full_name": full_name,
        "method": request.method,
        "redirect_to": "/login/",
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"[AUTH_LOGOUT_SUCCESS] {json.dumps(console_log)}")
    print(f"[AUTH_LOGOUT_SUCCESS] {json.dumps(console_log)}")
    
    # Add success message
    messages.success(request, f'You have been successfully logged out. Goodbye, {full_name or username}!')
    
    # Log the redirect
    console_log = {
        "view": "logout_view",
        "action": "redirecting_to_app_chooser",
        "from_user": username,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"[AUTH_LOGOUT_REDIRECT] {json.dumps(console_log)}")
    print(f"[AUTH_LOGOUT_REDIRECT] {json.dumps(console_log)}")
    
    return redirect('/')


@login_required
def profile_view(request):
    """
    Display and edit teacher profile
    Uses neutral base template since user hasn't chosen application yet
    """
    # Log profile access
    console_log = {
        "view": "profile_view",
        "action": "profile_accessed",
        "user": request.user.username,
        "method": request.method,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"[AUTH_PROFILE_ACCESS] {json.dumps(console_log)}")
    print(f"[AUTH_PROFILE_ACCESS] {json.dumps(console_log)}")
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        # Create Teacher profile if it doesn't exist
        teacher = Teacher.objects.create(
            user=request.user,
            name=request.user.get_full_name() or request.user.username,
            email=request.user.email or f"{request.user.username}@example.com"
        )
        
        console_log = {
            "view": "profile_view",
            "action": "created_teacher_profile",
            "user_id": request.user.id,
            "teacher_id": teacher.id
        }
        logger.info(f"[AUTH_PROFILE] {json.dumps(console_log)}")
        print(f"[AUTH_PROFILE] {json.dumps(console_log)}")
    
    if request.method == 'POST':
        # Update profile
        teacher.name = request.POST.get('name', teacher.name)
        teacher.email = request.POST.get('email', teacher.email)
        teacher.phone = request.POST.get('phone', teacher.phone)
        teacher.save()
        
        # Also update User email if changed
        if request.user.email != teacher.email:
            request.user.email = teacher.email
            request.user.save()
        
        console_log = {
            "view": "profile_view",
            "action": "profile_updated",
            "user_id": request.user.id,
            "teacher_id": teacher.id,
            "updated_fields": ["name", "email", "phone"]
        }
        logger.info(f"[AUTH_PROFILE_UPDATE] {json.dumps(console_log)}")
        print(f"[AUTH_PROFILE_UPDATE] {json.dumps(console_log)}")
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('core:profile')
    
    context = {
        'teacher': teacher,
        'user': request.user,
        'page_title': 'My Profile - PrimePath'
    }
    return render(request, 'core/auth/profile.html', context)


def check_auth_status(request):
    """
    AJAX endpoint to check authentication status
    Returns JSON with auth status and user info
    """
    if request.user.is_authenticated:
        try:
            teacher = request.user.teacher_profile
            teacher_data = {
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'is_head_teacher': teacher.is_head_teacher
            }
        except Teacher.DoesNotExist:
            teacher_data = None
        
        response_data = {
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'full_name': request.user.get_full_name(),
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser
            },
            'teacher': teacher_data
        }
    else:
        response_data = {
            'authenticated': False,
            'user': None,
            'teacher': None
        }
    
    console_log = {
        "view": "check_auth_status",
        "authenticated": response_data['authenticated'],
        "user": request.user.username if request.user.is_authenticated else None
    }
    logger.debug(f"[AUTH_STATUS_CHECK] {json.dumps(console_log)}")
    
    return JsonResponse(response_data)
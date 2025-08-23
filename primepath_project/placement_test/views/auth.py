"""
Placement Test Authentication Views
Shares authentication with RoutineTest - same users, same credentials
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from core.models import Teacher
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def get_user_role(user):
    """
    Determine user role (same logic as RoutineTest)
    Admin: is_superuser=True
    Teacher: has Teacher profile
    Student: everyone else
    """
    if user.is_superuser:
        return 'admin'
    
    try:
        teacher = user.teacher_profile
        return 'teacher'
    except:
        return 'student'

@csrf_protect
@require_http_methods(["GET", "POST"])
def placement_login(request):
    """
    Placement Test login - shares credentials with RoutineTest
    Redirects to appropriate dashboard based on role
    """
    # Log request
    logger.info(f"[PlacementTest Login] Method: {request.method}, User: {request.user}")
    
    # If already logged in, redirect to placement test index
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/PlacementTest/')
        logger.info(f"User {request.user.username} already authenticated, redirecting to {next_url}")
        return redirect(next_url)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember', False)
        
        logger.info(f"Login attempt for username: {username}")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember:
                request.session.set_expiry(0)  # Browser close
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            logger.info(f"User {username} logged in successfully")
            messages.success(request, f'Welcome back, {username}!')
            
            # Get next URL or redirect based on role
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Default redirect to PlacementTest index
            return redirect('PlacementTest:index')
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, 'Invalid username or password.')
    
    # Render login template
    context = {
        'page_title': 'Login - PrimePath',
        'app_name': 'PlacementTest'
    }
    
    return render(request, 'placement_test/auth/login.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def placement_logout(request):
    """
    Handle logout and redirect to login page
    """
    username = request.user.username
    logout(request)
    logger.info(f"User {username} logged out from PlacementTest")
    messages.success(request, 'You have been logged out successfully.')
    return redirect('PlacementTest:login')
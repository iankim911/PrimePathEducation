"""
RoutineTest Authentication Views
Handles Admin, Teacher, and Student login with role-based redirects
BUILDER: Day 1 - Authentication System
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

# BUILDER: Role definitions (hardcoded for MVP)
USER_ROLES = {
    'ADMIN': 'admin',
    'TEACHER': 'teacher', 
    'STUDENT': 'student'
}

def get_user_role(user):
    """
    BUILDER: Determine user role
    Admin: is_superuser=True
    Teacher: has Teacher profile
    Student: everyone else
    """
    if user.is_superuser:
        return USER_ROLES['ADMIN']
    
    try:
        teacher = user.teacher_profile
        return USER_ROLES['TEACHER']
    except:
        return USER_ROLES['STUDENT']

@csrf_protect
@require_http_methods(["GET", "POST"])
def routinetest_login(request):
    """
    BUILDER: RoutineTest login with role-based redirect
    Copied from core/auth_views.py and modified for roles
    """
    # If already logged in, redirect based on role
    if request.user.is_authenticated:
        role = get_user_role(request.user)
        
        # Role-based redirect
        if role == USER_ROLES['ADMIN']:
            return redirect('RoutineTest:admin_dashboard')
        elif role == USER_ROLES['TEACHER']:
            return redirect('RoutineTest:teacher_dashboard')
        else:
            return redirect('RoutineTest:student_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Log attempt
        logger.info(f"[ROUTINETEST_LOGIN] Attempt: {username}")
        
        # Authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            # Login successful
            login(request, user)
            
            # Set session expiry
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            # Get role and redirect accordingly
            role = get_user_role(user)
            
            # Log success
            logger.info(f"[ROUTINETEST_LOGIN] Success: {username} as {role}")
            messages.success(request, f'Welcome to RoutineTest, {user.get_full_name() or user.username}!')
            
            # Role-based redirect
            if role == USER_ROLES['ADMIN']:
                return redirect('RoutineTest:admin_dashboard')
            elif role == USER_ROLES['TEACHER']:
                return redirect('RoutineTest:teacher_dashboard')
            else:
                return redirect('RoutineTest:student_dashboard')
        else:
            # Login failed
            logger.warning(f"[ROUTINETEST_LOGIN] Failed: {username}")
            messages.error(request, 'Invalid username or password.')
    
    # Render login template
    context = {
        'page_title': 'Login - PrimePath',
        'app_name': 'RoutineTest'
    }
    
    return render(request, 'primepath_routinetest/auth/login_brand.html', context)

@login_required
def routinetest_logout(request):
    """
    BUILDER: Handle logout for RoutineTest
    """
    username = request.user.username
    logout(request)
    messages.success(request, f'You have been logged out from RoutineTest.')
    logger.info(f"[ROUTINETEST_LOGOUT] User logged out: {username}")
    return redirect('RoutineTest:login')

# BUILDER: Dashboard views (shells for now)
@login_required
def admin_dashboard(request):
    """
    BUILDER: Admin dashboard shell
    Day 1: Basic template only
    """
    # Check if admin
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('RoutineTest:login')
    
    context = {
        'page_title': 'Admin Dashboard - RoutineTest',
        'user_role': 'admin',
        'username': request.user.username
    }
    return render(request, 'primepath_routinetest/dashboards/admin_dashboard.html', context)

@login_required  
def teacher_dashboard(request):
    """
    BUILDER: Teacher dashboard shell
    Day 1: Basic template only
    """
    # Check if teacher
    role = get_user_role(request.user)
    if role != USER_ROLES['TEACHER']:
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('RoutineTest:login')
    
    try:
        teacher = request.user.teacher_profile
        teacher_name = teacher.name
    except:
        teacher_name = request.user.username
    
    context = {
        'page_title': 'Teacher Dashboard - RoutineTest',
        'user_role': 'teacher',
        'teacher_name': teacher_name
    }
    return render(request, 'primepath_routinetest/dashboards/teacher_dashboard.html', context)

@login_required
def student_dashboard(request):
    """
    BUILDER: Student dashboard shell
    Day 1: Basic template only
    """
    # Students are everyone who isn't admin or teacher
    context = {
        'page_title': 'Student Dashboard - RoutineTest',
        'user_role': 'student',
        'student_name': request.user.get_full_name() or request.user.username
    }
    return render(request, 'primepath_routinetest/dashboards/student_dashboard.html', context)
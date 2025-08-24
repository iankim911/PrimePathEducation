from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from primepath_student.models import StudentProfile
import re


@csrf_protect
@require_http_methods(["GET", "POST"])
def student_register(request):
    """Student registration view"""
    if request.method == 'POST':
        # Get form data
        phone_number = request.POST.get('phone_number', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Validation
        errors = []
        
        # Phone number validation
        phone_regex = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_regex.match(phone_number):
            errors.append("Please enter a valid phone number")
        
        # Check if phone number already exists
        if StudentProfile.objects.filter(phone_number=phone_number).exists():
            errors.append("This phone number is already registered")
        
        # Student ID validation
        if not student_id:
            # Generate one if not provided
            student_id = StudentProfile.generate_student_id()
        elif StudentProfile.objects.filter(student_id=student_id).exists():
            errors.append("This student ID is already taken")
        
        # Password validation
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if password != password_confirm:
            errors.append("Passwords do not match")
        
        # Name validation
        if not first_name or not last_name:
            errors.append("Please provide both first and last name")
        
        if errors:
            return render(request, 'primepath_student/auth/register.html', {
                'errors': errors,
                'form_data': request.POST
            })
        
        try:
            with transaction.atomic():
                # Create user account
                username = f"student_{phone_number}"  # Use phone as basis for username
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create student profile
                student_profile = StudentProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    phone_number=phone_number
                )
                
                # Log the user in
                login(request, user)
                messages.success(request, f"Welcome {first_name}! Your Student ID is: {student_id}")
                return redirect('primepath_student:dashboard')
                
        except Exception as e:
            messages.error(request, "Registration failed. Please try again.")
            return render(request, 'primepath_student/auth/register.html', {
                'errors': [str(e)],
                'form_data': request.POST
            })
    
    return render(request, 'primepath_student/auth/register.html')


@csrf_protect
@require_http_methods(["GET", "POST"])
def student_login(request):
    """Student login view"""
    if request.user.is_authenticated:
        # Check if user has student profile
        if hasattr(request.user, 'primepath_student_profile'):
            return redirect('primepath_student:dashboard')
        else:
            logout(request)
            messages.error(request, "You don't have a student account. Please register.")
            return redirect('primepath_student:register')
    
    if request.method == 'POST':
        login_id = request.POST.get('login_id', '').strip()  # Can be phone or student ID
        password = request.POST.get('password', '')
        
        # Try to find student by phone or student ID
        student_profile = None
        try:
            # First try phone number
            if re.match(r'^\+?1?\d{9,15}$', login_id):
                student_profile = StudentProfile.objects.get(phone_number=login_id)
            else:
                # Try student ID
                student_profile = StudentProfile.objects.get(student_id=login_id)
        except StudentProfile.DoesNotExist:
            messages.error(request, "Invalid login credentials")
            return render(request, 'primepath_student/auth/login.html')
        
        if student_profile:
            # Authenticate user
            user = authenticate(username=student_profile.user.username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                
                # Redirect to next page if specified
                next_page = request.GET.get('next', 'primepath_student:dashboard')
                return redirect(next_page)
            else:
                messages.error(request, "Invalid password")
        else:
            messages.error(request, "Invalid login credentials")
    
    return render(request, 'primepath_student/auth/login.html')


def student_logout(request):
    """Student logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('primepath_student:login')


@csrf_protect
@require_http_methods(["GET", "POST"])
def kakao_login(request):
    """Kakao login integration (placeholder for now)"""
    # This will be implemented when Kakao OAuth is set up
    messages.info(request, "Kakao login coming soon!")
    return redirect('primepath_student:login')
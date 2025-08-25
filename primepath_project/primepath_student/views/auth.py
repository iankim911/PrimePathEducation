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
        # Get form data - support both old and new field names
        phone_number = request.POST.get('phone_number', '').strip()
        student_id = request.POST.get('student_id', '').strip() or request.POST.get('username', '').strip()
        
        # Handle password fields
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        password = request.POST.get('password', '') or password1
        password_confirm = request.POST.get('password_confirm', '') or password2
        
        # Handle name fields
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        
        # If full_name provided but not first/last, split it
        if full_name and not (first_name and last_name):
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
        
        # Get optional fields
        grade = request.POST.get('grade', '')
        
        # Validation
        errors = []
        
        # Phone number validation - clean it first
        phone_number = re.sub(r'[^\d]', '', phone_number)  # Remove non-digits
        if not re.match(r'^\d{10,15}$', phone_number):
            errors.append("Please enter a valid phone number")
        
        # Check if phone number already exists
        if StudentProfile.objects.filter(phone_number=phone_number).exists():
            errors.append("This phone number is already registered")
        
        # Student ID validation
        if not student_id:
            errors.append("Please provide a Student ID")
        elif StudentProfile.objects.filter(student_id=student_id).exists():
            errors.append("This student ID is already taken")
        
        # Password validation
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if password != password_confirm:
            errors.append("Passwords do not match")
        
        # Name validation
        if not first_name:
            errors.append("Please provide your name")
        
        if errors:
            return render(request, 'primepath_student/auth/login_register_modern.html', {
                'errors': errors,
                'form_data': request.POST,
                'mode': 'signup'
            })
        
        try:
            with transaction.atomic():
                # Create user account
                username = student_id  # Use student_id as username
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name or first_name
                )
                
                # Create student profile
                student_profile = StudentProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    phone_number=phone_number,
                    grade=grade if grade else None
                )
                
                # Log the user in
                login(request, user)
                messages.success(request, f"Welcome {first_name}! Your Student ID is: {student_id}")
                return redirect('primepath_student:dashboard')
                
        except Exception as e:
            messages.error(request, "Registration failed. Please try again.")
            return render(request, 'primepath_student/auth/login_register_modern.html', {
                'errors': [str(e)],
                'form_data': request.POST,
                'mode': 'signup'
            })
    
    # GET request - show modern form in signup mode
    return render(request, 'primepath_student/auth/login_register_modern.html', {
        'mode': 'signup'
    })


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
        # Support both field names
        login_id = request.POST.get('phone_number', '').strip() or request.POST.get('login_id', '').strip()
        password = request.POST.get('password', '')
        
        # Clean phone number if it looks like one
        login_id_clean = re.sub(r'[^\d]', '', login_id)  # Remove non-digits for comparison
        
        # Try to find student by phone or student ID
        student_profile = None
        try:
            # First try phone number (cleaned)
            if re.match(r'^\d{10,15}$', login_id_clean):
                student_profile = StudentProfile.objects.get(phone_number=login_id_clean)
            else:
                # Try student ID (original input)
                student_profile = StudentProfile.objects.get(student_id=login_id)
        except StudentProfile.DoesNotExist:
            messages.error(request, "Invalid login credentials")
            return render(request, 'primepath_student/auth/login_register_modern.html', {
                'mode': 'login',
                'errors': ['Invalid phone number/student ID or password']
            })
        
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
                return render(request, 'primepath_student/auth/login_register_modern.html', {
                    'mode': 'login',
                    'errors': ['Invalid password']
                })
        else:
            messages.error(request, "Invalid login credentials")
            return render(request, 'primepath_student/auth/login_register_modern.html', {
                'mode': 'login',
                'errors': ['Invalid login credentials']
            })
    
    # GET request - show modern form in login mode
    return render(request, 'primepath_student/auth/login_register_modern.html', {
        'mode': 'login'
    })


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
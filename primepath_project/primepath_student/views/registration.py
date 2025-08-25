from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from core.utils.authentication import student_login as safe_student_login
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from ..forms import StudentRegistrationForm, StudentPasswordResetForm, StudentLoginForm
from ..models import StudentProfile
import json


@csrf_protect
@never_cache
def student_register(request):
    """Student registration view with comprehensive form"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Debug: Check what username will be set
                student_id = form.cleaned_data.get('student_id')
                print(f"[REGISTRATION_DEBUG] Attempting to create user with student_id: {student_id}")
                
                # Check if user already exists
                from django.contrib.auth.models import User
                if User.objects.filter(username=student_id).exists():
                    print(f"[REGISTRATION_DEBUG] ERROR: User with username '{student_id}' already exists!")
                    messages.error(request, f'Student ID "{student_id}" is already taken. Please choose another.')
                    return render(request, 'primepath_student/auth/register.html', {
                        'form': form,
                        'title': 'Create Student Account'
                    })
                
                print(f"[REGISTRATION_DEBUG] Username '{student_id}' is available, proceeding with form.save()")
                user = form.save()
                print(f"[REGISTRATION_DEBUG] User created successfully: {user.username} (ID: {user.id})")
                messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
                
                # Auto-login the user with comprehensive authentication handling
                username = form.cleaned_data['student_id']
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                if user:
                    login_successful = safe_student_login(
                        request, 
                        user, 
                        registration_form_data=form.cleaned_data
                    )
                    if login_successful:
                        return redirect('primepath_student:dashboard')
                    else:
                        messages.error(request, "Account created but login failed. Please try logging in manually.")
                        return redirect('primepath_student:login')
                else:
                    return redirect('primepath_student:login')
                    
            except Exception as e:
                print(f"[REGISTRATION_DEBUG] Exception during registration: {str(e)}")
                print(f"[REGISTRATION_DEBUG] Exception type: {type(e)}")
                import traceback
                print(f"[REGISTRATION_DEBUG] Full traceback:")
                traceback.print_exc()
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Extract form errors for better display
            print(f"[REGISTRATION_DEBUG] Form is invalid!")
            print(f"[REGISTRATION_DEBUG] Form errors: {form.errors}")
            print(f"[REGISTRATION_DEBUG] Non-field errors: {form.non_field_errors()}")
            
            for field, errors in form.errors.items():
                for error in errors:
                    error_msg = f'{field}: {error}'
                    print(f"[REGISTRATION_DEBUG] Adding error message: {error_msg}")
                    messages.error(request, error_msg)
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'primepath_student/auth/register.html', {
        'form': form,
        'title': 'Create Student Account'
    })


@csrf_exempt
def check_availability(request):
    """AJAX endpoint to check if student ID, phone, or email is available"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        check_type = data.get('type')
        value = data.get('value', '').strip()
        
        if not value:
            return JsonResponse({'available': True})
        
        available = True
        message = ''
        
        if check_type == 'student_id':
            if StudentProfile.objects.filter(student_id=value).exists() or User.objects.filter(username=value).exists():
                available = False
                message = 'This Student ID is already taken'
        
        elif check_type == 'phone':
            if StudentProfile.objects.filter(phone_number=value).exists():
                available = False
                message = 'This phone number is already registered'
        
        elif check_type == 'email':
            if User.objects.filter(email=value).exists():
                available = False
                message = 'This email address is already registered'
        
        return JsonResponse({
            'available': available,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_protect
@never_cache
def student_login(request):
    """Enhanced student login supporting ID and phone"""
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            
            # Authenticate using username (which is student_id)
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                login_successful = safe_student_login(
                    request, 
                    auth_user, 
                    login_form_data=form.cleaned_data
                )
                
                if login_successful:
                    # Set session expiry based on remember_me
                    if not form.cleaned_data.get('remember_me', False):
                        request.session.set_expiry(0)  # Browser session only
                    
                    messages.success(request, f'Welcome back, {auth_user.first_name}!')
                    return redirect('primepath_student:dashboard')
                else:
                    messages.error(request, 'Login failed. Please try again.')
            else:
                messages.error(request, 'Invalid login credentials.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = StudentLoginForm()
    
    return render(request, 'primepath_student/auth/login.html', {
        'form': form,
        'title': 'Student Login'
    })


@csrf_protect
def password_reset_request(request):
    """Enhanced password reset supporting multiple recovery methods"""
    if request.method == 'POST':
        form = StudentPasswordResetForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data.get('users_cache', [])
            contact_method = form.cleaned_data['contact_method']
            
            for user in users:
                # Generate reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Build reset URL
                reset_url = request.build_absolute_uri(
                    reverse('primepath_student:password_reset_confirm', kwargs={
                        'uidb64': uid,
                        'token': token
                    })
                )
                
                # Get student profile for additional info
                try:
                    profile = user.primepath_student_profile
                except:
                    profile = None
                
                # Determine email to send to
                if contact_method == 'student_id' and profile and profile.recovery_email:
                    send_to_email = profile.recovery_email
                else:
                    send_to_email = user.email
                
                # Send reset email
                if send_to_email:
                    subject = 'PrimePath - Password Reset'
                    html_message = render_to_string('primepath_student/emails/password_reset.html', {
                        'user': user,
                        'reset_url': reset_url,
                        'contact_method': contact_method,
                        'profile': profile,
                    })
                    plain_message = strip_tags(html_message)
                    
                    try:
                        send_mail(
                            subject,
                            plain_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [send_to_email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        
                        messages.success(request, 
                            f'Password reset instructions have been sent to {send_to_email}')
                    except Exception as e:
                        messages.error(request, 'Unable to send reset email. Please try again.')
                
                # For phone method, also log the attempt (in production, you'd send SMS)
                if contact_method == 'phone':
                    messages.info(request, 
                        'SMS password reset is coming soon. Please use email recovery for now.')
            
            return redirect('primepath_student:login')
    else:
        form = StudentPasswordResetForm()
    
    return render(request, 'primepath_student/auth/password_reset.html', {
        'form': form,
        'title': 'Reset Password'
    })


def password_reset_confirm(request, uidb64, token):
    """Handle password reset confirmation"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password2:
                if password1 == password2:
                    user.set_password(password1)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully!')
                    return redirect('primepath_student:login')
                else:
                    messages.error(request, 'Passwords do not match.')
            else:
                messages.error(request, 'Please fill in both password fields.')
        
        return render(request, 'primepath_student/auth/password_reset_confirm.html', {
            'validlink': True,
            'title': 'Set New Password'
        })
    else:
        return render(request, 'primepath_student/auth/password_reset_confirm.html', {
            'validlink': False,
            'title': 'Invalid Reset Link'
        })
"""
User Registration Views
Multi-step registration with Google and Kakao OAuth support
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
import json
import requests
import secrets
import hashlib
from datetime import datetime, timedelta

from core.forms.registration import (
    BasicRegistrationForm, PersonalInfoForm, AddressForm,
    EducationalInfoForm, ParentGuardianForm, AdditionalInfoForm,
    SocialAuthCompleteProfileForm
)
from core.models.user_profile import (
    UserProfile, SocialAuthToken, EmailVerification, 
    PhoneVerification, LoginHistory
)
from core.oauth_config import (
    get_google_auth_url, get_kakao_auth_url,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    GOOGLE_TOKEN_URL, GOOGLE_USER_INFO_URL,
    KAKAO_CLIENT_ID, KAKAO_CLIENT_SECRET, KAKAO_REDIRECT_URI,
    KAKAO_TOKEN_URL, KAKAO_USER_INFO_URL
)

class RegistrationChoiceView(TemplateView):
    """Landing page for registration with social login options"""
    template_name = 'registration/choice.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Generate state parameter for OAuth security
        state = secrets.token_urlsafe(32)
        self.request.session['oauth_state'] = state
        
        context['google_auth_url'] = get_google_auth_url(state)
        context['kakao_auth_url'] = get_kakao_auth_url(state)
        
        return context


class MultiStepRegistrationView(View):
    """Multi-step registration wizard for email registration"""
    
    FORMS = [
        ('basic', BasicRegistrationForm),
        ('personal', PersonalInfoForm),
        ('address', AddressForm),
        ('educational', EducationalInfoForm),
        ('parent', ParentGuardianForm),
        ('additional', AdditionalInfoForm),
    ]
    
    TEMPLATES = {
        'basic': 'registration/step1_basic.html',
        'personal': 'registration/step2_personal.html',
        'address': 'registration/step3_address.html',
        'educational': 'registration/step4_educational.html',
        'parent': 'registration/step5_parent.html',
        'additional': 'registration/step6_additional.html',
    }
    
    def get(self, request, step='basic'):
        # Get current step form
        form_class = dict(self.FORMS)[step]
        
        # Check if we have saved data for this step
        saved_data = request.session.get(f'registration_{step}', {})
        form = form_class(initial=saved_data)
        
        # Calculate progress
        current_step_index = [f[0] for f in self.FORMS].index(step)
        progress = int((current_step_index / len(self.FORMS)) * 100)
        
        # Skip parent step for non-students
        if step == 'parent':
            account_type = request.session.get('registration_basic', {}).get('account_type')
            if account_type and account_type != 'STUDENT':
                return redirect('registration:step', step='additional')
        
        context = {
            'form': form,
            'step': step,
            'progress': progress,
            'current_step': current_step_index + 1,
            'total_steps': len(self.FORMS),
            'can_skip': step in ['additional'],  # Allow skipping optional steps
        }
        
        return render(request, self.TEMPLATES[step], context)
    
    def post(self, request, step='basic'):
        form_class = dict(self.FORMS)[step]
        form = form_class(request.POST)
        
        if form.is_valid():
            # Save form data to session
            request.session[f'registration_{step}'] = form.cleaned_data
            
            # Get next step
            steps = [f[0] for f in self.FORMS]
            current_index = steps.index(step)
            
            # Check if this is the last step
            if current_index == len(steps) - 1:
                return self.complete_registration(request)
            
            # Move to next step
            next_step = steps[current_index + 1]
            
            # Skip parent step for non-students
            if next_step == 'parent':
                account_type = request.session.get('registration_basic', {}).get('account_type')
                if account_type and account_type != 'STUDENT':
                    next_step = 'additional'
            
            return redirect('registration:step', step=next_step)
        
        # Form has errors
        current_step_index = [f[0] for f in self.FORMS].index(step)
        progress = int((current_step_index / len(self.FORMS)) * 100)
        
        context = {
            'form': form,
            'step': step,
            'progress': progress,
            'current_step': current_step_index + 1,
            'total_steps': len(self.FORMS),
        }
        
        return render(request, self.TEMPLATES[step], context)
    
    @transaction.atomic
    def complete_registration(self, request):
        """Complete the registration process"""
        try:
            # Gather all form data
            basic_data = request.session.get('registration_basic', {})
            personal_data = request.session.get('registration_personal', {})
            address_data = request.session.get('registration_address', {})
            educational_data = request.session.get('registration_educational', {})
            parent_data = request.session.get('registration_parent', {})
            additional_data = request.session.get('registration_additional', {})
            
            # Create user account
            user = User.objects.create_user(
                username=basic_data['username'],
                email=basic_data['email'],
                password=basic_data['password1']
            )
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                account_type=basic_data['account_type'],
                auth_provider='EMAIL',
                terms_accepted=basic_data.get('terms_accepted', False),
                privacy_policy_accepted=basic_data.get('privacy_policy_accepted', False),
                **personal_data,
                **address_data,
                **educational_data,
                **parent_data,
                **additional_data
            )
            
            # Create email verification token
            EmailVerification.objects.create(
                user=user,
                email=user.email
            )
            
            # Clear session data
            for step, _ in self.FORMS:
                request.session.pop(f'registration_{step}', None)
            
            # Log the user in
            login(request, user)
            
            # Send welcome email (implement email sending)
            # send_welcome_email(user)
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('registration:complete')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('registration:step', step='basic')


class GoogleOAuthCallbackView(View):
    """Handle Google OAuth callback"""
    
    def get(self, request):
        # Check state parameter for security
        state = request.GET.get('state')
        saved_state = request.session.get('oauth_state')
        
        if not state or state != saved_state:
            messages.error(request, 'Invalid OAuth state. Please try again.')
            return redirect('registration:choice')
        
        # Get authorization code
        code = request.GET.get('code')
        if not code:
            messages.error(request, 'Authorization failed. Please try again.')
            return redirect('registration:choice')
        
        try:
            # Exchange code for access token
            token_response = requests.post(GOOGLE_TOKEN_URL, data={
                'code': code,
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'redirect_uri': GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code',
            })
            
            token_data = token_response.json()
            
            if 'access_token' not in token_data:
                raise Exception('Failed to get access token')
            
            # Get user info
            user_response = requests.get(
                GOOGLE_USER_INFO_URL,
                headers={'Authorization': f"Bearer {token_data['access_token']}"}
            )
            
            user_info = user_response.json()
            
            # Check if user already exists
            existing_user = User.objects.filter(email=user_info['email']).first()
            
            if existing_user:
                # User exists, log them in
                if hasattr(existing_user, 'profile'):
                    # Update OAuth token
                    SocialAuthToken.objects.update_or_create(
                        user=existing_user,
                        provider='GOOGLE',
                        defaults={
                            'access_token': token_data['access_token'],
                            'refresh_token': token_data.get('refresh_token', ''),
                            'token_expiry': datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                        }
                    )
                    
                    login(request, existing_user)
                    return redirect('dashboard')
            
            # Create new user
            with transaction.atomic():
                # Create Django user
                username = user_info['email'].split('@')[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=user_info['email'],
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', '')
                )
                
                # Create user profile
                profile = UserProfile.objects.create(
                    user=user,
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    auth_provider='GOOGLE',
                    social_id=user_info['id'],
                    profile_photo_url=user_info.get('picture', ''),
                    email_verified=user_info.get('verified_email', False)
                )
                
                # Save OAuth token
                SocialAuthToken.objects.create(
                    user=user,
                    provider='GOOGLE',
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token', ''),
                    token_expiry=datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                )
                
                # Log the user in
                login(request, user)
                
                # Redirect to profile completion
                return redirect('registration:complete_profile')
                
        except Exception as e:
            messages.error(request, f'OAuth authentication failed: {str(e)}')
            return redirect('registration:choice')


class KakaoOAuthCallbackView(View):
    """Handle Kakao OAuth callback"""
    
    def get(self, request):
        # Check state parameter for security
        state = request.GET.get('state')
        saved_state = request.session.get('oauth_state')
        
        if state and state != saved_state:
            messages.error(request, 'Invalid OAuth state. Please try again.')
            return redirect('registration:choice')
        
        # Get authorization code
        code = request.GET.get('code')
        if not code:
            messages.error(request, 'Authorization failed. Please try again.')
            return redirect('registration:choice')
        
        try:
            # Exchange code for access token
            token_response = requests.post(KAKAO_TOKEN_URL, data={
                'grant_type': 'authorization_code',
                'client_id': KAKAO_CLIENT_ID,
                'client_secret': KAKAO_CLIENT_SECRET,
                'redirect_uri': KAKAO_REDIRECT_URI,
                'code': code,
            })
            
            token_data = token_response.json()
            
            if 'access_token' not in token_data:
                raise Exception('Failed to get access token')
            
            # Get user info
            user_response = requests.get(
                KAKAO_USER_INFO_URL,
                headers={'Authorization': f"Bearer {token_data['access_token']}"}
            )
            
            user_info = user_response.json()
            
            # Extract user data from Kakao response
            kakao_account = user_info.get('kakao_account', {})
            properties = user_info.get('properties', {})
            
            email = kakao_account.get('email')
            
            # Check if user already exists
            if email:
                existing_user = User.objects.filter(email=email).first()
            else:
                # Try to find by social ID
                existing_profile = UserProfile.objects.filter(
                    social_id=str(user_info['id']),
                    auth_provider='KAKAO'
                ).first()
                existing_user = existing_profile.user if existing_profile else None
            
            if existing_user:
                # User exists, log them in
                SocialAuthToken.objects.update_or_create(
                    user=existing_user,
                    provider='KAKAO',
                    defaults={
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data.get('refresh_token', ''),
                        'token_expiry': datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                    }
                )
                
                login(request, existing_user)
                return redirect('dashboard')
            
            # Create new user
            with transaction.atomic():
                # Generate username from Kakao nickname or ID
                nickname = properties.get('nickname', f"kakao_{user_info['id']}")
                username = nickname.replace(' ', '_').lower()
                
                # Ensure unique username
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email or f"{username}@kakao.local",
                )
                
                # Parse Kakao profile data
                gender_map = {'male': 'M', 'female': 'F'}
                gender = gender_map.get(kakao_account.get('gender'), '')
                
                # Create user profile
                profile = UserProfile.objects.create(
                    user=user,
                    first_name=nickname,
                    auth_provider='KAKAO',
                    social_id=str(user_info['id']),
                    profile_photo_url=properties.get('profile_image', ''),
                    email_verified=kakao_account.get('is_email_verified', False),
                    gender=gender,
                    phone_number=kakao_account.get('phone_number', '')
                )
                
                # Save OAuth token
                SocialAuthToken.objects.create(
                    user=user,
                    provider='KAKAO',
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token', ''),
                    token_expiry=datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                )
                
                # Log the user in
                login(request, user)
                
                # Redirect to profile completion
                return redirect('registration:complete_profile')
                
        except Exception as e:
            messages.error(request, f'Kakao authentication failed: {str(e)}')
            return redirect('registration:choice')


class CompleteProfileView(FormView):
    """Complete profile after social login"""
    template_name = 'registration/complete_profile.html'
    form_class = SocialAuthCompleteProfileForm
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('registration:choice')
        
        # Check if profile is already complete
        if hasattr(request.user, 'profile'):
            if request.user.profile.profile_completion_percentage >= 80:
                return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'profile'):
            kwargs['instance'] = self.request.user.profile
        return kwargs
    
    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        
        messages.success(self.request, 'Profile completed successfully!')
        return redirect('dashboard')


class RegistrationCompleteView(TemplateView):
    """Registration completion page"""
    template_name = 'registration/complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            context['profile'] = self.request.user.profile
            context['completion_percentage'] = self.request.user.profile.profile_completion_percentage
        
        return context
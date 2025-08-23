"""
Custom adapters for django-allauth to integrate with existing user system
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from core.models import UserProfile, SocialAuthToken
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for allauth"""
    
    def is_open_for_signup(self, request):
        """Allow signups through social accounts"""
        return True
    
    def save_user(self, request, user, form, commit=True):
        """Save user and create UserProfile"""
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
            # Create or update UserProfile
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.get_full_name() or user.email.split('@')[0],
                    'email': user.email,
                    'auth_provider': 'GOOGLE',
                }
            )
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for allauth"""
    
    def pre_social_login(self, request, sociallogin):
        """Handle social login before user is logged in"""
        # Check if user exists with this email
        if sociallogin.is_existing:
            return
            
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                # Try to connect to existing user with same email
                user = User.objects.filter(email=email).first()
                if user:
                    sociallogin.connect(request, user)
        except Exception as e:
            logger.error(f"Error in pre_social_login: {e}")
    
    def save_user(self, request, sociallogin, form=None):
        """Save user from social login"""
        user = super().save_user(request, sociallogin, form)
        
        # Extract user data from social account
        extra_data = sociallogin.account.extra_data
        
        # Update or create UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'name': extra_data.get('name', user.email.split('@')[0]),
                'email': user.email,
                'auth_provider': 'GOOGLE',
            }
        )
        
        if not created:
            # Update existing profile
            profile.name = extra_data.get('name', profile.name)
            profile.auth_provider = 'GOOGLE'
            profile.save()
        
        # Save social auth tokens
        if hasattr(sociallogin, 'token'):
            SocialAuthToken.objects.update_or_create(
                user=user,
                provider='GOOGLE',
                defaults={
                    'access_token': sociallogin.token.token,
                    'refresh_token': sociallogin.token.token_secret if hasattr(sociallogin.token, 'token_secret') else '',
                    'expires_at': sociallogin.token.expires_at if hasattr(sociallogin.token, 'expires_at') else None,
                }
            )
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """Populate user instance from social account data"""
        user = super().populate_user(request, sociallogin, data)
        
        # Set additional user fields from Google data
        extra_data = sociallogin.account.extra_data
        if extra_data:
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
            
        return user
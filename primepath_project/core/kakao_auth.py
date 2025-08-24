"""
KakaoTalk OAuth Authentication Backend
Handles KakaoTalk login integration
"""
import requests
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from .models import Teacher

logger = logging.getLogger(__name__)
User = get_user_model()


class KakaoOAuth2Backend(BaseBackend):
    """Custom authentication backend for KakaoTalk OAuth"""
    
    def authenticate(self, request, kakao_access_token=None, **kwargs):
        """
        Authenticate user with KakaoTalk access token
        """
        if not kakao_access_token:
            return None
            
        try:
            # Get user info from Kakao
            user_info = self.get_kakao_user_info(kakao_access_token)
            if not user_info:
                return None
            
            # Extract user data
            kakao_id = str(user_info.get('id'))
            kakao_account = user_info.get('kakao_account', {})
            profile = kakao_account.get('profile', {})
            
            # Get or create user
            user = self.get_or_create_user(
                kakao_id=kakao_id,
                email=kakao_account.get('email'),
                nickname=profile.get('nickname', f'kakao_{kakao_id}'),
                profile_image=profile.get('profile_image_url')
            )
            
            return user
            
        except Exception as e:
            logger.error(f"KakaoTalk authentication error: {e}")
            return None
    
    def get_kakao_user_info(self, access_token):
        """
        Fetch user information from Kakao API
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        response = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get Kakao user info: {response.text}")
            return None
    
    def get_or_create_user(self, kakao_id, email, nickname, profile_image):
        """
        Get existing user or create new one from Kakao data
        """
        # Try to find user by username (kakao_id)
        username = f'kakao_{kakao_id}'
        
        try:
            user = User.objects.get(username=username)
            # Update user info if changed
            if email and user.email != email:
                user.email = email
                user.save()
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email or f'{username}@kakao.local',
                first_name=nickname
            )
            
            # Create Teacher profile for new user
            Teacher.objects.create(
                user=user,
                name=nickname,
                email=email or f'{username}@kakao.local',
                profile_image_url=profile_image,
                is_kakao_user=True,
                kakao_id=str(kakao_id)
            )
            
        return user
    
    def get_user(self, user_id):
        """
        Get user by ID for session
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
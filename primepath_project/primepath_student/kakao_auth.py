"""
KakaoTalk OAuth Authentication for Students
Handles student authentication via Kakao OAuth 2.0
"""
import requests
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from primepath_student.models import StudentProfile
from django.db import transaction

logger = logging.getLogger(__name__)
User = get_user_model()


class StudentKakaoOAuth2Backend(BaseBackend):
    """Authentication backend for student Kakao login"""
    
    def authenticate(self, request, kakao_access_token=None, **kwargs):
        """Authenticate student with Kakao access token"""
        if not kakao_access_token:
            return None
            
        try:
            # Get user info from Kakao
            user_info = self.get_kakao_user_info(kakao_access_token)
            if not user_info:
                logger.error("Failed to get Kakao user info")
                return None
            
            # Extract user data
            kakao_id = str(user_info.get('id'))
            kakao_account = user_info.get('kakao_account', {})
            profile = kakao_account.get('profile', {})
            
            # Try to find existing student by kakao_id
            try:
                student_profile = StudentProfile.objects.get(kakao_id=kakao_id)
                return student_profile.user
            except StudentProfile.DoesNotExist:
                # Create new student account
                return self.create_student_from_kakao(
                    kakao_id=kakao_id,
                    email=kakao_account.get('email'),
                    nickname=profile.get('nickname', f'student_{kakao_id[:8]}'),
                    profile_image=profile.get('profile_image_url'),
                    phone_number=None  # No phone number in basic OAuth scope
                )
                
        except Exception as e:
            logger.error(f"Student Kakao authentication error: {e}")
            return None
    
    def get_kakao_user_info(self, access_token):
        """Fetch user information from Kakao API"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        response = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers=headers,
            params={
                'property_keys': '["kakao_account.profile", "kakao_account.email"]'
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get Kakao user info: {response.text}")
            return None
    
    def create_student_from_kakao(self, kakao_id, email, nickname, profile_image, phone_number):
        """Create new student account from Kakao data"""
        with transaction.atomic():
            # Generate unique username
            username = f'kakao_student_{kakao_id}'
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email or f'{username}@kakao.local',
                first_name=nickname.split()[0] if nickname else 'Student',
                last_name=nickname.split()[-1] if nickname and len(nickname.split()) > 1 else ''
            )
            
            # Generate student ID
            student_id = StudentProfile.generate_student_id()
            
            # Create student profile
            student_profile = StudentProfile.objects.create(
                user=user,
                student_id=student_id,
                kakao_id=kakao_id,
                phone_number=f'kakao_{kakao_id[:10]}',  # Placeholder phone number
                recovery_email=email,
                email_verified=bool(email),
                phone_verified=False  # No phone verification from Kakao basic OAuth
            )
            
            logger.info(f"Created new student account from Kakao: {username}")
            return user
    
    def get_user(self, user_id):
        """Get user by ID for session"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
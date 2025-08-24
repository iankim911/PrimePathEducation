"""
Registration URL Configuration
"""
from django.urls import path
from core.views_registration import (
    RegistrationChoiceView,
    MultiStepRegistrationView,
    GoogleOAuthCallbackView,
    KakaoOAuthCallbackView,
    CompleteProfileView,
    RegistrationCompleteView,
)

app_name = 'registration'

urlpatterns = [
    # Registration choice (landing page)
    path('register/', RegistrationChoiceView.as_view(), name='choice'),
    
    # Multi-step email registration
    path('register/<str:step>/', MultiStepRegistrationView.as_view(), name='step'),
    
    # OAuth callbacks for registration flow
    path('auth/google/callback/', GoogleOAuthCallbackView.as_view(), name='google_callback'),
    path('auth/kakao/callback/register/', KakaoOAuthCallbackView.as_view(), name='kakao_callback'),
    
    # Profile completion
    path('complete-profile/', CompleteProfileView.as_view(), name='complete_profile'),
    path('registration-complete/', RegistrationCompleteView.as_view(), name='complete'),
]
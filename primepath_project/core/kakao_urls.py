"""
KakaoTalk OAuth URL Configuration
Add these to your main urls.py
"""
from django.urls import path
from . import kakao_views

kakao_urlpatterns = [
    # KakaoTalk OAuth URLs
    path('auth/kakao/login/', kakao_views.kakao_login, name='kakao_login'),
    path('auth/kakao/callback/', kakao_views.kakao_callback, name='kakao_callback'),
    path('auth/kakao/logout/', kakao_views.kakao_logout, name='kakao_logout'),
    path('auth/kakao/js-login/', kakao_views.kakao_javascript_login, name='kakao_js_login'),
]
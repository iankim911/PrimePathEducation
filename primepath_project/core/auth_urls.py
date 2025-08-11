"""
Authentication URLs for teacher login/logout/profile
Provides standard Django authentication endpoints
"""
from django.urls import path
from .auth_views import login_view, logout_view, profile_view, check_auth_status

# Authentication URL patterns
urlpatterns = [
    # Login/Logout
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Profile
    path('profile/', profile_view, name='profile'),
    
    # AJAX endpoints
    path('api/auth/status/', check_auth_status, name='auth_status'),
]
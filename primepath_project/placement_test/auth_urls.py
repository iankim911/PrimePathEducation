"""
Placement Test Authentication URLs
"""
from django.urls import path
from .views import auth

urlpatterns = [
    path('login/', auth.placement_login, name='login'),
    path('logout/', auth.placement_logout, name='logout'),
]
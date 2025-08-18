"""
BUILDER: RoutineTest Authentication URLs
Day 1 - Login, Logout, and Dashboard routes
"""
from django.urls import path
from .views import auth

urlpatterns = [
    # Authentication
    path('login/', auth.routinetest_login, name='login'),
    path('logout/', auth.routinetest_logout, name='logout'),
    
    # Dashboard views
    path('admin/dashboard/', auth.admin_dashboard, name='admin_dashboard'),
    path('teacher/dashboard/', auth.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', auth.student_dashboard, name='student_dashboard'),
]
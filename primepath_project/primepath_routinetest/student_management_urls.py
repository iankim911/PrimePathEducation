"""
Phase 2: Student Management URLs for Teachers
URLs for teachers to manage students in their classes
"""
from django.urls import path
from .views import student_management_v2 as views

urlpatterns = [
    # Student management for teachers
    path('class/<str:class_code>/students/', views.manage_class_students, name='manage_class_students'),
    path('class/<str:class_code>/students/bulk-assign/', views.bulk_assign_students, name='bulk_assign_students'),
    path('students/search/', views.search_students, name='search_students'),
    path('students/create/', views.create_student_account, name='create_student'),
    path('students/', views.student_list, name='student_list'),
]
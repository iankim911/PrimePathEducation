"""
Exam Management URLs
URLs for exam creation, editing, and management
"""
from django.urls import path
from . import views
from .views import exam

urlpatterns = [
    # Exam management
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.create_exam, name='create_exam'),
    path('exams/check-version/', views.check_exam_version, name='check_exam_version'),
    path('exams/<uuid:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exams/<uuid:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('exams/<uuid:exam_id>/preview/', views.preview_exam, name='preview_exam'),
    path('exams/<uuid:exam_id>/audio/add/', views.add_audio, name='add_audio'),
    path('exams/<uuid:exam_id>/questions/', views.manage_questions, name='manage_questions'),
    path('exams/<uuid:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    
    # Answer Keys Library API endpoints
    path('api/teacher/copyable-classes/', exam.get_teacher_copyable_classes, name='get_teacher_copyable_classes'),
    path('api/exams/<uuid:exam_id>/copy/', exam.copy_exam, name='copy_exam'),
]
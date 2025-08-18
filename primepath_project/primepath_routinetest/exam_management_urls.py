"""
BUILDER: Day 4 - Exam Management URLs
URL patterns for exam upload, assignment, and administration
"""

from django.urls import path
from .views import exam_management

urlpatterns = [
    # Admin URLs
    path('admin/exams/upload/', exam_management.upload_exam, name='upload_exam'),
    path('admin/exams/<uuid:exam_id>/answer-key/', exam_management.set_answer_key, name='set_answer_key'),
    
    # Teacher URLs
    path('teacher/exams/', exam_management.list_available_exams, name='list_available_exams'),
    path('teacher/exams/assign/', exam_management.assign_exam_to_class, name='assign_exam_to_class'),
    path('teacher/exams/assign-individual/', exam_management.assign_exam_to_students, name='assign_exam_to_students'),
    path('teacher/assignments/<uuid:assignment_id>/extend/', exam_management.extend_deadline, name='extend_deadline'),
    
    # Student URLs
    path('student/exams/', exam_management.view_assigned_exams, name='view_assigned_exams'),
    path('student/exams/<uuid:exam_id>/start/', exam_management.start_exam, name='start_exam'),
    path('student/exams/<uuid:exam_id>/auto-save/', exam_management.auto_save_progress, name='auto_save_progress'),
    path('student/exams/<uuid:exam_id>/submit/', exam_management.submit_exam, name='submit_exam'),
]
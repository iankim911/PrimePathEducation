"""
BUILDER: Day 2 & 3 - Class and Student Management URLs
"""
from django.urls import path
from .views import class_management, student_management

urlpatterns = [
    # Admin class management
    path('admin/classes/', class_management.manage_classes, name='manage_classes'),
    path('admin/classes/create/', class_management.create_class, name='create_class'),
    path('admin/classes/<uuid:class_id>/assign-teacher/', class_management.assign_teacher, name='assign_teacher'),
    path('admin/classes/<uuid:class_id>/remove-teacher/', class_management.remove_teacher, name='remove_teacher'),
    path('admin/classes/<uuid:class_id>/delete/', class_management.delete_class, name='delete_class'),
    
    # Teacher student management (Day 3)
    path('teacher/dashboard/', student_management.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/classes/', student_management.teacher_classes, name='teacher_classes'),
    path('teacher/classes/<uuid:class_id>/students/', student_management.view_class_students, name='view_class_students'),
    path('teacher/students/enroll/', student_management.enroll_student, name='enroll_student'),
    path('teacher/students/<uuid:enrollment_id>/unenroll/', student_management.unenroll_student, name='unenroll_student'),
    path('teacher/students/<uuid:student_id>/update/', student_management.update_student, name='update_student'),
    path('teacher/students/search/', student_management.search_students, name='search_students'),
    path('teacher/students/bulk-enroll/', student_management.bulk_enroll_students, name='bulk_enroll'),
]
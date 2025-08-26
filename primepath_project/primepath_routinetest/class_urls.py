"""
BUILDER: Day 2 & 3 - Class and Student Management URLs
Includes admin Classes & Teachers management interface
"""
from django.urls import path
from .views import class_management, student_management, class_details, admin_classes_teachers

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
    
    # Class Details with Student Management and Exam Schedule
    path('class/<str:class_code>/details/', class_details.class_details, name='class_details'),
    path('class/<str:class_code>/add-student/', class_details.add_student_to_class, name='add_student_to_class'),
    path('class/<str:class_code>/remove-student/', class_details.remove_student_from_class, name='remove_student_from_class'),
    path('class/<str:class_code>/start-exam/', class_details.start_exam_for_class, name='start_exam_for_class'),
    path('class/<str:class_code>/launch-preview/', class_details.launch_teacher_preview, name='launch_teacher_preview'),
    path('class/<str:class_code>/delete-exam/', class_details.delete_exam_from_schedule, name='delete_exam_from_schedule'),
    path('student/<uuid:student_id>/details/', class_details.get_student_details, name='get_student_details'),
    
    # NEW: Class-Contextual Exam Selection API Endpoints
    path('api/class/<str:class_code>/available-exams/', class_details.get_available_exams_for_class, name='get_available_exams_for_class'),
    path('api/class/<str:class_code>/assign-exams/', class_details.assign_exam_to_schedule, name='assign_exam_to_schedule'),
    
    # Admin Classes & Teachers Management
    path('admin/classes-teachers/', admin_classes_teachers.admin_classes_teachers, name='admin_classes_teachers'),
    path('admin/classes-teachers/create-class/', admin_classes_teachers.create_class, name='admin_create_class'),
    path('admin/classes-teachers/delete-class/', admin_classes_teachers.delete_class, name='admin_delete_class'),
    path('admin/classes-teachers/set-curriculum/', admin_classes_teachers.set_curriculum_recommendation, name='admin_set_curriculum_recommendation'),
    path('admin/classes-teachers/assign-teacher/', admin_classes_teachers.assign_teacher_to_class, name='admin_assign_teacher_to_class'),
    path('admin/classes-teachers/remove-teacher/', admin_classes_teachers.remove_teacher_from_class, name='admin_remove_teacher_from_class'),
    path('admin/classes-teachers/handle-request/', admin_classes_teachers.handle_access_request, name='admin_handle_access_request'),
    path('admin/classes-teachers/pending-requests-count/', admin_classes_teachers.get_pending_requests_count, name='admin_get_pending_requests_count'),
]
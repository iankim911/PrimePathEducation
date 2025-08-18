"""
ARCHITECT: Day 4 - Exam Management Core Architecture
Based on PRD Section 5: Exam Management System
"""

EXAM_MANAGEMENT_ARCHITECTURE = {
    "models": {
        "RoutineExam": {
            "fields": [
                "id (UUID)",
                "name (CharField)",
                "exam_type (CharField: 'monthly_review', 'quarterly')",
                "curriculum_level (CharField from 44 levels)",
                "academic_year (CharField)",
                "quarter (CharField: Q1, Q2, Q3, Q4)",
                "pdf_file (FileField)",
                "answer_key (JSONField)",
                "audio_files (ManyToMany)",
                "version (IntegerField)",
                "created_by (ForeignKey: User)",
                "created_at (DateTimeField)",
                "updated_at (DateTimeField)",
                "is_active (BooleanField)"
            ],
            "methods": [
                "get_questions()",
                "validate_answer_key()",
                "clone_exam()",
                "get_statistics()"
            ],
            "indexes": [
                "curriculum_level, quarter, exam_type",
                "academic_year, quarter",
                "is_active"
            ]
        },
        
        "ExamAssignment": {
            "fields": [
                "id (UUID)",
                "exam (ForeignKey: RoutineExam)",
                "class_assigned (ForeignKey: Class)",
                "assigned_students (ManyToMany: Student, through='StudentExamAssignment')",
                "assigned_by (ForeignKey: Teacher)",
                "deadline (DateTimeField)",
                "allow_multiple_attempts (BooleanField default=True)",
                "is_bulk_assignment (BooleanField)",
                "created_at (DateTimeField)",
                "updated_at (DateTimeField)"
            ],
            "methods": [
                "is_past_deadline()",
                "get_completion_rate()",
                "extend_deadline()",
                "get_student_progress()"
            ],
            "constraints": [
                "unique_together: exam, class_assigned, deadline"
            ]
        },
        
        "StudentExamAssignment": {
            "fields": [
                "id (UUID)",
                "student (ForeignKey: Student)",
                "exam_assignment (ForeignKey: ExamAssignment)",
                "status (CharField: 'assigned', 'in_progress', 'completed', 'missed')",
                "assigned_at (DateTimeField)",
                "started_at (DateTimeField, nullable)",
                "completed_at (DateTimeField, nullable)"
            ],
            "methods": [
                "can_take_exam()",
                "mark_as_started()",
                "mark_as_completed()"
            ]
        },
        
        "ExamAttempt": {
            "fields": [
                "id (UUID)",
                "student (ForeignKey: Student)",
                "exam (ForeignKey: RoutineExam)",
                "assignment (ForeignKey: StudentExamAssignment)",
                "attempt_number (IntegerField)",
                "answers (JSONField)",
                "score (DecimalField)",
                "time_spent (DurationField)",
                "started_at (DateTimeField)",
                "submitted_at (DateTimeField, nullable)",
                "is_submitted (BooleanField)",
                "auto_saved_data (JSONField)",
                "violation_flags (JSONField)"
            ],
            "methods": [
                "calculate_score()",
                "auto_save()",
                "submit()",
                "flag_violation()"
            ],
            "indexes": [
                "student, exam, attempt_number",
                "is_submitted, submitted_at"
            ]
        }
    },
    
    "views": {
        "admin": [
            "upload_exam (POST: /admin/exams/upload/)",
            "manage_exam_matrix (GET: /admin/exams/matrix/)",
            "edit_answer_key (POST: /admin/exams/<id>/answer-key/)",
            "clone_exam (POST: /admin/exams/<id>/clone/)"
        ],
        
        "teacher": [
            "list_available_exams (GET: /teacher/exams/)",
            "assign_exam_to_class (POST: /teacher/exams/assign/)",
            "assign_exam_to_students (POST: /teacher/exams/assign-individual/)",
            "view_assignment_progress (GET: /teacher/assignments/<id>/progress/)",
            "extend_deadline (POST: /teacher/assignments/<id>/extend/)"
        ],
        
        "student": [
            "view_assigned_exams (GET: /student/exams/)",
            "start_exam (POST: /student/exams/<id>/start/)",
            "auto_save_progress (POST: /student/exams/<id>/auto-save/)",
            "submit_exam (POST: /student/exams/<id>/submit/)",
            "view_exam_results (GET: /student/exams/<id>/results/)"
        ]
    },
    
    "services": {
        "ExamService": {
            "methods": [
                "create_exam(pdf_file, exam_type, curriculum_level, quarter)",
                "validate_pdf_format(pdf_file)",
                "extract_questions_from_pdf(pdf_file)",
                "save_answer_key(exam_id, answer_key)",
                "get_exams_by_curriculum(curriculum_level, quarter)"
            ]
        },
        
        "AssignmentService": {
            "methods": [
                "assign_to_class(exam_id, class_id, deadline, teacher)",
                "assign_to_students(exam_id, student_ids, deadline, teacher)",
                "check_deadline_status(assignment_id)",
                "get_student_assignments(student_id, status=None)",
                "bulk_assign_differentiated(assignments_dict)"
            ]
        },
        
        "AttemptService": {
            "methods": [
                "start_attempt(student_id, exam_id, assignment_id)",
                "auto_save_progress(attempt_id, answers)",
                "submit_attempt(attempt_id)",
                "calculate_score(attempt_id)",
                "get_best_score(student_id, exam_id)",
                "get_average_score(student_id, exam_id)"
            ]
        },
        
        "AntiCheatService": {
            "methods": [
                "detect_tab_switch(attempt_id)",
                "detect_copy_paste(attempt_id)",
                "flag_violation(attempt_id, violation_type)",
                "get_violation_report(attempt_id)"
            ]
        }
    },
    
    "permissions": {
        "admin": [
            "Full CRUD on all exams",
            "Access to all exam statistics",
            "Can override any assignment"
        ],
        "teacher": [
            "Read access to exam library",
            "Create/modify assignments for their classes",
            "View progress for their students only",
            "Cannot modify exam content or answer keys"
        ],
        "student": [
            "View only assigned exams",
            "Take exams before deadline",
            "View own results and history",
            "No access to answer keys"
        ]
    },
    
    "technical_requirements": {
        "auto_save": {
            "interval": "60 seconds",
            "storage": "LocalStorage + Backend",
            "sync": "On network recovery"
        },
        "anti_cheat": {
            "copy_paste": "Disabled via JavaScript",
            "tab_switch": "Detect and warn",
            "right_click": "Disabled during exam",
            "fullscreen": "Optional enforcement"
        },
        "scoring": {
            "calculation": "Immediate on submission",
            "display": "Show score and correct answers",
            "tracking": "Best score AND average"
        }
    }
}
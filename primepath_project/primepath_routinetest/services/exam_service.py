"""
Service for exam management and operations.
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from core.exceptions import ValidationException, ExamConfigurationException
from core.constants import DEFAULT_OPTIONS_COUNT, DEFAULT_QUESTION_POINTS
from ..models import Exam, Question, AudioFile, TeacherClassAssignment
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ExamService:
    """Handles exam creation, management, and question operations."""
    
    @staticmethod
    @transaction.atomic
    def create_exam(
        exam_data: Dict[str, Any],
        pdf_file: Optional[UploadedFile] = None,
        audio_files: Optional[List[UploadedFile]] = None,
        audio_names: Optional[List[str]] = None
    ) -> Exam:
        """
        Create a new exam with associated files.
        
        Args:
            exam_data: Dictionary containing exam information
            pdf_file: PDF file upload
            audio_files: List of audio file uploads
            audio_names: List of display names for audio files
            
        Returns:
            Created Exam instance
        """
        import json
        
        # Helper function to serialize dates/times
        def serialize_datetime(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, 'strftime'):
                return obj.strftime('%H:%M:%S')
            return str(obj) if obj else None
        
        # Log exam creation attempt
        console_log = {
            "service": "ExamService",
            "action": "create_exam_start",
            "exam_name": exam_data.get('name'),
            "exam_type": exam_data.get('exam_type', 'REVIEW'),
            "time_period_month": exam_data.get('time_period_month'),  # Phase 2
            "time_period_quarter": exam_data.get('time_period_quarter'),  # Phase 2
            "academic_year": exam_data.get('academic_year'),  # Phase 2
            "class_codes": exam_data.get('class_codes', []),  # Phase 3
            "class_codes_count": len(exam_data.get('class_codes', [])),  # Phase 3
            "has_instructions": bool(exam_data.get('instructions')),  # General instructions (kept at exam level)
            "curriculum_level_id": exam_data.get('curriculum_level_id'),
            "has_pdf": pdf_file is not None,
            "pdf_name": pdf_file.name if pdf_file else None,
            "audio_count": len(audio_files) if audio_files else 0,
            "note": "Scheduling now managed per class via ClassExamSchedule"
        }
        logger.info(f"[EXAM_SERVICE_CREATE] {json.dumps(console_log)}")
        print(f"[EXAM_SERVICE_CREATE] {json.dumps(console_log)}")
        
        # CRITICAL: Validate PDF file before creating exam - PDF IS REQUIRED
        ExamService.validate_pdf_file(pdf_file)  # This will raise ValidationException if pdf_file is None
        ExamService.log_pdf_save_attempt(None, pdf_file, "before_create")
        
        # Create the exam
        exam = Exam.objects.create(
            name=exam_data['name'],
            exam_type=exam_data.get('exam_type', 'REVIEW'),  # Add exam type with default
            time_period_month=exam_data.get('time_period_month'),  # Phase 2: Add month
            time_period_quarter=exam_data.get('time_period_quarter'),  # Phase 2: Add quarter
            academic_year=exam_data.get('academic_year'),  # Phase 2: Add academic year
            class_codes=exam_data.get('class_codes', []),  # Phase 3: Add class codes
            instructions=exam_data.get('instructions', ''),  # General instructions (kept at exam level)
            curriculum_level_id=exam_data.get('curriculum_level_id'),
            pdf_file=pdf_file,
            timer_minutes=exam_data.get('timer_minutes', 60),
            total_questions=exam_data['total_questions'],
            default_options_count=exam_data.get('default_options_count', DEFAULT_OPTIONS_COUNT),
            passing_score=exam_data.get('passing_score', 0),
            pdf_rotation=exam_data.get('pdf_rotation', 0),  # Add PDF rotation field
            created_by=exam_data.get('created_by'),
            is_active=exam_data.get('is_active', True)
        )
        
        # Log successful exam object creation with PDF validation
        if pdf_file:
            ExamService.log_pdf_save_attempt(exam, pdf_file, "after_save")
        
        console_log = {
            "service": "ExamService",
            "action": "exam_object_created",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "pdf_file_path": exam.pdf_file.name if exam.pdf_file else None,
            "pdf_rotation": exam.pdf_rotation,
            "pdf_validation_passed": bool(pdf_file)
        }
        logger.info(f"[EXAM_SERVICE_CREATED] {json.dumps(console_log)}")
        print(f"[EXAM_SERVICE_CREATED] {json.dumps(console_log)}")
        
        # Create placeholder questions
        ExamService.create_questions_for_exam(exam)
        
        # Handle audio files
        if audio_files:
            ExamService.attach_audio_files(exam, audio_files, audio_names or [])
        
        logger.info(
            f"Created exam {exam.id}: {exam.name}",
            extra={'exam_id': str(exam.id), 'total_questions': exam.total_questions}
        )
        
        # Final success log
        console_log = {
            "service": "ExamService",
            "action": "create_exam_complete",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "questions_created": exam.total_questions,
            "audio_files_attached": len(audio_files) if audio_files else 0
        }
        logger.info(f"[EXAM_SERVICE_COMPLETE] {json.dumps(console_log)}")
        print(f"[EXAM_SERVICE_COMPLETE] {json.dumps(console_log)}")
        
        return exam
    
    @staticmethod
    def create_questions_for_exam(exam: Exam) -> List[Question]:
        """
        Create placeholder questions for an exam.
        
        Args:
            exam: Exam instance
            
        Returns:
            List of created Question instances
        """
        from primepath_routinetest.models.exam_abstraction import ExamAbstraction
        questions = ExamAbstraction.get_questions(exam)
        existing_numbers = set(
            questions.values_list('question_number', flat=True) if questions else []
        )
        logger.debug(f"[EXAM_SERVICE] Creating questions for exam type: {type(exam).__name__}, existing: {len(existing_numbers)}")
        
        questions_to_create = []
        for num in range(1, exam.total_questions + 1):
            if num not in existing_numbers:
                questions_to_create.append(
                    Question(
                        exam=exam,
                        question_number=num,
                        question_type='MCQ',  # Default type
                        correct_answer='',
                        points=DEFAULT_QUESTION_POINTS,
                        options_count=exam.default_options_count
                    )
                )
        
        created_questions = Question.objects.bulk_create(questions_to_create)
        
        logger.info(
            f"Created {len(created_questions)} questions for exam {exam.id}"
        )
        
        return created_questions
    
    @staticmethod
    def attach_audio_files(
        exam: Exam,
        audio_files: List[UploadedFile],
        audio_names: List[str]
    ) -> List[AudioFile]:
        """
        Attach audio files to an exam.
        
        Args:
            exam: Exam instance
            audio_files: List of audio file uploads
            audio_names: List of display names
            
        Returns:
            List of created AudioFile instances
        """
        audio_objects = []
        
        for index, audio_file in enumerate(audio_files):
            name = (
                audio_names[index] 
                if index < len(audio_names) 
                else f"Audio {index + 1}"
            )
            
            audio_obj = AudioFile(
                exam=exam,
                audio_file=audio_file,
                name=name,
                order=index + 1,
                start_question=0,  # 0 indicates unassigned
                end_question=0     # 0 indicates unassigned
            )
            audio_objects.append(audio_obj)
        
        created_audio = AudioFile.objects.bulk_create(audio_objects)
        
        logger.info(
            f"Attached {len(created_audio)} audio files to exam {exam.id}"
        )
        
        return created_audio
    
    @staticmethod
    @transaction.atomic
    def update_exam_questions(
        exam: Exam,
        questions_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update questions for an exam with types and answers.
        
        Args:
            exam: Exam instance
            questions_data: List of question data dictionaries
            
        Returns:
            Summary of updates
        """
        updated_count = 0
        created_count = 0
        
        for q_data in questions_data:
            question_id = q_data.get('id')
            
            if question_id:
                # Update existing question
                try:
                    question = Question.objects.get(id=question_id, exam=exam)
                    question.question_type = q_data.get('question_type', 'MCQ')
                    question.correct_answer = q_data.get('correct_answer', '')
                    
                    # Calculate correct options_count based on answer data
                    if question.question_type in ['SHORT', 'LONG', 'MIXED']:
                        # For SHORT/LONG/MIXED, calculate from actual answer data
                        calculated_count = ExamService._calculate_options_count(
                            question.question_type, 
                            question.correct_answer
                        )
                        question.options_count = calculated_count
                    elif question.question_type in ['MCQ', 'CHECKBOX'] and 'options_count' in q_data:
                        # For MCQ/CHECKBOX, use provided value
                        question.options_count = q_data['options_count']
                    
                    question.save()
                    updated_count += 1
                    
                except Question.DoesNotExist:
                    logger.warning(
                        f"Question {question_id} not found for exam {exam.id}"
                    )
            else:
                # Create new question
                question_num = int(q_data.get('question_number'))
                question_type = q_data.get('question_type', 'MCQ')
                correct_answer = q_data.get('correct_answer', '')
                
                # Calculate options_count for SHORT/LONG/MIXED questions
                if question_type in ['SHORT', 'LONG', 'MIXED']:
                    options_count = ExamService._calculate_options_count(
                        question_type, 
                        correct_answer
                    )
                else:
                    options_count = q_data.get('options_count', DEFAULT_OPTIONS_COUNT)
                
                Question.objects.update_or_create(
                    exam=exam,
                    question_number=question_num,
                    defaults={
                        'question_type': question_type,
                        'correct_answer': correct_answer,
                        'points': q_data.get('points', DEFAULT_QUESTION_POINTS),
                        'options_count': options_count
                    }
                )
                created_count += 1
        
        logger.info(
            f"Updated exam {exam.id}: {updated_count} updated, {created_count} created"
        )
        
        return {
            'updated': updated_count,
            'created': created_count,
            'total': len(questions_data)
        }
    
    @staticmethod
    def get_next_version_number(curriculum_level_id: int, date_str: str = None) -> int:
        """
        Get the next available version number for a curriculum level on a specific date.
        Only returns version number if there are existing uploads for the same level on the same day.
        
        Args:
            curriculum_level_id: Curriculum level ID
            date_str: Date in YYMMDD format (if None, uses today)
            
        Returns:
            Next available version number (2, 3, etc.) or None if no version needed
        """
        from datetime import datetime
        
        # Get today's date in YYMMDD format if not provided
        if not date_str:
            date_str = datetime.now().strftime('%y%m%d')
        
        # Look for exams with the new naming pattern for this level and date
        existing_exams = Exam.objects.filter(
            curriculum_level_id=curriculum_level_id,
            name__contains=f'_{date_str}'  # Contains today's date
        ).values_list('name', flat=True)
        
        # Check if any exam exists for this level and date
        exams_today = []
        for exam_name in existing_exams:
            # Check if it matches our date pattern
            if f'_{date_str}' in exam_name:
                exams_today.append(exam_name)
        
        if not exams_today:
            # No exams for this level today, no version needed
            return None
        
        # Find the highest version number
        max_version = 1
        for exam_name in exams_today:
            # Check for version pattern _v2, _v3, etc.
            if f'_{date_str}_v' in exam_name:
                try:
                    version_part = exam_name.split(f'_{date_str}_v')[-1]
                    version_num = int(version_part.split('_')[0]) if '_' in version_part else int(version_part)
                    max_version = max(max_version, version_num)
                except (ValueError, IndexError):
                    continue
        
        # Return the next version number
        return max_version + 1
    
    @staticmethod
    def get_next_version_letter(curriculum_level_id: int) -> str:
        """
        DEPRECATED: Kept for backward compatibility.
        Get the next available version letter for a curriculum level.
        
        Args:
            curriculum_level_id: Curriculum level ID
            
        Returns:
            Next available version letter (a-z)
        """
        existing_exams = Exam.objects.filter(
            curriculum_level_id=curriculum_level_id,
            name__regex=r'^\[RoutineTest\].*_v_[a-z]$'
        ).values_list('name', flat=True)
        
        used_versions = set()
        for exam_name in existing_exams:
            if '_v_' in exam_name:
                version = exam_name.split('_v_')[-1]
                if len(version) == 1 and version.isalpha() and version.islower():
                    used_versions.add(version)
        
        # Find next available letter
        for i in range(26):  # a-z
            candidate = chr(ord('a') + i)
            if candidate not in used_versions:
                return candidate
        
        # If all letters used, raise exception
        raise ExamConfigurationException(
            "All version letters (a-z) have been used for this curriculum level"
        )
    
    @staticmethod
    @transaction.atomic
    def delete_exam(exam: Exam) -> None:
        """
        Delete an exam and all associated files.
        
        Args:
            exam: Exam instance to delete
        """
        exam_name = exam.name
        exam_id = exam.id
        
        # Delete associated files
        if exam.pdf_file:
            exam.pdf_file.delete()
        
        # Delete audio files
        for audio in exam.routine_audio_files.all():
            if audio.audio_file:
                try:
                    audio.audio_file.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete audio file: {e}")
        
        # Delete the exam (cascades to questions and audio records)
        exam.delete()
        
        logger.info(f"Deleted exam {exam_id}: {exam_name}")
    
    # ============== PERMISSION METHODS ==============
    
    # Program to class code mapping
    PROGRAM_CLASS_MAPPING = {
        'CORE': [
            'PRIMARY_1A', 'PRIMARY_1B', 'PRIMARY_1C', 'PRIMARY_1D',
            'PRIMARY_2A', 'PRIMARY_2B', 'PRIMARY_2C', 'PRIMARY_2D',
            'PRIMARY_3A', 'PRIMARY_3B', 'PRIMARY_3C', 'PRIMARY_3D',
        ],
        'ASCENT': [
            'PRIMARY_4A', 'PRIMARY_4B', 'PRIMARY_4C', 'PRIMARY_4D',
            'PRIMARY_5A', 'PRIMARY_5B', 'PRIMARY_5C', 'PRIMARY_5D',
            'PRIMARY_6A', 'PRIMARY_6B', 'PRIMARY_6C', 'PRIMARY_6D',
        ],
        'EDGE': [
            'MIDDLE_1A', 'MIDDLE_1B', 'MIDDLE_1C', 'MIDDLE_1D',
            'MIDDLE_2A', 'MIDDLE_2B', 'MIDDLE_2C', 'MIDDLE_2D',
            'MIDDLE_3A', 'MIDDLE_3B', 'MIDDLE_3C', 'MIDDLE_3D',
        ],
        'PINNACLE': [
            'HIGH_1A', 'HIGH_1B', 'HIGH_1C', 'HIGH_1D',
            'HIGH_2A', 'HIGH_2B', 'HIGH_2C', 'HIGH_2D',
            'HIGH_3A', 'HIGH_3B', 'HIGH_3C', 'HIGH_3D',
        ]
    }
    
    @classmethod
    def get_teacher_assignments(cls, user: User) -> Dict[str, str]:
        """Get all class assignments for a teacher"""
        if not user.is_authenticated:
            return {}
        
        # Admins have full access to everything
        if user.is_superuser or user.is_staff:
            all_classes = {}
            for program_classes in ExamService.PROGRAM_CLASS_MAPPING.values():
                for class_code in program_classes:
                    all_classes[class_code] = 'FULL'
            return all_classes
        
        # Get teacher assignments (excluding expired ones)
        if hasattr(user, 'teacher_profile'):
            from django.db.models import Q
            from django.utils import timezone
            
            assignments = TeacherClassAssignment.objects.filter(
                teacher=user.teacher_profile,
                is_active=True
            ).filter(
                Q(expires_on__isnull=True) | Q(expires_on__gt=timezone.now())
            ).values_list('class_code', 'access_level')
            return dict(assignments)
        
        return {}
    
    @classmethod
    def get_filtered_class_choices_for_teacher(cls, user: User, full_access_only: bool = True) -> list:
        """
        Get filtered class choices for a teacher based on their assignments.
        Returns list of tuples: [(class_code, display_name), ...]
        
        Args:
            user: The user to get classes for
            full_access_only: If True, only return classes where teacher has FULL access (for Upload/Create)
                            If False, return all assigned classes (for Copy destination)
        
        This is the CRITICAL method that ensures teachers only see appropriate classes
        when creating, editing, or copying exams.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Get all available class choices
        from ..models import Exam
        all_choices = Exam.get_class_code_choices()
        
        # For admins, return all choices
        if user.is_superuser or user.is_staff:
            logger.info(f"[CLASS_FILTER] Admin {user.username} gets ALL {len(all_choices)} classes")
            print(f"[CLASS_FILTER] Admin {user.username} can access ALL classes")
            return all_choices
        
        # For teachers, filter based on assignments
        teacher_assignments = ExamService.get_teacher_assignments(user)
        
        if not teacher_assignments:
            logger.warning(f"[CLASS_FILTER] User {user.username} has NO class assignments")
            print(f"[CLASS_FILTER] Teacher {user.username} has NO assigned classes")
            return []
        
        # Filter choices based on access level requirement
        filtered_choices = []
        for class_code, display_name in all_choices:
            if class_code in teacher_assignments:
                access_level = teacher_assignments[class_code]
                
                # CRITICAL: For Upload/Create, only show FULL access classes
                if full_access_only and access_level != 'FULL':
                    logger.debug(f"[CLASS_FILTER] Skipping {class_code} - has {access_level} access (need FULL)")
                    continue
                
                # Add access level to display name for clarity
                # Convert "FULL" to "FULL ACCESS" for better clarity
                display_access = "FULL ACCESS" if access_level == "FULL" else access_level
                enhanced_display = f"{display_name} ({display_access})"
                filtered_choices.append((class_code, enhanced_display))
                logger.debug(f"[CLASS_FILTER] Including class {class_code} with {access_level} access")
        
        filter_type = "FULL access only" if full_access_only else "all assigned"
        logger.info(f"[CLASS_FILTER] Teacher {user.username} gets {len(filtered_choices)}/{len(all_choices)} classes ({filter_type})")
        print(f"[CLASS_FILTER] Teacher {user.username} can access {len(filtered_choices)} classes ({filter_type}): {[c[0] for c in filtered_choices][:5]}...")
        
        return filtered_choices
    
    @classmethod
    def can_teacher_edit_exam(cls, user: User, exam: Exam) -> bool:
        """Check if teacher can edit a specific exam - ENHANCED VERSION WITH OWNERSHIP"""
        import logging
        logger = logging.getLogger(__name__)
        
        # CRITICAL: Check admin status FIRST
        if not user.is_authenticated:
            logger.debug(f"[PERMISSION_EDIT] User not authenticated")
            return False
        
        # Admins can edit everything
        if user.is_superuser or user.is_staff:
            logger.info(f"[PERMISSION_EDIT] User {user.username} is admin, granting edit permission")
            print(f"[PERMISSION_EDIT] Admin {user.username} has EDIT access to exam {exam.id}")
            return True
        
        # For non-admins, check teacher profile
        if not hasattr(user, 'teacher_profile'):
            logger.warning(f"[PERMISSION_EDIT] User {user.username} has no teacher_profile and is not admin")
            return False
        
        teacher = user.teacher_profile
        
        # CRITICAL FIX: Check if teacher is the creator/owner of the exam
        if exam.created_by and exam.created_by.id == teacher.id:
            logger.info(f"[PERMISSION_EDIT] Teacher {teacher.name} is the OWNER of exam {exam.name}, granting FULL edit permission")
            print(f"[PERMISSION_EDIT] Teacher {teacher.name} OWNS exam {exam.id} - FULL ACCESS")
            return True
        
        # Get teacher's assignments
        assignments = ExamService.get_teacher_assignments(user)
        
        # Log teacher's assignments for debugging
        logger.debug(f"[PERMISSION_EDIT] Teacher {teacher.name} has assignments: {list(assignments.keys())}")
        
        # Check if teacher has edit access to any of the exam's classes
        exam_classes = exam.class_codes if exam.class_codes else []
        
        # If exam has no specific class codes, check if teacher has any edit permissions
        # This allows teachers with edit permissions to manage program-level exams
        if not exam_classes:
            # Teacher can edit program-level exams if they have edit access to any class
            can_edit = any(access == 'FULL' for access in assignments.values())
            logger.debug(f"[PERMISSION_EDIT] Program-level exam, teacher {teacher.name} can_edit: {can_edit}")
            return can_edit
        
        # Check specific class codes
        for class_code in exam_classes:
            if class_code in assignments and assignments[class_code] == 'FULL':
                logger.info(f"[PERMISSION_EDIT] Teacher {teacher.name} has {assignments[class_code]} access to class {class_code}, granting edit permission")
                print(f"[PERMISSION_EDIT] Teacher {teacher.name} has EDIT access via class {class_code}")
                return True
        
        logger.debug(f"[PERMISSION_EDIT] Teacher {teacher.name} has NO edit access to exam {exam.name}")
        return False
    
    @classmethod
    def organize_exams_hierarchically(
        cls, 
        exams, 
        user: User,
        filter_assigned_only: bool = False,  # Backward compatibility
        ownership_filter: str = 'my'  # NEW: 'my' or 'others'
    ) -> Dict[str, Dict[str, List]]:
        """Organize exams hierarchically by program and class with access info - ENHANCED with ownership filtering"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Get teacher assignments
        assignments = ExamService.get_teacher_assignments(user)
        is_admin = user.is_superuser or user.is_staff
        
        # Initialize structure
        organized = {program: defaultdict(list) for program in ExamService.PROGRAM_CLASS_MAPPING.keys()}
        
        # Map class codes to programs
        class_to_program = {}
        for program, classes in ExamService.PROGRAM_CLASS_MAPPING.items():
            for class_code in classes:
                class_to_program[class_code] = program
        
        # ENHANCED: Log debugging info with new ownership system
        logger.info(f"[EXAM_HIERARCHY_ENHANCED] Processing {len(list(exams))} exams")
        logger.info(f"[EXAM_HIERARCHY_ENHANCED] User: {user}, is_admin: {is_admin}")
        logger.info(f"[EXAM_HIERARCHY_ENHANCED] Legacy filter_assigned_only: {filter_assigned_only}")
        logger.info(f"[EXAM_HIERARCHY_ENHANCED] NEW ownership_filter: {ownership_filter}")
        logger.info(f"[EXAM_HIERARCHY_ENHANCED] Teacher assignments: {assignments}")
        
        # CRITICAL FIX: Proper filtering for ownership-based system
        # ownership='my' → Show ONLY exams where user has FULL/OWNER access
        # ownership='others' → Show ONLY exams where user has VIEW ONLY access
        if ownership_filter == 'my':
            filter_mode = 'MY_EXAMS'  # Show only editable exams
            effective_filter_assigned = True  # Keep for backward compat
            filter_description = "My Test Files (FULL/OWNER access only)"
        elif ownership_filter == 'others':
            filter_mode = 'OTHERS_EXAMS'  # Show only VIEW ONLY exams
            effective_filter_assigned = True  # CHANGED: Must filter, not show all!
            filter_description = "Other Teachers' Test Files (VIEW ONLY access only)"
        else:
            filter_mode = 'LEGACY'
            effective_filter_assigned = filter_assigned_only  # Fallback to legacy
            filter_description = f"Legacy filtering (assigned_only={filter_assigned_only})"
            
        logger.info(f"[EXAM_HIERARCHY_FIX] Ownership filter: {ownership_filter}")
        logger.info(f"[EXAM_HIERARCHY_FIX] Filter mode: {filter_mode}")
        logger.info(f"[EXAM_HIERARCHY_FIX] Effective filtering: {filter_description}")
        logger.info(f"[EXAM_HIERARCHY_FIX] Will apply filtering: {effective_filter_assigned}")
        
        # Process each exam
        exam_count = 0
        for exam in exams:
            exam_classes = exam.class_codes if exam.class_codes else []
            
            # Log exam details
            if exam_count < 5:  # Log first 5 exams for debugging
                logger.info(f"[EXAM_HIERARCHY] Exam: {exam.name}, class_codes: {exam_classes}, has_curriculum: {hasattr(exam, 'curriculum_level') and exam.curriculum_level}")
            
            # If no class codes (empty list or None), try to infer from curriculum level
            if (not exam_classes or exam_classes == []) and hasattr(exam, 'curriculum_level') and exam.curriculum_level:
                # Infer class codes from curriculum level's program
                try:
                    program_name = exam.curriculum_level.subprogram.program.name  # CORE, ASCENT, EDGE, or PINNACLE
                    logger.info(f"[EXAM_HIERARCHY] Found program {program_name} for exam {exam.name}")
                    
                    # Use a special marker to indicate this is a program-level exam
                    exam_classes = [f"PROGRAM_{program_name}"]
                    logger.info(f"[EXAM_HIERARCHY] Exam {exam.name} marked as program-level for {program_name}")
                except Exception as e:
                    logger.warning(f"[EXAM_HIERARCHY] Could not infer program from curriculum_level: {e}")
                    exam_classes = ['GENERAL']
            
            # CRITICAL: Check ownership FIRST - owners have FULL access regardless
            is_owner = False
            if exam.created_by and hasattr(user, 'teacher_profile'):
                try:
                    is_owner = exam.created_by.id == user.teacher_profile.id
                    if is_owner:
                        logger.info(f"[EXAM_PERMISSION_OWNERSHIP] User {user.username} OWNS exam {exam.name} - FULL ACCESS")
                    else:
                        logger.debug(f"[EXAM_PERMISSION_OWNERSHIP] User {user.username} does not own exam {exam.name} (created_by={exam.created_by.id}, teacher={user.teacher_profile.id})")
                except Exception as e:
                    logger.warning(f"[EXAM_PERMISSION_OWNERSHIP] Error checking ownership for exam {exam.name}: {e}")
            else:
                if not exam.created_by:
                    logger.debug(f"[EXAM_PERMISSION_OWNERSHIP] Exam {exam.name} has no created_by field")
                if not hasattr(user, 'teacher_profile'):
                    logger.debug(f"[EXAM_PERMISSION_OWNERSHIP] User {user.username} has no teacher_profile")
            
            # CRITICAL FIX: Apply proper filtering based on ownership mode
            if effective_filter_assigned and not is_admin:
                should_include = False
                
                # ENHANCED DEBUG LOGGING
                logger.info(f"[FILTER_FIX] ====== FILTERING EXAM: {exam.name} ======")
                logger.info(f"[FILTER_FIX] Filter mode: {filter_mode}")
                logger.info(f"[FILTER_FIX] Exam ID: {exam.id}")
                logger.info(f"[FILTER_FIX] Exam classes: {exam_classes}")
                logger.info(f"[FILTER_FIX] Teacher assignments: {assignments}")
                logger.info(f"[FILTER_FIX] Is owner: {is_owner}")
                
                # Track why exam is included/excluded
                inclusion_reasons = []
                exclusion_reasons = []
                
                # Determine the user's access level for this exam
                user_access_level = None
                
                # Check ownership first
                if is_owner:
                    user_access_level = 'OWNER'
                    logger.info(f"[FILTER_FIX] User is OWNER of this exam")
                elif not exam_classes or exam_classes == []:
                    # No class codes - user has no access unless owner
                    user_access_level = 'NONE'
                    logger.info(f"[FILTER_FIX] Exam has no class codes, user has NO access")
                else:
                    # Check access level from class assignments
                    highest_access = 'NONE'
                    for cls in exam_classes:
                        if cls.startswith('PROGRAM_'):
                            continue  # Skip program-level markers
                        
                        if cls in assignments:
                            access = assignments[cls]
                            logger.info(f"[FILTER_FIX] Class {cls}: User has {access} access")
                            
                            # Determine highest access level
                            if access == 'FULL':
                                highest_access = 'FULL'
                                break  # FULL is highest, no need to check more
                            elif access == 'VIEW' and highest_access == 'NONE':
                                highest_access = 'VIEW'
                    
                    user_access_level = highest_access
                    logger.info(f"[FILTER_FIX] User's highest access level: {user_access_level}")
                
                # Apply filter based on mode
                if filter_mode == 'MY_EXAMS':
                    # Show ONLY exams where user has FULL/OWNER access
                    if user_access_level in ['OWNER', 'FULL']:
                        should_include = True
                        inclusion_reasons.append(f"User has {user_access_level} access (MY_EXAMS mode)")
                        logger.info(f"[FILTER_FIX] ✅ INCLUDING: User has editable access ({user_access_level})")
                    else:
                        exclusion_reasons.append(f"User has {user_access_level} access, need FULL/OWNER for MY_EXAMS")
                        logger.info(f"[FILTER_FIX] ❌ EXCLUDING: User only has {user_access_level} access")
                
                elif filter_mode == 'OTHERS_EXAMS':
                    # Show ONLY exams where user has VIEW ONLY access (not FULL/OWNER)
                    if user_access_level == 'VIEW':
                        should_include = True
                        inclusion_reasons.append(f"User has VIEW ONLY access (OTHERS_EXAMS mode)")
                        logger.info(f"[FILTER_FIX] ✅ INCLUDING: User has VIEW ONLY access")
                    else:
                        exclusion_reasons.append(f"User has {user_access_level} access, need VIEW ONLY for OTHERS_EXAMS")
                        logger.info(f"[FILTER_FIX] ❌ EXCLUDING: User has {user_access_level} access, not VIEW ONLY")
                
                else:  # LEGACY mode
                    # Original behavior: show exams from editable classes
                    if user_access_level in ['OWNER', 'FULL']:
                        should_include = True
                        inclusion_reasons.append(f"User has editable access (LEGACY mode)")
                    else:
                        exclusion_reasons.append(f"User has {user_access_level} access, not editable")
                
                # Final decision
                if not should_include:
                    logger.info(f"[FILTER_FIX] ❌❌❌ EXCLUDING EXAM: {exam.name}")
                    logger.info(f"[FILTER_FIX] Exclusion reasons: {exclusion_reasons}")
                    logger.info(f"[FILTER_FIX] ====== END FILTERING (EXCLUDED) ======")
                    continue  # Skip this exam
                else:
                    logger.info(f"[FILTER_FIX] ✅✅✅ INCLUDING EXAM: {exam.name}")
                    logger.info(f"[FILTER_FIX] Inclusion reasons: {inclusion_reasons}")
                    logger.info(f"[FILTER_FIX] ====== END FILTERING (INCLUDED) ======")
            
            # Add permissions to exam with ownership priority
            if is_admin:
                # ADMIN ALWAYS HAS FULL PERMISSIONS
                exam.can_edit = True
                exam.can_copy = True
                exam.can_delete = True
                exam.is_owner = False
                exam.access_badge = 'ADMIN'
            elif not effective_filter_assigned:
                # SHOWING ALL EXAMS (toggle = All Exams) - Set initial permissions
                logger.debug(f"[PERMISSION_DEBUG] Setting permissions for exam '{exam.name}' in 'Show All' mode")
                logger.debug(f"[PERMISSION_DEBUG] is_owner={is_owner}, user={user.username}")
                
                # Initialize with VIEW ONLY permissions
                exam.can_edit = False
                exam.can_copy = True  # Can copy to their classes
                exam.can_delete = False
                exam.is_owner = is_owner  # CRITICAL FIX: Preserve ownership status
                exam.access_badge = 'VIEW ONLY'
                
                # Check if this is actually an owned exam (ownership takes precedence)
                if is_owner:
                    # OWNER gets full permissions and proper badge
                    exam.can_edit = True
                    exam.can_delete = True
                    exam.access_badge = 'OWNER'
                    logger.info(f"[PERMISSION_DEBUG] ✅ Exam '{exam.name}' marked as OWNER for {user.username}")
                else:
                    # Check edit/delete permissions through class assignments
                    if ExamService.can_teacher_edit_exam(user, exam):
                        exam.can_edit = True
                        # Determine if FULL ACCESS or just EDIT
                        has_full_access = False
                        for cls in (exam.class_codes or []):
                            if cls in assignments and assignments[cls] == 'FULL':
                                has_full_access = True
                                break
                        exam.access_badge = 'FULL ACCESS' if has_full_access else 'EDIT'
                        logger.debug(f"[PERMISSION_DEBUG] Exam '{exam.name}' has edit access, badge: {exam.access_badge}")
                    
                    if ExamPermissionService.can_teacher_delete_exam(user, exam):
                        exam.can_delete = True
                        logger.debug(f"[PERMISSION_DEBUG] Exam '{exam.name}' has delete permission")
            else:
                # ASSIGNED ONLY MODE - Set permissions based on actual access level
                logger.debug(f"[PERMISSION_DEBUG] Setting permissions for exam '{exam.name}' in 'Assigned Only' mode")
                logger.debug(f"[PERMISSION_DEBUG] is_owner={is_owner}, user={user.username}")
                
                # For owned exams in assigned mode
                if is_owner:
                    # Owner gets full permissions on their own exams
                    exam.can_edit = True
                    exam.can_copy = True
                    exam.can_delete = True
                    exam.is_owner = True
                    exam.access_badge = 'OWNER'
                    logger.info(f"[PERMISSION_DEBUG] ✅ Exam '{exam.name}' marked as OWNER in assigned mode")
                else:
                    # Non-owner: set permissions based on actual access
                    exam.can_edit = ExamService.can_teacher_edit_exam(user, exam)
                    exam.can_copy = len(assignments) > 0
                    exam.can_delete = ExamPermissionService.can_teacher_delete_exam(user, exam)
                    exam.is_owner = False
                    
                    # Check the highest access level for this exam's classes
                    highest_access = 'VIEW'
                    for cls in (exam.class_codes or []):
                        if cls in assignments:
                            access = assignments[cls]
                            if access == 'FULL':
                                highest_access = 'FULL'
                                break
                    
                    # Set badge based on highest access level
                    if highest_access == 'FULL':
                        exam.access_badge = 'FULL ACCESS'
                    elif highest_access == 'CO_TEACHER':
                        exam.access_badge = 'EDIT'
                    else:
                        # This should NEVER happen in assigned mode - exam should have been filtered out
                        logger.error(f"[FILTER_BUG] ❌❌❌ CRITICAL BUG: Exam '{exam.name}' has VIEW ONLY access in ASSIGNED mode!")
                        logger.error(f"[FILTER_BUG] This exam should have been filtered out earlier!")
                        logger.error(f"[FILTER_BUG] SKIPPING THIS EXAM - not adding to results")
                        # CRITICAL FIX: Don't add VIEW ONLY exams in assigned mode
                        # Skip to next exam completely - don't add to organized dict
                        continue
                    
                    logger.debug(f"[PERMISSION_DEBUG] Exam '{exam.name}' access badge: {exam.access_badge} (highest: {highest_access})")
            
            # CRITICAL CHECK: If we're in filter mode and somehow got here with a VIEW ONLY exam, skip it
            if effective_filter_assigned and not is_admin and hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                logger.error(f"[FILTER_CRITICAL] ❌❌❌ CAUGHT VIEW ONLY exam '{exam.name}' about to be added - SKIPPING!")
                continue
            
            # Organize by class code
            if exam_classes:
                for class_code in exam_classes:
                    if class_code.startswith('PROGRAM_'):
                        # This is a program-level exam without specific class assignment
                        program = class_code.replace('PROGRAM_', '')
                        if program in ExamService.PROGRAM_CLASS_MAPPING:
                            exam.class_access_level = 'FULL' if is_admin else 'VIEW'
                            exam.is_accessible = is_admin
                            organized[program]['All Classes'].append(exam)
                            logger.info(f"[EXAM_HIERARCHY] Added exam to {program}/All Classes")
                        else:
                            logger.warning(f"[EXAM_HIERARCHY] Unknown program {program}")
                            organized['CORE']['GENERAL'].append(exam)
                    elif class_code == 'GENERAL':
                        # Fall back for exams without proper classification
                        exam.class_access_level = 'FULL' if is_admin else 'VIEW'
                        exam.is_accessible = is_admin
                        organized['CORE']['GENERAL'].append(exam)
                        logger.info(f"[EXAM_HIERARCHY] Added exam to CORE/GENERAL")
                    else:
                        # Normal class code processing
                        program = class_to_program.get(class_code)
                        if not program:
                            logger.warning(f"[EXAM_HIERARCHY] Unknown class_code: {class_code}, defaulting to CORE")
                            program = 'CORE'
                        
                        # Add access level info
                        exam.class_access_level = 'FULL' if is_admin else assignments.get(class_code, 'VIEW')
                        exam.is_accessible = class_code in assignments or is_admin
                        
                        organized[program][class_code].append(exam)
            else:
                # If no class codes at all, put in CORE with a generic class
                logger.warning(f"[EXAM_HIERARCHY] Exam {exam.name} has no class_codes, placing in CORE/UNASSIGNED")
                exam.class_access_level = 'FULL' if is_admin else 'VIEW'
                exam.is_accessible = is_admin
                organized['CORE']['UNASSIGNED'].append(exam)
            
            exam_count += 1
        
        # Log summary and clean up empty programs
        result = {}
        for program, classes in organized.items():
            # Convert defaultdict to regular dict
            class_dict = dict(classes)
            if class_dict:  # Only add program if it has classes with exams
                result[program] = class_dict
                logger.info(f"[EXAM_HIERARCHY] {program}: {len(class_dict)} classes, "
                          f"{sum(len(exams) for exams in class_dict.values())} exams")
        
        if not result:
            logger.warning(f"[EXAM_HIERARCHY] No exams were organized into any programs!")
        else:
            logger.info(f"[EXAM_HIERARCHY] Final result: {list(result.keys())} programs")
        
        # FINAL SAFETY CHECK: If filter is on, ensure NO VIEW ONLY exams in result
        if effective_filter_assigned and not is_admin:
            logger.info(f"[FILTER_FINAL_CHECK] Running final safety check for VIEW ONLY exams...")
            view_only_found = []
            cleaned_result = {}
            
            for program, classes in result.items():
                cleaned_classes = {}
                for class_code, exams in classes.items():
                    cleaned_exams = []
                    for exam in exams:
                        if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                            view_only_found.append(f"{exam.name} (ID: {exam.id})")
                            logger.error(f"[FILTER_FINAL_CHECK] ❌❌❌ FOUND VIEW ONLY exam that should be filtered: {exam.name}")
                        else:
                            cleaned_exams.append(exam)
                    
                    if cleaned_exams:  # Only add class if it has exams after cleaning
                        cleaned_classes[class_code] = cleaned_exams
                
                if cleaned_classes:  # Only add program if it has classes with exams
                    cleaned_result[program] = cleaned_classes
            
            if view_only_found:
                logger.error(f"[FILTER_FINAL_CHECK] ❌ CRITICAL: Found and removed {len(view_only_found)} VIEW ONLY exams!")
                logger.error(f"[FILTER_FINAL_CHECK] Removed exams: {', '.join(view_only_found)}")
                result = cleaned_result
            else:
                logger.info(f"[FILTER_FINAL_CHECK] ✅ PASSED: No VIEW ONLY exams found in final result")
        
        return result
    
    @classmethod
    def get_class_display_name(cls, class_code: str) -> str:
        """Get human-readable display name for a class code"""
        display_names = {
            # Special categories
            'All Classes': 'All Classes',
            'GENERAL': 'General',
            'UNASSIGNED': 'Unassigned',
            # Primary School
            'PRIMARY_1A': 'Grade 1A', 'PRIMARY_1B': 'Grade 1B', 
            'PRIMARY_1C': 'Grade 1C', 'PRIMARY_1D': 'Grade 1D',
            'PRIMARY_2A': 'Grade 2A', 'PRIMARY_2B': 'Grade 2B',
            'PRIMARY_2C': 'Grade 2C', 'PRIMARY_2D': 'Grade 2D',
            'PRIMARY_3A': 'Grade 3A', 'PRIMARY_3B': 'Grade 3B',
            'PRIMARY_3C': 'Grade 3C', 'PRIMARY_3D': 'Grade 3D',
            'PRIMARY_4A': 'Grade 4A', 'PRIMARY_4B': 'Grade 4B',
            'PRIMARY_4C': 'Grade 4C', 'PRIMARY_4D': 'Grade 4D',
            'PRIMARY_5A': 'Grade 5A', 'PRIMARY_5B': 'Grade 5B',
            'PRIMARY_5C': 'Grade 5C', 'PRIMARY_5D': 'Grade 5D',
            'PRIMARY_6A': 'Grade 6A', 'PRIMARY_6B': 'Grade 6B',
            'PRIMARY_6C': 'Grade 6C', 'PRIMARY_6D': 'Grade 6D',
            # Middle School
            'MIDDLE_1A': 'Middle 1A', 'MIDDLE_1B': 'Middle 1B',
            'MIDDLE_1C': 'Middle 1C', 'MIDDLE_1D': 'Middle 1D',
            'MIDDLE_2A': 'Middle 2A', 'MIDDLE_2B': 'Middle 2B',
            'MIDDLE_2C': 'Middle 2C', 'MIDDLE_2D': 'Middle 2D',
            'MIDDLE_3A': 'Middle 3A', 'MIDDLE_3B': 'Middle 3B',
            'MIDDLE_3C': 'Middle 3C', 'MIDDLE_3D': 'Middle 3D',
            # High School
            'HIGH_1A': 'High 1A', 'HIGH_1B': 'High 1B',
            'HIGH_1C': 'High 1C', 'HIGH_1D': 'High 1D',
            'HIGH_2A': 'High 2A', 'HIGH_2B': 'High 2B',
            'HIGH_2C': 'High 2C', 'HIGH_2D': 'High 2D',
            'HIGH_3A': 'High 3A', 'HIGH_3B': 'High 3B',
            'HIGH_3C': 'High 3C', 'HIGH_3D': 'High 3D',
        }
        return display_names.get(class_code, class_code)
    
    @staticmethod
    @transaction.atomic
    def update_audio_assignments(
        exam: Exam,
        audio_assignments: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Update audio-to-question assignments for an exam using new Question.audio_file relationship.
        
        Args:
            exam: Exam instance
            audio_assignments: Dict mapping question_number -> audio_id
            
        Returns:
            Dictionary with assignment results
        """
        updated_count = 0
        errors = []
        
        # Handle None or empty audio_assignments
        if not audio_assignments:
            audio_assignments = {}
        
        # Convert audio_assignments keys to integers and validate
        validated_assignments = {}
        for question_num_str, audio_id in audio_assignments.items():
            try:
                question_num = int(question_num_str)
                validated_assignments[question_num] = audio_id
            except (ValueError, TypeError):
                errors.append(f"Invalid question number: {question_num_str}")
                continue
        
        # First, clear all existing assignments for this exam
        from ..models import Question
        Question.objects.filter(exam=exam).update(audio_file=None)
        
        # Update questions with new audio assignments
        for question_num, audio_id in validated_assignments.items():
            try:
                # Get the question
                question = Question.objects.get(exam=exam, question_number=question_num)
                
                # Get the audio file for this exam
                audio_file = AudioFile.objects.get(id=audio_id, exam=exam)
                
                # Assign audio to question
                question.audio_file = audio_file
                question.save()
                
                updated_count += 1
                
            except Question.DoesNotExist:
                errors.append(f"Question {question_num} not found for exam {exam.id}")
            except AudioFile.DoesNotExist:
                errors.append(f"Audio file {audio_id} not found for exam {exam.id}")
            except Exception as e:
                errors.append(f"Error updating audio {audio_id} to question {question_num}: {str(e)}")
        
        logger.info(
            f"Updated audio assignments for exam {exam.id}: {updated_count} assignments updated"
        )
        
        return {
            'updated': updated_count,
            'errors': errors,
            'total_assignments': len(validated_assignments)
        }
    
    @staticmethod
    def _calculate_options_count(question_type: str, correct_answer: str) -> int:
        """
        Calculate the correct options_count based on the answer data.
        
        Args:
            question_type: Type of question (SHORT, LONG, MIXED, etc.)
            correct_answer: The answer data string
            
        Returns:
            Calculated number of options/answers
        """
        if not correct_answer:
            return 1
        
        answer = str(correct_answer).strip()
        
        # For MIXED questions with JSON structure
        if question_type == 'MIXED':
            try:
                import json
                parsed = json.loads(answer)
                if isinstance(parsed, list):
                    return max(len(parsed), 1)
            except:
                pass
        
        # For LONG questions
        if question_type == 'LONG':
            # Check for multiple parts separated by triple pipe
            if '|||' in answer:
                parts = [p.strip() for p in answer.split('|||') if p.strip()]
                return max(len(parts), 1)
        
        # For SHORT questions
        if question_type == 'SHORT':
            # Check for multiple parts separated by pipe
            if '|' in answer:
                parts = [p.strip() for p in answer.split('|') if p.strip()]
                return max(len(parts), 1)
            elif ',' in answer:
                # Check if it's letter format or actual answers
                parts = [p.strip() for p in answer.split(',') if p.strip()]
                # If all parts are single letters, it's MCQ format
                if all(len(p) == 1 and p.isalpha() for p in parts):
                    return len(parts)
                return max(len(parts), 1)
        
        # Default to 1
        return 1
    
    @staticmethod
    @transaction.atomic
    def manage_student_roster(
        exam: Exam,
        roster_data: List[Dict[str, Any]],
        teacher = None
    ) -> Dict[str, Any]:
        """
        REMOVED: Roster functionality has been completely removed.
        This method is kept for backward compatibility but returns empty results.
        The prime goal in Answer Keys section is to assign answers, not manage rosters.
        
        Args:
            exam: Exam instance (ignored)
            roster_data: List of student data dictionaries (ignored)
            teacher: Teacher instance (ignored)
            
        Returns:
            Empty summary indicating roster functionality is removed
        """
        # Roster functionality completely removed - not needed for Answer Keys
        logger.warning("[ROSTER_REMOVED] manage_student_roster called but roster functionality has been removed")
        
        return {
            'created': 0,
            'updated': 0,
            'errors': ['Roster functionality has been removed. The prime goal in Answer Keys section is to assign answers.'],
            'total': 0,
            'message': 'ROSTER FUNCTIONALITY REMOVED - Not needed for Answer Keys'
        }
    
    @staticmethod
    def bulk_import_roster(
        exam: Exam,
        csv_content: str,
        teacher = None
    ) -> Dict[str, Any]:
        """
        REMOVED: Roster functionality has been completely removed.
        
        Args:
            exam: Exam instance (ignored)
            csv_content: CSV content as string (ignored)
            teacher: Teacher instance (ignored)
            
        Returns:
            Empty result indicating roster functionality is removed
        """
        # Roster functionality completely removed - not needed for Answer Keys
        logger.warning("[ROSTER_REMOVED] bulk_import_roster called but roster functionality has been removed")
        
        return {
            'created': 0,
            'updated': 0,
            'errors': ['Roster functionality has been removed. The prime goal in Answer Keys section is to assign answers.'],
            'total': 0,
            'message': 'ROSTER FUNCTIONALITY REMOVED'
        }
    
    @staticmethod
    def update_roster_completion(
        roster_entry_id: str,
        session = None
    ) -> bool:
        """
        REMOVED: Roster functionality has been completely removed.
        
        Args:
            roster_entry_id: StudentRoster entry ID (ignored)
            session: StudentSession instance (ignored)
            
        Returns:
            False - roster functionality removed
        """
        # Roster functionality completely removed - not needed for Answer Keys
        logger.warning("[ROSTER_REMOVED] update_roster_completion called but roster functionality has been removed")
        return False  # Always return False as roster functionality is removed
    
    @staticmethod
    def get_roster_report(exam: Exam) -> Dict[str, Any]:
        """
        REMOVED: Roster functionality has been completely removed.
        
        Args:
            exam: Exam instance (ignored)
            
        Returns:
            Empty report indicating roster functionality is removed
        """
        # Roster functionality completely removed - not needed for Answer Keys
        logger.warning("[ROSTER_REMOVED] get_roster_report called but roster functionality has been removed")
        
        return {
            'exam_id': str(exam.id) if exam else 'N/A',
            'exam_name': exam.name if exam else 'N/A',
            'total_assigned': 0,
            'by_status': {},
            'by_class': {},
            'completion_rate': 0,
            'students': [],
            'message': 'ROSTER FUNCTIONALITY REMOVED - The prime goal in Answer Keys section is to assign answers, not manage rosters'
        }
    
    @staticmethod
    def get_all_exams_with_stats() -> List[Dict[str, Any]]:
        """
        Get all exams with statistics.
        
        Returns:
            List of dictionaries containing exam information and statistics
        """
        from django.db.models import Count, Q
        
        try:
            exams = Exam.objects.select_related(
                'curriculum_level',
                'curriculum_level__subprogram',
                'curriculum_level__subprogram__program'
            ).annotate(
                total_sessions=Count('sessions', distinct=True),
                completed_sessions=Count(
                    'sessions',
                    filter=Q(sessions__completed_at__isnull=False),
                    distinct=True
                ),
                total_questions_count=Count('questions', distinct=True),
                audio_files_count=Count('audio_files', distinct=True)
            ).filter(is_active=True).order_by('-created_at')
            
            exam_stats = []
            for exam in exams:
                stats = {
                    'id': str(exam.id),
                    'name': exam.name,
                    'curriculum_level': exam.curriculum_level.full_name if exam.curriculum_level else 'None',
                    'timer_minutes': exam.timer_minutes,
                    'total_questions': exam.total_questions,
                    'total_sessions': exam.total_sessions,
                    'completed_sessions': exam.completed_sessions,
                    'completion_rate': (
                        exam.completed_sessions / exam.total_sessions * 100
                        if exam.total_sessions > 0 else 0
                    ),
                    'has_pdf': bool(exam.pdf_file),
                    'audio_files_count': exam.audio_files_count,
                    'created_at': exam.created_at.isoformat() if exam.created_at else None,
                    'is_active': exam.is_active
                }
                exam_stats.append(stats)
            
            logger.info(f"Retrieved stats for {len(exam_stats)} exams")
            return exam_stats
            
        except Exception as e:
            logger.error(f"Error getting exam stats: {e}")
            return []
    
    # ==================== CLASS-SPECIFIC SCHEDULING METHODS ====================
    
    @staticmethod
    @transaction.atomic
    def create_class_schedule(
        exam: Exam,
        class_code: str,
        schedule_data: Dict[str, Any],
        teacher = None
    ) -> 'ClassExamSchedule':
        """
        Create or update a class-specific schedule for an exam.
        
        Args:
            exam: Exam instance
            class_code: Class code (e.g., 'CLASS_7A')
            schedule_data: Dictionary containing schedule information
            teacher: Teacher creating the schedule
            
        Returns:
            Created or updated ClassExamSchedule instance
        """
        from ..models import ClassExamSchedule
        import json
        
        # Log schedule creation attempt
        console_log = {
            "service": "ExamService",
            "action": "create_class_schedule_start",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "class_code": class_code,
            "scheduled_date": str(schedule_data.get('scheduled_date')) if schedule_data.get('scheduled_date') else None,
            "scheduled_start_time": str(schedule_data.get('scheduled_start_time')) if schedule_data.get('scheduled_start_time') else None,
            "scheduled_end_time": str(schedule_data.get('scheduled_end_time')) if schedule_data.get('scheduled_end_time') else None,
            "location": schedule_data.get('location'),
            "allow_late_submission": schedule_data.get('allow_late_submission', False)
        }
        logger.info(f"[CLASS_SCHEDULE_CREATE] {json.dumps(console_log)}")
        print(f"[CLASS_SCHEDULE_CREATE] {json.dumps(console_log)}")
        
        # Create or update the class schedule
        schedule, created = ClassExamSchedule.objects.update_or_create(
            exam=exam,
            class_code=class_code,
            defaults={
                'scheduled_date': schedule_data.get('scheduled_date'),
                'scheduled_start_time': schedule_data.get('scheduled_start_time'),
                'scheduled_end_time': schedule_data.get('scheduled_end_time'),
                'location': schedule_data.get('location', ''),
                'additional_instructions': schedule_data.get('additional_instructions', ''),
                'allow_late_submission': schedule_data.get('allow_late_submission', False),
                'late_submission_penalty': schedule_data.get('late_submission_penalty', 0),
                'created_by': teacher,
                'is_active': True
            }
        )
        
        action_type = "created" if created else "updated"
        console_log = {
            "service": "ExamService",
            "action": f"class_schedule_{action_type}",
            "schedule_id": str(schedule.id),
            "exam_id": str(exam.id),
            "class_code": class_code,
            "is_scheduled": schedule.is_scheduled()
        }
        logger.info(f"[CLASS_SCHEDULE_{action_type.upper()}] {json.dumps(console_log)}")
        print(f"[CLASS_SCHEDULE_{action_type.upper()}] {json.dumps(console_log)}")
        
        return schedule
    
    @staticmethod
    def bulk_create_class_schedules(
        exam: Exam,
        schedules_data: List[Dict[str, Any]],
        teacher = None
    ) -> Dict[str, Any]:
        """
        Create multiple class schedules for an exam at once.
        
        Args:
            exam: Exam instance
            schedules_data: List of schedule dictionaries
            teacher: Teacher creating the schedules
            
        Returns:
            Summary of created/updated schedules
        """
        created_count = 0
        updated_count = 0
        errors = []
        
        for schedule_data in schedules_data:
            try:
                class_code = schedule_data.get('class_code')
                if not class_code:
                    errors.append("Missing class_code in schedule data")
                    continue
                
                schedule = ExamService.create_class_schedule(
                    exam=exam,
                    class_code=class_code,
                    schedule_data=schedule_data,
                    teacher=teacher
                )
                
                if schedule._state.adding:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                error_msg = f"Error creating schedule for {class_code}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[CLASS_SCHEDULE_ERROR] {error_msg}")
        
        return {
            'created': created_count,
            'updated': updated_count,
            'errors': errors,
            'total': len(schedules_data)
        }
    
    @staticmethod
    def get_class_schedules_for_exam(exam: Exam) -> List[Dict[str, Any]]:
        """
        Get all class schedules for an exam.
        
        Args:
            exam: Exam instance
            
        Returns:
            List of schedule dictionaries
        """
        from ..models import ClassExamSchedule
        
        schedules = ClassExamSchedule.objects.filter(
            exam=exam,
            is_active=True
        ).order_by('scheduled_date', 'scheduled_start_time', 'class_code')
        
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                'id': str(schedule.id),
                'class_code': schedule.class_code,
                'class_display': schedule.get_class_display(),
                'scheduled_date': schedule.scheduled_date.isoformat() if schedule.scheduled_date else None,
                'scheduled_start_time': schedule.scheduled_start_time.strftime('%H:%M') if schedule.scheduled_start_time else None,
                'scheduled_end_time': schedule.scheduled_end_time.strftime('%H:%M') if schedule.scheduled_end_time else None,
                'location': schedule.location,
                'additional_instructions': schedule.additional_instructions,
                'allow_late_submission': schedule.allow_late_submission,
                'late_submission_penalty': schedule.late_submission_penalty,
                'schedule_display': schedule.get_schedule_display(),
                'is_scheduled': schedule.is_scheduled()
            })
        
        return schedule_list
    
    @staticmethod
    def delete_class_schedule(schedule_id: str) -> bool:
        """
        Delete a class schedule.
        
        Args:
            schedule_id: ClassExamSchedule ID
            
        Returns:
            Success status
        """
        from ..models import ClassExamSchedule
        import json
        
        try:
            schedule = ClassExamSchedule.objects.get(id=schedule_id)
            
            console_log = {
                "service": "ExamService",
                "action": "delete_class_schedule",
                "schedule_id": str(schedule_id),
                "exam_id": str(schedule.exam_id),
                "class_code": schedule.class_code
            }
            logger.info(f"[CLASS_SCHEDULE_DELETE] {json.dumps(console_log)}")
            print(f"[CLASS_SCHEDULE_DELETE] {json.dumps(console_log)}")
            
            schedule.delete()
            return True
            
        except ClassExamSchedule.DoesNotExist:
            logger.error(f"[CLASS_SCHEDULE_ERROR] Schedule {schedule_id} not found")
            return False
    
    @staticmethod
    def check_class_access(exam: Exam, class_code: str, current_time=None) -> Dict[str, Any]:
        """
        Check if a class can access an exam based on its schedule.
        
        Args:
            exam: Exam instance
            class_code: Class code to check
            current_time: Optional datetime to check against
            
        Returns:
            Dictionary with access status and message
        """
        from ..models import ClassExamSchedule
        
        try:
            schedule = ClassExamSchedule.objects.get(
                exam=exam,
                class_code=class_code,
                is_active=True
            )
            
            can_access, message = schedule.can_student_access(current_time)
            
            return {
                'can_access': can_access,
                'message': message,
                'schedule': schedule.get_schedule_display() if schedule.is_scheduled() else None,
                'late_policy': schedule.get_late_policy_display()
            }
            
        except ClassExamSchedule.DoesNotExist:
            # No schedule for this class means they can access anytime
            return {
                'can_access': True,
                'message': 'Exam available',
                'schedule': None,
                'late_policy': 'No schedule set'
            }
    
    # ==================== ROUTINETEST [RT]/[QTR] NAMING METHODS ====================
    
    @staticmethod
    def get_routinetest_curriculum_levels():
        """
        Get curriculum levels available for RoutineTest with [RT]/[QTR] naming.
        Filters curriculum levels based on RoutineTest whitelist.
        
        Returns:
            List of dictionaries with curriculum level data and display names
        """
        from ..constants import ROUTINETEST_CURRICULUM_WHITELIST
        from core.models import CurriculumLevel
        import json
        
        logger.info("[ROUTINETEST_CURRICULUM] Getting curriculum levels for RoutineTest")
        print("[ROUTINETEST_CURRICULUM] Getting curriculum levels for RoutineTest")
        
        curriculum_levels = []
        
        # Loop through whitelist and find matching curriculum levels
        for program_name, subprogram_name, level_number in ROUTINETEST_CURRICULUM_WHITELIST:
            try:
                # Find the curriculum level in database
                curriculum_level = CurriculumLevel.objects.select_related(
                    'subprogram__program'
                ).get(
                    subprogram__program__name=program_name,
                    subprogram__name__icontains=subprogram_name,  # Use icontains for flexible matching
                    level_number=level_number
                )
                
                # Get existing exam count for this level
                existing_count = Exam.objects.filter(
                    curriculum_level=curriculum_level,
                    is_active=True
                ).count()
                
                # Generate display data
                level_data = {
                    'id': curriculum_level.id,
                    'program_name': program_name,
                    'subprogram_name': subprogram_name,
                    'level_number': level_number,
                    'full_name': curriculum_level.full_name,
                    'existing_count': existing_count,
                    # Format for RoutineTest dropdown
                    'routinetest_display_preview': f"[RT/QTR] - [Time Period] - {program_name} {subprogram_name} Level {level_number}",
                    'curriculum_level': curriculum_level
                }
                
                curriculum_levels.append(level_data)
                
            except CurriculumLevel.DoesNotExist:
                # Log missing curriculum level
                console_log = {
                    "service": "ExamService", 
                    "action": "curriculum_level_not_found",
                    "program": program_name,
                    "subprogram": subprogram_name,
                    "level": level_number
                }
                logger.warning(f"[ROUTINETEST_CURRICULUM_MISSING] {json.dumps(console_log)}")
                print(f"[ROUTINETEST_CURRICULUM_MISSING] {json.dumps(console_log)}")
                continue
        
        # Log results
        console_log = {
            "service": "ExamService",
            "action": "get_routinetest_curriculum_levels",
            "total_whitelist": len(ROUTINETEST_CURRICULUM_WHITELIST),
            "found_levels": len(curriculum_levels),
            "missing_levels": len(ROUTINETEST_CURRICULUM_WHITELIST) - len(curriculum_levels)
        }
        logger.info(f"[ROUTINETEST_CURRICULUM_RESULT] {json.dumps(console_log)}")
        print(f"[ROUTINETEST_CURRICULUM_RESULT] {json.dumps(console_log)}")
        
        return curriculum_levels
    
    @staticmethod
    def get_routinetest_curriculum_hierarchy():
        """
        Get curriculum hierarchy specifically structured for copy modal JavaScript.
        Returns a hierarchical dictionary optimized for frontend dropdown population.
        
        Returns:
            Dict: Hierarchical curriculum structure {Program: {subprograms: {SubProgram: {levels: [...]}}}}
        """
        from ..constants import ROUTINETEST_CURRICULUM_WHITELIST
        from core.models import CurriculumLevel
        import json
        
        logger.info("[ROUTINETEST_CURRICULUM_HIERARCHY] Building hierarchy for copy modal")
        print("[ROUTINETEST_CURRICULUM_HIERARCHY] Building hierarchy for copy modal")
        
        curriculum_hierarchy = {}
        levels_processed = 0
        
        # Loop through whitelist and build hierarchy
        for program_name, subprogram_name, level_number in ROUTINETEST_CURRICULUM_WHITELIST:
            try:
                # Find the curriculum level in database
                curriculum_level = CurriculumLevel.objects.select_related(
                    'subprogram__program'
                ).get(
                    subprogram__program__name=program_name,
                    subprogram__name__icontains=subprogram_name,
                    level_number=level_number
                )
                
                # Initialize program if not exists
                if program_name not in curriculum_hierarchy:
                    curriculum_hierarchy[program_name] = {'subprograms': {}}
                
                # Initialize subprogram if not exists
                if subprogram_name not in curriculum_hierarchy[program_name]['subprograms']:
                    curriculum_hierarchy[program_name]['subprograms'][subprogram_name] = {'levels': []}
                
                # Add level data
                level_data = {
                    'id': curriculum_level.id,
                    'number': level_number
                }
                
                curriculum_hierarchy[program_name]['subprograms'][subprogram_name]['levels'].append(level_data)
                levels_processed += 1
                
            except CurriculumLevel.DoesNotExist:
                console_log = {
                    "service": "ExamService", 
                    "action": "hierarchy_level_not_found",
                    "program": program_name,
                    "subprogram": subprogram_name,
                    "level": level_number
                }
                logger.warning(f"[ROUTINETEST_CURRICULUM_HIERARCHY_MISSING] {json.dumps(console_log)}")
                print(f"[ROUTINETEST_CURRICULUM_HIERARCHY_MISSING] {json.dumps(console_log)}")
                continue
        
        # Sort levels within each subprogram by level number
        for program_name, program_data in curriculum_hierarchy.items():
            for subprogram_name, subprogram_data in program_data['subprograms'].items():
                subprogram_data['levels'].sort(key=lambda x: x['number'])
        
        # Log results
        console_log = {
            "service": "ExamService",
            "action": "get_routinetest_curriculum_hierarchy",
            "total_programs": len(curriculum_hierarchy),
            "total_levels": levels_processed,
            "program_names": list(curriculum_hierarchy.keys())
        }
        logger.info(f"[ROUTINETEST_CURRICULUM_HIERARCHY_RESULT] {json.dumps(console_log)}")
        print(f"[ROUTINETEST_CURRICULUM_HIERARCHY_RESULT] {json.dumps(console_log)}")
        
        return curriculum_hierarchy
    
    @staticmethod
    def get_routinetest_curriculum_hierarchy_for_frontend():
        """
        COMPREHENSIVE FIX: Enhanced curriculum hierarchy method specifically optimized 
        for frontend Copy Exam modal integration with robust error handling and validation.
        
        Returns:
            Dict: Enhanced curriculum structure with frontend-specific optimizations
        """
        import json
        import traceback
        from django.utils import timezone
        from ..constants import ROUTINETEST_CURRICULUM_WHITELIST
        from core.models import CurriculumLevel
        
        logger.info("[COPY_MODAL_FIX] Building enhanced curriculum hierarchy for frontend")
        print("[COPY_MODAL_FIX] Building enhanced curriculum hierarchy for frontend")
        
        try:
            # Start with the existing hierarchy method
            base_hierarchy = ExamService.get_routinetest_curriculum_hierarchy()
            
            # Enhance with frontend-specific features
            enhanced_hierarchy = {}
            total_levels_processed = 0
            
            for program, program_data in base_hierarchy.items():
                enhanced_hierarchy[program] = {
                    'subprograms': {},
                    'meta': {
                        'total_subprograms': len(program_data.get('subprograms', {})),
                        'total_levels': 0
                    }
                }
                
                for subprogram, subprogram_data in program_data.get('subprograms', {}).items():
                    levels = subprogram_data.get('levels', [])
                    
                    # Sort levels by number for consistent frontend display
                    sorted_levels = sorted(levels, key=lambda x: x.get('number', 0))
                    
                    enhanced_hierarchy[program]['subprograms'][subprogram] = {
                        'levels': sorted_levels,
                        'meta': {
                            'level_count': len(sorted_levels),
                            'level_range': f"{min(l['number'] for l in sorted_levels)}-{max(l['number'] for l in sorted_levels)}" if sorted_levels else "0"
                        }
                    }
                    
                    enhanced_hierarchy[program]['meta']['total_levels'] += len(sorted_levels)
                    total_levels_processed += len(sorted_levels)
            
            # Add comprehensive validation and metadata
            validation_result = {
                'is_valid': True,
                'validation_errors': [],
                'programs_count': len(enhanced_hierarchy),
                'total_levels': total_levels_processed,
                'expected_programs': ['CORE', 'ASCENT', 'EDGE', 'PINNACLE'],
                'structure_check': {}
            }
            
            # Validate expected programs
            expected_programs = validation_result['expected_programs']
            for program in expected_programs:
                if program not in enhanced_hierarchy:
                    validation_result['validation_errors'].append(f"Missing expected program: {program}")
                    validation_result['is_valid'] = False
                else:
                    subprogram_count = len(enhanced_hierarchy[program]['subprograms'])
                    validation_result['structure_check'][program] = {
                        'present': True,
                        'subprograms_count': subprogram_count,
                        'levels_count': enhanced_hierarchy[program]['meta']['total_levels']
                    }
            
            # Create final response with comprehensive debugging
            final_response = {
                'curriculum_data': enhanced_hierarchy,
                'metadata': {
                    'generated_at': timezone.now().isoformat(),
                    'method': 'get_routinetest_curriculum_hierarchy_for_frontend',
                    'version': '2.0_comprehensive_fix',
                    'frontend_optimized': True
                },
                'validation': validation_result,
                'debug_info': {
                    'whitelist_count': len(ROUTINETEST_CURRICULUM_WHITELIST),
                    'database_levels_found': total_levels_processed,
                    'json_serializable': True,
                    'structure_valid': validation_result['is_valid']
                }
            }
            
            # Test JSON serialization
            try:
                json.dumps(final_response)
                final_response['debug_info']['json_serializable'] = True
            except (TypeError, ValueError) as e:
                final_response['debug_info']['json_serializable'] = False
                final_response['debug_info']['json_error'] = str(e)
                logger.error(f"[COPY_MODAL_FIX] JSON serialization failed: {e}")
            
            logger.info(f"[COPY_MODAL_FIX] Enhanced hierarchy built successfully")
            logger.info(f"[COPY_MODAL_FIX] Programs: {list(enhanced_hierarchy.keys())}")
            logger.info(f"[COPY_MODAL_FIX] Total levels: {total_levels_processed}")
            logger.info(f"[COPY_MODAL_FIX] Validation: {'✅ PASSED' if validation_result['is_valid'] else '❌ FAILED'}")
            
            print(f"[COPY_MODAL_FIX] ✅ Enhanced hierarchy completed: {len(enhanced_hierarchy)} programs, {total_levels_processed} levels")
            
            return final_response
            
        except Exception as e:
            logger.error(f"[COPY_MODAL_FIX] Critical error building enhanced hierarchy: {e}")
            logger.error(f"[COPY_MODAL_FIX] Stack trace: {traceback.format_exc()}")
            
            # Return fallback structure
            fallback_response = {
                'curriculum_data': {
                    'CORE': {'subprograms': {'Phonics': {'levels': [{'id': 1, 'number': 1}]}}},
                    'ASCENT': {'subprograms': {'Nova': {'levels': [{'id': 2, 'number': 1}]}}},
                    'EDGE': {'subprograms': {'Spark': {'levels': [{'id': 3, 'number': 1}]}}},
                    'PINNACLE': {'subprograms': {'Vision': {'levels': [{'id': 4, 'number': 1}]}}}
                },
                'metadata': {
                    'generated_at': timezone.now().isoformat(),
                    'method': 'get_routinetest_curriculum_hierarchy_for_frontend',
                    'version': '2.0_fallback',
                    'is_fallback': True,
                    'error': str(e)
                },
                'validation': {
                    'is_valid': False,
                    'validation_errors': [f"Failed to generate hierarchy: {e}"],
                    'is_fallback': True
                }
            }
            
            return fallback_response

    @staticmethod
    def generate_routinetest_exam_name(
        exam_type: str,
        time_period_month: str = None,
        time_period_quarter: str = None,
        academic_year: str = None,
        curriculum_level_id: int = None,
        include_version: bool = True
    ) -> Dict[str, str]:
        """
        Generate RoutineTest exam name with [RT]/[QTR] pattern.
        
        Args:
            exam_type: 'REVIEW' or 'QUARTERLY'
            time_period_month: Month code (e.g., 'JAN', 'FEB')
            time_period_quarter: Quarter code (e.g., 'Q1', 'Q2')
            academic_year: Year (e.g., '2025')
            curriculum_level_id: CurriculumLevel ID
            include_version: Whether to include version/date in name
            
        Returns:
            Dictionary with display_name and base_name
        """
        from core.models import CurriculumLevel
        from datetime import datetime
        import json
        
        console_log = {
            "service": "ExamService",
            "action": "generate_routinetest_exam_name",
            "exam_type": exam_type,
            "time_period_month": time_period_month,
            "time_period_quarter": time_period_quarter,
            "academic_year": academic_year,
            "curriculum_level_id": curriculum_level_id
        }
        logger.info(f"[ROUTINETEST_NAME_GEN] {json.dumps(console_log)}")
        print(f"[ROUTINETEST_NAME_GEN] {json.dumps(console_log)}")
        
        # Determine prefix
        prefix = 'RT' if exam_type == 'REVIEW' else 'QTR'
        
        # Build display name parts
        display_parts = [f"[{prefix}]"]
        base_parts = [prefix]
        
        # Add time period
        if exam_type == 'REVIEW' and time_period_month:
            # Convert month code to display name
            month_choices = dict(Exam.MONTH_CHOICES)
            month_display = month_choices.get(time_period_month, time_period_month)
            if academic_year:
                display_parts.append(f"[{month_display} {academic_year}]")
                base_parts.append(f"{time_period_month}{academic_year}")
            else:
                display_parts.append(f"[{month_display}]")
                base_parts.append(time_period_month)
                
        elif exam_type == 'QUARTERLY' and time_period_quarter:
            quarter_choices = dict(Exam.QUARTER_CHOICES)
            quarter_display = quarter_choices.get(time_period_quarter, time_period_quarter)
            if academic_year:
                display_parts.append(f"[{quarter_display} {academic_year}]")
                base_parts.append(f"{time_period_quarter}{academic_year}")
            else:
                display_parts.append(f"[{quarter_display}]")
                base_parts.append(time_period_quarter)
        
        
        # Add curriculum level
        if curriculum_level_id:
            try:
                curriculum_level = CurriculumLevel.objects.select_related(
                    'subprogram__program'
                ).get(id=curriculum_level_id)
                
                program_name = curriculum_level.subprogram.program.name
                subprogram_name = curriculum_level.subprogram.name
                level_number = curriculum_level.level_number
                
                # Clean subprogram name (remove program prefix if exists)
                clean_subprogram = subprogram_name
                if subprogram_name.startswith(program_name + ' '):
                    clean_subprogram = subprogram_name[len(program_name) + 1:]
                
                # Add to display name
                curriculum_display = f"{program_name} {clean_subprogram} Level {level_number}"
                display_parts.append(curriculum_display)
                
                # Add to base name (file-friendly)
                curriculum_base = f"{program_name}_{clean_subprogram}_Lv{level_number}".replace(" ", "_")
                base_parts.append(curriculum_base)
                
            except CurriculumLevel.DoesNotExist:
                logger.warning(f"[ROUTINETEST_NAME_GEN] Curriculum level {curriculum_level_id} not found")
        
        # Build final names
        display_name = " - ".join(display_parts)
        base_name = "_".join(base_parts)
        
        # Add version/date if requested
        final_name = base_name
        if include_version:
            date_str = datetime.now().strftime('%y%m%d')
            final_name = f"{base_name}_{date_str}"
        
        result = {
            'display_name': display_name,
            'base_name': base_name,
            'final_name': final_name,
            'prefix': prefix
        }
        
        # Log result
        console_log = {
            "service": "ExamService",
            "action": "routinetest_name_generated",
            "display_name": display_name,
            "base_name": base_name,
            "final_name": final_name
        }
        logger.info(f"[ROUTINETEST_NAME_RESULT] {json.dumps(console_log)}")
        print(f"[ROUTINETEST_NAME_RESULT] {json.dumps(console_log)}")
        
        return result
    
    # ========== PDF ROTATION PERSISTENCE FIX ==========
    @staticmethod
    def validate_pdf_file(pdf_file):
        """
        Enhanced PDF file validation to prevent upload failures
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not pdf_file:
            logger.error("[PDF_VALIDATION] No PDF file provided")
            raise ValidationException("PDF file is required", code="MISSING_PDF")
        
        if not pdf_file.name.lower().endswith('.pdf'):
            logger.error(f"[PDF_VALIDATION] Invalid file type: {pdf_file.name}")
            raise ValidationException("File must be a PDF", code="INVALID_FILE_TYPE")
        
        if pdf_file.size == 0:
            logger.error("[PDF_VALIDATION] Empty PDF file")
            raise ValidationException("PDF file is empty", code="EMPTY_FILE")
        
        if pdf_file.size > 10 * 1024 * 1024:  # 10MB
            logger.error(f"[PDF_VALIDATION] File too large: {pdf_file.size} bytes")
            raise ValidationException("PDF file too large (max 10MB)", code="FILE_TOO_LARGE")
        
        # Test file readability
        try:
            current_pos = pdf_file.tell()
            content = pdf_file.read()
            pdf_file.seek(current_pos)  # Reset position
            
            if len(content) == 0:
                logger.error("[PDF_VALIDATION] PDF content is empty")
                raise ValidationException("PDF file content is empty", code="EMPTY_CONTENT")
                
            logger.info(f"[PDF_VALIDATION] ✅ PDF file validated: {pdf_file.name}, {pdf_file.size} bytes")
            return True
            
        except Exception as e:
            logger.error(f"[PDF_VALIDATION] Cannot read PDF: {str(e)}")
            raise ValidationException(f"Cannot read PDF file: {str(e)}", code="READ_ERROR")
    
    @staticmethod
    def log_pdf_save_attempt(exam, pdf_file, step):
        """
        Comprehensive logging for PDF save process
        """
        import logging
        import json
        import os
        logger = logging.getLogger(__name__)
        
        log_data = {
            "action": "pdf_save_process",
            "step": step,
            "exam_id": str(exam.id) if exam else "None",
            "exam_name": exam.name if exam else "None",
            "pdf_rotation": exam.pdf_rotation if exam else "None",
            "pdf_file_name": pdf_file.name if pdf_file else "None",
            "pdf_file_size": pdf_file.size if pdf_file else 0,
        }
        
        if step == "after_save" and exam and exam.pdf_file:
            try:
                log_data.update({
                    "pdf_field_name": exam.pdf_file.name,
                    "pdf_field_url": exam.pdf_file.url,
                    "file_exists_check": os.path.exists(exam.pdf_file.path) if exam.pdf_file.name else False
                })
            except Exception as e:
                log_data["file_check_error"] = str(e)
        
        logger.info(f"[PDF_SAVE_LOG] {json.dumps(log_data)}")
        print(f"[PDF_SAVE_LOG] {json.dumps(log_data)}")
    # ========== END PDF ROTATION PERSISTENCE FIX ==========


class ExamPermissionService:
    """
    Service class for handling all exam-related permissions in the Answer Keys library.
    Provides centralized logic for teacher access control and exam visibility.
    """
    
    # Map class codes to program levels
    CLASS_TO_PROGRAM = {
        # Primary (1-3) -> CORE
        'PRIMARY_1A': 'CORE', 'PRIMARY_1B': 'CORE', 'PRIMARY_1C': 'CORE', 'PRIMARY_1D': 'CORE',
        'PRIMARY_2A': 'CORE', 'PRIMARY_2B': 'CORE', 'PRIMARY_2C': 'CORE', 'PRIMARY_2D': 'CORE',
        'PRIMARY_3A': 'CORE', 'PRIMARY_3B': 'CORE', 'PRIMARY_3C': 'CORE', 'PRIMARY_3D': 'CORE',
        # Primary (4-6) -> ASCENT
        'PRIMARY_4A': 'ASCENT', 'PRIMARY_4B': 'ASCENT', 'PRIMARY_4C': 'ASCENT', 'PRIMARY_4D': 'ASCENT',
        'PRIMARY_5A': 'ASCENT', 'PRIMARY_5B': 'ASCENT', 'PRIMARY_5C': 'ASCENT', 'PRIMARY_5D': 'ASCENT',
        'PRIMARY_6A': 'ASCENT', 'PRIMARY_6B': 'ASCENT', 'PRIMARY_6C': 'ASCENT', 'PRIMARY_6D': 'ASCENT',
        # Middle School -> EDGE
        'MIDDLE_1A': 'EDGE', 'MIDDLE_1B': 'EDGE', 'MIDDLE_1C': 'EDGE', 'MIDDLE_1D': 'EDGE',
        'MIDDLE_2A': 'EDGE', 'MIDDLE_2B': 'EDGE', 'MIDDLE_2C': 'EDGE', 'MIDDLE_2D': 'EDGE',
        'MIDDLE_3A': 'EDGE', 'MIDDLE_3B': 'EDGE', 'MIDDLE_3C': 'EDGE', 'MIDDLE_3D': 'EDGE',
        # High School -> PINNACLE
        'HIGH_1A': 'PINNACLE', 'HIGH_1B': 'PINNACLE', 'HIGH_1C': 'PINNACLE', 'HIGH_1D': 'PINNACLE',
        'HIGH_2A': 'PINNACLE', 'HIGH_2B': 'PINNACLE', 'HIGH_2C': 'PINNACLE', 'HIGH_2D': 'PINNACLE',
        'HIGH_3A': 'PINNACLE', 'HIGH_3B': 'PINNACLE', 'HIGH_3C': 'PINNACLE', 'HIGH_3D': 'PINNACLE',
    }
    
    PROGRAM_ORDER = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']
    
    @classmethod
    def is_admin(cls, user):
        """Check if user is admin"""
        return user.is_superuser or user.is_staff
    
    @classmethod
    def get_teacher_assignments(cls, user):
        """Get all class assignments for a teacher"""
        if not hasattr(user, 'teacher_profile'):
            return {}
        
        from django.db.models import Q
        from django.utils import timezone
        from ..models import TeacherClassAssignment
        
        assignments = TeacherClassAssignment.objects.filter(
            teacher=user.teacher_profile,
            is_active=True
        ).filter(
            Q(expires_on__isnull=True) | Q(expires_on__gt=timezone.now())
        ).values_list('class_code', 'access_level')
        
        return dict(assignments)
    
    @classmethod
    def get_teacher_accessible_classes(cls, user):
        """Get all classes the teacher can access (with any permission level)"""
        if ExamPermissionService.is_admin(user):
            return 'ALL'  # Admins can access all classes
        
        return list(cls.get_teacher_assignments(user).keys())
    
    @classmethod
    def get_teacher_editable_classes(cls, user):
        """Get classes where teacher has edit permissions"""
        if ExamPermissionService.is_admin(user):
            return 'ALL'
        
        assignments = ExamService.get_teacher_assignments(user)
        return [class_code for class_code, access_level in assignments.items() 
                if access_level == 'FULL']
    
    # DUPLICATE METHOD REMOVED - Using primary version at line 469
    # The primary version has been fixed with proper admin check
    # @classmethod
    # def can_teacher_edit_exam(cls, user, exam):
    #     """DUPLICATE - See line 469 for the active version"""
    #     pass
    
    @classmethod
    def can_teacher_copy_exam(cls, user, source_exam):
        """Check if teacher can copy an exam"""
        if ExamPermissionService.is_admin(user):
            return True
        
        if not hasattr(user, 'teacher_profile'):
            return False
        
        # Teacher can copy if they have at least one assigned class
        accessible_classes = cls.get_teacher_accessible_classes(user)
        return accessible_classes and accessible_classes != []
    
    @classmethod
    def can_teacher_delete_exam(cls, user, exam):
        """
        Check if teacher can delete an exam - ENHANCED WITH ROBUST OWNERSHIP RECOGNITION.
        
        Teacher can delete if:
        1. They are admin (superuser or staff)
        2. They created the exam (exam.created_by matches their teacher profile) - OWNER HAS FULL RIGHTS
        3. They have FULL access to at least one of the exam's assigned classes
        """
        import logging
        import json
        from django.utils import timezone
        logger = logging.getLogger(__name__)
        
        # COMPREHENSIVE DEBUG LOGGING
        debug_info = {
            "method": "can_teacher_delete_exam",
            "user": str(user.username) if user else "None",
            "user_id": user.id if user else None,
            "exam_id": str(exam.id) if exam else "None",
            "exam_name": exam.name if exam else "None",
            "timestamp": timezone.now().isoformat()
        }
        
        # Check if user is authenticated
        if not user or not user.is_authenticated:
            debug_info["result"] = "DENIED"
            debug_info["reason"] = "User not authenticated"
            logger.warning(f"[DELETE_PERMISSION] {json.dumps(debug_info)}")
            print(f"[DELETE_PERMISSION_CHECK] {json.dumps(debug_info)}")
            return False
        
        # Admins can delete everything
        if user.is_superuser or user.is_staff:
            debug_info["result"] = "ALLOWED"
            debug_info["reason"] = "User is admin"
            debug_info["is_superuser"] = user.is_superuser
            debug_info["is_staff"] = user.is_staff
            logger.info(f"[DELETE_PERMISSION] {json.dumps(debug_info)}")
            print(f"[DELETE_PERMISSION_CHECK] {json.dumps(debug_info)}")
            return True
        
        # Get teacher profile - try multiple ways
        teacher = None
        if hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
        else:
            # Try to get teacher profile directly from database
            try:
                from core.models import Teacher
                teacher = Teacher.objects.filter(user=user).first()
                if teacher:
                    debug_info["teacher_lookup"] = "Found via database query"
            except Exception as e:
                debug_info["teacher_lookup_error"] = str(e)
        
        if not teacher:
            debug_info["result"] = "DENIED"
            debug_info["reason"] = "No teacher profile found"
            logger.warning(f"[DELETE_PERMISSION] {json.dumps(debug_info)}")
            print(f"[DELETE_PERMISSION_CHECK] {json.dumps(debug_info)}")
            return False
        
        debug_info["teacher_id"] = teacher.id
        debug_info["teacher_name"] = teacher.name
        
        # CRITICAL FIX: Check if teacher created the exam - OWNER HAS FULL RIGHTS
        # Enhanced ownership check with multiple verification methods
        if exam.created_by:
            debug_info["exam_created_by_id"] = exam.created_by.id
            debug_info["exam_created_by_name"] = exam.created_by.name if hasattr(exam.created_by, 'name') else str(exam.created_by)
            debug_info["ownership_check"] = {
                "method1_direct_id": exam.created_by.id == teacher.id,
                "method2_user_match": exam.created_by.user_id == user.id if hasattr(exam.created_by, 'user_id') else False,
                "exam_created_by_type": type(exam.created_by).__name__,
                "teacher_type": type(teacher).__name__
            }
            
            # Primary ownership check - direct ID comparison
            if exam.created_by.id == teacher.id:
                debug_info["result"] = "ALLOWED"
                debug_info["reason"] = "User is exam owner (created_by)"
                logger.info(f"[DELETE_PERMISSION] {json.dumps(debug_info)}")
                print(f"[DELETE_PERMISSION_CHECK] ✅ OWNER ACCESS GRANTED: {json.dumps(debug_info)}")
                return True
            
            # Secondary ownership check - via user relationship
            if hasattr(exam.created_by, 'user_id') and exam.created_by.user_id == user.id:
                debug_info["result"] = "ALLOWED"
                debug_info["reason"] = "User is exam owner (via user_id match)"
                logger.info(f"[DELETE_PERMISSION] {json.dumps(debug_info)}")
                print(f"[DELETE_PERMISSION_CHECK] ✅ OWNER ACCESS GRANTED (secondary check): {json.dumps(debug_info)}")
                return True
        else:
            debug_info["exam_created_by"] = "None"
            debug_info["warning"] = "Exam has no created_by field set"
            logger.warning(f"[DELETE_PERMISSION] Exam {exam.name} has no created_by: {json.dumps(debug_info)}")
        
        # Check if teacher has FULL access to any of the exam's classes
        assignments = cls.get_teacher_assignments(user)
        exam_classes = exam.class_codes if hasattr(exam, 'class_codes') and exam.class_codes else []
        
        debug_info["teacher_assignments"] = list(assignments.keys())
        debug_info["teacher_access_levels"] = assignments
        debug_info["exam_classes"] = exam_classes
        
        for class_code in exam_classes:
            if class_code in assignments:
                access_level = assignments[class_code]
                debug_info[f"class_{class_code}_access"] = access_level
                
                if access_level == 'FULL':
                    debug_info["result"] = "ALLOWED"
                    debug_info["reason"] = f"Teacher has FULL access to class {class_code}"
                    logger.info(f"[DELETE_PERMISSION] {json.dumps(debug_info)}")
                    print(f"[DELETE_PERMISSION_CHECK] ✅ CLASS ACCESS GRANTED: {json.dumps(debug_info)}")
                    return True
        
        # Final denial with comprehensive reason
        debug_info["result"] = "DENIED"
        debug_info["reason"] = "No ownership or FULL class access"
        debug_info["denial_details"] = {
            "is_owner": False,
            "has_full_class_access": False,
            "teacher_classes_with_access": list(assignments.keys()),
            "exam_requires_classes": exam_classes
        }
        logger.info(f"[DELETE_PERMISSION] {json.dumps(debug_info)}")
        print(f"[DELETE_PERMISSION_CHECK] ❌ ACCESS DENIED: {json.dumps(debug_info)}")
        return False
    
    @classmethod
    def get_teacher_copyable_classes(cls, user):
        """Get classes where teacher can copy exams to"""
        if ExamPermissionService.is_admin(user):
            # Return all class codes for admins
            all_class_codes = list(cls.CLASS_TO_PROGRAM.keys())
            return all_class_codes
        
        # For teachers, only return assigned classes
        return cls.get_teacher_accessible_classes(user)
    
    @classmethod
    def get_exam_access_level(cls, user, exam):
        """
        Get the access level for a specific exam
        Returns: 'EDIT', 'COPY', 'VIEW'
        """
        if ExamPermissionService.is_admin(user):
            return 'EDIT'
        
        if not hasattr(user, 'teacher_profile'):
            return 'VIEW'
        
        if cls.can_teacher_edit_exam(user, exam):
            return 'EDIT'
        elif cls.can_teacher_copy_exam(user, source_exam=exam):
            return 'COPY'
        else:
            return 'VIEW'
    
    # REMOVED: Duplicate method - using the primary version above
    # @classmethod
    # def organize_exams_hierarchically(cls, exams, user, assigned_only=False):
    #     """DUPLICATE METHOD REMOVED - SEE PRIMARY VERSION ABOVE"""
    #     pass
    
    @classmethod
    def get_exam_permission_info(cls, user, exam):
        """
        Get comprehensive permission info for an exam
        
        Returns:
            dict: Permission metadata for the exam
        """
        is_admin = cls.is_admin(user)
        access_level = cls.get_exam_access_level(user, exam)
        teacher_assignments = ExamService.get_teacher_assignments(user)
        
        # Check permissions for each class code
        class_permissions = {}
        exam_class_codes = exam.class_codes if exam.class_codes else []
        
        for class_code in exam_class_codes:
            if is_admin:
                class_permissions[class_code] = {
                    'access_level': 'FULL',
                    'can_edit': True,
                    'can_copy': True,
                    'is_accessible': True,
                    'visual_style': 'accessible'
                }
            elif class_code in teacher_assignments:
                teacher_access = teacher_assignments[class_code]
                can_edit = teacher_access == 'FULL'
                class_permissions[class_code] = {
                    'access_level': teacher_access,
                    'can_edit': can_edit,
                    'can_copy': True,
                    'is_accessible': True,
                    'visual_style': 'accessible'
                }
            else:
                class_permissions[class_code] = {
                    'access_level': 'VIEW',
                    'can_edit': False,
                    'can_copy': True,  # Can copy to their own classes
                    'is_accessible': False,
                    'visual_style': 'view-only'
                }
        
        # Determine overall exam permissions
        can_edit_any = any(perm['can_edit'] for perm in class_permissions.values())
        can_copy = cls.can_teacher_copy_exam(user, exam)
        has_accessible_classes = any(perm['is_accessible'] for perm in class_permissions.values())
        
        return {
            'access_level': access_level,
            'can_edit': can_edit_any,
            'can_copy': can_copy,
            'can_view': True,  # Everyone can view
            'has_accessible_classes': has_accessible_classes,
            'class_permissions': class_permissions,
            'is_admin': is_admin
        }
    
    @classmethod
    def filter_exams_by_permission(cls, exams, user, filter_type='all'):
        """
        Filter exams based on user permissions
        
        Args:
            exams: QuerySet of exams
            user: Current user
            filter_type: 'all', 'editable', 'assigned_only'
        
        Returns:
            Filtered QuerySet
        """
        if filter_type == 'all':
            return exams
        
        if ExamPermissionService.is_admin(user):
            return exams  # Admins see everything
        
        if not hasattr(user, 'teacher_profile'):
            return exams  # Non-teachers see everything in view mode
        
        teacher_assignments = ExamService.get_teacher_assignments(user)
        assigned_class_codes = list(teacher_assignments.keys())
        
        if filter_type == 'assigned_only':
            # Only show exams from classes teacher is assigned to
            filtered_exams = []
            for exam in exams:
                exam_class_codes = exam.class_codes if exam.class_codes else []
                if any(code in assigned_class_codes for code in exam_class_codes):
                    filtered_exams.append(exam.id)
            return exams.filter(id__in=filtered_exams)
        
        elif filter_type == 'editable':
            # Only show exams teacher can edit
            editable_class_codes = [
                code for code, access in teacher_assignments.items() 
                if access == 'FULL'
            ]
            filtered_exams = []
            for exam in exams:
                exam_class_codes = exam.class_codes if exam.class_codes else []
                if any(code in editable_class_codes for code in exam_class_codes):
                    filtered_exams.append(exam.id)
            return exams.filter(id__in=filtered_exams)
        
        return exams
    
    @classmethod
    def get_permission_summary(cls, user):
        """Get summary of user's permissions for debugging"""
        teacher_assignments = ExamService.get_teacher_assignments(user)
        accessible_classes = cls.get_teacher_accessible_classes(user)
        editable_classes = cls.get_teacher_editable_classes(user)
        copyable_classes = cls.get_teacher_copyable_classes(user)
        
        return {
            'is_admin': cls.is_admin(user),
            'has_teacher_profile': hasattr(user, 'teacher_profile'),
            'teacher_assignments': teacher_assignments,
            'accessible_classes': accessible_classes,
            'editable_classes': editable_classes,
            'copyable_classes_count': len(copyable_classes) if isinstance(copyable_classes, list) else 'ALL',
        }
    
    @classmethod
    def organize_exams_hierarchically(cls, exams, user, filter_assigned_only=False):
        """
        Delegate to ExamService.organize_exams_hierarchically for backward compatibility.
        This prevents AttributeError if code tries to call this method on ExamPermissionService.
        """
        return ExamService.organize_exams_hierarchically(
            exams, user, filter_assigned_only=filter_assigned_only
        )

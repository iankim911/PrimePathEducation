"""
Exam and AudioFile models
Part of Phase 9: Model Modularization
"""
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
import uuid


class Exam(models.Model):
    """Main exam model containing test information and configuration"""
    # Exam Type choices for RoutineTest module
    EXAM_TYPE_CHOICES = [
        ('REVIEW', 'Review / Monthly Exam'),
        ('QUARTERLY', 'Quarterly Exam'),
    ]
    
    # Month choices for Review/Monthly exams
    MONTH_CHOICES = [
        ('JAN', 'January'),
        ('FEB', 'February'),
        ('MAR', 'March'),
        ('APR', 'April'),
        ('MAY', 'May'),
        ('JUN', 'June'),
        ('JUL', 'July'),
        ('AUG', 'August'),
        ('SEP', 'September'),
        ('OCT', 'October'),
        ('NOV', 'November'),
        ('DEC', 'December'),
    ]
    
    # Quarter choices for Quarterly exams
    QUARTER_CHOICES = [
        ('Q1', 'Q1 (Jan-Mar)'),
        ('Q2', 'Q2 (Apr-Jun)'),
        ('Q3', 'Q3 (Jul-Sep)'),
        ('Q4', 'Q4 (Oct-Dec)'),
    ]
    
    # Academic year choices (2025-2030 as requested)
    ACADEMIC_YEAR_CHOICES = [
        ('2025', '2025'),
        ('2026', '2026'),
        ('2027', '2027'),
        ('2028', '2028'),
        ('2029', '2029'),
        ('2030', '2030'),
    ]
    
    
    # Dynamic class code choices from PrimePath curriculum mapping
    @classmethod
    def get_class_code_choices(cls):
        """Get class choices dynamically from the Class model and curriculum mapping"""
        from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING
        from .class_model import Class
        
        choices = []
        
        # First, add all class codes from the curriculum mapping
        for code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
            choices.append((code, f"{code} - {curriculum}"))
        
        # Also include any existing classes from the database
        existing_classes = Class.objects.filter(is_active=True).values_list('section', 'name')
        existing_codes = {code for code, _ in choices}
        
        for section, name in existing_classes:
            if section and section not in existing_codes:
                display_name = name if name else section
                choices.append((section, display_name))
        
        # Sort by code for consistent ordering
        choices.sort(key=lambda x: x[0])
        
        return choices
    
    # For backward compatibility, maintain CLASS_CODE_CHOICES as a property
    CLASS_CODE_CHOICES = []  # Will be populated dynamically
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    
    # RoutineTest specific field - exam type
    exam_type = models.CharField(
        max_length=10, 
        choices=EXAM_TYPE_CHOICES,
        default='REVIEW',
        help_text="Type of exam: Review (monthly) or Quarterly"
    )
    
    # Phase 2: Time period fields
    time_period_month = models.CharField(
        max_length=3,
        choices=MONTH_CHOICES,
        null=True,
        blank=True,
        help_text="Month for Review/Monthly exams"
    )
    
    time_period_quarter = models.CharField(
        max_length=2,
        choices=QUARTER_CHOICES,
        null=True,
        blank=True,
        help_text="Quarter for Quarterly exams"
    )
    
    academic_year = models.CharField(
        max_length=4,
        choices=ACADEMIC_YEAR_CHOICES,
        null=True,
        blank=True,
        help_text="Academic year for the exam"
    )
    
    
    # Phase 3: Class codes (DEPRECATED - use class_code instead)
    # Kept for backward compatibility during migration
    class_codes = models.JSONField(
        default=list,
        blank=True,
        help_text="DEPRECATED: List of class codes (migrate to class_code field)"
    )
    
    # Phase 4: Single class code (ONE-TO-ONE relationship)
    class_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=CLASS_CODE_CHOICES,
        help_text="Single class code this exam belongs to (one-to-one relationship)",
        db_index=True  # Add index for performance
    )
    
    # Exam-level instructions (kept from Phase 4, but scheduling moved to ClassExamSchedule)
    instructions = models.TextField(
        blank=True,
        default='',
        help_text="General instructions for students taking this exam"
    )
    
    curriculum_level = models.ForeignKey(
        'core.CurriculumLevel', 
        on_delete=models.CASCADE, 
        related_name='routine_exams', 
        null=True, 
        blank=True
    )
    pdf_file = models.FileField(
        upload_to='routinetest/exams/pdfs/',
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Maximum file size: 10MB"
    )
    timer_minutes = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    total_questions = models.IntegerField(validators=[MinValueValidator(1)])
    default_options_count = models.IntegerField(
        default=5, 
        validators=[MinValueValidator(2), MaxValueValidator(10)]
    )
    passing_score = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    pdf_rotation = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(270)],
        help_text="PDF rotation angle in degrees (0, 90, 180, 270)"
    )
    created_by = models.ForeignKey('core.Teacher', on_delete=models.SET_NULL, null=True, related_name='routine_exams_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['curriculum_level', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        exam_type_label = dict(self.EXAM_TYPE_CHOICES).get(self.exam_type, self.exam_type)
        time_period = self.get_time_period_display()
        base_str = f"[{exam_type_label}] {self.name}"
        
        if time_period:
            base_str += f" - {time_period}"
        
        if self.curriculum_level:
            base_str += f" - {self.curriculum_level.full_name}"
        
        return base_str
    
    def get_exam_type_display_short(self):
        """Get short display name for exam type"""
        if self.exam_type == 'REVIEW':
            return 'Review'
        elif self.exam_type == 'QUARTERLY':
            return 'Quarterly'
        return self.exam_type
    
    def get_time_period_display(self):
        """Get formatted time period display based on exam type"""
        if self.exam_type == 'REVIEW' and self.time_period_month:
            month_display = dict(self.MONTH_CHOICES).get(self.time_period_month, self.time_period_month)
            if self.academic_year:
                return f"{month_display} {self.academic_year}"
            return month_display
        elif self.exam_type == 'QUARTERLY' and self.time_period_quarter:
            quarter_display = dict(self.QUARTER_CHOICES).get(self.time_period_quarter, self.time_period_quarter)
            if self.academic_year:
                return f"{quarter_display} {self.academic_year}"
            return quarter_display
        return ""
    
    def get_time_period_short(self):
        """Get short time period display for compact views"""
        if self.exam_type == 'REVIEW' and self.time_period_month:
            if self.academic_year:
                return f"{self.time_period_month} {self.academic_year}"
            return self.time_period_month
        elif self.exam_type == 'QUARTERLY' and self.time_period_quarter:
            if self.academic_year:
                return f"{self.time_period_quarter} {self.academic_year}"
            return self.time_period_quarter
        return ""
    
    def get_class_codes_display(self):
        """Get formatted display of selected class codes - UPDATED for single class"""
        # Use new single class_code field if available
        if self.class_code:
            class_dict = dict(self.CLASS_CODE_CHOICES)
            return class_dict.get(self.class_code, self.class_code)
        
        # Fallback to old class_codes for backward compatibility
        if not self.class_codes:
            return ""
        
        # Convert codes to display names
        class_dict = dict(self.CLASS_CODE_CHOICES)
        display_names = [class_dict.get(code, code) for code in self.class_codes]
        
        # Log warning if multiple classes detected
        if len(display_names) > 1:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"[ONE_TO_ONE_FIX] Exam {self.id} still has multiple classes: {display_names}")
        
        if len(display_names) <= 4:
            return ", ".join(display_names)
        else:
            return f"{', '.join(display_names[:3])}... (+{len(display_names)-3} more)"
    
    def get_class_codes_short(self):
        """Get short display of class codes for compact views - UPDATED for single class"""
        # Use new single class_code field if available
        if self.class_code:
            return self.class_code.replace('CLASS_', '')
        
        # Fallback to old class_codes
        if not self.class_codes:
            return ""
        
        if len(self.class_codes) == 1:
            # Remove 'CLASS_' prefix for short display
            return self.class_codes[0].replace('CLASS_', '')
        elif len(self.class_codes) <= 3:
            codes = [code.replace('CLASS_', '') for code in self.class_codes]
            return ", ".join(codes)
        else:
            return f"{len(self.class_codes)} classes"
    
    def get_class_codes_list(self):
        """Get list of class codes with their display names - UPDATED for single class"""
        # Use new single class_code field if available
        if self.class_code:
            class_dict = dict(self.CLASS_CODE_CHOICES)
            return [{'code': self.class_code, 'name': class_dict.get(self.class_code, self.class_code)}]
        
        # Fallback to old class_codes
        if not self.class_codes:
            return []
        
        class_dict = dict(self.CLASS_CODE_CHOICES)
        return [
            {'code': code, 'name': class_dict.get(code, code)}
            for code in self.class_codes
        ]
    
    @property
    def effective_class_codes(self):
        """
        Property to get effective class codes for backward compatibility.
        Returns a list for compatibility, but should only have one item.
        """
        if self.class_code:
            # New single class field - return as single-item list for compatibility
            return [self.class_code]
        elif self.class_codes:
            # Old multi-class field - log warning if multiple
            if isinstance(self.class_codes, list) and len(self.class_codes) > 1:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"[ONE_TO_ONE_WARNING] Exam {self.id} has {len(self.class_codes)} classes - should be migrated to single class")
            return self.class_codes if isinstance(self.class_codes, list) else []
        else:
            return []
    
    @property
    def effective_class_code(self):
        """
        Property to get the single effective class code.
        This is the preferred method for new code.
        """
        if self.class_code:
            return self.class_code
        elif self.class_codes and isinstance(self.class_codes, list) and len(self.class_codes) > 0:
            # Return first class from old field as fallback
            return self.class_codes[0]
        else:
            return None
    
    def get_class_schedules(self):
        """Get all class schedules for this exam"""
        return self.class_schedules.filter(is_active=True).order_by('scheduled_date', 'scheduled_start_time')
    
    def has_class_schedules(self):
        """Check if exam has any class-specific schedules"""
        return self.class_schedules.filter(is_active=True).exists()
    
    def get_schedule_for_class(self, class_code):
        """Get schedule for a specific class"""
        try:
            return self.class_schedules.get(class_code=class_code, is_active=True)
        except:
            return None
    
    # ==================== ROUTINETEST [RT]/[QTR] NAMING SYSTEM ====================
    
    def get_routinetest_prefix(self):
        """Get [REVIEW] or [QUARTERLY] prefix based on exam type per PRD"""
        if self.exam_type == 'REVIEW':
            return 'REVIEW'
        elif self.exam_type == 'QUARTERLY':
            return 'QUARTERLY'
        return 'REVIEW'  # Default fallback
    
    
    def get_routinetest_display_name(self):
        """
        Get RoutineTest display name in format per PRD:
        [REVIEW | January] - CORE Phonics Level 1
        [QUARTERLY | Q1] - CORE Phonics Level 1
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Build prefix with time period per PRD format
        prefix = self.get_routinetest_prefix()
        
        # Get just the month/quarter without year
        if self.exam_type == 'REVIEW' and self.time_period_month:
            month_display = dict(self.MONTH_CHOICES).get(self.time_period_month, self.time_period_month)
            prefix_with_period = f"[{prefix} | {month_display}]"
        elif self.exam_type == 'QUARTERLY' and self.time_period_quarter:
            quarter_display = self.time_period_quarter  # Just Q1, Q2, etc
            prefix_with_period = f"[{prefix} | {quarter_display}]"
        else:
            prefix_with_period = f"[{prefix}]"
        
        parts = [prefix_with_period]
        
        
        # Add curriculum level
        if self.curriculum_level:
            # Format: CORE Phonics Level 1 (using the program and subprogram names)
            program_name = self.curriculum_level.subprogram.program.name
            subprogram_name = self.curriculum_level.subprogram.name
            level_number = self.curriculum_level.level_number
            
            # Clean subprogram name (remove program prefix if exists)
            clean_subprogram = subprogram_name
            if subprogram_name.startswith(program_name + ' '):
                clean_subprogram = subprogram_name[len(program_name) + 1:]
            
            curriculum_display = f"{program_name} {clean_subprogram} Level {level_number}"
            parts.append(curriculum_display)
        
        display_name = " - ".join(parts)
        
        # Log the name generation
        console_log = {
            "model": "Exam",
            "action": "get_routinetest_display_name",
            "exam_id": str(self.id),
            "exam_type": self.exam_type,
            "prefix": prefix,
            "time_period": self.get_time_period_display(),
            "curriculum": self.curriculum_level.full_name if self.curriculum_level else None,
            "generated_name": display_name
        }
        logger.info(f"[ROUTINETEST_NAMING] {console_log}")
        print(f"[ROUTINETEST_NAMING] {console_log}")
        
        return display_name
    
    def get_routinetest_base_name(self):
        """
        Get RoutineTest base name for file naming:
        RT_January_CORE_Phonics_Lv1
        QTR_Q1_CORE_Phonics_Lv1
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Start with prefix
        prefix = self.get_routinetest_prefix()
        parts = [prefix]
        
        # Add time period (short format)
        time_period_short = self.get_time_period_short()
        if time_period_short:
            # Clean up time period for file naming (remove spaces, special chars)
            clean_period = time_period_short.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
            parts.append(clean_period)
        
        
        # Add curriculum level
        if self.curriculum_level:
            program_name = self.curriculum_level.subprogram.program.name
            subprogram_name = self.curriculum_level.subprogram.name
            level_number = self.curriculum_level.level_number
            
            # Clean subprogram name
            clean_subprogram = subprogram_name
            if subprogram_name.startswith(program_name + ' '):
                clean_subprogram = subprogram_name[len(program_name) + 1:]
            
            # Format for file naming: CORE_Phonics_Lv1
            curriculum_base = f"{program_name}_{clean_subprogram}_Lv{level_number}".replace(" ", "_")
            parts.append(curriculum_base)
        
        base_name = "_".join(parts)
        
        # Log the base name generation
        console_log = {
            "model": "Exam",
            "action": "get_routinetest_base_name",
            "exam_id": str(self.id),
            "exam_type": self.exam_type,
            "generated_base_name": base_name
        }
        logger.info(f"[ROUTINETEST_BASE_NAMING] {console_log}")
        print(f"[ROUTINETEST_BASE_NAMING] {console_log}")
        
        return base_name
    
    def get_answer_mapping_status(self):
        """
        Check the answer mapping status for this exam.
        Returns a dict with detailed status information.
        
        Returns:
            dict: {
                'is_complete': bool - True if all questions have answers
                'total_questions': int - Total number of questions
                'mapped_questions': int - Questions with answers
                'unmapped_questions': int - Questions without answers
                'unmapped_question_numbers': list - Question numbers without answers
                'percentage_complete': float - Percentage of questions with answers
                'status_label': str - 'Complete', 'Partial', or 'Not Started'
                'status_color': str - CSS color class for status display
                'status_class': str - CSS-friendly class name for status (complete, partial, not-started)
            }
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Get all questions for this exam
            questions = self.routine_questions.all()
            total_questions = questions.count()
            
            if total_questions == 0:
                # No questions created yet
                logger.warning(f"[ANSWER_MAPPING] Exam {self.id} has no questions")
                return {
                    'is_complete': False,
                    'total_questions': 0,
                    'mapped_questions': 0,
                    'unmapped_questions': 0,
                    'unmapped_question_numbers': [],
                    'percentage_complete': 0,
                    'status_label': 'No Questions',
                    'status_color': 'warning'
                }
            
            # Check which questions have answers
            unmapped = []
            mapped_count = 0
            
            for question in questions:
                has_answer = False
                
                # Check if question has an answer based on its type
                if question.question_type in ['MCQ', 'CHECKBOX']:
                    # For MCQ and CHECKBOX, check if correct_answer is not empty
                    has_answer = bool(question.correct_answer and question.correct_answer.strip())
                elif question.question_type in ['SHORT', 'LONG', 'MIXED']:
                    # For text-based answers, check if correct_answer has content
                    has_answer = bool(question.correct_answer and question.correct_answer.strip())
                
                if has_answer:
                    mapped_count += 1
                else:
                    unmapped.append(question.question_number)
            
            unmapped_count = len(unmapped)
            percentage_complete = (mapped_count / total_questions * 100) if total_questions > 0 else 0
            
            # Determine status label and color
            if unmapped_count == 0:
                status_label = 'Complete'
                status_color = 'success'
                status_class = 'complete'
                is_complete = True
            elif mapped_count == 0:
                status_label = 'Not Started'
                status_color = 'danger'
                status_class = 'not-started'
                is_complete = False
            else:
                status_label = 'Partial'
                status_color = 'warning'
                status_class = 'partial'
                is_complete = False
            
            # Log the status check
            logger.info(f"[ANSWER_MAPPING] Exam {self.id} ({self.name}): "
                       f"{mapped_count}/{total_questions} questions mapped. "
                       f"Status: {status_label}")
            
            return {
                'is_complete': is_complete,
                'total_questions': total_questions,
                'mapped_questions': mapped_count,
                'unmapped_questions': unmapped_count,
                'unmapped_question_numbers': unmapped[:10],  # Limit to first 10 for display
                'percentage_complete': round(percentage_complete, 1),
                'status_label': status_label,
                'status_color': status_color,
                'status_class': status_class
            }
            
        except Exception as e:
            logger.error(f"[ANSWER_MAPPING_ERROR] Error checking answer mapping for exam {self.id}: {str(e)}")
            return {
                'is_complete': False,
                'total_questions': 0,
                'mapped_questions': 0,
                'unmapped_questions': 0,
                'unmapped_question_numbers': [],
                'percentage_complete': 0,
                'status_label': 'Error',
                'status_color': 'danger',
                'status_class': 'error'
            }
    
    def has_all_answers_mapped(self):
        """
        Quick check if all questions have answers mapped.
        Returns True only if ALL questions have answers.
        """
        status = self.get_answer_mapping_status()
        return status['is_complete']
    
    # Phase 5: Student Roster Methods
    def get_roster_stats(self):
        """
        Get statistics about student roster assignments.
        
        Returns:
            dict: Statistics about roster assignments and completion
        """
        roster_entries = self.student_roster.all()
        total_assigned = roster_entries.count()
        
        if total_assigned == 0:
            return {
                'total_assigned': 0,
                'not_started': 0,
                'in_progress': 0,
                'completed': 0,
                'excused': 0,
                'completion_rate': 0,
                'has_roster': False
            }
        
        not_started = roster_entries.filter(completion_status='NOT_STARTED').count()
        in_progress = roster_entries.filter(completion_status='IN_PROGRESS').count()
        completed = roster_entries.filter(completion_status='COMPLETED').count()
        excused = roster_entries.filter(completion_status='EXCUSED').count()
        
        completion_rate = (completed / total_assigned * 100) if total_assigned > 0 else 0
        
        return {
            'total_assigned': total_assigned,
            'not_started': not_started,
            'in_progress': in_progress,
            'completed': completed,
            'excused': excused,
            'completion_rate': round(completion_rate, 1),
            'has_roster': True
        }
    
    def get_roster_by_class(self):
        """
        Get roster grouped by class code.
        
        Returns:
            dict: Roster entries grouped by class
        """
        from collections import defaultdict
        roster_by_class = defaultdict(list)
        
        for entry in self.student_roster.select_related('session').all():
            roster_by_class[entry.class_code].append(entry)
        
        return dict(roster_by_class)
    
    def has_student_roster(self):
        """Check if exam has any roster assignments"""
        return self.student_roster.exists()
    
    # ========== PERMISSION AND ACCESS METHODS FOR ANSWER KEYS LIBRARY ==========
    
    def get_accessible_classes(self, teacher):
        """
        Get class codes from this exam that the teacher can access
        
        Args:
            teacher: Teacher instance
            
        Returns:
            list: Class codes the teacher can access
        """
        from ..services.exam_service import ExamPermissionService
        if not teacher or not hasattr(teacher, 'user'):
            return []
        
        teacher_assignments = ExamPermissionService.get_teacher_assignments(teacher.user)
        exam_class_codes = self.class_codes if self.class_codes else []
        
        return [code for code in exam_class_codes if code in teacher_assignments]
    
    def can_teacher_edit(self, teacher):
        """
        Check if teacher can edit this exam
        
        Args:
            teacher: Teacher instance or User instance
            
        Returns:
            bool: True if teacher can edit this exam
        """
        from ..services.exam_service import ExamPermissionService
        
        # Handle both Teacher and User instances
        if hasattr(teacher, 'user'):
            user = teacher.user
        else:
            user = teacher
        
        return ExamPermissionService.can_teacher_edit_exam(user, self)
    
    def can_teacher_copy(self, teacher):
        """
        Check if teacher can copy this exam
        
        Args:
            teacher: Teacher instance or User instance
            
        Returns:
            bool: True if teacher can copy this exam
        """
        from ..services.exam_service import ExamPermissionService
        
        # Handle both Teacher and User instances  
        if hasattr(teacher, 'user'):
            user = teacher.user
        else:
            user = teacher
        
        return ExamPermissionService.can_teacher_copy_exam(user, self)
    
    def get_permission_info(self, user):
        """
        Get comprehensive permission info for this exam and the given user
        
        Args:
            user: User instance
            
        Returns:
            dict: Permission metadata
        """
        from ..services.exam_service import ExamPermissionService
        return ExamPermissionService.get_exam_permission_info(user, self)
    
    def get_program_from_class_codes(self):
        """
        Get the program level(s) this exam belongs to based on class codes
        
        Returns:
            set: Program names (CORE, ASCENT, EDGE, PINNACLE)
        """
        from ..services.exam_service import ExamPermissionService
        
        programs = set()
        exam_class_codes = self.class_codes if self.class_codes else []
        
        for class_code in exam_class_codes:
            program = ExamPermissionService.CLASS_TO_PROGRAM.get(class_code, 'CORE')
            programs.add(program)
        
        return programs
    
    def get_primary_program(self):
        """
        Get the primary program for this exam (first one alphabetically)
        
        Returns:
            str: Program name
        """
        programs = self.get_program_from_class_codes()
        if not programs:
            return 'CORE'
        
        # Return in order of PROGRAM_ORDER
        from ..services.exam_service import ExamPermissionService
        for program in ExamPermissionService.PROGRAM_ORDER:
            if program in programs:
                return program
        
        return 'CORE'
    
    def get_class_permissions_for_user(self, user):
        """
        Get permission info for each class code in this exam
        
        Args:
            user: User instance
            
        Returns:
            dict: Class code -> permission info mapping
        """
        permission_info = self.get_permission_info(user)
        return permission_info.get('class_permissions', {})
    
    def has_accessible_classes_for_user(self, user):
        """
        Check if user has any accessible classes for this exam
        
        Args:
            user: User instance
            
        Returns:
            bool: True if user can access at least one class
        """
        permission_info = self.get_permission_info(user)
        return permission_info.get('has_accessible_classes', False)
    
    @classmethod
    def create_copy(cls, source_exam, target_class_codes, exam_type=None, time_period=None, 
                   academic_year=None, created_by=None):
        """
        Create a copy of an exam for different classes
        
        Args:
            source_exam: Source Exam instance to copy
            target_class_codes: List of class codes for the new exam
            exam_type: New exam type (REVIEW/QUARTERLY) or None to keep same
            time_period: New time period or None to keep same
            academic_year: New academic year or None to keep same
            created_by: Teacher creating the copy
            
        Returns:
            Exam: New exam instance
        """
        import copy
        from django.db import transaction
        
        with transaction.atomic():
            # Create the new exam
            new_exam = cls()
            
            # Copy basic fields
            new_exam.name = f"Copy of {source_exam.name}"
            new_exam.exam_type = exam_type or source_exam.exam_type
            new_exam.curriculum_level = source_exam.curriculum_level
            new_exam.timer_minutes = source_exam.timer_minutes
            new_exam.total_questions = source_exam.total_questions
            new_exam.default_options_count = source_exam.default_options_count
            new_exam.passing_score = source_exam.passing_score
            new_exam.pdf_rotation = source_exam.pdf_rotation
            new_exam.instructions = source_exam.instructions
            new_exam.created_by = created_by
            new_exam.is_active = True
            
            # Set time period fields based on exam type
            if new_exam.exam_type == 'REVIEW':
                new_exam.time_period_month = time_period or source_exam.time_period_month
                new_exam.time_period_quarter = None
            elif new_exam.exam_type == 'QUARTERLY':
                new_exam.time_period_quarter = time_period or source_exam.time_period_quarter
                new_exam.time_period_month = None
            
            new_exam.academic_year = academic_year or source_exam.academic_year
            new_exam.class_codes = target_class_codes
            
            # Copy PDF file
            if source_exam.pdf_file:
                new_exam.pdf_file = source_exam.pdf_file
            
            new_exam.save()
            
            # Copy questions
            for source_question in source_exam.routine_questions.all():
                source_question.pk = None  # Reset primary key
                source_question.exam = new_exam
                source_question.save()
            
            # Copy audio files
            for source_audio in source_exam.routine_audio_files.all():
                source_audio.pk = None  # Reset primary key
                source_audio.exam = new_exam
                source_audio.save()
            
            return new_exam


class StudentRoster(models.Model):
    """
    Phase 5: Student Roster & Assignment
    Tracks which students are assigned to take an exam
    """
    COMPLETION_STATUS = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('EXCUSED', 'Excused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_roster')
    
    # Student information
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(
        max_length=50, 
        blank=True,
        help_text="School student ID or roll number"
    )
    class_code = models.CharField(
        max_length=20,
        choices=Exam.CLASS_CODE_CHOICES,
        help_text="Student's class"
    )
    
    # Assignment tracking
    assigned_by = models.ForeignKey(
        'core.Teacher', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='roster_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    # Completion tracking
    completion_status = models.CharField(
        max_length=20,
        choices=COMPLETION_STATUS,
        default='NOT_STARTED'
    )
    session = models.ForeignKey(
        'primepath_routinetest.StudentSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roster_entry',
        help_text="Linked session when student takes the exam"
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Special notes about this student's assignment"
    )
    
    class Meta:
        ordering = ['class_code', 'student_name']
        unique_together = ['exam', 'student_name', 'student_id']
        indexes = [
            models.Index(fields=['exam', 'completion_status']),
            models.Index(fields=['exam', 'class_code']),
        ]
    
    def __str__(self):
        return f"{self.student_name} ({self.class_code}) - {self.exam.name}"
    
    def update_completion_status(self):
        """Update completion status based on linked session"""
        if self.session:
            if self.session.completed_at:
                self.completion_status = 'COMPLETED'
                self.completed_at = self.session.completed_at
            else:
                self.completion_status = 'IN_PROGRESS'
        return self.completion_status
    
    def get_status_display_with_icon(self):
        """Get status with appropriate icon"""
        icons = {
            'NOT_STARTED': '⏳',
            'IN_PROGRESS': '📝',
            'COMPLETED': '✅',
            'EXCUSED': '🔄',
        }
        return f"{icons.get(self.completion_status, '')} {self.get_completion_status_display()}"


class AudioFile(models.Model):
    """Audio file model for listening comprehension questions"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='routine_audio_files')
    name = models.CharField(
        max_length=200, 
        help_text="Descriptive name for this audio file", 
        default="Audio File"
    )
    audio_file = models.FileField(
        upload_to='routinetest/exams/audio/',
        validators=[FileExtensionValidator(['mp3', 'wav', 'm4a'])]
    )
    start_question = models.IntegerField(validators=[MinValueValidator(1)])
    end_question = models.IntegerField(validators=[MinValueValidator(1)])
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'start_question']
        indexes = [
            models.Index(fields=['exam', 'order']),
        ]

    def __str__(self):
        if hasattr(self, 'name') and self.name:
            return f"{self.name} (Q{self.start_question}-{self.end_question})"
        return f"Audio for Q{self.start_question}-{self.end_question}"
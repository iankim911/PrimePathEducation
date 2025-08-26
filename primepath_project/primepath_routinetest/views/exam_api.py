"""
Exam Management API Views
Handles AJAX requests for exam management modal
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json
import logging

from ..models import ExamAssignment, Class, StudentEnrollment
from ..models.class_access import TeacherClassAssignment  # Import from correct module
from ..models.exam_management import RoutineExam  # Use RoutineExam for exam management
# Removed legacy Exam import - only use RoutineExam for RoutineTest module
from core.models import Student, Teacher
from placement_test.models import StudentSession

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def get_class_overview(request, class_code):
    """Get overview data for a class and timeslot"""
    timeslot = request.GET.get('timeslot', '')
    
    try:
        # First, check if class exists in TeacherClassAssignment (this is the actual data)
        assignment = TeacherClassAssignment.objects.filter(
            class_code=class_code, 
            is_active=True
        ).first()
        
        if not assignment:
            # If no assignment exists, return meaningful data anyway
            logger.warning(f"No active assignment found for class {class_code}")
            return JsonResponse({
                'class_code': class_code,
                'class_name': class_code.replace('_', ' ').title(),
                'curriculum': 'Not configured',
                'timeslot': timeslot,
                'exams': [],
                'warning': 'No active teacher assignment found for this class'
            })
        
        # Get class information - try Class model first, fallback to assignment data
        class_obj = Class.objects.filter(name=class_code).first()
        class_display_name = class_obj.name if class_obj else assignment.get_class_code_display()
        
        # Get curriculum mapping - schedule_matrix_optimized removed, using default
        curriculum = None  # Matrix optimization removed, curriculum handled differently now
        
        # Get exams for this timeslot from multiple sources
        exams = []
        
        # Method 1: Try ExamAssignment if Class object exists
        if class_obj:
            assignments = ExamAssignment.objects.filter(
                class_assigned=class_obj
            ).select_related('exam')
            
            for assignment in assignments:
                exam = assignment.exam  # This is a RoutineExam instance
                exam_name = exam.name
                exam_type = getattr(exam, 'exam_type', 'monthly_review')
                
                # Convert exam_type to display format
                type_display = 'Review' if exam_type == 'monthly_review' else 'Quarterly'
                
                exams.append({
                    'id': str(exam.id),
                    'name': exam_name,
                    'type': type_display,
                    'status': 'Assigned',
                    'duration': 60  # RoutineExam doesn't have timer_minutes field
                })
        
        # Method 2: Get exams from ExamScheduleMatrix
        # CRITICAL FIX: Apply same overview logic here for consistency
        try:
            from ..models import ExamScheduleMatrix
            if timeslot and timeslot.lower() != 'overview':
                # Filter by specific timeslot
                logger.info(f"[OVERVIEW_API_FIX] Filtering by specific timeslot: {timeslot} for class {class_code}")
                matrix_entries = ExamScheduleMatrix.objects.filter(
                    class_code=class_code,
                    time_period_value=timeslot
                ).prefetch_related('exams')
            else:
                # For 'overview', get ALL exams for this class
                logger.info(f"[OVERVIEW_API_FIX] Getting ALL exams for class {class_code} (overview mode)")
                matrix_entries = ExamScheduleMatrix.objects.filter(
                    class_code=class_code
                ).prefetch_related('exams')
            
            for matrix_entry in matrix_entries:
                for exam in matrix_entry.exams.all():
                    # Avoid duplicates
                    existing_ids = [e['id'] for e in exams]
                    if str(exam.id) not in existing_ids:
                        exam_type = getattr(exam, 'exam_type', None)
                        if exam_type:
                            # RoutineExam
                            type_display = 'Review' if exam_type == 'monthly_review' else 'Quarterly'
                            duration = 60
                        else:
                            # Legacy Exam
                            type_display = 'Review' if 'review' in exam.name.lower() else 'Quarterly'
                            duration = getattr(exam, 'timer_minutes', 60)
                        
                        exams.append({
                            'id': str(exam.id),
                            'name': exam.name,
                            'type': type_display,
                            'status': 'Scheduled',
                            'duration': duration
                        })
        except Exception as matrix_error:
            logger.warning(f"Could not access ExamScheduleMatrix: {matrix_error}")
        
        return JsonResponse({
            'class_code': class_code,
            'class_name': class_display_name,
            'curriculum': curriculum,
            'timeslot': timeslot,
            'exams': exams,
            'teacher': assignment.teacher.name if assignment and assignment.teacher else 'Not assigned'
        })
        
    except Exception as e:
        logger.error(f"Error getting class overview for {class_code}: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Error loading overview data: {str(e)}',
            'class_code': class_code,
            'timeslot': timeslot,
            'exams': []
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_class_exams(request, class_code):
    """Get all exams for a class and timeslot from both ExamAssignment and ExamScheduleMatrix"""
    timeslot = request.GET.get('timeslot', '')
    
    try:
        from primepath_routinetest.models import ExamScheduleMatrix
        exams = []
        
        # First, get exams from ExamAssignment (legacy system)
        try:
            # Find class by name (class_code is actually the class name)
            class_obj = Class.objects.filter(name=class_code).first()
            if class_obj:
                assignments = ExamAssignment.objects.filter(
                    class_assigned=class_obj
                ).select_related('exam')
                
                for assignment in assignments:
                    exam = assignment.exam  # This is a RoutineExam instance
                    exam_type = getattr(exam, 'exam_type', 'monthly_review')
                    type_display = 'Review' if exam_type == 'monthly_review' else 'Quarterly'
                    
                    exams.append({
                        'id': str(exam.id),
                        'name': exam.name,
                        'type': type_display,
                        'duration': 60,  # Default duration for RoutineExam
                        'question_count': len(exam.get_questions()) if hasattr(exam, 'get_questions') else 0,
                        'created_date': exam.created_at.strftime('%Y-%m-%d') if hasattr(exam, 'created_at') else '',
                        'status': 'Active',  # RoutineExam.is_active field
                        'source': 'ExamAssignment'
                    })
        except Exception as e:
            logger.warning(f"Error getting ExamAssignment data: {e}")
        
        # Second, get exams from ExamScheduleMatrix (new system for copied exams)
        try:
            # CRITICAL FIX: Handle 'overview' timeslot to show ALL exams for class
            if timeslot and timeslot.lower() != 'overview':
                # Find exams in the matrix for this class and specific timeslot
                logger.info(f"[EXAM_API_FIX] Filtering by specific timeslot: {timeslot} for class {class_code}")
                matrix_entries = ExamScheduleMatrix.objects.filter(
                    class_code=class_code,
                    time_period_value=timeslot
                ).prefetch_related('exams')
            else:
                # For 'overview' or no timeslot, get ALL exams for this class
                logger.info(f"[EXAM_API_FIX] Getting ALL exams for class {class_code} (overview mode)")
                matrix_entries = ExamScheduleMatrix.objects.filter(
                    class_code=class_code
                ).prefetch_related('exams')
                
                for matrix_entry in matrix_entries:
                    for exam in matrix_entry.exams.all():
                        # Check if this exam is already in the list from ExamAssignment
                        existing_exam_ids = [e['id'] for e in exams]
                        if str(exam.id) not in existing_exam_ids:
                            # Handle both RoutineExam and legacy Exam
                            exam_type = getattr(exam, 'exam_type', None)
                            if exam_type:
                                # This is a RoutineExam
                                type_display = 'Review' if exam_type == 'monthly_review' else 'Quarterly'
                                duration = 60
                                question_count = len(exam.get_questions()) if hasattr(exam, 'get_questions') else 0
                            else:
                                # This is a legacy Exam (placement test)
                                type_display = 'Review' if 'review' in exam.name.lower() else 'Quarterly'
                                duration = getattr(exam, 'timer_minutes', 60)
                                question_count = exam.questions.count() if hasattr(exam, 'questions') else 0
                            
                            exams.append({
                                'id': str(exam.id),
                                'name': exam.name,
                                'type': type_display,
                                'duration': duration,
                                'question_count': question_count,
                                'created_date': exam.created_at.strftime('%Y-%m-%d') if hasattr(exam, 'created_at') else '',
                                'status': matrix_entry.status or 'Active',
                                'source': 'ExamScheduleMatrix'
                            })
        except Exception as e:
            logger.warning(f"Error getting ExamScheduleMatrix data: {e}")
        
        # Log the fix for debugging
        filter_mode = "ALL exams (overview)" if not timeslot or timeslot.lower() == 'overview' else f"filtered by {timeslot}"
        logger.info(f"[EXAM_API_FIX] Retrieved {len(exams)} exams for class {class_code}, mode: {filter_mode}")
        
        return JsonResponse({
            'exams': exams,
            'filter_mode': filter_mode,
            'class_code': class_code,
            'timeslot': timeslot,
            'total_found': len(exams)
        })
        
    except Exception as e:
        logger.error(f"Error getting class exams for {class_code}: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Error loading exam data: {str(e)}',
            'class_code': class_code,
            'timeslot': timeslot
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_class_students(request, class_code):
    """Get students enrolled in a class"""
    try:
        # First check if the class exists in TeacherClassAssignment
        assignment = TeacherClassAssignment.objects.filter(
            class_code=class_code, 
            is_active=True
        ).first()
        
        if not assignment:
            logger.warning(f"No active teacher assignment found for class {class_code}")
            # Return empty but valid response instead of 404
            return JsonResponse({
                'students': [],
                'total': 0,
                'active': 0,
                'class_code': class_code,
                'warning': 'No active teacher assignment found for this class'
            })
        
        # Get students for this class through enrollments
        students_data = []
        from primepath_routinetest.models import StudentEnrollment
        
        # Try to get enrollments by class object if it exists
        class_obj = Class.objects.filter(name=class_code).first()
        if class_obj:
            enrollments = StudentEnrollment.objects.filter(
                class_assigned=class_obj,
                status='active'
            ).select_related('student')
            
            for enrollment in enrollments:
                student = enrollment.student
                # Get last activity from sessions
                last_session = StudentSession.objects.filter(
                    student_name=student.name
                ).order_by('-created_at').first()
                
                students_data.append({
                    'id': str(student.id),
                    'name': student.name,
                    'email': student.parent_email or '',  # Students have parent_email, not email
                    'status': 'Active' if enrollment.status == 'active' else 'Inactive',
                    'last_activity': last_session.created_at.strftime('%Y-%m-%d %H:%M') if last_session else 'Never'
                })
        else:
            # If no Class object exists, we can't find enrollments
            # But we can still return valid response for the assignment that exists
            logger.info(f"Class object not found for {class_code}, but teacher assignment exists")
        
        return JsonResponse({
            'students': students_data,
            'total': len(students_data),
            'active': sum(1 for s in students_data if s['status'] == 'Active'),
            'class_code': class_code,
            'teacher': assignment.teacher.name if assignment and assignment.teacher else None
        })
        
    except Exception as e:
        logger.error(f"Error getting class students for {class_code}: {e}", exc_info=True)
        return JsonResponse({
            'students': [],
            'total': 0,
            'active': 0,
            'class_code': class_code,
            'error': f'Error loading student data: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_all_classes(request):
    """Get all classes for exam copying"""
    try:
        from primepath_routinetest.models import TeacherClassAssignment
        
        classes = []
        # Get all unique class codes from the choices defined in the model
        class_choices = TeacherClassAssignment._meta.get_field('class_code').choices
        
        # Only include classes that have active assignments (i.e., actually exist)
        active_class_codes = TeacherClassAssignment.objects.filter(
            is_active=True
        ).values_list('class_code', flat=True).distinct()
        
        for code, display_name in class_choices:
            if code in active_class_codes:
                classes.append({
                    'code': code,  # e.g., "CLASS_2B"
                    'name': display_name  # e.g., "Class 2B"
                })
        
        # Sort by class code for better organization
        classes.sort(key=lambda x: x['code'])
        
        return JsonResponse({'classes': classes})
        
    except Exception as e:
        logger.error(f"Error getting all classes: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_class_all_exams(request, class_code):
    """Get all exams from a class (for copying)"""
    try:
        exams = []
        # class_code here is actually the class ID (UUID)
        # Get exams associated with this class through ExamScheduleMatrix
        from primepath_routinetest.models import ExamScheduleMatrix
        
        # Get all matrix entries for this class
        matrix_entries = ExamScheduleMatrix.objects.filter(
            class_code=class_code  # This might need to be adjusted based on actual field
        ).prefetch_related('exams')
        
        # Collect all unique exams
        exam_set = set()
        for matrix in matrix_entries:
            for exam in matrix.exams.all():
                exam_set.add(exam)
        
        # Convert to list format
        for exam in exam_set:
            exams.append({
                'id': str(exam.id),
                'name': exam.name,
                'type': exam.exam_type if hasattr(exam, 'exam_type') else 'REVIEW',
                'question_count': exam.routine_questions.count() if hasattr(exam, 'routine_questions') else 0
            })
        
        return JsonResponse({'exams': exams})
        
    except Exception as e:
        logger.error(f"Error getting exams for copying: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_target_class_existing_exams(request, class_code):
    """Get exams already assigned to target class for copy conflict detection"""
    try:
        timeslot = request.GET.get('timeslot', '')
        
        existing_exams = []
        
        # Get exams from ExamScheduleMatrix for this class and timeslot
        try:
            from primepath_routinetest.models import ExamScheduleMatrix
            
            matrix_entries = ExamScheduleMatrix.objects.filter(
                class_code=class_code,
                time_period_value=timeslot
            ).prefetch_related('exams')
            
            for matrix in matrix_entries:
                for exam in matrix.exams.all():
                    existing_exams.append({
                        'id': str(exam.id),
                        'name': exam.name,
                        'exam_type': getattr(exam, 'exam_type', 'UNKNOWN'),
                        'time_period': timeslot
                    })
            
            logger.info(f"Found {len(existing_exams)} existing exams for {class_code} in {timeslot}")
            
        except Exception as e:
            logger.warning(f"Error getting existing exams: {e}")
        
        return JsonResponse({
            'existing_exams': existing_exams,
            'class_code': class_code,
            'timeslot': timeslot,
            'count': len(existing_exams)
        })
        
    except Exception as e:
        logger.error(f"Error getting existing exams for {class_code}: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_class_filtered_exams(request, class_code):
    """Get filtered exams from a class based on exam type and time period"""
    try:
        exam_type = request.GET.get('exam_type', '')
        time_period = request.GET.get('time_period', '')
        
        logger.info(f"Filtering exams for class {class_code}, type: {exam_type}, period: {time_period}")
        
        # Validate input parameters
        if not exam_type:
            logger.warning(f"No exam type provided for class {class_code}")
            return JsonResponse({
                'exams': [],
                'message': 'Please select an exam type',
                'filters_applied': {
                    'class_code': class_code,
                    'exam_type': exam_type,
                    'time_period': time_period,
                    'total_found': 0
                }
            })
        
        if not time_period:
            logger.warning(f"No time period provided for class {class_code}")
            return JsonResponse({
                'exams': [],
                'message': 'Please select a time period',
                'filters_applied': {
                    'class_code': class_code,
                    'exam_type': exam_type,
                    'time_period': time_period,
                    'total_found': 0
                }
            })
        
        # Verify class exists
        from primepath_routinetest.models import TeacherClassAssignment
        class_exists = TeacherClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).exists()
        
        if not class_exists:
            logger.warning(f"Class {class_code} not found or not active")
            return JsonResponse({
                'exams': [],
                'message': f'Class {class_code} not found in the system',
                'filters_applied': {
                    'class_code': class_code,
                    'exam_type': exam_type,
                    'time_period': time_period,
                    'total_found': 0
                }
            })
        
        exams = []
        
        # Use RoutineExam for routine test management (already imported at top)
        
        # Build filter conditions with defensive programming
        filter_conditions = {
            'is_active': True
        }
        
        # Add exam type filter - handle both new and legacy formats
        if exam_type:
            # Handle legacy exam types
            if exam_type == 'REVIEW':
                filter_conditions['exam_type__in'] = ['REVIEW', 'monthly_review']
            elif exam_type == 'QUARTERLY':
                filter_conditions['exam_type__in'] = ['QUARTERLY', 'quarterly']
            else:
                filter_conditions['exam_type'] = exam_type
        
        # Add time period filter based on exam type
        # Use Django Q objects to combine OR conditions instead of union() to avoid SQLite issues
        from django.db.models import Q
        
        if time_period:
            if exam_type == 'REVIEW':
                # Try both new and legacy fields for backward compatibility
                time_period_q = Q(time_period_month=time_period) | Q(quarter=time_period)
                filter_conditions_combined = {**filter_conditions}
                filtered_exams = RoutineExam.objects.filter(Q(**filter_conditions_combined) & time_period_q)
                
            elif exam_type == 'QUARTERLY':
                # Try both new and legacy fields for backward compatibility
                time_period_q = Q(time_period_quarter=time_period) | Q(quarter=time_period)
                filter_conditions_combined = {**filter_conditions}
                filtered_exams = RoutineExam.objects.filter(Q(**filter_conditions_combined) & time_period_q)
            else:
                filtered_exams = RoutineExam.objects.filter(**filter_conditions)
        else:
            filtered_exams = RoutineExam.objects.filter(**filter_conditions)
        
        logger.info(f"Initial filter found {filtered_exams.count()} exams before class association check")
        
        # Additional filtering: check if exams are associated with the source class
        # This ensures we only show exams that actually exist for the source class
        available_exam_ids = set()
        
        # Get exams through ExamScheduleMatrix or ExamAssignment
        try:
            from primepath_routinetest.models import ExamScheduleMatrix, ExamAssignment
            
            # Try ExamScheduleMatrix first
            matrix_entries = ExamScheduleMatrix.objects.filter(
                class_code=class_code
            ).prefetch_related('exams')
            
            for matrix in matrix_entries:
                for exam in matrix.exams.all():
                    available_exam_ids.add(exam.id)
            
            logger.info(f"Found {len(available_exam_ids)} exams in ExamScheduleMatrix for {class_code}")
            
            # Also try ExamAssignment
            class_obj = Class.objects.filter(name=class_code).first()
            if class_obj:
                assignments = ExamAssignment.objects.filter(
                    class_assigned=class_obj
                ).select_related('exam')
            
                for assignment in assignments:
                    available_exam_ids.add(assignment.exam.id)
                    
                logger.info(f"Added {assignments.count()} exams from ExamAssignment for {class_code}")
                
        except Exception as matrix_error:
            logger.warning(f"Error accessing exam associations: {matrix_error}")
            # If we can't determine class associations, show all filtered exams
            available_exam_ids = set(exam.id for exam in filtered_exams)
            logger.info(f"Using all filtered exams as fallback: {len(available_exam_ids)} exams")
        
        # Filter exams to only those available for the source class
        if available_exam_ids:
            final_exams = filtered_exams.filter(id__in=available_exam_ids)
        else:
            # If no class associations found, still show filtered exams for testing
            final_exams = filtered_exams
            logger.warning(f"No class associations found for {class_code}, showing all filtered exams")
        
        # Convert to list format
        for exam in final_exams:
            # Get time period display with fallback
            time_period_display = exam.get_time_period_display()
            
            # Get question count with multiple fallback methods
            question_count = 0
            if hasattr(exam, 'routine_questions'):
                question_count = exam.routine_questions.count()
            elif hasattr(exam, 'get_questions'):
                question_count = len(exam.get_questions())
            elif hasattr(exam, 'answer_key') and exam.answer_key:
                question_count = len(exam.answer_key)
            
            exams.append({
                'id': str(exam.id),
                'name': exam.name,
                'exam_type': exam.exam_type,
                'time_period': time_period_display,
                'question_count': question_count,
                'curriculum': getattr(exam, 'curriculum_level', 'Not specified')
            })
        
        # Determine appropriate message based on results
        message = None
        if len(exams) == 0:
            if exam_type == 'REVIEW':
                message = f'No Review exams found for {time_period}'
            elif exam_type == 'QUARTERLY':
                message = f'No Quarterly exams found for {time_period}'
            else:
                message = f'No {exam_type} exams found for {time_period}'
            
            # Provide helpful context - safely get count to avoid SQLite issues
            try:
                total_filtered = filtered_exams.count()
                if total_filtered > 0:
                    message += f' in class {class_code} (found {total_filtered} exams system-wide but none assigned to this class)'
                else:
                    message += f' in the system'
            except Exception as count_error:
                logger.warning(f"Could not get filtered exam count: {count_error}")
                message += f' in class {class_code}'
        
        logger.info(f"Final result: {len(exams)} exams matching filters for class {class_code}")
        
        # Safely get system-wide count
        total_system_wide = 0
        try:
            if 'filtered_exams' in locals():
                total_system_wide = filtered_exams.count()
        except Exception as count_error:
            logger.warning(f"Could not get system-wide count: {count_error}")
            total_system_wide = 0
        
        return JsonResponse({
            'exams': exams,
            'message': message,
            'filters_applied': {
                'class_code': class_code,
                'exam_type': exam_type,
                'time_period': time_period,
                'total_found': len(exams),
                'total_system_wide': total_system_wide
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting filtered exams for class {class_code}: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Unable to load exams. Error: {str(e)}',
            'exams': [],
            'filters_applied': {
                'class_code': class_code,
                'exam_type': exam_type,
                'time_period': time_period,
                'total_found': 0
            }
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def copy_exam(request):
    """Copy an exam from one class to another with proper naming convention"""
    try:
        from primepath_routinetest.models import ExamScheduleMatrix, Exam
        from datetime import datetime
        from django.utils import timezone
        import uuid
        
        data = json.loads(request.body)
        source_exam_id = data.get('source_exam_id')
        target_class_code = data.get('target_class')  # This is the class code string
        target_timeslot = data.get('target_timeslot')
        academic_year = data.get('academic_year')  # NEW: Year selection
        custom_suffix = data.get('custom_suffix', '').strip()  # NEW: Custom naming suffix
        
        # Enhanced console logging
        logger.info(f"[COPY_EXAM_REQUEST] exam={source_exam_id}, class={target_class_code}, timeslot={target_timeslot}, year={academic_year}, suffix={custom_suffix}")
        
        # Get source exam - Use RoutineExam model for compatibility with ExamScheduleMatrix
        from primepath_routinetest.models.exam_management import RoutineExam
        source_exam = RoutineExam.objects.filter(id=source_exam_id).first()
        if not source_exam:
            logger.error(f"[COPY_EXAM_ERROR] Source exam not found in RoutineExam model: {source_exam_id}")
            # Try Exam as fallback (from primepath_routinetest.models)
            source_exam_alt = Exam.objects.filter(id=source_exam_id).first()
            if source_exam_alt:
                logger.info(f"[COPY_EXAM_FALLBACK] Found in Exam model instead")
                # Use Exam data
                source_exam = source_exam_alt
            else:
                return JsonResponse({'error': f'Source exam not found: {source_exam_id}'}, status=404)
        
        # Determine exam type and period from target_timeslot
        exam_type = 'REVIEW'  # Default
        time_period = target_timeslot
        
        # Check if it's a quarter (Q1, Q2, Q3, Q4)
        if target_timeslot and target_timeslot.startswith('Q'):
            exam_type = 'QUARTERLY'
        
        # Use provided year or default to current year
        if not academic_year:
            academic_year = str(datetime.now().year)
        
        # Generate the new exam name based on the same convention as Upload Exam
        new_exam_name = generate_exam_name(
            exam_type=exam_type,
            time_period=target_timeslot,
            academic_year=academic_year,
            source_exam=source_exam,
            custom_suffix=custom_suffix
        )
        
        logger.info(f"[COPY_EXAM_NAME_GENERATED] Generated name: {new_exam_name}")
        
        # Create a copy of the exam with the new name
        try:
            # Use the user directly for RoutineExam.created_by field
            created_by = request.user if request.user.is_authenticated else None
            
            # Create the copied exam
            copied_exam = create_copied_exam(
                source_exam=source_exam,
                new_name=new_exam_name,
                target_class_code=target_class_code,
                exam_type=exam_type,
                time_period=target_timeslot,
                academic_year=academic_year,
                created_by=created_by
            )
            
            logger.info(f"[COPY_EXAM_SUCCESS] Created exam copy: {copied_exam.id} - {copied_exam.name}")
        except Exception as e:
            logger.error(f"[COPY_EXAM_ERROR] Failed to create exam copy: {str(e)}")
            return JsonResponse({'error': f'Failed to create exam copy: {str(e)}'}, status=500)
        
        # Check if exam already exists in the matrix for this class and period
        existing_matrix = ExamScheduleMatrix.objects.filter(
            class_code=target_class_code,
            time_period_value=target_timeslot,
            exams=copied_exam
        ).exists()
        
        if existing_matrix:
            # This shouldn't happen with a new copy, but check anyway
            logger.warning(f"[COPY_EXAM_WARNING] Exam already in matrix: {copied_exam.name}")
        
        # Get or create the matrix entry for this class and time period
        current_year = academic_year or str(datetime.now().year)
        
        # Try to get the Teacher instance for the current user
        created_by_teacher = None
        if request.user.is_authenticated:
            try:
                from core.models import Teacher
                created_by_teacher = Teacher.objects.filter(user=request.user).first()
            except Exception:
                pass
        
        matrix_entry, created = ExamScheduleMatrix.objects.get_or_create(
            class_code=target_class_code,
            academic_year=current_year,
            time_period_type='QUARTERLY' if exam_type == 'QUARTERLY' else 'MONTHLY',
            time_period_value=target_timeslot,
            defaults={
                'status': 'PENDING',
                'created_by': created_by_teacher
            }
        )
        
        # Add the copied exam to the matrix entry (not the source exam!)
        matrix_entry.exams.add(copied_exam)
        
        logger.info(f"[COPY_EXAM_MATRIX_SUCCESS] Added exam {copied_exam.name} to matrix for {target_class_code} - {target_timeslot}")
        
        return JsonResponse({
            'success': True,
            'matrix_id': str(matrix_entry.id),
            'exam_id': str(copied_exam.id),
            'exam_name': copied_exam.name,
            'original_name': source_exam.name,
            'class_code': target_class_code,
            'timeslot': target_timeslot,
            'academic_year': academic_year,
            'custom_suffix': custom_suffix,
            'message': f'Exam "{copied_exam.name}" successfully created and assigned to {target_class_code} for {target_timeslot}'
        })
        
    except Exception as e:
        logger.error(f"Error copying exam: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_exam(request, exam_id):
    """Delete an exam assignment from both ExamAssignment and ExamScheduleMatrix"""
    try:
        from primepath_routinetest.models import ExamScheduleMatrix
        
        class_code = request.GET.get('class_code')
        timeslot = request.GET.get('timeslot')
        
        removed_from_assignment = False
        removed_from_matrix = False
        
        if class_code and timeslot:
            # Try to remove from ExamAssignment (legacy system)
            try:
                class_obj = Class.objects.filter(name=class_code).first()
                if class_obj:
                    deleted_assignments = ExamAssignment.objects.filter(
                        exam_id=exam_id,
                        class_assigned=class_obj
                    ).delete()
                    if deleted_assignments[0] > 0:
                        removed_from_assignment = True
                        logger.info(f"Removed exam {exam_id} from ExamAssignment for class {class_code}")
            except Exception as e:
                logger.warning(f"Error removing from ExamAssignment: {e}")
            
            # Try to remove from ExamScheduleMatrix (new system for copied exams)
            try:
                matrix_entries = ExamScheduleMatrix.objects.filter(
                    class_code=class_code,
                    time_period_value=timeslot,
                    exams=exam_id
                )
                for matrix_entry in matrix_entries:
                    matrix_entry.exams.remove(exam_id)
                    removed_from_matrix = True
                    logger.info(f"Removed exam {exam_id} from ExamScheduleMatrix for class {class_code}, timeslot {timeslot}")
            except Exception as e:
                logger.warning(f"Error removing from ExamScheduleMatrix: {e}")
        
        if removed_from_assignment or removed_from_matrix:
            message = f"Exam removed from class {class_code}"
            if removed_from_assignment and removed_from_matrix:
                message += " (from both assignment and schedule matrix)"
            elif removed_from_assignment:
                message += " (from assignment)"
            elif removed_from_matrix:
                message += " (from schedule matrix)"
            
            return JsonResponse({'success': True, 'message': message})
        else:
            return JsonResponse({'success': False, 'message': 'Exam not found in this class/timeslot'})
        
    except Exception as e:
        logger.error(f"Error deleting exam: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["PATCH"])
def update_exam_duration(request, exam_id):
    """Update exam duration"""
    try:
        data = json.loads(request.body)
        duration = data.get('duration', 60)
        
        # Get exam from RoutineExam only
        exam = get_object_or_404(RoutineExam, id=exam_id)
        
        # Update the timer_minutes field which stores the exam duration
        exam.timer_minutes = duration
        exam.save()
        
        return JsonResponse({'success': True, 'message': 'Duration updated'})
        
    except Exception as e:
        logger.error(f"Error updating duration: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def schedule_exam(request):
    """Schedule an exam with date and time"""
    try:
        data = json.loads(request.body)
        exam_id = data.get('exam_id')
        date = data.get('date')
        time = data.get('time')
        duration = data.get('duration', 60)
        
        # This would typically update the ExamAssignment with schedule info
        # For now, we'll store it in the assignment metadata
        
        assignment = ExamAssignment.objects.filter(exam_id=exam_id).first()
        if assignment:
            if not hasattr(assignment, 'metadata'):
                assignment.metadata = {}
            
            assignment.metadata.update({
                'scheduled_date': date,
                'scheduled_time': time,
                'duration': duration
            })
            assignment.save()
        
        return JsonResponse({'success': True, 'message': 'Exam scheduled successfully'})
        
    except Exception as e:
        logger.error(f"Error scheduling exam: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================================
# HELPER FUNCTIONS FOR COPY EXAM
# ============================================================================

def generate_exam_name(exam_type, time_period, academic_year, source_exam, custom_suffix=''):
    """
    Generate exam name following the same convention as Upload Exam
    Format: [RT/QTR] - [Mon Year] - [Program] [SubProgram] Lv[X]_[custom]
    """
    from primepath_routinetest.models import RoutineExam as Exam
    
    name_parts = []
    
    # Add exam type prefix
    prefix = '[QTR]' if exam_type == 'QUARTERLY' else '[RT]'
    name_parts.append(prefix)
    
    # Add time period with year
    if exam_type == 'REVIEW':
        # Convert month code to abbreviated name
        month_abbrev = {
            'JAN': 'Jan', 'FEB': 'Feb', 'MAR': 'Mar', 'APR': 'Apr',
            'MAY': 'May', 'JUN': 'Jun', 'JUL': 'Jul', 'AUG': 'Aug',
            'SEP': 'Sep', 'OCT': 'Oct', 'NOV': 'Nov', 'DEC': 'Dec'
        }
        month_name = month_abbrev.get(time_period, time_period)
        period_str = f"{month_name} {academic_year}"
    else:  # QUARTERLY
        period_str = f"{time_period} {academic_year}"
    
    name_parts.append(period_str)
    
    # Extract curriculum info from source exam
    curriculum_str = ""
    if hasattr(source_exam, 'curriculum_level') and source_exam.curriculum_level:
        curriculum = source_exam.curriculum_level
        if hasattr(curriculum, 'subprogram') and curriculum.subprogram:
            program_name = curriculum.subprogram.program.name
            subprogram_name = curriculum.subprogram.name
            level_number = curriculum.level_number
            curriculum_str = f"{program_name} {subprogram_name} Lv{level_number}"
    else:
        # Try to extract from the source exam name if no curriculum level
        import re
        pattern = r'(CORE|ASCENT|EDGE|PINNACLE)\s+(\w+)\s+Lv(\d+)'
        match = re.search(pattern, source_exam.name)
        if match:
            curriculum_str = f"{match.group(1)} {match.group(2)} Lv{match.group(3)}"
        else:
            # Fallback to generic
            curriculum_str = "General Exam"
    
    if curriculum_str:
        name_parts.append(curriculum_str)
    
    # Join with separator
    base_name = ' - '.join(name_parts)
    
    # Add custom suffix if provided
    if custom_suffix:
        # Add underscore separator if suffix doesn't start with one
        if not custom_suffix.startswith('_'):
            custom_suffix = '_' + custom_suffix
        base_name += custom_suffix
    
    logger.info(f"[GENERATE_EXAM_NAME] Generated: {base_name}")
    
    return base_name


def create_copied_exam(source_exam, new_name, target_class_code, exam_type, time_period, academic_year, created_by=None):
    """
    Create a copy of an exam with a new name and metadata
    UPDATED: Creates a new exam instance for ONE-TO-ONE relationship
    """
    from primepath_routinetest.models import RoutineExam, Question, AudioFile, Exam
    from django.db import transaction
    import uuid
    
    logger.info(f"[ONE_TO_ONE_FIX] Creating new exam copy for class {target_class_code}")
    
    with transaction.atomic():
        # Create the new exam as RoutineExam (compatible with ExamScheduleMatrix)
        # Extract curriculum level as string
        curriculum_level_str = ""
        if hasattr(source_exam, 'curriculum_level'):
            curriculum = source_exam.curriculum_level
            if curriculum and hasattr(curriculum, 'subprogram'):
                # Convert curriculum object to string format
                program_name = curriculum.subprogram.program.name
                subprogram_name = curriculum.subprogram.name
                level_number = curriculum.level_number
                curriculum_level_str = f"{program_name} {subprogram_name} Level {level_number}"
            elif isinstance(curriculum, str):
                curriculum_level_str = curriculum
        
        copied_exam = RoutineExam.objects.create(
            id=uuid.uuid4(),
            name=new_name,
            exam_type=exam_type,
            time_period_month=time_period if exam_type == 'REVIEW' else None,
            time_period_quarter=time_period if exam_type == 'QUARTERLY' else None,
            quarter=time_period if exam_type == 'QUARTERLY' else None,  # backward compatibility
            academic_year=academic_year,
            curriculum_level=curriculum_level_str,
            pdf_file=source_exam.pdf_file if hasattr(source_exam, 'pdf_file') else None,
            timer_minutes=source_exam.timer_minutes if hasattr(source_exam, 'timer_minutes') else 60,  # Inherit timer_minutes
            total_questions=source_exam.total_questions if hasattr(source_exam, 'total_questions') else 0,  # Inherit total_questions
            default_options_count=source_exam.default_options_count if hasattr(source_exam, 'default_options_count') else 5,  # Inherit default_options_count
            passing_score=source_exam.passing_score if hasattr(source_exam, 'passing_score') else None,  # Inherit passing_score
            pdf_rotation=source_exam.pdf_rotation if hasattr(source_exam, 'pdf_rotation') else 0,  # Inherit pdf_rotation
            instructions=source_exam.instructions if hasattr(source_exam, 'instructions') else '',  # Inherit instructions
            answer_key=source_exam.answer_key if hasattr(source_exam, 'answer_key') else {},
            created_by=created_by,
            is_active=True
        )
        
        # CRITICAL ONE-TO-ONE FIX: Check if we should use Exam model instead
        # If source exam is an Exam instance, create an Exam copy
        if hasattr(source_exam, 'class_code') or hasattr(source_exam, 'class_codes'):
            logger.info(f"[ONE_TO_ONE_FIX] Source is Exam model, creating Exam copy with single class")
            # Create Exam instance instead of RoutineExam
            from primepath_routinetest.models import RoutineExam as Exam
            
            copied_exam = Exam.objects.create(
                id=uuid.uuid4(),
                name=new_name,
                exam_type=exam_type,
                time_period_month=time_period if exam_type == 'REVIEW' else None,
                time_period_quarter=time_period if exam_type == 'QUARTERLY' else None,
                academic_year=academic_year,
                curriculum_level_id=source_exam.curriculum_level_id if hasattr(source_exam, 'curriculum_level_id') else None,
                class_code=target_class_code,  # SINGLE CLASS - ONE-TO-ONE
                class_codes=[target_class_code],  # Keep for backward compatibility temporarily
                pdf_file=source_exam.pdf_file if hasattr(source_exam, 'pdf_file') else None,
                timer_minutes=source_exam.timer_minutes if hasattr(source_exam, 'timer_minutes') else 60,
                total_questions=source_exam.total_questions if hasattr(source_exam, 'total_questions') else 0,
                default_options_count=source_exam.default_options_count if hasattr(source_exam, 'default_options_count') else 5,
                passing_score=source_exam.passing_score if hasattr(source_exam, 'passing_score') else None,
                pdf_rotation=source_exam.pdf_rotation if hasattr(source_exam, 'pdf_rotation') else 0,
                instructions=source_exam.instructions if hasattr(source_exam, 'instructions') else '',
                answer_key=source_exam.answer_key if hasattr(source_exam, 'answer_key') else {},
                created_by=created_by,
                owner=created_by,  # Set owner for permission system
                is_active=True
            )
            
            # Copy questions if they exist
            try:
                for question in source_exam.routine_questions.all():
                    Question.objects.create(
                        exam=copied_exam,
                        question_number=question.question_number,
                        question_type=question.question_type,
                        question_text=question.question_text if hasattr(question, 'question_text') else '',
                        points=question.points,
                        correct_answer=question.correct_answer if hasattr(question, 'correct_answer') else '',
                        options_count=question.options_count if hasattr(question, 'options_count') else 5
                    )
                logger.info(f"[ONE_TO_ONE_FIX] Copied {source_exam.routine_questions.count()} questions")
            except Exception as e:
                logger.warning(f"[ONE_TO_ONE_FIX] Could not copy questions: {e}")
            
            logger.info(f"[ONE_TO_ONE_FIX] Successfully created Exam copy {copied_exam.id} for class {target_class_code}")
            return copied_exam
        
        # Otherwise continue with RoutineExam creation
        logger.info(f"[ONE_TO_ONE_FIX] Creating RoutineExam copy (no class_code field)")
        # Note: RoutineExam doesn't have class_code field - classes are managed through ExamScheduleMatrix
        
        # Note: Skipping questions and audio files for RoutineExam copy
        # because Question and AudioFile models expect primepath_routinetest.Exam, not RoutineExam
        # The copied exam will need questions to be added separately through the exam editor
        
        logger.info(f"[CREATE_COPIED_EXAM] Successfully created exam copy: {copied_exam.id} - {copied_exam.name}")
        
        return copied_exam
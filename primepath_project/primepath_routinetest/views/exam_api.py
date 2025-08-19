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

from ..models import ExamAssignment, TeacherClassAssignment, Class, StudentEnrollment
from ..models.exam_management import RoutineExam  # Use RoutineExam for exam management
from ..models.exam import Exam  # Legacy placement test exams
from core.models import Student, Teacher
from placement_test.models import StudentSession

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def get_class_overview(request, class_code):
    """Get overview data for a class and timeslot"""
    timeslot = request.GET.get('timeslot', '')
    
    try:
        # Get class information - class_code is actually class name
        class_obj = Class.objects.filter(name=class_code).first()
        if not class_obj:
            return JsonResponse({'error': 'Class not found'}, status=404)
        
        # Get curriculum mapping
        from ..views.schedule_matrix_optimized import get_class_curriculum_mapping_cached
        curriculum = get_class_curriculum_mapping_cached(class_code, request.GET.get('year', 2024))
        
        # Get exams for this timeslot
        exams = []
        # ExamAssignment uses class_assigned ForeignKey to Class model
        assignments = ExamAssignment.objects.filter(
            class_assigned=class_obj
        ).select_related('exam')
        
        for assignment in assignments:
            exam = assignment.exam  # This is a RoutineExam instance
            # RoutineExam has different field names than legacy Exam
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
        
        return JsonResponse({
            'class_code': class_code,
            'class_name': class_obj.name if class_obj else class_code,
            'curriculum': curriculum,
            'timeslot': timeslot,
            'exams': exams
        })
        
    except Exception as e:
        logger.error(f"Error getting class overview for {class_code}: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Error loading overview data: {str(e)}',
            'class_code': class_code,
            'timeslot': timeslot
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
            if timeslot:
                # Find exams in the matrix for this class and timeslot
                matrix_entries = ExamScheduleMatrix.objects.filter(
                    class_code=class_code,
                    time_period_value=timeslot
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
        
        logger.info(f"Retrieved {len(exams)} exams for class {class_code}, timeslot {timeslot}")
        return JsonResponse({'exams': exams})
        
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
        # Get students for this class through enrollments
        students_data = []
        from primepath_routinetest.models import StudentEnrollment
        enrollments = StudentEnrollment.objects.filter(
            class_assigned__name=class_code,
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
        
        return JsonResponse({
            'students': students_data,
            'total': len(students_data),
            'active': sum(1 for s in students_data if s['status'] == 'Active')
        })
        
    except Exception as e:
        logger.error(f"Error getting class students for {class_code}: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Error loading student data: {str(e)}',
            'class_code': class_code,
            'student_count': 0
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
def get_class_filtered_exams(request, class_code):
    """Get filtered exams from a class based on exam type and time period"""
    try:
        exam_type = request.GET.get('exam_type', '')
        time_period = request.GET.get('time_period', '')
        
        logger.info(f"Filtering exams for class {class_code}, type: {exam_type}, period: {time_period}")
        
        exams = []
        
        # Import the RoutineExam model for routine test management
        from primepath_routinetest.models import RoutineExam as Exam
        
        # Build filter conditions
        filter_conditions = {
            'is_active': True
        }
        
        # Add exam type filter
        if exam_type:
            filter_conditions['exam_type'] = exam_type
        
        # Add time period filter based on exam type
        if time_period:
            if exam_type == 'REVIEW':
                filter_conditions['time_period_month'] = time_period
            elif exam_type == 'QUARTERLY':
                filter_conditions['time_period_quarter'] = time_period
        
        # Query exams with filters
        filtered_exams = Exam.objects.filter(**filter_conditions)
        
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
            
            # Also try ExamAssignment
            class_obj = Class.objects.filter(name=class_code).first()
            if class_obj:
                assignments = ExamAssignment.objects.filter(
                    class_assigned=class_obj
                ).select_related('exam')
            
                for assignment in assignments:
                    available_exam_ids.add(assignment.exam.id)
                
        except Exception as matrix_error:
            logger.warning(f"Error accessing exam associations: {matrix_error}")
            # If we can't determine class associations, show all filtered exams
            available_exam_ids = set(exam.id for exam in filtered_exams)
        
        # Filter exams to only those available for the source class
        final_exams = filtered_exams.filter(id__in=available_exam_ids)
        
        # Convert to list format
        for exam in final_exams:
            # Get time period display
            time_period_display = exam.get_time_period_display()
            
            exams.append({
                'id': str(exam.id),
                'name': exam.name,
                'exam_type': exam.exam_type,
                'time_period': time_period_display,
                'question_count': exam.routine_questions.count() if hasattr(exam, 'routine_questions') else 0,
                'curriculum': exam.curriculum_level.full_name if exam.curriculum_level else ''
            })
        
        logger.info(f"Found {len(exams)} exams matching filters for class {class_code}")
        
        return JsonResponse({
            'exams': exams,
            'filters_applied': {
                'class_code': class_code,
                'exam_type': exam_type,
                'time_period': time_period,
                'total_found': len(exams)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting filtered exams: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def copy_exam(request):
    """Copy an exam from one class to another"""
    try:
        from primepath_routinetest.models import ExamScheduleMatrix
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        data = json.loads(request.body)
        source_exam_id = data.get('source_exam_id')
        target_class_code = data.get('target_class')  # This is the class code string
        target_timeslot = data.get('target_timeslot')
        
        logger.info(f"Copy exam request: exam={source_exam_id}, class={target_class_code}, timeslot={target_timeslot}")
        
        # Get source exam - try both Exam and RoutineExam models
        source_exam = RoutineExam.objects.filter(id=source_exam_id).first()
        if not source_exam:
            source_exam = Exam.objects.filter(id=source_exam_id).first()
        if not source_exam:
            logger.error(f"Source exam not found: {source_exam_id}")
            return JsonResponse({'error': f'Source exam not found: {source_exam_id}'}, status=404)
        
        # Determine exam type and period from target_timeslot
        exam_type = 'REVIEW'  # Default
        time_period = target_timeslot
        
        # Check if it's a quarter (Q1, Q2, Q3, Q4)
        if target_timeslot and target_timeslot.startswith('Q'):
            exam_type = 'QUARTERLY'
        
        # Check if exam already exists in the matrix for this class and period
        existing_matrix = ExamScheduleMatrix.objects.filter(
            class_code=target_class_code,
            time_period_value=target_timeslot,
            exams=source_exam
        ).exists()
        
        if existing_matrix:
            return JsonResponse({'error': 'Exam already assigned to this class/period'}, status=400)
        
        # Get or create the matrix entry for this class and time period
        current_year = datetime.now().year
        
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
            academic_year=str(current_year),
            time_period_type='QUARTERLY' if exam_type == 'QUARTERLY' else 'MONTHLY',
            time_period_value=target_timeslot,
            defaults={
                'status': 'PENDING',
                'created_by': created_by_teacher
            }
        )
        
        # Add the exam to the matrix entry
        matrix_entry.exams.add(source_exam)
        
        logger.info(f"Successfully copied exam {source_exam.name} to {target_class_code} for {target_timeslot}")
        
        return JsonResponse({
            'success': True,
            'matrix_id': str(matrix_entry.id),
            'exam_name': source_exam.name,
            'class_code': target_class_code,
            'timeslot': target_timeslot,
            'message': f'Exam "{source_exam.name}" copied to {target_class_code} for {target_timeslot}'
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
        
        # Try to get exam from RoutineExam first, then Exam
        exam = RoutineExam.objects.filter(id=exam_id).first()
        if not exam:
            exam = get_object_or_404(Exam, id=exam_id)
        
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
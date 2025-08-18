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

from ..models import Exam, ExamAssignment, TeacherClassAssignment, Class, StudentEnrollment
from core.models import Student, Teacher
from placement_test.models import StudentSession

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def get_class_overview(request, class_code):
    """Get overview data for a class and timeslot"""
    timeslot = request.GET.get('timeslot', '')
    
    try:
        # Get class information
        class_obj = Class.objects.filter(code=class_code).first()
        if not class_obj:
            return JsonResponse({'error': 'Class not found'}, status=404)
        
        # Get curriculum mapping
        from ..views.schedule_matrix_optimized import get_class_curriculum_mapping_cached
        curriculum = get_class_curriculum_mapping_cached(class_code, request.GET.get('year', 2024))
        
        # Get exams for this timeslot
        exams = []
        assignments = ExamAssignment.objects.filter(
            class_code=class_code,
            timeslot=timeslot
        ).select_related('exam')
        
        for assignment in assignments:
            exams.append({
                'id': str(assignment.exam.id),
                'name': assignment.exam.name,
                'type': 'Review' if 'review' in assignment.exam.name.lower() else 'Quarterly',
                'status': assignment.status or 'Assigned',
                'duration': getattr(assignment.exam, 'duration', 60)
            })
        
        return JsonResponse({
            'class_code': class_code,
            'class_name': class_obj.name if class_obj else class_code,
            'curriculum': curriculum,
            'timeslot': timeslot,
            'exams': exams
        })
        
    except Exception as e:
        logger.error(f"Error getting class overview: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_class_exams(request, class_code):
    """Get all exams for a class and timeslot"""
    timeslot = request.GET.get('timeslot', '')
    
    try:
        exams = []
        assignments = ExamAssignment.objects.filter(
            class_code=class_code,
            timeslot=timeslot
        ).select_related('exam')
        
        for assignment in assignments:
            exam = assignment.exam
            exams.append({
                'id': str(exam.id),
                'name': exam.name,
                'type': 'Review' if 'review' in exam.name.lower() else 'Quarterly',
                'duration': getattr(exam, 'duration', 60),
                'question_count': exam.questions.count() if hasattr(exam, 'questions') else 0,
                'created_date': exam.created_at.strftime('%Y-%m-%d') if hasattr(exam, 'created_at') else '',
                'status': assignment.status or 'Active'
            })
        
        return JsonResponse({'exams': exams})
        
    except Exception as e:
        logger.error(f"Error getting class exams: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_class_students(request, class_code):
    """Get students enrolled in a class"""
    try:
        # Get students for this class
        students_data = []
        students = Student.objects.filter(class_code=class_code)
        
        for student in students:
            # Get last activity from sessions
            last_session = StudentSession.objects.filter(
                student_name=student.name
            ).order_by('-created_at').first()
            
            students_data.append({
                'id': student.id,
                'name': student.name,
                'email': getattr(student, 'email', ''),
                'status': 'Active' if student.is_active else 'Inactive',
                'last_activity': last_session.created_at.strftime('%Y-%m-%d %H:%M') if last_session else 'Never'
            })
        
        return JsonResponse({
            'students': students_data,
            'total': len(students_data),
            'active': sum(1 for s in students_data if s['status'] == 'Active')
        })
        
    except Exception as e:
        logger.error(f"Error getting class students: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_all_classes(request):
    """Get all classes for exam copying"""
    try:
        classes = []
        all_classes = Class.objects.all().order_by('code')
        
        for cls in all_classes:
            classes.append({
                'code': cls.code,
                'name': cls.name
            })
        
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
        all_exams = Exam.objects.filter(
            classexamassignment__class_code=class_code
        ).distinct()
        
        for exam in all_exams:
            exams.append({
                'id': str(exam.id),
                'name': exam.name,
                'type': 'Review' if 'review' in exam.name.lower() else 'Quarterly',
                'question_count': exam.questions.count() if hasattr(exam, 'questions') else 0
            })
        
        return JsonResponse({'exams': exams})
        
    except Exception as e:
        logger.error(f"Error getting exams for copying: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def copy_exam(request):
    """Copy an exam from one class to another"""
    try:
        data = json.loads(request.body)
        source_exam_id = data.get('source_exam_id')
        target_class = data.get('target_class')
        target_timeslot = data.get('target_timeslot')
        
        # Get source exam
        source_exam = get_object_or_404(Exam, id=source_exam_id)
        
        # Check if assignment already exists
        existing = ExamAssignment.objects.filter(
            class_code=target_class,
            timeslot=target_timeslot,
            exam=source_exam
        ).exists()
        
        if existing:
            return JsonResponse({'error': 'Exam already assigned to this class/timeslot'}, status=400)
        
        # Create new assignment
        assignment = ExamAssignment.objects.create(
            class_code=target_class,
            timeslot=target_timeslot,
            exam=source_exam,
            status='Active'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Exam copied successfully',
            'assignment_id': str(assignment.id) if hasattr(assignment, 'id') else None
        })
        
    except Exception as e:
        logger.error(f"Error copying exam: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_exam(request, exam_id):
    """Delete an exam assignment"""
    try:
        # For now, we'll just remove the assignment, not the exam itself
        # This preserves the exam for other classes
        class_code = request.GET.get('class_code')
        timeslot = request.GET.get('timeslot')
        
        if class_code and timeslot:
            ExamAssignment.objects.filter(
                exam_id=exam_id,
                class_code=class_code,
                timeslot=timeslot
            ).delete()
        
        return JsonResponse({'success': True, 'message': 'Exam removed from class'})
        
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
        
        exam = get_object_or_404(Exam, id=exam_id)
        
        # Update duration (assuming there's a duration field)
        if hasattr(exam, 'duration'):
            exam.duration = duration
        else:
            # Store in exam metadata or create field
            if not hasattr(exam, 'metadata'):
                exam.metadata = {}
            exam.metadata['duration'] = duration
        
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
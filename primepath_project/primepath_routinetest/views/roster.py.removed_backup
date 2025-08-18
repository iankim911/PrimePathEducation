"""
Phase 5: Student Roster & Assignment Views
Handles roster management, assignment tracking, and completion monitoring
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib import messages
import json
import logging

from ..models import Exam, StudentRoster
from ..services import ExamService
from common.mixins import AjaxResponseMixin

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def manage_roster(request, exam_id):
    """
    Phase 5: Manage student roster for an exam.
    
    GET: Display roster management page
    POST: Add/update roster entries
    """
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Log access
    console_log = {
        "view": "manage_roster",
        "method": request.method,
        "exam_id": str(exam_id),
        "exam_name": exam.name
    }
    logger.info(f"[PHASE5_ROSTER_VIEW] {json.dumps(console_log)}")
    print(f"[PHASE5_ROSTER_VIEW] {json.dumps(console_log)}")
    
    if request.method == "POST":
        # Handle roster updates
        try:
            roster_data = json.loads(request.body)
            students = roster_data.get('students', [])
            
            # Get teacher from request (if authenticated)
            teacher = getattr(request.user, 'teacher_profile', None) if request.user.is_authenticated else None
            
            # Process roster updates
            results = ExamService.manage_student_roster(exam, students, teacher)
            
            console_log = {
                "view": "manage_roster",
                "action": "roster_updated",
                "exam_id": str(exam_id),
                "created": results['created'],
                "updated": results['updated'],
                "errors": len(results.get('errors', []))
            }
            logger.info(f"[PHASE5_ROSTER_UPDATE] {json.dumps(console_log)}")
            print(f"[PHASE5_ROSTER_UPDATE] {json.dumps(console_log)}")
            
            return JsonResponse({
                'success': True,
                'message': f"Roster updated: {results['created']} added, {results['updated']} updated",
                'results': results
            })
            
        except Exception as e:
            logger.error(f"[PHASE5_ROSTER_ERROR] Error updating roster: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET request - display roster management page
    roster_entries = StudentRoster.objects.filter(exam=exam).select_related('session')
    roster_stats = exam.get_roster_stats()
    
    context = {
        'exam': exam,
        'roster_entries': roster_entries,
        'roster_stats': roster_stats,
        'class_codes': exam.CLASS_CODE_CHOICES,
        'completion_statuses': StudentRoster.COMPLETION_STATUS
    }
    
    return render(request, 'primepath_routinetest/manage_roster.html', context)


@require_http_methods(["POST"])
def import_roster_csv(request, exam_id):
    """
    Phase 5: Import student roster from CSV file.
    """
    exam = get_object_or_404(Exam, id=exam_id)
    
    if 'csv_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'No CSV file provided'
        }, status=400)
    
    csv_file = request.FILES['csv_file']
    
    try:
        # Read CSV content
        csv_content = csv_file.read().decode('utf-8')
        
        # Get teacher from request
        teacher = getattr(request.user, 'teacher_profile', None) if request.user.is_authenticated else None
        
        # Import roster
        results = ExamService.bulk_import_roster(exam, csv_content, teacher)
        
        console_log = {
            "view": "import_roster_csv",
            "exam_id": str(exam_id),
            "file_name": csv_file.name,
            "created": results['created'],
            "updated": results['updated'],
            "errors": len(results.get('errors', []))
        }
        logger.info(f"[PHASE5_ROSTER_IMPORT] {json.dumps(console_log)}")
        print(f"[PHASE5_ROSTER_IMPORT] {json.dumps(console_log)}")
        
        if results['created'] > 0 or results['updated'] > 0:
            messages.success(
                request, 
                f"Successfully imported: {results['created']} new students, {results['updated']} updated"
            )
        
        if results.get('errors'):
            for error in results['errors'][:5]:  # Show first 5 errors
                messages.warning(request, error)
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"[PHASE5_ROSTER_IMPORT_ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
def roster_report(request, exam_id):
    """
    Phase 5: Generate and display roster report.
    """
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Generate report
    report = ExamService.get_roster_report(exam)
    
    # Check if JSON response requested
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(report)
    
    # Otherwise render HTML report
    context = {
        'exam': exam,
        'report': report
    }
    
    return render(request, 'primepath_routinetest/roster_report.html', context)


@require_http_methods(["POST"])
def update_roster_status(request, roster_id):
    """
    Phase 5: Update individual roster entry status.
    """
    try:
        roster_entry = get_object_or_404(StudentRoster, id=roster_id)
        
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in dict(StudentRoster.COMPLETION_STATUS):
            return JsonResponse({
                'success': False,
                'error': 'Invalid status'
            }, status=400)
        
        roster_entry.completion_status = new_status
        roster_entry.save()
        
        console_log = {
            "view": "update_roster_status",
            "roster_id": str(roster_id),
            "student": roster_entry.student_name,
            "new_status": new_status
        }
        logger.info(f"[PHASE5_ROSTER_STATUS_UPDATE] {json.dumps(console_log)}")
        print(f"[PHASE5_ROSTER_STATUS_UPDATE] {json.dumps(console_log)}")
        
        return JsonResponse({
            'success': True,
            'message': f"Status updated to {roster_entry.get_completion_status_display()}"
        })
        
    except Exception as e:
        logger.error(f"[PHASE5_ROSTER_ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["DELETE"])
def remove_roster_entry(request, roster_id):
    """
    Phase 5: Remove a student from the roster.
    """
    try:
        roster_entry = get_object_or_404(StudentRoster, id=roster_id)
        student_name = roster_entry.student_name
        exam_id = roster_entry.exam.id
        
        roster_entry.delete()
        
        console_log = {
            "view": "remove_roster_entry",
            "roster_id": str(roster_id),
            "student": student_name,
            "exam_id": str(exam_id)
        }
        logger.info(f"[PHASE5_ROSTER_REMOVE] {json.dumps(console_log)}")
        print(f"[PHASE5_ROSTER_REMOVE] {json.dumps(console_log)}")
        
        return JsonResponse({
            'success': True,
            'message': f"Removed {student_name} from roster"
        })
        
    except Exception as e:
        logger.error(f"[PHASE5_ROSTER_ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
def export_roster(request, exam_id):
    """
    Phase 5: Export roster to CSV.
    """
    exam = get_object_or_404(Exam, id=exam_id)
    roster_entries = StudentRoster.objects.filter(exam=exam).order_by('class_code', 'student_name')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="roster_{exam.name}_{exam.id}.csv"'
    
    import csv
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Student Name',
        'Student ID',
        'Class',
        'Status',
        'Assigned At',
        'Completed At',
        'Notes'
    ])
    
    # Write data
    for entry in roster_entries:
        writer.writerow([
            entry.student_name,
            entry.student_id,
            entry.get_class_code_display() if hasattr(entry, 'get_class_code_display') else entry.class_code,
            entry.get_completion_status_display(),
            entry.assigned_at.strftime('%Y-%m-%d %H:%M') if entry.assigned_at else '',
            entry.completed_at.strftime('%Y-%m-%d %H:%M') if entry.completed_at else '',
            entry.notes
        ])
    
    console_log = {
        "view": "export_roster",
        "exam_id": str(exam_id),
        "exam_name": exam.name,
        "entries_exported": roster_entries.count()
    }
    logger.info(f"[PHASE5_ROSTER_EXPORT] {json.dumps(console_log)}")
    print(f"[PHASE5_ROSTER_EXPORT] {json.dumps(console_log)}")
    
    return response
"""
Session management views
Handles viewing and managing student test sessions
"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ..models import StudentSession, StudentAnswer
import csv
import logging

logger = logging.getLogger(__name__)


@login_required
def session_list(request):
    """List all placement test sessions with filtering options."""
    sessions = StudentSession.objects.select_related('exam', 'original_curriculum_level', 'school').all()
    
    # Apply search filter
    search_query = request.GET.get('search')
    if search_query:
        sessions = sessions.filter(
            Q(student_name__icontains=search_query) |
            Q(school__name__icontains=search_query) |
            Q(school_name_manual__icontains=search_query)
        )
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'completed':
            sessions = sessions.filter(completed_at__isnull=False)
        elif status_filter == 'in_progress':
            sessions = sessions.filter(completed_at__isnull=True)
    
    grade_filter = request.GET.get('grade')
    if grade_filter:
        sessions = sessions.filter(grade=grade_filter)
    
    academic_rank_filter = request.GET.get('academic_rank')
    if academic_rank_filter:
        sessions = sessions.filter(academic_rank=academic_rank_filter)
    
    date_from = request.GET.get('date_from')
    if date_from:
        sessions = sessions.filter(started_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        sessions = sessions.filter(started_at__date__lte=date_to)
    
    # Calculate statistics
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(completed_at__isnull=False).count()
    in_progress_sessions = sessions.filter(completed_at__isnull=True).count()
    not_started_sessions = 0  # Sessions are started when created
    
    # Order by most recent first
    sessions = sessions.order_by('-started_at')
    
    # Check if there are any in-progress sessions (for auto-refresh)
    has_in_progress = in_progress_sessions > 0
    
    context = {
        'sessions': sessions[:50],  # Show latest 50 sessions
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'in_progress_sessions': in_progress_sessions,
        'not_started_sessions': not_started_sessions,
        'has_in_progress': has_in_progress,
    }
    
    return render(request, 'placement_test/session_list.html', context)


@login_required
def session_detail(request, session_id):
    """Display detailed information about a specific session."""
    session = get_object_or_404(StudentSession, id=session_id)
    answers = StudentAnswer.objects.filter(session=session).select_related('question').order_by('question__question_number')
    
    context = {
        'session': session,
        'answers': answers,
    }
    return render(request, 'placement_test/session_detail.html', context)


@login_required
def grade_session(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    return render(request, 'placement_test/grade_session.html', {'session': session})


@login_required
def export_result(request, session_id):
    """Export session results as PDF or CSV."""
    session = get_object_or_404(StudentSession, id=session_id)
    
    # For now, return a simple CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="placement_test_result_{session_id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Grade', 'School', 'Test Date', 'Score', 'Assigned Level'])
    writer.writerow([
        session.student_name,
        session.grade,
        session.school.name if session.school else session.school_name_manual or 'N/A',
        session.started_at.strftime('%Y-%m-%d %H:%M') if session.started_at else 'N/A',
        f"{session.score}%" if session.score else 'N/A',
        session.original_curriculum_level.full_name if session.original_curriculum_level else 'N/A'
    ])
    
    return response
"""
Admin Dashboard for Student Portal Oversight
Provides comprehensive monitoring and management tools
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg, Q, F, Sum
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json
import csv

from primepath_student.models import StudentProfile, StudentClassAssignment, StudentExamSession
from primepath_routinetest.models import RoutineExam, ExamLaunchSession, Class, StudentEnrollment
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from core.models import Student, Teacher


def is_admin(user):
    """Check if user is admin or staff"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard for student portal"""
    context = {
        'page_title': 'Student Portal Admin Dashboard',
        'stats': get_dashboard_stats(),
        'active_sessions': get_active_sessions(),
        'recent_launches': get_recent_launches(),
        'top_performers': get_top_performers(),
        'struggling_students': get_struggling_students(),
        'class_overview': get_class_overview(),
        'system_health': get_system_health(),
    }
    return render(request, 'primepath_student/admin/dashboard.html', context)


def get_dashboard_stats():
    """Get overall statistics for the dashboard"""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    stats = {
        # Student Statistics
        'total_students': StudentProfile.objects.count(),
        'active_students_today': StudentExamSession.objects.filter(
            started_at__gte=today_start
        ).values('student').distinct().count(),
        'active_students_week': StudentExamSession.objects.filter(
            started_at__gte=week_ago
        ).values('student').distinct().count(),
        'new_registrations_week': StudentProfile.objects.filter(
            created_at__gte=week_ago
        ).count(),
        
        # Exam Statistics
        'total_exams': RoutineExam.objects.filter(is_active=True).count(),
        'active_launches': ExamLaunchSession.objects.filter(
            is_active=True,
            expires_at__gt=now
        ).count(),
        'exams_taken_today': StudentExamSession.objects.filter(
            started_at__gte=today_start
        ).count(),
        'exams_completed_today': StudentExamSession.objects.filter(
            completed_at__gte=today_start,
            status='completed'
        ).count(),
        
        # Performance Statistics
        'average_score_today': StudentExamSession.objects.filter(
            completed_at__gte=today_start,
            status='completed'
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0,
        'average_score_week': StudentExamSession.objects.filter(
            completed_at__gte=week_ago,
            status='completed'
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0,
        
        # Class Statistics
        'total_classes': len(CLASS_CODE_CHOICES),
        'active_classes': StudentClassAssignment.objects.filter(
            is_active=True
        ).values('class_code').distinct().count(),
    }
    
    # Calculate completion rate
    if stats['exams_taken_today'] > 0:
        stats['completion_rate_today'] = round(
            (stats['exams_completed_today'] / stats['exams_taken_today']) * 100, 1
        )
    else:
        stats['completion_rate_today'] = 0
    
    return stats


def get_active_sessions():
    """Get currently active exam sessions"""
    active_sessions = StudentExamSession.objects.filter(
        status='in_progress'
    ).select_related('student', 'exam', 'class_assignment').order_by('-started_at')[:10]
    
    sessions_data = []
    for session in active_sessions:
        time_elapsed = timezone.now() - session.started_at if session.started_at else timedelta(0)
        time_remaining = session.get_time_remaining() if hasattr(session, 'get_time_remaining') else None
        
        sessions_data.append({
            'id': session.id,
            'student_name': session.student.user.get_full_name() or session.student.student_id,
            'student_id': session.student.student_id,
            'exam_name': session.exam.name,
            'class_code': session.class_assignment.class_code if session.class_assignment else 'N/A',
            'started_at': session.started_at,
            'time_elapsed': int(time_elapsed.total_seconds() / 60),  # in minutes
            'time_remaining': time_remaining,
            'progress': session.get_progress_percentage() if hasattr(session, 'get_progress_percentage') else 0,
        })
    
    return sessions_data


def get_recent_launches():
    """Get recently launched exams"""
    recent_launches = ExamLaunchSession.objects.filter(
        is_active=True
    ).select_related('exam', 'launched_by').order_by('-launched_at')[:5]
    
    launches_data = []
    for launch in recent_launches:
        # Count students who have started
        students_started = StudentExamSession.objects.filter(
            exam=launch.exam,
            started_at__gte=launch.launched_at
        ).count()
        
        launches_data.append({
            'id': launch.id,
            'exam_name': launch.exam.name,
            'class_code': launch.class_code,
            'class_display': dict(CLASS_CODE_CHOICES).get(launch.class_code, launch.class_code),
            'launched_by': launch.launched_by.get_full_name() if launch.launched_by else 'System',
            'launched_at': launch.launched_at,
            'expires_at': launch.expires_at,
            'duration_minutes': launch.duration_minutes,
            'students_started': students_started,
            'is_expired': launch.is_expired(),
        })
    
    return launches_data


def get_top_performers():
    """Get top performing students"""
    # Get students with highest average scores
    top_performers = StudentProfile.objects.annotate(
        avg_score=Avg('exam_sessions__score', 
                      filter=Q(exam_sessions__status='completed')),
        exams_taken=Count('exam_sessions',
                          filter=Q(exam_sessions__status='completed'))
    ).filter(
        exams_taken__gt=0
    ).order_by('-avg_score')[:5]
    
    performers_data = []
    for student in top_performers:
        performers_data.append({
            'student_name': student.user.get_full_name() or student.student_id,
            'student_id': student.student_id,
            'average_score': round(student.avg_score or 0, 1),
            'exams_taken': student.exams_taken,
        })
    
    return performers_data


def get_struggling_students():
    """Get students who may need help"""
    # Students with low average scores or incomplete exams
    struggling = StudentProfile.objects.annotate(
        avg_score=Avg('exam_sessions__score',
                      filter=Q(exam_sessions__status='completed')),
        incomplete_count=Count('exam_sessions',
                               filter=Q(exam_sessions__status__in=['expired', 'abandoned']))
    ).filter(
        Q(avg_score__lt=60) | Q(incomplete_count__gt=2)
    ).order_by('avg_score')[:5]
    
    struggling_data = []
    for student in struggling:
        struggling_data.append({
            'student_name': student.user.get_full_name() or student.student_id,
            'student_id': student.student_id,
            'average_score': round(student.avg_score or 0, 1) if student.avg_score else 'N/A',
            'incomplete_exams': student.incomplete_count,
        })
    
    return struggling_data


def get_class_overview():
    """Get overview of all classes"""
    class_data = []
    
    for class_code, class_display in CLASS_CODE_CHOICES:
        # Get statistics for each class
        students_count = StudentClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).count()
        
        active_exams = ExamLaunchSession.objects.filter(
            class_code=class_code,
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        avg_score = StudentExamSession.objects.filter(
            class_assignment__class_code=class_code,
            status='completed'
        ).aggregate(avg=Avg('score'))['avg'] or 0
        
        class_data.append({
            'class_code': class_code,
            'class_display': class_display,
            'students_count': students_count,
            'active_exams': active_exams,
            'average_score': round(avg_score, 1),
        })
    
    return class_data


def get_system_health():
    """Get system health metrics"""
    now = timezone.now()
    hour_ago = now - timedelta(hours=1)
    
    health = {
        'status': 'healthy',  # healthy, warning, critical
        'issues': [],
        'metrics': {
            'active_sessions': StudentExamSession.objects.filter(
                status='in_progress'
            ).count(),
            'sessions_last_hour': StudentExamSession.objects.filter(
                started_at__gte=hour_ago
            ).count(),
            'expired_sessions': StudentExamSession.objects.filter(
                status='in_progress',
                expires_at__lt=now
            ).count(),
            'pending_launches': ExamLaunchSession.objects.filter(
                is_active=True,
                expires_at__gt=now
            ).count(),
        }
    }
    
    # Check for issues
    if health['metrics']['expired_sessions'] > 5:
        health['issues'].append('Multiple expired sessions need cleanup')
        health['status'] = 'warning'
    
    if health['metrics']['active_sessions'] > 100:
        health['issues'].append('High number of active sessions')
        health['status'] = 'warning'
    
    if health['metrics']['sessions_last_hour'] == 0:
        health['issues'].append('No new sessions in the last hour')
    
    return health


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def monitor_session(request, session_id):
    """Monitor a specific exam session in real-time"""
    session = get_object_or_404(StudentExamSession, id=session_id)
    
    data = {
        'session_id': str(session.id),
        'student': {
            'name': session.student.user.get_full_name() or session.student.student_id,
            'id': session.student.student_id,
            'phone': session.student.phone_number,
        },
        'exam': {
            'name': session.exam.name,
            'total_questions': session.total_questions,
        },
        'status': session.status,
        'started_at': session.started_at.isoformat() if session.started_at else None,
        'last_activity': session.auto_saved_at.isoformat() if session.auto_saved_at else None,
        'answers': session.answers,
        'correct_answers': session.correct_answers,
        'score': float(session.score) if session.score else None,
        'time_remaining': session.get_time_remaining() if hasattr(session, 'get_time_remaining') else None,
    }
    
    return JsonResponse(data)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def terminate_session(request, session_id):
    """Terminate an exam session"""
    session = get_object_or_404(StudentExamSession, id=session_id)
    
    if session.status == 'in_progress':
        session.status = 'expired'
        session.completed_at = timezone.now()
        session.save()
        
        messages.success(request, f"Session for {session.student.student_id} has been terminated")
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Session is not in progress'})


@login_required
@user_passes_test(is_admin)
def export_data(request):
    """Export student data to CSV"""
    export_type = request.GET.get('type', 'students')
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'students':
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Name', 'Phone', 'Classes', 'Exams Taken', 'Average Score'])
        
        students = StudentProfile.objects.all()
        for student in students:
            classes = ', '.join([
                dict(CLASS_CODE_CHOICES).get(a.class_code, a.class_code)
                for a in student.class_assignments.filter(is_active=True)
            ])
            exams_taken = student.exam_sessions.filter(status='completed').count()
            avg_score = student.exam_sessions.filter(
                status='completed'
            ).aggregate(avg=Avg('score'))['avg'] or 0
            
            writer.writerow([
                student.student_id,
                student.user.get_full_name() or 'N/A',
                student.phone_number,
                classes,
                exams_taken,
                round(avg_score, 1)
            ])
    
    elif export_type == 'sessions':
        response['Content-Disposition'] = 'attachment; filename="exam_sessions.csv"'
        writer = csv.writer(response)
        writer.writerow(['Session ID', 'Student ID', 'Student Name', 'Exam', 'Class', 
                        'Started', 'Completed', 'Status', 'Score'])
        
        sessions = StudentExamSession.objects.select_related(
            'student', 'exam', 'class_assignment'
        ).order_by('-started_at')
        
        for session in sessions:
            writer.writerow([
                str(session.id),
                session.student.student_id,
                session.student.user.get_full_name() or 'N/A',
                session.exam.name,
                session.class_assignment.class_code if session.class_assignment else 'N/A',
                session.started_at.strftime('%Y-%m-%d %H:%M') if session.started_at else '',
                session.completed_at.strftime('%Y-%m-%d %H:%M') if session.completed_at else '',
                session.status,
                session.score if session.score else ''
            ])
    
    return response


@login_required
@user_passes_test(is_admin)
def analytics_view(request):
    """Detailed analytics view"""
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    if not end_date:
        end_date = timezone.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get analytics data
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'exam_trends': get_exam_trends(start_date, end_date),
        'class_performance': get_class_performance(start_date, end_date),
        'time_analysis': get_time_analysis(start_date, end_date),
    }
    
    return render(request, 'primepath_student/admin/analytics.html', context)


def get_exam_trends(start_date, end_date):
    """Get exam completion trends"""
    # Daily exam completions
    sessions = StudentExamSession.objects.filter(
        completed_at__range=[start_date, end_date],
        status='completed'
    ).extra(
        select={'day': 'date(completed_at)'}
    ).values('day').annotate(
        count=Count('id'),
        avg_score=Avg('score')
    ).order_by('day')
    
    return list(sessions)


def get_class_performance(start_date, end_date):
    """Get performance by class"""
    performance = []
    
    for class_code, class_display in CLASS_CODE_CHOICES:
        sessions = StudentExamSession.objects.filter(
            class_assignment__class_code=class_code,
            completed_at__range=[start_date, end_date],
            status='completed'
        )
        
        if sessions.exists():
            performance.append({
                'class_code': class_code,
                'class_display': class_display,
                'total_exams': sessions.count(),
                'average_score': sessions.aggregate(avg=Avg('score'))['avg'] or 0,
                'students': sessions.values('student').distinct().count(),
            })
    
    return performance


def get_time_analysis(start_date, end_date):
    """Analyze exam timing patterns"""
    # Hour of day analysis
    sessions = StudentExamSession.objects.filter(
        started_at__range=[start_date, end_date]
    ).extra(
        select={'hour': 'extract(hour from started_at)'}
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')
    
    return list(sessions)
"""
Comprehensive Analytics and Reporting System
Provides detailed insights for teachers and administrators
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg, Q, F, Sum, StdDev, Min, Max
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from datetime import datetime, timedelta
import json
import csv
from io import BytesIO
import pandas as pd
import numpy as np
from collections import defaultdict

from core.models import Teacher
from primepath_routinetest.models import (
    RoutineExam, ExamLaunchSession, Class, StudentEnrollment,
    TeacherClassAssignment, ExamScheduleMatrix
)
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from primepath_student.models import StudentProfile, StudentClassAssignment, StudentExamSession

import logging
logger = logging.getLogger(__name__)


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard for teachers"""
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    is_admin = request.user.is_superuser or request.user.is_staff
    
    # Get teacher's classes
    if is_admin:
        accessible_classes = [code for code, _ in CLASS_CODE_CHOICES]
    else:
        accessible_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher_profile,
            is_active=True
        ).values_list('class_code', flat=True)
    
    # Date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_class = request.GET.get('class_code', '')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Filter by class if selected
    if selected_class and selected_class in accessible_classes:
        class_filter = [selected_class]
    else:
        class_filter = accessible_classes
    
    context = {
        'is_admin': is_admin,
        'start_date': start_date,
        'end_date': end_date,
        'selected_class': selected_class,
        'accessible_classes': [(code, dict(CLASS_CODE_CHOICES).get(code, code)) 
                               for code in accessible_classes],
        'overview_stats': get_overview_stats(class_filter, start_date, end_date),
        'performance_trends': get_performance_trends(class_filter, start_date, end_date),
        'exam_analytics': get_exam_analytics(class_filter, start_date, end_date),
        'student_analytics': get_student_analytics(class_filter, start_date, end_date),
        'class_comparison': get_class_comparison(accessible_classes, start_date, end_date),
    }
    
    return render(request, 'primepath_routinetest/analytics/dashboard.html', context)


def get_overview_stats(class_codes, start_date, end_date):
    """Get overview statistics"""
    # Convert dates to timezone-aware datetime
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    
    # Get all sessions in date range
    sessions = StudentExamSession.objects.filter(
        class_assignment__class_code__in=class_codes,
        started_at__range=[start_datetime, end_datetime]
    )
    
    completed_sessions = sessions.filter(status='completed')
    
    stats = {
        'total_exams_taken': sessions.count(),
        'total_exams_completed': completed_sessions.count(),
        'unique_students': sessions.values('student').distinct().count(),
        'average_score': completed_sessions.aggregate(avg=Avg('score'))['avg'] or 0,
        'completion_rate': 0,
        'pass_rate': 0,
        'total_time_spent': 0,
        'average_time_per_exam': 0,
    }
    
    # Calculate rates
    if stats['total_exams_taken'] > 0:
        stats['completion_rate'] = round(
            (stats['total_exams_completed'] / stats['total_exams_taken']) * 100, 1
        )
    
    # Pass rate (assuming 60% is passing)
    passing_sessions = completed_sessions.filter(score__gte=60).count()
    if stats['total_exams_completed'] > 0:
        stats['pass_rate'] = round(
            (passing_sessions / stats['total_exams_completed']) * 100, 1
        )
    
    # Time calculations
    for session in completed_sessions:
        if session.started_at and session.completed_at:
            time_spent = (session.completed_at - session.started_at).total_seconds() / 60
            stats['total_time_spent'] += time_spent
    
    if stats['total_exams_completed'] > 0:
        stats['average_time_per_exam'] = round(
            stats['total_time_spent'] / stats['total_exams_completed'], 1
        )
    
    stats['average_score'] = round(stats['average_score'], 1)
    
    return stats


def get_performance_trends(class_codes, start_date, end_date):
    """Get performance trends over time"""
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    
    # Daily performance
    daily_stats = StudentExamSession.objects.filter(
        class_assignment__class_code__in=class_codes,
        completed_at__range=[start_datetime, end_datetime],
        status='completed'
    ).annotate(
        date=TruncDate('completed_at')
    ).values('date').annotate(
        count=Count('id'),
        avg_score=Avg('score'),
        min_score=Min('score'),
        max_score=Max('score')
    ).order_by('date')
    
    # Format for chart
    trends = {
        'dates': [],
        'exam_counts': [],
        'average_scores': [],
        'score_ranges': []
    }
    
    for stat in daily_stats:
        trends['dates'].append(stat['date'].strftime('%Y-%m-%d'))
        trends['exam_counts'].append(stat['count'])
        trends['average_scores'].append(round(stat['avg_score'] or 0, 1))
        trends['score_ranges'].append({
            'min': round(stat['min_score'] or 0, 1),
            'max': round(stat['max_score'] or 0, 1)
        })
    
    return trends


def get_exam_analytics(class_codes, start_date, end_date):
    """Get detailed exam analytics"""
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    
    # Get exams with statistics
    exam_stats = []
    
    # Get unique exams taken in the period
    exam_ids = StudentExamSession.objects.filter(
        class_assignment__class_code__in=class_codes,
        started_at__range=[start_datetime, end_datetime]
    ).values_list('exam', flat=True).distinct()
    
    for exam_id in exam_ids:
        exam = RoutineExam.objects.get(id=exam_id)
        sessions = StudentExamSession.objects.filter(
            exam=exam,
            class_assignment__class_code__in=class_codes,
            started_at__range=[start_datetime, end_datetime]
        )
        
        completed = sessions.filter(status='completed')
        
        if completed.exists():
            stats = completed.aggregate(
                attempts=Count('id'),
                avg_score=Avg('score'),
                std_dev=StdDev('score'),
                min_score=Min('score'),
                max_score=Max('score'),
                avg_correct=Avg('correct_answers')
            )
            
            # Question-level analysis
            question_stats = analyze_question_performance(exam, completed)
            
            exam_stats.append({
                'exam': exam,
                'attempts': stats['attempts'],
                'average_score': round(stats['avg_score'] or 0, 1),
                'std_deviation': round(stats['std_dev'] or 0, 1),
                'min_score': round(stats['min_score'] or 0, 1),
                'max_score': round(stats['max_score'] or 0, 1),
                'pass_rate': completed.filter(score__gte=60).count() / stats['attempts'] * 100,
                'question_stats': question_stats,
                'difficulty_level': calculate_difficulty_level(stats['avg_score']),
            })
    
    # Sort by attempts (most popular first)
    exam_stats.sort(key=lambda x: x['attempts'], reverse=True)
    
    return exam_stats[:10]  # Top 10 exams


def analyze_question_performance(exam, sessions):
    """Analyze performance on individual questions"""
    question_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    for session in sessions:
        if session.answers:
            for q_num, answer in session.answers.items():
                question_stats[q_num]['total'] += 1
                # Check if answer is correct
                correct_answer = exam.answer_key.get(q_num) if exam.answer_key else None
                if correct_answer and answer == correct_answer:
                    question_stats[q_num]['correct'] += 1
    
    # Calculate success rates
    question_analysis = []
    for q_num, stats in question_stats.items():
        if stats['total'] > 0:
            success_rate = (stats['correct'] / stats['total']) * 100
            question_analysis.append({
                'question_number': q_num,
                'success_rate': round(success_rate, 1),
                'attempts': stats['total'],
                'difficulty': get_question_difficulty(success_rate)
            })
    
    # Sort by question number
    question_analysis.sort(key=lambda x: int(x['question_number']) if x['question_number'].isdigit() else 0)
    
    return question_analysis


def get_question_difficulty(success_rate):
    """Categorize question difficulty based on success rate"""
    if success_rate >= 80:
        return 'Easy'
    elif success_rate >= 60:
        return 'Medium'
    elif success_rate >= 40:
        return 'Hard'
    else:
        return 'Very Hard'


def calculate_difficulty_level(avg_score):
    """Calculate exam difficulty level"""
    if avg_score >= 80:
        return 'Easy'
    elif avg_score >= 65:
        return 'Moderate'
    elif avg_score >= 50:
        return 'Challenging'
    else:
        return 'Difficult'


def get_student_analytics(class_codes, start_date, end_date):
    """Get student performance analytics"""
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    
    # Top performers
    top_students = StudentProfile.objects.filter(
        exam_sessions__class_assignment__class_code__in=class_codes,
        exam_sessions__completed_at__range=[start_datetime, end_datetime],
        exam_sessions__status='completed'
    ).annotate(
        avg_score=Avg('exam_sessions__score'),
        exam_count=Count('exam_sessions'),
        total_correct=Sum('exam_sessions__correct_answers'),
        total_questions=Sum('exam_sessions__total_questions')
    ).filter(
        exam_count__gt=0
    ).order_by('-avg_score')[:10]
    
    # Students needing help
    struggling_students = StudentProfile.objects.filter(
        exam_sessions__class_assignment__class_code__in=class_codes,
        exam_sessions__completed_at__range=[start_datetime, end_datetime],
        exam_sessions__status='completed'
    ).annotate(
        avg_score=Avg('exam_sessions__score'),
        exam_count=Count('exam_sessions')
    ).filter(
        exam_count__gt=0,
        avg_score__lt=60
    ).order_by('avg_score')[:10]
    
    # Format student data
    def format_student(student):
        return {
            'name': student.user.get_full_name() or student.student_id,
            'student_id': student.student_id,
            'average_score': round(student.avg_score or 0, 1),
            'exams_taken': student.exam_count,
            'accuracy': round((student.total_correct / student.total_questions * 100) 
                             if student.total_questions else 0, 1)
        }
    
    return {
        'top_performers': [format_student(s) for s in top_students],
        'struggling_students': [format_student(s) for s in struggling_students],
        'total_active_students': StudentProfile.objects.filter(
            exam_sessions__class_assignment__class_code__in=class_codes,
            exam_sessions__started_at__range=[start_datetime, end_datetime]
        ).distinct().count()
    }


def get_class_comparison(class_codes, start_date, end_date):
    """Compare performance across classes"""
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    
    class_stats = []
    
    for class_code in class_codes:
        sessions = StudentExamSession.objects.filter(
            class_assignment__class_code=class_code,
            completed_at__range=[start_datetime, end_datetime],
            status='completed'
        )
        
        if sessions.exists():
            stats = sessions.aggregate(
                exam_count=Count('id'),
                avg_score=Avg('score'),
                std_dev=StdDev('score'),
                student_count=Count('student', distinct=True)
            )
            
            class_stats.append({
                'class_code': class_code,
                'class_display': dict(CLASS_CODE_CHOICES).get(class_code, class_code),
                'exam_count': stats['exam_count'],
                'average_score': round(stats['avg_score'] or 0, 1),
                'std_deviation': round(stats['std_dev'] or 0, 1),
                'student_count': stats['student_count'],
                'pass_rate': sessions.filter(score__gte=60).count() / stats['exam_count'] * 100
                            if stats['exam_count'] > 0 else 0
            })
    
    # Sort by average score
    class_stats.sort(key=lambda x: x['average_score'], reverse=True)
    
    return class_stats


@login_required
@require_http_methods(["GET"])
def export_analytics_report(request):
    """Export analytics report to Excel"""
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    is_admin = request.user.is_superuser or request.user.is_staff
    
    # Get parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_type = request.GET.get('type', 'full')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get accessible classes
    if is_admin:
        accessible_classes = [code for code, _ in CLASS_CODE_CHOICES]
    else:
        accessible_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher_profile,
            is_active=True
        ).values_list('class_code', flat=True)
    
    # Create Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # Overview sheet
        overview_data = get_overview_stats(accessible_classes, start_date, end_date)
        df_overview = pd.DataFrame([overview_data])
        df_overview.to_excel(writer, sheet_name='Overview', index=False)
        
        # Performance trends sheet
        trends_data = get_performance_trends(accessible_classes, start_date, end_date)
        if trends_data['dates']:
            df_trends = pd.DataFrame({
                'Date': trends_data['dates'],
                'Exams Completed': trends_data['exam_counts'],
                'Average Score': trends_data['average_scores']
            })
            df_trends.to_excel(writer, sheet_name='Performance Trends', index=False)
        
        # Class comparison sheet
        class_data = get_class_comparison(accessible_classes, start_date, end_date)
        if class_data:
            df_classes = pd.DataFrame(class_data)
            df_classes.to_excel(writer, sheet_name='Class Comparison', index=False)
        
        # Student performance sheet
        student_data = get_student_analytics(accessible_classes, start_date, end_date)
        if student_data['top_performers']:
            df_students = pd.DataFrame(student_data['top_performers'])
            df_students.to_excel(writer, sheet_name='Top Students', index=False)
        
        # Exam analytics sheet
        exam_data = get_exam_analytics(accessible_classes, start_date, end_date)
        if exam_data:
            exam_summary = []
            for exam_stat in exam_data:
                exam_summary.append({
                    'Exam Name': exam_stat['exam'].name,
                    'Attempts': exam_stat['attempts'],
                    'Average Score': exam_stat['average_score'],
                    'Pass Rate': round(exam_stat['pass_rate'], 1),
                    'Difficulty': exam_stat['difficulty_level']
                })
            df_exams = pd.DataFrame(exam_summary)
            df_exams.to_excel(writer, sheet_name='Exam Analytics', index=False)
    
    # Prepare response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=analytics_report_{start_date}_{end_date}.xlsx'
    
    return response


@login_required
@require_http_methods(["GET"])
def get_chart_data(request):
    """API endpoint for chart data"""
    chart_type = request.GET.get('chart', 'performance')
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    is_admin = request.user.is_superuser or request.user.is_staff
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get accessible classes
    if is_admin:
        accessible_classes = [code for code, _ in CLASS_CODE_CHOICES]
    else:
        accessible_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher_profile,
            is_active=True
        ).values_list('class_code', flat=True)
    
    if chart_type == 'performance':
        data = get_performance_trends(accessible_classes, start_date, end_date)
    elif chart_type == 'class_comparison':
        data = get_class_comparison(accessible_classes, start_date, end_date)
    elif chart_type == 'student_distribution':
        data = get_score_distribution(accessible_classes, start_date, end_date)
    else:
        data = {}
    
    return JsonResponse(data)


def get_score_distribution(class_codes, start_date, end_date):
    """Get score distribution for histogram"""
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    
    scores = StudentExamSession.objects.filter(
        class_assignment__class_code__in=class_codes,
        completed_at__range=[start_datetime, end_datetime],
        status='completed'
    ).values_list('score', flat=True)
    
    # Create bins for histogram
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    distribution = []
    
    for i in range(len(bins) - 1):
        count = sum(1 for score in scores if bins[i] <= score < bins[i+1])
        distribution.append({
            'range': f'{bins[i]}-{bins[i+1]}',
            'count': count
        })
    
    return {'distribution': distribution}
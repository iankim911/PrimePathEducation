"""
Dashboard Service - Statistics and analytics for teacher dashboard
Part of Phase 5 modularization
"""
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard statistics and analytics."""
    
    @staticmethod
    def get_dashboard_stats():
        """Get comprehensive dashboard statistics."""
        from placement_test.models import StudentSession, PlacementExam as Exam, StudentAnswer
        from core.models import School, CurriculumLevel
        
        try:
            # Get basic counts
            stats = {
                'total_sessions': StudentSession.objects.count(),
                'active_exams': Exam.objects.filter(is_active=True).count(),
                'total_schools': School.objects.count(),
                'completed_sessions': StudentSession.objects.filter(
                    completed_at__isnull=False
                ).count(),
            }
            
            # Calculate completion rate
            if stats['total_sessions'] > 0:
                stats['completion_rate'] = (
                    stats['completed_sessions'] / stats['total_sessions'] * 100
                )
            else:
                stats['completion_rate'] = 0
            
            # Get recent activity (last 24 hours)
            recent_cutoff = timezone.now() - timedelta(hours=24)
            stats['recent_sessions'] = StudentSession.objects.filter(
                started_at__gte=recent_cutoff
            ).count()
            
            # Get average score for completed sessions
            completed_sessions = StudentSession.objects.filter(
                completed_at__isnull=False
            ).annotate(
                score=Count('answers', filter=Q(answers__is_correct=True))
            ).aggregate(
                avg_score=Avg('score')
            )
            stats['average_score'] = completed_sessions['avg_score'] or 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {
                'total_sessions': 0,
                'active_exams': 0,
                'total_schools': 0,
                'completed_sessions': 0,
                'completion_rate': 0,
                'recent_sessions': 0,
                'average_score': 0
            }
    
    @staticmethod
    def get_recent_sessions(limit=10):
        """Get recent student sessions with optimized queries."""
        from placement_test.models import StudentSession
        
        try:
            sessions = StudentSession.objects.select_related(
                'exam',
                'school',
                'original_curriculum_level',
                'final_curriculum_level',
                'original_curriculum_level__subprogram',
                'final_curriculum_level__subprogram'
            ).prefetch_related(
                'answers'
            ).order_by('-started_at')[:limit]
            
            # Add computed fields
            for session in sessions:
                if session.completed_at:
                    session.duration = (
                        session.completed_at - session.started_at
                    ).total_seconds() / 60  # Convert to minutes
                else:
                    session.duration = None
                
                # Calculate score
                total_answers = session.answers.count()
                correct_answers = session.answers.filter(is_correct=True).count()
                
                if total_answers > 0:
                    session.score_percentage = (correct_answers / total_answers) * 100
                else:
                    session.score_percentage = 0
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting recent sessions: {e}")
            return []
    
    @staticmethod
    def get_exam_statistics():
        """Get statistics for each exam."""
        from placement_test.models import PlacementExam as Exam, StudentSession
        
        try:
            exams = Exam.objects.filter(is_active=True).annotate(
                session_count=Count('sessions'),
                completion_count=Count(
                    'sessions',
                    filter=Q(sessions__completed_at__isnull=False)
                ),
                avg_duration=Avg(
                    F('sessions__completed_at') - F('sessions__started_at'),
                    filter=Q(sessions__completed_at__isnull=False)
                )
            ).order_by('-session_count')
            
            exam_stats = []
            for exam in exams:
                stats = {
                    'exam': exam,
                    'session_count': exam.session_count,
                    'completion_count': exam.completion_count,
                    'completion_rate': (
                        exam.completion_count / exam.session_count * 100
                        if exam.session_count > 0 else 0
                    ),
                    'avg_duration_minutes': (
                        exam.avg_duration.total_seconds() / 60
                        if exam.avg_duration else 0
                    )
                }
                exam_stats.append(stats)
            
            return exam_stats
            
        except Exception as e:
            logger.error(f"Error getting exam statistics: {e}")
            return []
    
    @staticmethod
    def get_school_performance():
        """Get performance statistics by school."""
        from placement_test.models import StudentSession
        from core.models import School
        
        try:
            schools = School.objects.annotate(
                student_count=Count('studentsession'),
                completed_count=Count(
                    'studentsession',
                    filter=Q(studentsession__completed_at__isnull=False)
                )
            ).filter(student_count__gt=0).order_by('-student_count')[:10]
            
            school_stats = []
            for school in schools:
                stats = {
                    'school': school,
                    'student_count': school.student_count,
                    'completed_count': school.completed_count,
                    'completion_rate': (
                        school.completed_count / school.student_count * 100
                        if school.student_count > 0 else 0
                    )
                }
                school_stats.append(stats)
            
            return school_stats
            
        except Exception as e:
            logger.error(f"Error getting school performance: {e}")
            return []
    
    @staticmethod
    def get_grade_distribution():
        """Get distribution of students by grade."""
        from placement_test.models import StudentSession
        
        try:
            distribution = StudentSession.objects.values('grade').annotate(
                count=Count('id')
            ).order_by('grade')
            
            return list(distribution)
            
        except Exception as e:
            logger.error(f"Error getting grade distribution: {e}")
            return []
    
    @staticmethod
    def get_curriculum_level_usage():
        """Get usage statistics for curriculum levels."""
        from core.models import CurriculumLevel
        
        try:
            levels = CurriculumLevel.objects.annotate(
                exam_count=Count('exams', filter=Q(exams__is_active=True)),
                session_count=Count('original_sessions')
            ).filter(
                Q(exam_count__gt=0) | Q(session_count__gt=0)
            ).select_related(
                'subprogram',
                'subprogram__program'
            ).order_by('-session_count')
            
            return levels
            
        except Exception as e:
            logger.error(f"Error getting curriculum level usage: {e}")
            return []
    
    @staticmethod
    def get_performance_trends(days=7):
        """Get performance trends over time."""
        from placement_test.models import StudentSession
        
        try:
            cutoff = timezone.now() - timedelta(days=days)
            
            # Group by date
            trends = []
            for i in range(days):
                date = timezone.now().date() - timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                sessions = StudentSession.objects.filter(
                    started_at__date=date
                )
                
                completed = sessions.filter(
                    completed_at__isnull=False
                ).count()
                
                total = sessions.count()
                
                trends.append({
                    'date': date,
                    'total_sessions': total,
                    'completed_sessions': completed,
                    'completion_rate': (
                        completed / total * 100 if total > 0 else 0
                    )
                })
            
            trends.reverse()  # Show oldest to newest
            return trends
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return []
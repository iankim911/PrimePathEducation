"""
Query optimization utilities for placement test app.
Addresses performance issues after 9000+ sessions.
"""
from django.db.models import Prefetch, Count, Q, F
from django.core.cache import cache
from .models import Exam, StudentSession, Question, StudentAnswer, AudioFile
import logging

logger = logging.getLogger(__name__)


class OptimizedQueries:
    """Optimized database queries with caching."""
    
    @staticmethod
    def get_exam_with_questions(exam_id, use_cache=True):
        """
        Get exam with all related data in a single query.
        Uses select_related and prefetch_related for optimization.
        """
        cache_key = f'exam_full_{exam_id}'
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for exam {exam_id}")
                return cached
        
        exam = Exam.objects.select_related(
            'curriculum_level',
            'curriculum_level__subprogram',
            'curriculum_level__subprogram__program',
            'created_by'
        ).prefetch_related(
            Prefetch('questions', queryset=Question.objects.order_by('question_number')),
            Prefetch('audio_files', queryset=AudioFile.objects.order_by('start_question'))
        ).get(id=exam_id)
        
        if use_cache:
            cache.set(cache_key, exam, 300)  # Cache for 5 minutes
            
        return exam
    
    @staticmethod
    def get_session_with_answers(session_id, use_cache=True):
        """
        Get session with all answers in optimized query.
        """
        cache_key = f'session_answers_{session_id}'
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        session = StudentSession.objects.select_related(
            'exam',
            'school',
            'original_curriculum_level',
            'final_curriculum_level'
        ).prefetch_related(
            Prefetch('answers', 
                    queryset=StudentAnswer.objects.select_related('question'))
        ).get(id=session_id)
        
        if use_cache and session.is_completed:
            # Only cache completed sessions
            cache.set(cache_key, session, 3600)  # Cache for 1 hour
            
        return session
    
    @staticmethod
    def get_recent_sessions(limit=10):
        """
        Get recent sessions with optimized query.
        """
        return StudentSession.objects.select_related(
            'exam',
            'school',
            'original_curriculum_level',
            'final_curriculum_level'
        ).order_by('-started_at')[:limit]
    
    @staticmethod
    def get_active_exams_count():
        """
        Get count of active exams with caching.
        """
        cache_key = 'active_exams_count'
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
            
        count = Exam.objects.filter(is_active=True).count()
        cache.set(cache_key, count, 60)  # Cache for 1 minute
        return count
    
    @staticmethod
    def batch_save_answers(session_id, answers_data):
        """
        Batch save multiple answers in a single transaction.
        Reduces database hits significantly.
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Get or create all answers in batch
            answers_to_update = []
            answers_to_create = []
            
            # Get existing answers
            existing = {
                (a.session_id, a.question_id): a 
                for a in StudentAnswer.objects.filter(
                    session_id=session_id,
                    question_id__in=[a['question_id'] for a in answers_data]
                )
            }
            
            for answer_data in answers_data:
                key = (session_id, answer_data['question_id'])
                if key in existing:
                    answer = existing[key]
                    answer.answer = answer_data['answer']
                    answer.answer_type = answer_data.get('answer_type', 'radio')
                    answers_to_update.append(answer)
                else:
                    answers_to_create.append(
                        StudentAnswer(
                            session_id=session_id,
                            question_id=answer_data['question_id'],
                            answer=answer_data['answer'],
                            answer_type=answer_data.get('answer_type', 'radio')
                        )
                    )
            
            # Bulk operations
            if answers_to_update:
                StudentAnswer.objects.bulk_update(
                    answers_to_update, 
                    ['answer', 'answer_type', 'updated_at']
                )
            
            if answers_to_create:
                StudentAnswer.objects.bulk_create(answers_to_create)
            
            # Clear cache for this session
            cache.delete(f'session_answers_{session_id}')
            
            logger.info(f"Batch saved {len(answers_data)} answers for session {session_id}")
    
    @staticmethod
    def cleanup_old_sessions(days=30):
        """
        Clean up old incomplete sessions to prevent database bloat.
        """
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Delete incomplete sessions older than cutoff
        deleted_count = StudentSession.objects.filter(
            is_completed=False,
            started_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old incomplete sessions")
        return deleted_count
    
    @staticmethod
    def get_session_statistics():
        """
        Get session statistics with single optimized query.
        """
        from django.db.models import Avg, Count
        
        cache_key = 'session_statistics'
        cached = cache.get(cache_key)
        
        if cached:
            return cached
        
        stats = StudentSession.objects.aggregate(
            total_sessions=Count('id'),
            completed_sessions=Count('id', filter=Q(is_completed=True)),
            avg_score=Avg('score', filter=Q(is_completed=True)),
            total_schools=Count('school', distinct=True)
        )
        
        cache.set(cache_key, stats, 300)  # Cache for 5 minutes
        return stats
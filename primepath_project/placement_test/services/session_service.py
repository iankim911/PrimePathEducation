"""
Service for managing student test sessions.
"""
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from core.models import School
from core.exceptions import ValidationException, SessionAlreadyCompletedException
from ..models import StudentSession, StudentAnswer, Exam, Question, DifficultyAdjustment
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Handles student session creation and management."""
    
    @staticmethod
    @transaction.atomic
    def create_session(
        student_data: Dict[str, Any],
        exam: Exam,
        curriculum_level_id: int,
        request_meta: Dict[str, str]
    ) -> StudentSession:
        """
        Create a new student session with answer placeholders.
        
        Args:
            student_data: Dictionary containing student information
            exam: Exam instance
            curriculum_level_id: Curriculum level ID
            request_meta: Request metadata (IP, user agent)
            
        Returns:
            Created StudentSession instance
        """
        # Handle school creation/retrieval
        school = None
        school_name = student_data.get('school_name')
        if school_name:
            school, _ = School.objects.get_or_create(name=school_name)
        
        # Create session
        session = StudentSession.objects.create(
            student_name=student_data['student_name'],
            parent_phone=student_data.get('parent_phone', ''),
            school=school,
            school_name_manual=school_name if not school else '',
            grade=student_data['grade'],
            academic_rank=student_data['academic_rank'],
            exam=exam,
            original_curriculum_level_id=curriculum_level_id,
            final_curriculum_level_id=curriculum_level_id,
            ip_address=request_meta.get('REMOTE_ADDR'),
            user_agent=request_meta.get('HTTP_USER_AGENT', '')
        )
        
        # Create answer placeholders for all questions
        questions = exam.questions.all()
        answer_objects = [
            StudentAnswer(
                session=session,
                question=question,
                answer=''
            )
            for question in questions
        ]
        StudentAnswer.objects.bulk_create(answer_objects)
        
        logger.info(
            f"Created session {session.id} for {student_data['student_name']}",
            extra={
                'session_id': str(session.id),
                'exam_id': str(exam.id),
                'student_name': student_data['student_name']
            }
        )
        
        return session
    
    @staticmethod
    def submit_answer(
        session: StudentSession,
        question_id: int,
        answer: str
    ) -> StudentAnswer:
        """
        Submit an answer for a specific question.
        
        Args:
            session: Student session
            question_id: Question ID
            answer: Answer text
            
        Returns:
            Updated StudentAnswer instance
            
        Raises:
            SessionAlreadyCompletedException: If session is completed
            ValidationException: If question is invalid
        """
        if session.is_completed:
            raise SessionAlreadyCompletedException(
                "Cannot submit answers to a completed test",
                code="SESSION_COMPLETED"
            )
        
        try:
            student_answer = StudentAnswer.objects.get(
                session=session,
                question_id=question_id
            )
        except StudentAnswer.DoesNotExist:
            raise ValidationException(
                "Invalid question for this session",
                code="INVALID_QUESTION",
                details={'question_id': question_id, 'session_id': str(session.id)}
            )
        
        student_answer.answer = answer
        student_answer.save()
        
        logger.debug(
            f"Answer submitted for session {session.id}, question {question_id}"
        )
        
        return student_answer
    
    @staticmethod
    @transaction.atomic
    def complete_session(session: StudentSession) -> Dict[str, Any]:
        """
        Complete a test session and calculate scores.
        
        Args:
            session: Student session to complete
            
        Returns:
            Dictionary with completion results
            
        Raises:
            SessionAlreadyCompletedException: If already completed
        """
        if session.is_completed:
            raise SessionAlreadyCompletedException(
                "Test has already been completed",
                code="ALREADY_COMPLETED"
            )
        
        # Auto-grade all answers
        total_score = 0
        total_possible = 0
        graded_count = 0
        
        for answer in session.answers.all():
            answer.auto_grade()
            answer.save()
            
            # Only count non-long answer questions in score
            if answer.question.question_type not in ['LONG']:
                total_possible += answer.question.points
                total_score += answer.points_earned
                graded_count += 1
        
        # Update session with results
        session.score = total_score
        session.percentage_score = (
            (total_score / total_possible * 100) if total_possible > 0 else 0
        )
        session.completed_at = timezone.now()
        
        # Calculate time spent
        time_diff = session.completed_at - session.started_at
        session.time_spent_seconds = int(time_diff.total_seconds())
        
        session.save()
        
        logger.info(
            f"Completed session {session.id} with score {session.percentage_score:.1f}%",
            extra={
                'session_id': str(session.id),
                'score': total_score,
                'percentage': float(session.percentage_score or 0),
                'time_spent': session.time_spent_seconds
            }
        )
        
        return {
            'total_score': total_score,
            'total_possible': total_possible,
            'percentage_score': float(session.percentage_score or 0),
            'graded_count': graded_count,
            'time_spent_seconds': session.time_spent_seconds
        }
    
    @staticmethod
    @transaction.atomic
    def adjust_session_difficulty(
        session: StudentSession,
        adjustment: int,
        new_level,
        new_exam: Exam
    ) -> StudentSession:
        """
        Adjust the difficulty of a session by changing the exam.
        
        Args:
            session: Current session
            adjustment: +1 or -1
            new_level: New curriculum level
            new_exam: New exam instance
            
        Returns:
            Updated session
        """
        if session.is_completed:
            raise SessionAlreadyCompletedException(
                "Cannot adjust difficulty of completed session"
            )
        
        # Record the adjustment
        DifficultyAdjustment.objects.create(
            session=session,
            from_level=session.final_curriculum_level,
            to_level=new_level,
            adjustment=adjustment
        )
        
        # Update session
        session.final_curriculum_level = new_level
        session.exam = new_exam
        session.difficulty_adjustments += adjustment
        session.save()
        
        # Clear existing answers and create new ones
        session.answers.all().delete()
        
        answer_objects = [
            StudentAnswer(
                session=session,
                question=question,
                answer=''
            )
            for question in new_exam.questions.all()
        ]
        StudentAnswer.objects.bulk_create(answer_objects)
        
        logger.info(
            f"Adjusted difficulty for session {session.id}: "
            f"{adjustment:+d} to level {new_level.full_name}"
        )
        
        return session
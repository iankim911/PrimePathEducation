"""
Service for grading and evaluation of student answers.
"""
from typing import Dict, Any, List, Optional
from django.db import transaction
from ..models import StudentAnswer, Question, StudentSession
import logging

logger = logging.getLogger(__name__)


class GradingService:
    """Handles grading logic for different question types."""
    
    @staticmethod
    def grade_mcq_answer(student_answer: str, correct_answer: str) -> bool:
        """
        Grade a multiple choice question.
        
        Args:
            student_answer: Student's answer
            correct_answer: Correct answer
            
        Returns:
            True if correct, False otherwise
        """
        return student_answer.strip().upper() == correct_answer.strip().upper()
    
    @staticmethod
    def grade_checkbox_answer(student_answer: str, correct_answer: str) -> bool:
        """
        Grade a checkbox (select all) question.
        
        Args:
            student_answer: Comma-separated student answers
            correct_answer: Comma-separated correct answers
            
        Returns:
            True if all correct options selected, False otherwise
        """
        # Convert to sets for comparison
        student_set = {
            ans.strip().upper() 
            for ans in student_answer.split(',') 
            if ans.strip()
        }
        correct_set = {
            ans.strip().upper() 
            for ans in correct_answer.split(',') 
            if ans.strip()
        }
        
        return student_set == correct_set
    
    @staticmethod
    def grade_short_answer(
        student_answer: str,
        correct_answer: str,
        case_sensitive: bool = False
    ) -> Optional[bool]:
        """
        Grade a short answer question.
        
        Args:
            student_answer: Student's answer
            correct_answer: Correct answer(s) separated by |
            case_sensitive: Whether to check case
            
        Returns:
            True if matches any acceptable answer, None if manual grading needed
        """
        if not correct_answer:
            # No automatic grading possible
            return None
            
        # Get all acceptable answers
        acceptable_answers = [
            ans.strip() for ans in correct_answer.split('|')
        ]
        
        student_ans = student_answer.strip()
        
        if not case_sensitive:
            student_ans = student_ans.lower()
            acceptable_answers = [ans.lower() for ans in acceptable_answers]
        
        return student_ans in acceptable_answers
    
    @staticmethod
    def auto_grade_answer(answer: StudentAnswer) -> Dict[str, Any]:
        """
        Automatically grade an answer based on question type.
        
        Args:
            answer: StudentAnswer instance
            
        Returns:
            Dictionary with grading results
        """
        question = answer.question
        result = {
            'is_correct': None,
            'points_earned': 0,
            'requires_manual_grading': False
        }
        
        if question.question_type == 'MCQ':
            result['is_correct'] = GradingService.grade_mcq_answer(
                answer.answer,
                question.correct_answer
            )
            
        elif question.question_type == 'CHECKBOX':
            result['is_correct'] = GradingService.grade_checkbox_answer(
                answer.answer,
                question.correct_answer
            )
            
        elif question.question_type == 'SHORT':
            result['is_correct'] = GradingService.grade_short_answer(
                answer.answer,
                question.correct_answer
            )
            if result['is_correct'] is None:
                result['requires_manual_grading'] = True
                
        elif question.question_type in ['LONG', 'MIXED']:
            # These require manual grading
            result['requires_manual_grading'] = True
            
        # Calculate points
        if result['is_correct']:
            result['points_earned'] = question.points
            
        return result
    
    @staticmethod
    @transaction.atomic
    def grade_session(
        session: StudentSession,
        manual_grades: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Grade an entire session, optionally with manual grades.
        
        Args:
            session: Student session to grade
            manual_grades: Dictionary of {question_id: {'is_correct': bool, 'points': int}}
            
        Returns:
            Summary of grading results
        """
        total_score = 0
        total_possible = 0
        auto_graded = 0
        manual_graded = 0
        requires_manual = []
        
        for answer in session.answers.select_related('question').all():
            question_id = answer.question.id
            
            # Check for manual grade first
            if manual_grades and question_id in manual_grades:
                grade_info = manual_grades[question_id]
                answer.is_correct = grade_info.get('is_correct')
                answer.points_earned = grade_info.get('points', 0)
                manual_graded += 1
            else:
                # Auto grade
                grade_result = GradingService.auto_grade_answer(answer)
                answer.is_correct = grade_result['is_correct']
                answer.points_earned = grade_result['points_earned']
                
                if grade_result['requires_manual_grading']:
                    requires_manual.append({
                        'question_id': question_id,
                        'question_number': answer.question.question_number,
                        'question_type': answer.question.question_type
                    })
                else:
                    auto_graded += 1
            
            answer.save()
            
            # Calculate totals (exclude LONG answers from total possible)
            if answer.question.question_type not in ['LONG']:
                total_possible += answer.question.points
                total_score += answer.points_earned
        
        # Update session score
        session.score = total_score
        session.percentage_score = (
            (total_score / total_possible * 100) if total_possible > 0 else 0
        )
        session.save()
        
        logger.info(
            f"Graded session {session.id}: "
            f"{auto_graded} auto, {manual_graded} manual, "
            f"{len(requires_manual)} need manual grading"
        )
        
        return {
            'total_score': total_score,
            'total_possible': total_possible,
            'percentage_score': float(session.percentage_score or 0),
            'auto_graded': auto_graded,
            'manual_graded': manual_graded,
            'requires_manual_grading': requires_manual,
            'is_complete': len(requires_manual) == 0
        }
    
    @staticmethod
    def get_session_analytics(session: StudentSession) -> Dict[str, Any]:
        """
        Get detailed analytics for a session.
        
        Args:
            session: Student session
            
        Returns:
            Dictionary with analytics data
        """
        answers = session.answers.select_related('question').all()
        
        # Group by question type
        type_performance = {}
        for answer in answers:
            q_type = answer.question.question_type
            if q_type not in type_performance:
                type_performance[q_type] = {
                    'total': 0,
                    'correct': 0,
                    'points_earned': 0,
                    'points_possible': 0
                }
            
            type_performance[q_type]['total'] += 1
            if answer.is_correct:
                type_performance[q_type]['correct'] += 1
            type_performance[q_type]['points_earned'] += answer.points_earned
            type_performance[q_type]['points_possible'] += answer.question.points
        
        # Calculate percentages
        for q_type, data in type_performance.items():
            data['percentage'] = (
                (data['correct'] / data['total'] * 100) 
                if data['total'] > 0 else 0
            )
        
        # Time analysis
        time_per_question = (
            session.time_spent_seconds / session.exam.total_questions
            if session.time_spent_seconds else 0
        )
        
        return {
            'type_performance': type_performance,
            'total_questions': session.exam.total_questions,
            'questions_answered': answers.filter(answer__gt='').count(),
            'time_spent_seconds': session.time_spent_seconds,
            'time_per_question': time_per_question,
            'difficulty_adjustments': session.difficulty_adjustments,
            'final_level': session.final_curriculum_level.full_name if session.final_curriculum_level else None
        }
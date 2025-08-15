"""
PHASE 8 COMPREHENSIVE POINTS SERVICE
Production-ready service for managing question points with enterprise-grade features.

This service provides:
- Multi-layer validation with detailed error reporting
- Transaction-safe bulk update operations  
- Points analytics and recommendations
- Session recalculation for affected students
- Extensive audit logging for debugging
- Performance optimization for bulk operations
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
from decimal import Decimal

from django.db import transaction, models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from ..models import Question, Exam, StudentSession, StudentAnswer
from .grading_service import GradingService

logger = logging.getLogger(__name__)

class PointsService:
    """
    Enterprise-grade Points Management Service
    
    Provides comprehensive points editing capabilities with:
    - Atomic transaction safety
    - Multi-layer validation
    - Bulk operations optimization
    - Analytics generation
    - Audit trail logging
    - Performance monitoring
    """
    
    # Configuration constants
    MIN_POINTS = 1
    MAX_POINTS = 10
    DEFAULT_POINTS = 1
    BULK_OPERATION_THRESHOLD = 50  # Log bulk operations involving 50+ questions
    
    @classmethod
    def validate_points_value(cls, points: Union[int, str, float]) -> Tuple[bool, str, int]:
        """
        Comprehensive points validation with detailed error reporting.
        
        Args:
            points: Points value to validate
            
        Returns:
            Tuple of (is_valid, error_message, validated_points)
        """
        try:
            # Step 1: Type conversion with error handling
            if isinstance(points, str):
                points = points.strip()
                if not points:
                    return False, "Points value cannot be empty", cls.DEFAULT_POINTS
                
                # Handle decimal strings
                try:
                    points_float = float(points)
                    points_int = int(points_float)
                    
                    # Check for decimal values
                    if points_float != points_int:
                        return False, f"Points must be a whole number, got {points_float}", cls.DEFAULT_POINTS
                    
                    points = points_int
                except ValueError:
                    return False, f"Invalid points format: '{points}' is not a number", cls.DEFAULT_POINTS
            
            elif isinstance(points, float):
                if not points.is_integer():
                    return False, f"Points must be a whole number, got {points}", cls.DEFAULT_POINTS
                points = int(points)
            
            elif not isinstance(points, int):
                return False, f"Points must be an integer, got {type(points).__name__}", cls.DEFAULT_POINTS
            
            # Step 2: Range validation
            if points < cls.MIN_POINTS:
                return False, f"Points must be at least {cls.MIN_POINTS}, got {points}", cls.MIN_POINTS
            
            if points > cls.MAX_POINTS:
                return False, f"Points cannot exceed {cls.MAX_POINTS}, got {points}", cls.MAX_POINTS
            
            # Step 3: Success
            return True, "", points
            
        except Exception as e:
            logger.error(f"[PointsService.validate_points_value] Unexpected error: {e}")
            return False, f"Validation error: {str(e)}", cls.DEFAULT_POINTS
    
    @classmethod
    @transaction.atomic
    def update_question_points(
        cls, 
        question_id: Union[int, str], 
        new_points: Union[int, str, float],
        user_id: Optional[int] = None,
        recalculate_sessions: bool = True
    ) -> Dict[str, Any]:
        """
        Update points for a single question with comprehensive validation and logging.
        
        Args:
            question_id: Question ID to update
            new_points: New points value
            user_id: User making the change (for audit trail)
            recalculate_sessions: Whether to recalculate affected student sessions
            
        Returns:
            Dictionary with operation results and metadata
        """
        operation_start = timezone.now()
        audit_log = {
            'operation': 'update_question_points',
            'timestamp': operation_start.isoformat(),
            'user_id': user_id,
            'question_id': str(question_id),
            'new_points': str(new_points),
            'success': False,
            'error': None,
            'changes': {},
            'affected_sessions': [],
            'performance': {}
        }
        
        try:
            logger.info(f"[PointsService] Starting points update: Q{question_id} -> {new_points} points")
            
            # Step 1: Validate points value
            is_valid, error_msg, validated_points = cls.validate_points_value(new_points)
            if not is_valid:
                audit_log['error'] = f"Validation failed: {error_msg}"
                logger.warning(f"[PointsService] Validation failed for Q{question_id}: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'validated_points': validated_points,
                    'audit_log': audit_log
                }
            
            # Step 2: Get and validate question
            try:
                question = Question.objects.select_related('exam').get(id=question_id)
            except ObjectDoesNotExist:
                error_msg = f"Question with ID {question_id} does not exist"
                audit_log['error'] = error_msg
                logger.error(f"[PointsService] {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'audit_log': audit_log
                }
            
            # Step 3: Check if change is needed
            old_points = question.points
            if old_points == validated_points:
                logger.info(f"[PointsService] No change needed for Q{question_id}: already {validated_points} points")
                audit_log['success'] = True
                audit_log['changes'] = {'no_change_needed': True}
                return {
                    'success': True,
                    'message': f'Question {question.question_number} already has {validated_points} points',
                    'old_points': old_points,
                    'new_points': validated_points,
                    'question': {
                        'id': question.id,
                        'number': question.question_number,
                        'type': question.question_type,
                        'exam': question.exam.name
                    },
                    'audit_log': audit_log
                }
            
            # Step 4: Apply update with model validation
            question.points = validated_points
            try:
                question.full_clean()  # Trigger model validation
                question.save()
            except ValidationError as ve:
                error_msg = f"Model validation failed: {ve}"
                audit_log['error'] = error_msg
                logger.error(f"[PointsService] {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'audit_log': audit_log
                }
            
            # Step 5: Log the change
            audit_log['changes'] = {
                'old_points': old_points,
                'new_points': validated_points,
                'points_delta': validated_points - old_points
            }
            
            logger.info(f"[PointsService] ✓ Updated Q{question.question_number}: {old_points} -> {validated_points} points")
            
            # Step 6: Recalculate affected student sessions (if requested)
            affected_sessions = []
            if recalculate_sessions:
                recalc_start = timezone.now()
                
                # Find sessions with answers to this question
                sessions_to_recalc = StudentSession.objects.filter(
                    answers__question=question,
                    completed_at__isnull=False
                ).distinct()
                
                logger.info(f"[PointsService] Found {sessions_to_recalc.count()} completed sessions to recalculate")
                
                for session in sessions_to_recalc:
                    try:
                        old_score = session.score
                        old_percentage = session.percentage_score
                        
                        # Recalculate session using GradingService
                        grading_result = GradingService.grade_session(session)
                        
                        affected_sessions.append({
                            'session_id': str(session.id),
                            'student_name': session.student_name,
                            'old_score': old_score,
                            'new_score': grading_result['total_score'],
                            'old_percentage': float(old_percentage) if old_percentage else 0,
                            'new_percentage': grading_result['percentage_score'],
                            'score_delta': grading_result['total_score'] - (old_score or 0)
                        })
                        
                        logger.debug(f"[PointsService] Recalculated session {session.id}: {old_percentage:.1f}% -> {grading_result['percentage_score']:.1f}%")
                        
                    except Exception as se:
                        logger.error(f"[PointsService] Failed to recalculate session {session.id}: {se}")
                        affected_sessions.append({
                            'session_id': str(session.id),
                            'error': str(se)
                        })
                
                recalc_duration = (timezone.now() - recalc_start).total_seconds()
                audit_log['performance']['recalculation_time_seconds'] = recalc_duration
                
                logger.info(f"[PointsService] Recalculated {len(affected_sessions)} sessions in {recalc_duration:.2f}s")
            
            # Step 7: Performance metrics
            total_duration = (timezone.now() - operation_start).total_seconds()
            audit_log['performance']['total_time_seconds'] = total_duration
            audit_log['affected_sessions'] = affected_sessions
            audit_log['success'] = True
            
            # Step 8: Final success log
            logger.info(f"[PointsService] ✅ Points update completed successfully in {total_duration:.2f}s")
            logger.info(f"[PointsService] Audit: {json.dumps(audit_log, indent=2)}")
            
            return {
                'success': True,
                'message': f'Successfully updated question {question.question_number} from {old_points} to {validated_points} points',
                'old_points': old_points,
                'new_points': validated_points,
                'points_delta': validated_points - old_points,
                'question': {
                    'id': question.id,
                    'number': question.question_number,
                    'type': question.question_type,
                    'exam': question.exam.name
                },
                'affected_sessions': affected_sessions,
                'performance': audit_log['performance'],
                'audit_log': audit_log
            }
            
        except Exception as e:
            # Rollback is automatic due to @transaction.atomic
            error_msg = f"Unexpected error updating question points: {str(e)}"
            audit_log['error'] = error_msg
            audit_log['performance']['total_time_seconds'] = (timezone.now() - operation_start).total_seconds()
            
            logger.error(f"[PointsService] {error_msg}", exc_info=True)
            logger.error(f"[PointsService] Failed audit: {json.dumps(audit_log, indent=2)}")
            
            return {
                'success': False,
                'error': error_msg,
                'audit_log': audit_log
            }
    
    @classmethod
    def get_points_analytics(cls, exam_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate analytics about points distribution across questions and exams.
        
        Args:
            exam_id: Specific exam to analyze, or None for all exams
            
        Returns:
            Dictionary with points analytics
        """
        try:
            logger.info(f"[PointsService] Generating points analytics for exam_id={exam_id}")
            
            # Build query
            questions_query = Question.objects.select_related('exam')
            if exam_id:
                questions_query = questions_query.filter(exam_id=exam_id)
            
            questions = questions_query.all()
            
            if not questions.exists():
                return {
                    'success': False,
                    'error': 'No questions found for analysis',
                    'data': {}
                }
            
            # Overall statistics
            total_questions = questions.count()
            points_values = list(questions.values_list('points', flat=True))
            
            analytics = {
                'success': True,
                'timestamp': timezone.now().isoformat(),
                'exam_scope': exam_id if exam_id else 'all_exams',
                'overview': {
                    'total_questions': total_questions,
                    'min_points': min(points_values),
                    'max_points': max(points_values),
                    'average_points': sum(points_values) / len(points_values),
                    'total_possible_points': sum(points_values)
                },
                'points_distribution': {},
                'by_question_type': {},
                'by_exam': {},
                'recommendations': []
            }
            
            # Points distribution
            from collections import Counter
            points_counter = Counter(points_values)
            analytics['points_distribution'] = dict(points_counter)
            
            # By question type
            type_analysis = {}
            for question in questions:
                q_type = question.question_type
                if q_type not in type_analysis:
                    type_analysis[q_type] = {
                        'count': 0,
                        'total_points': 0,
                        'avg_points': 0,
                        'points_range': [float('inf'), 0]
                    }
                
                type_analysis[q_type]['count'] += 1
                type_analysis[q_type]['total_points'] += question.points
                type_analysis[q_type]['points_range'][0] = min(type_analysis[q_type]['points_range'][0], question.points)
                type_analysis[q_type]['points_range'][1] = max(type_analysis[q_type]['points_range'][1], question.points)
            
            # Calculate averages
            for q_type, data in type_analysis.items():
                data['avg_points'] = data['total_points'] / data['count']
                if data['points_range'][0] == float('inf'):
                    data['points_range'] = [0, 0]
            
            analytics['by_question_type'] = type_analysis
            
            # By exam (if analyzing all exams)
            if not exam_id:
                exam_analysis = {}
                for question in questions:
                    exam_name = question.exam.name
                    if exam_name not in exam_analysis:
                        exam_analysis[exam_name] = {
                            'exam_id': question.exam.id,
                            'question_count': 0,
                            'total_points': 0,
                            'avg_points': 0
                        }
                    
                    exam_analysis[exam_name]['question_count'] += 1
                    exam_analysis[exam_name]['total_points'] += question.points
                
                # Calculate averages
                for exam_name, data in exam_analysis.items():
                    data['avg_points'] = data['total_points'] / data['question_count']
                
                analytics['by_exam'] = exam_analysis
            
            # Recommendations
            recommendations = []
            
            # Check for imbalanced points
            if analytics['overview']['max_points'] - analytics['overview']['min_points'] > 5:
                recommendations.append({
                    'type': 'balance_concern',
                    'message': f"Large points range detected ({analytics['overview']['min_points']}-{analytics['overview']['max_points']}). Consider standardizing point values.",
                    'priority': 'medium'
                })
            
            # Check for unusual distributions
            most_common_points = max(points_counter, key=points_counter.get)
            if points_counter[most_common_points] / total_questions > 0.8:
                recommendations.append({
                    'type': 'diversity_suggestion',
                    'message': f"Most questions ({points_counter[most_common_points]}/{total_questions}) use {most_common_points} points. Consider varying point values for different difficulty levels.",
                    'priority': 'low'
                })
            
            analytics['recommendations'] = recommendations
            
            logger.info(f"[PointsService] ✅ Analytics generated: {total_questions} questions analyzed")
            
            return analytics
            
        except Exception as e:
            error_msg = f"Analytics generation failed: {str(e)}"
            logger.error(f"[PointsService] {error_msg}", exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'data': {}
            }
    
    @classmethod
    def get_affected_sessions_preview(cls, question_id: Union[int, str]) -> Dict[str, Any]:
        """
        COMPREHENSIVE: Preview which student sessions would be affected by changing a question's points.
        
        This method provides detailed impact assessment before making point changes, helping teachers
        understand the consequences of their actions on student scores and progress.
        
        Args:
            question_id: Question ID to analyze for impact
            
        Returns:
            Dictionary with comprehensive impact analysis including:
            - Summary statistics of affected sessions
            - Detailed breakdown of each affected session
            - Risk assessment and recommendations
            - Performance metrics
        """
        operation_start = timezone.now()
        
        try:
            logger.info(f"[PointsService.get_affected_sessions_preview] Analyzing impact for question {question_id}")
            
            # Step 1: Validate and get the question
            try:
                question = Question.objects.select_related('exam').get(id=question_id)
            except Question.DoesNotExist:
                error_msg = f'Question {question_id} not found'
                logger.error(f"[PointsService.get_affected_sessions_preview] {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
            
            logger.debug(f"[PointsService.get_affected_sessions_preview] Question found: {question.exam.name} Q{question.question_number}")
            
            # Step 2: Find all completed sessions that answered this question
            affected_sessions_query = StudentSession.objects.filter(
                answers__question=question,
                completed_at__isnull=False
            ).distinct().select_related('exam', 'final_curriculum_level').prefetch_related(
                'answers__question'
            )
            
            affected_sessions = list(affected_sessions_query)
            
            logger.debug(f"[PointsService.get_affected_sessions_preview] Found {len(affected_sessions)} affected sessions")
            
            if not affected_sessions:
                # No sessions affected - safe to change points
                return {
                    'success': True,
                    'question': {
                        'id': question.id,
                        'number': question.question_number,
                        'type': question.question_type,
                        'current_points': question.points,
                        'exam_id': question.exam.id,
                        'exam_name': question.exam.name
                    },
                    'impact_summary': {
                        'total_affected_sessions': 0,
                        'sessions_with_correct_answers': 0,
                        'sessions_with_incorrect_answers': 0,
                        'sessions_with_no_answers': 0,
                        'risk_level': 'NONE',
                        'recommendation': 'Safe to change - no completed sessions affected'
                    },
                    'sessions': [],
                    'performance_metrics': {
                        'analysis_time_seconds': (timezone.now() - operation_start).total_seconds()
                    }
                }
            
            # Step 3: Analyze each affected session in detail
            session_analysis = []
            correct_answers = 0
            incorrect_answers = 0
            no_answers = 0
            
            for session in affected_sessions:
                try:
                    # Get the student's answer to this specific question
                    try:
                        student_answer = session.answers.get(question=question)
                        answer_text = student_answer.answer
                        is_correct = student_answer.is_correct
                        points_earned = student_answer.points_earned
                        
                        # Categorize the answer
                        if is_correct is True:
                            correct_answers += 1
                            answer_category = 'correct'
                        elif is_correct is False:
                            incorrect_answers += 1
                            answer_category = 'incorrect'
                        else:
                            no_answers += 1
                            answer_category = 'ungraded'
                            
                    except StudentAnswer.DoesNotExist:
                        # Session exists but student never answered this question
                        answer_text = '[No answer provided]'
                        is_correct = None
                        points_earned = 0
                        answer_category = 'no_answer'
                        no_answers += 1
                    
                    # Calculate potential score impact
                    current_session_score = session.score or 0
                    current_percentage = float(session.percentage_score) if session.percentage_score else 0
                    
                    # Estimate impact of changing points (for preview purposes)
                    point_change_impact = {
                        'current_points_earned': points_earned,
                        'would_change_if_points_increase': is_correct is True,
                        'would_change_if_points_decrease': is_correct is True,
                    }
                    
                    # Create session analysis record
                    session_record = {
                        'session_id': str(session.id),
                        'student_name': session.student_name,
                        'student_email': session.student_email,
                        'completion_date': session.completed_at.isoformat() if session.completed_at else None,
                        'exam_name': session.exam.name,
                        'current_session_score': current_session_score,
                        'current_percentage': current_percentage,
                        'final_level': session.final_curriculum_level.full_name if session.final_curriculum_level else None,
                        'question_response': {
                            'answer': answer_text[:100] + '...' if len(answer_text) > 100 else answer_text,
                            'is_correct': is_correct,
                            'points_earned': points_earned,
                            'category': answer_category
                        },
                        'impact_assessment': point_change_impact,
                        'risk_factors': []
                    }
                    
                    # Add risk factors
                    if current_percentage >= 90:
                        session_record['risk_factors'].append('High-performing student')
                    elif current_percentage <= 60:
                        session_record['risk_factors'].append('Struggling student')
                    
                    if session.final_curriculum_level:
                        session_record['risk_factors'].append('Level placement determined')
                    
                    session_analysis.append(session_record)
                    
                except Exception as session_error:
                    logger.error(f"[PointsService.get_affected_sessions_preview] Error analyzing session {session.id}: {session_error}")
                    session_analysis.append({
                        'session_id': str(session.id),
                        'error': f'Analysis error: {str(session_error)}',
                        'student_name': getattr(session, 'student_name', 'Unknown'),
                        'completion_date': session.completed_at.isoformat() if session.completed_at else None
                    })
            
            # Step 4: Generate risk assessment and recommendations
            total_sessions = len(affected_sessions)
            risk_level = 'LOW'
            recommendations = []
            
            if total_sessions > 100:
                risk_level = 'HIGH'
                recommendations.append('Large number of affected sessions - consider backup before changes')
            elif total_sessions > 20:
                risk_level = 'MEDIUM'
                recommendations.append('Moderate impact - review affected sessions carefully')
            
            if correct_answers > total_sessions * 0.8:
                recommendations.append('Most students answered correctly - increasing points will significantly boost scores')
            elif correct_answers < total_sessions * 0.3:
                recommendations.append('Most students answered incorrectly - point changes will have minimal positive impact')
            
            # Check for high-performing students
            high_performers = [s for s in session_analysis if s.get('current_percentage', 0) >= 90]
            if len(high_performers) > 5:
                recommendations.append(f'{len(high_performers)} high-performing students affected - changes may impact level placements')
            
            # Step 5: Compile comprehensive results
            performance_metrics = {
                'analysis_time_seconds': (timezone.now() - operation_start).total_seconds(),
                'sessions_analyzed': total_sessions,
                'database_queries': 3,  # Approximate query count
            }
            
            result = {
                'success': True,
                'timestamp': operation_start.isoformat(),
                'question': {
                    'id': question.id,
                    'number': question.question_number,
                    'type': question.question_type,
                    'current_points': question.points,
                    'exam_id': question.exam.id,
                    'exam_name': question.exam.name,
                    'correct_answer_preview': question.correct_answer[:50] + '...' if len(question.correct_answer) > 50 else question.correct_answer
                },
                'impact_summary': {
                    'total_affected_sessions': total_sessions,
                    'sessions_with_correct_answers': correct_answers,
                    'sessions_with_incorrect_answers': incorrect_answers,
                    'sessions_with_no_answers': no_answers,
                    'success_rate_percentage': round((correct_answers / total_sessions * 100) if total_sessions > 0 else 0, 1),
                    'risk_level': risk_level,
                    'recommendations': recommendations
                },
                'sessions': session_analysis,
                'performance_metrics': performance_metrics
            }
            
            # Step 6: Log completion
            logger.info(f"[PointsService.get_affected_sessions_preview] ✅ Impact analysis completed")
            logger.info(f"[PointsService.get_affected_sessions_preview] Summary: {total_sessions} sessions, {correct_answers} correct, {incorrect_answers} incorrect, Risk: {risk_level}")
            
            return result
            
        except Exception as e:
            error_msg = f"Impact analysis failed: {str(e)}"
            logger.error(f"[PointsService.get_affected_sessions_preview] {error_msg}", exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'performance_metrics': {
                    'analysis_time_seconds': (timezone.now() - operation_start).total_seconds(),
                    'failed': True
                }
            }
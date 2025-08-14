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
        ENHANCED: Grade a short answer question with comprehensive auto-grading.
        Now handles multiple answer formats for backward compatibility.
        
        Args:
            student_answer: Student's answer (can be JSON, pipe-separated, or formatted)
            correct_answer: Correct answer(s) - single or comma/pipe-separated
            case_sensitive: Whether to check case
            
        Returns:
            True if matches any acceptable answer, False if wrong, None only if no correct_answer
        """
        logger.debug(f"[SHORT_GRADING] Student: '{student_answer}', Correct: '{correct_answer}'")
        
        if not correct_answer:
            # No automatic grading possible
            logger.debug("[SHORT_GRADING] No correct_answer provided, cannot auto-grade")
            return None
        
        # CRITICAL FIX: Handle frontend format "A: X | B: Y" conversion
        if ':' in student_answer and '|' in student_answer:
            # Frontend sends "A: A | B: A" format, convert to "A|A"
            logger.debug(f"[SHORT_GRADING] Detected frontend format: {student_answer}")
            parts = student_answer.split('|')
            values = []
            for part in parts:
                part = part.strip()
                if ':' in part:
                    # Extract value after colon
                    value = part.split(':')[1].strip()
                    values.append(value)
            if values:
                student_answer = '|'.join(values)
                logger.debug(f"[SHORT_GRADING] Converted to backend format: {student_answer}")
        
        # Check if this is a multiple short answer
        # It could have comma-separated OR pipe-separated values for multiple fields
        is_multiple_fields = False
        separator = ','
        
        if ',' in correct_answer:
            # Comma always means multiple fields for SHORT answers
            is_multiple_fields = True
            separator = ','
        elif '|' in correct_answer:
            # Pipe could mean alternatives OR multiple fields
            # Check if the parts look like answer letters (B|C) vs alternatives (cat|feline)
            parts = correct_answer.split('|')
            # If all parts are single letters, it's likely multiple fields
            if all(len(p.strip()) == 1 and p.strip().upper() in 'ABCDEFGHIJ' for p in parts):
                is_multiple_fields = True
                separator = '|'
            # Also check if it's non-letter but identical (like 111|111)
            elif len(parts) > 1 and len(set(parts)) == 1:
                is_multiple_fields = True
                separator = '|'
        
        if is_multiple_fields:
            # Multiple short answers expected
            logger.debug(f"[SHORT_GRADING] Multiple fields detected, separator: '{separator}'")
            try:
                # Try to parse student answer as JSON
                import json
                student_answers = json.loads(student_answer)
                
                # Get expected parts
                expected_parts = [part.strip() for part in correct_answer.split(separator)]
                
                # ENHANCED: Actually compare answers instead of just checking existence
                all_correct = True
                for i, expected in enumerate(expected_parts):
                    # Try to get answer by index or by key
                    student_part = None
                    if isinstance(student_answers, dict):
                        # Try various key formats
                        for key in [str(i), f'part_{i}', f'answer_{i}', chr(65+i)]:
                            if key in student_answers:
                                student_part = str(student_answers[key]).strip()
                                break
                    elif isinstance(student_answers, list) and i < len(student_answers):
                        student_part = str(student_answers[i]).strip()
                    
                    # Compare the answers
                    if student_part is None:
                        logger.debug(f"[SHORT_GRADING] Missing answer for part {i}")
                        all_correct = False
                    else:
                        # Check if answer matches (with case sensitivity option)
                        if case_sensitive:
                            is_match = student_part == expected
                        else:
                            is_match = student_part.lower() == expected.lower()
                        
                        if not is_match:
                            logger.debug(f"[SHORT_GRADING] Part {i} incorrect: '{student_part}' != '{expected}'")
                            all_correct = False
                        else:
                            logger.debug(f"[SHORT_GRADING] Part {i} correct: '{student_part}' == '{expected}'")
                
                return all_correct
                
            except (json.JSONDecodeError, TypeError) as e:
                logger.debug(f"[SHORT_GRADING] JSON parse error: {e}")
                # Try direct comparison as fallback
                if case_sensitive:
                    return student_answer.strip() == correct_answer.strip()
                else:
                    return student_answer.strip().lower() == correct_answer.strip().lower()
        else:
            # Single short answer
            # Get all acceptable answers (pipe means alternatives)
            acceptable_answers = [
                ans.strip() for ans in correct_answer.split('|')
            ]
            
            student_ans = student_answer.strip()
            
            if not case_sensitive:
                student_ans = student_ans.lower()
                acceptable_answers = [ans.lower() for ans in acceptable_answers]
            
            is_correct = student_ans in acceptable_answers
            logger.debug(f"[SHORT_GRADING] Single answer: '{student_ans}' in {acceptable_answers} = {is_correct}")
            return is_correct
    
    @staticmethod
    def grade_mixed_question(student_answer: str, correct_answer: str) -> Optional[bool]:
        """
        ENHANCED: Grade MIXED questions by evaluating only MCQ/SHORT sub-parts.
        LONG sub-parts are ignored. Uses all-or-nothing scoring.
        
        Handles complex JSON formats like:
        [{"type":"Multiple Choice","value":"B,C"}, {"type":"Short Answer","value":"a"}]
        
        Args:
            student_answer: JSON string with sub-part answers
            correct_answer: Expected answers for sub-parts
            
        Returns:
            True if ALL gradable parts correct, False otherwise, None if no gradable parts
        """
        import json
        
        logger.debug(f"[MIXED_GRADING] Starting evaluation")
        logger.debug(f"[MIXED_GRADING] Student answer: {student_answer[:100]}...")
        logger.debug(f"[MIXED_GRADING] Correct answer: {correct_answer[:100]}...")
        
        if not correct_answer or not student_answer:
            logger.debug("[MIXED_GRADING] Missing answer data")
            return False
        
        # CRITICAL FIX: Handle frontend format "A: X | B: Y" conversion for MIXED
        if ':' in student_answer and '|' in student_answer and not student_answer.startswith('['):
            # Frontend sends "A: B,C | B: B,C" format, convert to JSON array
            logger.debug(f"[MIXED_GRADING] Detected frontend format: {student_answer}")
            parts = student_answer.split('|')
            formatted_answers = []
            for part in parts:
                part = part.strip()
                if ':' in part:
                    # Extract value after colon
                    value = part.split(':')[1].strip()
                    formatted_answers.append({
                        "type": "Multiple Choice",
                        "value": value
                    })
            if formatted_answers:
                student_answer = json.dumps(formatted_answers)
                logger.debug(f"[MIXED_GRADING] Converted to backend format: {student_answer}")
        
        # Special case: if answers are identical strings, it's correct
        if student_answer.strip() == correct_answer.strip():
            logger.debug("[MIXED_GRADING] Exact match - returning True")
            return True
        
        try:
            # Parse student answers
            if isinstance(student_answer, str):
                student_data = json.loads(student_answer)
            else:
                student_data = student_answer
            
            # Parse correct answers
            if isinstance(correct_answer, str):
                if correct_answer.startswith('['):
                    # Array format with type/value objects
                    correct_data = json.loads(correct_answer)
                elif correct_answer.startswith('{'):
                    # Object format
                    correct_data = json.loads(correct_answer)
                else:
                    # Simple format like "A,B,C" or "A|B|C"
                    parts = correct_answer.replace('|', ',').split(',')
                    correct_data = [{'value': part.strip()} for part in parts]
            else:
                correct_data = correct_answer
            
            # Handle array of objects with type/value format
            if isinstance(correct_data, list) and isinstance(student_data, list):
                gradable_parts = []
                all_correct = True
                
                # Compare each element
                for i, correct_item in enumerate(correct_data):
                    if i >= len(student_data):
                        logger.debug(f"[MIXED_GRADING] Missing student answer at index {i}")
                        all_correct = False
                        continue
                    
                    student_item = student_data[i]
                    
                    # Extract type and value
                    correct_type = correct_item.get('type', '') if isinstance(correct_item, dict) else ''
                    correct_value = correct_item.get('value', correct_item) if isinstance(correct_item, dict) else correct_item
                    
                    student_type = student_item.get('type', '') if isinstance(student_item, dict) else ''
                    student_value = student_item.get('value', student_item) if isinstance(student_item, dict) else student_item
                    
                    # Skip LONG answer types
                    if correct_type.lower() == 'long answer' or len(str(correct_value)) > 50:
                        logger.debug(f"[MIXED_GRADING] Skipping LONG part at index {i}")
                        continue
                    
                    # This is a gradable part
                    gradable_parts.append(i)
                    
                    # Compare values (case-insensitive for MCQ/SHORT)
                    if str(student_value).strip().upper() != str(correct_value).strip().upper():
                        logger.debug(f"[MIXED_GRADING] Part {i} incorrect: '{student_value}' != '{correct_value}'")
                        all_correct = False
                    else:
                        logger.debug(f"[MIXED_GRADING] Part {i} correct: '{student_value}' == '{correct_value}'")
                
                if not gradable_parts:
                    logger.debug("[MIXED_GRADING] No gradable parts found")
                    return None
                
                logger.debug(f"[MIXED_GRADING] Final result: {all_correct} ({len(gradable_parts)} gradable parts)")
                return all_correct
            
            # Handle dictionary format (legacy)
            elif isinstance(correct_data, dict):
                gradable_parts = []
                all_correct = True
                
                for key, correct_value in correct_data.items():
                    # Skip LONG answers
                    if len(str(correct_value)) > 50 or str(correct_value).lower() in ['essay', 'long', 'text']:
                        logger.debug(f"[MIXED_GRADING] Skipping LONG part: {key}")
                        continue
                    
                    gradable_parts.append(key)
                    
                    # Get student's answer
                    student_value = None
                    if isinstance(student_data, dict):
                        student_value = student_data.get(key)
                    elif isinstance(student_data, list):
                        try:
                            idx = int(key) if key.isdigit() else ord(key.upper()) - ord('A')
                            if 0 <= idx < len(student_data):
                                student_value = student_data[idx]
                        except (ValueError, IndexError):
                            pass
                    
                    if student_value is None:
                        logger.debug(f"[MIXED_GRADING] Missing answer for part {key}")
                        all_correct = False
                    elif str(student_value).strip().upper() != str(correct_value).strip().upper():
                        logger.debug(f"[MIXED_GRADING] Part {key} incorrect")
                        all_correct = False
                
                if not gradable_parts:
                    return None
                
                return all_correct
            
            else:
                # Unrecognized format
                logger.warning(f"[MIXED_GRADING] Unrecognized format - attempting direct comparison")
                return str(student_answer).strip() == str(correct_answer).strip()
            
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.error(f"[MIXED_GRADING] Error processing: {e}")
            # Fallback to direct comparison
            return str(student_answer).strip() == str(correct_answer).strip()
    
    @staticmethod
    def auto_grade_answer(answer: StudentAnswer) -> Dict[str, Any]:
        """
        ENHANCED: Automatically grade an answer based on question type.
        - MCQ, CHECKBOX, SHORT: Full auto-grading
        - MIXED: Auto-grade MCQ/SHORT parts only (all-or-nothing)
        - LONG: Never auto-graded (excluded from scoring)
        
        Args:
            answer: StudentAnswer instance
            
        Returns:
            Dictionary with grading results
        """
        question = answer.question
        result = {
            'is_correct': None,
            'points_earned': 0,
            'requires_manual_grading': False,
            'excluded_from_scoring': False  # New flag for LONG questions
        }
        
        logger.debug(f"[AUTO_GRADE] Q{question.question_number} ({question.question_type})")
        
        if question.question_type == 'MCQ':
            result['is_correct'] = GradingService.grade_mcq_answer(
                answer.answer,
                question.correct_answer
            )
            logger.debug(f"[AUTO_GRADE] MCQ result: {result['is_correct']}")
            
        elif question.question_type == 'CHECKBOX':
            result['is_correct'] = GradingService.grade_checkbox_answer(
                answer.answer,
                question.correct_answer
            )
            logger.debug(f"[AUTO_GRADE] CHECKBOX result: {result['is_correct']}")
            
        elif question.question_type == 'SHORT':
            result['is_correct'] = GradingService.grade_short_answer(
                answer.answer,
                question.correct_answer
            )
            # SHORT answers should always be auto-gradable now
            if result['is_correct'] is None and question.correct_answer:
                # Fallback: if we have a correct answer, attempt direct comparison
                result['is_correct'] = (
                    answer.answer.strip().upper() == question.correct_answer.strip().upper()
                )
            logger.debug(f"[AUTO_GRADE] SHORT result: {result['is_correct']}")
                
        elif question.question_type == 'MIXED':
            # Grade only MCQ/SHORT sub-parts with all-or-nothing scoring
            result['is_correct'] = GradingService.grade_mixed_question(
                answer.answer,
                question.correct_answer
            )
            if result['is_correct'] is None:
                result['requires_manual_grading'] = True
            logger.debug(f"[AUTO_GRADE] MIXED result: {result['is_correct']}")
            
        elif question.question_type == 'LONG':
            # LONG questions are excluded from auto-grading and scoring
            result['requires_manual_grading'] = True
            result['excluded_from_scoring'] = True
            logger.debug(f"[AUTO_GRADE] LONG excluded from scoring")
            
        # Calculate points (only if correct and not excluded)
        if result['is_correct'] and not result['excluded_from_scoring']:
            result['points_earned'] = question.points
            
        return result
    
    @staticmethod
    @transaction.atomic
    def grade_session(
        session: StudentSession,
        manual_grades: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        ENHANCED: Grade an entire session with NEW scoring policy.
        
        CRITICAL CHANGES:
        - LONG questions are EXCLUDED from total_possible calculation
        - SHORT questions are fully auto-graded
        - MIXED questions use all-or-nothing grading for MCQ/SHORT parts only
        
        Args:
            session: Student session to grade
            manual_grades: Dictionary of {question_id: {'is_correct': bool, 'points': int}}
            
        Returns:
            Summary of grading results with adjusted scoring
        """
        console_group = f"[GradingService.grade_session] Session {session.id}"
        logger.info(f"{console_group} - Starting ENHANCED grading (LONG excluded)")
        
        total_score = 0
        total_possible = 0
        total_possible_including_long = 0  # Track for comparison
        auto_graded = 0
        manual_graded = 0
        requires_manual = []
        excluded_questions = []  # Track LONG questions
        
        # Detailed breakdown for debugging
        question_breakdown = {
            'MCQ': {'score': 0, 'possible': 0, 'count': 0, 'auto_graded': 0},
            'SHORT': {'score': 0, 'possible': 0, 'count': 0, 'auto_graded': 0},
            'LONG': {'score': 0, 'possible': 0, 'count': 0, 'excluded': True},
            'MIXED': {'score': 0, 'possible': 0, 'count': 0, 'auto_graded': 0},
            'CHECKBOX': {'score': 0, 'possible': 0, 'count': 0, 'auto_graded': 0}
        }
        
        logger.info(f"{console_group} - Processing {session.answers.count()} answers")
        
        for answer in session.answers.select_related('question').all():
            question_id = answer.question.id
            question_type = answer.question.question_type
            question_points = answer.question.points
            
            logger.debug(
                f"{console_group} - Q{answer.question.question_number} "
                f"({question_type}): {question_points} points, "
                f"Answer: '{answer.answer[:50]}...'" if answer.answer else "No answer"
            )
            
            # Check for manual grade first
            if manual_grades and question_id in manual_grades:
                grade_info = manual_grades[question_id]
                answer.is_correct = grade_info.get('is_correct')
                answer.points_earned = grade_info.get('points', 0)
                manual_graded += 1
                logger.debug(f"{console_group} - Q{answer.question.question_number}: Manual grade applied")
            else:
                # Auto grade with enhanced logic
                grade_result = GradingService.auto_grade_answer(answer)
                answer.is_correct = grade_result['is_correct']
                answer.points_earned = grade_result['points_earned']
                
                # Check if excluded from scoring (LONG questions)
                if grade_result.get('excluded_from_scoring', False):
                    excluded_questions.append({
                        'question_id': question_id,
                        'question_number': answer.question.question_number,
                        'question_type': question_type,
                        'points': question_points
                    })
                    logger.info(
                        f"{console_group} - Q{answer.question.question_number} ({question_type}): "
                        f"EXCLUDED from scoring ({question_points} points not counted)"
                    )
                elif grade_result['requires_manual_grading']:
                    requires_manual.append({
                        'question_id': question_id,
                        'question_number': answer.question.question_number,
                        'question_type': answer.question.question_type
                    })
                    logger.debug(f"{console_group} - Q{answer.question.question_number}: Requires manual grading")
                else:
                    auto_graded += 1
                    logger.debug(
                        f"{console_group} - Q{answer.question.question_number}: "
                        f"Auto-graded: {answer.points_earned}/{question_points} "
                        f"(Correct: {answer.is_correct})"
                    )
            
            answer.save()
            
            # CRITICAL: Exclude LONG questions from total_possible
            if question_type == 'LONG':
                # LONG questions do NOT contribute to total_possible
                total_possible_including_long += question_points
                logger.info(
                    f"{console_group} - LONG question excluded: "
                    f"Q{answer.question.question_number} ({question_points} points not in denominator)"
                )
            else:
                # All other question types contribute to scoring
                total_possible += question_points
                total_score += answer.points_earned
                logger.debug(
                    f"{console_group} - Added to scoring: "
                    f"{answer.points_earned}/{question_points} points"
                )
            
            # Track breakdown by question type for debugging
            if question_type in question_breakdown:
                question_breakdown[question_type]['score'] += answer.points_earned
                question_breakdown[question_type]['possible'] += question_points
                question_breakdown[question_type]['count'] += 1
                if not grade_result.get('requires_manual_grading', False) and question_type != 'LONG':
                    question_breakdown[question_type]['auto_graded'] += 1
        
        # Log detailed breakdown for debugging
        logger.info(f"{console_group} - Question Type Breakdown:")
        for q_type, data in question_breakdown.items():
            if data['count'] > 0:
                if q_type == 'LONG':
                    logger.info(
                        f"  {q_type}: {data['count']} questions, {data['possible']} points "
                        f"[EXCLUDED FROM SCORING]"
                    )
                else:
                    type_percentage = (data['score'] / data['possible'] * 100) if data['possible'] > 0 else 0
                    logger.info(
                        f"  {q_type}: {data['score']}/{data['possible']} points "
                        f"({type_percentage:.1f}%) across {data['count']} questions "
                        f"[{data.get('auto_graded', 0)} auto-graded]"
                    )
        
        # Calculate percentage score (excluding LONG questions)
        percentage_score = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        # Update session score
        session.score = total_score
        session.percentage_score = percentage_score
        session.save()
        
        # Log comprehensive results
        logger.info(f"{console_group} - " + "=" * 50)
        logger.info(
            f"{console_group} - FINAL RESULTS (LONG EXCLUDED):"
        )
        logger.info(
            f"{console_group} - Score: {total_score}/{total_possible} = {percentage_score:.2f}%"
        )
        logger.info(
            f"{console_group} - (Would be {total_score}/{total_possible_including_long} "
            f"= {(total_score/total_possible_including_long*100) if total_possible_including_long > 0 else 0:.2f}% "
            f"if LONG included)"
        )
        logger.info(
            f"{console_group} - Auto-graded: {auto_graded}, Manual: {manual_graded}, "
            f"Needs manual: {len(requires_manual)}, Excluded: {len(excluded_questions)}"
        )
        logger.info(f"{console_group} - " + "=" * 50)
        
        # Warnings for edge cases
        if total_possible == 0:
            logger.warning(
                f"{console_group} - WARNING: total_possible is 0! "
                f"This means all questions are LONG type or no questions exist."
            )
        
        if percentage_score > 100:
            logger.warning(
                f"{console_group} - WARNING: Percentage over 100% ({percentage_score:.2f}%), "
                f"check for calculation error"
            )
        
        if len(excluded_questions) > 0:
            logger.info(
                f"{console_group} - LONG questions excluded from scoring: "
                f"{[q['question_number'] for q in excluded_questions]}"
            )
        
        return {
            'total_score': total_score,
            'total_possible': total_possible,
            'total_possible_including_long': total_possible_including_long,
            'percentage_score': float(percentage_score),
            'auto_graded': auto_graded,
            'manual_graded': manual_graded,
            'requires_manual_grading': requires_manual,
            'excluded_questions': excluded_questions,
            'is_complete': len(requires_manual) == 0,
            'question_breakdown': question_breakdown
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
    
    @staticmethod
    def get_detailed_results(session_id: str) -> Dict[str, Any]:
        """
        Get detailed results for a session.
        Alias for get_session_analytics to maintain compatibility.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with detailed results
        """
        from ..models import StudentSession
        session = StudentSession.objects.get(id=session_id)
        return GradingService.get_session_analytics(session)
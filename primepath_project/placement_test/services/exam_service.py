"""
Service for exam management and operations.
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from core.exceptions import ValidationException, ExamConfigurationException
from core.constants import DEFAULT_OPTIONS_COUNT, DEFAULT_QUESTION_POINTS
from ..models import PlacementExam, Question, PlacementAudioFile
# Backward compatibility aliases
Exam = PlacementExam  
AudioFile = PlacementAudioFile
import logging

logger = logging.getLogger(__name__)


class ExamService:
    """Handles exam creation, management, and question operations."""
    
    @staticmethod
    @transaction.atomic
    def create_exam(
        exam_data: Dict[str, Any],
        pdf_file: Optional[UploadedFile] = None,
        audio_files: Optional[List[UploadedFile]] = None,
        audio_names: Optional[List[str]] = None
    ) -> Exam:
        """
        Create a new exam with associated files.
        
        Args:
            exam_data: Dictionary containing exam information
            pdf_file: PDF file upload
            audio_files: List of audio file uploads
            audio_names: List of display names for audio files
            
        Returns:
            Created Exam instance
        """
        import logging
        import json
        
        logger = logging.getLogger(__name__)
        
        # CRITICAL: Validate PDF file before creating exam - PDF IS REQUIRED
        ExamService.validate_pdf_file(pdf_file)  # This will raise ValidationException if pdf_file is None
        ExamService.log_pdf_save_attempt(None, pdf_file, "before_create")
        
        # Create the exam
        exam = Exam.objects.create(
            name=exam_data['name'],
            curriculum_level_id=exam_data.get('curriculum_level_id'),
            pdf_file=pdf_file,
            timer_minutes=exam_data.get('timer_minutes', 60),
            total_questions=exam_data['total_questions'],
            default_options_count=exam_data.get('default_options_count', DEFAULT_OPTIONS_COUNT),
            passing_score=exam_data.get('passing_score', 0),
            pdf_rotation=exam_data.get('pdf_rotation', 0),  # Add PDF rotation field
            created_by=exam_data.get('created_by'),
            is_active=exam_data.get('is_active', True)
        )
        
        # Log successful exam object creation with PDF validation
        if pdf_file:
            ExamService.log_pdf_save_attempt(exam, pdf_file, "after_save")
        
        console_log = {
            "service": "ExamService",
            "action": "placement_exam_created",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "pdf_file_path": exam.pdf_file.name if exam.pdf_file else None,
            "pdf_rotation": exam.pdf_rotation,
            "pdf_validation_passed": bool(pdf_file)
        }
        logger.info(f"[PLACEMENT_EXAM_CREATED] {json.dumps(console_log)}")
        print(f"[PLACEMENT_EXAM_CREATED] {json.dumps(console_log)}")
        
        # Create placeholder questions
        ExamService.create_questions_for_exam(exam)
        
        # Handle audio files
        if audio_files:
            ExamService.attach_audio_files(exam, audio_files, audio_names or [])
        
        logger.info(
            f"Created exam {exam.id}: {exam.name}",
            extra={'exam_id': str(exam.id), 'total_questions': exam.total_questions}
        )
        
        return exam
    
    @staticmethod
    def create_questions_for_exam(exam: Exam) -> List[Question]:
        """
        Create placeholder questions for an exam.
        
        Args:
            exam: Exam instance
            
        Returns:
            List of created Question instances
        """
        existing_numbers = set(
            exam.questions.values_list('question_number', flat=True)
        )
        
        questions_to_create = []
        for num in range(1, exam.total_questions + 1):
            if num not in existing_numbers:
                questions_to_create.append(
                    Question(
                        exam=exam,
                        question_number=num,
                        question_type='MCQ',  # Default type
                        correct_answer='',
                        points=DEFAULT_QUESTION_POINTS,
                        options_count=exam.default_options_count
                    )
                )
        
        created_questions = Question.objects.bulk_create(questions_to_create)
        
        logger.info(
            f"Created {len(created_questions)} questions for exam {exam.id}"
        )
        
        return created_questions
    
    @staticmethod
    def attach_audio_files(
        exam: Exam,
        audio_files: List[UploadedFile],
        audio_names: List[str]
    ) -> List[AudioFile]:
        """
        Attach audio files to an exam.
        
        Args:
            exam: Exam instance
            audio_files: List of audio file uploads
            audio_names: List of display names
            
        Returns:
            List of created AudioFile instances
        """
        audio_objects = []
        
        for index, audio_file in enumerate(audio_files):
            name = (
                audio_names[index] 
                if index < len(audio_names) 
                else f"Audio {index + 1}"
            )
            
            audio_obj = AudioFile(
                exam=exam,
                audio_file=audio_file,
                name=name,
                order=index + 1,
                start_question=0,  # 0 indicates unassigned
                end_question=0     # 0 indicates unassigned
            )
            audio_objects.append(audio_obj)
        
        created_audio = AudioFile.objects.bulk_create(audio_objects)
        
        logger.info(
            f"Attached {len(created_audio)} audio files to exam {exam.id}"
        )
        
        return created_audio
    
    @staticmethod
    @transaction.atomic
    def update_exam_questions(
        exam: Exam,
        questions_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update questions for an exam with types and answers.
        
        Args:
            exam: Exam instance
            questions_data: List of question data dictionaries
            
        Returns:
            Summary of updates
        """
        updated_count = 0
        created_count = 0
        
        for q_data in questions_data:
            question_id = q_data.get('id')
            
            if question_id:
                # Update existing question
                try:
                    question = Question.objects.get(id=question_id, exam=exam)
                    question.question_type = q_data.get('question_type', 'MCQ')
                    question.correct_answer = q_data.get('correct_answer', '')
                    
                    # CRITICAL FIX: Handle points update from Save All
                    if 'points' in q_data:
                        new_points = q_data['points']
                        # Validate points range
                        if isinstance(new_points, (int, str)):
                            try:
                                points_value = int(new_points)
                                if 1 <= points_value <= 10:
                                    old_points = question.points
                                    question.points = points_value
                                    logger.info(
                                        f"[ExamService] Updated points for Q{question.question_number}: "
                                        f"{old_points} -> {points_value}"
                                    )
                                else:
                                    logger.warning(
                                        f"[ExamService] Invalid points value for Q{question.question_number}: "
                                        f"{points_value} (must be 1-10)"
                                    )
                            except (ValueError, TypeError) as e:
                                logger.error(
                                    f"[ExamService] Error parsing points for Q{question.question_number}: "
                                    f"{new_points} - {e}"
                                )
                    else:
                        logger.debug(
                            f"[ExamService] No points update for Q{question.question_number}, "
                            f"keeping existing value: {question.points}"
                        )
                    
                    # Calculate correct options_count based on answer data
                    if question.question_type in ['SHORT', 'LONG', 'MIXED']:
                        # For SHORT/LONG/MIXED, calculate from actual answer data
                        calculated_count = ExamService._calculate_options_count(
                            question.question_type, 
                            question.correct_answer
                        )
                        question.options_count = calculated_count
                    elif question.question_type in ['MCQ', 'CHECKBOX'] and 'options_count' in q_data:
                        # For MCQ/CHECKBOX, use provided value
                        question.options_count = q_data['options_count']
                    
                    question.save()
                    updated_count += 1
                    
                except Question.DoesNotExist:
                    logger.warning(
                        f"Question {question_id} not found for exam {exam.id}"
                    )
            else:
                # Create new question
                question_num = int(q_data.get('question_number'))
                question_type = q_data.get('question_type', 'MCQ')
                correct_answer = q_data.get('correct_answer', '')
                
                # Calculate options_count for SHORT/LONG/MIXED questions
                if question_type in ['SHORT', 'LONG', 'MIXED']:
                    options_count = ExamService._calculate_options_count(
                        question_type, 
                        correct_answer
                    )
                else:
                    options_count = q_data.get('options_count', DEFAULT_OPTIONS_COUNT)
                
                Question.objects.update_or_create(
                    exam=exam,
                    question_number=question_num,
                    defaults={
                        'question_type': question_type,
                        'correct_answer': correct_answer,
                        'points': q_data.get('points', DEFAULT_QUESTION_POINTS),
                        'options_count': options_count
                    }
                )
                created_count += 1
        
        logger.info(
            f"Updated exam {exam.id}: {updated_count} updated, {created_count} created"
        )
        
        return {
            'updated': updated_count,
            'created': created_count,
            'total': len(questions_data)
        }
    
    @staticmethod
    def get_next_version_number(curriculum_level_id: int, date_str: str = None) -> int:
        """
        Get the next available version number for a curriculum level on a specific date.
        Only returns version number if there are existing uploads for the same level on the same day.
        
        Args:
            curriculum_level_id: Curriculum level ID
            date_str: Date in YYMMDD format (if None, uses today)
            
        Returns:
            Next available version number (2, 3, etc.) or None if no version needed
        """
        from datetime import datetime
        
        # Get today's date in YYMMDD format if not provided
        if not date_str:
            date_str = datetime.now().strftime('%y%m%d')
        
        # Look for exams with the new naming pattern for this level and date
        existing_exams = Exam.objects.filter(
            curriculum_level_id=curriculum_level_id,
            name__contains=f'_{date_str}'  # Contains today's date
        ).values_list('name', flat=True)
        
        # Check if any exam exists for this level and date
        exams_today = []
        for exam_name in existing_exams:
            # Check if it matches our date pattern
            if f'_{date_str}' in exam_name:
                exams_today.append(exam_name)
        
        if not exams_today:
            # No exams for this level today, no version needed
            return None
        
        # Find the highest version number
        max_version = 1
        for exam_name in exams_today:
            # Check for version pattern _v2, _v3, etc.
            if f'_{date_str}_v' in exam_name:
                try:
                    version_part = exam_name.split(f'_{date_str}_v')[-1]
                    version_num = int(version_part.split('_')[0]) if '_' in version_part else int(version_part)
                    max_version = max(max_version, version_num)
                except (ValueError, IndexError):
                    continue
        
        # Return the next version number
        return max_version + 1
    
    @staticmethod
    def get_next_version_letter(curriculum_level_id: int) -> str:
        """
        DEPRECATED: Kept for backward compatibility.
        Get the next available version letter for a curriculum level.
        
        Args:
            curriculum_level_id: Curriculum level ID
            
        Returns:
            Next available version letter (a-z)
        """
        existing_exams = Exam.objects.filter(
            curriculum_level_id=curriculum_level_id,
            name__regex=r'^\[PlacementTest\].*_v_[a-z]$'
        ).values_list('name', flat=True)
        
        used_versions = set()
        for exam_name in existing_exams:
            if '_v_' in exam_name:
                version = exam_name.split('_v_')[-1]
                if len(version) == 1 and version.isalpha() and version.islower():
                    used_versions.add(version)
        
        # Find next available letter
        for i in range(26):  # a-z
            candidate = chr(ord('a') + i)
            if candidate not in used_versions:
                return candidate
        
        # If all letters used, raise exception
        raise ExamConfigurationException(
            "All version letters (a-z) have been used for this curriculum level"
        )
    
    @staticmethod
    @transaction.atomic
    def delete_exam(exam: Exam) -> None:
        """
        Delete an exam and all associated files.
        
        Args:
            exam: Exam instance to delete
        """
        exam_name = exam.name
        exam_id = exam.id
        
        # Delete associated files
        if exam.pdf_file:
            exam.pdf_file.delete()
        
        # Delete audio files
        for audio in exam.audio_files.all():
            if audio.audio_file:
                try:
                    audio.audio_file.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete audio file: {e}")
        
        # Delete the exam (cascades to questions and audio records)
        exam.delete()
        
        logger.info(f"Deleted exam {exam_id}: {exam_name}")
    
    @staticmethod
    @transaction.atomic
    def update_audio_assignments(
        exam: Exam,
        audio_assignments: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Update audio-to-question assignments for an exam using new Question.audio_file relationship.
        
        Args:
            exam: Exam instance
            audio_assignments: Dict mapping question_number -> audio_id
            
        Returns:
            Dictionary with assignment results
        """
        updated_count = 0
        errors = []
        
        # Handle None or empty audio_assignments
        if not audio_assignments:
            audio_assignments = {}
        
        # Convert audio_assignments keys to integers and validate
        validated_assignments = {}
        for question_num_str, audio_id in audio_assignments.items():
            try:
                question_num = int(question_num_str)
                validated_assignments[question_num] = audio_id
            except (ValueError, TypeError):
                errors.append(f"Invalid question number: {question_num_str}")
                continue
        
        # First, clear all existing assignments for this exam
        from ..models import Question
        Question.objects.filter(exam=exam).update(audio_file=None)
        
        # Update questions with new audio assignments
        for question_num, audio_id in validated_assignments.items():
            try:
                # Get the question
                question = Question.objects.get(exam=exam, question_number=question_num)
                
                # Get the audio file for this exam
                audio_file = AudioFile.objects.get(id=audio_id, exam=exam)
                
                # Assign audio to question
                question.audio_file = audio_file
                question.save()
                
                updated_count += 1
                
            except Question.DoesNotExist:
                errors.append(f"Question {question_num} not found for exam {exam.id}")
            except AudioFile.DoesNotExist:
                errors.append(f"Audio file {audio_id} not found for exam {exam.id}")
            except Exception as e:
                errors.append(f"Error updating audio {audio_id} to question {question_num}: {str(e)}")
        
        logger.info(
            f"Updated audio assignments for exam {exam.id}: {updated_count} assignments updated"
        )
        
        return {
            'updated': updated_count,
            'errors': errors,
            'total_assignments': len(validated_assignments)
        }
    
    @staticmethod
    def _calculate_options_count(question_type: str, correct_answer: str) -> int:
        """
        Calculate the correct options_count based on the answer data.
        
        Args:
            question_type: Type of question (SHORT, LONG, MIXED, etc.)
            correct_answer: The answer data string
            
        Returns:
            Calculated number of options/answers
        """
        if not correct_answer:
            return 1
        
        answer = str(correct_answer).strip()
        
        # For MIXED questions with JSON structure
        if question_type == 'MIXED':
            try:
                import json
                parsed = json.loads(answer)
                if isinstance(parsed, list):
                    return max(len(parsed), 1)
            except:
                pass
        
        # For LONG questions
        if question_type == 'LONG':
            # Check for multiple parts separated by triple pipe
            if '|||' in answer:
                parts = [p.strip() for p in answer.split('|||') if p.strip()]
                return max(len(parts), 1)
        
        # For SHORT questions
        if question_type == 'SHORT':
            # Check for multiple parts separated by pipe
            if '|' in answer:
                parts = [p.strip() for p in answer.split('|') if p.strip()]
                return max(len(parts), 1)
            elif ',' in answer:
                # Check if it's letter format or actual answers
                parts = [p.strip() for p in answer.split(',') if p.strip()]
                # If all parts are single letters, it's MCQ format
                if all(len(p) == 1 and p.isalpha() for p in parts):
                    return len(parts)
                return max(len(parts), 1)
        
        # Default to 1
        return 1
    
    @staticmethod
    def get_all_exams_with_stats() -> List[Dict[str, Any]]:
        """
        Get all exams with statistics.
        
        Returns:
            List of dictionaries containing exam information and statistics
        """
        from django.db.models import Count, Q
        
        try:
            exams = Exam.objects.select_related(
                'curriculum_level',
                'curriculum_level__subprogram',
                'curriculum_level__subprogram__program'
            ).annotate(
                total_sessions=Count('sessions', distinct=True),
                completed_sessions=Count(
                    'sessions',
                    filter=Q(sessions__completed_at__isnull=False),
                    distinct=True
                ),
                total_questions_count=Count('questions', distinct=True),
                audio_files_count=Count('audio_files', distinct=True)
            ).filter(is_active=True).order_by('-created_at')
            
            exam_stats = []
            for exam in exams:
                stats = {
                    'id': str(exam.id),
                    'name': exam.name,
                    'curriculum_level': exam.curriculum_level.full_name if exam.curriculum_level else 'None',
                    'timer_minutes': exam.timer_minutes,
                    'total_questions': exam.total_questions,
                    'total_sessions': exam.total_sessions,
                    'completed_sessions': exam.completed_sessions,
                    'completion_rate': (
                        exam.completed_sessions / exam.total_sessions * 100
                        if exam.total_sessions > 0 else 0
                    ),
                    'has_pdf': bool(exam.pdf_file),
                    'audio_files_count': exam.audio_files_count,
                    'created_at': exam.created_at.isoformat() if exam.created_at else None,
                    'is_active': exam.is_active
                }
                exam_stats.append(stats)
            
            logger.info(f"Retrieved stats for {len(exam_stats)} exams")
            return exam_stats
            
        except Exception as e:
            logger.error(f"Error getting exam stats: {e}")
            return []
    
    # ========== PDF ROTATION PERSISTENCE FIX ==========
    @staticmethod
    def validate_pdf_file(pdf_file):
        """
        Enhanced PDF file validation to prevent upload failures
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not pdf_file:
            logger.error("[PDF_VALIDATION] No PDF file provided")
            raise ValidationException("PDF file is required", code="MISSING_PDF")
        
        if not pdf_file.name.lower().endswith('.pdf'):
            logger.error(f"[PDF_VALIDATION] Invalid file type: {pdf_file.name}")
            raise ValidationException("File must be a PDF", code="INVALID_FILE_TYPE")
        
        if pdf_file.size == 0:
            logger.error("[PDF_VALIDATION] Empty PDF file")
            raise ValidationException("PDF file is empty", code="EMPTY_FILE")
        
        if pdf_file.size > 10 * 1024 * 1024:  # 10MB
            logger.error(f"[PDF_VALIDATION] File too large: {pdf_file.size} bytes")
            raise ValidationException("PDF file too large (max 10MB)", code="FILE_TOO_LARGE")
        
        # Test file readability
        try:
            current_pos = pdf_file.tell()
            content = pdf_file.read()
            pdf_file.seek(current_pos)  # Reset position
            
            if len(content) == 0:
                logger.error("[PDF_VALIDATION] PDF content is empty")
                raise ValidationException("PDF file content is empty", code="EMPTY_CONTENT")
                
            logger.info(f"[PDF_VALIDATION] ✅ PDF file validated: {pdf_file.name}, {pdf_file.size} bytes")
            return True
            
        except Exception as e:
            logger.error(f"[PDF_VALIDATION] Cannot read PDF: {str(e)}")
            raise ValidationException(f"Cannot read PDF file: {str(e)}", code="READ_ERROR")
    
    @staticmethod
    def log_pdf_save_attempt(exam, pdf_file, step):
        """
        Comprehensive logging for PDF save process
        """
        import logging
        import json
        import os
        logger = logging.getLogger(__name__)
        
        log_data = {
            "action": "pdf_save_process",
            "step": step,
            "exam_id": str(exam.id) if exam else "None",
            "exam_name": exam.name if exam else "None",
            "pdf_rotation": exam.pdf_rotation if exam else "None",
            "pdf_file_name": pdf_file.name if pdf_file else "None",
            "pdf_file_size": pdf_file.size if pdf_file else 0,
        }
        
        if step == "after_save" and exam and exam.pdf_file:
            try:
                log_data.update({
                    "pdf_field_name": exam.pdf_file.name,
                    "pdf_field_url": exam.pdf_file.url,
                    "file_exists_check": os.path.exists(exam.pdf_file.path) if exam.pdf_file.name else False
                })
            except Exception as e:
                log_data["file_check_error"] = str(e)
        
        logger.info(f"[PDF_SAVE_LOG] {json.dumps(log_data)}")
        print(f"[PDF_SAVE_LOG] {json.dumps(log_data)}")
    # ========== END PDF ROTATION PERSISTENCE FIX ==========

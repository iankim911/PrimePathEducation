"""
Service for exam management and operations.
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from core.exceptions import ValidationException, ExamConfigurationException
from core.constants import DEFAULT_OPTIONS_COUNT, DEFAULT_QUESTION_POINTS
from ..models import Exam, Question, AudioFile
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
        # Create the exam
        exam = Exam.objects.create(
            name=exam_data['name'],
            curriculum_level_id=exam_data.get('curriculum_level_id'),
            pdf_file=pdf_file,
            timer_minutes=exam_data.get('timer_minutes', 60),
            total_questions=exam_data['total_questions'],
            default_options_count=exam_data.get('default_options_count', DEFAULT_OPTIONS_COUNT),
            passing_score=exam_data.get('passing_score', 0),
            created_by=exam_data.get('created_by'),
            is_active=exam_data.get('is_active', True)
        )
        
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
                start_question=1,  # Default, to be updated when assigned
                end_question=1     # Default, to be updated when assigned
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
                    
                    # Update options count for MCQ
                    if question.question_type == 'MCQ' and 'options_count' in q_data:
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
                
                Question.objects.update_or_create(
                    exam=exam,
                    question_number=question_num,
                    defaults={
                        'question_type': q_data.get('question_type', 'MCQ'),
                        'correct_answer': q_data.get('correct_answer', ''),
                        'points': q_data.get('points', DEFAULT_QUESTION_POINTS),
                        'options_count': q_data.get('options_count', DEFAULT_OPTIONS_COUNT)
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
    def get_next_version_letter(curriculum_level_id: int) -> str:
        """
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
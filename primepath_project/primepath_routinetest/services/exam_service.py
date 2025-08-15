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
        import json
        
        # Helper function to serialize dates/times
        def serialize_datetime(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, 'strftime'):
                return obj.strftime('%H:%M:%S')
            return str(obj) if obj else None
        
        # Log exam creation attempt
        console_log = {
            "service": "ExamService",
            "action": "create_exam_start",
            "exam_name": exam_data.get('name'),
            "exam_type": exam_data.get('exam_type', 'REVIEW'),
            "time_period_month": exam_data.get('time_period_month'),  # Phase 2
            "time_period_quarter": exam_data.get('time_period_quarter'),  # Phase 2
            "academic_year": exam_data.get('academic_year'),  # Phase 2
            "class_codes": exam_data.get('class_codes', []),  # Phase 3
            "class_codes_count": len(exam_data.get('class_codes', [])),  # Phase 3
            "has_instructions": bool(exam_data.get('instructions')),  # General instructions (kept at exam level)
            "curriculum_level_id": exam_data.get('curriculum_level_id'),
            "has_pdf": pdf_file is not None,
            "pdf_name": pdf_file.name if pdf_file else None,
            "audio_count": len(audio_files) if audio_files else 0,
            "note": "Scheduling now managed per class via ClassExamSchedule"
        }
        logger.info(f"[EXAM_SERVICE_CREATE] {json.dumps(console_log)}")
        print(f"[EXAM_SERVICE_CREATE] {json.dumps(console_log)}")
        
        # Create the exam
        exam = Exam.objects.create(
            name=exam_data['name'],
            exam_type=exam_data.get('exam_type', 'REVIEW'),  # Add exam type with default
            time_period_month=exam_data.get('time_period_month'),  # Phase 2: Add month
            time_period_quarter=exam_data.get('time_period_quarter'),  # Phase 2: Add quarter
            academic_year=exam_data.get('academic_year'),  # Phase 2: Add academic year
            class_codes=exam_data.get('class_codes', []),  # Phase 3: Add class codes
            instructions=exam_data.get('instructions', ''),  # General instructions (kept at exam level)
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
        
        # Log successful exam object creation
        console_log = {
            "service": "ExamService",
            "action": "exam_object_created",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "pdf_file_path": exam.pdf_file.name if exam.pdf_file else None
        }
        logger.info(f"[EXAM_SERVICE_CREATED] {json.dumps(console_log)}")
        print(f"[EXAM_SERVICE_CREATED] {json.dumps(console_log)}")
        
        # Create placeholder questions
        ExamService.create_questions_for_exam(exam)
        
        # Handle audio files
        if audio_files:
            ExamService.attach_audio_files(exam, audio_files, audio_names or [])
        
        logger.info(
            f"Created exam {exam.id}: {exam.name}",
            extra={'exam_id': str(exam.id), 'total_questions': exam.total_questions}
        )
        
        # Final success log
        console_log = {
            "service": "ExamService",
            "action": "create_exam_complete",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "questions_created": exam.total_questions,
            "audio_files_attached": len(audio_files) if audio_files else 0
        }
        logger.info(f"[EXAM_SERVICE_COMPLETE] {json.dumps(console_log)}")
        print(f"[EXAM_SERVICE_COMPLETE] {json.dumps(console_log)}")
        
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
            exam.routine_questions.values_list('question_number', flat=True)
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
            name__regex=r'^\[RoutineTest\].*_v_[a-z]$'
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
    @transaction.atomic
    def manage_student_roster(
        exam: Exam,
        roster_data: List[Dict[str, Any]],
        teacher = None
    ) -> Dict[str, Any]:
        """
        Phase 5: Manage student roster assignments for an exam.
        
        Args:
            exam: Exam instance
            roster_data: List of student data dictionaries
            teacher: Teacher instance (for tracking who assigned)
            
        Returns:
            Summary of roster operations
        """
        from ..models import StudentRoster
        import json
        
        created_count = 0
        updated_count = 0
        errors = []
        
        # Log roster management start
        console_log = {
            "service": "ExamService",
            "action": "manage_roster_start",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "roster_count": len(roster_data),
            "teacher": teacher.name if teacher else None
        }
        logger.info(f"[PHASE5_ROSTER_MANAGE] {json.dumps(console_log)}")
        print(f"[PHASE5_ROSTER_MANAGE] {json.dumps(console_log)}")
        
        for student_data in roster_data:
            try:
                # Check if roster entry already exists
                roster_entry, created = StudentRoster.objects.update_or_create(
                    exam=exam,
                    student_name=student_data['student_name'],
                    student_id=student_data.get('student_id', ''),
                    defaults={
                        'class_code': student_data['class_code'],
                        'assigned_by': teacher,
                        'notes': student_data.get('notes', '')
                    }
                )
                
                if created:
                    created_count += 1
                    console_log = {
                        "action": "roster_entry_created",
                        "student": student_data['student_name'],
                        "class": student_data['class_code']
                    }
                    logger.info(f"[PHASE5_ROSTER_CREATED] {json.dumps(console_log)}")
                else:
                    updated_count += 1
                    console_log = {
                        "action": "roster_entry_updated",
                        "student": student_data['student_name'],
                        "class": student_data['class_code']
                    }
                    logger.info(f"[PHASE5_ROSTER_UPDATED] {json.dumps(console_log)}")
                    
            except Exception as e:
                error_msg = f"Error processing {student_data.get('student_name', 'unknown')}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[PHASE5_ROSTER_ERROR] {error_msg}")
        
        # Log completion
        console_log = {
            "service": "ExamService",
            "action": "manage_roster_complete",
            "exam_id": str(exam.id),
            "created": created_count,
            "updated": updated_count,
            "errors": len(errors)
        }
        logger.info(f"[PHASE5_ROSTER_COMPLETE] {json.dumps(console_log)}")
        print(f"[PHASE5_ROSTER_COMPLETE] {json.dumps(console_log)}")
        
        return {
            'created': created_count,
            'updated': updated_count,
            'errors': errors,
            'total': len(roster_data)
        }
    
    @staticmethod
    def bulk_import_roster(
        exam: Exam,
        csv_content: str,
        teacher = None
    ) -> Dict[str, Any]:
        """
        Phase 5: Bulk import student roster from CSV.
        
        Expected CSV format:
        student_name,student_id,class_code,notes
        
        Args:
            exam: Exam instance
            csv_content: CSV content as string
            teacher: Teacher instance
            
        Returns:
            Import results
        """
        import csv
        import io
        
        roster_data = []
        errors = []
        
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is line 1)
                try:
                    if not row.get('student_name'):
                        errors.append(f"Row {row_num}: Missing student name")
                        continue
                    
                    if not row.get('class_code'):
                        errors.append(f"Row {row_num}: Missing class code")
                        continue
                    
                    roster_data.append({
                        'student_name': row['student_name'].strip(),
                        'student_id': row.get('student_id', '').strip(),
                        'class_code': row['class_code'].strip(),
                        'notes': row.get('notes', '').strip()
                    })
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if roster_data:
                results = ExamService.manage_student_roster(exam, roster_data, teacher)
                results['csv_errors'] = errors
                return results
            else:
                return {
                    'created': 0,
                    'updated': 0,
                    'errors': errors,
                    'total': 0
                }
                
        except Exception as e:
            logger.error(f"[PHASE5_ROSTER_IMPORT_ERROR] CSV parsing error: {str(e)}")
            return {
                'created': 0,
                'updated': 0,
                'errors': [f"CSV parsing error: {str(e)}"],
                'total': 0
            }
    
    @staticmethod
    def update_roster_completion(
        roster_entry_id: str,
        session = None
    ) -> bool:
        """
        Phase 5: Update roster entry when student starts or completes exam.
        
        Args:
            roster_entry_id: StudentRoster entry ID
            session: StudentSession instance (optional)
            
        Returns:
            Success status
        """
        from ..models import StudentRoster
        
        try:
            roster_entry = StudentRoster.objects.get(id=roster_entry_id)
            
            if session:
                roster_entry.session = session
                roster_entry.update_completion_status()
                roster_entry.save()
                
                console_log = {
                    "action": "roster_completion_updated",
                    "roster_id": str(roster_entry_id),
                    "student": roster_entry.student_name,
                    "status": roster_entry.completion_status,
                    "session_id": str(session.id) if session else None
                }
                logger.info(f"[PHASE5_ROSTER_STATUS] {json.dumps(console_log)}")
                print(f"[PHASE5_ROSTER_STATUS] {json.dumps(console_log)}")
                
                return True
                
        except StudentRoster.DoesNotExist:
            logger.error(f"[PHASE5_ROSTER_ERROR] Roster entry {roster_entry_id} not found")
            
        return False
    
    @staticmethod
    def get_roster_report(exam: Exam) -> Dict[str, Any]:
        """
        Phase 5: Generate comprehensive roster report for an exam.
        
        Args:
            exam: Exam instance
            
        Returns:
            Detailed roster report
        """
        from ..models import StudentRoster
        import json
        
        roster_entries = StudentRoster.objects.filter(exam=exam).select_related('session')
        
        report = {
            'exam_id': str(exam.id),
            'exam_name': exam.name,
            'total_assigned': roster_entries.count(),
            'by_status': {},
            'by_class': {},
            'completion_rate': 0,
            'students': []
        }
        
        # Count by status
        for status_code, status_label in StudentRoster.COMPLETION_STATUS:
            count = roster_entries.filter(completion_status=status_code).count()
            report['by_status'][status_label] = count
        
        # Count by class
        for entry in roster_entries:
            class_code = entry.class_code
            if class_code not in report['by_class']:
                report['by_class'][class_code] = {
                    'total': 0,
                    'completed': 0,
                    'in_progress': 0,
                    'not_started': 0
                }
            
            report['by_class'][class_code]['total'] += 1
            
            if entry.completion_status == 'COMPLETED':
                report['by_class'][class_code]['completed'] += 1
            elif entry.completion_status == 'IN_PROGRESS':
                report['by_class'][class_code]['in_progress'] += 1
            elif entry.completion_status == 'NOT_STARTED':
                report['by_class'][class_code]['not_started'] += 1
            
            # Add student details
            report['students'].append({
                'name': entry.student_name,
                'id': entry.student_id,
                'class': entry.class_code,
                'status': entry.get_completion_status_display(),
                'assigned_at': entry.assigned_at.isoformat() if entry.assigned_at else None,
                'completed_at': entry.completed_at.isoformat() if entry.completed_at else None
            })
        
        # Calculate overall completion rate
        if report['total_assigned'] > 0:
            completed = report['by_status'].get('Completed', 0)
            report['completion_rate'] = round(completed / report['total_assigned'] * 100, 1)
        
        console_log = {
            "action": "roster_report_generated",
            "exam_id": str(exam.id),
            "total_students": report['total_assigned'],
            "completion_rate": report['completion_rate']
        }
        logger.info(f"[PHASE5_ROSTER_REPORT] {json.dumps(console_log)}")
        print(f"[PHASE5_ROSTER_REPORT] {json.dumps(console_log)}")
        
        return report
    
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
    
    # ==================== CLASS-SPECIFIC SCHEDULING METHODS ====================
    
    @staticmethod
    @transaction.atomic
    def create_class_schedule(
        exam: Exam,
        class_code: str,
        schedule_data: Dict[str, Any],
        teacher = None
    ) -> 'ClassExamSchedule':
        """
        Create or update a class-specific schedule for an exam.
        
        Args:
            exam: Exam instance
            class_code: Class code (e.g., 'CLASS_7A')
            schedule_data: Dictionary containing schedule information
            teacher: Teacher creating the schedule
            
        Returns:
            Created or updated ClassExamSchedule instance
        """
        from ..models import ClassExamSchedule
        import json
        
        # Log schedule creation attempt
        console_log = {
            "service": "ExamService",
            "action": "create_class_schedule_start",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "class_code": class_code,
            "scheduled_date": str(schedule_data.get('scheduled_date')) if schedule_data.get('scheduled_date') else None,
            "scheduled_start_time": str(schedule_data.get('scheduled_start_time')) if schedule_data.get('scheduled_start_time') else None,
            "scheduled_end_time": str(schedule_data.get('scheduled_end_time')) if schedule_data.get('scheduled_end_time') else None,
            "location": schedule_data.get('location'),
            "allow_late_submission": schedule_data.get('allow_late_submission', False)
        }
        logger.info(f"[CLASS_SCHEDULE_CREATE] {json.dumps(console_log)}")
        print(f"[CLASS_SCHEDULE_CREATE] {json.dumps(console_log)}")
        
        # Create or update the class schedule
        schedule, created = ClassExamSchedule.objects.update_or_create(
            exam=exam,
            class_code=class_code,
            defaults={
                'scheduled_date': schedule_data.get('scheduled_date'),
                'scheduled_start_time': schedule_data.get('scheduled_start_time'),
                'scheduled_end_time': schedule_data.get('scheduled_end_time'),
                'location': schedule_data.get('location', ''),
                'additional_instructions': schedule_data.get('additional_instructions', ''),
                'allow_late_submission': schedule_data.get('allow_late_submission', False),
                'late_submission_penalty': schedule_data.get('late_submission_penalty', 0),
                'created_by': teacher,
                'is_active': True
            }
        )
        
        action_type = "created" if created else "updated"
        console_log = {
            "service": "ExamService",
            "action": f"class_schedule_{action_type}",
            "schedule_id": str(schedule.id),
            "exam_id": str(exam.id),
            "class_code": class_code,
            "is_scheduled": schedule.is_scheduled()
        }
        logger.info(f"[CLASS_SCHEDULE_{action_type.upper()}] {json.dumps(console_log)}")
        print(f"[CLASS_SCHEDULE_{action_type.upper()}] {json.dumps(console_log)}")
        
        return schedule
    
    @staticmethod
    def bulk_create_class_schedules(
        exam: Exam,
        schedules_data: List[Dict[str, Any]],
        teacher = None
    ) -> Dict[str, Any]:
        """
        Create multiple class schedules for an exam at once.
        
        Args:
            exam: Exam instance
            schedules_data: List of schedule dictionaries
            teacher: Teacher creating the schedules
            
        Returns:
            Summary of created/updated schedules
        """
        created_count = 0
        updated_count = 0
        errors = []
        
        for schedule_data in schedules_data:
            try:
                class_code = schedule_data.get('class_code')
                if not class_code:
                    errors.append("Missing class_code in schedule data")
                    continue
                
                schedule = ExamService.create_class_schedule(
                    exam=exam,
                    class_code=class_code,
                    schedule_data=schedule_data,
                    teacher=teacher
                )
                
                if schedule._state.adding:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                error_msg = f"Error creating schedule for {class_code}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[CLASS_SCHEDULE_ERROR] {error_msg}")
        
        return {
            'created': created_count,
            'updated': updated_count,
            'errors': errors,
            'total': len(schedules_data)
        }
    
    @staticmethod
    def get_class_schedules_for_exam(exam: Exam) -> List[Dict[str, Any]]:
        """
        Get all class schedules for an exam.
        
        Args:
            exam: Exam instance
            
        Returns:
            List of schedule dictionaries
        """
        from ..models import ClassExamSchedule
        
        schedules = ClassExamSchedule.objects.filter(
            exam=exam,
            is_active=True
        ).order_by('scheduled_date', 'scheduled_start_time', 'class_code')
        
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                'id': str(schedule.id),
                'class_code': schedule.class_code,
                'class_display': schedule.get_class_display(),
                'scheduled_date': schedule.scheduled_date.isoformat() if schedule.scheduled_date else None,
                'scheduled_start_time': schedule.scheduled_start_time.strftime('%H:%M') if schedule.scheduled_start_time else None,
                'scheduled_end_time': schedule.scheduled_end_time.strftime('%H:%M') if schedule.scheduled_end_time else None,
                'location': schedule.location,
                'additional_instructions': schedule.additional_instructions,
                'allow_late_submission': schedule.allow_late_submission,
                'late_submission_penalty': schedule.late_submission_penalty,
                'schedule_display': schedule.get_schedule_display(),
                'is_scheduled': schedule.is_scheduled()
            })
        
        return schedule_list
    
    @staticmethod
    def delete_class_schedule(schedule_id: str) -> bool:
        """
        Delete a class schedule.
        
        Args:
            schedule_id: ClassExamSchedule ID
            
        Returns:
            Success status
        """
        from ..models import ClassExamSchedule
        import json
        
        try:
            schedule = ClassExamSchedule.objects.get(id=schedule_id)
            
            console_log = {
                "service": "ExamService",
                "action": "delete_class_schedule",
                "schedule_id": str(schedule_id),
                "exam_id": str(schedule.exam_id),
                "class_code": schedule.class_code
            }
            logger.info(f"[CLASS_SCHEDULE_DELETE] {json.dumps(console_log)}")
            print(f"[CLASS_SCHEDULE_DELETE] {json.dumps(console_log)}")
            
            schedule.delete()
            return True
            
        except ClassExamSchedule.DoesNotExist:
            logger.error(f"[CLASS_SCHEDULE_ERROR] Schedule {schedule_id} not found")
            return False
    
    @staticmethod
    def check_class_access(exam: Exam, class_code: str, current_time=None) -> Dict[str, Any]:
        """
        Check if a class can access an exam based on its schedule.
        
        Args:
            exam: Exam instance
            class_code: Class code to check
            current_time: Optional datetime to check against
            
        Returns:
            Dictionary with access status and message
        """
        from ..models import ClassExamSchedule
        
        try:
            schedule = ClassExamSchedule.objects.get(
                exam=exam,
                class_code=class_code,
                is_active=True
            )
            
            can_access, message = schedule.can_student_access(current_time)
            
            return {
                'can_access': can_access,
                'message': message,
                'schedule': schedule.get_schedule_display() if schedule.is_scheduled() else None,
                'late_policy': schedule.get_late_policy_display()
            }
            
        except ClassExamSchedule.DoesNotExist:
            # No schedule for this class means they can access anytime
            return {
                'can_access': True,
                'message': 'Exam available',
                'schedule': None,
                'late_policy': 'No schedule set'
            }
    
    # ==================== ROUTINETEST [RT]/[QTR] NAMING METHODS ====================
    
    @staticmethod
    def get_routinetest_curriculum_levels():
        """
        Get curriculum levels available for RoutineTest with [RT]/[QTR] naming.
        Filters curriculum levels based on RoutineTest whitelist.
        
        Returns:
            List of dictionaries with curriculum level data and display names
        """
        from ..constants import ROUTINETEST_CURRICULUM_WHITELIST
        from core.models import CurriculumLevel
        import json
        
        logger.info("[ROUTINETEST_CURRICULUM] Getting curriculum levels for RoutineTest")
        print("[ROUTINETEST_CURRICULUM] Getting curriculum levels for RoutineTest")
        
        curriculum_levels = []
        
        # Loop through whitelist and find matching curriculum levels
        for program_name, subprogram_name, level_number in ROUTINETEST_CURRICULUM_WHITELIST:
            try:
                # Find the curriculum level in database
                curriculum_level = CurriculumLevel.objects.select_related(
                    'subprogram__program'
                ).get(
                    subprogram__program__name=program_name,
                    subprogram__name__icontains=subprogram_name,  # Use icontains for flexible matching
                    level_number=level_number
                )
                
                # Get existing exam count for this level
                existing_count = Exam.objects.filter(
                    curriculum_level=curriculum_level,
                    is_active=True
                ).count()
                
                # Generate display data
                level_data = {
                    'id': curriculum_level.id,
                    'program_name': program_name,
                    'subprogram_name': subprogram_name,
                    'level_number': level_number,
                    'full_name': curriculum_level.full_name,
                    'existing_count': existing_count,
                    # Format for RoutineTest dropdown
                    'routinetest_display_preview': f"[RT/QTR] - [Time Period] - {program_name} {subprogram_name} Level {level_number}",
                    'curriculum_level': curriculum_level
                }
                
                curriculum_levels.append(level_data)
                
            except CurriculumLevel.DoesNotExist:
                # Log missing curriculum level
                console_log = {
                    "service": "ExamService", 
                    "action": "curriculum_level_not_found",
                    "program": program_name,
                    "subprogram": subprogram_name,
                    "level": level_number
                }
                logger.warning(f"[ROUTINETEST_CURRICULUM_MISSING] {json.dumps(console_log)}")
                print(f"[ROUTINETEST_CURRICULUM_MISSING] {json.dumps(console_log)}")
                continue
        
        # Log results
        console_log = {
            "service": "ExamService",
            "action": "get_routinetest_curriculum_levels",
            "total_whitelist": len(ROUTINETEST_CURRICULUM_WHITELIST),
            "found_levels": len(curriculum_levels),
            "missing_levels": len(ROUTINETEST_CURRICULUM_WHITELIST) - len(curriculum_levels)
        }
        logger.info(f"[ROUTINETEST_CURRICULUM_RESULT] {json.dumps(console_log)}")
        print(f"[ROUTINETEST_CURRICULUM_RESULT] {json.dumps(console_log)}")
        
        return curriculum_levels
    
    @staticmethod
    def generate_routinetest_exam_name(
        exam_type: str,
        time_period_month: str = None,
        time_period_quarter: str = None,
        academic_year: str = None,
        curriculum_level_id: int = None,
        include_version: bool = True
    ) -> Dict[str, str]:
        """
        Generate RoutineTest exam name with [RT]/[QTR] pattern.
        
        Args:
            exam_type: 'REVIEW' or 'QUARTERLY'
            time_period_month: Month code (e.g., 'JAN', 'FEB')
            time_period_quarter: Quarter code (e.g., 'Q1', 'Q2')
            academic_year: Year (e.g., '2025')
            curriculum_level_id: CurriculumLevel ID
            include_version: Whether to include version/date in name
            
        Returns:
            Dictionary with display_name and base_name
        """
        from core.models import CurriculumLevel
        from datetime import datetime
        import json
        
        console_log = {
            "service": "ExamService",
            "action": "generate_routinetest_exam_name",
            "exam_type": exam_type,
            "time_period_month": time_period_month,
            "time_period_quarter": time_period_quarter,
            "academic_year": academic_year,
            "curriculum_level_id": curriculum_level_id
        }
        logger.info(f"[ROUTINETEST_NAME_GEN] {json.dumps(console_log)}")
        print(f"[ROUTINETEST_NAME_GEN] {json.dumps(console_log)}")
        
        # Determine prefix
        prefix = 'RT' if exam_type == 'REVIEW' else 'QTR'
        
        # Build display name parts
        display_parts = [f"[{prefix}]"]
        base_parts = [prefix]
        
        # Add time period
        if exam_type == 'REVIEW' and time_period_month:
            # Convert month code to display name
            month_choices = dict(Exam.MONTH_CHOICES)
            month_display = month_choices.get(time_period_month, time_period_month)
            if academic_year:
                display_parts.append(f"[{month_display} {academic_year}]")
                base_parts.append(f"{time_period_month}{academic_year}")
            else:
                display_parts.append(f"[{month_display}]")
                base_parts.append(time_period_month)
                
        elif exam_type == 'QUARTERLY' and time_period_quarter:
            quarter_choices = dict(Exam.QUARTER_CHOICES)
            quarter_display = quarter_choices.get(time_period_quarter, time_period_quarter)
            if academic_year:
                display_parts.append(f"[{quarter_display} {academic_year}]")
                base_parts.append(f"{time_period_quarter}{academic_year}")
            else:
                display_parts.append(f"[{quarter_display}]")
                base_parts.append(time_period_quarter)
        
        
        # Add curriculum level
        if curriculum_level_id:
            try:
                curriculum_level = CurriculumLevel.objects.select_related(
                    'subprogram__program'
                ).get(id=curriculum_level_id)
                
                program_name = curriculum_level.subprogram.program.name
                subprogram_name = curriculum_level.subprogram.name
                level_number = curriculum_level.level_number
                
                # Clean subprogram name (remove program prefix if exists)
                clean_subprogram = subprogram_name
                if subprogram_name.startswith(program_name + ' '):
                    clean_subprogram = subprogram_name[len(program_name) + 1:]
                
                # Add to display name
                curriculum_display = f"{program_name} {clean_subprogram} Level {level_number}"
                display_parts.append(curriculum_display)
                
                # Add to base name (file-friendly)
                curriculum_base = f"{program_name}_{clean_subprogram}_Lv{level_number}".replace(" ", "_")
                base_parts.append(curriculum_base)
                
            except CurriculumLevel.DoesNotExist:
                logger.warning(f"[ROUTINETEST_NAME_GEN] Curriculum level {curriculum_level_id} not found")
        
        # Build final names
        display_name = " - ".join(display_parts)
        base_name = "_".join(base_parts)
        
        # Add version/date if requested
        final_name = base_name
        if include_version:
            date_str = datetime.now().strftime('%y%m%d')
            final_name = f"{base_name}_{date_str}"
        
        result = {
            'display_name': display_name,
            'base_name': base_name,
            'final_name': final_name,
            'prefix': prefix
        }
        
        # Log result
        console_log = {
            "service": "ExamService",
            "action": "routinetest_name_generated",
            "display_name": display_name,
            "base_name": base_name,
            "final_name": final_name
        }
        logger.info(f"[ROUTINETEST_NAME_RESULT] {json.dumps(console_log)}")
        print(f"[ROUTINETEST_NAME_RESULT] {json.dumps(console_log)}")
        
        return result
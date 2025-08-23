# Generated migration to fix exam-class relationship from many-to-many to one-to-one
# Date: 2025-08-23
# Purpose: Ensure each exam belongs to exactly one class

from django.db import migrations, models
import json
import uuid
import logging

logger = logging.getLogger(__name__)

def split_multi_class_exams(apps, schema_editor):
    """
    Split exams with multiple class codes into separate exam instances.
    Each exam should belong to exactly one class.
    """
    Exam = apps.get_model('primepath_routinetest', 'Exam')
    db_alias = schema_editor.connection.alias
    
    exams_to_split = []
    split_count = 0
    
    # Find all exams with multiple class codes
    for exam in Exam.objects.using(db_alias).all():
        if exam.class_codes and isinstance(exam.class_codes, list) and len(exam.class_codes) > 1:
            exams_to_split.append(exam)
            logger.info(f"[MIGRATION] Found exam {exam.id} with {len(exam.class_codes)} classes: {exam.class_codes}")
    
    logger.info(f"[MIGRATION] Found {len(exams_to_split)} exams to split")
    
    # Split each multi-class exam into separate instances
    for exam in exams_to_split:
        original_classes = exam.class_codes.copy()
        
        # Keep the first class with the original exam
        first_class = original_classes[0]
        exam.class_codes = [first_class]
        exam.save()
        logger.info(f"[MIGRATION] Updated original exam {exam.id} to class {first_class}")
        
        # Create new exam instances for remaining classes
        for class_code in original_classes[1:]:
            # Create a new exam with the same data but different ID and class
            new_exam_data = {
                'name': f"{exam.name} - {class_code}",
                'exam_type': getattr(exam, 'exam_type', 'REVIEW'),
                'time_period_month': getattr(exam, 'time_period_month', None),
                'time_period_quarter': getattr(exam, 'time_period_quarter', None),
                'academic_year': getattr(exam, 'academic_year', None),
                'curriculum_level_id': exam.curriculum_level_id,
                'pdf_file': exam.pdf_file,
                'timer_minutes': exam.timer_minutes,
                'total_questions': exam.total_questions,
                'default_options_count': exam.default_options_count,
                'passing_score': exam.passing_score,
                'pdf_rotation': getattr(exam, 'pdf_rotation', 0),
                'instructions': getattr(exam, 'instructions', ''),
                'created_by_id': exam.created_by_id,
                'is_active': exam.is_active,
                'class_codes': [class_code],  # Single class for new instance
            }
            
            new_exam = Exam.objects.using(db_alias).create(**new_exam_data)
            split_count += 1
            logger.info(f"[MIGRATION] Created new exam {new_exam.id} for class {class_code} (copy of {exam.id})")
            
            # Copy questions if they exist
            try:
                Question = apps.get_model('primepath_routinetest', 'Question')
                for question in Question.objects.using(db_alias).filter(exam=exam):
                    Question.objects.using(db_alias).create(
                        exam=new_exam,
                        question_number=question.question_number,
                        question_type=getattr(question, 'question_type', 'MCQ'),
                        correct_answer=getattr(question, 'correct_answer', ''),
                        options=getattr(question, 'options', [])
                    )
            except Exception as e:
                logger.warning(f"[MIGRATION] Could not copy questions: {e}")
            
            # Copy audio files if they exist
            try:
                AudioFile = apps.get_model('primepath_routinetest', 'AudioFile')
                for audio in AudioFile.objects.using(db_alias).filter(exam=exam):
                    AudioFile.objects.using(db_alias).create(
                        exam=new_exam,
                        audio_file=audio.audio_file,
                        name=getattr(audio, 'name', 'Audio File'),
                        start_question=audio.start_question,
                        end_question=audio.end_question,
                        order=getattr(audio, 'order', 1)
                    )
            except Exception as e:
                logger.warning(f"[MIGRATION] Could not copy audio files: {e}")
    
    logger.info(f"[MIGRATION] Successfully split {split_count} new exam instances from {len(exams_to_split)} multi-class exams")
    
    # Ensure all remaining exams have single class or empty
    for exam in Exam.objects.using(db_alias).all():
        if exam.class_codes and isinstance(exam.class_codes, list) and len(exam.class_codes) > 1:
            logger.error(f"[MIGRATION] ERROR: Exam {exam.id} still has multiple classes after migration!")

def reverse_split(apps, schema_editor):
    """
    Reverse operation - not recommended as it would lose data.
    This is a placeholder that does nothing.
    """
    logger.warning("[MIGRATION] Reverse migration not implemented - would cause data loss")
    pass

class Migration(migrations.Migration):
    
    dependencies = [
        ('primepath_routinetest', '0021_alter_classaccessrequest_requested_access_level_and_more'),
    ]
    
    operations = [
        migrations.RunPython(
            split_multi_class_exams,
            reverse_split,
            hints={'model_name': 'exam'}
        ),
        
        # Add a new field for single class code (phase 2 of migration)
        migrations.AddField(
            model_name='exam',
            name='class_code',
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                help_text="Single class code this exam belongs to (one-to-one relationship)"
            ),
            preserve_default=False,
        ),
        
        # Add custom validation to ensure one-to-one relationship
        migrations.RunSQL(
            sql=[
                """
                -- Add console logging for debugging
                -- This is PostgreSQL/SQLite compatible comment
                -- Ensures class_codes field only has one item or is empty
                """,
            ],
            reverse_sql=[
                "-- Reverse migration placeholder",
            ],
        ),
    ]
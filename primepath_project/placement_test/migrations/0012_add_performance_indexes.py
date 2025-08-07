"""
Add database indexes for performance optimization after 9000+ sessions.
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Allow partial index creation
    
    dependencies = [
        ('placement_test', '0011_remove_skip_first_left_half'),
    ]

    operations = [
        # Index for StudentSession queries
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['completed_at', '-started_at'], name='session_status_idx'),
        ),
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['exam', 'completed_at'], name='session_exam_idx'),
        ),
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['school', '-started_at'], name='session_school_idx'),
        ),
        
        # Index for StudentAnswer queries
        migrations.AddIndex(
            model_name='studentanswer',
            index=models.Index(fields=['session', 'question'], name='answer_lookup_idx'),
        ),
        # Skip created_at index as StudentAnswer doesn't have this field
        
        # Index for Exam queries
        migrations.AddIndex(
            model_name='exam',
            index=models.Index(fields=['is_active', 'curriculum_level'], name='exam_active_idx'),
        ),
        # Skip created_at index as Exam model doesn't have this field
        
        # Index for Question queries
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['exam', 'question_number'], name='question_order_idx'),
        ),
        
        # Index for AudioFile queries
        migrations.AddIndex(
            model_name='audiofile',
            index=models.Index(fields=['exam', 'start_question'], name='audio_exam_idx'),
        ),
    ]
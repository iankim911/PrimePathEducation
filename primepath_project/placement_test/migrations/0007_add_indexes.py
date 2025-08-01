# Generated migration for adding database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('placement_test', '0006_audiofile_name'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['started_at'], name='placement_t_started_7c5d8f_idx'),
        ),
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['grade', 'academic_rank'], name='placement_t_grade_ac_rank_idx'),
        ),
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['exam', 'completed_at'], name='placement_t_exam_comp_idx'),
        ),
        migrations.AddIndex(
            model_name='exam',
            index=models.Index(fields=['curriculum_level', 'is_active'], name='placement_t_curr_active_idx'),
        ),
        migrations.AddIndex(
            model_name='exam',
            index=models.Index(fields=['created_at'], name='placement_t_created_idx'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['exam', 'question_number'], name='placement_t_exam_qnum_idx'),
        ),
        migrations.AddIndex(
            model_name='studentanswer',
            index=models.Index(fields=['session', 'question'], name='placement_t_sess_quest_idx'),
        ),
        migrations.AddIndex(
            model_name='audiofile',
            index=models.Index(fields=['exam', 'order'], name='placement_t_exam_order_idx'),
        ),
    ]
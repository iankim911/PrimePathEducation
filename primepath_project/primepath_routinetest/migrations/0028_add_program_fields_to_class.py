# Generated manually on 2025-08-26
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primepath_routinetest', '0027_studentsession_is_teacher_preview_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='program',
            field=models.CharField(
                blank=True,
                choices=[
                    ('CORE', 'CORE'),
                    ('ASCENT', 'ASCENT'),
                    ('EDGE', 'EDGE'),
                    ('PINNACLE', 'PINNACLE')
                ],
                db_index=True,
                help_text='Program this class belongs to',
                max_length=20,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='class',
            name='subprogram',
            field=models.CharField(
                blank=True,
                help_text='Specific subprogram within the program',
                max_length=100,
                null=True
            ),
        ),
        migrations.AddIndex(
            model_name='class',
            index=models.Index(fields=['program', 'is_active'], name='routinetest_program_8a3f21_idx'),
        ),
    ]
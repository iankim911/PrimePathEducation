# Generated manually to fix ExamScheduleMatrix model reference
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('primepath_routinetest', '0019_remove_routineexam_routinetest_curricu_e7d5a3_idx_and_more'),
    ]

    operations = [
        # First, drop the old many-to-many table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS primepath_routinetest_examschedulematrix_exams;",
            reverse_sql="-- Cannot reverse this operation"
        ),
        
        # Then update the field to reference RoutineExam
        migrations.AlterField(
            model_name='examschedulematrix',
            name='exams',
            field=models.ManyToManyField(
                blank=True,
                related_name='matrix_schedules',
                to='primepath_routinetest.RoutineExam'
            ),
        ),
    ]
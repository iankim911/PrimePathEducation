# Generated manually for Day 3 Student Management

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_student'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('primepath_routinetest', '0016_alter_class_assigned_teachers_and_more'),
    ]

    operations = [
        # Create the new model with proper structure
        migrations.CreateModel(
            name='StudentEnrollment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('enrollment_date', models.DateTimeField(auto_now_add=True)),
                ('academic_year', models.CharField(default='2024-2025', max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('transferred', 'Transferred'), ('graduated', 'Graduated')], default='active', max_length=20)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='primepath_routinetest.class')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_enrollments', to='auth.user')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='core.student')),
            ],
            options={
                'db_table': 'routinetest_student_enrollment',
                'ordering': ['-enrollment_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='studentenrollment',
            unique_together={('student', 'class_assigned', 'academic_year')},
        ),
        migrations.AddIndex(
            model_name='studentenrollment',
            index=models.Index(fields=['class_assigned', 'status'], name='routinetest_class_a_4a5d5f_idx'),
        ),
        migrations.AddIndex(
            model_name='studentenrollment',
            index=models.Index(fields=['student', 'academic_year'], name='routinetest_student_c83b7e_idx'),
        ),
    ]
# Generated manually for Day 3 Student Management

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0006_examlevelmapping_unique_exam_per_mapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('current_grade_level', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('parent_phone', models.CharField(blank=True, max_length=20)),
                ('parent_email', models.EmailField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, help_text='Django user account for authentication', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['current_grade_level'], name='core_studen_current_3e8b47_idx'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['is_active'], name='core_studen_is_acti_7c8b6c_idx'),
        ),
    ]
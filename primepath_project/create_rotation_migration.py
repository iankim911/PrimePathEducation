#!/usr/bin/env python
"""Create migration file for PDF rotation field"""
import os

migration_content = '''# Generated for PDF rotation feature
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('placement_test', '0012_add_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='pdf_rotation',
            field=models.IntegerField(
                default=0, 
                validators=[
                    django.core.validators.MinValueValidator(0), 
                    django.core.validators.MaxValueValidator(270)
                ],
                help_text='PDF rotation angle in degrees (0, 90, 180, 270)'
            ),
        ),
    ]
'''

try:
    migration_path = 'placement_test/migrations/0013_exam_pdf_rotation.py'
    with open(migration_path, 'w') as f:
        f.write(migration_content)
    print(f"✅ Migration file created: {migration_path}")
except Exception as e:
    print(f"❌ Error creating migration: {e}")
    # Try alternative approach
    print(migration_content)
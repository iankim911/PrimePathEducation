"""
Migration to add KakaoTalk-related fields to Teacher model
Run: python manage.py makemigrations core
     python manage.py migrate core
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    
    dependencies = [
        ('core', '0010_add_global_teacher_access'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='teacher',
            name='is_kakao_user',
            field=models.BooleanField(default=False, help_text='User authenticated via KakaoTalk'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='profile_image_url',
            field=models.URLField(max_length=500, blank=True, null=True, help_text='Profile image from KakaoTalk'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='kakao_id',
            field=models.CharField(max_length=100, blank=True, null=True, unique=True, help_text='KakaoTalk user ID'),
        ),
    ]
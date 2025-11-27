# Generated migration for ExamLevelMapping

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('placement_test', '0001_initial'),
        ('core', '0002_alter_curriculumlevel_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamLevelMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('curriculum_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_mappings', to='core.curriculumlevel')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_mappings', to='placement_test.exam')),
            ],
            options={
                'ordering': ['curriculum_level', 'slot'],
                'unique_together': {('curriculum_level', 'exam'), ('curriculum_level', 'slot')},
            },
        ),
    ]
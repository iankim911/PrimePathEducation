# Generated migration file

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('placement_test', '0002_studentsession_parent_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='passing_score',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
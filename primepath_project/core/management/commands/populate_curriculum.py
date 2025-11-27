from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Program, SubProgram, CurriculumLevel


class Command(BaseCommand):
    help = 'Populates curriculum levels (3 levels for each subprogram)'

    def handle(self, *args, **options):
        with transaction.atomic():
            for subprogram in SubProgram.objects.all():
                for level_num in range(1, 4):
                    CurriculumLevel.objects.get_or_create(
                        subprogram=subprogram,
                        level_number=level_num,
                        defaults={
                            'description': f'{subprogram.name} Level {level_num}'
                        }
                    )
            
            total_levels = CurriculumLevel.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created curriculum levels. Total levels: {total_levels}'
                )
            )
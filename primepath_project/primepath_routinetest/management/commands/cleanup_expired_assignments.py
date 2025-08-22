"""
Management command to deactivate expired teacher assignments
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from primepath_routinetest.models import TeacherClassAssignment
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Deactivate expired temporary teacher assignments'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deactivated without making changes'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find expired assignments that are still active
        expired_assignments = TeacherClassAssignment.objects.filter(
            is_active=True,
            expires_on__isnull=False,
            expires_on__lt=timezone.now()
        )
        
        count = expired_assignments.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No expired assignments found')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {count} expired assignment(s)')
        )
        
        # Show details
        for assignment in expired_assignments:
            days_overdue = (timezone.now() - assignment.expires_on).days
            self.stdout.write(
                f'  - {assignment.teacher.name}: {assignment.get_class_code_display()} '
                f'(expired {days_overdue} days ago)'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nDry run - no changes made')
            )
        else:
            # Deactivate expired assignments
            updated = expired_assignments.update(
                is_active=False,
                notes=expired_assignments.values_list('notes', flat=True)[0] + 
                      f'\n[System: Deactivated due to expiration on {timezone.now().date()}]'
                      if expired_assignments.exists() else ''
            )
            
            # Log each deactivation
            for assignment in expired_assignments:
                assignment.is_active = False
                assignment.notes = (assignment.notes or '') + \
                    f'\n[System: Deactivated due to expiration on {timezone.now().date()}]'
                assignment.save()
                
                logger.info(
                    f'Deactivated expired assignment: {assignment.teacher.name} - '
                    f'{assignment.get_class_code_display()} (expired: {assignment.expires_on})'
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\nDeactivated {count} expired assignment(s)')
            )
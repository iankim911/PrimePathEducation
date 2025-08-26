"""
Management command to synchronize StudentProfile records with legacy Student model.
This ensures all students registered through the new system appear in class management.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from core.models import Student
from primepath_student.models import StudentProfile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronize StudentProfile records with legacy Student model'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving to database',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each student',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('STUDENT PROFILE SYNCHRONIZATION'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved\n'))
        
        # Statistics
        stats = {
            'profiles_found': 0,
            'students_created': 0,
            'students_updated': 0,
            'students_skipped': 0,
            'errors': 0
        }
        
        # Get all StudentProfiles
        profiles = StudentProfile.objects.all().select_related('user')
        stats['profiles_found'] = profiles.count()
        
        self.stdout.write(f"Found {stats['profiles_found']} StudentProfile records to process\n")
        
        for profile in profiles:
            try:
                self.stdout.write(f"\nProcessing: {profile.student_id} - {profile.get_full_name()}")
                
                # Check if legacy Student exists for this user
                legacy_student = None
                if profile.user:
                    legacy_student = Student.objects.filter(user=profile.user).first()
                
                if not legacy_student:
                    # Try to find by name as fallback
                    full_name = profile.get_full_name()
                    if full_name:
                        legacy_student = Student.objects.filter(name=full_name).first()
                
                if legacy_student:
                    # Update existing Student
                    if verbose:
                        self.stdout.write(f"  Found existing Student (ID: {legacy_student.id})")
                    
                    changes = []
                    
                    # Update fields if different
                    if legacy_student.name != (profile.get_full_name() or profile.student_id):
                        old_name = legacy_student.name
                        legacy_student.name = profile.get_full_name() or profile.student_id
                        changes.append(f"name: '{old_name}' → '{legacy_student.name}'")
                    
                    if legacy_student.user != profile.user:
                        legacy_student.user = profile.user
                        changes.append(f"user: linked to {profile.user.username}")
                    
                    grade_display = profile.get_grade_display() if profile.grade else 'Unknown'
                    if legacy_student.current_grade_level != grade_display:
                        old_grade = legacy_student.current_grade_level
                        legacy_student.current_grade_level = grade_display
                        changes.append(f"grade: '{old_grade}' → '{grade_display}'")
                    
                    if legacy_student.parent_phone != (profile.phone_number or ''):
                        legacy_student.parent_phone = profile.phone_number or ''
                        changes.append(f"phone: updated")
                    
                    if legacy_student.parent_email != (profile.user.email or ''):
                        legacy_student.parent_email = profile.user.email or ''
                        changes.append(f"email: updated")
                    
                    if profile.date_of_birth and legacy_student.date_of_birth != profile.date_of_birth:
                        legacy_student.date_of_birth = profile.date_of_birth
                        changes.append(f"DOB: updated")
                    
                    if not legacy_student.is_active:
                        legacy_student.is_active = True
                        changes.append(f"status: activated")
                    
                    if changes:
                        if not dry_run:
                            legacy_student.save()
                        stats['students_updated'] += 1
                        self.stdout.write(self.style.WARNING(f"  ✓ Updated: {', '.join(changes)}"))
                    else:
                        stats['students_skipped'] += 1
                        if verbose:
                            self.stdout.write(self.style.SUCCESS(f"  ✓ No changes needed"))
                    
                else:
                    # Create new Student
                    if verbose:
                        self.stdout.write(f"  Creating new Student record")
                    
                    student_data = {
                        'user': profile.user,
                        'name': profile.get_full_name() or profile.student_id,
                        'current_grade_level': profile.get_grade_display() if profile.grade else 'Unknown',
                        'parent_phone': profile.phone_number or '',
                        'parent_email': profile.user.email or '',
                        'date_of_birth': profile.date_of_birth,
                        'is_active': True
                    }
                    
                    if not dry_run:
                        legacy_student = Student.objects.create(**student_data)
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Created Student (ID: {legacy_student.id})"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Would create Student: {student_data['name']}"))
                    
                    stats['students_created'] += 1
                
                # Log the sync
                logger.info(f"[SYNC_STUDENT] Synced profile {profile.student_id} to legacy Student model")
                
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(self.style.ERROR(f"  ✗ Error: {str(e)}"))
                logger.error(f"[SYNC_STUDENT] Error syncing profile {profile.student_id}: {e}")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('SYNCHRONIZATION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f"\nProfiles processed: {stats['profiles_found']}")
        self.stdout.write(self.style.SUCCESS(f"  Created: {stats['students_created']}"))
        self.stdout.write(self.style.WARNING(f"  Updated: {stats['students_updated']}"))
        self.stdout.write(f"  Skipped: {stats['students_skipped']}")
        if stats['errors'] > 0:
            self.stdout.write(self.style.ERROR(f"  Errors: {stats['errors']}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN COMPLETE - No changes were saved'))
            self.stdout.write('Run without --dry-run to apply changes')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ SYNCHRONIZATION COMPLETE'))
            
            # Also log in console for debugging
            print(f"\n[STUDENT_SYNC][{datetime.now().strftime('%H:%M:%S')}] Synchronization complete:")
            print(f"  - Profiles: {stats['profiles_found']}")
            print(f"  - Created: {stats['students_created']}")
            print(f"  - Updated: {stats['students_updated']}")
            print(f"  - Skipped: {stats['students_skipped']}")
            print(f"  - Errors: {stats['errors']}")
"""
Django management command to update class codes based on curriculum mapping
Usage: python manage.py update_class_codes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import (
    CLASS_CODE_CURRICULUM_MAPPING,
    get_curriculum_for_class,
    get_program_from_class_code,
    get_subprogram_from_class_code,
    get_level_from_class_code
)
from core.models import Teacher
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Update or create classes based on the official class code mapping'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing classes with matching names',
        )
        parser.add_argument(
            '--academic-year',
            type=str,
            default='2025',
            help='Academic year for new classes (default: 2025)',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        academic_year = options['academic_year']
        
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*80}\n"
            f"CLASS CODE UPDATE UTILITY\n"
            f"{'='*80}\n"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))
        
        # Get default teacher for creation
        default_teacher = self.get_default_teacher()
        if not default_teacher and not dry_run:
            self.stdout.write(self.style.ERROR(
                "No teacher found. Please ensure at least one teacher exists."
            ))
            return
        
        # Statistics
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        self.stdout.write(f"Processing {len(CLASS_CODE_CURRICULUM_MAPPING)} class codes...\n")
        
        with transaction.atomic():
            for class_code, curriculum_level in CLASS_CODE_CURRICULUM_MAPPING.items():
                try:
                    # Extract details from curriculum
                    program = get_program_from_class_code(class_code)
                    subprogram = get_subprogram_from_class_code(class_code)
                    level = get_level_from_class_code(class_code)
                    
                    # Generate class name
                    class_name = f"{class_code} - {curriculum_level}"
                    
                    # Check if class exists
                    existing_class = Class.objects.filter(name__icontains=class_code).first()
                    
                    if existing_class:
                        if update_existing:
                            if not dry_run:
                                existing_class.name = class_name
                                existing_class.grade_level = curriculum_level
                                existing_class.section = class_code
                                existing_class.academic_year = academic_year
                                existing_class.save()
                            self.stdout.write(self.style.SUCCESS(
                                f"  ✓ Updated: {class_code} -> {curriculum_level}"
                            ))
                            updated_count += 1
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"  ⊘ Skipped: {class_code} (already exists)"
                            ))
                            skipped_count += 1
                    else:
                        # Create new class
                        if not dry_run:
                            new_class = Class.objects.create(
                                name=class_name,
                                grade_level=curriculum_level,
                                section=class_code,
                                academic_year=academic_year,
                                created_by=default_teacher,  # This is now a User instance
                                is_active=True
                            )
                            # Find associated teacher profile and assign
                            if default_teacher:
                                try:
                                    teacher = Teacher.objects.get(user=default_teacher)
                                    new_class.assigned_teachers.add(teacher)
                                except Teacher.DoesNotExist:
                                    pass  # No teacher profile for this user
                        
                        self.stdout.write(self.style.SUCCESS(
                            f"  + Created: {class_code} -> {curriculum_level}"
                        ))
                        created_count += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"  ✗ Error processing {class_code}: {str(e)}"
                    ))
                    error_count += 1
                    if not dry_run:
                        raise  # Re-raise to trigger rollback
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*80}\n"
            f"SUMMARY\n"
            f"{'='*80}\n"
        ))
        
        self.stdout.write(f"  Created:  {created_count} classes")
        self.stdout.write(f"  Updated:  {updated_count} classes")
        self.stdout.write(f"  Skipped:  {skipped_count} classes")
        self.stdout.write(f"  Errors:   {error_count} classes")
        self.stdout.write(f"  Total:    {len(CLASS_CODE_CURRICULUM_MAPPING)} class codes")
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDRY RUN COMPLETE - No changes were made.\n"
                "Run without --dry-run to apply changes."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Class codes updated successfully!"))
        
        # Show program distribution
        self.show_program_distribution()
    
    def get_default_teacher(self):
        """Get a default user for class creation"""
        # Try to find admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            return admin_user
        
        # Try to find any staff user
        staff_user = User.objects.filter(is_staff=True).first()
        if staff_user:
            return staff_user
        
        # Return any user
        return User.objects.first()
    
    def show_program_distribution(self):
        """Show distribution of classes by program"""
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*80}\n"
            f"PROGRAM DISTRIBUTION\n"
            f"{'='*80}\n"
        ))
        
        from primepath_routinetest.class_code_mapping import get_curriculum_statistics
        
        stats = get_curriculum_statistics()
        
        for program, data in stats['programs'].items():
            self.stdout.write(f"\n{program} Program: {data['class_codes']} class codes")
            # Show first 5 codes as examples
            example_codes = data['codes'][:5]
            if example_codes:
                self.stdout.write(f"  Examples: {', '.join(example_codes)}")
                if len(data['codes']) > 5:
                    self.stdout.write(f"  ... and {len(data['codes']) - 5} more")
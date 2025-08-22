"""
Management command to create dummy teachers for testing
These teachers have easily identifiable names and emails for easy removal pre-deployment
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from core.models import Teacher
from primepath_routinetest.models import Class
import random


class Command(BaseCommand):
    help = 'Creates 10 dummy teachers with identifiable test data and assigns them randomly to classes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all test teachers instead of creating them',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        if options['delete']:
            self.delete_test_teachers(dry_run=options['dry_run'])
        else:
            self.create_test_teachers(dry_run=options['dry_run'])

    def delete_test_teachers(self, dry_run=False):
        """Delete all test teachers (those with TEST_ prefix)"""
        self.stdout.write(self.style.WARNING('Deleting test teachers...'))
        
        # Find test teachers by the TEST_ prefix pattern
        test_teachers = Teacher.objects.filter(name__startswith='Test Teacher ')
        test_users = User.objects.filter(username__startswith='TEST_TEACHER_')
        
        teacher_count = test_teachers.count()
        user_count = test_users.count()
        
        self.stdout.write(f"Found {teacher_count} test teachers and {user_count} test users")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes made'))
            for teacher in test_teachers[:10]:  # Show first 10
                self.stdout.write(f"  Would delete: {teacher.name} (ID: {teacher.id})")
        else:
            # Delete teachers (this will cascade appropriately)
            test_teachers.delete()
            # Delete associated users
            test_users.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {teacher_count} test teachers and {user_count} test users'))

    def create_test_teachers(self, dry_run=False):
        """Create 10 test teachers and assign them randomly to classes"""
        self.stdout.write(self.style.SUCCESS('Creating test teachers...'))
        
        # Get all active classes
        classes = list(Class.objects.filter(is_active=True))
        
        if not classes:
            self.stdout.write(self.style.ERROR('No active classes found. Please create classes first.'))
            return
        
        # Define subjects for more realistic teacher names
        subjects = [
            'Math', 'Science', 'English', 'History', 'Geography',
            'Physics', 'Chemistry', 'Biology', 'Literature', 'Art'
        ]
        
        # Define access levels for variety
        access_levels = ['FULL', 'FULL', 'FULL', 'VIEW_ONLY', 'VIEW_ONLY']  # 60% FULL, 40% VIEW_ONLY
        
        total_created = 0
        teacher_data = []
        
        with transaction.atomic():
            for i in range(1, 11):  # Create 10 teachers
                # Create unique identifiers with TEST_ prefix
                username = f"TEST_TEACHER_{i}"
                subject = subjects[i-1] if i <= len(subjects) else 'General'
                
                # Teacher details
                teacher_info = {
                    'name': f"Test Teacher {i}",
                    'username': username,
                    'email': f"test.teacher.{i}@testschool.edu",
                    'phone': f"555-8{i:03d}",
                    'subject': subject,
                    'is_head': i == 1,  # Make first one a head teacher
                    'access_level': random.choice(access_levels)
                }
                
                if dry_run:
                    self.stdout.write(f"  Would create: {teacher_info['name']} ({subject}) - {teacher_info['email']}")
                    teacher_data.append(teacher_info)
                else:
                    try:
                        # Create Django user
                        user = User.objects.create_user(
                            username=username,
                            email=teacher_info['email'],
                            password='TestTeacher123!',  # Default password for all test teachers
                            first_name='Test',
                            last_name=f'Teacher {i}'
                        )
                        user.is_staff = True  # Teachers need staff status
                        user.save()
                        
                        # Create Teacher profile
                        teacher = Teacher.objects.create(
                            user=user,
                            name=teacher_info['name'],
                            email=teacher_info['email'],
                            phone=teacher_info['phone'],
                            is_head_teacher=teacher_info['is_head'],
                            is_active=True,
                            global_access_level=teacher_info['access_level']
                        )
                        
                        # Randomly assign to 2-5 classes
                        num_classes = random.randint(2, min(5, len(classes)))
                        assigned_classes = random.sample(classes, num_classes)
                        
                        for class_obj in assigned_classes:
                            class_obj.assigned_teachers.add(teacher)
                        
                        self.stdout.write(self.style.SUCCESS(
                            f"  Created: {teacher.name} ({subject})"
                        ))
                        self.stdout.write(f"    Email: {teacher.email}")
                        self.stdout.write(f"    Access Level: {teacher.global_access_level}")
                        self.stdout.write(f"    Assigned to {num_classes} classes: {', '.join([c.name for c in assigned_classes[:3]])}{'...' if num_classes > 3 else ''}")
                        
                        total_created += 1
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Error creating teacher: {e}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN Summary:'))
            self.stdout.write(f"Would create {len(teacher_data)} test teachers")
            self.stdout.write("\nSample teacher data:")
            for data in teacher_data[:3]:  # Show first 3 examples
                self.stdout.write(f"  Name: {data['name']}, Email: {data['email']}, Username: {data['username']}")
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {total_created} test teachers'))
            
            # Show class coverage
            self.stdout.write('\n' + '='*60)
            self.stdout.write('CLASS COVERAGE CHECK')
            self.stdout.write('='*60)
            
            # Check how many classes now have teachers
            classes_with_teachers = 0
            for class_obj in classes:
                if class_obj.assigned_teachers.exists():
                    classes_with_teachers += 1
            
            self.stdout.write(f'Classes with teachers: {classes_with_teachers}/{len(classes)}')
            
            # Show summary
            self.stdout.write('\n' + '='*60)
            self.stdout.write('TEST TEACHER SUMMARY')
            self.stdout.write('='*60)
            self.stdout.write(f'Total Teachers Created: {total_created}')
            self.stdout.write('Identification Pattern: All have "TEST_" prefix')
            self.stdout.write('Default Password: TestTeacher123!')
            self.stdout.write('Access Levels: Mix of FULL and VIEW_ONLY')
            self.stdout.write('='*60)
            self.stdout.write(self.style.WARNING(
                '\nIMPORTANT: These are TEST teachers. To remove them before deployment, run:\n'
                '  python manage.py create_test_teachers --delete'
            ))
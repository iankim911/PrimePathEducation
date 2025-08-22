"""
Management command to create dummy students for testing
These students have easily identifiable names and IDs for easy removal pre-deployment
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from core.models import Student
from primepath_routinetest.models import Class, StudentEnrollment
import uuid
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Creates 5 dummy students per class with identifiable test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all test students instead of creating them',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        if options['delete']:
            self.delete_test_students(dry_run=options['dry_run'])
        else:
            self.create_test_students(dry_run=options['dry_run'])

    def delete_test_students(self, dry_run=False):
        """Delete all test students (those with TEST_ prefix in username)"""
        self.stdout.write(self.style.WARNING('Deleting test students...'))
        
        # Find test students by the TEST_ prefix pattern
        test_students = Student.objects.filter(name__startswith='Test Student ')
        test_users = User.objects.filter(username__startswith='TEST_STUDENT_')
        
        student_count = test_students.count()
        user_count = test_users.count()
        
        self.stdout.write(f"Found {student_count} test students and {user_count} test users")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes made'))
            for student in test_students[:10]:  # Show first 10
                self.stdout.write(f"  Would delete: {student.name} (ID: {student.id})")
        else:
            # Delete students (this will cascade to enrollments)
            test_students.delete()
            # Delete associated users
            test_users.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {student_count} test students and {user_count} test users'))

    def create_test_students(self, dry_run=False):
        """Create 5 test students per class"""
        self.stdout.write(self.style.SUCCESS('Creating test students...'))
        
        # Get all active classes
        classes = Class.objects.filter(is_active=True)
        
        if not classes.exists():
            self.stdout.write(self.style.ERROR('No active classes found. Please create classes first.'))
            return
        
        total_created = 0
        student_data = []
        
        with transaction.atomic():
            for class_obj in classes:
                self.stdout.write(f"\nProcessing class: {class_obj}")
                
                # Create 5 students for this class
                for i in range(1, 6):
                    # Create unique identifiers with TEST_ prefix for easy deletion
                    student_number = f"{class_obj.grade_level}_{class_obj.section}_{i}" if class_obj.section else f"{class_obj.grade_level}_{i}"
                    student_id = f"TEST_{uuid.uuid4().hex[:8].upper()}"  # TEST_XXXXXXXX format
                    username = f"TEST_STUDENT_{student_number}".replace(' ', '_').replace('-', '_').upper()
                    
                    # Student details
                    student_info = {
                        'name': f"Test Student {i}",
                        'username': username,
                        'student_id': student_id,
                        'email': f"test.student.{student_number.lower()}@testschool.edu".replace(' ', '.'),
                        'grade_level': class_obj.grade_level,
                        'dob': date.today() - timedelta(days=365 * random.randint(10, 18)),  # Random age 10-18
                        'parent_phone': f"555-{random.randint(1000, 9999)}",
                        'parent_email': f"parent{i}@testmail.com",
                        'notes': f"TEST DATA - Auto-generated dummy student for {class_obj.name}. DELETE BEFORE DEPLOYMENT."
                    }
                    
                    if dry_run:
                        self.stdout.write(f"  Would create: {student_info['name']} (ID: {student_info['student_id']})")
                        student_data.append(student_info)
                    else:
                        try:
                            # Create Django user (optional - only if you need login capability)
                            user = User.objects.create_user(
                                username=username,
                                email=student_info['email'],
                                password='TestPassword123!',  # Default password for all test students
                                first_name='Test',
                                last_name=f'Student {i}'
                            )
                            
                            # Create Student profile
                            student = Student.objects.create(
                                user=user,
                                name=student_info['name'],
                                current_grade_level=student_info['grade_level'],
                                date_of_birth=student_info['dob'],
                                parent_phone=student_info['parent_phone'],
                                parent_email=student_info['parent_email'],
                                notes=student_info['notes'],
                                is_active=True
                            )
                            
                            # Enroll in class
                            enrollment = StudentEnrollment.objects.create(
                                student=student,
                                class_assigned=class_obj,
                                academic_year=class_obj.academic_year,
                                status='active'
                            )
                            
                            self.stdout.write(self.style.SUCCESS(
                                f"  Created: {student.name} (ID: {student.id}) - Enrolled in {class_obj.name}"
                            ))
                            total_created += 1
                            
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"  Error creating student: {e}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN Summary:'))
            self.stdout.write(f"Would create {len(student_data)} test students across {classes.count()} classes")
            self.stdout.write("\nSample student data:")
            for data in student_data[:3]:  # Show first 3 examples
                self.stdout.write(f"  Name: {data['name']}, ID: {data['student_id']}, Username: {data['username']}")
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {total_created} test students'))
            self.stdout.write(self.style.WARNING(
                '\nIMPORTANT: These are TEST students. To remove them before deployment, run:\n'
                '  python manage.py create_test_students --delete'
            ))
            
            # Show summary
            self.stdout.write('\n' + '='*50)
            self.stdout.write('TEST STUDENT SUMMARY')
            self.stdout.write('='*50)
            self.stdout.write(f'Total Students Created: {total_created}')
            self.stdout.write(f'Classes Populated: {classes.count()}')
            self.stdout.write('Identification Pattern: All have "TEST_" prefix')
            self.stdout.write('Default Password: TestPassword123!')
            self.stdout.write('='*50)
"""
Management command to create dummy students for testing
These will be deleted before launch
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Student
from datetime import date, timedelta
import random
import uuid

class Command(BaseCommand):
    help = 'Create dummy students for testing (Student1, Student2, ... StudentN)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of dummy students to create (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing dummy students first'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            # Delete existing dummy students
            deleted = Student.objects.filter(name__startswith='Student').delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing dummy students'))
        
        # Grade levels to randomly assign
        grade_levels = ['PS1', 'PS2', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6']
        
        # Generate random parent phone numbers and emails
        created_students = []
        
        for i in range(1, count + 1):
            student_name = f"Student{i}"
            
            # Check if student already exists
            if Student.objects.filter(name=student_name).exists():
                self.stdout.write(self.style.WARNING(f'Student {student_name} already exists, skipping'))
                continue
            
            # Generate random data
            grade = random.choice(grade_levels)
            
            # Random date of birth (between 5 and 18 years old)
            age = random.randint(5, 18)
            dob = date.today() - timedelta(days=age*365 + random.randint(0, 364))
            
            # Generate parent contact info
            phone_suffix = str(1000 + i).zfill(4)
            parent_phone = f"555-{phone_suffix[:3]}-{phone_suffix[3:]}"
            parent_email = f"parent.student{i}@testmail.com"
            
            # Create student
            student = Student.objects.create(
                name=student_name,
                current_grade_level=grade,
                date_of_birth=dob,
                parent_phone=parent_phone,
                parent_email=parent_email,
                notes=f"Test student #{i} - TO BE DELETED BEFORE LAUNCH",
                is_active=True
            )
            
            created_students.append(student)
            self.stdout.write(self.style.SUCCESS(f'Created: {student_name} (Grade: {grade}, Age: {age})'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {len(created_students)} dummy students'))
        self.stdout.write(self.style.WARNING('⚠️  REMEMBER: These dummy students must be deleted before launch!'))
        
        # Create a few sample enrollments for testing
        if created_students:
            self.stdout.write(self.style.INFO('\n📚 Creating sample class enrollments...'))
            
            from primepath_routinetest.models import Class, StudentEnrollment
            
            # Create or get test classes for each grade
            test_classes = []
            for class_code in ['PS1', 'P1', 'P2']:
                class_obj, created = Class.objects.get_or_create(
                    name=class_code,
                    defaults={
                        'grade_level': class_code,
                        'academic_year': '2024-2025'
                    }
                )
                test_classes.append(class_obj)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created test class: {class_code}'))
            
            # Enroll some students in classes
            for i, student in enumerate(created_students[:15]):  # Enroll first 15 students
                class_index = i % len(test_classes)
                class_obj = test_classes[class_index]
                
                enrollment, created = StudentEnrollment.objects.get_or_create(
                    student=student,
                    class_assigned=class_obj,
                    defaults={
                        'status': 'active',
                        'academic_year': '2024-2025'
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'  Enrolled {student.name} in {class_obj.name}'
                    ))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Dummy student creation complete!'))
"""
Setup Test Data for RoutineTest User Testing
Run this script to create all necessary test data for user testing
"""

import os
import sys
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Teacher, Student
from primepath_routinetest.models import (
    Class, StudentEnrollment,
    RoutineExam, ExamAssignment, StudentExamAssignment
)

print("="*60)
print("SETTING UP TEST DATA FOR ROUTINETEST")
print("="*60)

# 1. Create Admin Account
print("\n1. Creating Admin Account...")
try:
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@primepath.edu',
        password='Admin123!'
    )
    print(f"✅ Admin created: username='admin', password='Admin123!'")
except:
    print("⚠️ Admin already exists")
    admin = User.objects.get(username='admin')

# 2. Create Teachers
print("\n2. Creating Teachers...")
teachers_data = [
    {'username': 'teacher1', 'name': 'Ms. Smith', 'email': 'smith@primepath.edu'},
    {'username': 'teacher2', 'name': 'Mr. Johnson', 'email': 'johnson@primepath.edu'},
    {'username': 'teacher3', 'name': 'Mrs. Davis', 'email': 'davis@primepath.edu'},
]

teachers = []
for t_data in teachers_data:
    try:
        user = User.objects.create_user(
            username=t_data['username'],
            email=t_data['email'],
            password='Teacher123!'
        )
        teacher = Teacher.objects.create(
            user=user,
            name=t_data['name'],
            email=t_data['email']
        )
        teachers.append(teacher)
        print(f"✅ Teacher created: {t_data['name']} (username='{t_data['username']}', password='Teacher123!')")
    except:
        print(f"⚠️ Teacher {t_data['username']} already exists")
        teacher = Teacher.objects.get(user__username=t_data['username'])
        teachers.append(teacher)

# 3. Create Classes
print("\n3. Creating Classes...")
classes_data = [
    {'name': 'Mathematics 5A', 'grade': 'Grade 5', 'section': 'A', 'teacher': teachers[0]},
    {'name': 'Mathematics 5B', 'grade': 'Grade 5', 'section': 'B', 'teacher': teachers[0]},
    {'name': 'English 5A', 'grade': 'Grade 5', 'section': 'A', 'teacher': teachers[1]},
    {'name': 'Science 6A', 'grade': 'Grade 6', 'section': 'A', 'teacher': teachers[2]},
]

classes = []
for c_data in classes_data:
    try:
        class_obj = Class.objects.create(
            name=c_data['name'],
            grade_level=c_data['grade'],
            section=c_data['section'],
            academic_year='2024-2025',
            created_by=admin
        )
        class_obj.assigned_teachers.add(c_data['teacher'])
        classes.append(class_obj)
        print(f"✅ Class created: {c_data['name']} (Teacher: {c_data['teacher'].name})")
    except:
        print(f"⚠️ Class {c_data['name']} may already exist")

# 4. Create Students
print("\n4. Creating Students...")
students_data = [
    # Grade 5 students
    {'name': 'John Doe', 'grade': 'Grade 5', 'username': 'john.doe'},
    {'name': 'Jane Smith', 'grade': 'Grade 5', 'username': 'jane.smith'},
    {'name': 'Alice Johnson', 'grade': 'Grade 5', 'username': 'alice.johnson'},
    {'name': 'Bob Wilson', 'grade': 'Grade 5', 'username': 'bob.wilson'},
    {'name': 'Charlie Brown', 'grade': 'Grade 5', 'username': 'charlie.brown'},
    # Grade 6 students
    {'name': 'David Lee', 'grade': 'Grade 6', 'username': 'david.lee'},
    {'name': 'Emma Davis', 'grade': 'Grade 6', 'username': 'emma.davis'},
    {'name': 'Frank Miller', 'grade': 'Grade 6', 'username': 'frank.miller'},
]

students = []
for s_data in students_data:
    try:
        # Create user account for student
        user = User.objects.create_user(
            username=s_data['username'],
            email=f"{s_data['username']}@student.primepath.edu",
            password='Student123!'
        )
        student = Student.objects.create(
            user=user,
            name=s_data['name'],
            current_grade_level=s_data['grade'],
            parent_email=f"parent.{s_data['username']}@gmail.com",
            parent_phone='555-0100'
        )
        students.append(student)
        print(f"✅ Student created: {s_data['name']} (username='{s_data['username']}', password='Student123!')")
    except:
        print(f"⚠️ Student {s_data['username']} already exists")
        student = Student.objects.get(user__username=s_data['username'])
        students.append(student)

# 5. Enroll Students in Classes
print("\n5. Enrolling Students in Classes...")
enrollments = [
    # Math 5A
    (students[0], classes[0]),  # John -> Math 5A
    (students[1], classes[0]),  # Jane -> Math 5A
    (students[2], classes[0]),  # Alice -> Math 5A
    # Math 5B
    (students[3], classes[1]),  # Bob -> Math 5B
    (students[4], classes[1]),  # Charlie -> Math 5B
    # English 5A
    (students[0], classes[2]),  # John -> English 5A
    (students[1], classes[2]),  # Jane -> English 5A
    # Science 6A
    (students[5], classes[3]),  # David -> Science 6A
    (students[6], classes[3]),  # Emma -> Science 6A
    (students[7], classes[3]),  # Frank -> Science 6A
]

for student, class_obj in enrollments:
    try:
        if class_obj and student:
            enrollment = StudentEnrollment.objects.create(
                student=student,
                class_assigned=class_obj,
                academic_year='2024-2025',
                status='active',
                created_by=class_obj.assigned_teachers.first().user
            )
            print(f"✅ Enrolled {student.name} in {class_obj.name}")
    except:
        print(f"⚠️ {student.name} already enrolled in {class_obj.name}")

# 6. Create Sample Exams
print("\n6. Creating Sample Exams...")
exams_data = [
    {
        'name': 'Q1 Mathematics Monthly Review 1',
        'type': 'monthly_review',
        'level': 'CORE Phonics Level 1',
        'quarter': 'Q1',
        'answers': {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': '42'}
    },
    {
        'name': 'Q1 English Monthly Review 1',
        'type': 'monthly_review',
        'level': 'CORE Phonics Level 1',
        'quarter': 'Q1',
        'answers': {'1': 'B', '2': 'A', '3': 'D', '4': 'C', '5': 'noun'}
    },
    {
        'name': 'Q1 Science Quarterly Exam',
        'type': 'quarterly',
        'level': 'CORE Phonics Level 2',
        'quarter': 'Q1',
        'answers': {'1': 'C', '2': 'B', '3': 'A', '4': 'D', '5': 'photosynthesis', '6': 'A', '7': 'B', '8': 'C'}
    },
]

exams = []
for e_data in exams_data:
    try:
        exam = RoutineExam.objects.create(
            name=e_data['name'],
            exam_type=e_data['type'],
            curriculum_level=e_data['level'],
            academic_year='2025',
            quarter=e_data['quarter'],
            answer_key=e_data['answers'],
            created_by=admin
        )
        exams.append(exam)
        print(f"✅ Exam created: {e_data['name']} ({len(e_data['answers'])} questions)")
    except:
        print(f"⚠️ Exam {e_data['name']} may already exist")

# 7. Assign Exams to Classes
print("\n7. Assigning Exams to Classes...")
if exams and classes:
    assignments = [
        (exams[0], classes[0], teachers[0]),  # Math exam -> Math 5A
        (exams[0], classes[1], teachers[0]),  # Math exam -> Math 5B
        (exams[1], classes[2], teachers[1]),  # English exam -> English 5A
        (exams[2], classes[3], teachers[2]),  # Science exam -> Science 6A
    ]
    
    for exam, class_obj, teacher in assignments:
        try:
            if exam and class_obj:
                # Create assignment with deadline in 7 days
                assignment = ExamAssignment.objects.create(
                    exam=exam,
                    class_assigned=class_obj,
                    assigned_by=teacher,
                    deadline=timezone.now() + timedelta(days=7),
                    allow_multiple_attempts=True,
                    is_bulk_assignment=True
                )
                
                # Create individual student assignments
                enrollments = StudentEnrollment.objects.filter(
                    class_assigned=class_obj,
                    status='active'
                )
                
                for enrollment in enrollments:
                    StudentExamAssignment.objects.create(
                        student=enrollment.student,
                        exam_assignment=assignment,
                        status='assigned'
                    )
                
                print(f"✅ Assigned '{exam.name}' to {class_obj.name} ({enrollments.count()} students)")
        except Exception as e:
            print(f"⚠️ Could not assign exam: {e}")

# Print Summary
print("\n" + "="*60)
print("TEST DATA SETUP COMPLETE!")
print("="*60)

print("\n📋 CREATED ACCOUNTS:")
print("\n👤 Admin:")
print("   Username: admin")
print("   Password: Admin123!")

print("\n👩‍🏫 Teachers:")
for t in teachers_data:
    print(f"   {t['name']}: username='{t['username']}', password='Teacher123!'")

print("\n🎓 Students (sample):")
print("   John Doe: username='john.doe', password='Student123!'")
print("   Jane Smith: username='jane.smith', password='Student123!'")
print("   (and 6 more students...)")

print("\n📚 Classes Created:")
print("   - Mathematics 5A (Ms. Smith)")
print("   - Mathematics 5B (Ms. Smith)")
print("   - English 5A (Mr. Johnson)")
print("   - Science 6A (Mrs. Davis)")

print("\n📝 Exams Created:")
print("   - Q1 Mathematics Monthly Review 1")
print("   - Q1 English Monthly Review 1")
print("   - Q1 Science Quarterly Exam")

print("\n✅ READY FOR TESTING!")
print("\n🌐 Access the application at: http://127.0.0.1:8000/RoutineTest/")
print("\n📖 Follow the test scenarios in 'user_testing_plan.md'")
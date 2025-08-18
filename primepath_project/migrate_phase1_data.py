"""
Data Migration Script - Phase 1 (PlacementTest) to Phase 2 (RoutineTest)
Migrates existing data from PlacementTest to RoutineTest
"""

import os
import sys
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from core.models import Teacher, Student, School, Program, SubProgram
from placement_test.models import Exam as PlacementExam, StudentSession
from primepath_routinetest.models import (
    Class, StudentEnrollment,
    RoutineExam, ExamAssignment, StudentExamAssignment, ExamAttempt
)

print("="*60)
print("DATA MIGRATION: PHASE 1 → PHASE 2")
print("="*60)

class DataMigrator:
    def __init__(self):
        self.stats = {
            'users': 0,
            'teachers': 0,
            'students': 0,
            'exams': 0,
            'sessions': 0,
            'errors': []
        }
    
    @transaction.atomic
    def migrate_users(self):
        """Migrate existing users and create teacher/student profiles"""
        print("\n1. Migrating Users...")
        
        users = User.objects.all()
        for user in users:
            try:
                # Check if user is staff/admin -> Teacher
                if user.is_staff or user.is_superuser:
                    if not hasattr(user, 'teacher_profile'):
                        teacher = Teacher.objects.create(
                            user=user,
                            name=user.get_full_name() or user.username,
                            email=user.email,
                            is_head_teacher=user.is_superuser
                        )
                        self.stats['teachers'] += 1
                        print(f"✅ Created teacher profile for {user.username}")
                
                # Regular users -> Students
                elif not user.is_staff:
                    if not hasattr(user, 'student_profile'):
                        student = Student.objects.create(
                            user=user,
                            name=user.get_full_name() or user.username,
                            current_grade_level='Grade 5'  # Default
                        )
                        self.stats['students'] += 1
                        print(f"✅ Created student profile for {user.username}")
                
                self.stats['users'] += 1
                
            except Exception as e:
                self.stats['errors'].append(f"User {user.username}: {e}")
                print(f"❌ Error migrating user {user.username}: {e}")
    
    @transaction.atomic
    def create_default_classes(self):
        """Create default classes based on curriculum levels"""
        print("\n2. Creating Default Classes...")
        
        # Get unique grade levels from existing data
        grade_levels = ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6']
        
        classes_created = 0
        for grade in grade_levels:
            try:
                class_obj, created = Class.objects.get_or_create(
                    name=f'{grade} - General',
                    defaults={
                        'grade_level': grade,
                        'section': 'A',
                        'academic_year': '2024-2025',
                        'created_by': User.objects.filter(is_superuser=True).first()
                    }
                )
                if created:
                    # Assign all teachers to all classes initially
                    teachers = Teacher.objects.all()
                    for teacher in teachers:
                        class_obj.assigned_teachers.add(teacher)
                    classes_created += 1
                    print(f"✅ Created class: {class_obj.name}")
            except Exception as e:
                self.stats['errors'].append(f"Class creation: {e}")
                print(f"❌ Error creating class: {e}")
        
        print(f"Created {classes_created} new classes")
    
    @transaction.atomic
    def migrate_exams(self):
        """Migrate PlacementTest exams to RoutineTest exams"""
        print("\n3. Migrating Exams...")
        
        placement_exams = PlacementExam.objects.all()
        
        for p_exam in placement_exams:
            try:
                # Determine exam type based on name
                exam_type = 'quarterly' if 'quarterly' in p_exam.name.lower() else 'monthly_review'
                
                # Get curriculum level from exam
                curriculum_level = 'CORE Phonics Level 1'  # Default
                if hasattr(p_exam, 'curriculum_level'):
                    curriculum_level = p_exam.curriculum_level
                
                # Create or get RoutineExam
                r_exam, created = RoutineExam.objects.get_or_create(
                    name=f"Migrated: {p_exam.name}",
                    defaults={
                        'exam_type': exam_type,
                        'curriculum_level': curriculum_level,
                        'academic_year': '2025',
                        'quarter': 'Q1',
                        'pdf_file': p_exam.pdf_file if hasattr(p_exam, 'pdf_file') else None,
                        'answer_key': {},  # Will need to be set manually
                        'created_by': p_exam.created_by if hasattr(p_exam, 'created_by') else None
                    }
                )
                
                if created:
                    self.stats['exams'] += 1
                    print(f"✅ Migrated exam: {p_exam.name}")
                    
                    # Migrate answer keys if available
                    if hasattr(p_exam, 'questions'):
                        answer_key = {}
                        for i, question in enumerate(p_exam.questions.all(), 1):
                            if hasattr(question, 'correct_answer'):
                                answer_key[str(i)] = question.correct_answer
                        r_exam.answer_key = answer_key
                        r_exam.save()
                        print(f"  → Migrated {len(answer_key)} answer keys")
                
            except Exception as e:
                self.stats['errors'].append(f"Exam {p_exam.name}: {e}")
                print(f"❌ Error migrating exam {p_exam.name}: {e}")
    
    @transaction.atomic
    def migrate_student_sessions(self):
        """Migrate student test sessions to exam attempts"""
        print("\n4. Migrating Student Sessions...")
        
        sessions = StudentSession.objects.all()
        
        for session in sessions:
            try:
                # Find corresponding student
                student = None
                if session.student_name:
                    # Try to find by name
                    student = Student.objects.filter(name=session.student_name).first()
                
                if not student:
                    # Create student if not found
                    student = Student.objects.create(
                        name=session.student_name or f"Student_{session.id}",
                        current_grade_level='Grade 5'
                    )
                    print(f"  → Created student: {student.name}")
                
                # Find corresponding exam
                r_exam = RoutineExam.objects.filter(
                    name__contains=session.exam.name if hasattr(session, 'exam') else 'Unknown'
                ).first()
                
                if r_exam and student:
                    # Create exam attempt
                    attempt = ExamAttempt.objects.create(
                        student=student,
                        exam=r_exam,
                        assignment=None,  # No assignment in Phase 1
                        attempt_number=1,
                        answers={},  # Would need to migrate answers
                        score=session.score if hasattr(session, 'score') else None,
                        is_submitted=session.completed_at is not None,
                        started_at=session.started_at,
                        submitted_at=session.completed_at
                    )
                    
                    self.stats['sessions'] += 1
                    print(f"✅ Migrated session for {student.name}")
                
            except Exception as e:
                self.stats['errors'].append(f"Session {session.id}: {e}")
                print(f"❌ Error migrating session: {e}")
    
    def enroll_students_in_classes(self):
        """Auto-enroll students in appropriate classes"""
        print("\n5. Enrolling Students in Classes...")
        
        students = Student.objects.all()
        enrollments = 0
        
        for student in students:
            try:
                # Find appropriate class based on grade level
                grade = student.current_grade_level
                class_obj = Class.objects.filter(grade_level=grade).first()
                
                if not class_obj:
                    # Use default class
                    class_obj = Class.objects.first()
                
                if class_obj:
                    enrollment, created = StudentEnrollment.objects.get_or_create(
                        student=student,
                        class_assigned=class_obj,
                        defaults={
                            'academic_year': '2024-2025',
                            'status': 'active'
                        }
                    )
                    if created:
                        enrollments += 1
                        print(f"✅ Enrolled {student.name} in {class_obj.name}")
                        
            except Exception as e:
                self.stats['errors'].append(f"Enrollment {student.name}: {e}")
                print(f"❌ Error enrolling {student.name}: {e}")
        
        print(f"Created {enrollments} new enrollments")
    
    def run_migration(self):
        """Run complete migration"""
        print("\n🚀 Starting Migration Process...")
        
        # Step 1: Migrate users
        self.migrate_users()
        
        # Step 2: Create default classes
        self.create_default_classes()
        
        # Step 3: Migrate exams
        self.migrate_exams()
        
        # Step 4: Migrate sessions
        self.migrate_student_sessions()
        
        # Step 5: Enroll students
        self.enroll_students_in_classes()
        
        # Print summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Users processed: {self.stats['users']}")
        print(f"Teachers created: {self.stats['teachers']}")
        print(f"Students created: {self.stats['students']}")
        print(f"Exams migrated: {self.stats['exams']}")
        print(f"Sessions migrated: {self.stats['sessions']}")
        
        if self.stats['errors']:
            print(f"\n⚠️ Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        else:
            print("\n✅ Migration completed successfully!")
        
        return self.stats


if __name__ == '__main__':
    print("\n⚠️  WARNING: This will migrate data from PlacementTest to RoutineTest.")
    print("Make sure to backup your database before proceeding!")
    
    confirm = input("\nProceed with migration? (yes/no): ")
    
    if confirm.lower() == 'yes':
        migrator = DataMigrator()
        stats = migrator.run_migration()
        
        # Save migration report
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(report_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        print(f"\n📄 Migration report saved to: {report_file}")
    else:
        print("Migration cancelled.")
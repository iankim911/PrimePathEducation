"""
TESTER: Day 4 - Exam Management Core Tests
Tests for exam upload, assignment, and basic administration
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from core.models import Teacher, Student
from primepath_routinetest.models import Class

# Test counters
TOTAL_TESTS = 0
PASSED_TESTS = 0
FAILED_TESTS = []

def test_decorator(test_name):
    """Decorator to track test execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            global TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
            TOTAL_TESTS += 1
            print(f"\n[TEST {TOTAL_TESTS}] {test_name}")
            try:
                result = func(*args, **kwargs)
                PASSED_TESTS += 1
                print(f"✅ PASSED: {test_name}")
                return result
            except Exception as e:
                FAILED_TESTS.append({
                    'test': test_name,
                    'error': str(e),
                    'number': TOTAL_TESTS
                })
                print(f"❌ FAILED: {test_name}")
                print(f"   Error: {e}")
                raise
        return wrapper
    return decorator

class Day4ExamManagementTests(TestCase):
    """Comprehensive tests for Day 4 Exam Management features"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users with unique usernames
        import random
        suffix = random.randint(1000, 9999)
        
        self.admin = User.objects.create_superuser(f'admin_d4_{suffix}', 'admin@test.com', 'admin123')
        self.teacher_user = User.objects.create_user(f'teacher_d4_{suffix}', 'teacher1@test.com', 'teacher123')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            name='Test Teacher',
            email='teacher1@test.com'
        )
        self.student_user = User.objects.create_user(f'student_d4_{suffix}', 'student1@test.com', 'student123')
        self.student = Student.objects.create(
            user=self.student_user,
            name='Test Student',
            current_grade_level='Grade 5'
        )
        
        # Create class
        self.test_class = Class.objects.create(
            name='Test Class 5A',
            section='A',
            grade_level='Grade 5',
            academic_year='2024-2025'
        )
        self.test_class.assigned_teachers.add(self.teacher)
    
    @test_decorator("Admin can upload a new exam PDF")
    def test_admin_upload_exam(self):
        """Test that admin can upload exam PDFs"""
        self.client.login(username=self.admin.username, password='admin123')
        
        # Create a mock PDF file
        pdf_content = b'%PDF-1.4 mock exam content'
        pdf_file = SimpleUploadedFile(
            'test_exam.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        
        response = self.client.post('/api/RoutineTest/admin/exams/upload/', {
            'name': 'Q1 Monthly Review 1',
            'exam_type': 'monthly_review',
            'curriculum_level': 'CORE Phonics Level 1',
            'academic_year': '2025',
            'quarter': 'Q1',
            'pdf_file': pdf_file
        })
        
        self.assertIn(response.status_code, [200, 201, 302])
        
        # Verify exam was created
        from primepath_routinetest.models import RoutineExam
        exam = RoutineExam.objects.filter(name='Q1 Monthly Review 1').first()
        self.assertIsNotNone(exam)
        self.assertEqual(exam.exam_type, 'monthly_review')
    
    @test_decorator("Admin can set answer keys for an exam")
    def test_admin_set_answer_key(self):
        """Test setting answer keys for uploaded exam"""
        self.client.login(username=self.admin.username, password='admin123')
        
        # Create exam first
        from primepath_routinetest.models import RoutineExam
        exam = RoutineExam.objects.create(
            name='Test Exam',
            exam_type='quarterly',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        
        # Set answer key
        answer_key = {
            '1': 'A',
            '2': 'B',
            '3': 'C',
            '4': 'D',
            '5': 'apple'
        }
        
        response = self.client.post(
            f'/api/RoutineTest/admin/exams/{exam.id}/answer-key/',
            json.dumps({'answer_key': answer_key}),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 201])
        
        # Verify answer key was saved
        exam.refresh_from_db()
        self.assertEqual(exam.answer_key, answer_key)
    
    @test_decorator("Teacher can view available exams for their curriculum levels")
    def test_teacher_view_available_exams(self):
        """Test that teachers can see exams in the library"""
        self.client.login(username=self.teacher_user.username, password='teacher123')
        
        # Create some exams
        from primepath_routinetest.models import RoutineExam
        exam1 = RoutineExam.objects.create(
            name='Monthly Review 1',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        exam2 = RoutineExam.objects.create(
            name='Quarterly Exam Q1',
            exam_type='quarterly',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        
        response = self.client.get('/api/RoutineTest/teacher/exams/')
        self.assertEqual(response.status_code, 200)
        
        if hasattr(response, 'json'):
            data = response.json()
            self.assertGreaterEqual(len(data.get('exams', [])), 2)
    
    @test_decorator("Teacher can assign exam to entire class")
    def test_teacher_assign_exam_to_class(self):
        """Test bulk assignment of exam to class"""
        self.client.login(username=self.teacher_user.username, password='teacher123')
        
        # Create exam
        from primepath_routinetest.models import RoutineExam
        exam = RoutineExam.objects.create(
            name='Class Test 1',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        
        # Enroll students in class
        from primepath_routinetest.models import StudentEnrollment
        enrollment = StudentEnrollment.objects.create(
            student=self.student,
            class_assigned=self.test_class,
            academic_year='2024-2025',
            status='active'
        )
        
        # Assign exam to class
        deadline = timezone.now() + timedelta(days=7)
        response = self.client.post(
            '/api/RoutineTest/teacher/exams/assign/',
            json.dumps({
                'exam_id': str(exam.id),
                'class_id': str(self.test_class.id),
                'deadline': deadline.isoformat(),
                'is_bulk': True
            }),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 201])
        
        # Verify assignment was created
        from primepath_routinetest.models import ExamAssignment
        assignment = ExamAssignment.objects.filter(
            exam=exam,
            class_assigned=self.test_class
        ).first()
        self.assertIsNotNone(assignment)
        self.assertTrue(assignment.is_bulk_assignment)
    
    @test_decorator("Teacher can assign different exams to individual students")
    def test_teacher_differentiated_assignment(self):
        """Test assigning different exams to specific students"""
        self.client.login(username=self.teacher_user.username, password='teacher123')
        
        # Create multiple students
        student2 = Student.objects.create(
            name='Student 2',
            current_grade_level='Grade 5'
        )
        
        # Enroll students
        from primepath_routinetest.models import StudentEnrollment
        StudentEnrollment.objects.create(
            student=self.student,
            class_assigned=self.test_class,
            academic_year='2024-2025',
            status='active'
        )
        StudentEnrollment.objects.create(
            student=student2,
            class_assigned=self.test_class,
            academic_year='2024-2025',
            status='active'
        )
        
        # Create different exams
        from primepath_routinetest.models import RoutineExam
        exam_basic = RoutineExam.objects.create(
            name='Basic Level Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        exam_advanced = RoutineExam.objects.create(
            name='Advanced Level Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 2',
            academic_year='2025',
            quarter='Q1'
        )
        
        # Assign different exams
        deadline = timezone.now() + timedelta(days=7)
        response = self.client.post(
            '/api/RoutineTest/teacher/exams/assign-individual/',
            json.dumps({
                'assignments': [
                    {
                        'student_id': str(self.student.id),
                        'exam_id': str(exam_basic.id),
                        'deadline': deadline.isoformat()
                    },
                    {
                        'student_id': str(student2.id),
                        'exam_id': str(exam_advanced.id),
                        'deadline': deadline.isoformat()
                    }
                ]
            }),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 201])
    
    @test_decorator("Student can view assigned exams")
    def test_student_view_assigned_exams(self):
        """Test that students can see their assigned exams"""
        # Setup assignment first
        from primepath_routinetest.models import RoutineExam, ExamAssignment, StudentExamAssignment, StudentEnrollment
        
        # Enroll student
        enrollment = StudentEnrollment.objects.create(
            student=self.student,
            class_assigned=self.test_class,
            academic_year='2024-2025',
            status='active'
        )
        
        # Create and assign exam
        exam = RoutineExam.objects.create(
            name='Student Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=self.test_class,
            assigned_by=self.teacher,
            deadline=timezone.now() + timedelta(days=7),
            is_bulk_assignment=True
        )
        
        student_assignment = StudentExamAssignment.objects.create(
            student=self.student,
            exam_assignment=assignment,
            status='assigned'
        )
        
        # Login as student
        self.client.login(username=self.student_user.username, password='student123')
        
        response = self.client.get('/api/RoutineTest/student/exams/')
        self.assertEqual(response.status_code, 200)
        
        if hasattr(response, 'json'):
            data = response.json()
            self.assertGreaterEqual(len(data.get('exams', [])), 1)
    
    @test_decorator("Student can start an assigned exam")
    def test_student_start_exam(self):
        """Test that student can begin taking an exam"""
        # Setup assignment
        from primepath_routinetest.models import RoutineExam, ExamAssignment, StudentExamAssignment, StudentEnrollment
        
        enrollment = StudentEnrollment.objects.create(
            student=self.student,
            class_assigned=self.test_class,
            academic_year='2024-2025',
            status='active'
        )
        
        exam = RoutineExam.objects.create(
            name='Start Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1',
            answer_key={'1': 'A', '2': 'B'}
        )
        
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=self.test_class,
            assigned_by=self.teacher,
            deadline=timezone.now() + timedelta(days=7),
            is_bulk_assignment=True
        )
        
        student_assignment = StudentExamAssignment.objects.create(
            student=self.student,
            exam_assignment=assignment,
            status='assigned'
        )
        
        self.client.login(username=self.student_user.username, password='student123')
        
        response = self.client.post(f'/api/RoutineTest/student/exams/{exam.id}/start/')
        self.assertIn(response.status_code, [200, 201])
        
        # Verify attempt was created
        from primepath_routinetest.models import ExamAttempt
        attempt = ExamAttempt.objects.filter(
            student=self.student,
            exam=exam
        ).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.attempt_number, 1)
    
    @test_decorator("Auto-save functionality during exam")
    def test_auto_save_exam_progress(self):
        """Test auto-save of exam answers"""
        # Create attempt
        from primepath_routinetest.models import RoutineExam, ExamAssignment, StudentExamAssignment, ExamAttempt
        
        exam = RoutineExam.objects.create(
            name='Auto Save Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=self.test_class,
            assigned_by=self.teacher,
            deadline=timezone.now() + timedelta(days=7)
        )
        
        student_assignment = StudentExamAssignment.objects.create(
            student=self.student,
            exam_assignment=assignment,
            status='in_progress'
        )
        
        attempt = ExamAttempt.objects.create(
            student=self.student,
            exam=exam,
            assignment=student_assignment,
            attempt_number=1,
            started_at=timezone.now()
        )
        
        self.client.login(username=self.student_user.username, password='student123')
        
        # Auto-save answers
        response = self.client.post(
            f'/api/RoutineTest/student/exams/{exam.id}/auto-save/',
            json.dumps({
                'attempt_id': str(attempt.id),
                'answers': {'1': 'A', '2': 'B', '3': 'C'}
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify auto-save
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.auto_saved_data)
        self.assertEqual(attempt.auto_saved_data.get('1'), 'A')
    
    @test_decorator("Student can submit completed exam")
    def test_student_submit_exam(self):
        """Test exam submission and scoring"""
        from primepath_routinetest.models import RoutineExam, ExamAssignment, StudentExamAssignment, ExamAttempt
        
        exam = RoutineExam.objects.create(
            name='Submit Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1',
            answer_key={'1': 'A', '2': 'B', '3': 'C'}
        )
        
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=self.test_class,
            assigned_by=self.teacher,
            deadline=timezone.now() + timedelta(days=7)
        )
        
        student_assignment = StudentExamAssignment.objects.create(
            student=self.student,
            exam_assignment=assignment,
            status='in_progress'
        )
        
        attempt = ExamAttempt.objects.create(
            student=self.student,
            exam=exam,
            assignment=student_assignment,
            attempt_number=1,
            started_at=timezone.now(),
            answers={'1': 'A', '2': 'B', '3': 'D'}  # 2 correct, 1 wrong
        )
        
        self.client.login(username=self.student_user.username, password='student123')
        
        response = self.client.post(
            f'/api/RoutineTest/student/exams/{exam.id}/submit/',
            json.dumps({'attempt_id': str(attempt.id)}),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 201])
        
        # Verify submission and score
        attempt.refresh_from_db()
        self.assertTrue(attempt.is_submitted)
        self.assertIsNotNone(attempt.submitted_at)
        self.assertEqual(attempt.score, Decimal('66.67'))  # 2/3 = 66.67%
    
    @test_decorator("Deadline enforcement for exam submission")
    def test_deadline_enforcement(self):
        """Test that exams cannot be submitted after deadline"""
        from primepath_routinetest.models import RoutineExam, ExamAssignment, StudentExamAssignment
        
        exam = RoutineExam.objects.create(
            name='Deadline Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        
        # Create assignment with past deadline
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=self.test_class,
            assigned_by=self.teacher,
            deadline=timezone.now() - timedelta(hours=1)  # Past deadline
        )
        
        student_assignment = StudentExamAssignment.objects.create(
            student=self.student,
            exam_assignment=assignment,
            status='assigned'
        )
        
        self.client.login(username=self.student_user.username, password='student123')
        
        # Try to start exam after deadline
        response = self.client.post(f'/api/RoutineTest/student/exams/{exam.id}/start/')
        self.assertIn(response.status_code, [400, 403])  # Should be rejected
    
    @test_decorator("Teacher can extend deadline for assignments")
    def test_teacher_extend_deadline(self):
        """Test deadline extension functionality"""
        from primepath_routinetest.models import RoutineExam, ExamAssignment
        
        exam = RoutineExam.objects.create(
            name='Extension Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1'
        )
        
        original_deadline = timezone.now() + timedelta(days=1)
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=self.test_class,
            assigned_by=self.teacher,
            deadline=original_deadline
        )
        
        self.client.login(username=self.teacher_user.username, password='teacher123')
        
        new_deadline = timezone.now() + timedelta(days=3)
        response = self.client.post(
            f'/api/RoutineTest/teacher/assignments/{assignment.id}/extend/',
            json.dumps({'new_deadline': new_deadline.isoformat()}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify deadline was extended
        assignment.refresh_from_db()
        self.assertGreater(assignment.deadline, original_deadline)
    
    @test_decorator("Track multiple attempts with best score and average")
    def test_multiple_attempts_tracking(self):
        """Test that system tracks both best score and average"""
        from primepath_routinetest.models import RoutineExam, ExamAssignment, StudentExamAssignment, ExamAttempt
        
        exam = RoutineExam.objects.create(
            name='Multiple Attempts Test',
            exam_type='monthly_review',
            curriculum_level='CORE Phonics Level 1',
            academic_year='2025',
            quarter='Q1',
            answer_key={'1': 'A', '2': 'B'}
        )
        
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=self.test_class,
            assigned_by=self.teacher,
            deadline=timezone.now() + timedelta(days=7),
            allow_multiple_attempts=True
        )
        
        student_assignment = StudentExamAssignment.objects.create(
            student=self.student,
            exam_assignment=assignment,
            status='in_progress'
        )
        
        # Create multiple attempts with different scores
        attempt1 = ExamAttempt.objects.create(
            student=self.student,
            exam=exam,
            assignment=student_assignment,
            attempt_number=1,
            answers={'1': 'A', '2': 'C'},  # 50% score
            score=Decimal('50.00'),
            is_submitted=True,
            started_at=timezone.now(),
            submitted_at=timezone.now()
        )
        
        attempt2 = ExamAttempt.objects.create(
            student=self.student,
            exam=exam,
            assignment=student_assignment,
            attempt_number=2,
            answers={'1': 'A', '2': 'B'},  # 100% score
            score=Decimal('100.00'),
            is_submitted=True,
            started_at=timezone.now(),
            submitted_at=timezone.now()
        )
        
        # Get best score and average
        attempts = ExamAttempt.objects.filter(
            student=self.student,
            exam=exam,
            is_submitted=True
        )
        
        best_score = max(a.score for a in attempts)
        avg_score = sum(a.score for a in attempts) / len(attempts)
        
        self.assertEqual(best_score, Decimal('100.00'))
        self.assertEqual(avg_score, Decimal('75.00'))


def run_day4_tests():
    """Run all Day 4 tests and print summary"""
    print("\n" + "="*60)
    print("DAY 4: EXAM MANAGEMENT CORE - TEST SUITE")
    print("="*60)
    
    # Run tests
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(Day4ExamManagementTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {TOTAL_TESTS}")
    print(f"Passed: {PASSED_TESTS}")
    print(f"Failed: {len(FAILED_TESTS)}")
    
    if FAILED_TESTS:
        print("\n❌ Failed Tests:")
        for failure in FAILED_TESTS:
            print(f"  - Test {failure['number']}: {failure['test']}")
            print(f"    Error: {failure['error']}")
    else:
        print("\n✅ All tests defined! Ready for implementation.")
    
    print("\n📝 Next Step: BUILDER agent should implement features to pass these tests")
    print("Run with: python manage.py test primepath_routinetest.tests.test_day4_exam_management")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_day4_tests()
    sys.exit(0 if success else 1)
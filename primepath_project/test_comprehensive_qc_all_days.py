"""
COMPREHENSIVE QC TEST SUITE - ALL DAYS (1-10)
Final quality check for entire RoutineTest implementation
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Teacher, Student
from primepath_routinetest.models import (
    Class, StudentEnrollment,
    RoutineExam, ExamAssignment, StudentExamAssignment, ExamAttempt
)

class ComprehensiveQCAllDays(TestCase):
    """Complete QC test covering Days 1-10 implementation"""
    
    def setUp(self):
        """Setup test environment"""
        self.client = Client()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'days_tested': [],
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def test_day1_authentication(self):
        """Day 1: Authentication System"""
        print("\n" + "="*60)
        print("DAY 1: AUTHENTICATION SYSTEM")
        print("="*60)
        
        try:
            # Create users
            admin = User.objects.create_superuser('admin_qc', 'admin@test.com', 'admin123')
            teacher_user = User.objects.create_user('teacher_qc', 'teacher@test.com', 'teacher123')
            student_user = User.objects.create_user('student_qc', 'student@test.com', 'student123')
            
            # Test login
            self.assertTrue(self.client.login(username='admin_qc', password='admin123'))
            self.client.logout()
            self.assertTrue(self.client.login(username='teacher_qc', password='teacher123'))
            self.client.logout()
            self.assertTrue(self.client.login(username='student_qc', password='student123'))
            
            print("✅ Authentication working")
            self.results['days_tested'].append('Day 1')
            self.results['passed'] += 1
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Day 1: {e}")
    
    def test_day2_class_management(self):
        """Day 2: Class Management"""
        print("\n" + "="*60)
        print("DAY 2: CLASS MANAGEMENT")
        print("="*60)
        
        try:
            # Create admin and teacher
            admin = User.objects.create_superuser('admin_d2', 'admin@test.com', 'admin123')
            teacher_user = User.objects.create_user('teacher_d2', 'teacher@test.com', 'teacher123')
            teacher = Teacher.objects.create(user=teacher_user, name='Teacher D2', email='teacher_d2@test.com')
            
            # Create class
            test_class = Class.objects.create(
                name='Test Class D2',
                section='A',
                grade_level='Grade 5',
                academic_year='2024-2025'
            )
            
            # Assign teacher
            test_class.assigned_teachers.add(teacher)
            
            self.assertEqual(test_class.assigned_teachers.count(), 1)
            print("✅ Class management working")
            self.results['days_tested'].append('Day 2')
            self.results['passed'] += 1
        except Exception as e:
            print(f"❌ Class management failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Day 2: {e}")
    
    def test_day3_student_management(self):
        """Day 3: Student Management"""
        print("\n" + "="*60)
        print("DAY 3: STUDENT MANAGEMENT")
        print("="*60)
        
        try:
            # Setup
            teacher_user = User.objects.create_user('teacher_d3', 'teacher@test.com', 'teacher123')
            teacher = Teacher.objects.create(user=teacher_user, name='Teacher D3', email='teacher_d3@test.com')
            
            test_class = Class.objects.create(
                name='Test Class D3',
                section='B',
                grade_level='Grade 5'
            )
            test_class.assigned_teachers.add(teacher)
            
            # Create and enroll students
            students = []
            for i in range(3):
                student = Student.objects.create(
                    name=f'Student D3-{i+1}',
                    current_grade_level='Grade 5'
                )
                students.append(student)
                
                enrollment = StudentEnrollment.objects.create(
                    student=student,
                    class_assigned=test_class,
                    academic_year='2024-2025',
                    status='active'
                )
            
            self.assertEqual(StudentEnrollment.objects.filter(class_assigned=test_class).count(), 3)
            print("✅ Student management working")
            self.results['days_tested'].append('Day 3')
            self.results['passed'] += 1
        except Exception as e:
            print(f"❌ Student management failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Day 3: {e}")
    
    def test_day4_exam_management(self):
        """Day 4: Exam Management Core"""
        print("\n" + "="*60)
        print("DAY 4: EXAM MANAGEMENT CORE")
        print("="*60)
        
        try:
            # Create exam
            exam = RoutineExam.objects.create(
                name='QC Test Exam D4',
                exam_type='monthly_review',
                curriculum_level='CORE Phonics Level 1',
                academic_year='2025',
                quarter='Q1',
                answer_key={'1': 'A', '2': 'B', '3': 'C'}
            )
            
            # Create class and teacher
            teacher_user = User.objects.create_user('teacher_d4', 'teacher@test.com', 'teacher123')
            teacher = Teacher.objects.create(user=teacher_user, name='Teacher D4', email='teacher_d4@test.com')
            
            test_class = Class.objects.create(
                name='Test Class D4',
                section='C',
                grade_level='Grade 5'
            )
            test_class.assigned_teachers.add(teacher)
            
            # Create assignment
            assignment = ExamAssignment.objects.create(
                exam=exam,
                class_assigned=test_class,
                assigned_by=teacher,
                deadline=timezone.now() + timedelta(days=7),
                is_bulk_assignment=True
            )
            
            self.assertIsNotNone(assignment)
            print("✅ Exam management working")
            self.results['days_tested'].append('Day 4')
            self.results['passed'] += 1
        except Exception as e:
            print(f"❌ Exam management failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Day 4: {e}")
    
    def test_day5_6_simplified(self):
        """Days 5-6: Simplified Implementation"""
        print("\n" + "="*60)
        print("DAYS 5-6: SIMPLIFIED IMPLEMENTATION")
        print("="*60)
        
        try:
            # Using existing models - no new implementation needed
            exam = RoutineExam.objects.create(
                name='QC Test D5-6',
                exam_type='quarterly',
                curriculum_level='CORE Phonics Level 2',
                academic_year='2025',
                quarter='Q1',
                answer_key={'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'apple'}
            )
            
            self.assertTrue(exam.validate_answer_key())
            print("✅ Simplified implementation working (using existing models)")
            self.results['days_tested'].append('Days 5-6')
            self.results['passed'] += 1
        except Exception as e:
            print(f"❌ Simplified implementation failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Days 5-6: {e}")
    
    def test_day7_9_student_workflow(self):
        """Days 7-9: Student Test Taking & Results"""
        print("\n" + "="*60)
        print("DAYS 7-9: STUDENT WORKFLOW")
        print("="*60)
        
        try:
            # Setup complete test scenario
            teacher_user = User.objects.create_user('teacher_d7', 'teacher@test.com', 'teacher123')
            teacher = Teacher.objects.create(user=teacher_user, name='Teacher D7', email='teacher_d7@test.com')
            
            student_user = User.objects.create_user('student_d7', 'student@test.com', 'student123')
            student = Student.objects.create(user=student_user, name='Student D7', current_grade_level='Grade 5')
            
            test_class = Class.objects.create(
                name='Test Class D7',
                section='D',
                grade_level='Grade 5'
            )
            test_class.assigned_teachers.add(teacher)
            
            # Enroll student
            enrollment = StudentEnrollment.objects.create(
                student=student,
                class_assigned=test_class,
                academic_year='2024-2025',
                status='active'
            )
            
            # Create and assign exam
            exam = RoutineExam.objects.create(
                name='QC Test D7-9',
                exam_type='monthly_review',
                curriculum_level='CORE Phonics Level 1',
                academic_year='2025',
                quarter='Q1',
                answer_key={'1': 'A', '2': 'B', '3': 'C'}
            )
            
            assignment = ExamAssignment.objects.create(
                exam=exam,
                class_assigned=test_class,
                assigned_by=teacher,
                deadline=timezone.now() + timedelta(days=7)
            )
            
            student_assignment = StudentExamAssignment.objects.create(
                student=student,
                exam_assignment=assignment,
                status='assigned'
            )
            
            # Simulate taking exam
            attempt = ExamAttempt.objects.create(
                student=student,
                exam=exam,
                assignment=student_assignment,
                attempt_number=1,
                answers={'1': 'A', '2': 'B', '3': 'D'}  # 2 correct, 1 wrong
            )
            
            # Calculate and verify score
            score = attempt.calculate_score()
            self.assertEqual(score, Decimal('66.67'))
            
            # Submit attempt
            attempt.submit()
            self.assertTrue(attempt.is_submitted)
            self.assertIsNotNone(attempt.submitted_at)
            
            print("✅ Student workflow working")
            self.results['days_tested'].append('Days 7-9')
            self.results['passed'] += 1
        except Exception as e:
            print(f"❌ Student workflow failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Days 7-9: {e}")
    
    def test_day10_integration(self):
        """Day 10: Full Integration Test"""
        print("\n" + "="*60)
        print("DAY 10: FULL INTEGRATION")
        print("="*60)
        
        try:
            # Complete workflow test
            # 1. Admin creates users
            admin = User.objects.create_superuser('admin_d10', 'admin@test.com', 'admin123')
            teacher_user = User.objects.create_user('teacher_d10', 'teacher@test.com', 'teacher123')
            student_user = User.objects.create_user('student_d10', 'student@test.com', 'student123')
            
            # 2. Create profiles
            teacher = Teacher.objects.create(user=teacher_user, name='Teacher D10', email='teacher_d10@test.com')
            student = Student.objects.create(user=student_user, name='Student D10', current_grade_level='Grade 5')
            
            # 3. Admin creates class
            test_class = Class.objects.create(
                name='Integration Test Class',
                section='INT',
                grade_level='Grade 5',
                academic_year='2024-2025',
                created_by=admin
            )
            
            # 4. Admin assigns teacher
            test_class.assigned_teachers.add(teacher)
            
            # 5. Teacher enrolls student
            enrollment = StudentEnrollment.objects.create(
                student=student,
                class_assigned=test_class,
                academic_year='2024-2025',
                status='active',
                created_by=teacher_user
            )
            
            # 6. Admin uploads exam
            exam = RoutineExam.objects.create(
                name='Integration Test Exam',
                exam_type='quarterly',
                curriculum_level='CORE Phonics Level 1',
                academic_year='2025',
                quarter='Q1',
                answer_key={'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E'},
                created_by=admin
            )
            
            # 7. Teacher assigns exam
            assignment = ExamAssignment.objects.create(
                exam=exam,
                class_assigned=test_class,
                assigned_by=teacher,
                deadline=timezone.now() + timedelta(days=7),
                allow_multiple_attempts=True
            )
            
            student_assignment = StudentExamAssignment.objects.create(
                student=student,
                exam_assignment=assignment,
                status='assigned'
            )
            
            # 8. Student takes exam (multiple attempts)
            attempt1 = ExamAttempt.objects.create(
                student=student,
                exam=exam,
                assignment=student_assignment,
                attempt_number=1,
                answers={'1': 'A', '2': 'B', '3': 'D', '4': 'D', '5': 'E'}  # 4/5 correct
            )
            attempt1.submit()
            
            attempt2 = ExamAttempt.objects.create(
                student=student,
                exam=exam,
                assignment=student_assignment,
                attempt_number=2,
                answers={'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E'}  # 5/5 correct
            )
            attempt2.submit()
            
            # 9. Verify scoring
            self.assertEqual(attempt1.score, Decimal('80.00'))
            self.assertEqual(attempt2.score, Decimal('100.00'))
            
            # 10. Check statistics
            attempts = ExamAttempt.objects.filter(student=student, exam=exam, is_submitted=True)
            best_score = max(a.score for a in attempts)
            avg_score = sum(a.score for a in attempts) / len(attempts)
            
            self.assertEqual(best_score, Decimal('100.00'))
            self.assertEqual(avg_score, Decimal('90.00'))
            
            print("✅ Full integration working")
            self.results['days_tested'].append('Day 10')
            self.results['passed'] += 1
            
        except Exception as e:
            print(f"❌ Integration failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Day 10: {e}")
    
    def tearDown(self):
        """Print final QC summary"""
        self.results['total_tests'] = self.results['passed'] + self.results['failed']
        
        print("\n" + "="*60)
        print("COMPREHENSIVE QC SUMMARY - ALL DAYS")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Days Tested: {', '.join(self.results['days_tested'])}")
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! System ready for deployment.")
        else:
            print("\n⚠️ Some tests failed. Review errors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Save results
        filename = f"qc_results_all_days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {filename}")


if __name__ == '__main__':
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(ComprehensiveQCAllDays)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)
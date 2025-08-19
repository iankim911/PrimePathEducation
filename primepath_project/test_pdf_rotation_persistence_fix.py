#!/usr/bin/env python
"""
COMPREHENSIVE TEST: PDF Rotation Persistence Fix
Tests the implemented fix to ensure PDF files are properly saved with rotation values
"""

import os
import sys
import django
from datetime import datetime
import tempfile
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from primepath_routinetest.models import Exam as RoutineTestExam
from placement_test.models import Exam as PlacementTestExam
from primepath_routinetest.services import ExamService as RoutineTestExamService
from placement_test.services import ExamService as PlacementTestExamService
from core.models import Teacher, CurriculumLevel
from core.exceptions import ValidationException

class PDFRotationPersistenceTest:
    """
    Test suite for PDF rotation persistence fix
    """
    
    def __init__(self):
        self.test_results = []
        self.created_exams = []
        
    def log_test_result(self, test_name, passed, details=None):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            'test_name': test_name,
            'status': status,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def create_test_pdf(self, content="Test PDF Content", filename="test_rotation.pdf"):
        """Create a simple test PDF file"""
        # Create a simple PDF-like content (not a real PDF, but enough for testing)
        pdf_content = f"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n{content}\n%%EOF"
        return SimpleUploadedFile(
            filename,
            pdf_content.encode('utf-8'),
            content_type='application/pdf'
        )
    
    def get_test_teacher(self):
        """Get or create a test teacher"""
        try:
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(
                username='test_pdf_user',
                defaults={'email': 'test@example.com', 'first_name': 'PDF', 'last_name': 'Test'}
            )
            
            teacher, created = Teacher.objects.get_or_create(
                user=user,
                defaults={'name': 'PDF Test Teacher', 'email': 'test@example.com'}
            )
            return teacher
        except Exception as e:
            print(f"Error creating test teacher: {e}")
            return None
    
    def get_test_curriculum_level(self):
        """Get a test curriculum level"""
        try:
            return CurriculumLevel.objects.first()
        except Exception as e:
            print(f"Error getting curriculum level: {e}")
            return None
    
    def test_pdf_validation_methods(self):
        """Test the new PDF validation methods"""
        print("\n" + "="*60)
        print("TESTING PDF VALIDATION METHODS")
        print("="*60)
        
        # Test 1: Valid PDF file validation
        try:
            valid_pdf = self.create_test_pdf()
            RoutineTestExamService.validate_pdf_file(valid_pdf)
            self.log_test_result("PDF validation - valid file", True, "Valid PDF file passed validation")
        except Exception as e:
            self.log_test_result("PDF validation - valid file", False, f"Valid PDF failed validation: {e}")
        
        # Test 2: Invalid file type validation
        try:
            invalid_file = SimpleUploadedFile("test.txt", b"Not a PDF", content_type='text/plain')
            RoutineTestExamService.validate_pdf_file(invalid_file)
            self.log_test_result("PDF validation - invalid type", False, "Invalid file type should have failed")
        except ValidationException as e:
            self.log_test_result("PDF validation - invalid type", True, f"Correctly rejected invalid type: {e}")
        except Exception as e:
            self.log_test_result("PDF validation - invalid type", False, f"Unexpected error: {e}")
        
        # Test 3: Empty file validation
        try:
            empty_file = SimpleUploadedFile("empty.pdf", b"", content_type='application/pdf')
            RoutineTestExamService.validate_pdf_file(empty_file)
            self.log_test_result("PDF validation - empty file", False, "Empty file should have failed")
        except ValidationException as e:
            self.log_test_result("PDF validation - empty file", True, f"Correctly rejected empty file: {e}")
        except Exception as e:
            self.log_test_result("PDF validation - empty file", False, f"Unexpected error: {e}")
    
    def test_routinetest_exam_creation_with_pdf_rotation(self):
        """Test RoutineTest exam creation with PDF rotation"""
        print("\n" + "="*60)
        print("TESTING ROUTINETEST EXAM CREATION WITH PDF ROTATION")
        print("="*60)
        
        teacher = self.get_test_teacher()
        curriculum_level = self.get_test_curriculum_level()
        
        if not teacher or not curriculum_level:
            self.log_test_result("RoutineTest exam creation - setup", False, "Failed to get test teacher or curriculum level")
            return
        
        # Test with different rotation values
        rotation_values = [0, 90, 180, 270]
        
        for rotation in rotation_values:
            try:
                test_pdf = self.create_test_pdf(f"Test content with {rotation}° rotation")
                
                exam_data = {
                    'name': f'Test RoutineTest Exam - {rotation}° Rotation',
                    'exam_type': 'REVIEW',
                    'time_period_month': 'JAN',
                    'academic_year': '2025',
                    'curriculum_level_id': curriculum_level.id,
                    'timer_minutes': 60,
                    'total_questions': 20,
                    'default_options_count': 5,
                    'pdf_rotation': rotation,
                    'created_by': teacher,
                    'is_active': True
                }
                
                exam = RoutineTestExamService.create_exam(
                    exam_data=exam_data,
                    pdf_file=test_pdf
                )
                
                self.created_exams.append(('routinetest', exam.id))
                
                # Verify the exam was created correctly
                success = True
                error_details = []
                
                if not exam.pdf_file:
                    success = False
                    error_details.append("PDF file not saved")
                
                if exam.pdf_rotation != rotation:
                    success = False
                    error_details.append(f"Rotation mismatch: expected {rotation}, got {exam.pdf_rotation}")
                
                if success and exam.pdf_file:
                    # Check if file exists on disk
                    if not os.path.exists(exam.pdf_file.path):
                        success = False
                        error_details.append("PDF file not found on disk")
                
                details = f"Rotation: {rotation}°, PDF saved: {bool(exam.pdf_file)}, File exists: {os.path.exists(exam.pdf_file.path) if exam.pdf_file else False}"
                if error_details:
                    details += f", Errors: {', '.join(error_details)}"
                
                self.log_test_result(f"RoutineTest creation - {rotation}° rotation", success, details)
                
            except Exception as e:
                self.log_test_result(f"RoutineTest creation - {rotation}° rotation", False, f"Exception: {str(e)}")
    
    def test_placementtest_exam_creation_with_pdf_rotation(self):
        """Test PlacementTest exam creation with PDF rotation"""
        print("\n" + "="*60)
        print("TESTING PLACEMENTTEST EXAM CREATION WITH PDF ROTATION")
        print("="*60)
        
        teacher = self.get_test_teacher()
        curriculum_level = self.get_test_curriculum_level()
        
        if not teacher or not curriculum_level:
            self.log_test_result("PlacementTest exam creation - setup", False, "Failed to get test teacher or curriculum level")
            return
        
        # Test with different rotation values
        rotation_values = [0, 90, 180, 270]
        
        for rotation in rotation_values:
            try:
                test_pdf = self.create_test_pdf(f"Test placement content with {rotation}° rotation")
                
                exam_data = {
                    'name': f'Test PlacementTest Exam - {rotation}° Rotation',
                    'curriculum_level_id': curriculum_level.id,
                    'timer_minutes': 45,
                    'total_questions': 15,
                    'default_options_count': 4,
                    'pdf_rotation': rotation,
                    'created_by': teacher,
                    'is_active': True
                }
                
                exam = PlacementTestExamService.create_exam(
                    exam_data=exam_data,
                    pdf_file=test_pdf
                )
                
                self.created_exams.append(('placementtest', exam.id))
                
                # Verify the exam was created correctly
                success = True
                error_details = []
                
                if not exam.pdf_file:
                    success = False
                    error_details.append("PDF file not saved")
                
                if exam.pdf_rotation != rotation:
                    success = False
                    error_details.append(f"Rotation mismatch: expected {rotation}, got {exam.pdf_rotation}")
                
                if success and exam.pdf_file:
                    # Check if file exists on disk
                    if not os.path.exists(exam.pdf_file.path):
                        success = False
                        error_details.append("PDF file not found on disk")
                
                details = f"Rotation: {rotation}°, PDF saved: {bool(exam.pdf_file)}, File exists: {os.path.exists(exam.pdf_file.path) if exam.pdf_file else False}"
                if error_details:
                    details += f", Errors: {', '.join(error_details)}"
                
                self.log_test_result(f"PlacementTest creation - {rotation}° rotation", success, details)
                
            except Exception as e:
                self.log_test_result(f"PlacementTest creation - {rotation}° rotation", False, f"Exception: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n" + "="*60)
        print("TESTING EDGE CASES AND ERROR HANDLING")
        print("="*60)
        
        teacher = self.get_test_teacher()
        curriculum_level = self.get_test_curriculum_level()
        
        # Test 1: No PDF file provided
        try:
            exam_data = {
                'name': 'Test No PDF Exam',
                'curriculum_level_id': curriculum_level.id,
                'total_questions': 10,
                'created_by': teacher
            }
            
            exam = RoutineTestExamService.create_exam(exam_data=exam_data, pdf_file=None)
            self.log_test_result("Edge case - no PDF file", False, "Should have failed without PDF file")
        except ValidationException as e:
            self.log_test_result("Edge case - no PDF file", True, f"Correctly handled missing PDF: {e}")
        except Exception as e:
            self.log_test_result("Edge case - no PDF file", False, f"Unexpected error: {e}")
        
        # Test 2: Very large rotation value
        try:
            test_pdf = self.create_test_pdf("Test large rotation")
            exam_data = {
                'name': 'Test Large Rotation Exam',
                'curriculum_level_id': curriculum_level.id,
                'total_questions': 10,
                'pdf_rotation': 720,  # 720 degrees
                'created_by': teacher
            }
            
            exam = RoutineTestExamService.create_exam(exam_data=exam_data, pdf_file=test_pdf)
            self.created_exams.append(('routinetest', exam.id))
            
            success = exam.pdf_file and exam.pdf_rotation == 720
            self.log_test_result("Edge case - large rotation value", success, f"Rotation saved as: {exam.pdf_rotation}°")
            
        except Exception as e:
            self.log_test_result("Edge case - large rotation value", False, f"Exception: {str(e)}")
    
    def cleanup_test_exams(self):
        """Clean up test exams created during testing"""
        print("\n" + "="*60)
        print("CLEANING UP TEST EXAMS")
        print("="*60)
        
        cleaned_count = 0
        for module, exam_id in self.created_exams:
            try:
                if module == 'routinetest':
                    exam = RoutineTestExam.objects.get(id=exam_id)
                    if exam.pdf_file:
                        exam.pdf_file.delete()
                    exam.delete()
                elif module == 'placementtest':
                    exam = PlacementTestExam.objects.get(id=exam_id)
                    if exam.pdf_file:
                        exam.pdf_file.delete()
                    exam.delete()
                
                cleaned_count += 1
                
            except Exception as e:
                print(f"   ⚠️  Error cleaning up {module} exam {exam_id}: {e}")
        
        print(f"   ✅ Cleaned up {cleaned_count} test exams")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("=" * 80)
        print("PDF ROTATION PERSISTENCE FIX - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Test started at: {datetime.now().isoformat()}")
        
        # Run all test methods
        self.test_pdf_validation_methods()
        self.test_routinetest_exam_creation_with_pdf_rotation()
        self.test_placementtest_exam_creation_with_pdf_rotation()
        self.test_edge_cases()
        
        # Cleanup
        self.cleanup_test_exams()
        
        # Summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   • {result['test_name']}: {result['details']}")
        
        print(f"\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"   {result['status']}: {result['test_name']}")
            if result['details']:
                print(f"      {result['details']}")
        
        # Overall assessment
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! PDF rotation persistence fix is working correctly.")
        elif failed_tests <= 2:
            print(f"\n⚠️  MOSTLY WORKING: {passed_tests}/{total_tests} tests passed. Minor issues may remain.")
        else:
            print(f"\n❌ MAJOR ISSUES: {failed_tests}/{total_tests} tests failed. Fix needs more work.")
        
        print("=" * 80)

def main():
    """Main test execution"""
    test_suite = PDFRotationPersistenceTest()
    test_suite.run_comprehensive_test()

if __name__ == "__main__":
    main()
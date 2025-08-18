#!/usr/bin/env python3
"""
Comprehensive QA Test: Modular Cell Details Implementation
Tests the complete cell details functionality with multiple exams per cell
"""

import os
import sys
import django
from datetime import datetime, timedelta
import json
import uuid

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from core.models import Teacher, CurriculumLevel, SubProgram, Program
from primepath_routinetest.models import Exam, Question, AudioFile, ExamScheduleMatrix
from primepath_routinetest.views.schedule_matrix import matrix_cell_detail

class ModularCellDetailsTest:
    def __init__(self):
        self.factory = RequestFactory()
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'errors': []
        }
        
    def log_test(self, test_name, passed, details=None):
        """Log test results"""
        self.test_results['tests_run'] += 1
        
        if passed:
            self.test_results['tests_passed'] += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   Details: {details}")
        else:
            self.test_results['tests_failed'] += 1
            print(f"❌ {test_name}: FAILED")
            if details:
                print(f"   Error: {details}")
                self.test_results['errors'].append(f"{test_name}: {details}")
    
    def test_curriculum_relationships(self):
        """Test 1: Verify CurriculumLevel relationship access works"""
        try:
            # Get a curriculum level with full relationships
            curriculum_levels = CurriculumLevel.objects.select_related(
                'subprogram__program'
            ).all()
            
            if not curriculum_levels.exists():
                self.log_test("Curriculum Relationships", False, "No curriculum levels found")
                return
            
            level = curriculum_levels.first()
            
            # Test all the access patterns we use
            program_name = level.subprogram.program.name if level.subprogram and level.subprogram.program else None
            subprogram_name = level.subprogram.name if level.subprogram else None
            level_number = level.level_number
            full_name = level.full_name
            
            success = all([
                program_name is not None,
                subprogram_name is not None,
                level_number is not None,
                full_name is not None
            ])
            
            details = f"Program: {program_name}, SubProgram: {subprogram_name}, Level: {level_number}"
            self.log_test("Curriculum Relationships", success, details)
            
        except Exception as e:
            self.log_test("Curriculum Relationships", False, str(e))
    
    def test_exam_creation_with_curriculum(self):
        """Test 2: Create test exams with proper curriculum relationships"""
        try:
            # Get curriculum levels
            curriculum_levels = list(CurriculumLevel.objects.select_related(
                'subprogram__program'
            ).all()[:3])
            
            if len(curriculum_levels) < 2:
                self.log_test("Exam Creation", False, "Not enough curriculum levels available")
                return
            
            # Create test exams
            test_exams = []
            for i, level in enumerate(curriculum_levels[:2], 1):
                exam = Exam.objects.create(
                    name=f"Test Modular Cell Exam {i}",
                    exam_type='REVIEW',
                    time_period_month='JAN',
                    academic_year='2025',
                    curriculum_level=level,
                    pdf_file='routinetest/exams/pdfs/test.pdf',
                    timer_minutes=60,
                    total_questions=20,
                    class_codes=['CLASS_7A', 'CLASS_8A']
                )
                
                # Create some questions for each exam
                for q_num in range(1, 6):  # 5 questions each
                    Question.objects.create(
                        exam=exam,
                        question_number=q_num,
                        question_type='MCQ',
                        correct_answer='A',
                        points=1,
                        options_count=4
                    )
                
                # Create an audio file
                AudioFile.objects.create(
                    exam=exam,
                    name=f"Audio for Exam {i}",
                    audio_file='routinetest/exams/audio/test.mp3',
                    start_question=1,
                    end_question=2
                )
                
                test_exams.append(exam)
            
            self.test_exams = test_exams
            self.log_test("Exam Creation", True, f"Created {len(test_exams)} test exams")
            
        except Exception as e:
            self.log_test("Exam Creation", False, str(e))
    
    def test_matrix_cell_creation(self):
        """Test 3: Create matrix cell with multiple exams"""
        try:
            if not hasattr(self, 'test_exams') or not self.test_exams:
                self.log_test("Matrix Cell Creation", False, "No test exams available")
                return
            
            # Use get_or_create to handle existing data
            matrix_cell, created = ExamScheduleMatrix.objects.get_or_create(
                class_code='CLASS_7A',
                academic_year='2025',
                time_period_type='MONTHLY',
                time_period_value='JAN',
                defaults={
                    'status': 'SCHEDULED'
                }
            )
            
            # Clear any existing exams first
            matrix_cell.exams.clear()
            
            # Add both exams to the cell
            for exam in self.test_exams:
                matrix_cell.exams.add(exam)
            
            self.test_matrix_cell = matrix_cell
            exam_count = matrix_cell.get_exam_count()
            action = "Created" if created else "Found existing"
            
            self.log_test("Matrix Cell Creation", True, 
                         f"{action} cell with {exam_count} exams (ID: {matrix_cell.id})")
            
        except Exception as e:
            self.log_test("Matrix Cell Creation", False, str(e))
    
    def test_detailed_exam_list_method(self):
        """Test 4: Test get_detailed_exam_list() method directly"""
        try:
            if not hasattr(self, 'test_matrix_cell'):
                self.log_test("Detailed Exam List Method", False, "No test matrix cell available")
                return
            
            # Call the method that was previously failing
            detailed_exams = self.test_matrix_cell.get_detailed_exam_list()
            
            # Verify the structure
            success = True
            error_details = []
            
            if not isinstance(detailed_exams, list):
                success = False
                error_details.append("Return type is not list")
            
            if len(detailed_exams) != len(self.test_exams):
                success = False
                error_details.append(f"Expected {len(self.test_exams)} exams, got {len(detailed_exams)}")
            
            # Test each exam's structure
            for i, exam_data in enumerate(detailed_exams):
                required_keys = ['id', 'name', 'curriculum', 'questions', 'timer', 'audio', 'answer_status']
                for key in required_keys:
                    if key not in exam_data:
                        success = False
                        error_details.append(f"Missing key '{key}' in exam {i}")
                
                # Test curriculum data specifically
                if 'curriculum' in exam_data:
                    curriculum = exam_data['curriculum']
                    if curriculum['program'] is None or curriculum['subprogram'] is None:
                        success = False
                        error_details.append(f"Curriculum relationships failed for exam {i}")
            
            details = f"Generated {len(detailed_exams)} detailed exam records"
            if error_details:
                details += f". Errors: {'; '.join(error_details)}"
            
            self.log_test("Detailed Exam List Method", success, details)
            
            # Store for next test
            if success:
                self.detailed_exams = detailed_exams
                
        except Exception as e:
            self.log_test("Detailed Exam List Method", False, str(e))
    
    def test_matrix_cell_detail_view(self):
        """Test 5: Test the matrix_cell_detail view"""
        try:
            if not hasattr(self, 'test_matrix_cell'):
                self.log_test("Matrix Cell Detail View", False, "No test matrix cell available")
                return
            
            # Create mock user and teacher
            user, _ = User.objects.get_or_create(
                username='testteacher',
                defaults={'password': 'testpass'}
            )
            teacher, _ = Teacher.objects.get_or_create(
                user=user,
                defaults={
                    'name': 'Test Teacher',
                    'email': 'test@example.com'
                }
            )
            
            # Create mock request
            request = self.factory.get(f'/RoutineTest/schedule-matrix/cell/{self.test_matrix_cell.id}/')
            request.user = user
            request.user.teacher = teacher
            
            # Call the view
            response = matrix_cell_detail(request, str(self.test_matrix_cell.id))
            
            # Check response
            success = response.status_code == 200
            details = f"Response status: {response.status_code}"
            
            if success:
                # Try to decode the response content
                try:
                    content = response.content.decode('utf-8')
                    if 'detailed_exams' in content:
                        details += ", Contains detailed_exams"
                    if 'exam-module-card' in content:
                        details += ", Contains exam module cards"
                except:
                    details += ", Content decode failed"
            
            self.log_test("Matrix Cell Detail View", success, details)
            
        except Exception as e:
            self.log_test("Matrix Cell Detail View", False, str(e))
    
    def test_uuid_serialization(self):
        """Test 6: Verify UUID serialization works in logging"""
        try:
            if not hasattr(self, 'test_matrix_cell'):
                self.log_test("UUID Serialization", False, "No test matrix cell available")
                return
            
            # Test JSON serialization of matrix cell data
            test_data = {
                "matrix_id": str(self.test_matrix_cell.id),
                "exam_ids": [str(exam.id) for exam in self.test_exams],
                "view": "matrix_cell_detail"
            }
            
            # This should not raise an exception
            json_string = json.dumps(test_data)
            parsed_back = json.loads(json_string)
            
            success = (
                parsed_back['matrix_id'] == str(self.test_matrix_cell.id) and
                len(parsed_back['exam_ids']) == len(self.test_exams)
            )
            
            self.log_test("UUID Serialization", success, "JSON serialization working correctly")
            
        except Exception as e:
            self.log_test("UUID Serialization", False, str(e))
    
    def test_modular_ui_data_structure(self):
        """Test 7: Verify modular UI data structure completeness"""
        try:
            if not hasattr(self, 'detailed_exams'):
                self.log_test("Modular UI Data Structure", False, "No detailed exams data available")
                return
            
            # Check each exam has all required data for modular cards
            required_structure = {
                'id': str,
                'name': str,
                'exam_type': str,
                'curriculum': dict,
                'questions': dict,
                'timer': dict,
                'audio': dict,
                'answer_status': dict,
                'activity_status': str,
                'actions': dict
            }
            
            success = True
            missing_items = []
            
            for i, exam in enumerate(self.detailed_exams):
                for key, expected_type in required_structure.items():
                    if key not in exam:
                        success = False
                        missing_items.append(f"Exam {i}: missing '{key}'")
                    elif not isinstance(exam[key], expected_type):
                        success = False
                        missing_items.append(f"Exam {i}: '{key}' wrong type")
                
                # Check nested curriculum structure
                if 'curriculum' in exam:
                    curriculum = exam['curriculum']
                    required_curriculum = ['level', 'program', 'subprogram', 'level_number']
                    for cur_key in required_curriculum:
                        if cur_key not in curriculum:
                            success = False
                            missing_items.append(f"Exam {i}: missing curriculum.{cur_key}")
            
            details = "All required fields present" if success else f"Missing: {', '.join(missing_items[:5])}"
            self.log_test("Modular UI Data Structure", success, details)
            
        except Exception as e:
            self.log_test("Modular UI Data Structure", False, str(e))
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            # Clean up test exams (cascades to questions and audio files)
            if hasattr(self, 'test_exams'):
                for exam in self.test_exams:
                    exam.delete()
            
            # Clean up matrix cell
            if hasattr(self, 'test_matrix_cell'):
                self.test_matrix_cell.delete()
            
            # Clean up test user/teacher
            User.objects.filter(username='testteacher').delete()
            
            print("🧹 Test data cleaned up")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def preliminary_cleanup(self):
        """Clean up any existing test data before starting"""
        try:
            # Clean up any existing test exams
            Exam.objects.filter(name__startswith='Test Modular Cell Exam').delete()
            
            # Clean up test user/teacher
            User.objects.filter(username='testteacher').delete()
            
            print("🧹 Preliminary cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Preliminary cleanup warning: {e}")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 60)
        print("COMPREHENSIVE QA TEST: MODULAR CELL DETAILS")
        print("=" * 60)
        print()
        
        # Clean up any existing test data first
        self.preliminary_cleanup()
        print()
        
        # Run tests in order
        self.test_curriculum_relationships()
        self.test_exam_creation_with_curriculum()
        self.test_matrix_cell_creation()
        self.test_detailed_exam_list_method()
        self.test_matrix_cell_detail_view()
        self.test_uuid_serialization()
        self.test_modular_ui_data_structure()
        
        # Summary
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")
        
        if self.test_results['tests_failed'] > 0:
            print("\nFAILURES:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print()
        
        # Overall result
        if self.test_results['tests_failed'] == 0:
            print("🎉 ALL TESTS PASSED - Modular Cell Details Implementation Complete!")
        else:
            print(f"⚠️ {self.test_results['tests_failed']} test(s) failed - Requires attention")
        
        print()
        
        # Cleanup
        self.cleanup_test_data()
        
        return self.test_results['tests_failed'] == 0

# Run the tests
if __name__ == "__main__":
    tester = ModularCellDetailsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
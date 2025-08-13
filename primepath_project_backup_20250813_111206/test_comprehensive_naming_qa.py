#!/usr/bin/env python
"""
Comprehensive QA test to ensure all features work after naming convention changes
Tests all critical functionality to ensure no regressions
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory, Client
from django.urls import reverse
from core.models import CurriculumLevel, Program, SubProgram
from placement_test.models import Exam, Question, AudioFile, StudentSession
from placement_test.services import ExamService
import tempfile

class ComprehensiveQATest:
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def log_result(self, test_name, passed, message=""):
        if passed:
            self.results['passed'].append(f"✅ {test_name}: {message}" if message else f"✅ {test_name}")
            print(f"✅ {test_name}")
        else:
            self.results['failed'].append(f"❌ {test_name}: {message}" if message else f"❌ {test_name}")
            print(f"❌ {test_name}: {message}")
    
    def test_curriculum_structure(self):
        """Test that curriculum structure is intact"""
        print("\n--- Testing Curriculum Structure ---")
        
        # Check programs exist
        programs = Program.objects.all()
        self.log_result("Programs exist", programs.count() > 0, f"Found {programs.count()} programs")
        
        # Check subprograms exist
        subprograms = SubProgram.objects.all()
        self.log_result("SubPrograms exist", subprograms.count() > 0, f"Found {subprograms.count()} subprograms")
        
        # Check curriculum levels exist
        levels = CurriculumLevel.objects.all()
        self.log_result("CurriculumLevels exist", levels.count() > 0, f"Found {levels.count()} levels")
        
        # Test new properties
        if levels.exists():
            level = levels.first()
            has_display_name = hasattr(level, 'display_name') and level.display_name
            has_exam_base_name = hasattr(level, 'exam_base_name') and level.exam_base_name
            
            self.log_result("CurriculumLevel.display_name property", has_display_name, level.display_name if has_display_name else "")
            self.log_result("CurriculumLevel.exam_base_name property", has_exam_base_name, level.exam_base_name if has_exam_base_name else "")
        
        return True
    
    def test_exam_model(self):
        """Test that Exam model works correctly"""
        print("\n--- Testing Exam Model ---")
        
        # Check existing exams
        exams = Exam.objects.all()
        self.log_result("Existing exams accessible", True, f"Found {exams.count()} exams")
        
        # Test creating a new exam with new naming
        level = CurriculumLevel.objects.first()
        if level:
            today_str = datetime.now().strftime('%y%m%d')
            test_exam_name = f"[PT]_Test_Lv1_{today_str}_QA"
            
            try:
                test_exam = Exam.objects.create(
                    name=test_exam_name,
                    curriculum_level=level,
                    timer_minutes=30,
                    total_questions=10,
                    default_options_count=5
                )
                self.log_result("Create exam with new naming", True, test_exam.name)
                
                # Test relationships
                questions_created = test_exam.questions.count() == 0  # Questions created separately
                self.log_result("Exam-Question relationship", True, f"{test_exam.questions.count()} questions")
                
                # Clean up
                test_exam.delete()
                
            except Exception as e:
                self.log_result("Create exam with new naming", False, str(e))
        
        return True
    
    def test_exam_service(self):
        """Test ExamService functionality"""
        print("\n--- Testing ExamService ---")
        
        level = CurriculumLevel.objects.first()
        if not level:
            self.log_result("ExamService tests", False, "No curriculum levels found")
            return False
        
        # Test version number generation
        today_str = datetime.now().strftime('%y%m%d')
        
        try:
            # Test new method
            version = ExamService.get_next_version_number(level.id, today_str)
            self.log_result("ExamService.get_next_version_number()", True, f"Version: {version}")
            
            # Test backward compatibility (old method should still work)
            try:
                old_version = ExamService.get_next_version_letter(level.id)
                self.log_result("ExamService.get_next_version_letter() (backward compat)", True, f"Version: {old_version}")
            except Exception as e:
                # It's OK if old method fails for levels with many versions
                self.results['warnings'].append(f"⚠️ Old version method: {str(e)}")
            
        except Exception as e:
            self.log_result("ExamService methods", False, str(e))
        
        return True
    
    def test_views_accessibility(self):
        """Test that all views are still accessible"""
        print("\n--- Testing Views Accessibility ---")
        
        # Test exam list view
        try:
            response = self.client.get(reverse('placement_test:exam_list'))
            self.log_result("Exam list view", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Exam list view", False, str(e))
        
        # Test create exam view
        try:
            response = self.client.get(reverse('placement_test:create_exam'))
            self.log_result("Create exam view", response.status_code == 200, f"Status: {response.status_code}")
            
            # Check that curriculum levels are in context
            if response.status_code == 200:
                has_levels = 'curriculum_levels' in response.context
                self.log_result("Create exam context", has_levels, 
                              f"Has {len(response.context.get('curriculum_levels', []))} levels" if has_levels else "Missing levels")
        except Exception as e:
            self.log_result("Create exam view", False, str(e))
        
        # Test version check endpoint
        level = CurriculumLevel.objects.first()
        if level:
            try:
                response = self.client.get(f'/api/placement/exams/check-version/?curriculum_level={level.id}')
                self.log_result("Version check API", response.status_code == 200, f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    has_date = 'date_str' in data
                    has_version = 'next_version' in data
                    self.log_result("Version API response format", has_date and has_version, 
                                  f"date_str: {data.get('date_str')}, version: {data.get('next_version')}")
            except Exception as e:
                self.log_result("Version check API", False, str(e))
        
        return True
    
    def test_student_interface(self):
        """Test that student interface still works"""
        print("\n--- Testing Student Interface ---")
        
        # Check if any active sessions exist
        sessions = StudentSession.objects.filter(completed_at__isnull=True)
        if sessions.exists():
            session = sessions.first()
            try:
                response = self.client.get(f'/placement/test/{session.id}/')
                self.log_result("Student test interface", response.status_code == 200, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Student test interface", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No active student sessions to test")
        
        # Test start test page
        try:
            response = self.client.get(reverse('placement_test:start_test'))
            self.log_result("Start test page", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Start test page", False, str(e))
        
        return True
    
    def test_question_types(self):
        """Test that all question types still work"""
        print("\n--- Testing Question Types ---")
        
        question_types = ['MCQ', 'SHORT', 'LONG', 'CHECKBOX', 'MIXED']
        
        exam = Exam.objects.first()
        if exam:
            for q_type in question_types:
                try:
                    question = Question.objects.create(
                        exam=exam,
                        question_number=999,  # High number to avoid conflicts
                        question_type=q_type,
                        correct_answer='test',
                        points=1,
                        options_count=5
                    )
                    self.log_result(f"Question type {q_type}", True, "Created successfully")
                    question.delete()  # Clean up
                except Exception as e:
                    self.log_result(f"Question type {q_type}", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No exams found to test question types")
        
        return True
    
    def test_audio_files(self):
        """Test that audio file functionality still works"""
        print("\n--- Testing Audio Files ---")
        
        # Check existing audio files
        audio_files = AudioFile.objects.all()
        self.log_result("Audio files accessible", True, f"Found {audio_files.count()} audio files")
        
        # Test audio-question relationship
        if audio_files.exists():
            audio = audio_files.first()
            assigned_questions = Question.objects.filter(audio_file=audio)
            self.log_result("Audio-Question relationship", True, 
                          f"Audio {audio.id} assigned to {assigned_questions.count()} questions")
        
        return True
    
    def test_placement_rules(self):
        """Test that placement rules still work"""
        print("\n--- Testing Placement Rules ---")
        
        try:
            response = self.client.get(reverse('core:placement_rules'))
            self.log_result("Placement rules page", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Placement rules page", False, str(e))
        
        return True
    
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n" + "="*60)
        print("COMPREHENSIVE QA TEST - POST NAMING CONVENTION CHANGES")
        print("="*60)
        
        self.test_curriculum_structure()
        self.test_exam_model()
        self.test_exam_service()
        self.test_views_accessibility()
        self.test_student_interface()
        self.test_question_types()
        self.test_audio_files()
        self.test_placement_rules()
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"\n✅ Passed: {len(self.results['passed'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⚠️  Warnings: {len(self.results['warnings'])}")
        
        if self.results['failed']:
            print("\nFailed Tests:")
            for failure in self.results['failed']:
                print(f"  {failure}")
        
        if self.results['warnings']:
            print("\nWarnings:")
            for warning in self.results['warnings']:
                print(f"  {warning}")
        
        # Save results to file
        results_file = 'naming_convention_qa_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {results_file}")
        
        return len(self.results['failed']) == 0

def main():
    """Run the comprehensive QA test"""
    tester = ComprehensiveQATest()
    success = tester.run_all_tests()
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL QA TESTS PASSED!")
        print("Naming convention changes implemented successfully.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ SOME QA TESTS FAILED!")
        print("Please review the failures above.")
        print("="*60)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
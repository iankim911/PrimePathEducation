#!/usr/bin/env python
"""
Double-check test to ensure ALL existing features remain intact after Internal Difficulty implementation
Tests every major feature systematically
"""

import os
import sys
import django
import json
import tempfile
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import CurriculumLevel, Program, SubProgram, ExamLevelMapping, PlacementRule
from placement_test.models import Exam, Question, StudentSession, AudioFile
from placement_test.services import ExamService, PlacementService, SessionService
import uuid

class ExistingFeaturesDoubleCheck:
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.critical_failures = []
    
    def log_result(self, test_name, passed, message="", critical=False):
        if passed:
            self.results['passed'].append(f"✅ {test_name}: {message}" if message else f"✅ {test_name}")
            print(f"✅ {test_name}")
        else:
            self.results['failed'].append(f"❌ {test_name}: {message}" if message else f"❌ {test_name}")
            print(f"❌ {test_name}: {message}")
            if critical:
                self.critical_failures.append(test_name)
    
    def test_exam_upload_naming(self):
        """Test exam upload and new naming convention"""
        print("\n--- Testing Exam Upload & Naming Convention ---")
        
        try:
            # Test create exam page loads
            response = self.client.get(reverse('placement_test:create_exam'))
            self.log_result("Create exam page loads", response.status_code == 200, 
                          f"Status: {response.status_code}", critical=True)
            
            if response.status_code == 200:
                content = response.content.decode()
                # Check for new naming elements
                has_pt_format = '[PT]' in content or 'PT_' in content
                has_lv_format = '_Lv' in content or 'Lv ' in content
                
                self.log_result("New naming format present", has_pt_format or has_lv_format,
                              "PT and Lv format found" if has_pt_format else "Old format")
                
                # Check curriculum levels are in context
                if hasattr(response, 'context') and response.context:
                    levels = response.context.get('curriculum_levels', [])
                    self.log_result("Curriculum levels in context", len(levels) > 0,
                                  f"Found {len(levels)} levels")
        except Exception as e:
            self.log_result("Exam upload functionality", False, str(e), critical=True)
        
        return True
    
    def test_exam_mapping(self):
        """Test exam-to-level mapping functionality"""
        print("\n--- Testing Exam-to-Level Mapping ---")
        
        try:
            response = self.client.get(reverse('core:exam_mapping'))
            self.log_result("Exam mapping page loads", response.status_code == 200,
                          f"Status: {response.status_code}", critical=True)
            
            if response.status_code == 200:
                content = response.content.decode()
                # Check for existing mapping elements
                has_slots = 'slot' in content.lower()
                has_selects = 'exam-select' in content
                has_save_button = 'Save All Mappings' in content
                
                self.log_result("Slot functionality present", has_slots)
                self.log_result("Exam selection dropdowns present", has_selects)
                self.log_result("Save mappings button present", has_save_button)
                
                # Check that difficulty column didn't break existing layout
                has_curriculum_column = 'Curriculum Level' in content
                has_exam_column = 'Mapped Exams' in content
                
                self.log_result("Original columns intact", 
                              has_curriculum_column and has_exam_column)
        except Exception as e:
            self.log_result("Exam mapping functionality", False, str(e), critical=True)
        
        return True
    
    def test_student_test_flow(self):
        """Test complete student test-taking flow"""
        print("\n--- Testing Student Test Flow ---")
        
        try:
            # Test start test page
            response = self.client.get(reverse('placement_test:start_test'))
            self.log_result("Start test page loads", response.status_code == 200,
                          f"Status: {response.status_code}", critical=True)
            
            # Check for student form elements
            if response.status_code == 200:
                content = response.content.decode()
                has_name_field = 'student_name' in content
                has_grade_field = 'grade' in content
                has_school_field = 'school' in content
                has_rank_field = 'academic_rank' in content
                
                self.log_result("Student name field present", has_name_field)
                self.log_result("Grade field present", has_grade_field)
                self.log_result("School field present", has_school_field)
                self.log_result("Academic rank field present", has_rank_field)
            
            # Test if we can access a test session
            session = StudentSession.objects.filter(completed_at__isnull=True).first()
            if session:
                response = self.client.get(f'/placement/test/{session.id}/')
                self.log_result("Student test interface accessible", 
                              response.status_code == 200,
                              f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode()
                    # Check for critical test elements
                    has_questions = 'question' in content.lower()
                    has_timer = 'timer' in content.lower()
                    has_navigation = 'navigation' in content.lower() or 'nav' in content.lower()
                    
                    self.log_result("Questions display", has_questions)
                    self.log_result("Timer functionality", has_timer)
                    self.log_result("Navigation elements", has_navigation)
            else:
                self.results['warnings'].append("⚠️ No active test sessions to verify")
                
        except Exception as e:
            self.log_result("Student test flow", False, str(e), critical=True)
        
        return True
    
    def test_placement_rules(self):
        """Test placement rules functionality"""
        print("\n--- Testing Placement Rules ---")
        
        try:
            response = self.client.get(reverse('core:placement_rules'))
            self.log_result("Placement rules page loads", response.status_code == 200,
                          f"Status: {response.status_code}", critical=True)
            
            if response.status_code == 200:
                content = response.content.decode()
                has_grade = 'Grade' in content
                has_percentile = 'percentile' in content.lower() or 'rank' in content.lower()
                has_curriculum = 'curriculum' in content.lower() or 'level' in content.lower()
                
                self.log_result("Grade column present", has_grade)
                self.log_result("Percentile/rank present", has_percentile)
                self.log_result("Curriculum levels present", has_curriculum)
            
            # Test PlacementService functionality
            try:
                # Test finding a placement rule
                rule = PlacementRule.objects.first()
                if rule:
                    # Test the service method still works
                    percentile = PlacementService.get_percentile_for_rank('TOP_10')
                    self.log_result("PlacementService.get_percentile_for_rank works", 
                                  percentile == 10)
                else:
                    self.results['warnings'].append("⚠️ No placement rules to test")
            except Exception as e:
                self.log_result("PlacementService methods", False, str(e))
                
        except Exception as e:
            self.log_result("Placement rules functionality", False, str(e), critical=True)
        
        return True
    
    def test_audio_functionality(self):
        """Test audio file functionality"""
        print("\n--- Testing Audio Functionality ---")
        
        try:
            # Check if audio files exist and are accessible
            audio_files = AudioFile.objects.all()
            self.log_result("Audio files accessible", True, 
                          f"Found {audio_files.count()} audio files")
            
            if audio_files.exists():
                audio = audio_files.first()
                # Check audio-question relationship
                if hasattr(audio, 'questions'):
                    related_questions = audio.questions.all()
                    self.log_result("Audio-Question relationship works", True,
                                  f"Audio linked to {related_questions.count()} questions")
                else:
                    # New relationship through Question.audio_file
                    from placement_test.models import Question
                    questions_with_audio = Question.objects.filter(audio_file=audio)
                    self.log_result("Question.audio_file relationship works", True,
                                  f"Audio assigned to {questions_with_audio.count()} questions")
            
            # Test audio in exam creation
            response = self.client.get(reverse('placement_test:create_exam'))
            if response.status_code == 200:
                content = response.content.decode()
                has_audio_upload = 'audio_files' in content
                self.log_result("Audio upload in exam creation", has_audio_upload)
                
        except Exception as e:
            self.log_result("Audio functionality", False, str(e))
        
        return True
    
    def test_question_types(self):
        """Test all question types"""
        print("\n--- Testing Question Types ---")
        
        question_types = ['MCQ', 'SHORT', 'LONG', 'CHECKBOX', 'MIXED']
        exam = Exam.objects.first()
        
        if not exam:
            self.results['warnings'].append("⚠️ No exams to test question types")
            return True
        
        for q_type in question_types:
            try:
                # Try to create a question of each type
                question = Question.objects.create(
                    exam=exam,
                    question_number=9999,  # High number to avoid conflicts
                    question_type=q_type,
                    correct_answer='test_answer',
                    points=1,
                    options_count=5
                )
                self.log_result(f"Question type {q_type}", True, "Created successfully")
                question.delete()  # Clean up
            except Exception as e:
                self.log_result(f"Question type {q_type}", False, str(e))
        
        return True
    
    def test_grading_system(self):
        """Test grading and results functionality"""
        print("\n--- Testing Grading System ---")
        
        try:
            from placement_test.services import GradingService
            
            # Check if GradingService methods exist and work
            has_grade_session = hasattr(GradingService, 'grade_session')
            has_auto_grade = hasattr(GradingService, 'auto_grade_answer')
            has_detailed_results = hasattr(GradingService, 'get_detailed_results')
            
            self.log_result("GradingService.grade_session exists", has_grade_session)
            self.log_result("GradingService.auto_grade_answer exists", has_auto_grade)
            self.log_result("GradingService.get_detailed_results exists", has_detailed_results)
            
            # Test result page for completed sessions
            completed_session = StudentSession.objects.filter(
                completed_at__isnull=False
            ).first()
            
            if completed_session:
                response = self.client.get(
                    reverse('placement_test:test_result', 
                           kwargs={'session_id': completed_session.id})
                )
                self.log_result("Test result page loads", response.status_code == 200,
                              f"Status: {response.status_code}")
            else:
                self.results['warnings'].append("⚠️ No completed sessions to test results")
                
        except Exception as e:
            self.log_result("Grading system", False, str(e))
        
        return True
    
    def test_teacher_dashboard(self):
        """Test teacher dashboard functionality"""
        print("\n--- Testing Teacher Dashboard ---")
        
        try:
            response = self.client.get(reverse('core:teacher_dashboard'))
            self.log_result("Teacher dashboard loads", response.status_code == 200,
                          f"Status: {response.status_code}", critical=True)
            
            if response.status_code == 200:
                content = response.content.decode()
                # Check for dashboard elements
                has_exam_link = 'Upload Exam' in content or 'Create Exam' in content
                has_mapping_link = 'Level Mapping' in content or 'Exam Mapping' in content
                has_rules_link = 'Placement Rules' in content
                has_sessions_link = 'Sessions' in content or 'View Sessions' in content
                
                self.log_result("Exam upload link present", has_exam_link)
                self.log_result("Level mapping link present", has_mapping_link)
                self.log_result("Placement rules link present", has_rules_link)
                self.log_result("Sessions link present", has_sessions_link)
                
        except Exception as e:
            self.log_result("Teacher dashboard", False, str(e), critical=True)
        
        return True
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n--- Testing API Endpoints ---")
        
        api_endpoints = [
            ('placement_test:submit_answer', 'POST'),
            ('core:save_exam_mappings', 'POST'),
            ('core:save_placement_rules', 'POST'),
            ('placement_test:check_exam_version', 'GET'),
        ]
        
        for endpoint_name, method in api_endpoints:
            try:
                url = reverse(endpoint_name)
                self.log_result(f"API endpoint {endpoint_name} exists", True, url)
            except Exception as e:
                self.log_result(f"API endpoint {endpoint_name}", False, 
                              f"URL not found: {str(e)}")
        
        return True
    
    def test_session_management(self):
        """Test session list and management"""
        print("\n--- Testing Session Management ---")
        
        try:
            response = self.client.get(reverse('placement_test:session_list'))
            self.log_result("Session list page loads", response.status_code == 200,
                          f"Status: {response.status_code}")
            
            # Test SessionService
            from placement_test.services import SessionService
            
            has_create = hasattr(SessionService, 'create_session')
            has_submit = hasattr(SessionService, 'submit_answer')
            has_complete = hasattr(SessionService, 'complete_session')
            
            self.log_result("SessionService.create_session exists", has_create)
            self.log_result("SessionService.submit_answer exists", has_submit)
            self.log_result("SessionService.complete_session exists", has_complete)
            
        except Exception as e:
            self.log_result("Session management", False, str(e))
        
        return True
    
    def test_database_relationships(self):
        """Test all critical database relationships"""
        print("\n--- Testing Database Relationships ---")
        
        try:
            # Test Exam relationships
            exam = Exam.objects.first()
            if exam:
                # Test exam can access questions
                questions = exam.questions.all()
                self.log_result("Exam->Questions relationship", True, 
                              f"Exam has {questions.count()} questions")
                
                # Test exam can access audio files
                audio_files = exam.audio_files.all()
                self.log_result("Exam->AudioFiles relationship", True,
                              f"Exam has {audio_files.count()} audio files")
                
                # Test exam can access sessions
                sessions = exam.sessions.all()
                self.log_result("Exam->Sessions relationship", True,
                              f"Exam has {sessions.count()} sessions")
            
            # Test CurriculumLevel relationships
            level = CurriculumLevel.objects.first()
            if level:
                # Test level can access exam mappings
                mappings = level.exam_mappings.all()
                self.log_result("CurriculumLevel->ExamMappings relationship", True,
                              f"Level has {mappings.count()} mappings")
                
                # Test level has subprogram
                has_subprogram = level.subprogram is not None
                self.log_result("CurriculumLevel->SubProgram relationship", has_subprogram)
            
        except Exception as e:
            self.log_result("Database relationships", False, str(e), critical=True)
        
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("DOUBLE-CHECK: EXISTING FEATURES AFTER INTERNAL DIFFICULTY IMPLEMENTATION")
        print("="*80)
        
        self.test_exam_upload_naming()
        self.test_exam_mapping()
        self.test_student_test_flow()
        self.test_placement_rules()
        self.test_audio_functionality()
        self.test_question_types()
        self.test_grading_system()
        self.test_teacher_dashboard()
        self.test_api_endpoints()
        self.test_session_management()
        self.test_database_relationships()
        
        # Print summary
        print("\n" + "="*80)
        print("DOUBLE-CHECK SUMMARY")
        print("="*80)
        print(f"\n✅ Passed: {len(self.results['passed'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⚠️  Warnings: {len(self.results['warnings'])}")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES: {len(self.critical_failures)}")
            for failure in self.critical_failures:
                print(f"  - {failure}")
        
        if self.results['failed']:
            print("\nAll Failed Tests:")
            for failure in self.results['failed']:
                print(f"  {failure}")
        
        if self.results['warnings']:
            print("\nWarnings:")
            for warning in self.results['warnings']:
                print(f"  {warning}")
        
        # Save results
        results_file = 'existing_features_double_check.json'
        with open(results_file, 'w') as f:
            json.dump({
                'passed': self.results['passed'],
                'failed': self.results['failed'],
                'warnings': self.results['warnings'],
                'critical_failures': self.critical_failures,
                'summary': {
                    'total_passed': len(self.results['passed']),
                    'total_failed': len(self.results['failed']),
                    'total_warnings': len(self.results['warnings']),
                    'critical_failures': len(self.critical_failures)
                }
            }, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
        
        return len(self.results['failed']) == 0 and len(self.critical_failures) == 0

def main():
    """Run the double-check test"""
    tester = ExistingFeaturesDoubleCheck()
    success = tester.run_all_tests()
    
    if success:
        print("\n" + "="*80)
        print("✅ DOUBLE-CHECK PASSED!")
        print("All existing features remain functional after Internal Difficulty implementation.")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ DOUBLE-CHECK FOUND ISSUES!")
        print("Some features may be affected. Please review the failures above.")
        print("="*80)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
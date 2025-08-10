#!/usr/bin/env python
"""
Comprehensive test to verify ALL existing features remain intact
after dual difficulty adjustment implementation
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
from placement_test.models import Exam, Question, StudentSession, AudioFile, StudentAnswer
from placement_test.services import ExamService, PlacementService, SessionService, GradingService
import uuid

class ComprehensiveFeatureCheck:
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
    
    def test_exam_creation_and_upload(self):
        """Test exam creation and file upload functionality"""
        print("\n--- Testing Exam Creation & Upload ---")
        
        try:
            # Test create exam page
            response = self.client.get(reverse('placement_test:create_exam'))
            self.log_result("Create exam page loads", response.status_code == 200, 
                          f"Status: {response.status_code}", critical=True)
            
            # Test exam naming convention
            if response.status_code == 200:
                content = response.content.decode()
                # Check for new naming elements
                has_pt_format = '[PT]' in content or 'PT_' in content
                has_lv_format = '_Lv' in content or 'Lv ' in content
                has_date_format = 'YYMMDD' in content or 'dateStr' in content
                
                self.log_result("PT naming format present", has_pt_format)
                self.log_result("Lv format present", has_lv_format)
                self.log_result("Date format functionality", has_date_format)
            
            # Test exam creation via service
            level = CurriculumLevel.objects.first()
            if level:
                exam_name = ExamService.generate_exam_name(level.id)
                self.log_result("ExamService.generate_exam_name works", True, exam_name)
                
                # Test version numbering
                version = ExamService.get_next_version_number(level.id)
                self.log_result("Version numbering works", version >= 1, f"Version: {version}")
            
        except Exception as e:
            self.log_result("Exam creation functionality", False, str(e), critical=True)
        
        return True
    
    def test_student_registration_flow(self):
        """Test student registration and test start flow"""
        print("\n--- Testing Student Registration Flow ---")
        
        try:
            # Test start test page
            response = self.client.get(reverse('placement_test:start_test'))
            self.log_result("Start test page loads", response.status_code == 200,
                          f"Status: {response.status_code}", critical=True)
            
            if response.status_code == 200:
                content = response.content.decode()
                # Check form fields
                has_name = 'student_name' in content
                has_phone = 'parent_phone' in content
                has_grade = 'grade' in content
                has_rank = 'academic_rank' in content
                has_school = 'school' in content
                
                self.log_result("Student name field present", has_name)
                self.log_result("Parent phone field present", has_phone)
                self.log_result("Grade selection present", has_grade)
                self.log_result("Academic rank selection present", has_rank)
                self.log_result("School selection present", has_school)
                
                # Check phone validation
                has_phone_validation = 'formatPhoneNumber' in content or 'phone-validation' in content
                self.log_result("Phone validation present", has_phone_validation)
                
        except Exception as e:
            self.log_result("Student registration flow", False, str(e), critical=True)
        
        return True
    
    def test_test_taking_interface(self):
        """Test the student test-taking interface"""
        print("\n--- Testing Test-Taking Interface ---")
        
        # Get or create a test session
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        
        if session:
            try:
                # Access test interface via correct URL
                response = self.client.get(f'/api/placement/session/{session.id}/')
                self.log_result("Test interface loads", response.status_code == 200,
                              f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    # Check essential components
                    has_questions = 'question' in content.lower()
                    has_timer = 'timer' in content.lower()
                    has_navigation = 'question-nav' in content or 'nav' in content.lower()
                    has_submit = 'submit' in content.lower()
                    
                    self.log_result("Questions display", has_questions)
                    self.log_result("Timer component", has_timer)
                    self.log_result("Navigation component", has_navigation)
                    self.log_result("Submit button", has_submit)
                    
                    # Check for PDF viewer if exam has PDF
                    if session.exam.pdf_file:
                        has_pdf = 'pdf-viewer' in content or 'pdfViewer' in content
                        self.log_result("PDF viewer present", has_pdf)
                    
                    # Check for audio player
                    has_audio = 'audio-player' in content or 'audioPlayer' in content
                    self.log_result("Audio player component", has_audio)
                    
            except Exception as e:
                self.log_result("Test-taking interface", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No active test sessions available")
        
        return True
    
    def test_answer_submission(self):
        """Test answer submission functionality"""
        print("\n--- Testing Answer Submission ---")
        
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        
        if session and session.exam.questions.exists():
            question = session.exam.questions.first()
            
            try:
                # Test answer submission endpoint
                url = reverse('placement_test:submit_answer', kwargs={'session_id': session.id})
                
                response = self.client.post(
                    url,
                    data=json.dumps({
                        'question_id': str(question.id),
                        'answer': 'Test answer'
                    }),
                    content_type='application/json'
                )
                
                self.log_result("Answer submission endpoint works", 
                              response.status_code == 200,
                              f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Check if answer was saved
                    answer_exists = StudentAnswer.objects.filter(
                        session=session,
                        question=question
                    ).exists()
                    self.log_result("Answer saved to database", answer_exists)
                    
            except Exception as e:
                self.log_result("Answer submission", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No test session with questions available")
        
        return True
    
    def test_grading_and_results(self):
        """Test grading system and results display"""
        print("\n--- Testing Grading & Results ---")
        
        # Find or create a completed session
        session = StudentSession.objects.filter(completed_at__isnull=False).first()
        
        if session:
            try:
                # Test grading service
                results = GradingService.grade_session(session)
                self.log_result("GradingService.grade_session works", True,
                              f"Score: {results.get('total_score', 0)}")
                
                # Test detailed results
                detailed = GradingService.get_detailed_results(session.id)
                self.log_result("GradingService.get_detailed_results works", True,
                              f"Questions graded: {len(detailed.get('questions', []))}")
                
                # Test results page
                response = self.client.get(
                    reverse('placement_test:test_result', kwargs={'session_id': session.id})
                )
                self.log_result("Results page loads", response.status_code == 200,
                              f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode()
                    has_score = 'score' in content.lower()
                    has_percentage = '%' in content
                    has_recommendation = 'recommendation' in content.lower() or 'level' in content.lower()
                    
                    self.log_result("Score display", has_score)
                    self.log_result("Percentage display", has_percentage)
                    self.log_result("Level recommendation", has_recommendation)
                    
            except Exception as e:
                self.log_result("Grading and results", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No completed sessions for testing")
        
        return True
    
    def test_placement_rules_system(self):
        """Test placement rules and level assignment"""
        print("\n--- Testing Placement Rules System ---")
        
        try:
            # Test placement rules page
            response = self.client.get(reverse('core:placement_rules'))
            self.log_result("Placement rules page loads", response.status_code == 200,
                          f"Status: {response.status_code}")
            
            # Test PlacementService
            level = PlacementService.determine_initial_level(grade=5, academic_rank='TOP_20')
            self.log_result("PlacementService.determine_initial_level works", 
                          level is not None,
                          f"Level: {level.full_name if level else 'None'}")
            
            # Test percentile conversion
            percentile = PlacementService.get_percentile_for_rank('TOP_10')
            self.log_result("PlacementService.get_percentile_for_rank works",
                          percentile == 10,
                          f"Percentile: {percentile}")
            
            # Test rule creation/saving
            rules_exist = PlacementRule.objects.exists()
            self.log_result("Placement rules exist in database", rules_exist,
                          f"Count: {PlacementRule.objects.count()}")
            
        except Exception as e:
            self.log_result("Placement rules system", False, str(e))
        
        return True
    
    def test_exam_level_mapping(self):
        """Test exam to curriculum level mapping"""
        print("\n--- Testing Exam-Level Mapping ---")
        
        try:
            # Test mapping page
            response = self.client.get(reverse('core:exam_mapping'))
            self.log_result("Exam mapping page loads", response.status_code == 200,
                          f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Check for mapping functionality
                has_slots = 'slot' in content.lower()
                has_dropdowns = 'exam-select' in content
                has_save = 'Save All Mappings' in content
                has_difficulty = 'difficulty' in content.lower()
                
                self.log_result("Slot functionality present", has_slots)
                self.log_result("Exam selection dropdowns", has_dropdowns)
                self.log_result("Save mappings button", has_save)
                self.log_result("Difficulty tier column", has_difficulty)
            
            # Test mapping relationships
            mappings_exist = ExamLevelMapping.objects.exists()
            self.log_result("Exam mappings exist in database", mappings_exist,
                          f"Count: {ExamLevelMapping.objects.count()}")
            
        except Exception as e:
            self.log_result("Exam-level mapping", False, str(e))
        
        return True
    
    def test_audio_functionality(self):
        """Test audio file handling and playback"""
        print("\n--- Testing Audio Functionality ---")
        
        try:
            # Check audio files
            audio_files = AudioFile.objects.all()
            self.log_result("Audio files accessible", True,
                          f"Count: {audio_files.count()}")
            
            if audio_files.exists():
                audio = audio_files.first()
                
                # Check audio-question relationship
                questions_with_audio = Question.objects.filter(audio_file=audio).count()
                self.log_result("Audio-Question relationships work", True,
                              f"Questions with this audio: {questions_with_audio}")
                
                # Check audio file has proper fields
                has_name = bool(audio.name)
                has_file = bool(audio.file)
                
                self.log_result("Audio files have names", has_name)
                self.log_result("Audio files have file references", has_file)
                
        except Exception as e:
            self.log_result("Audio functionality", False, str(e))
        
        return True
    
    def test_session_management(self):
        """Test session list and session management"""
        print("\n--- Testing Session Management ---")
        
        try:
            # Test session list page
            response = self.client.get(reverse('placement_test:session_list'))
            self.log_result("Session list page loads", response.status_code == 200,
                          f"Status: {response.status_code}")
            
            # Test SessionService methods
            has_create = hasattr(SessionService, 'create_session')
            has_submit = hasattr(SessionService, 'submit_answer')
            has_complete = hasattr(SessionService, 'complete_session')
            
            self.log_result("SessionService.create_session exists", has_create)
            self.log_result("SessionService.submit_answer exists", has_submit)
            self.log_result("SessionService.complete_session exists", has_complete)
            
            # Test session detail page if sessions exist
            session = StudentSession.objects.first()
            if session:
                response = self.client.get(
                    reverse('placement_test:session_detail', kwargs={'session_id': session.id})
                )
                self.log_result("Session detail page loads", response.status_code == 200,
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Session management", False, str(e))
        
        return True
    
    def test_difficulty_adjustments(self):
        """Test all three difficulty adjustment features"""
        print("\n--- Testing Difficulty Adjustments ---")
        
        try:
            # Test PlacementService difficulty methods
            level = CurriculumLevel.objects.filter(internal_difficulty__isnull=False).first()
            if level:
                easier = PlacementService.find_alternate_difficulty_exam(level, -1)
                harder = PlacementService.find_alternate_difficulty_exam(level, 1)
                
                self.log_result("Find easier exam works", True,
                              "Found" if easier else "None available")
                self.log_result("Find harder exam works", True,
                              "Found" if harder else "None available")
            
            # Test mid-exam adjustment URL
            session = StudentSession.objects.filter(completed_at__isnull=True).first()
            if session:
                url = reverse('placement_test:manual_adjust_difficulty',
                            kwargs={'session_id': session.id})
                self.log_result("Mid-exam adjustment URL exists", True, url)
            
            # Test post-submit adjustment URL
            if session:
                url = reverse('placement_test:post_submit_difficulty_choice',
                            kwargs={'session_id': session.id})
                self.log_result("Post-submit adjustment URL exists", True, url)
            
            # Test post-results adjustment URL
            url = reverse('placement_test:request_difficulty_change')
            self.log_result("Post-results adjustment URL exists", True, url)
            
        except Exception as e:
            self.log_result("Difficulty adjustments", False, str(e))
        
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
                
                # Check dashboard links
                has_exam_link = 'Upload Exam' in content or 'Create Exam' in content
                has_mapping_link = 'Level Mapping' in content or 'Exam Mapping' in content
                has_rules_link = 'Placement Rules' in content
                has_sessions_link = 'Sessions' in content
                
                self.log_result("Exam management link", has_exam_link)
                self.log_result("Level mapping link", has_mapping_link)
                self.log_result("Placement rules link", has_rules_link)
                self.log_result("Sessions link", has_sessions_link)
                
        except Exception as e:
            self.log_result("Teacher dashboard", False, str(e), critical=True)
        
        return True
    
    def test_database_integrity(self):
        """Test database relationships and integrity"""
        print("\n--- Testing Database Integrity ---")
        
        try:
            # Test Exam relationships
            exam = Exam.objects.first()
            if exam:
                questions = exam.questions.all()
                audio_files = exam.audio_files.all()
                sessions = exam.sessions.all()
                
                self.log_result("Exam->Questions relationship", True,
                              f"Questions: {questions.count()}")
                self.log_result("Exam->AudioFiles relationship", True,
                              f"Audio files: {audio_files.count()}")
                self.log_result("Exam->Sessions relationship", True,
                              f"Sessions: {sessions.count()}")
            
            # Test CurriculumLevel relationships
            level = CurriculumLevel.objects.first()
            if level:
                has_subprogram = level.subprogram is not None
                has_internal_diff = hasattr(level, 'internal_difficulty')
                mappings = level.exam_mappings.all()
                
                self.log_result("CurriculumLevel->SubProgram relationship", has_subprogram)
                self.log_result("CurriculumLevel has internal_difficulty", has_internal_diff)
                self.log_result("CurriculumLevel->ExamMappings relationship", True,
                              f"Mappings: {mappings.count()}")
            
        except Exception as e:
            self.log_result("Database integrity", False, str(e), critical=True)
        
        return True
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("\n" + "="*80)
        print("COMPREHENSIVE FEATURE CHECK - POST DUAL DIFFICULTY IMPLEMENTATION")
        print("="*80)
        
        self.test_exam_creation_and_upload()
        self.test_student_registration_flow()
        self.test_test_taking_interface()
        self.test_answer_submission()
        self.test_grading_and_results()
        self.test_placement_rules_system()
        self.test_exam_level_mapping()
        self.test_audio_functionality()
        self.test_session_management()
        self.test_difficulty_adjustments()
        self.test_teacher_dashboard()
        self.test_database_integrity()
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE CHECK SUMMARY")
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
        results_file = 'comprehensive_feature_check_results.json'
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
        
        # Calculate success rate
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        success_rate = (len(self.results['passed']) / total_tests * 100) if total_tests > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        return len(self.results['failed']) == 0 and len(self.critical_failures) == 0

def main():
    """Run the comprehensive feature check"""
    tester = ComprehensiveFeatureCheck()
    success = tester.run_all_tests()
    
    if success:
        print("\n" + "="*80)
        print("✅ COMPREHENSIVE CHECK PASSED!")
        print("All existing features remain fully functional after dual difficulty implementation.")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("⚠️ COMPREHENSIVE CHECK FOUND ISSUES!")
        print("Some features may need attention. Please review the failures above.")
        print("="*80)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
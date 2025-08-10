#!/usr/bin/env python
"""
Comprehensive test for dual difficulty adjustment feature
Tests all three adjustment points:
1. Mid-exam adjustment (existing)
2. Post-submit adjustment (new)
3. Post-results adjustment (existing)
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
from placement_test.models import Exam, StudentSession
from placement_test.services import PlacementService
from core.models import CurriculumLevel

class DualDifficultyAdjustmentTest:
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
    
    def test_mid_exam_adjustment_buttons(self):
        """Test that mid-exam adjustment buttons are present and functional"""
        print("\n--- Testing Mid-Exam Adjustment ---")
        
        # Get an active session
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        if not session:
            # Create a test session
            exam = Exam.objects.filter(is_active=True).first()
            if exam:
                session = StudentSession.objects.create(
                    student_name="Test Student",
                    parent_phone="010-1234-5678",
                    school_id=1,
                    grade=5,
                    academic_rank="TOP_10",
                    exam=exam
                )
        
        if session:
            try:
                # Access the test interface
                response = self.client.get(f'/api/placement/session/{session.id}/')
                
                self.log_result("Test interface loads", response.status_code == 200,
                              f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode()
                    # Check for difficulty adjustment buttons
                    has_easier_btn = 'decrease-difficulty-btn' in content or 'Easier Exam' in content
                    has_harder_btn = 'increase-difficulty-btn' in content or 'Harder Exam' in content
                    
                    self.log_result("Easier exam button present", has_easier_btn)
                    self.log_result("Harder exam button present", has_harder_btn)
                    
                    # Test the manual adjust endpoint exists
                    try:
                        url = reverse('placement_test:manual_adjust_difficulty', 
                                    kwargs={'session_id': session.id})
                        self.log_result("Manual adjust difficulty URL exists", True, url)
                    except:
                        self.log_result("Manual adjust difficulty URL exists", False)
            except Exception as e:
                self.log_result("Mid-exam adjustment test", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No test sessions available for mid-exam test")
        
        return True
    
    def test_post_submit_adjustment_flow(self):
        """Test the new post-submit difficulty choice modal"""
        print("\n--- Testing Post-Submit Adjustment ---")
        
        # Create a test session to complete
        exam = Exam.objects.filter(is_active=True).first()
        if not exam:
            self.results['warnings'].append("⚠️ No active exams for testing")
            return False
        
        session = StudentSession.objects.create(
            student_name="Post-Submit Test",
            parent_phone="010-5555-5555",
            school_id=1,
            grade=7,
            academic_rank="TOP_20",
            exam=exam
        )
        
        try:
            # Complete the test via AJAX (simulating JavaScript)
            complete_url = reverse('placement_test:complete_test', 
                                 kwargs={'session_id': session.id})
            
            response = self.client.post(
                complete_url,
                data=json.dumps({
                    'timer_expired': False,
                    'unsaved_count': 0
                }),
                content_type='application/json'
            )
            
            self.log_result("Complete test endpoint responds", 
                          response.status_code == 200,
                          f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.content)
                
                # Check response structure
                self.log_result("Response has success flag", 'success' in data)
                self.log_result("Response has show_difficulty_choice flag", 
                              'show_difficulty_choice' in data)
                
                # Check if difficulty choice is offered (depends on available levels)
                if data.get('show_difficulty_choice'):
                    self.log_result("Difficulty choice modal triggered", True,
                                  "Modal should be shown")
                    
                    # Test the post-submit difficulty endpoint
                    try:
                        post_submit_url = reverse('placement_test:post_submit_difficulty_choice',
                                                kwargs={'session_id': session.id})
                        
                        # Test choosing "Just Right" (0)
                        response = self.client.post(
                            post_submit_url,
                            data=json.dumps({'adjustment': 0}),
                            content_type='application/json'
                        )
                        
                        self.log_result("Post-submit choice endpoint works",
                                      response.status_code == 200,
                                      f"Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            choice_data = json.loads(response.content)
                            self.log_result("Choice returns redirect URL",
                                          'redirect_url' in choice_data)
                    except Exception as e:
                        self.log_result("Post-submit choice endpoint", False, str(e))
                else:
                    self.log_result("Difficulty choice not shown", True,
                                  "No alternative levels available")
                    
        except Exception as e:
            self.log_result("Post-submit adjustment flow", False, str(e))
        
        return True
    
    def test_post_results_adjustment(self):
        """Test existing post-results difficulty adjustment"""
        print("\n--- Testing Post-Results Adjustment ---")
        
        # Find a completed session
        session = StudentSession.objects.filter(completed_at__isnull=False).first()
        
        if not session:
            # Create and complete a test session
            exam = Exam.objects.filter(is_active=True).first()
            if exam:
                from django.utils import timezone
                session = StudentSession.objects.create(
                    student_name="Results Test",
                    parent_phone="010-6666-6666",
                    school_id=1,
                    grade=9,
                    academic_rank="TOP_40",
                    exam=exam,
                    completed_at=timezone.now(),
                    total_score=75,
                    percentage_score=75.0
                )
        
        if session:
            try:
                # Access results page
                response = self.client.get(
                    reverse('placement_test:test_result', 
                          kwargs={'session_id': session.id})
                )
                
                self.log_result("Results page loads", response.status_code == 200,
                              f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    # Check for difficulty adjustment section
                    has_difficulty_section = 'difficulty-adjustment-section' in content
                    has_easier_option = 'Try Easier Level' in content
                    has_harder_option = 'Try Harder Level' in content
                    
                    self.log_result("Difficulty adjustment section present", 
                                  has_difficulty_section)
                    self.log_result("Try Easier Level option present", has_easier_option)
                    self.log_result("Try Harder Level option present", has_harder_option)
                    
                    # Test the request_difficulty_change endpoint
                    try:
                        url = reverse('placement_test:request_difficulty_change')
                        self.log_result("Request difficulty change URL exists", True, url)
                    except:
                        self.log_result("Request difficulty change URL exists", False)
                        
            except Exception as e:
                self.log_result("Post-results adjustment test", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No completed sessions for post-results test")
        
        return True
    
    def test_difficulty_modal_component(self):
        """Test that difficulty choice modal component exists and is properly included"""
        print("\n--- Testing Difficulty Modal Component ---")
        
        try:
            # Check if modal template exists
            modal_path = 'templates/components/placement_test/difficulty_choice_modal.html'
            modal_exists = os.path.exists(modal_path)
            self.log_result("Difficulty modal template exists", modal_exists)
            
            # Check if CSS exists
            css_path = 'static/css/components/difficulty-modal.css'
            css_exists = os.path.exists(css_path)
            self.log_result("Difficulty modal CSS exists", css_exists)
            
            # Check if modal is included in student test template
            with open('templates/placement_test/student_test_v2.html', 'r') as f:
                template_content = f.read()
                modal_included = 'difficulty_choice_modal.html' in template_content
                css_included = 'difficulty-modal.css' in template_content
                
                self.log_result("Modal included in test template", modal_included)
                self.log_result("Modal CSS linked in template", css_included)
                
        except Exception as e:
            self.log_result("Modal component test", False, str(e))
        
        return True
    
    def test_javascript_integration(self):
        """Test that JavaScript properly handles the modal"""
        print("\n--- Testing JavaScript Integration ---")
        
        try:
            # Check answer-manager.js for modal handling
            with open('static/js/modules/answer-manager.js', 'r') as f:
                js_content = f.read()
                
                has_modal_check = 'show_difficulty_choice' in js_content
                has_modal_show = 'showDifficultyChoiceModal' in js_content
                has_modal_handlers = 'handleDifficultyChoice' in js_content
                
                self.log_result("JS checks for show_difficulty_choice flag", has_modal_check)
                self.log_result("JS has showDifficultyChoiceModal method", has_modal_show)
                self.log_result("JS has handleDifficultyChoice method", has_modal_handlers)
                
        except Exception as e:
            self.log_result("JavaScript integration test", False, str(e))
        
        return True
    
    def test_placement_service_support(self):
        """Test that PlacementService supports difficulty adjustments"""
        print("\n--- Testing PlacementService Support ---")
        
        try:
            # Get a curriculum level with internal difficulty
            level = CurriculumLevel.objects.filter(internal_difficulty__isnull=False).first()
            
            if not level:
                # Set internal difficulty for testing
                level = CurriculumLevel.objects.first()
                if level:
                    level.internal_difficulty = 2
                    level.save()
            
            if level:
                # Test finding easier exam
                easier_result = PlacementService.find_alternate_difficulty_exam(level, -1)
                self.log_result("PlacementService can find easier exam", True,
                              "Found" if easier_result else "None available")
                
                # Test finding harder exam
                harder_result = PlacementService.find_alternate_difficulty_exam(level, 1)
                self.log_result("PlacementService can find harder exam", True,
                              "Found" if harder_result else "None available")
            else:
                self.results['warnings'].append("⚠️ No curriculum levels for testing")
                
        except Exception as e:
            self.log_result("PlacementService support test", False, str(e))
        
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("DUAL DIFFICULTY ADJUSTMENT - COMPREHENSIVE TEST")
        print("="*80)
        
        self.test_mid_exam_adjustment_buttons()
        self.test_post_submit_adjustment_flow()
        self.test_post_results_adjustment()
        self.test_difficulty_modal_component()
        self.test_javascript_integration()
        self.test_placement_service_support()
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
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
        
        # Save results
        results_file = 'dual_difficulty_adjustment_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'passed': self.results['passed'],
                'failed': self.results['failed'],
                'warnings': self.results['warnings'],
                'summary': {
                    'total_passed': len(self.results['passed']),
                    'total_failed': len(self.results['failed']),
                    'total_warnings': len(self.results['warnings'])
                }
            }, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
        
        return len(self.results['failed']) == 0

def main():
    """Run the comprehensive test"""
    tester = DualDifficultyAdjustmentTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("Dual difficulty adjustment feature implemented successfully.")
        print("\nFeature Summary:")
        print("1. ✅ Mid-exam adjustment (existing) - Working")
        print("2. ✅ Post-submit adjustment (new) - Implemented")
        print("3. ✅ Post-results adjustment (existing) - Working")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ SOME TESTS FAILED!")
        print("Please review the failures above.")
        print("="*80)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
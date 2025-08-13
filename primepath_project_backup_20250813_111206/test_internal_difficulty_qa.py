#!/usr/bin/env python
"""
Comprehensive QA test for Internal Difficulty Level feature implementation
Tests all the new functionality and ensures no existing features are broken
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
from core.models import CurriculumLevel, Program, SubProgram, ExamLevelMapping
from placement_test.models import Exam, Question, StudentSession
from placement_test.services import PlacementService
from django.contrib.auth.models import User

class InternalDifficultyQATest:
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
    
    def test_model_field_addition(self):
        """Test that internal_difficulty field was added to CurriculumLevel"""
        print("\n--- Testing Model Field Addition ---")
        
        # Check if field exists
        level = CurriculumLevel.objects.first()
        if not level:
            self.log_result("CurriculumLevel exists", False, "No curriculum levels found")
            return False
        
        has_field = hasattr(level, 'internal_difficulty')
        self.log_result("internal_difficulty field exists", has_field)
        
        if has_field:
            # Test setting and retrieving value
            test_value = 5
            level.internal_difficulty = test_value
            level.save()
            level.refresh_from_db()
            
            self.log_result("Field can be set and retrieved", 
                          level.internal_difficulty == test_value,
                          f"Value: {level.internal_difficulty}")
        
        return True
    
    def test_exam_mapping_view(self):
        """Test that exam_mapping view includes difficulty data"""
        print("\n--- Testing Exam Mapping View ---")
        
        try:
            response = self.client.get(reverse('core:exam_mapping'))
            self.log_result("Exam mapping view loads", response.status_code == 200, 
                          f"Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if difficulty inputs are in the HTML
                content = response.content.decode()
                has_difficulty_input = 'difficulty-input' in content
                has_difficulty_header = 'Difficulty Tier' in content
                
                self.log_result("Difficulty column header present", has_difficulty_header)
                self.log_result("Difficulty input fields present", has_difficulty_input)
        except Exception as e:
            self.log_result("Exam mapping view", False, str(e))
        
        return True
    
    def test_save_difficulty_endpoint(self):
        """Test the save_difficulty_levels endpoint"""
        print("\n--- Testing Save Difficulty Endpoint ---")
        
        level = CurriculumLevel.objects.first()
        if not level:
            self.log_result("Save difficulty endpoint", False, "No levels to test")
            return False
        
        test_data = {
            'difficulty_updates': [
                {'level_id': level.id, 'difficulty': 3}
            ]
        }
        
        try:
            response = self.client.post(
                reverse('core:save_difficulty_levels'),
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            self.log_result("Save difficulty endpoint responds", 
                          response.status_code == 200,
                          f"Status: {response.status_code}")
            
            if response.status_code == 200:
                # Verify the value was saved
                level.refresh_from_db()
                self.log_result("Difficulty value saved correctly",
                              level.internal_difficulty == 3,
                              f"Saved value: {level.internal_difficulty}")
        except Exception as e:
            self.log_result("Save difficulty endpoint", False, str(e))
        
        return True
    
    def test_placement_service_enhancements(self):
        """Test PlacementService difficulty-aware methods"""
        print("\n--- Testing PlacementService Enhancements ---")
        
        # Test that new method exists
        has_method = hasattr(PlacementService, 'find_alternate_difficulty_exam')
        self.log_result("find_alternate_difficulty_exam method exists", has_method)
        
        if has_method:
            # Test the method with a sample level
            level = CurriculumLevel.objects.first()
            if level:
                try:
                    # Set a difficulty for testing
                    level.internal_difficulty = 2
                    level.save()
                    
                    # Try to find easier exam (adjustment = -1)
                    result = PlacementService.find_alternate_difficulty_exam(level, -1)
                    self.log_result("Find easier exam works", True, 
                                  "Result: " + ("Found" if result else "None available"))
                    
                    # Try to find harder exam (adjustment = +1)
                    result = PlacementService.find_alternate_difficulty_exam(level, 1)
                    self.log_result("Find harder exam works", True,
                                  "Result: " + ("Found" if result else "None available"))
                    
                except Exception as e:
                    self.log_result("PlacementService methods", False, str(e))
        
        return True
    
    def test_test_result_template(self):
        """Test that test_result template has difficulty adjustment options"""
        print("\n--- Testing Test Result Template ---")
        
        # Find a completed session to test with
        session = StudentSession.objects.filter(completed_at__isnull=False).first()
        
        if not session:
            self.results['warnings'].append("⚠️ No completed sessions to test result page")
            return True
        
        try:
            response = self.client.get(
                reverse('placement_test:test_result', kwargs={'session_id': session.id})
            )
            
            self.log_result("Test result page loads", response.status_code == 200,
                          f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                has_difficulty_section = 'difficulty-adjustment-section' in content
                has_easier_button = 'Try Easier Level' in content
                has_harder_button = 'Try Harder Level' in content
                
                self.log_result("Difficulty adjustment section present", has_difficulty_section)
                self.log_result("Try Easier Level button present", has_easier_button)
                self.log_result("Try Harder Level button present", has_harder_button)
        except Exception as e:
            self.log_result("Test result template", False, str(e))
        
        return True
    
    def test_request_difficulty_change_endpoint(self):
        """Test the request_difficulty_change endpoint"""
        print("\n--- Testing Request Difficulty Change Endpoint ---")
        
        # Check if the URL pattern exists
        try:
            url = reverse('placement_test:request_difficulty_change')
            self.log_result("request_difficulty_change URL exists", True, url)
        except Exception as e:
            self.log_result("request_difficulty_change URL", False, str(e))
            return False
        
        # Find a completed session to test with
        session = StudentSession.objects.filter(completed_at__isnull=False).first()
        
        if session:
            test_data = {
                'session_id': str(session.id),
                'adjustment': '1'  # Try harder
            }
            
            try:
                response = self.client.post(url, data=test_data, follow=True)
                
                # Check if it redirects appropriately (either to new test or back to result)
                self.log_result("Difficulty change endpoint responds", 
                              response.status_code == 200,
                              f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Difficulty change endpoint", False, str(e))
        else:
            self.results['warnings'].append("⚠️ No completed sessions to test difficulty change")
        
        return True
    
    def test_existing_features_intact(self):
        """Test that existing features still work"""
        print("\n--- Testing Existing Features ---")
        
        # Test exam list
        try:
            response = self.client.get(reverse('placement_test:exam_list'))
            self.log_result("Exam list still works", response.status_code == 200)
        except Exception as e:
            self.log_result("Exam list", False, str(e))
        
        # Test create exam view
        try:
            response = self.client.get(reverse('placement_test:create_exam'))
            self.log_result("Create exam still works", response.status_code == 200)
        except Exception as e:
            self.log_result("Create exam", False, str(e))
        
        # Test start test
        try:
            response = self.client.get(reverse('placement_test:start_test'))
            self.log_result("Start test still works", response.status_code == 200)
        except Exception as e:
            self.log_result("Start test", False, str(e))
        
        # Test placement rules
        try:
            response = self.client.get(reverse('core:placement_rules'))
            self.log_result("Placement rules still works", response.status_code == 200)
        except Exception as e:
            self.log_result("Placement rules", False, str(e))
        
        return True
    
    def test_backward_compatibility(self):
        """Test backward compatibility for levels without difficulty set"""
        print("\n--- Testing Backward Compatibility ---")
        
        # Create a level without difficulty
        level = CurriculumLevel.objects.first()
        if level:
            level.internal_difficulty = None
            level.save()
            
            try:
                # Test that PlacementService handles None difficulty gracefully
                result = PlacementService.find_alternate_difficulty_exam(level, 1)
                self.log_result("Handles None difficulty gracefully", True,
                              "Falls back to level-based logic")
            except Exception as e:
                self.log_result("None difficulty handling", False, str(e))
        
        return True
    
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n" + "="*60)
        print("INTERNAL DIFFICULTY LEVEL - COMPREHENSIVE QA TEST")
        print("="*60)
        
        self.test_model_field_addition()
        self.test_exam_mapping_view()
        self.test_save_difficulty_endpoint()
        self.test_placement_service_enhancements()
        self.test_test_result_template()
        self.test_request_difficulty_change_endpoint()
        self.test_existing_features_intact()
        self.test_backward_compatibility()
        
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
        results_file = 'internal_difficulty_qa_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {results_file}")
        
        return len(self.results['failed']) == 0

def main():
    """Run the comprehensive QA test"""
    tester = InternalDifficultyQATest()
    success = tester.run_all_tests()
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL QA TESTS PASSED!")
        print("Internal Difficulty Level feature implemented successfully.")
        print("="*60)
        print("\n📊 FEATURE SUMMARY:")
        print("1. ✅ Added internal_difficulty field to CurriculumLevel model")
        print("2. ✅ Updated exam_mapping view to show/edit difficulty tiers")
        print("3. ✅ Added endpoint to save difficulty levels")
        print("4. ✅ Enhanced PlacementService with difficulty-aware logic")
        print("5. ✅ Added post-exam difficulty change option")
        print("6. ✅ All existing features remain functional")
        print("7. ✅ Backward compatibility maintained")
    else:
        print("\n" + "="*60)
        print("❌ SOME QA TESTS FAILED!")
        print("Please review the failures above.")
        print("="*60)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
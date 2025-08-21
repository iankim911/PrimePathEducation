#!/usr/bin/env python
"""
Comprehensive test for Copy Exam Modal Fix
Tests both frontend and backend functionality
Date: 2025-08-20
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta

# Setup Django FIRST before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

# Now import Django modules
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

from primepath_routinetest.models import RoutineExam, ExamScheduleMatrix
from primepath_routinetest.models.class_model import Class
from core.models import Teacher
from primepath_routinetest.views.exam_api import copy_exam

class TestCopyModalFix(TestCase):
    """Test the comprehensive copy modal fix"""
    
    def setUp(self):
        """Set up test data"""
        print("\n" + "="*80)
        print("COPY MODAL COMPREHENSIVE TEST")
        print("="*80)
        
        # Create or get test user and teacher
        self.user, created = User.objects.get_or_create(
            username='testteacher',
            defaults={
                'email': 'test@example.com'
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
            
        self.teacher, _ = Teacher.objects.get_or_create(
            user=self.user,
            defaults={
                'name': 'Test Teacher',
                'is_head_teacher': True
            }
        )
        
        # Create test classes
        self.class_3a = Class.objects.create(
            name='Class 3A',
            grade_level='3',
            section='A',
            academic_year='2025'
        )
        
        self.class_3b = Class.objects.create(
            name='Class 3B',
            grade_level='3',
            section='B',
            academic_year='2025'
        )
        
        # Create source exam
        self.source_exam = RoutineExam.objects.create(
            name='Test Math Exam Q1 2025',
            exam_type='QUARTERLY',
            curriculum_level='CORE Elite Level 1',
            academic_year='2025',
            time_period_quarter='Q1',
            created_by=self.teacher,
            duration_minutes=60,
            passing_score=70
        )
        
        # Add exam to class 3A matrix
        self.matrix_3a = ExamScheduleMatrix.objects.create(
            class_code='3A',
            time_period_value='Q1',
            time_period_type='QUARTER',
            academic_year='2025',
            created_by=self.teacher
        )
        self.matrix_3a.exams.add(self.source_exam)
        
        print(f"✅ Created test exam: {self.source_exam.name} (ID: {self.source_exam.id})")
        print(f"✅ Created test classes: {self.class_3a.name}, {self.class_3b.name}")
        
        self.client = Client()
        self.factory = RequestFactory()
    
    def test_1_frontend_modal_elements(self):
        """Test that modal elements exist in the template"""
        print("\n🔍 Test 1: Frontend Modal Elements")
        print("-" * 40)
        
        # Login
        self.client.login(username='testteacher', password='testpass123')
        
        # Load the exam list page
        response = self.client.get('/RoutineTest/exams/')
        
        if response.status_code != 200:
            print(f"❌ Failed to load exam list page: {response.status_code}")
            return
        
        content = response.content.decode('utf-8')
        
        # Check for modal elements
        elements_to_check = [
            ('copyExamModal', 'Modal container'),
            ('copyExamForm', 'Copy form'),
            ('sourceExamId', 'Source exam ID field'),
            ('sourceExamName', 'Source exam name display'),
            ('targetClass', 'Target class selector'),
            ('timeslot', 'Timeslot selector'),
            ('copyExamType', 'Exam type selector'),
        ]
        
        for element_id, description in elements_to_check:
            if f'id="{element_id}"' in content or f"id='{element_id}'" in content:
                print(f"  ✅ {description} (#{element_id}) found")
            else:
                print(f"  ❌ {description} (#{element_id}) NOT found")
        
        # Check for JavaScript functions
        if 'openCopyModal' in content:
            print("  ✅ openCopyModal function referenced")
        else:
            print("  ❌ openCopyModal function NOT found")
        
        if 'closeCopyModal' in content:
            print("  ✅ closeCopyModal function referenced")
        else:
            print("  ❌ closeCopyModal function NOT found")
        
        # Check for external script
        if 'copy-exam-modal.js' in content:
            print("  ✅ External copy-exam-modal.js script included")
        else:
            print("  ⚠️  External copy-exam-modal.js script NOT included")
    
    def test_2_backend_copy_endpoint(self):
        """Test the backend copy exam endpoint"""
        print("\n🔍 Test 2: Backend Copy Endpoint")
        print("-" * 40)
        
        # Create request
        copy_data = {
            'source_exam_id': str(self.source_exam.id),
            'target_class': '3B',
            'target_timeslot': 'Q2'
        }
        
        print(f"  📤 Sending copy request:")
        print(f"     Source exam: {self.source_exam.name}")
        print(f"     Target class: {copy_data['target_class']}")
        print(f"     Target timeslot: {copy_data['target_timeslot']}")
        
        # Create request with user
        request = self.factory.post(
            '/RoutineTest/api/copy-exam/',
            data=json.dumps(copy_data),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call the view directly
        try:
            response = copy_exam(request)
            response_data = json.loads(response.content.decode('utf-8'))
            
            print(f"  📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ Copy successful!")
                if 'message' in response_data:
                    print(f"     Message: {response_data['message']}")
                
                # Verify the exam was copied
                matrix_3b = ExamScheduleMatrix.objects.filter(
                    class_code='3B',
                    time_period_value='Q2'
                ).first()
                
                if matrix_3b and self.source_exam in matrix_3b.exams.all():
                    print(f"  ✅ Exam verified in target class matrix")
                else:
                    print(f"  ❌ Exam NOT found in target class matrix")
            else:
                print(f"  ❌ Copy failed: {response_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Exception during copy: {str(e)}")
    
    def test_3_duplicate_prevention(self):
        """Test that duplicate copies are prevented"""
        print("\n🔍 Test 3: Duplicate Copy Prevention")
        print("-" * 40)
        
        copy_data = {
            'source_exam_id': str(self.source_exam.id),
            'target_class': '3B',
            'target_timeslot': 'Q1'
        }
        
        # First copy - should succeed
        request1 = self.factory.post(
            '/RoutineTest/api/copy-exam/',
            data=json.dumps(copy_data),
            content_type='application/json'
        )
        request1.user = self.user
        
        try:
            response1 = copy_exam(request1)
            if response1.status_code == 200:
                print("  ✅ First copy succeeded")
            else:
                print(f"  ❌ First copy failed: {response1.status_code}")
        except Exception as e:
            print(f"  ❌ First copy exception: {str(e)}")
        
        # Second copy - should fail
        request2 = self.factory.post(
            '/RoutineTest/api/copy-exam/',
            data=json.dumps(copy_data),
            content_type='application/json'
        )
        request2.user = self.user
        
        try:
            response2 = copy_exam(request2)
            response_data = json.loads(response2.content.decode('utf-8'))
            
            if response2.status_code == 400:
                print("  ✅ Duplicate copy correctly prevented")
                if 'error' in response_data:
                    print(f"     Error message: {response_data['error']}")
            else:
                print(f"  ❌ Duplicate copy NOT prevented: {response2.status_code}")
                
        except Exception as e:
            print(f"  ❌ Second copy exception: {str(e)}")
    
    def test_4_javascript_function_availability(self):
        """Test JavaScript function availability in rendered template"""
        print("\n🔍 Test 4: JavaScript Function Availability")
        print("-" * 40)
        
        # Login and get the page
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get('/RoutineTest/exams/')
        
        if response.status_code != 200:
            print(f"  ❌ Failed to load page: {response.status_code}")
            return
        
        content = response.content.decode('utf-8')
        
        # Count occurrences of function definitions
        open_modal_count = content.count('window.openCopyModal')
        close_modal_count = content.count('window.closeCopyModal')
        
        print(f"  📊 Function definition counts:")
        print(f"     window.openCopyModal: {open_modal_count} occurrences")
        print(f"     window.closeCopyModal: {close_modal_count} occurrences")
        
        # Check for duplicate definitions (should be minimal)
        if open_modal_count <= 2:  # One definition + one alias is OK
            print(f"  ✅ No excessive duplicate openCopyModal definitions")
        else:
            print(f"  ⚠️  Multiple openCopyModal definitions found ({open_modal_count})")
        
        if close_modal_count <= 2:
            print(f"  ✅ No excessive duplicate closeCopyModal definitions")
        else:
            print(f"  ⚠️  Multiple closeCopyModal definitions found ({close_modal_count})")
        
        # Check for console logging
        if '[COPY MODAL]' in content:
            print(f"  ✅ Console logging present")
        else:
            print(f"  ❌ Console logging NOT found")
    
    def test_5_modal_css_styles(self):
        """Test that modal CSS styles are present"""
        print("\n🔍 Test 5: Modal CSS Styles")
        print("-" * 40)
        
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get('/RoutineTest/exams/')
        
        if response.status_code != 200:
            print(f"  ❌ Failed to load page: {response.status_code}")
            return
        
        content = response.content.decode('utf-8')
        
        # Check for modal styles
        style_checks = [
            ('#copyExamModal', 'Modal base styles'),
            ('.modal-content', 'Modal content styles'),
            ('.btn-copy', 'Copy button styles'),
            ('#copyExamModal.show', 'Modal show state styles'),
        ]
        
        for selector, description in style_checks:
            if selector in content:
                print(f"  ✅ {description} ({selector}) found")
            else:
                print(f"  ⚠️  {description} ({selector}) not found")


def run_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 STARTING COMPREHENSIVE COPY MODAL TESTS")
    print("="*80)
    
    # Create test instance
    test = TestCopyModalFix()
    test.setUp()
    
    # Run tests
    try:
        test.test_1_frontend_modal_elements()
        test.test_2_backend_copy_endpoint()
        test.test_3_duplicate_prevention()
        test.test_4_javascript_function_availability()
        test.test_5_modal_css_styles()
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ COPY MODAL TESTS COMPLETED")
    print("="*80)
    print("\n📋 SUMMARY:")
    print("  - Frontend modal elements tested")
    print("  - Backend copy endpoint tested")
    print("  - Duplicate prevention tested")
    print("  - JavaScript functions tested")
    print("  - CSS styles tested")
    print("\n💡 Check console logs in browser for detailed debugging info")


if __name__ == '__main__':
    run_tests()
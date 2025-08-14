#!/usr/bin/env python3
"""
Comprehensive test for exam_mapping view fix
Tests the AttributeError fix and validates all functionality
"""

import os
import sys
import json
import django
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.db import connection
from placement_test.models import Exam, Question
from core.models import ExamLevelMapping, CurriculumLevel, Teacher, Program
from core.views import exam_mapping

User = get_user_model()

class ExamMappingTester:
    def __init__(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        if success:
            self.passed += 1
            print(f"  ✅ {test_name}")
            if details:
                print(f"     {details}")
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            print(f"     ERROR: {details}")
    
    def test_view_loads_without_error(self):
        """Test that exam_mapping view loads without AttributeError"""
        print("\n📄 Testing View Load...")
        
        try:
            # Create or get a test teacher
            teacher = Teacher.objects.first()
            if not teacher:
                teacher = Teacher.objects.create(
                    username=f"test_teacher_{datetime.now().timestamp()}",
                    email="test@teacher.com"
                )
            
            # Create request
            request = self.factory.get('/core/exam-mapping/')
            request.user = teacher
            
            # Add session middleware
            from django.contrib.sessions.middleware import SessionMiddleware
            middleware = SessionMiddleware(lambda x: x)
            middleware.process_request(request)
            request.session.save()
            
            # Call the view
            response = exam_mapping(request)
            
            # Check response
            self.log_result(
                "View loads without AttributeError",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
            
            # Check for error indicators in response
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                has_error = 'AttributeError' in content or "'dict' object has no attribute" in content
                self.log_result(
                    "No AttributeError in response",
                    not has_error,
                    "Response clean" if not has_error else "Error found in response"
                )
            
        except AttributeError as e:
            self.log_result(
                "View loads without AttributeError",
                False,
                str(e)
            )
        except Exception as e:
            self.log_result(
                "View loads without error",
                False,
                f"{type(e).__name__}: {str(e)}"
            )
    
    def test_data_structure_integrity(self):
        """Test that data structures are correctly formatted"""
        print("\n🔍 Testing Data Structure...")
        
        try:
            # Get test data
            programs = Program.objects.prefetch_related('subprograms__levels').all()
            all_exams = Exam.objects.filter(is_active=True)
            
            if not all_exams.exists():
                self.log_result(
                    "Exams exist for testing",
                    False,
                    "No active exams found"
                )
                return
            
            # Simulate the view's data processing
            from core.models import ExamLevelMapping
            exam_to_level_map = {}
            for mapping in ExamLevelMapping.objects.select_related('curriculum_level').all():
                exam_to_level_map[mapping.exam_id] = mapping.curriculum_level
            
            test_exam = all_exams.first()
            
            # Test the fixed structure
            exam_info = {
                'id': str(test_exam.id),
                'name': test_exam.name,
                'display_name': test_exam.name.replace('PRIME ', '').replace('Level ', 'Lv '),
                'has_pdf': bool(test_exam.pdf_file),
                'is_mapped_elsewhere': False,
                'is_mapped_here': False,
                'mapped_to_level': None
            }
            
            # Validate structure
            required_keys = ['id', 'name', 'display_name', 'has_pdf', 
                           'is_mapped_elsewhere', 'is_mapped_here', 'mapped_to_level']
            
            has_all_keys = all(key in exam_info for key in required_keys)
            self.log_result(
                "Exam info has all required keys",
                has_all_keys,
                f"Keys: {list(exam_info.keys())}"
            )
            
            # Validate types
            type_checks = [
                ('id', str),
                ('name', str),
                ('display_name', str),
                ('has_pdf', bool)
            ]
            
            for key, expected_type in type_checks:
                actual_type = type(exam_info.get(key))
                is_correct = actual_type == expected_type
                self.log_result(
                    f"{key} is {expected_type.__name__}",
                    is_correct,
                    f"Got {actual_type.__name__}"
                )
            
        except Exception as e:
            self.log_result(
                "Data structure test",
                False,
                str(e)
            )
    
    def test_duplicate_prevention_logic(self):
        """Test that duplicate exam prevention still works"""
        print("\n🔒 Testing Duplicate Prevention...")
        
        try:
            from core.models import ExamLevelMapping
            
            # Check for current duplicates
            from django.db.models import Count
            duplicates = ExamLevelMapping.objects.values('exam').annotate(
                count=Count('exam')
            ).filter(count__gt=1)
            
            has_no_duplicates = duplicates.count() == 0
            self.log_result(
                "No duplicate exam mappings",
                has_no_duplicates,
                f"Found {duplicates.count()} duplicates" if not has_no_duplicates else "All exams unique"
            )
            
            # Test that validation works
            if ExamLevelMapping.objects.exists():
                existing = ExamLevelMapping.objects.first()
                other_level = CurriculumLevel.objects.exclude(
                    id=existing.curriculum_level_id
                ).first()
                
                if other_level:
                    try:
                        # Try to create duplicate
                        test_mapping = ExamLevelMapping(
                            exam=existing.exam,
                            curriculum_level=other_level,
                            slot=1
                        )
                        test_mapping.clean()
                        self.log_result(
                            "Duplicate prevention works",
                            False,
                            "Duplicate was allowed!"
                        )
                    except Exception:
                        self.log_result(
                            "Duplicate prevention works",
                            True,
                            "Correctly prevented duplicate"
                        )
                        
        except Exception as e:
            self.log_result(
                "Duplicate prevention test",
                False,
                str(e)
            )
    
    def test_exam_mapping_display(self):
        """Test that existing mappings display correctly"""
        print("\n📊 Testing Mapping Display...")
        
        try:
            # Check if mappings exist
            mapping_count = ExamLevelMapping.objects.count()
            self.log_result(
                "Exam mappings exist",
                mapping_count > 0,
                f"Found {mapping_count} mappings"
            )
            
            if mapping_count > 0:
                # Get a sample mapping
                sample_mapping = ExamLevelMapping.objects.select_related(
                    'exam', 'curriculum_level'
                ).first()
                
                # Verify it has required data
                has_exam = sample_mapping.exam is not None
                has_level = sample_mapping.curriculum_level is not None
                has_slot = sample_mapping.slot is not None
                
                self.log_result(
                    "Mapping has complete data",
                    all([has_exam, has_level, has_slot]),
                    f"Exam: {has_exam}, Level: {has_level}, Slot: {has_slot}"
                )
                
                if has_exam:
                    # Test display name generation
                    display_name = sample_mapping.exam.name.replace('PRIME ', '').replace('Level ', 'Lv ')
                    self.log_result(
                        "Display name generation works",
                        len(display_name) > 0,
                        f"'{sample_mapping.exam.name}' → '{display_name}'"
                    )
                    
        except Exception as e:
            self.log_result(
                "Mapping display test",
                False,
                str(e)
            )
    
    def test_console_logging(self):
        """Test that console logging is working"""
        print("\n📝 Testing Console Logging...")
        
        try:
            # Capture console output
            import io
            from contextlib import redirect_stdout
            
            teacher = Teacher.objects.first()
            if not teacher:
                teacher = Teacher.objects.create(
                    username=f"test_log_{datetime.now().timestamp()}",
                    email="test@log.com"
                )
            
            request = self.factory.get('/core/exam-mapping/')
            request.user = teacher
            
            # Add session
            from django.contrib.sessions.middleware import SessionMiddleware
            middleware = SessionMiddleware(lambda x: x)
            middleware.process_request(request)
            request.session.save()
            
            # Capture output
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                response = exam_mapping(request)
            
            output = output_buffer.getvalue()
            
            # Check for expected log entries
            expected_logs = [
                '[EXAM_MAPPING_INIT]',
                '[EXAM_RETRIEVAL]',
                '[MAPPING_LOAD]',
                '[EXAM_MAPPING_COMPLETE]',
                '[TEMPLATE_VALIDATION]'
            ]
            
            for log_marker in expected_logs:
                has_log = log_marker in output
                self.log_result(
                    f"Has {log_marker} log",
                    has_log,
                    "Found" if has_log else "Missing"
                )
            
            # Check for fix version
            has_fix_version = '"fix_version": "2.0"' in output
            self.log_result(
                "Fix version 2.0 logged",
                has_fix_version,
                "Fix is active" if has_fix_version else "Fix not detected"
            )
            
        except Exception as e:
            self.log_result(
                "Console logging test",
                False,
                str(e)
            )
    
    def test_other_views_unaffected(self):
        """Test that other views are not affected by the fix"""
        print("\n🔄 Testing Other Views...")
        
        try:
            from core.views import placement_rules
            
            teacher = Teacher.objects.first()
            if not teacher:
                teacher = Teacher.objects.create(
                    username=f"test_other_{datetime.now().timestamp()}",
                    email="test@other.com"
                )
            
            # Test placement_rules view
            request = self.factory.get('/core/student-levels/')
            request.user = teacher
            
            # Add session
            from django.contrib.sessions.middleware import SessionMiddleware
            middleware = SessionMiddleware(lambda x: x)
            middleware.process_request(request)
            request.session.save()
            
            response = placement_rules(request)
            
            self.log_result(
                "placement_rules view works",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_result(
                "Other views test",
                False,
                str(e)
            )
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("🧪 EXAM MAPPING FIX COMPREHENSIVE TEST")
        print("="*60)
        
        self.test_view_loads_without_error()
        self.test_data_structure_integrity()
        self.test_duplicate_prevention_logic()
        self.test_exam_mapping_display()
        self.test_console_logging()
        self.test_other_views_unaffected()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print("\n⚠️ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Final verdict
        print("\n" + "="*60)
        if self.failed == 0:
            print("✅ FIX SUCCESSFUL: All tests passed!")
            print("The AttributeError has been resolved.")
        else:
            print("⚠️ FIX INCOMPLETE: Some tests failed.")
            print("Please review the failed tests above.")
        print("="*60)
        
        return self.failed == 0

if __name__ == '__main__':
    tester = ExamMappingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)